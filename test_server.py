#\!/usr/bin/env python3
"""
Test script to verify MCP server connectivity and behavior
"""

import asyncio
import subprocess
import sys
import time
import os


def run_diagnostic_commands():
    """Run diagnostic commands to check server status"""
    print("🔍 Running Server Diagnostics")
    print("=" * 50)
    
    print("\n1. 📊 Checking if server process is running...")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        server_processes = [line for line in result.stdout.split('\n') if 'server.py' in line and 'grep' not in line]
        if server_processes:
            print("✅ Found server processes:")
            for proc in server_processes:
                print(f"   {proc}")
        else:
            print("❌ No server.py processes found")
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
    
    print("\n2. 🌐 Checking network connections...")
    try:
        result = subprocess.run(['lsof', '-i', '-P', '-n'], capture_output=True, text=True)
        python_connections = [line for line in result.stdout.split('\n') if 'python' in line.lower()]
        if python_connections:
            print("✅ Found Python network connections:")
            for conn in python_connections[:5]:  # Show first 5
                print(f"   {conn}")
            if len(python_connections) > 5:
                print(f"   ... and {len(python_connections) - 5} more")
        else:
            print("❌ No Python network connections found")
    except Exception as e:
        print(f"❌ Error checking network connections: {e}")
    
    print("\n3. 📝 Checking dependencies...")
    required_modules = ['mcp', 'pybaseball', 'pandas', 'matplotlib', 'seaborn']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n📦 Install missing dependencies:")
        print(f"pip install {' '.join(missing)}")
    
    print("\n" + "=" * 50)


def main():
    """Main test function"""
    print("🏁 MCP Server Test Suite")
    print("Starting comprehensive server analysis...")
    print("=" * 60)
    
    # Run diagnostic commands
    run_diagnostic_commands()
    
    print("\n🎯 Analysis Complete\!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run 'python3 server.py' to start the enhanced server")
    print("2. Look for the new detailed startup messages")
    print("3. Server will show 'ready to accept connections' when working")
    print("4. Use Ctrl+C to stop the server")


if __name__ == "__main__":
    main()
EOF < /dev/null