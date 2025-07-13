@echo off
title Distributed NRC Scraper Setup
echo ========================================
echo    Distributed NRC Scraper Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if setup script exists
if not exist "setup_distributed_scraper.py" (
    echo ERROR: setup_distributed_scraper.py not found
    pause
    exit /b 1
)

REM Install dependencies first
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Failed to install some packages, continuing anyway...
)

echo.
echo Starting setup wizard...
echo.
python setup_distributed_scraper.py

if errorlevel 1 (
    echo.
    echo ERROR: Setup failed
    pause
    exit /b 1
) else (
    echo.
    echo Setup completed successfully!
    echo.
    echo Next steps:
    echo 1. Configure the coordination file sharing method
    echo 2. Run test_distributed_setup.py to verify setup
    echo 3. Start scraping with start_scraping.bat
    echo.
    pause
) 