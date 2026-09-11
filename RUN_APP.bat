@echo off
REM Football Intelligence Application - Setup & Run Script for Windows

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   Football Intelligence - Application Launcher            ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check if in correct directory
if not exist "football_analytics" (
    echo ✗ Error: Run this script from /home/baris/statsbomb directory
    echo   Current directory: %cd%
    pause
    exit /b 1
)

REM Check if venv exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo.
echo Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r football_analytics\app_backend\requirements.txt >nul 2>&1

if errorlevel 1 (
    echo ✗ Error installing dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully
echo.
echo Starting Football Intelligence Application...
echo ═══════════════════════════════════════════════════════════
echo.

REM Run the Flask app
cd football_analytics
python app_backend\app.py

pause
