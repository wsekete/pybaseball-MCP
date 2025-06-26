#!/usr/bin/env python3
"""
Direct test of pybaseball functions to diagnose issues
"""

import sys
import traceback
import pybaseball as pyb

def test_basic_functions():
    """Test basic pybaseball functions"""
    
    print("Testing pybaseball basic functions...")
    
    # Test 1: Player lookup (this was working)
    try:
        print("1. Testing player lookup...")
        result = pyb.playerid_lookup("Mike Trout", fuzzy=True)
        print(f"   ✅ Player lookup successful: {len(result)} results")
    except Exception as e:
        print(f"   ❌ Player lookup failed: {e}")
        traceback.print_exc()
    
    # Test 2: Batting stats with default parameters
    try:
        print("2. Testing batting stats (basic call)...")
        result = pyb.batting_stats(2024, 2024)
        print(f"   ✅ Basic batting stats successful: {len(result)} results")
    except Exception as e:
        print(f"   ❌ Basic batting stats failed: {e}")
        traceback.print_exc()
    
    # Test 3: Batting stats with stat_columns parameter
    try:
        print("3. Testing batting stats with stat_columns...")
        result = pyb.batting_stats(2024, 2024, stat_columns='standard')
        print(f"   ✅ Batting stats with stat_columns successful: {len(result)} results")
    except Exception as e:
        print(f"   ❌ Batting stats with stat_columns failed: {e}")
        traceback.print_exc()
    
    # Test 4: Check what stat_columns options are available
    try:
        print("4. Testing batting stats function signature...")
        import inspect
        sig = inspect.signature(pyb.batting_stats)
        print(f"   Function signature: {sig}")
        
        # Try to get the function's docstring
        if pyb.batting_stats.__doc__:
            print(f"   Docstring preview: {pyb.batting_stats.__doc__[:200]}...")
    except Exception as e:
        print(f"   ❌ Function inspection failed: {e}")
    
    # Test 5: Check if there are any enums or constants
    try:
        print("5. Checking pybaseball module attributes...")
        import pybaseball
        attrs = [attr for attr in dir(pybaseball) if 'stat' in attr.lower() or 'enum' in attr.lower()]
        if attrs:
            print(f"   Found stat-related attributes: {attrs}")
        else:
            print(f"   No obvious stat-related enums found")
    except Exception as e:
        print(f"   ❌ Module inspection failed: {e}")

if __name__ == "__main__":
    test_basic_functions()
