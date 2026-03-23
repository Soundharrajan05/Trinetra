#!/bin/bash
# TRINETRA AI - Cleanup Script for Linux/Mac
# This script removes temporary files and cached data

echo "========================================"
echo "TRINETRA AI - Cleanup Utility"
echo "========================================"
echo ""

echo "This script will remove:"
echo "- Python cache files (__pycache__, *.pyc)"
echo "- Hypothesis test cache (.hypothesis)"
echo "- Pytest cache (.pytest_cache)"
echo "- Log files (logs/*.log)"
echo "- Trained models (models/*.pkl)"
echo ""

read -p "Do you want to continue? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Cleaning up..."

# Remove Python cache
echo "[1/5] Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove Hypothesis cache
echo "[2/5] Removing Hypothesis cache..."
rm -rf .hypothesis 2>/dev/null
rm -rf backend/.hypothesis 2>/dev/null

# Remove Pytest cache
echo "[3/5] Removing Pytest cache..."
rm -rf .pytest_cache 2>/dev/null
rm -rf backend/.pytest_cache 2>/dev/null

# Remove log files
echo "[4/5] Removing log files..."
if [ -d "logs" ]; then
    rm -f logs/*.log 2>/dev/null
fi

# Remove trained models (optional)
echo "[5/5] Removing trained models..."
if [ -d "models" ]; then
    rm -f models/*.pkl 2>/dev/null
fi

# Remove coverage files
rm -f .coverage 2>/dev/null
rm -rf htmlcov 2>/dev/null

echo ""
echo "========================================"
echo "Cleanup completed successfully!"
echo "========================================"
echo ""
echo "Note: The model will be retrained on next run"
echo ""
