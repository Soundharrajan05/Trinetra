@echo off
REM TRINETRA AI - Cleanup Script for Windows
REM This script removes temporary files and cached data

echo ========================================
echo TRINETRA AI - Cleanup Utility
echo ========================================
echo.

echo This script will remove:
echo - Python cache files (__pycache__, *.pyc)
echo - Hypothesis test cache (.hypothesis)
echo - Pytest cache (.pytest_cache)
echo - Log files (logs/*.log)
echo - Trained models (models/*.pkl)
echo.

set /p confirm="Do you want to continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cleanup cancelled
    pause
    exit /b 0
)

echo.
echo Cleaning up...

REM Remove Python cache
echo [1/5] Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

REM Remove Hypothesis cache
echo [2/5] Removing Hypothesis cache...
if exist ".hypothesis" rd /s /q ".hypothesis"
if exist "backend\.hypothesis" rd /s /q "backend\.hypothesis"

REM Remove Pytest cache
echo [3/5] Removing Pytest cache...
if exist ".pytest_cache" rd /s /q ".pytest_cache"
if exist "backend\.pytest_cache" rd /s /q "backend\.pytest_cache"

REM Remove log files
echo [4/5] Removing log files...
if exist "logs" (
    del /q logs\*.log >nul 2>&1
)

REM Remove trained models (optional)
echo [5/5] Removing trained models...
if exist "models\*.pkl" (
    del /q models\*.pkl >nul 2>&1
)

REM Remove coverage files
if exist ".coverage" del /q .coverage >nul 2>&1
if exist "htmlcov" rd /s /q "htmlcov"

echo.
echo ========================================
echo Cleanup completed successfully!
echo ========================================
echo.
echo Note: The model will be retrained on next run
echo.
pause
