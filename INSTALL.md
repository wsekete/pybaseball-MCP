# Installation Guide

This guide provides detailed instructions for installing and setting up the Pybaseball MCP Server.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 500MB free space

### Required Software
- Python 3.8+ with pip
- Git (optional, for cloning)
- Claude Desktop (for Claude integration)

## Installation Methods

### Method 1: Automated Installation (Recommended)

The easiest way to install the Pybaseball MCP Server:

```bash
# Clone the repository
git clone https://github.com/wsekete/pybaseball-MCP.git
cd pybaseball-MCP

# Run the installation script
./install.sh
```

The script will:
- Check Python installation
- Install dependencies
- Test the server
- Configure Claude Desktop (optional)
- Create usage examples

### Method 2: Manual Installation

If you prefer to install manually:

#### Step 1: Download the Code
```bash
# Option A: Clone with Git
git clone https://github.com/wsekete/pybaseball-MCP.git
cd pybaseball-MCP

# Option B: Download ZIP
# Download from GitHub and extract
```

#### Step 2: Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install individual packages
pip install mcp pybaseball pandas matplotlib seaborn pillow
```

#### Step 3: Test Installation
```bash
# Test the server
python server.py --help

# Test imports
python -c "import server; print('Installation successful!')"
```

### Method 3: Docker Installation

For containerized deployment:

```bash
# Clone the repository
git clone https://github.com/wsekete/pybaseball-MCP.git
cd pybaseball-MCP

# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t pybaseball-mcp .
docker run -p 3000:3000 pybaseball-mcp
```

### Method 4: pip Installation (Coming Soon)

Once published to PyPI:
```bash
pip install pybaseball-mcp
```

## Configuration

### Claude Desktop Setup

#### Automatic Configuration
The install script can configure Claude Desktop automatically. When prompted, choose 'y':
```
Would you like to configure Claude Desktop automatically? (y/N): y
```

#### Manual Configuration

1. **Locate the configuration file:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. **Add the server configuration:**
   ```json
   {
     "mcpServers": {
       "pybaseball": {
         "command": "python3",
         "args": ["/absolute/path/to/pybaseball-mcp-server/server.py"],
         "description": "Baseball statistics and analytics server"
       }
     }
   }
   ```

3. **Replace the path** with your actual installation path.

4. **Restart Claude Desktop** to apply changes.

### Environment Variables (Optional)

Create a `.env` file for custom configuration:
```bash
# Cache settings
PYBASEBALL_CACHE_DIR=/path/to/cache
PYBASEBALL_CACHE_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/path/to/logs/pybaseball-mcp.log

# Performance
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
```

## Verification

### Test the Installation

1. **Basic functionality test:**
   ```bash
   python server.py --test
   ```

2. **Claude Desktop test:**
   - Open Claude Desktop
   - Look for the MCP icon in the interface
   - Try a query: "Look up Mike Trout's player ID"

3. **Manual server test:**
   ```bash
   # Start the server
   python server.py

   # You should see:
   # ✅ Pybaseball MCP Server is running
   # 📡 Use Ctrl+C to stop the server
   ```

### Troubleshooting Common Issues

#### Import Errors
```bash
# If you get import errors, try:
pip install --upgrade -r requirements.txt

# Or reinstall specific packages:
pip uninstall pybaseball && pip install pybaseball
```

#### Permission Errors
```bash
# On macOS/Linux, you might need:
sudo pip install -r requirements.txt

# Or use user installation:
pip install --user -r requirements.txt
```

#### Claude Desktop Not Recognizing Server
1. Check the configuration file path
2. Verify the server path is absolute
3. Test the server independently
4. Restart Claude Desktop

#### Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.9 server.py
```

## Development Setup

For developers who want to contribute:

### Additional Dependencies
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black isort flake8 mypy

# Or install with dev extras (when using pip package)
pip install "pybaseball-mcp[dev]"
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run checks manually
pre-commit run --all-files
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tools --cov=utils

# Run specific test file
pytest test_server.py
```

## Performance Optimization

### Caching
The server automatically caches frequently requested data. To optimize:

1. **Set cache directory:**
   ```bash
   export PYBASEBALL_CACHE_DIR=/path/to/fast/storage
   ```

2. **Pre-populate cache:**
   ```bash
   python -c "import pybaseball as pyb; pyb.cache.enable()"
   ```

### Memory Usage
For large datasets:
- Use smaller date ranges
- Apply appropriate filters (minimum PA/IP)
- Consider pagination for large results

## Security Considerations

### Data Privacy
- The server processes publicly available baseball statistics
- No personal data is collected or stored
- All data comes from official baseball sources

### Network Security
- Server runs locally by default
- Uses MCP protocol over stdio (secure)
- No external network access required during normal operation

## Updates and Maintenance

### Updating the Server
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the server
```

### Monitoring
Check logs for issues:
```bash
# View recent logs
tail -f /path/to/logs/pybaseball-mcp.log

# Check for errors
grep ERROR /path/to/logs/pybaseball-mcp.log
```

## Getting Help

### Documentation
- [README.md](README.md) - Basic overview
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [API.md](API.md) - Tool reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Documentation**: Check the docs for detailed guides

### Frequently Asked Questions

**Q: Why can't I find a specific player?**
A: Try different name formats, check spelling, or use fuzzy search.

**Q: Why is historical data limited?**
A: Some advanced statistics are only available for recent years (2015+).

**Q: Can I use this with other MCP clients?**
A: Yes! The server follows the MCP standard and works with any compatible client.

**Q: Is this free to use?**
A: Yes, the server is open source and free for personal and commercial use.

---

For additional help, please check the [GitHub repository](https://github.com/wsekete/pybaseball-MCP) or open an issue.
