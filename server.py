#!/usr/bin/env python3
"""
Pybaseball MCP Server

A comprehensive MCP server that provides access to baseball statistics and data
through the pybaseball library. This server exposes tools for:
- Player lookup and identification
- Batting and pitching statistics
- Statcast data and analytics
- Team statistics and standings
- Data visualization and charts
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio
import sys
import os

from mcp.server.fastmcp import FastMCP
from tools.player_tools import register_player_tools
from tools.stats_tools import register_stats_tools
from tools.plotting_tools import register_plotting_tools
from utils.data_processing import DataProcessor
from utils.validation import Validator


# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context for managing shared resources"""
    data_processor: DataProcessor
    validator: Validator
    cache: Dict[str, Any]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with shared resources"""
    logger.info("🚀 Initializing pybaseball MCP server...")
    
    # Initialize shared resources
    data_processor = DataProcessor()
    validator = Validator()
    cache = {}
    
    context = AppContext(
        data_processor=data_processor,
        validator=validator,
        cache=cache
    )
    
    logger.info("✅ Server context initialized successfully")
    logger.info("🎯 Server is ready to accept connections")
    
    try:
        yield context
    finally:
        logger.info("🛑 Shutting down pybaseball MCP server...")
        # Clean up resources if needed
        cache.clear()
        logger.info("💾 Cleanup completed")


# Create the FastMCP server
mcp = FastMCP(
    "pybaseball-mcp-server",
    description="Comprehensive baseball statistics and analytics server using pybaseball",
    lifespan=app_lifespan
)


# Health check resource
@mcp.resource("health://status")
def health_check() -> str:
    """Server health check"""
    return "✅ Pybaseball MCP Server is running"


# Server info resource
@mcp.resource("info://server")
def server_info() -> str:
    """Server information and capabilities"""
    return """
# Pybaseball MCP Server

## Available Tool Categories:
- **Player Tools**: Player lookup, identification, and basic info
- **Stats Tools**: Batting, pitching, and fielding statistics
- **Plotting Tools**: Data visualization and charts

## Data Sources:
- FanGraphs
- Baseball Reference
- MLB Statcast
- Baseball Savant

## Features:
- Comprehensive player statistics
- Advanced analytics and metrics
- Data visualization capabilities
- Historical data access
- Real-time season data
"""


def main():
    """Main entry point for the server"""
    try:
        logger.info("🔧 Starting server initialization...")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        logger.info(f"🐍 Python version: {sys.version}")
        
        # Register all tool categories
        logger.info("📝 Registering tool categories...")
        register_player_tools(mcp)
        register_stats_tools(mcp)
        register_plotting_tools(mcp)
        
        logger.info("✅ All tools registered successfully")
        logger.info("🌐 Starting MCP server...")
        logger.info("⏳ Server will now listen for connections...")
        logger.info("📡 Use Ctrl+C to stop the server")
        
        # Run the server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        logger.exception("Full error details:")
        raise


if __name__ == "__main__":
    main()
