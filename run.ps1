# TRINETRA AI - PowerShell Run Script
# ============================================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🛡️  TRINETRA AI - Starting System  🛡️                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "trinetra_env")) {
    Write-Host "❌ Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\trinetra_env\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env and add your Gemini API key" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
}

# Check if dataset exists
if (-not (Test-Path "data\trinetra_trade_fraud_dataset_1000_rows_complex.csv")) {
    Write-Host "⚠️  Dataset not found" -ForegroundColor Yellow
    Write-Host "Please ensure dataset is in data/ directory" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
}

# Run the application
Write-Host ""
Write-Host "Starting TRINETRA AI..." -ForegroundColor Green
Write-Host ""

python main.py

# If main.py exits, show message
Write-Host ""
Write-Host "TRINETRA AI has stopped" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
