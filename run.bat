@echo off
REM TRINETRA AI - Windows Run Script
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🛡️  TRINETRA AI - Starting System  🛡️                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist trinetra_env (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call trinetra_env\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found
    echo Creating from template...
    copy .env.example .env >nul
    echo Please edit .env and add your Gemini API key
    pause
)

REM Check if dataset exists
if not exist data\trinetra_trade_fraud_dataset_1000_rows_complex.csv (
    echo WARNING: Dataset not found
    echo Please ensure dataset is in data/ directory
    pause
)

REM Run the application
echo.
echo Starting TRINETRA AI...
echo.
python main.py

REM If main.py exits, show message
echo.
echo TRINETRA AI has stopped
pause
