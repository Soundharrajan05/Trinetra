#!/bin/bash
# TRINETRA AI - Unix/Linux/Mac Setup Script
# ============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🛡️  TRINETRA AI - Setup Script  🛡️                         ║"
echo "║  Setting up Trade Fraud Intelligence System...              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

python3 --version
echo "✅ Python found"

# Check Python version
echo ""
echo "[2/6] Verifying Python version..."
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if [ $? -ne 0 ]; then
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi
echo "✅ Python version is compatible"

# Create virtual environment
echo ""
echo "[3/6] Creating virtual environment..."
if [ -d "trinetra_env" ]; then
    echo "⚠️  Virtual environment already exists, skipping creation"
else
    python3 -m venv trinetra_env
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[4/6] Activating virtual environment..."
source trinetra_env/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "[5/6] Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo "✅ Pip upgraded"

# Install dependencies
echo ""
echo "[6/6] Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

# Setup environment file
echo ""
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env and add your Gemini API key"
else
    echo "⚠️  .env file already exists, skipping"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p models logs data
echo "✅ Directories created"

# Verify installation
echo ""
echo "Verifying installation..."
python -c "import fastapi, streamlit, pandas, sklearn, plotly; print('✅ All core packages imported successfully')"
if [ $? -ne 0 ]; then
    echo "❌ Package verification failed"
    exit 1
fi

# Display success message
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ TRINETRA AI Setup Complete!                             ║"
echo "║                                                              ║"
echo "║  Next steps:                                                ║"
echo "║  1. Edit .env file and add your Gemini API key             ║"
echo "║  2. Ensure dataset is in data/ directory                   ║"
echo "║  3. Run: ./run.sh                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
