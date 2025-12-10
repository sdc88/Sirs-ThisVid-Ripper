@echo off
echo ════════════════════════════════════════════════════════════════
echo   SIR'S THISVID RIPPER
echo ════════════════════════════════════════════════════════════════
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Check for required packages and install if missing
echo Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting ripper...
echo.

REM Run the script
python "%~dp0thisvid_scraper.py"

echo.
pause
