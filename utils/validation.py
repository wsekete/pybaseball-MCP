"""
Validation utilities for pybaseball MCP server.

This module provides input validation, error handling, and data validation
functions to ensure robust operation of the MCP server.
"""

import re
from typing import List, Optional, Union, Tuple
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """Handles input validation and data validation for baseball data requests"""
    
    def __init__(self):
        self.valid_teams = {
            'LAA', 'HOU', 'OAK', 'TOR', 'ATL', 'MIL', 'STL', 'CHC', 
            'ARI', 'LAD', 'SF', 'CLE', 'SEA', 'MIA', 'NYM', 'WSH',
            'BAL', 'SD', 'PHI', 'PIT', 'TEX', 'TB', 'BOS', 'CIN',
            'COL', 'KC', 'DET', 'MIN', 'CWS', 'NYY'
        }
        
        self.valid_positions = {
            'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'DH', 'P'
        }
        
        self.valid_stat_sources = {
            'fangraphs', 'baseball_reference', 'bref', 'fg'
        }

    def validate_player_name(self, name: str) -> str:
        """Validate and clean player name input"""
        if not name or not isinstance(name, str):
            raise ValidationError("Player name must be a non-empty string")
        
        # Clean the name
        cleaned_name = name.strip()
        
        if len(cleaned_name) < 2:
            raise ValidationError("Player name must be at least 2 characters long")
        
        if len(cleaned_name) > 50:
            raise ValidationError("Player name is unusually long")
        
        # Check for reasonable characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", cleaned_name):
            raise ValidationError("Player name contains invalid characters")
        
        return cleaned_name

    def validate_season(self, season: Union[int, str]) -> int:
        """Validate season year"""
        try:
            season_int = int(season)
        except (ValueError, TypeError):
            raise ValidationError("Season must be a valid year")
        
        current_year = datetime.now().year
        
        if season_int < 1871:  # First professional baseball season
            raise ValidationError("Season cannot be before 1871")
        
        if season_int > current_year + 1:  # Allow next year for spring training
            raise ValidationError(f"Season cannot be after {current_year + 1}")
        
        return season_int

    def validate_date(self, date_str: str) -> str:
        """Validate date string format"""
        if not date_str or not isinstance(date_str, str):
            raise ValidationError("Date must be a non-empty string")
        
        # Try common date formats
        date_formats = [
            '%Y-%m-%d',      # 2023-01-01
            '%m/%d/%Y',      # 01/01/2023
            '%m-%d-%Y',      # 01-01-2023
            '%Y/%m/%d',      # 2023/01/01
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            raise ValidationError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format")
        
        # Return in standard format
        return parsed_date.strftime('%Y-%m-%d')

    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[str, str]:
        """Validate date range"""
        start = self.validate_date(start_date)
        end = self.validate_date(end_date)
        
        start_dt = datetime.strptime(start, '%Y-%m-%d')
        end_dt = datetime.strptime(end, '%Y-%m-%d')
        
        if start_dt >= end_dt:
            raise ValidationError("Start date must be before end date")
        
        # Check for reasonable range (not more than 5 years)
        if (end_dt - start_dt).days > 365 * 5:
            raise ValidationError("Date range cannot exceed 5 years")
        
        return start, end

    def validate_team(self, team: str) -> str:
        """Validate team abbreviation"""
        if not team or not isinstance(team, str):
            raise ValidationError("Team must be a non-empty string")
        
        team_upper = team.upper().strip()
        
        if team_upper not in self.valid_teams:
            valid_teams_str = ", ".join(sorted(self.valid_teams))
            raise ValidationError(
                f"Invalid team abbreviation: {team}. "
                f"Valid teams: {valid_teams_str}"
            )
        
        return team_upper

    def validate_position(self, position: str) -> str:
        """Validate position abbreviation"""
        if not position or not isinstance(position, str):
            raise ValidationError("Position must be a non-empty string")
        
        position_upper = position.upper().strip()
        
        if position_upper not in self.valid_positions:
            valid_positions_str = ", ".join(sorted(self.valid_positions))
            raise ValidationError(
                f"Invalid position: {position}. "
                f"Valid positions: {valid_positions_str}"
            )
        
        return position_upper

    def validate_stat_source(self, source: str) -> str:
        """Validate statistics source"""
        if not source or not isinstance(source, str):
            raise ValidationError("Source must be a non-empty string")
        
        source_lower = source.lower().strip()
        
        if source_lower not in self.valid_stat_sources:
            valid_sources_str = ", ".join(sorted(self.valid_stat_sources))
            raise ValidationError(
                f"Invalid statistics source: {source}. "
                f"Valid sources: {valid_sources_str}"
            )
        
        return source_lower

    def validate_page_size(self, page_size: Union[int, str], max_size: int = 1000) -> int:
        """Validate page size for data retrieval"""
        try:
            size_int = int(page_size)
        except (ValueError, TypeError):
            raise ValidationError("Page size must be a valid integer")
        
        if size_int < 1:
            raise ValidationError("Page size must be at least 1")
        
        if size_int > max_size:
            raise ValidationError(f"Page size cannot exceed {max_size}")
        
        return size_int

    def validate_statcast_params(self, start_dt: str, end_dt: str) -> Tuple[str, str]:
        """Validate parameters specific to Statcast data requests"""
        start, end = self.validate_date_range(start_dt, end_dt)
        
        # Statcast data is only available from 2015 onwards
        start_dt_obj = datetime.strptime(start, '%Y-%m-%d')
        if start_dt_obj.year < 2015:
            raise ValidationError("Statcast data is only available from 2015 onwards")
        
        return start, end

    def validate_numeric_range(self, value: Union[int, float, str], 
                             min_val: Optional[float] = None,
                             max_val: Optional[float] = None,
                             param_name: str = "parameter") -> float:
        """Validate numeric parameter within specified range"""
        try:
            numeric_val = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{param_name} must be a valid number")
        
        if min_val is not None and numeric_val < min_val:
            raise ValidationError(f"{param_name} must be at least {min_val}")
        
        if max_val is not None and numeric_val > max_val:
            raise ValidationError(f"{param_name} cannot exceed {max_val}")
        
        return numeric_val

    def validate_boolean(self, value: Union[bool, str], param_name: str = "parameter") -> bool:
        """Validate boolean parameter"""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on'):
                return True
            elif value_lower in ('false', '0', 'no', 'off'):
                return False
        
        raise ValidationError(f"{param_name} must be a boolean value (true/false)")

    def sanitize_input(self, text: str) -> str:
        """Sanitize text input to prevent issues"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove potential problematic characters
        sanitized = re.sub(r'[<>"\';]', '', text)
        sanitized = sanitized.strip()
        
        return sanitized

    def validate_and_suggest_player_name(self, name: str) -> Tuple[str, List[str]]:
        """Validate player name and provide suggestions for common issues"""
        cleaned_name = self.validate_player_name(name)
        suggestions = []
        
        # Common name format suggestions
        if ',' not in cleaned_name and len(cleaned_name.split()) >= 2:
            parts = cleaned_name.split()
            if len(parts) == 2:
                suggestions.append(f"{parts[1]}, {parts[0]}")  # "First Last" -> "Last, First"
        
        # Check for common abbreviations that should be spelled out
        abbreviations = {
            'jr': 'Jr.',
            'sr': 'Sr.',
            'ii': 'II',
            'iii': 'III'
        }
        
        for abbr, full in abbreviations.items():
            if abbr.lower() in cleaned_name.lower() and full not in cleaned_name:
                suggested = cleaned_name.replace(abbr, full)
                suggestions.append(suggested)
        
        return cleaned_name, suggestions
