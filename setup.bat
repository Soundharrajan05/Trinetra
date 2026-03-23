@echo off
REM TRINETRA AI - Windows Setup Script
echo Setting up TRINETRA AI...
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
python --version
echo OK: Python found
echo.

REM Check Python version
echo [2/6] Verifying Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8+ required
    pause
    exit /b 1
)
echo OK: Python version compatible
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist trinetra_env (
    echo SKIP: Virtual environment exists
) else (
    python -m venv trinetra_env
    echo OK: Virtual environment created
)
echo.

REM Activate and install
echo [4/6] Activating virtual environment...
call trinetra_env\Scripts\activate.bat
echo OK: Virtual environment activated
echo.

echo [5/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo OK: Pip upgraded
echo.

echo [6/6] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed
echo.

REM Setup environment
if not exist .env (
    copy .env.example .env >nul
    echo OK: Created .env file
)

REM Create directories
if not exist models mkdir models
if not exist logs mkdir logs
if not exist data mkdir data
echo OK: Directories created
echo.

echo ========================================
echo Setup Complete!
echo Next: Edit .env and run run.bat
echo ========================================
pause
