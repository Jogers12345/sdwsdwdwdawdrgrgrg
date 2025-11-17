@echo off
title BSEE - Binary Structure Exploration Engine
color 0A
echo.
echo  ==========================================
echo    BSEE - Binary Structure Exploration Engine
echo    ==========================================
echo.

REM Simple check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Python found
echo.

REM Set project directory
set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

REM Check if running from correct directory
if not exist "legacy\main.py" (
    echo ERROR: Please run from BSEE project directory
    echo Current directory: %PROJECT_DIR%
    echo.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment activated
) else (
    echo ERROR: Virtual environment activation script not found
    pause
    exit /b 1
)

REM Install basic requirements
echo Installing basic requirements...
python -m pip install numpy scipy matplotlib pyyaml click pandas >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some packages failed to install, continuing...
)

echo Requirements installation complete
echo.

REM Launch menu
:main
echo.
echo    ==========================================
echo    Select launch mode:
echo    1. GUI Mode
echo    2. CLI Mode
echo    3. Exit
echo    ==========================================
echo.
choice /c 123 /n /m "Select option (1-3): "

if errorlevel 3 goto exit_bsee
if errorlevel 2 goto cli_mode
if errorlevel 1 goto gui_mode

:gui_mode
echo.
echo Starting GUI mode...
if exist "legacy\gui_main.py" (
    python legacy\gui_main.py
) else (
    echo ERROR: GUI file not found at: legacy\gui_main.py
    echo Falling back to CLI mode...
    goto cli_mode
)
goto end

:cli_mode
echo.
echo Starting CLI mode...
if exist "legacy\main.py" (
    python legacy\main.py
) else (
    echo ERROR: CLI file not found at: legacy\main.py
    echo Please check your BSEE installation
)
goto end

:end
echo.
echo    Press any key to exit...
pause >nul

:exit_bsee
echo.
echo Thank you for using BSEE!
echo.
pause
exit /b 0