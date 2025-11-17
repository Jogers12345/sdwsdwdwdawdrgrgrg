@echo off
:: =============================================================================
:: BSEE - Fixed Version - Simple and Robust
:: =============================================================================
title BSEE - Binary Structure Exploration Engine
color 0A
setlocal enabledelayedexpansion

:: Configuration
set PROJECT_NAME=BSEE
set PROJECT_DIR=%~dp0..
set VENV_DIR=%PROJECT_DIR%\venv
set LOG_FILE=%PROJECT_DIR%\logs\bsee_setup.log

:: Create logs directory
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

:: Simple error function that prevents instant closing
:error_exit
echo.
echo [ERROR] %~1
echo [ERROR] Please check the log file: %LOG_FILE%
pause
exit /b 1

:: =============================================================================
:: STEP 1: Basic Setup
:: =============================================================================
echo.
echo BSEE - Binary Structure Exploration Engine
echo =================================
echo.

:: Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python from: https://www.python.org/downloads/
    goto error_exit
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

:: =============================================================================
:: STEP 2: Virtual Environment
:: =============================================================================
echo Setting up virtual environment...

:: Remove old venv if corrupted
if exist "%VENV_DIR%" (
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo Removing corrupted virtual environment...
        rmdir /s /q "%VENV_DIR%"
    )
)

:: Create venv if not exists
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        goto error_exit
    )
)

:: Activate venv
echo Activating virtual environment...
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment activation failed
    goto error_exit
)

:: Set Python path
set PYTHONPATH=%PROJECT_DIR%;%PROJECT_DIR%\legacy;%PYTHONPATH%

:: =============================================================================
:: STEP 3: Dependencies
:: =============================================================================
echo Installing dependencies...

:: Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

:: Install core dependencies
echo Installing core packages...
python -m pip install numpy scipy matplotlib pyyaml click pandas >nul 2>&1
if errorlevel 1 (
    echo [WARN] Some packages failed to install, continuing...
)

:: Install GUI dependencies
echo Installing GUI packages...
python -m pip install pillow >nul 2>&1
if errorlevel 1 (
    echo [WARN] GUI packages failed, continuing...
)

:: =============================================================================
:: STEP 4: Fix Python Paths
:: =============================================================================
echo Fixing Python import paths...

:: Create bsee module if missing
if not exist "%PROJECT_DIR%\bsee" (
    echo Creating BSEE module structure...
    mkdir "%PROJECT_DIR%\bsee" >nul 2>&1
    echo # BSEE Package > "%PROJECT_DIR%\bsee\__init__.py" >nul 2>&1
)

:: =============================================================================
:: STEP 5: Windows Integration (Admin only)
:: =============================================================================
echo Setting up Windows integration...

net session >nul 2>&1
if %errorlevel% == 0 (
    echo Administrator privileges detected

    :: File associations
    assoc .bin=BSEEFile >nul 2>&1
    ftype BSEEFile="\"%PROJECT_DIR%\BSEE.bat\" \"%%1\"" >nul 2>&1

    :: Environment variables
    setx BSEE_HOME "%PROJECT_DIR%" >nul 2>&1

    echo Windows integration completed
) else (
    echo Standard user mode - Windows integration skipped
)

:: =============================================================================
:: STEP 6: Launch Application
:: =============================================================================
echo.
echo Launch Options:
echo 1. GUI Mode
echo 2. CLI Mode
echo 3. Exit
echo.

set /p choice=Select option (1-3):
if "%choice%"=="1" goto launch_gui
if "%choice%"=="2" goto launch_cli
if "%choice%"=="3" goto exit_bsee

goto main

:launch_gui
echo Starting GUI...
if exist "%PROJECT_DIR%\legacy\gui_main.py" (
    python "%PROJECT_DIR%\legacy\gui_main.py"
) else (
    echo [ERROR] GUI file not found
    goto error_exit
)
goto end

:launch_cli
echo Starting CLI...
if exist "%PROJECT_DIR%\legacy\main.py" (
    python "%PROJECT_DIR%\legacy\main.py" %*
) else (
    echo [ERROR] CLI file not found
    goto error_exit
)
goto end

:exit_bsee
echo Thank you for using BSEE!
goto end

:end
pause
exit /b 0