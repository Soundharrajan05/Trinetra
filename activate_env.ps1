# PowerShell activation script for TRINETRA AI virtual environment
Write-Host "Activating TRINETRA AI virtual environment..." -ForegroundColor Green
& .\trinetra_env\Scripts\Activate.ps1
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "Python version:" -ForegroundColor Yellow
python --version
Write-Host "Pip version:" -ForegroundColor Yellow
pip --version
Write-Host ""
Write-Host "Ready to install packages with: pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host "Ready to run the application with: python main.py" -ForegroundColor Cyan