#!/usr/bin/env python3
"""
Test the fixed pybaseball MCP functions
"""

import sys
import os
sys.path.append('/Users/wseke/Documents/pybaseball-mcp-server')

from tools.stats_tools import register_stats_tools
from tools.plotting_tools import register_plotting_tools  
from mcp.server.fastmcp import FastMCP
from utils.data_processing import DataProcessor
from utils.validation import Validator

# Mock context for testing
class MockContext:
    def __init__(self):
        self.request_context = MockRequestContext()

class MockRequestContext:
    def __init__(self):
        self.lifespan_context = MockLifespanContext()

class MockLifespanContext:
    def __init__(self):
        self.validator = Validator()
        self.data_processor = DataProcessor()

def test_batting_stats():
    """Test batting stats function directly"""
    
    print("Testing batting stats function...")
    
    # Create mock MCP server for function registration
    mcp = FastMCP("test")
    register_stats_tools(mcp)
    
    # Find the batting stats tool
    batting_tool = None
    for tool_name, tool_func in mcp._tools.items():
        if 'batting_stats' in tool_name:
            batting_tool = tool_func
            break
    
    if not batting_tool:
        print("❌ Batting stats tool not found")
        return
    
    try:
        # Test with mock context
        ctx = MockContext()
        result = batting_tool(season=2024, qual=50, ctx=ctx)
        
        if "❌" in result:
            print(f"❌ Batting stats test failed: {result}")
        else:
            print("✅ Batting stats test successful!")
            print(f"Result length: {len(result)} characters")
            # Show first few lines
            lines = result.split('\\n')[:5]
            for line in lines:
                print(f"   {line}")
            
    except Exception as e:
        print(f"❌ Batting stats test error: {e}")
        import traceback
        traceback.print_exc()

def test_plotting_tools():
    """Test that plotting tools load without errors"""
    
    print("\\nTesting plotting tools...")
    
    try:
        mcp = FastMCP("test")
        register_plotting_tools(mcp)
        print("✅ Plotting tools registered successfully")
        
    except Exception as e:
        print(f"❌ Plotting tools test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_batting_stats()
    test_plotting_tools()
