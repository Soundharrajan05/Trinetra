# TRINETRA AI - PowerShell Setup Script
# ============================================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🛡️  TRINETRA AI - Setup Script  🛡️                         ║" -ForegroundColor Cyan
Write-Host "║  Setting up Trade Fraud Intelligence System...              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version
Write-Host ""
Write-Host "[2/6] Verifying Python version..." -ForegroundColor Yellow
$versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python 3.8 or higher is required" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Python version is compatible" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "[3/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "trinetra_env") {
    Write-Host "⚠️  Virtual environment already exists, skipping creation" -ForegroundColor Yellow
} else {
    python -m venv trinetra_env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[4/6] Activating virtual environment..." -ForegroundColor Yellow
& .\trinetra_env\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "[5/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ Pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[6/6] Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Setup environment file
Write-Host ""
Write-Host "Setting up environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env and add your Gemini API key" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  .env file already exists, skipping" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
@("models", "logs", "data") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "import fastapi, streamlit, pandas, sklearn, plotly; print('✅ All core packages imported successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Package verification failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Display success message
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ TRINETRA AI Setup Complete!                             ║" -ForegroundColor Green
Write-Host "║                                                              ║" -ForegroundColor Green
Write-Host "║  Next steps:                                                ║" -ForegroundColor Green
Write-Host "║  1. Edit .env file and add your Gemini API key             ║" -ForegroundColor Green
Write-Host "║  2. Ensure dataset is in data/ directory                   ║" -ForegroundColor Green
Write-Host "║  3. Run: .\run.ps1                                         ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
