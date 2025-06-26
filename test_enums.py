#!/usr/bin/env python3
"""
Explore pybaseball enums to understand valid values
"""

import pybaseball as pyb

def explore_enums():
    """Explore pybaseball enums"""
    
    print("Exploring pybaseball enums...")
    
    try:
        # Check if we can access the enums module
        if hasattr(pyb, 'enums'):
            print("Found enums module")
            enums_module = pyb.enums
            
            # Look for batting stats enum
            if hasattr(enums_module, 'fangraphs'):
                fg_module = enums_module.fangraphs
                print(f"Fangraphs module attributes: {dir(fg_module)}")
                
                # Look for batting stats enum
                if hasattr(fg_module, 'FangraphsBattingStats'):
                    batting_enum = fg_module.FangraphsBattingStats
                    print(f"FangraphsBattingStats enum members: {list(batting_enum)}")
                    
                    # Print each member with its value
                    for member in batting_enum:
                        print(f"  {member.name} = {member.value}")
                        
                # Look for pitching stats enum
                if hasattr(fg_module, 'FangraphsPitchingStats'):
                    pitching_enum = fg_module.FangraphsPitchingStats
                    print(f"FangraphsPitchingStats enum members: {list(pitching_enum)}")
                    
                    # Print each member with its value
                    for member in pitching_enum:
                        print(f"  {member.name} = {member.value}")
                        
    except Exception as e:
        print(f"Error exploring enums: {e}")
        import traceback
        traceback.print_exc()

def test_with_enum():
    """Test batting stats with actual enum values"""
    
    try:
        from pybaseball.enums.fangraphs import FangraphsBattingStats
        
        print("\\nTesting with actual enum values...")
        
        # Try with standard batting stats
        result = pyb.batting_stats(2024, 2024, stat_columns=FangraphsBattingStats.STANDARD)
        print(f"✅ Batting stats with enum successful: {len(result)} results")
        
        # Test other enum values
        for enum_member in FangraphsBattingStats:
            try:
                result = pyb.batting_stats(2024, 2024, stat_columns=enum_member, qual=1)
                print(f"✅ {enum_member.name}: {len(result)} results")
                break  # Just test one to avoid rate limiting
            except Exception as e:
                print(f"❌ {enum_member.name}: {e}")
                
    except Exception as e:
        print(f"Error testing with enum: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_enums()
    test_with_enum()
