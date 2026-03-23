@echo off
REM TRINETRA AI - Windows Cleanup Script
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🛡️  TRINETRA AI - Cleanup Script  🛡️                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo This will remove:
echo - Virtual environment (trinetra_env)
echo - Generated models (models/*.pkl)
echo - Log files (logs/*.log)
echo - Python cache files (__pycache__, *.pyc)
echo - Test artifacts (.pytest_cache, .coverage, .hypothesis)
echo.
echo .env and data files will NOT be removed
echo.

set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Cleanup cancelled
    pause
    exit /b 0
)

echo.
echo Cleaning up...

REM Remove virtual environment
if exist trinetra_env (
    echo Removing virtual environment...
    rmdir /s /q trinetra_env
    echo OK: Virtual environment removed
)

REM Remove model files
if exist models\*.pkl (
    echo Removing model files...
    del /q models\*.pkl
    echo OK: Model files removed
)

REM Remove log files
if exist logs\*.log (
    echo Removing log files...
    del /q logs\*.log
    echo OK: Log files removed
)

REM Remove Python cache
echo Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc >nul 2>&1

REM Remove test artifacts
if exist .pytest_cache (
    rmdir /s /q .pytest_cache
)
if exist .coverage (
    del /q .coverage
)
if exist .hypothesis (
    rmdir /s /q .hypothesis
)
if exist htmlcov (
    rmdir /s /q htmlcov
)

echo OK: Python cache removed
echo.
echo ========================================
echo Cleanup complete!
echo Run setup.bat to reinstall
echo ========================================
pause
