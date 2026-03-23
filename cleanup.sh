#!/bin/bash
# TRINETRA AI - Unix/Linux/Mac Cleanup Script
# ============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🛡️  TRINETRA AI - Cleanup Script  🛡️                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "This will remove:"
echo "- Virtual environment (trinetra_env)"
echo "- Generated models (models/*.pkl)"
echo "- Log files (logs/*.log)"
echo "- Python cache files (__pycache__, *.pyc)"
echo "- Test artifacts (.pytest_cache, .coverage, .hypothesis)"
echo ""
echo ".env and data files will NOT be removed"
echo ""

read -p "Are you sure? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Cleaning up..."

# Remove virtual environment
if [ -d "trinetra_env" ]; then
    echo "Removing virtual environment..."
    rm -rf trinetra_env
    echo "✅ Virtual environment removed"
fi

# Remove model files
if ls models/*.pkl 1> /dev/null 2>&1; then
    echo "Removing model files..."
    rm -f models/*.pkl
    echo "✅ Model files removed"
fi

# Remove log files
if ls logs/*.log 1> /dev/null 2>&1; then
    echo "Removing log files..."
    rm -f logs/*.log
    echo "✅ Log files removed"
fi

# Remove Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove test artifacts
rm -rf .pytest_cache .coverage .hypothesis htmlcov 2>/dev/null

echo "✅ Python cache removed"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Cleanup complete!                                          ║"
echo "║  Run ./setup.sh to reinstall                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
