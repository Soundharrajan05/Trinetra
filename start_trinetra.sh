#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║  🛡️  TRINETRA AI - Trade Fraud Intelligence System  🛡️      ║"
echo "║                                                              ║"
echo "║  Starting system... Please wait...                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if required files exist
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found"
    echo "Please run this script from the TRINETRA AI directory"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    echo "Please ensure all files are present"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Start the system
echo "🚀 Starting TRINETRA AI..."
$PYTHON_CMD main.py