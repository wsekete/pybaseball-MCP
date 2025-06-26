"""
Data processing utilities for pybaseball MCP server.

This module provides utilities for processing and formatting baseball data
from various sources including FanGraphs, Baseball Reference, and Statcast.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import base64
import io
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data processing and formatting for baseball statistics"""
    
    def __init__(self):
        self.team_abbreviations = {
            'LAA': 'Los Angeles Angels',
            'HOU': 'Houston Astros',
            'OAK': 'Oakland Athletics',
            'TOR': 'Toronto Blue Jays',
            'ATL': 'Atlanta Braves',
            'MIL': 'Milwaukee Brewers',
            'STL': 'St. Louis Cardinals',
            'CHC': 'Chicago Cubs',
            'ARI': 'Arizona Diamondbacks',
            'LAD': 'Los Angeles Dodgers',
            'SF': 'San Francisco Giants',
            'CLE': 'Cleveland Guardians',
            'SEA': 'Seattle Mariners',
            'MIA': 'Miami Marlins',
            'NYM': 'New York Mets',
            'WSH': 'Washington Nationals',
            'BAL': 'Baltimore Orioles',
            'SD': 'San Diego Padres',
            'PHI': 'Philadelphia Phillies',
            'PIT': 'Pittsburgh Pirates',
            'TEX': 'Texas Rangers',
            'TB': 'Tampa Bay Rays',
            'BOS': 'Boston Red Sox',
            'CIN': 'Cincinnati Reds',
            'COL': 'Colorado Rockies',
            'KC': 'Kansas City Royals',
            'DET': 'Detroit Tigers',
            'MIN': 'Minnesota Twins',
            'CWS': 'Chicago White Sox',
            'NYY': 'New York Yankees'
        }

    def format_dataframe_as_markdown(self, df: pd.DataFrame, title: str = "") -> str:
        """Convert a pandas DataFrame to formatted markdown table"""
        if df.empty:
            return f"## {title}\n\nNo data available."
        
        # Round numeric columns to reasonable precision
        df_formatted = df.copy()
        for col in df_formatted.select_dtypes(include=[np.number]).columns:
            if df_formatted[col].dtype == 'float64':
                df_formatted[col] = df_formatted[col].round(3)
        
        markdown = f"## {title}\n\n" if title else ""
        markdown += df_formatted.to_markdown(index=False, tablefmt="pipe")
        return markdown

    def add_statistical_context(self, df: pd.DataFrame, metric_col: str) -> str:
        """Add statistical context to data (percentiles, league averages, etc.)"""
        if df.empty or metric_col not in df.columns:
            return ""
        
        values = df[metric_col].dropna()
        if len(values) == 0:
            return ""
        
        stats = {
            'count': len(values),
            'mean': values.mean(),
            'median': values.median(),
            'std': values.std(),
            'min': values.min(),
            'max': values.max(),
            'q25': values.quantile(0.25),
            'q75': values.quantile(0.75)
        }
        
        context = f"""
### Statistical Summary for {metric_col}
- **Count**: {stats['count']}
- **Average**: {stats['mean']:.3f}
- **Median**: {stats['median']:.3f}
- **Range**: {stats['min']:.3f} - {stats['max']:.3f}
- **25th-75th Percentile**: {stats['q25']:.3f} - {stats['q75']:.3f}
"""
        return context

    def format_player_stats_response(self, df: pd.DataFrame, player_name: str, 
                                   season: int, stat_type: str) -> str:
        """Format player statistics response with context"""
        if df.empty:
            return f"No {stat_type} statistics found for {player_name} in {season}."
        
        # Main stats table
        title = f"{player_name} - {season} {stat_type.title()} Statistics"
        response = self.format_dataframe_as_markdown(df, title)
        
        # Add context for key metrics
        key_metrics = {
            'batting': ['AVG', 'OBP', 'SLG', 'OPS', 'wRC+', 'HR', 'RBI'],
            'pitching': ['ERA', 'WHIP', 'K/9', 'BB/9', 'FIP', 'xFIP', 'WAR']
        }
        
        if stat_type in key_metrics:
            for metric in key_metrics[stat_type]:
                if metric in df.columns:
                    response += self.add_statistical_context(df, metric)
                    break  # Add context for first available key metric
        
        return response

    def resolve_team_name(self, team_input: str) -> str:
        """Resolve team name from abbreviation or full name"""
        team_upper = team_input.upper()
        
        # Check if it's already an abbreviation
        if team_upper in self.team_abbreviations:
            return team_upper
        
        # Check if it's a full name that maps to an abbreviation
        for abbr, full_name in self.team_abbreviations.items():
            if team_input.lower() in full_name.lower():
                return abbr
        
        # Return original if no match found
        return team_input

    def create_summary_insights(self, df: pd.DataFrame, context: str = "") -> str:
        """Generate insights and summary from data"""
        if df.empty:
            return "No data available for analysis."
        
        insights = []
        
        # Basic data insights
        insights.append(f"📊 **Dataset contains {len(df)} records**")
        
        if context:
            insights.append(f"🔍 **Context**: {context}")
        
        # Identify notable values in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            if not df[col].isna().all():
                max_val = df[col].max()
                min_val = df[col].min()
                max_idx = df[col].idxmax()
                min_idx = df[col].idxmin()
                
                # Get player/team name if available
                name_col = None
                for possible_name in ['Name', 'Player', 'Team', 'name', 'player', 'team']:
                    if possible_name in df.columns:
                        name_col = possible_name
                        break
                
                if name_col:
                    max_name = df.loc[max_idx, name_col]
                    min_name = df.loc[min_idx, name_col]
                    insights.append(f"🏆 **{col}**: Highest = {max_val} ({max_name}), Lowest = {min_val} ({min_name})")
                else:
                    insights.append(f"📈 **{col}**: Range = {min_val} to {max_val}")
        
        return "\n".join(insights)

    def encode_image_to_base64(self, image_buffer: io.BytesIO) -> str:
        """Encode image buffer to base64 string"""
        image_buffer.seek(0)
        img_str = base64.b64encode(image_buffer.read()).decode()
        return f"data:image/png;base64,{img_str}"

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column names"""
        df_clean = df.copy()
        
        # Remove special characters and standardize
        df_clean.columns = df_clean.columns.str.replace(r'[^\w\s]', '', regex=True)
        df_clean.columns = df_clean.columns.str.replace(r'\s+', '_', regex=True)
        df_clean.columns = df_clean.columns.str.strip()
        
        return df_clean

    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate that date range is reasonable"""
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            # Check that start is before end
            if start >= end:
                return False
            
            # Check that range is not too large (e.g., more than 5 years)
            if (end - start).days > 365 * 5:
                return False
            
            return True
        except:
            return False
