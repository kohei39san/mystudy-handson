#!/bin/bash
# Run script for Redmine MCP Server

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env..."
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
fi

# Check if REDMINE_URL is set
if [ -z "$REDMINE_URL" ]; then
    echo "⚠️  REDMINE_URL not set. Using default: http://localhost:3000"
    echo "💡 To configure, set environment variable or edit .env file:"
    echo "   export REDMINE_URL=https://your-redmine-server.com"
    echo "   or edit .env file and set REDMINE_URL=https://your-redmine-server.com"
    echo ""
fi

echo "🚀 Starting Redmine MCP Server..."
echo "📍 Target Redmine URL: ${REDMINE_URL:-http://localhost:3000}"
echo "🐛 Debug mode: ${DEBUG:-false}"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Change to src directory and run the MCP server
cd src
python redmine_mcp_server.py