#!/bin/bash

# TRINETRA AI - Property-Based Test Runner
# This script runs all property-based tests locally

echo "=========================================="
echo "TRINETRA AI - Property-Based Test Runner"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating your virtual environment first"
    echo ""
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest is not installed"
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

echo "Running property-based tests..."
echo ""

# Set test mode to avoid API calls
export TEST_MODE=true

# Run property-based tests with statistics
pytest backend/test_*_property.py \
    -v \
    --tb=short \
    --hypothesis-show-statistics \
    --color=yes

# Capture exit code
EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All property-based tests passed!"
else
    echo "❌ Some tests failed. Check output above."
fi
echo "=========================================="

exit $EXIT_CODE
