@echo off
title Distributed NRC Scraper
echo ========================================
echo    Distributed NRC Scraper Starter
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

REM Check if required files exist
if not exist "distributed_config.py" (
    echo ERROR: distributed_config.py not found
    echo Please run setup_distributed_scraper.py first
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import requests, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo Starting distributed NRC scraper...
echo.
python run_distributed_scraper_config.py

if errorlevel 1 (
    echo.
    echo ERROR: Scraper failed to start or encountered an error
    echo Check the log files for details
    pause
) else (
    echo.
    echo Scraper completed successfully
    pause
) 