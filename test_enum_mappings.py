#!/usr/bin/env python3
"""
Test what the actual enum values should be for common stat types
"""

import pybaseball as pyb
from pybaseball.enums.fangraphs import FangraphsBattingStats, FangraphsPitchingStats

def test_enum_mappings():
    """Test different enum values to see what works"""
    
    print("Testing batting stats enum mappings...")
    
    # Test common enum mappings for batting
    test_enums = [
        FangraphsBattingStats.COMMON,  # 'c' - likely standard stats
    ]
    
    for enum_val in test_enums:
        try:
            print(f"\\nTesting {enum_val.name} (value: {enum_val.value})...")
            result = pyb.batting_stats(2024, 2024, stat_columns=enum_val, qual=1)
            print(f"✅ Success: {len(result)} results")
            print(f"   Columns: {list(result.columns)[:10]}...")  # Show first 10 columns
            break  # Stop after first success
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\\n" + "="*50)
    print("Testing pitching stats enum mappings...")
    
    # Test common enum mappings for pitching
    test_enums = [
        FangraphsPitchingStats.COMMON,  # 'c' - likely standard stats
    ]
    
    for enum_val in test_enums:
        try:
            print(f"\\nTesting {enum_val.name} (value: {enum_val.value})...")
            result = pyb.pitching_stats(2024, 2024, stat_columns=enum_val, qual=1)
            print(f"✅ Success: {len(result)} results")
            print(f"   Columns: {list(result.columns)[:10]}...")  # Show first 10 columns
            break  # Stop after first success
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_enum_mappings()
