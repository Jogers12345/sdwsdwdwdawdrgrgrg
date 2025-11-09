@echo off
:: =============================================================================
:: BSEE - Binary Structure Exploration Engine - Unified Windows Launcher
:: =============================================================================
:: This script automatically sets up a virtual environment and starts BSEE
:: Compatible with Windows 10/11 - optimized for native Windows execution
:: =============================================================================

:: Set console properties for better appearance
title BSEE - Binary Structure Exploration Engine
color 0A
mode con: cols=120 lines=40

:: Prevent multiple initialization loops
if "%BSEE_INIT%"=="1" goto main
set BSEE_INIT=1

:: Change to script directory
cd /d "%~dp0"

:: Display welcome banner
echo.
echo  ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
echo  ║                         BSEE - Binary Structure Exploration Engine                         ║
echo  ║                         Advanced Binary Analysis & Optimization                      ║
echo  ║                                    Version 2.0                                      ║
echo  ╚════════════════════════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check if running as administrator (optional optimization)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo    [INFO] Running with administrator privileges - optimizations enabled
    set IS_ADMIN=1
) else (
    echo    [INFO] Running with standard user privileges
    set IS_ADMIN=0
)

:: =============================================================================
:: STEP 1: Environment Setup and Validation
:: =============================================================================
echo.
echo    ══════════════════════════════════════════════════════════════════════════════════════════╗
echo    ║                              ENVIRONMENT SETUP                                    ║
echo    ╚═════════════════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check Python installation with detailed version check
echo    [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] Python is not installed or not in PATH
    echo.
    echo    Please install Python 3.9+ from: https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    echo    After installing Python, please run this script again.
    echo.
    pause
    exit /b 1
)

:: Get detailed Python version information
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

echo    [SUCCESS] Found Python %PYTHON_VERSION% (Major: %PYTHON_MAJOR%, Minor: %PYTHON_MINOR%)

:: Validate Python version
if %PYTHON_MAJOR% LSS 3 (
    echo    [ERROR] Python 3.9+ is required. Found Python %PYTHON_MAJOR%.%PYTHON_MINOR%
    echo    Please upgrade Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 9 (
        echo    [ERROR] Python 3.9+ is required. Found Python %PYTHON_MAJOR%.%PYTHON_MINOR%
        echo    Please upgrade Python from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: =============================================================================
:: STEP 2: Virtual Environment Management
:: =============================================================================
echo    [2/7] Setting up Python virtual environment...

:: Remove old virtual environment if corrupted
if exist "venv\Lib\site-packages\pip" (
    if not exist "venv\Lib\site-packages\pip\__init__.py" (
        echo    [WARN] Corrupted virtual environment detected, removing...
        if exist "venv" rmdir /s /q "venv"
    )
)

:: Create or verify virtual environment
if not exist "venv\" (
    echo    [INFO] Creating virtual environment...
    python -m venv venv --clear
    if errorlevel 1 (
        echo    [ERROR] Failed to create virtual environment
        echo    This may be due to Python installation issues or insufficient permissions.
        pause
        exit /b 1
    )
    echo    [SUCCESS] Virtual environment created
) else (
    echo    [SUCCESS] Virtual environment exists
)

:: Activate virtual environment with fallback mechanisms
echo    [3/7] Activating virtual environment...

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    if errorlevel 1 (
        echo    [ERROR] Failed to activate virtual environment
        goto venv_recovery
    )
    echo    [SUCCESS] Virtual environment activated
) else (
    :venv_recovery
    echo    [WARN] Activation script not found, attempting recovery...
    if exist "venv" rmdir /s /q "venv"
    python -m venv venv
    if exist "venv\Scripts\activate.bat" (
        call "venv\Scripts\activate.bat"
        echo    [SUCCESS] Virtual environment recovered and activated
    ) else (
        echo    [ERROR] Failed to recover virtual environment
        pause
        exit /b 1
    )
)

:: =============================================================================
:: STEP 3: Dependency Installation and Verification
:: =============================================================================
echo    [4/7] Installing and verifying dependencies...

:: Upgrade pip and install wheel for faster installs
echo    [INFO] Upgrading pip and installing wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

:: Define comprehensive dependency list
set CORE_DEPS=numpy scipy matplotlib pillow psutil click tqdm pyyaml lz4 zstandard
set GUI_DEPS=tkinter PyQt5 pyqt5-tools pyqt5.sip
set ML_DEPS=scikit-learn pandas seaborn jupyter ipywidgets plotly bokeh
set DEV_DEPS=pytest pytest-cov pytest-mock black flake8 mypy bandit safety sphinx
set OPTIONAL_DEPS=numba cython statsmodels sympy networkx

:: Create requirements file for reference
echo # BSEE Dependencies - Auto-generated by launcher > requirements.txt
echo # Core dependencies >> requirements.txt
echo %CORE_DEPS% >> requirements.txt
echo. >> requirements.txt
echo # GUI dependencies >> requirements.txt
echo %GUI_DEPS% >> requirements.txt
echo. >> requirements.txt
echo # Machine Learning dependencies >> requirements.txt
echo %ML_DEPS% >> requirements.txt
echo. >> requirements.txt
echo # Development dependencies >> requirements.txt
echo %DEV_DEPS% >> requirements.txt
echo. >> requirements.txt

:: Install core dependencies
echo    [INFO] Installing core dependencies...
for %%p in (%CORE_DEPS%) do (
    echo    [INFO] Installing %%p...
    python -m pip install %%p >nul 2>&1
    if errorlevel 1 (
        echo    [WARN] Failed to install %%p, continuing...
    ) else (
        echo    [SUCCESS] %%p installed
    )
)

:: Install GUI dependencies (with fallback)
echo    [INFO] Installing GUI dependencies...
for %%p in (%GUI_DEPS%) do (
    python -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        echo    [INFO] Installing %%p...
        python -m pip install %%p >nul 2>&1
        if errorlevel 1 (
            echo    [WARN] Failed to install %%p, GUI may not be available
        ) else (
            echo    [SUCCESS] %%p installed
        )
    else (
        echo    [INFO] %%p already available
    )
)

:: =============================================================================
:: STEP 4: System and Hardware Optimization
:: =============================================================================
echo    [5/7] Optimizing for Windows environment...

:: Set Windows-specific environment variables
set PYTHONPATH=%CD%;%PYTHONPATH%
set BSEE_HOME=%CD%
set BSEE_CONFIG_DIR=%CD%\config
set BSEE_DATA_DIR=%CD%\data
set BSEE_MODELS_DIR=%CD%\models
set BSEE_RESULTS_DIR=%CD%\results

:: Create necessary directories
if not exist "config" mkdir config
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "results" mkdir results
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp

:: Set Windows file associations if administrator
if %IS_ADMIN% EQU 1 (
    echo    [INFO] Administrator privileges detected - setting file associations...
    assoc .bin=BSEEFile >nul 2>&1
    ftype BSEEFile="\"%CD%\BSEE.bat\" \"%%1\"" >nul 2>&1
)

:: Optimize Windows performance settings
if %IS_ADMIN% EQU 1 (
    echo    [INFO] Optimizing Windows performance settings...
    :: Set process priority (will be applied when GUI starts)
    wmic process where "name='python.exe'" CALL setpriority "high priority" >nul 2>&1
)

:: =============================================================================
:: STEP 5: Validation and Diagnostics
:: =============================================================================
echo    [6/7] Validating installation...

:: Test core imports
echo    [INFO] Testing core module imports...
python -c "
import sys
import numpy as np
import scipy
import matplotlib
import psutil
import click
import yaml
print('Core modules imported successfully')
" >nul 2>&1

if errorlevel 1 (
    echo    [WARN] Some core modules failed to import - functionality may be limited
) else (
    echo    [SUCCESS] All core modules imported successfully
)

:: Check BSEE modules
echo    [INFO] Checking BSEE modules...
python -c "
import sys
sys.path.insert(0, '.')
try:
    import bsee
    from bsee.engine.pipeline import Pipeline
    from bsee.strategies.base_strategy import BaseStrategy
    print('BSEE modules imported successfully')
except ImportError as e:
    print(f'BSEE import error: {e}')
    sys.exit(1)
" >nul 2>&1

if errorlevel 1 (
    echo    [WARN] BSEE modules not found - running in development mode
) else (
    echo    [SUCCESS] BSEE modules validated
)

:: Generate system information
echo    [INFO] Collecting system information...
python -c "
import platform
import psutil
import sys

print(f'System: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'CPU: {platform.processor()} ({psutil.cpu_count()} cores)')
print(f'Memory: {psutil.virtual_memory().total // (1024**3)} GB')
print(f'Disk: {psutil.disk_usage(\".\").total // (1024**3)} GB free')
" > system_info.txt 2>&1

:: =============================================================================
:: STEP 6: Launch Interface Selection
:: =============================================================================
echo.
echo    ══════════════════════════════════════════════════════════════════════════════════════════╗
echo    ║                              LAUNCH OPTIONS                                      ║
echo    ╚═════════════════════════════════════════════════════════════════════════════════════════╝
echo.

:main
:: Check for command line arguments
if "%~1"=="" (
    goto interactive_mode
) else (
    goto command_mode
)

:interactive_mode
echo    Please select launch mode:
    echo.
    echo    [1] GUI Mode      - Graphical interface (Recommended for most users)
    echo    [2] CLI Mode       - Command-line interface
    echo    [3] Preset Mode   - Choose from predefined configurations
    echo    [4] Test Mode     - Run validation tests
    echo    [5] Help          - Show detailed help and documentation
    echo    [6] Exit          - Exit BSEE
    echo.

    choice /c 123456 /n /m "Select option (1-6): "

    if errorlevel 6 goto exit_bsee
    if errorlevel 5 goto show_help
    if errorlevel 4 goto test_mode
    if errorlevel 3 goto preset_mode
    if errorlevel 2 goto cli_mode
    if errorlevel 1 goto gui_mode

:command_mode
if "%~1"=="gui" goto gui_mode
if "%~1"=="cli" goto cli_mode
if "%~1"=="test" goto test_mode
if "%~1"=="help" goto show_help
if "%~1"=="preset" goto preset_mode

echo    [INFO] Unknown argument: %~1
echo    Use --help for available options
goto main

:gui_mode
echo.
echo    [INFO] Starting BSEE GUI Interface...
echo    [INFO] Loading graphical components...

:: Check if GUI dependencies are available
python -c "
try:
    import tkinter
    print('tkinter available')
except ImportError:
    print('tkinter not available - installing...')
    import subprocess
    subprocess.run(['python', '-m', 'pip', 'install', 'tkinter'])
" >nul 2>&1

:: Start GUI application
if exist "legacy\gui_main.py" (
    python legacy\gui_main.py
) else (
    echo    [ERROR] GUI application not found
    echo    Falling back to CLI mode...
    timeout /t 3 /nobreak >nul
    goto cli_mode
)
goto end_script

:cli_mode
echo.
echo    [INFO] Starting BSEE CLI Interface...
echo    [INFO] Loading command-line components...

if not exist "legacy\main.py" (
    echo    [ERROR] Main application not found
    timeout /t 3 /nobreak >nul
    goto interactive_mode
)

:: Check if input file provided
if "%~2"=="" (
    echo    [INFO] No input file provided, entering interactive CLI mode
    echo.
    echo    Available options:
    echo    - Drag and drop a file onto this window
    - Type file path manually
    - Type 'help' for CLI commands
    echo.

    :cli_input
    set /p INPUT="Enter file path or command: "
    if "%INPUT%"=="" goto cli_input
    if /i "%INPUT%"=="help" (
        python legacy\main.py --help
        goto cli_input
    ) else if /i "%INPUT%"=="exit" (
        goto exit_bsee
    ) else (
        python legacy\main.py "%INPUT%" %3 %4 %5 %6 %7 %8 %9
    )
) else (
    python legacy\main.py %~2 %~3 %~4 %~5 %~6 %~7 %~8 %~9
)
goto end_script

:preset_mode
echo.
echo    [INFO] Available Configuration Presets:
echo.
echo    [1] Neural Network      - Advanced ML-based analysis
echo    [2] Performance        - Optimized for speed
echo    [3] Research Analysis  - Comprehensive research-grade analysis
echo.
choice /c 123 /n /m "Select preset (1-3): "

if errorlevel 3 (
    set PRESET_FILE=config\presets\research_analysis_preset.yaml
    echo    [INFO] Loading Research Analysis preset...
) else if errorlevel 2 (
    set PRESET_FILE=config\presets\performance_optimized_preset.yaml
    echo    [INFO] Loading Performance Optimized preset...
) else (
    set PRESET_FILE=config\presets\neural_network_preset.yaml
    echo    [INFO] Loading Neural Network preset...
)

if exist "%PRESET_FILE%" (
    python legacy\main.py --preset "%PRESET_FILE%"
) else (
    echo    [ERROR] Preset file not found: %PRESET_FILE%
    echo    Using default configuration...
    python legacy\main.py
)
goto end_script

:test_mode
echo.
echo    [INFO] Running BSEE Test Suite...
echo    [INFO] This will validate the installation and run comprehensive tests

:: Check if pytest is available
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo    [INFO] Installing pytest...
    python -m pip install pytest pytest-cov pytest-mock >nul 2>&1
)

:: Run tests
if exist "tests" (
    echo    [INFO] Running unit tests...
    python -m pytest tests/unit/ -v --tb=short

    echo.
    echo    [INFO] Running integration tests...
    python -m pytest tests/integration/ -v --tb=short

    echo.
    echo    [INFO] Running Phase 4 tests...
    python run_phase4_tests.py --verbose
) else (
    echo    [ERROR] Test suite not found
    echo    Please ensure you have the complete BSEE installation
)

echo.
echo    [INFO] Test execution completed
timeout /t 3 /nobreak >nul
goto interactive_mode

:show_help
echo.
echo    [INFO] BSEE Help and Documentation
echo.
echo    BSEE (Binary Structure Exploration Engine) is an advanced tool for analyzing and
echo    optimizing binary files through reversible transformations.
echo.
echo    Usage:
echo      BSEE.bat                    - Interactive mode
echo      BSEE.bat gui [file]        - Start GUI mode
echo      BSEE.bat cli [file] [args] - Start CLI mode
echo      BSEE.bat preset [name]     - Use configuration preset
echo      BSEE.bat test              - Run validation tests
echo      BSEE.bat help              - Show this help
echo.
echo    Configuration Presets:
echo      - neural_network:    Advanced ML-based analysis
echo      - performance:       Speed-optimized analysis
echo      - research:          Comprehensive research analysis
echo.
echo    Examples:
echo      BSEE.bat gui data.bin
echo      BSEE.bat cli data.bin --strategy mcts --max-operations 1000
echo      BSEE.bat preset neural_network
echo.
echo    For more detailed help, run:
echo      python main.py --help
echo.
timeout /t 5 /nobreak >nul
goto interactive_mode

:exit_bsee
echo.
echo    [INFO] Thank you for using BSEE!
echo    [INFO] Visit https://github.com/bsee/bsee for updates and documentation
echo.
pause
exit /b 0

:end_script
echo.
echo    [INFO] BSEE session completed
echo    [INFO] Logs and results saved to their respective directories
echo.

:: Optional: Keep window open for debugging (uncomment if needed)
:: pause
exit /b 0