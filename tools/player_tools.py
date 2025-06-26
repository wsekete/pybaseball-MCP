"""
Player lookup and identification tools for pybaseball MCP server.

These tools provide functionality for finding players, resolving player IDs,
and getting basic player information.
"""

import logging
from typing import Optional, List, Dict, Any
from fuzzywuzzy import fuzz, process

from mcp.server.fastmcp import FastMCP, Context
import pybaseball as pyb
from utils.data_processing import DataProcessor
from utils.validation import Validator, ValidationError

logger = logging.getLogger(__name__)


def register_player_tools(mcp: FastMCP):
    """Register all player-related tools with the MCP server"""
    
    @mcp.tool()
    def lookup_player_id(
        player_name: str,
        fuzzy_match: bool = True,
        limit: int = 10,
        ctx: Context = None
    ) -> str:
        """
        Look up a player's ID by name using pybaseball's player lookup functionality.
        
        Args:
            player_name: Player's name (e.g., "Mike Trout", "Albert Pujols")
            fuzzy_match: Whether to use fuzzy matching for similar names
            limit: Maximum number of results to return
            
        Returns:
            Formatted string with player lookup results including IDs and basic info
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate input
            clean_name = validator.validate_player_name(player_name)
            limit = validator.validate_page_size(limit, max_size=50)
            
            # Look up player
            df = pyb.playerid_lookup(clean_name, fuzzy=fuzzy_match)
            
            if df.empty:
                # Try suggestions
                suggested_name, suggestions = validator.validate_and_suggest_player_name(clean_name)
                suggestion_text = ""
                if suggestions:
                    suggestion_text = f"\n\n**Suggestions to try:**\n" + "\n".join(f"- {s}" for s in suggestions)
                
                return f"❌ No players found for '{clean_name}'{suggestion_text}"
            
            # Limit results
            if len(df) > limit:
                df = df.head(limit)
                truncated_note = f"\n\n*Note: Results limited to {limit} entries*"
            else:
                truncated_note = ""
            
            # Format response
            title = f"Player Lookup Results for '{clean_name}'"
            response = data_processor.format_dataframe_as_markdown(df, title)
            
            # Add helpful context
            context = f"""
### How to Use These Results:
- **key_mlbam**: Use for Statcast data queries
- **key_fangraphs**: Use for FanGraphs statistics
- **key_bbref**: Use for Baseball Reference statistics
- **mlb_played_first/last**: Career span in MLB
            """
            
            response += context + truncated_note
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in lookup_player_id: {e}")
            return f"❌ Error looking up player: {e}"

    @mcp.tool()
    def reverse_lookup_player(
        player_id: str,
        id_type: str = "mlbam",
        ctx: Context = None
    ) -> str:
        """
        Look up a player's name and details using their ID.
        
        Args:
            player_id: Player's ID number
            id_type: Type of ID ("mlbam", "fangraphs", "bbref")
            
        Returns:
            Formatted string with player information
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate input
            if not player_id:
                raise ValidationError("Player ID cannot be empty")
            
            id_type = id_type.lower().strip()
            valid_id_types = ["mlbam", "fangraphs", "bbref"]
            if id_type not in valid_id_types:
                raise ValidationError(f"Invalid ID type. Valid types: {', '.join(valid_id_types)}")
            
            # Perform reverse lookup
            df = pyb.playerid_reverse_lookup([player_id], key_type=id_type)
            
            if df.empty:
                return f"❌ No player found with {id_type} ID: {player_id}"
            
            # Format response
            player_info = df.iloc[0]
            response = f"""# Player Information

**Name**: {player_info.get('name_first', 'Unknown')} {player_info.get('name_last', 'Unknown')}
**MLB Career**: {player_info.get('mlb_played_first', 'Unknown')} - {player_info.get('mlb_played_last', 'Unknown')}

## Player IDs:
- **MLB AM ID**: {player_info.get('key_mlbam', 'N/A')}
- **FanGraphs ID**: {player_info.get('key_fangraphs', 'N/A')}
- **Baseball Reference ID**: {player_info.get('key_bbref', 'N/A')}

## Additional Details:
"""
            
            # Add any additional columns as details
            for col in df.columns:
                if col not in ['name_first', 'name_last', 'mlb_played_first', 'mlb_played_last', 
                              'key_mlbam', 'key_fangraphs', 'key_bbref']:
                    value = player_info.get(col, 'N/A')
                    response += f"- **{col.replace('_', ' ').title()}**: {value}\n"
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in reverse_lookup_player: {e}")
            return f"❌ Error performing reverse lookup: {e}"

    @mcp.tool()
    def search_players_fuzzy(
        search_term: str,
        min_years_played: int = 1,
        limit: int = 20,
        ctx: Context = None
    ) -> str:
        """
        Search for players using fuzzy matching with additional filters.
        
        Args:
            search_term: Partial name or search term
            min_years_played: Minimum years played in MLB
            limit: Maximum number of results
            
        Returns:
            Formatted string with matching players
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate input
            search_term = validator.sanitize_input(search_term)
            if len(search_term) < 2:
                raise ValidationError("Search term must be at least 2 characters")
            
            min_years_played = validator.validate_numeric_range(
                min_years_played, min_val=0, max_val=30, param_name="min_years_played"
            )
            limit = validator.validate_page_size(limit, max_size=100)
            
            # Perform fuzzy search
            df = pyb.playerid_lookup(search_term, fuzzy=True)
            
            if df.empty:
                return f"❌ No players found matching '{search_term}'"
            
            # Filter by years played if specified
            if min_years_played > 0:
                df = df.copy()
                df['years_played'] = (
                    df['mlb_played_last'].astype(int) - df['mlb_played_first'].astype(int) + 1
                )
                df = df[df['years_played'] >= min_years_played]
            
            if df.empty:
                return f"❌ No players found matching '{search_term}' with at least {min_years_played} years played"
            
            # Sort by relevance (you could implement more sophisticated scoring)
            df = df.head(limit)
            
            # Format response
            title = f"Fuzzy Search Results for '{search_term}'"
            response = data_processor.format_dataframe_as_markdown(df, title)
            
            # Add search insights
            insights = data_processor.create_summary_insights(
                df, f"Searched for players matching '{search_term}'"
            )
            response += f"\n\n### Search Insights\n{insights}"
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in search_players_fuzzy: {e}")
            return f"❌ Error searching players: {e}"

    @mcp.tool()
    def get_player_career_span(
        player_name: str,
        ctx: Context = None
    ) -> str:
        """
        Get a player's career span and basic career information.
        
        Args:
            player_name: Player's name
            
        Returns:
            Formatted string with career span information
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate input
            clean_name = validator.validate_player_name(player_name)
            
            # Look up player
            df = pyb.playerid_lookup(clean_name, fuzzy=True)
            
            if df.empty:
                return f"❌ No players found for '{clean_name}'"
            
            # If multiple results, take the first one but mention alternatives
            player_info = df.iloc[0]
            alternatives_note = ""
            
            if len(df) > 1:
                alternatives = df.iloc[1:]['name_first'] + ' ' + df.iloc[1:]['name_last']
                alternatives_note = f"\n\n*Note: Multiple players found. Also showing: {', '.join(alternatives.head(3).tolist())}*"
            
            # Calculate career span
            first_year = player_info.get('mlb_played_first', 'Unknown')
            last_year = player_info.get('mlb_played_last', 'Unknown')
            
            if first_year != 'Unknown' and last_year != 'Unknown':
                career_length = int(last_year) - int(first_year) + 1
                career_span_text = f"{first_year} - {last_year} ({career_length} seasons)"
            else:
                career_span_text = f"{first_year} - {last_year}"
            
            # Format response
            response = f"""# Career Information: {player_info.get('name_first', '')} {player_info.get('name_last', '')}

## Career Span
**MLB Career**: {career_span_text}

## Player Identifiers
- **MLB AM ID**: {player_info.get('key_mlbam', 'N/A')}
- **FanGraphs ID**: {player_info.get('key_fangraphs', 'N/A')}
- **Baseball Reference ID**: {player_info.get('key_bbref', 'N/A')}

## Quick Facts
- **Birth Year**: {player_info.get('birth_year', 'Unknown')}
- **Career Started**: {first_year}
- **Career Ended**: {last_year}
"""
            
            if first_year != 'Unknown' and last_year != 'Unknown':
                response += f"- **Career Length**: {career_length} seasons\n"
            
            response += alternatives_note
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in get_player_career_span: {e}")
            return f"❌ Error getting career information: {e}"

    logger.info("Player tools registered successfully")
