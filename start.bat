@echo off
if not "%CMD_INIT%"=="1" (
  set CMD_INIT=1
  cmd.exe /k "%~f0" %*
  exit /b
)

cd /d "%~dp0"
setlocal enabledelayedexpansion

title BSEE - Binary Structure Exploration Engine

echo.
echo  ========================================
echo    BSEE - Binary Structure Exploration Engine
echo  ========================================
echo.

:: Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Python is not installed or not in PATH
    echo    Please install Python 3.9+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo    Found Python %PYTHON_VERSION%

:: Check if virtual environment exists
echo [2/5] Checking virtual environment...
if not exist "venv\" (
    echo    Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo    ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo    Virtual environment created successfully
) else (
    echo    Virtual environment found
)

:: Activate virtual environment
echo [3/5] Activating virtual environment...

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else if exist "venv\Scripts\Activate.ps1" (
    powershell -ExecutionPolicy Bypass -File "venv\Scripts\Activate.ps1"
) else if exist "venv\Scripts\activate" (
    call "venv\Scripts\activate"
) else (
    echo    ERROR: Could not find activation script. Rebuilding venv...
    rmdir /s /q venv
    python -m venv venv
    call "venv\Scripts\activate.bat"
)

:: Check and install required dependencies
echo [4/5] Checking dependencies...
echo    Checking required packages...

set PACKAGES=numpy scipy pyyaml matplotlib pillow psutil click tqdm lz4 zstandard

for %%p in (%PACKAGES%) do (
    python -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        echo    Installing %%p...
        pip install %%p
        if errorlevel 1 (
            echo    WARNING: Failed to install %%p, continuing anyway...
        ) else (
            echo    %%p installed successfully
        )
    ) else (
        echo    %%p is already installed
    )
)

echo [5/5] Ready to start BSEE
echo.
echo  Launch Options:
echo    1. GUI Mode (Recommended)
echo    2. CLI Mode
echo    3. Help
echo.

:: === FIXED SECTION START ===
if "%~1"=="" (
    echo    Choose launch mode [1-3]:
    choice /c 123 /n /m "Choose launch mode (1=GUI, 2=CLI, 3=Help): "

    if errorlevel 3 goto SHOW_HELP
    if errorlevel 2 goto CLI_MODE
    if errorlevel 1 goto GUI_MODE
    goto END
)

goto ARG_MODE
:: === FIXED SECTION END ===


:GUI_MODE
echo.
echo    Starting BSEE GUI...
python gui_main.py
goto END


:SHOW_HELP
echo.
echo    Showing CLI help...
python main.py --help
echo.
pause
goto END


:CLI_MODE
echo.
echo    CLI Interactive Mode
echo    ===================
echo.

if not exist "inputs\" mkdir inputs

:get_file
echo    Available files in inputs\ folder:
if exist "inputs\*.bin" (
    dir /b inputs\*.bin
) else (
    echo    No .bin files found.
    echo.
    set /p CREATE_TEST="Create a test file for demonstration? [Y/n]: "
    if /i not "%CREATE_TEST%"=="n" (
        echo    Creating test binary file...
        python -c "import os,random; data=(b'\xAA\x55'*128)+(b'\x00\xFF'*128)+os.urandom(512); open('inputs/test.bin','wb').write(data); print('Created test.bin (',len(data),'bytes)')"

        echo.
    )
)

set /p INPUT_FILE="Enter input filename (e.g. test.bin): "
if "%INPUT_FILE%"=="" goto get_file
if not exist "inputs\%INPUT_FILE%" (
    echo    ERROR: File does not exist.
    goto get_file
)

echo.
set /p STRATEGY_CHOICE="Choose strategy [1-6, default=1]: "
if "%STRATEGY_CHOICE%"=="" set STRATEGY_CHOICE=1

if "%STRATEGY_CHOICE%"=="1" set STRATEGY=greedy
if "%STRATEGY_CHOICE%"=="2" set STRATEGY=beam
if "%STRATEGY_CHOICE%"=="3" set STRATEGY=annealing
if "%STRATEGY_CHOICE%"=="4" set STRATEGY=mcts
if "%STRATEGY_CHOICE%"=="5" set STRATEGY=genetic
if "%STRATEGY_CHOICE%"=="6" set STRATEGY=heuristic

set /p MAX_OPS="Enter max operations [default=1000]: "
if "%MAX_OPS%"=="" set MAX_OPS=1000

set /p MAX_COST="Enter max cost [default=10000]: "
if "%MAX_COST%"=="" set MAX_COST=10000

set /p OUTPUT_DIR="Enter output directory [default=results]: "
if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=results

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo.
echo    Starting analysis...
python main.py "inputs\%INPUT_FILE%" --strategy %STRATEGY% --max-operations %MAX_OPS% --max-cost %MAX_COST% --output-dir "%OUTPUT_DIR%"
goto END


:ARG_MODE
if "%~1"=="gui" (
    python gui_main.py %*
) else (
    python main.py %*
)
goto END


:END
echo.
echo    BSEE execution completed.
echo.
pause
