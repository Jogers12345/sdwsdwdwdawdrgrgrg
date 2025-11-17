@echo off
setlocal enabledelayedexpansion
title BSEE - Binary Structure Exploration Engine
color 0A

echo BSEE - Binary Structure Exploration Engine
echo ========================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)

echo SUCCESS: Python found

echo Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created!
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated!
echo.

echo Installing requirements...
python -m pip install numpy scipy matplotlib pyyaml click pandas
echo.

echo Setup complete!
echo.
echo ========================================
echo Select launch mode:
echo 1. GUI Mode
echo 2. CLI Mode
echo 3. Exit
echo.

choice /c 123 /n /m "Select option (1-3): "
if errorlevel 3 goto exit_bsee
if errorlevel 2 goto cli_mode
if errorlevel 1 goto gui_mode

:gui_mode
echo Starting GUI mode...
python legacy\gui_main.py
goto end

:cli_mode
echo Starting CLI mode...
python legacy\main.py %*
goto end

:exit_bsee
echo Thank you for using BSEE!
pause

:end
pause
exit /b 0