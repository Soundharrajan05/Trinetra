@echo off
REM TRINETRA AI - Test Script for Windows
REM This script runs the test suite

echo ========================================
echo TRINETRA AI - Running Tests
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run pytest with coverage
echo.
echo Running test suite...
echo.

pytest backend/tests/ -v --cov=backend --cov-report=html --cov-report=term

if errorlevel 1 (
    echo.
    echo [ERROR] Some tests failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo All tests passed!
echo ========================================
echo.
echo Coverage report generated in: htmlcov/index.html
echo.

REM Deactivate virtual environment
deactivate
pause
