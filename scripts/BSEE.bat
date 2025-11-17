@echo off
title BSEE Launcher
color 0A

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)

echo Python found
echo Setting up virtual environment...

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing requirements...
python -m pip install numpy scipy matplotlib pyyaml click pandas

echo Setup complete!
echo.
echo 1. GUI Mode
echo 2. CLI Mode
echo 3. Exit
echo.
choice /c 123 /n /m "Select option (1-3): "

if errorlevel 3 goto exit_bsee
if errorlevel 2 goto cli_mode
if errorlevel 1 goto gui_mode

:gui_mode
python legacy\gui_main.py
goto end

:cli_mode
python legacy\main.py
goto end

:exit_bsee
pause
exit /b 0