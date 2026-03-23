#!/bin/bash
# TRINETRA AI - Unix/Linux/Mac Run Script
# ============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🛡️  TRINETRA AI - Starting System  🛡️                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "trinetra_env" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source trinetra_env/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "Creating from template..."
    cp .env.example .env
    echo "Please edit .env and add your Gemini API key"
    read -p "Press Enter to continue..."
fi

# Check if dataset exists
if [ ! -f "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv" ]; then
    echo "⚠️  Dataset not found"
    echo "Please ensure dataset is in data/ directory"
    read -p "Press Enter to continue..."
fi

# Run the application
echo ""
echo "Starting TRINETRA AI..."
echo ""

python main.py

# If main.py exits, show message
echo ""
echo "TRINETRA AI has stopped"
