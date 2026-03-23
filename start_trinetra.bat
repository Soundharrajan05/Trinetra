@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║  🛡️  TRINETRA AI - Trade Fraud Intelligence System  🛡️      ║
echo ║                                                              ║
echo ║  Starting system... Please wait...                          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "main.py" (
    echo ❌ main.py not found
    echo Please run this script from the TRINETRA AI directory
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ requirements.txt not found
    echo Please ensure all files are present
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
pip install -r requirements.txt --quiet

REM Start the system
echo 🚀 Starting TRINETRA AI...
python main.py

pause