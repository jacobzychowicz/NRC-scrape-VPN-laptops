@echo off
title Distributed NRC Scraper Test
echo ========================================
echo    Distributed NRC Scraper Test
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

REM Check if test script exists
if not exist "test_distributed_setup.py" (
    echo ERROR: test_distributed_setup.py not found
    pause
    exit /b 1
)

REM Check if config exists
if not exist "distributed_config.py" (
    echo ERROR: distributed_config.py not found
    echo Please run setup_laptop.bat first
    pause
    exit /b 1
)

echo Running setup tests...
echo.
python test_distributed_setup.py

if errorlevel 1 (
    echo.
    echo ERROR: Some tests failed
    echo Check the output above for details
    pause
    exit /b 1
) else (
    echo.
    echo All tests passed! Your setup is ready.
    echo.
    echo You can now start scraping with start_scraping.bat
    echo.
    pause
) 