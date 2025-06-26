#!/usr/bin/env python3
"""
Test the correct way to pass enum values to pybaseball
"""

import pybaseball as pyb
from pybaseball.enums.fangraphs import FangraphsBattingStats, FangraphsPitchingStats

def test_list_of_enums():
    """Test passing lists of enum values"""
    
    print("Testing with list of enum values...")
    
    # Test with a list containing COMMON
    try:
        print("\\nTesting batting with [COMMON]...")
        result = pyb.batting_stats(2024, 2024, stat_columns=[FangraphsBattingStats.COMMON], qual=1)
        print(f"✅ Success: {len(result)} results")
        print(f"   Columns: {list(result.columns)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test with a list of basic stats
    try:
        print("\\nTesting batting with basic stats...")
        basic_stats = [
            FangraphsBattingStats.NAME,
            FangraphsBattingStats.TEAM, 
            FangraphsBattingStats.AVG,
            FangraphsBattingStats.OBP,
            FangraphsBattingStats.SLG,
            FangraphsBattingStats.HR,
            FangraphsBattingStats.RBI
        ]
        result = pyb.batting_stats(2024, 2024, stat_columns=basic_stats, qual=1)
        print(f"✅ Success: {len(result)} results")
        print(f"   Columns: {list(result.columns)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test what happens with no stat_columns parameter
    try:
        print("\\nTesting batting with no stat_columns (default)...")
        result = pyb.batting_stats(2024, 2024, qual=1)
        print(f"✅ Success: {len(result)} results")
        print(f"   Columns: {list(result.columns)[:10]}...")  # Show first 10 columns
    except Exception as e:
        print(f"❌ Failed: {e}")

def test_pitching_similarly():
    """Test pitching stats similarly"""
    
    print("\\n" + "="*50)
    print("Testing pitching stats...")
    
    # Test with no stat_columns parameter (default)
    try:
        print("\\nTesting pitching with no stat_columns (default)...")
        result = pyb.pitching_stats(2024, 2024, qual=1)
        print(f"✅ Success: {len(result)} results")
        print(f"   Columns: {list(result.columns)[:10]}...")  # Show first 10 columns
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_list_of_enums()
    test_pitching_similarly()
