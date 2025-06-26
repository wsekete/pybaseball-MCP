"""
Statistics tools for pybaseball MCP server.

These tools provide access to batting, pitching, and fielding statistics
from various sources including FanGraphs and Baseball Reference.
"""

import logging
from typing import Optional, Union, List

from mcp.server.fastmcp import FastMCP, Context
import pybaseball as pyb
from utils.data_processing import DataProcessor
from utils.validation import Validator, ValidationError

logger = logging.getLogger(__name__)


def _map_stat_columns_to_enum(stat_type_str: str, category: str) -> Optional[List]:
    """
    Future implementation: Map string stat types to proper pybaseball enums.
    
    Args:
        stat_type_str: String like "standard", "advanced", etc.
        category: "batting" or "pitching"
        
    Returns:
        List of enum values or None to use defaults
        
    TODO: Implement proper enum mapping once we understand the pybaseball enum system better
    """
    # For now, return None to use defaults
    # In future versions, this could map to specific enum combinations
    
    # Example future implementation:
    # if category == "batting":
    #     from pybaseball.enums.fangraphs import FangraphsBattingStats
    #     if stat_type_str == "standard":
    #         return [FangraphsBattingStats.NAME, FangraphsBattingStats.TEAM, 
    #                FangraphsBattingStats.AVG, FangraphsBattingStats.OBP, ...]
    
    return None


def register_stats_tools(mcp: FastMCP):
    """Register all statistics-related tools with the MCP server"""
    
    @mcp.tool()
    def get_batting_stats(
        season: int,
        split_seasons: bool = True,
        stat_columns: str = "standard",
        league: str = "all",
        qual: int = 50,
        ctx: Context = None
    ) -> str:
        """
        Get batting statistics for a season from FanGraphs.
        
        Args:
            season: Season year (e.g., 2023)
            split_seasons: Whether to split seasons (for trades)
            stat_columns: Type of stats ("standard", "advanced", "batted_ball", "more", "pitch_type", "plate_discipline")
            league: League filter ("all", "al", "nl")
            qual: Minimum plate appearances qualifier
            
        Returns:
            Formatted batting statistics table with insights
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            season = validator.validate_season(season)
            qual = validator.validate_numeric_range(qual, min_val=0, max_val=700, param_name="qual")
            
            logger.info(f"Getting batting stats for season {season}, qual {qual}, stat_columns {stat_columns}")
            
            # Handle stat_columns parameter - use default if "standard", otherwise investigate enums
            actual_stat_columns = None  # Use pybaseball default
            
            if stat_columns != "standard":
                # For now, log the request but use default columns
                # TODO: Implement proper enum mapping for advanced stat types
                logger.warning(f"Advanced stat_columns '{stat_columns}' requested but using default columns for now")
                # In future versions, we can implement:
                # stat_columns = _map_stat_columns_to_enum(stat_columns, "batting")
            
            valid_leagues = ["all", "al", "nl"]
            league = league.lower()
            if league not in valid_leagues:
                raise ValidationError(f"Invalid league. Valid options: {', '.join(valid_leagues)}")
            
            # Get batting stats with comprehensive error handling
            try:
                logger.info(f"Calling pybaseball.batting_stats with params: season={season}, split_seasons={split_seasons}, league={league}, qual={qual}")
                
                # Call pybaseball without stat_columns for now (uses defaults)
                df = pyb.batting_stats(
                    start_season=season,
                    end_season=season,
                    split_seasons=split_seasons,
                    league=league,
                    qual=qual
                    # Note: stat_columns parameter omitted to use defaults
                )
                logger.info(f"Successfully retrieved {len(df) if not df.empty else 0} batting records")
            except Exception as pyb_error:
                logger.error(f"Pybaseball error: {type(pyb_error).__name__}: {pyb_error}")
                return f"❌ Error fetching batting statistics from pybaseball: {pyb_error}"
            
            if df.empty:
                return f"❌ No batting statistics found for {season} with qualifier {qual}+"
            
            # Format response
            title = f"{season} Batting Statistics (Default Stats) - Min {qual} PA"
            response = data_processor.format_dataframe_as_markdown(df, title)
            
            # Add insights
            insights = data_processor.create_summary_insights(
                df, f"{season} season with {qual}+ plate appearances"
            )
            response += f"\n\n### Season Insights\n{insights}"
            
            # Add context about the stats
            response += f"\n\n**About Default Stats**: Standard batting statistics including traditional metrics like AVG, OBP, SLG, HR, RBI, and advanced metrics like WAR."
            
            if stat_columns != "standard":
                response += f"\n\n*Note: Advanced stat type '{stat_columns}' was requested but default columns are used in this version.*"
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in get_batting_stats: {e}")
            return f"❌ Error retrieving batting statistics: {e}"

    @mcp.tool()
    def get_pitching_stats(
        season: int,
        split_seasons: bool = True,
        stat_columns: str = "standard",
        league: str = "all",
        qual: int = 20,
        ctx: Context = None
    ) -> str:
        """
        Get pitching statistics for a season from FanGraphs.
        
        Args:
            season: Season year (e.g., 2023)
            split_seasons: Whether to split seasons (for trades)
            stat_columns: Type of stats ("standard", "advanced", "batted_ball", "more", "pitch_type", "plate_discipline")
            league: League filter ("all", "al", "nl")
            qual: Minimum innings pitched qualifier
            
        Returns:
            Formatted pitching statistics table with insights
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            season = validator.validate_season(season)
            qual = validator.validate_numeric_range(qual, min_val=0, max_val=300, param_name="qual")
            
            logger.info(f"Getting pitching stats for season {season}, qual {qual}, stat_columns {stat_columns}")
            
            # Handle stat_columns parameter - use default if "standard", otherwise investigate enums
            actual_stat_columns = None  # Use pybaseball default
            
            if stat_columns != "standard":
                # For now, log the request but use default columns
                # TODO: Implement proper enum mapping for advanced stat types
                logger.warning(f"Advanced stat_columns '{stat_columns}' requested but using default columns for now")
                # In future versions, we can implement:
                # stat_columns = _map_stat_columns_to_enum(stat_columns, "pitching")
            
            valid_leagues = ["all", "al", "nl"]
            league = league.lower()
            if league not in valid_leagues:
                raise ValidationError(f"Invalid league. Valid options: {', '.join(valid_leagues)}")
            
            # Get pitching stats with comprehensive error handling
            try:
                logger.info(f"Calling pybaseball.pitching_stats with params: season={season}, split_seasons={split_seasons}, league={league}, qual={qual}")
                
                # Call pybaseball without stat_columns for now (uses defaults)
                df = pyb.pitching_stats(
                    start_season=season,
                    end_season=season,
                    split_seasons=split_seasons,
                    league=league,
                    qual=qual
                    # Note: stat_columns parameter omitted to use defaults
                )
                logger.info(f"Successfully retrieved {len(df) if not df.empty else 0} pitching records")
            except Exception as pyb_error:
                logger.error(f"Pybaseball error: {type(pyb_error).__name__}: {pyb_error}")
                return f"❌ Error fetching pitching statistics from pybaseball: {pyb_error}"
            
            if df.empty:
                return f"❌ No pitching statistics found for {season} with qualifier {qual}+ IP"
            
            # Format response
            title = f"{season} Pitching Statistics (Default Stats) - Min {qual} IP"
            response = data_processor.format_dataframe_as_markdown(df, title)
            
            # Add insights
            insights = data_processor.create_summary_insights(
                df, f"{season} season with {qual}+ innings pitched"
            )
            response += f"\n\n### Season Insights\n{insights}"
            
            # Add context about the stats
            response += f"\n\n**About Default Stats**: Standard pitching statistics including traditional metrics like ERA, WHIP, K/9, BB/9, and advanced metrics like WAR."
            
            if stat_columns != "standard":
                response += f"\n\n*Note: Advanced stat type '{stat_columns}' was requested but default columns are used in this version.*"
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in get_pitching_stats: {e}")
            return f"❌ Error retrieving pitching statistics: {e}"

    @mcp.tool()
    def get_player_batting_stats_range(
        start_season: int,
        end_season: int,
        player_name: str,
        ctx: Context = None
    ) -> str:
        """
        Get a specific player's batting statistics over a range of seasons.
        
        Args:
            start_season: Starting season year
            end_season: Ending season year
            player_name: Player's name
            
        Returns:
            Formatted player batting statistics with year-over-year analysis
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            start_season = validator.validate_season(start_season)
            end_season = validator.validate_season(end_season)
            clean_name = validator.validate_player_name(player_name)
            
            if start_season > end_season:
                raise ValidationError("Start season must be before or equal to end season")
            
            # Look up player first
            player_df = pyb.playerid_lookup(clean_name, fuzzy=True)
            if player_df.empty:
                return f"❌ Player '{clean_name}' not found"
            
            player_info = player_df.iloc[0]
            player_id = player_info.get('key_fangraphs')
            
            if not player_id:
                return f"❌ No FanGraphs ID found for {clean_name}"
            
            # Get batting stats for the range
            df = pyb.batting_stats_range(
                start_dt=f"{start_season}-03-01",
                end_dt=f"{end_season}-11-01"
            )
            
            # Filter for our player
            player_stats = df[df['Name'].str.contains(clean_name, case=False, na=False)]
            
            if player_stats.empty:
                return f"❌ No batting statistics found for {clean_name} from {start_season} to {end_season}"
            
            # Format response
            title = f"{clean_name} Batting Statistics ({start_season}-{end_season})"
            response = data_processor.format_dataframe_as_markdown(player_stats, title)
            
            # Add career insights for this period
            if len(player_stats) > 1:
                numeric_cols = player_stats.select_dtypes(include=['number']).columns
                summary_stats = {}
                
                for col in ['AVG', 'OBP', 'SLG', 'OPS', 'HR', 'RBI']:
                    if col in numeric_cols:
                        summary_stats[col] = {
                            'avg': player_stats[col].mean(),
                            'best': player_stats[col].max(),
                            'worst': player_stats[col].min()
                        }
                
                if summary_stats:
                    response += f"\n\n### Career Summary ({start_season}-{end_season})\n"
                    for stat, values in summary_stats.items():
                        response += f"- **{stat}**: Avg {values['avg']:.3f}, Best {values['best']:.3f}, Worst {values['worst']:.3f}\n"
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in get_player_batting_stats_range: {e}")
            return f"❌ Error retrieving player batting statistics: {e}"

    @mcp.tool()
    def get_team_batting_stats(
        season: int,
        team: Optional[str] = None,
        league: str = "all",
        ctx: Context = None
    ) -> str:
        """
        Get team batting statistics for a season.
        
        Args:
            season: Season year
            team: Specific team abbreviation (optional)
            league: League filter ("all", "al", "nl")
            
        Returns:
            Formatted team batting statistics
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            season = validator.validate_season(season)
            
            if team:
                team = validator.validate_team(team)
            
            valid_leagues = ["all", "al", "nl"]
            league = league.lower()
            if league not in valid_leagues:
                raise ValidationError(f"Invalid league. Valid options: {', '.join(valid_leagues)}")
            
            # Get team batting stats
            df = pyb.team_batting(season, league=league)
            
            if df.empty:
                return f"❌ No team batting statistics found for {season}"
            
            # Filter for specific team if requested
            if team:
                team_stats = df[df['Team'] == team]
                if team_stats.empty:
                    return f"❌ No batting statistics found for {team} in {season}"
                df = team_stats
                title = f"{team} {season} Batting Statistics"
            else:
                title = f"{season} Team Batting Statistics"
            
            # Format response
            response = data_processor.format_dataframe_as_markdown(df, title)
            
            # Add league insights
            if team is None:
                insights = data_processor.create_summary_insights(
                    df, f"{season} team batting performance"
                )
                response += f"\n\n### League Insights\n{insights}"
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in get_team_batting_stats: {e}")
            return f"❌ Error retrieving team batting statistics: {e}"

    logger.info("Statistics tools registered successfully")
