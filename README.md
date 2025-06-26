# Pybaseball MCP Server

A comprehensive Model Context Protocol (MCP) server that provides access to baseball statistics and analytics through the pybaseball library. This server exposes baseball data and visualization tools for use with MCP-compatible clients like Claude Desktop.

## Features

### 🔍 Player Tools
- **Player Lookup**: Find players by name with fuzzy matching
- **Reverse Lookup**: Get player information from IDs
- **Career Information**: View player career spans and details
- **Fuzzy Search**: Advanced player search with filters

### 📊 Statistics Tools  
- **Batting Statistics**: FanGraphs batting stats by season
- **Pitching Statistics**: FanGraphs pitching stats by season
- **Player Range Stats**: Multi-season player statistics
- **Team Statistics**: Team-level batting and pitching data

### 📈 Visualization Tools
- **Spray Charts**: Interactive spray charts for hit distribution
- **Comparison Charts**: Side-by-side player statistical comparisons
- **Multiple Chart Types**: Standard, heatmap, and overlay visualizations

## Installation

### Quick Start (Recommended)

**One-line installation:**
```bash
git clone https://github.com/wsekete/pybaseball-MCP.git && cd pybaseball-MCP && ./install.sh
```

The script will automatically:
- ✅ Check Python compatibility
- ✅ Install all dependencies  
- ✅ Test the installation
- ✅ Configure Claude Desktop (optional)
- ✅ Create usage examples

### Alternative Installation Methods

#### Method 1: Docker (Easiest)
```bash
git clone https://github.com/wsekete/pybaseball-MCP.git
cd pybaseball-MCP
docker-compose up -d
```

#### Method 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/wsekete/pybaseball-MCP.git
cd pybaseball-MCP

# Install dependencies
pip install -r requirements.txt

# Test the installation
python server.py --help
```

#### Method 3: pip Installation (Coming Soon)
```bash
pip install pybaseball-mcp
```

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for cloning)
- Docker (optional, for containerized deployment)

## Usage

### Running the Server

Start the MCP server:
```bash
python server.py
```

The server will start and listen for MCP connections.

### Connecting to Claude Desktop

#### Automatic Configuration (Recommended)
If you used the install script, Claude Desktop should already be configured! Just restart Claude Desktop.

#### Manual Configuration
1. **Locate your Claude Desktop config file:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. **Add the server configuration:**
```json
{
  "mcpServers": {
    "pybaseball": {
      "command": "python3",
      "args": ["/absolute/path/to/pybaseball-MCP/server.py"],
      "description": "Baseball statistics and analytics server"
    }
  }
}
```

3. **Replace `/absolute/path/to/pybaseball-MCP/` with your actual path**
4. **Restart Claude Desktop**

> **💡 Tip**: Use the provided `claude_desktop_config.json` as a template!

### Example Queries

Once connected, you can ask Claude queries like:

#### Player Lookup
- "Look up Mike Trout's player ID"
- "Find players named Johnson with fuzzy matching" 
- "What is Aaron Judge's career span?"

#### Statistics
- "Get 2023 batting statistics for players with 500+ plate appearances"
- "Show me Clayton Kershaw's pitching stats from 2020-2023"
- "Compare team batting stats for the Dodgers and Yankees in 2023"

#### Visualizations
- "Create a spray chart for Albert Pujols in 2012" 
- "Make a comparison chart for Shohei Ohtani and Mike Trout's 2023 batting stats"
- "Generate a heatmap spray chart for Ronald Acuña Jr. in 2023"

## Available Tools

### Player Tools
| Tool | Description |
|------|-------------|
| `lookup_player_id` | Find player IDs by name |
| `reverse_lookup_player` | Get player info from ID |
| `search_players_fuzzy` | Advanced player search |
| `get_player_career_span` | View career information |

### Statistics Tools  
| Tool | Description |
|------|-------------|
| `get_batting_stats` | Season batting statistics |
| `get_pitching_stats` | Season pitching statistics |
| `get_player_batting_stats_range` | Multi-season player stats |
| `get_team_batting_stats` | Team batting statistics |

### Plotting Tools
| Tool | Description |
|------|-------------|
| `create_spray_chart` | Player spray charts |
| `create_stat_comparison_chart` | Player comparison charts |

## Data Sources

This server pulls data from multiple sources via pybaseball:
- **FanGraphs**: Advanced statistics and metrics
- **Baseball Reference**: Traditional statistics  
- **MLB Statcast**: Advanced tracking data
- **Baseball Savant**: Statcast visualizations

## Configuration

### Validation Settings
The server includes robust validation for:
- Player names and IDs
- Season years (1871-present)
- Date ranges (max 5 years)
- Team abbreviations
- Statistical parameters

### Performance Features
- **Caching**: Automatic caching of frequently requested data
- **Error Handling**: Graceful error handling with helpful messages
- **Data Processing**: Intelligent data formatting and insights
- **Visualization**: High-quality charts with contextual information

## Development

### Project Structure
```
pybaseball-mcp-server/
├── server.py              # Main MCP server
├── requirements.txt       # Dependencies
├── tools/                 # Tool implementations
│   ├── player_tools.py    # Player lookup tools
│   ├── stats_tools.py     # Statistics tools
│   └── plotting_tools.py  # Visualization tools
├── utils/                 # Shared utilities
│   ├── data_processing.py # Data formatting
│   └── validation.py      # Input validation
└── README.md
```

### Adding New Tools

To add new tools:

1. Create or modify files in the `tools/` directory
2. Register tools in the appropriate `register_*_tools()` function
3. Import and call the registration function in `server.py`
4. Test the new functionality

### Error Handling

The server includes comprehensive error handling:
- Input validation with helpful error messages
- Graceful handling of missing data
- Fallback suggestions for failed queries
- Detailed logging for debugging

## Troubleshooting

### Common Issues

**"Player not found" errors:**
- Try alternative name formats (e.g., "Last, First")
- Use fuzzy matching options
- Check spelling and common abbreviations

**"No data available" errors:**
- Verify the season/date range is valid
- Check that the player was active during the requested period
- Ensure Statcast data availability (2015+)

**Import/dependency errors:**
- Reinstall requirements: `pip install -r requirements.txt --upgrade`
- Check Python version compatibility
- Verify pybaseball installation

### Performance Tips

- Use appropriate qualifiers (PA/IP minimums) to limit data size
- Cache frequently requested data
- Consider date range limitations for large queries

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## License

This project uses the pybaseball library and follows its licensing terms. Please refer to the pybaseball documentation for data usage guidelines.

## Support

For issues related to:
- **MCP functionality**: Check MCP documentation
- **Baseball data**: Refer to pybaseball documentation  
- **Server issues**: Check the logs and error messages

---

**Built with ❤️ for baseball analytics and MCP**
