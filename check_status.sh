#!/bin/bash
# Quick server status check script

echo "🔍 Pybaseball MCP Server Status Check"
echo "====================================="

echo -e "\n📊 Server Process:"
ps aux | grep server.py | grep -v grep || echo "❌ No server running"

echo -e "\n📝 Dependencies:"
python3 -c "
modules = ['mcp', 'pybaseball', 'pandas', 'matplotlib', 'seaborn']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module} - MISSING')
" 2>/dev/null

echo -e "\n🎯 To start server:"
echo "cd /Users/wseke/Documents/pybaseball-mcp-server"
echo "python3 server.py"

echo -e "\n✅ Look for: '🎯 Server is ready to accept connections'"
echo "📡 Use Ctrl+C to stop the server"
