@echo off
REM TRINETRA AI - Property-Based Test Runner (Windows)
REM This script runs all property-based tests locally

echo ==========================================
echo TRINETRA AI - Property-Based Test Runner
echo ==========================================
echo.

REM Check if pytest is installed
where pytest >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: pytest is not installed
    echo    Run: pip install -r requirements.txt
    exit /b 1
)

echo Running property-based tests...
echo.

REM Set test mode to avoid API calls
set TEST_MODE=true

REM Run property-based tests with statistics
pytest backend/test_*_property.py -v --tb=short --hypothesis-show-statistics --color=yes

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ==========================================
if %EXIT_CODE% EQU 0 (
    echo All property-based tests passed!
) else (
    echo Some tests failed. Check output above.
)
echo ==========================================

exit /b %EXIT_CODE%
