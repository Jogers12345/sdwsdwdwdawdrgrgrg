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
setlocal enabledelayedexpansion

:: Prevent multiple initialization loops
if "%BSEE_INIT%"=="1" goto main
set BSEE_INIT=1

:: Configuration
set PROJECT_NAME=BSEE
set PROJECT_DIR=%~dp0..
set VENV_DIR=%PROJECT_DIR%\venv
set MIN_PYTHON_VERSION=3.9
set LOG_FILE=%PROJECT_DIR%\logs\install.log

:: Create logs directory if it doesn't exist
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

:: Change to script directory
cd /d "%~dp0"

:: Display welcome banner
echo.
echo  ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
echo  ║                         BSEE - Binary Structure Exploration Engine                         ║
echo  ║                         Advanced Binary Analysis & Optimization                      ║
echo  ║                                    Version 2.1                                      ║
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

:: Function to display info
:info
echo    [INFO] %~1
echo [INFO] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display error
:error
echo    [ERROR] %~1
echo [ERROR] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display success
:success
echo    [SUCCESS] %~1
echo [INFO] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display warning
:warning
echo    [WARNING] %~1
echo [WARNING] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Check Python installation with detailed version check
echo    [1/8] Checking Python installation...
call :info "Checking Python installation..."
python --version >nul 2>&1
if errorlevel 1 (
    call :error "Python is not installed or not in PATH"
    echo.
    echo    Would you like to download and install Python?
    echo    1. Yes (recommended)
    echo    2. No (I'll install manually)
    echo    3. Try to find existing Python installation
    echo.
    set /p choice="Select option (1-3): "

    if "!choice!"=="1" (
        call :info "Opening Python download page..."
        start https://www.python.org/downloads/
        call :display "Please download Python 3.9 or higher and run the installer."
        call :display "Make sure to check 'Add Python to PATH' during installation."
        pause
        goto :check_python_again
    ) else if "!choice!"=="2" (
        call :error "Please install Python 3.9+ manually and add it to PATH"
        pause
        exit /b 1
    ) else if "!choice!"=="3" (
        call :info "Searching for Python installations..."
        call :find_python
    ) else (
        call :error "Invalid choice. Exiting."
        pause
        exit /b 1
    )
) else (
    goto :check_python_version
)

:check_python_again
python --version >nul 2>&1
if errorlevel 1 (
    call :error "Python still not found. Please install Python and try again."
    pause
    exit /b 1
)

:check_python_version
:: Get detailed Python version information
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

call :success "Found Python %PYTHON_VERSION% (Major: %PYTHON_MAJOR%, Minor: %PYTHON_MINOR%)"

:: Validate Python version
if %PYTHON_MAJOR% LSS 3 (
    call :error "Python 3.9+ is required. Found Python %PYTHON_MAJOR%.%PYTHON_MINOR%"
    echo    Please upgrade Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 9 (
        call :error "Python 3.9+ is required. Found Python %PYTHON_MAJOR%.%PYTHON_MINOR%"
        echo    Please upgrade Python from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

call :success "Python version check passed"

:: =============================================================================
:: STEP 2: Virtual Environment Management
:: =============================================================================
echo    [2/8] Setting up Python virtual environment...

:: Remove old virtual environment if corrupted
if exist "venv\Lib\site-packages\pip" (
    if not exist "venv\Lib\site-packages\pip\__init__.py" (
        call :warning "Corrupted virtual environment detected, removing..."
        if exist "venv" rmdir /s /q "venv"
    )
)

:: Create or verify virtual environment
if not exist "venv\" (
    call :info "Creating virtual environment..."
    python -m venv venv --clear
    if errorlevel 1 (
        call :error "Failed to create virtual environment"
        echo    This may be due to Python installation issues or insufficient permissions.
        pause
        exit /b 1
    )
    call :success "Virtual environment created"
) else (
    call :info "Virtual environment exists"
)

:: Activate virtual environment with fallback mechanisms
echo    [3/8] Activating virtual environment...

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    if errorlevel 1 (
        call :error "Failed to activate virtual environment"
        goto venv_recovery
    )
    call :success "Virtual environment activated"
) else (
    :venv_recovery
    call :warning "Activation script not found, attempting recovery..."
    if exist "venv" rmdir /s /q "venv"
    python -m venv venv
    if exist "venv\Scripts\activate.bat" (
        call "venv\Scripts\activate.bat"
        call :success "Virtual environment recovered and activated"
    ) else (
        call :error "Failed to recover virtual environment"
        pause
        exit /b 1
    )
)

:: Upgrade pip
echo    [INFO] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    call :warning "Failed to upgrade pip, continuing with current version"
) else (
    call :success "Pip upgraded successfully"
)

:: =============================================================================
:: STEP 3: Comprehensive Dependency Installation
:: =============================================================================
echo    [4/8] Installing and verifying dependencies...

:: Check if requirements directory exists
set REQUIREMENTS_DIR=%PROJECT_DIR%\requirements
if exist "%REQUIREMENTS_DIR%" (
    call :info "Found requirements directory, installing from multiple files..."

    :: Install base requirements
    if exist "%REQUIREMENTS_DIR%\base.txt" (
        call :info "Installing base requirements..."
        python -m pip install -r "%REQUIREMENTS_DIR%\base.txt"
        if errorlevel 1 (
            call :warning "Some base requirements failed to install"
        ) else (
            call :success "Base requirements installed"
        )
    )

    :: Install GUI requirements
    if exist "%REQUIREMENTS_DIR%\gui.txt" (
        call :info "Installing GUI requirements..."
        python -m pip install -r "%REQUIREMENTS_DIR%\gui.txt"
        if errorlevel 1 (
            call :warning "Some GUI requirements failed to install"
        ) else (
            call :success "GUI requirements installed"
        )
    )

    :: Install ML requirements
    if exist "%REQUIREMENTS_DIR%\ml.txt" (
        call :info "Installing ML requirements..."
        python -m pip install -r "%REQUIREMENTS_DIR%\ml.txt"
        if errorlevel 1 (
            call :warning "Some ML requirements failed to install"
        ) else (
            call :success "ML requirements installed"
        )
    )

    :: Install development requirements
    if exist "%REQUIREMENTS_DIR%\dev.txt" (
        call :info "Installing development requirements..."
        python -m pip install -r "%REQUIREMENTS_DIR%\dev.txt"
        if errorlevel 1 (
            call :warning "Some development requirements failed to install"
        ) else (
            call :success "Development requirements installed"
        )
    )

    :: Install optional requirements
    if exist "%REQUIREMENTS_DIR%\optional.txt" (
        call :info "Installing optional requirements..."
        python -m pip install -r "%REQUIREMENTS_DIR%\optional.txt"
        if errorlevel 1 (
            call :warning "Some optional requirements failed to install"
        ) else (
            call :success "Optional requirements installed"
        )
    )
) else (
    :: Fallback to single requirements.txt file
    call :info "Installing from requirements.txt..."
    if exist "%PROJECT_DIR%\requirements.txt" (
        python -m pip install -r "%PROJECT_DIR%\requirements.txt"
        if errorlevel 1 (
            call :warning "Some requirements failed to install"
        ) else (
            call :success "Requirements installed"
        )
    ) else (
        call :warning "No requirements files found, skipping dependency installation"
    )
)

:: Install the project itself if pyproject.toml exists
if exist "%PROJECT_DIR%\pyproject.toml" (
    call :info "Installing project in development mode..."
    python -m pip install -e .
    if errorlevel 1 (
        call :warning "Project installation failed, continuing anyway"
    ) else (
        call :success "Project installed in development mode"
    )
)

:: =============================================================================
:: STEP 4: System and Hardware Optimization
:: =============================================================================
echo    [5/8] Optimizing for Windows environment...

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
    call :info "Administrator privileges detected - setting file associations..."
    assoc .bin=BSEEFile >nul 2>&1
    ftype BSEEFile="\"%CD%\BSEE.bat\" \"%%1\"" >nul 2>&1
)

:: Optimize Windows performance settings
if %IS_ADMIN% EQU 1 (
    call :info "Optimizing Windows performance settings..."
    :: Set process priority (will be applied when GUI starts)
    wmic process where "name='python.exe'" CALL setpriority "high priority" >nul 2>&1
)

:: =============================================================================
:: STEP 5: Validation and Diagnostics
:: =============================================================================
echo    [6/8] Validating installation...

:: Test core imports
call :info "Testing core module imports..."
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
    call :warning "Some core modules failed to import - functionality may be limited"
) else (
    call :success "All core modules imported successfully"
)

:: Check BSEE modules
call :info "Checking BSEE modules..."
python -c "
import sys
import os
from pathlib import Path

# Ensure project root is in Python path for BSEE imports
project_root = Path('.').resolve()
sys.path.insert(0, str(project_root))

# Additional fix for virtual environment compatibility
if 'VIRTUAL_ENV' in os.environ:
    venv_site_packages = Path(os.environ['VIRTUAL_ENV']) / 'Lib' / 'site-packages'
    if str(venv_site_packages) not in sys.path:
        sys.path.insert(0, str(venv_site_packages))

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
    call :warning "BSEE modules not found - running in development mode"
) else (
    call :success "BSEE modules validated"
)

:: Generate system information
call :info "Collecting system information..."
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
:: STEP 6: Testing Suite Integration
:: =============================================================================
echo    [7/8] Testing suite integration...

:: Check if tests directory exists
set TESTS_DIR=%PROJECT_DIR%\tests
if exist "%TESTS_DIR%" (
    call :display "Testing suite found. Would you like to:"
    call :display "1. Run smoke tests (quick validation)"
    call :display "2. Run full test suite"
    call :display "3. Skip tests for now"
    call :display ""
    set /p test_choice="Select option (1-3): "

    if "!test_choice!"=="1" (
        call :info "Running smoke tests..."
        call :run_smoke_tests
    ) else if "!test_choice!"=="2" (
        call :info "Running full test suite..."
        call :run_full_tests
    ) else if "!test_choice!"=="3" (
        call :info "Skipping tests"
    ) else (
        call :warning "Invalid choice, skipping tests"
    )
) else (
    call :warning "No tests directory found, skipping testing suite"
)

:: =============================================================================
:: STEP 7: Launch Interface Selection
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
    echo    [3] Test Mode     - Run validation tests
    echo    [4] Development Mode - Launch with development preset and debug flags
    echo    [5] Preset Mode   - Choose from predefined configurations
    echo    [6] Configuration Check - Validate all config files and show status
    echo    [7] Help          - Show detailed help and documentation
    echo    [8] Exit          - Exit BSEE
    echo.

    choice /c 12345678 /n /m "Select option (1-8): "

    if errorlevel 8 goto exit_bsee
    if errorlevel 7 goto show_help
    if errorlevel 6 goto check_configuration
    if errorlevel 5 goto preset_mode
    if errorlevel 4 goto launch_development
    if errorlevel 3 goto launch_test
    if errorlevel 2 goto launch_cli
    if errorlevel 1 goto launch_gui

:command_mode
if "%~1"=="gui" goto launch_gui
if "%~1"=="cli" goto launch_cli
if "%~1"=="test" goto launch_test
if "%~1"=="dev" goto launch_development
if "%~1"=="development" goto launch_development
if "%~1"=="preset" goto preset_mode
if "%~1"=="config" goto check_configuration
if "%~1"=="help" goto show_help

echo    [INFO] Unknown argument: %~1
echo    Use --help for available options
goto main

:: ===============================================
:: Launch Functions
:: ===============================================

:launch_gui
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
    call :error "GUI application not found"
    echo    Falling back to CLI mode...
    timeout /t 3 /nobreak >nul
    goto launch_cli
)
goto end_script

:launch_cli
echo.
echo    [INFO] Starting BSEE CLI Interface...
echo    [INFO] Loading command-line components...

if not exist "legacy\main.py" (
    call :error "Main application not found"
    timeout /t 3 /nobreak >nul
    goto interactive_mode
)

:: Check if input file provided
if "%~2"=="" (
    echo    [INFO] No input file provided, entering interactive CLI mode
    echo.
    echo    Available options:
    echo    - Drag and drop a file onto this window
    echo    - Type file path manually
    echo    - Type 'help' for CLI commands
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

:launch_test
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
    python tests\run_phase4_tests.py --verbose
) else (
    call :error "Test suite not found"
    echo    Please ensure you have the complete BSEE installation
)

echo.
echo    [INFO] Test execution completed
timeout /t 3 /nobreak >nul
goto interactive_mode

:launch_development
echo.
echo    [INFO] Launching BSEE in development mode...
set DEVELOPMENT_SCRIPT=%PROJECT_DIR%\legacy\main.py
if exist "%DEVELOPMENT_SCRIPT%" (
    python "%DEVELOPMENT_SCRIPT%" --preset development --debug %*
) else (
    call :error "Development script not found"
    pause
    exit /b 1
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
    call :error "Preset file not found: %PRESET_FILE%"
    echo    Using default configuration...
    python legacy\main.py
)
goto end_script

:check_configuration
call :info "Checking configuration files..."
set CONFIG_DIR=%PROJECT_DIR%\config
if exist "%CONFIG_DIR%" (
    call :success "Configuration directory found"

    :: Check strategies
    if exist "%CONFIG_DIR%\strategies\" (
        call :info "Strategy configurations:"
        dir "%CONFIG_DIR%\strategies\" /b *.yaml
    ) else (
        call :warning "No strategies directory found"
    )

    :: Check policies
    if exist "%CONFIG_DIR%\policies\" (
        call :info "Policy configurations:"
        dir "%CONFIG_DIR%\policies\" /b *.yaml
    ) else (
        call :warning "No policies directory found"
    )

    :: Check costs
    if exist "%CONFIG_DIR%\costs\" (
        call :info "Cost configurations:"
        dir "%CONFIG_DIR%\costs\" /b *.yaml
    ) else (
        call :warning "No costs directory found"
    )

    :: Check presets
    if exist "%CONFIG_DIR%\presets\" (
        call :info "Preset configurations:"
        dir "%CONFIG_DIR%\presets\" /b *.yaml
    ) else (
        call :warning "No presets directory found"
    )

    call :success "Configuration check completed"
) else (
    call :error "Configuration directory not found"
)
pause
goto interactive_mode

:show_help
echo.
echo    [INFO] BSEE Help and Documentation
echo.
echo    BSEE (Binary Structure Exploration Engine) is an advanced tool for analyzing and
echo    optimizing binary files through reversible transformations.
echo.
echo    Usage:
echo      BSEE.bat                        - Interactive mode
echo      BSEE.bat gui [file]              - Start GUI mode
echo      BSEE.bat cli [file] [args]       - Start CLI mode
echo      BSEE.bat test                    - Run validation tests
echo      BSEE.bat dev [args]              - Development mode with debug flags
echo      BSEE.bat preset [name]           - Use configuration preset
echo      BSEE.bat config                  - Check configuration status
echo      BSEE.bat help                    - Show this help
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
echo    Requirements Installation:
echo      BSEE uses modular requirements in requirements/ folder:
echo      - base.txt: Core runtime dependencies
echo      - gui.txt: Graphical interface dependencies
echo      - ml.txt: Machine learning dependencies
echo      - dev.txt: Development and testing dependencies
echo      - optional.txt: Optional performance dependencies
echo.
echo    For more detailed help, run:
echo      python legacy/main.py --help
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

:: ===============================================
:: Helper Functions
:: ===============================================

:find_python
call :info "Searching for Python installations in common locations..."

:: Check common Python installation paths
for %%P in (
    "C:\Python39\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Program Files\Python39\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files (x86)\Python39\python.exe"
    "C:\Program Files (x86)\Python310\python.exe"
    "C:\Program Files (x86)\Python311\python.exe"
    "C:\Program Files (x86)\Python312\python.exe"
) do (
    if exist "%%P" (
        call :success "Found Python at: %%P"
        set PYTHON_PATH=%%P
        :: Add to PATH for current session
        set PATH=%%~dpP;%PATH%
        goto :python_found
    )
)

call :error "Python not found in common locations"
call :display "Please install Python manually and try again"
pause
exit /b 1

:python_found
call :success "Python found and added to PATH"
goto :eof

:: ===============================================
:: Testing Functions
:: ===============================================

:run_smoke_tests
call :info "Running smoke tests for startup validation..."
if exist "%TESTS_DIR%\test_smoke.py" (
    python "%TESTS_DIR%\test_smoke.py"
    if errorlevel 1 (
        call :warning "Some smoke tests failed"
    ) else (
        call :success "All smoke tests passed"
    )
) else (
    call :warning "Smoke test file not found, creating basic validation..."
    :: Create basic smoke test
    python -c "
import sys
print('Basic validation:')
print('Python version:', sys.version)
try:
    import numpy as np
    print('NumPy:', np.__version__)
except ImportError:
    print('NumPy not available')
try:
    import scipy
    print('SciPy available')
except ImportError:
    print('SciPy not available')
print('Basic validation completed')
"
)
goto :eof

:run_full_tests
call :info "Running full test suite..."
if exist "%TESTS_DIR%\run_tests.py" (
    python "%TESTS_DIR%\run_tests.py"
    if errorlevel 1 (
        call :warning "Some tests failed"
    ) else (
        call :success "All tests passed"
    )
) else (
    call :info "Running pytest on tests directory..."
    python -m pytest "%TESTS_DIR%" -v
    if errorlevel 1 (
        call :warning "Some tests failed"
    ) else (
        call :success "All tests passed"
    )
)
goto :eof

:: ===============================================
:: Function to display text
:: ===============================================
:display
echo %~1
goto :eof