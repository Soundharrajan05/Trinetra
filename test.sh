#!/bin/bash
# TRINETRA AI - Test Script for Linux/Mac
# This script runs the test suite

echo "========================================"
echo "TRINETRA AI - Running Tests"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run pytest with coverage
echo ""
echo "Running test suite..."
echo ""

pytest backend/tests/ -v --cov=backend --cov-report=html --cov-report=term

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Some tests failed"
    exit 1
fi

echo ""
echo "========================================"
echo "All tests passed!"
echo "========================================"
echo ""
echo "Coverage report generated in: htmlcov/index.html"
echo ""

# Deactivate virtual environment
deactivate
