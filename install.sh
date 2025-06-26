#!/bin/bash

# Pybaseball MCP Server Installation Script
# This script sets up the pybaseball MCP server for use with Claude Desktop and other MCP clients

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.8"
    
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python 3.8 or higher is required. Current version: $python_version"
        exit 1
    fi
    
    log_success "Python $python_version is installed and compatible"
}

# Check if pip is installed
check_pip() {
    log_info "Checking pip installation..."
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed. Please install pip."
        exit 1
    fi
    
    log_success "pip3 is installed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Upgrade pip first
    python3 -m pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        log_success "Dependencies installed from requirements.txt"
    else
        log_warning "requirements.txt not found, installing minimal dependencies..."
        python3 -m pip install mcp pybaseball pandas matplotlib seaborn
    fi
}

# Test the server
test_server() {
    log_info "Testing server installation..."
    
    # Test that the server can be imported
    if python3 -c "import server; print('Server import successful')" 2>/dev/null; then
        log_success "Server can be imported successfully"
    else
        log_error "Failed to import server. Please check the installation."
        return 1
    fi
    
    # Test that required tools can be imported
    if python3 -c "from tools import player_tools, stats_tools, plotting_tools; print('Tools import successful')" 2>/dev/null; then
        log_success "All tools imported successfully"
    else
        log_error "Failed to import tools. Please check the installation."
        return 1
    fi
}

# Create Claude Desktop configuration
setup_claude_desktop() {
    log_info "Setting up Claude Desktop configuration..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        config_dir="$HOME/Library/Application Support/Claude"
        config_file="$config_dir/claude_desktop_config.json"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        config_dir="$HOME/.config/claude"
        config_file="$config_dir/claude_desktop_config.json"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        config_dir="$APPDATA/Claude"
        config_file="$config_dir/claude_desktop_config.json"
    else
        log_warning "Unknown OS. Please manually configure Claude Desktop."
        return 1
    fi
    
    # Create config directory if it doesn't exist
    mkdir -p "$config_dir"
    
    # Get absolute path to current directory
    current_dir=$(pwd)
    server_path="$current_dir/server.py"
    
    # Create or update configuration
    if [ -f "$config_file" ]; then
        log_info "Existing Claude Desktop configuration found. Creating backup..."
        cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create the configuration
    cat > "$config_file" << EOF
{
  "mcpServers": {
    "pybaseball": {
      "command": "python3",
      "args": ["$server_path"],
      "description": "Baseball statistics and analytics server using pybaseball"
    }
  }
}
EOF
    
    log_success "Claude Desktop configuration created at: $config_file"
    log_info "Configuration includes pybaseball MCP server at: $server_path"
}

# Create example usage file
create_examples() {
    log_info "Creating usage examples..."
    
    cat > "EXAMPLES.md" << 'EOF'
# Pybaseball MCP Usage Examples

## Getting Started

Once the server is running and connected to Claude Desktop, you can use natural language queries like:

### Player Lookup Examples
```
Look up Mike Trout's player ID
Find players named Johnson
What is Aaron Judge's career span?
Search for players with last name starting with "Pu"
```

### Statistics Examples
```
Get 2023 batting statistics for players with 500+ plate appearances
Show me Clayton Kershaw's pitching stats from 2020-2023
Compare team batting stats for the Dodgers and Yankees in 2023
What were the top home run hitters in 2022?
```

### Visualization Examples
```
Create a spray chart for Albert Pujols in 2012
Make a comparison chart for Shohei Ohtani and Mike Trout's 2023 batting stats
Generate a heatmap spray chart for Ronald Acuña Jr. in 2023
Compare Aaron Judge and Giancarlo Stanton's home run distributions
```

## Advanced Queries

### Multi-season Analysis
```
Compare Babe Ruth's stats across his career
Show me how Mike Trout's performance has changed over time
Analyze the evolution of strikeout rates in baseball from 2000-2023
```

### Team Analysis
```
Compare National League vs American League offensive stats for 2023
Show me the best pitching rotations by ERA in 2022
Which teams had the best defensive metrics in 2023?
```

### Historical Data
```
Who were the best players in the deadball era?
Compare modern players to players from the 1990s
Show me World Series MVP performances
```

## Tips for Better Results

1. **Be specific with years**: Always specify the season or year range
2. **Use common player names**: "Mike Trout" works better than "Michael Trout"
3. **Specify qualifiers**: e.g., "minimum 300 plate appearances"
4. **Ask for explanations**: "Explain what WAR means in these results"
5. **Request comparisons**: "Compare these players" or "Show me the differences"

## Troubleshooting

If you get "player not found" errors:
- Try different name formats (e.g., "Last, First" or "First Last")
- Use partial names for fuzzy matching
- Check spelling of player names

If data seems incomplete:
- Verify the season/year is correct
- Some advanced stats only available for recent years (2015+)
- Historical data may be limited for older players
EOF

    log_success "Usage examples created in EXAMPLES.md"
}

# Main installation process
main() {
    echo "============================================="
    echo "    Pybaseball MCP Server Installation"
    echo "============================================="
    echo ""
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Run installation steps
    check_python
    check_pip
    install_dependencies
    
    log_info "Testing installation..."
    if test_server; then
        log_success "Server installation test passed!"
    else
        log_error "Server installation test failed. Please check the logs above."
        exit 1
    fi
    
    # Optional Claude Desktop setup
    echo ""
    read -p "Would you like to configure Claude Desktop automatically? (y/N): " setup_claude
    if [[ $setup_claude =~ ^[Yy]$ ]]; then
        setup_claude_desktop
    else
        log_info "Skipping Claude Desktop configuration. You can set it up manually later."
    fi
    
    # Create examples
    create_examples
    
    echo ""
    echo "============================================="
    echo "           Installation Complete!"
    echo "============================================="
    echo ""
    log_success "Pybaseball MCP Server is now installed and ready to use!"
    echo ""
    echo "Next steps:"
    echo "1. Start the server: python3 server.py"
    echo "2. Connect from Claude Desktop or other MCP client"
    echo "3. Check EXAMPLES.md for usage examples"
    echo ""
    echo "For help and documentation, see README.md"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Pybaseball MCP Server Installation Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test-only    Only run tests, don't install"
        echo "  --no-claude    Skip Claude Desktop configuration"
        echo ""
        exit 0
        ;;
    --test-only)
        check_python
        test_server
        exit 0
        ;;
    --no-claude)
        export SKIP_CLAUDE_SETUP=1
        ;;
esac

# Run main installation
main "$@"
