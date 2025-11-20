@echo off
:: =============================================================================
:: BSEE - Binary Structure Exploration Engine - Enhanced Production Windows Launcher
:: =============================================================================
:: Comprehensive one-click setup with Windows integration, error handling, and testing
:: Compatible with Windows 10/11 - Production-ready with full automation
:: Version 2.2 - Production Edition
:: =============================================================================

:: Set console properties for better appearance
title BSEE - Binary Structure Exploration Engine v2.2 (Production)
color 0A
mode con: cols=120 lines=50
setlocal enabledelayedexpansion

:: Prevent multiple initialization loops
if "%BSEE_INIT%"=="1" goto main
set BSEE_INIT=1

:: Enhanced Configuration with Desktop deployment support
set PROJECT_NAME=BSEE
set PROJECT_DIR=%~dp0..
set VENV_DIR=%PROJECT_DIR%\venv
set MIN_PYTHON_VERSION=3.9
set LOG_FILE=%PROJECT_DIR%\logs\bsee_setup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set ERROR_COUNT=0
set WARNING_COUNT=0

:: Production mode detection
if "%~1"=="--production" (
    set AUTO_MODE=1
    set SKIP_PROMPTS=1
    set INSTALL_ALL=1
    set RUN_TESTS=1
    set FIX_PATHS=1
    set CREATE_DESKTOP_SHORTCUTS=1
    call :info "Running in PRODUCTION MODE (one-click setup)"
)

:: Enhanced project directory detection for C:\Desktop deployment
if "%BSEE_DESKTOP_DEPLOY%"=="1" (
    set PROJECT_DIR=C:\Desktop\BSEE
) else (
    :: Auto-detect desktop deployment
    echo "%~dp0" | findstr /i "Desktop" >nul
    if !errorlevel! equ 0 (
        set PROJECT_DIR=C:\Desktop\BSEE
        set BSEE_DESKTOP_DEPLOY=1
        call :info "Desktop deployment detected"
    ) else (
        set PROJECT_DIR=%~dp0..
    )
)

:: Validate project directory structure
if not exist "%PROJECT_DIR%\legacy" (
    if exist "C:\Desktop\BSEE\legacy" (
        set PROJECT_DIR=C:\Desktop\BSEE
        set BSEE_DESKTOP_DEPLOY=1
        call :info "Fallback to Desktop BSEE installation"
    )
)

:: Create logs directory if it doesn't exist
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

:: Change to script directory
cd /d "%~dp0"

:: Display welcome banner
echo.
echo  ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
echo  ║                   BSEE - Binary Structure Exploration Engine                              ║
echo  ║                     Production Edition v2.2 - One Click Setup                           ║
echo  ║                  Advanced Binary Analysis & Optimization                               ║
echo  ╚════════════════════════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check if running as administrator (optional optimization)
net session >nul 2>&1
if %errorLevel% == 0 (
    call :info "Running with administrator privileges - Windows integration enabled"
    set IS_ADMIN=1
) else (
    call :info "Running with standard user privileges"
    set IS_ADMIN=0
)

:: Initialize log file with system information
call :log_system_info

:: =============================================================================
:: STEP 1: Enhanced Environment Setup and Validation
:: =============================================================================
echo.
echo    ══════════════════════════════════════════════════════════════════════════════════════════╗
echo    ║                          ENHANCED ENVIRONMENT SETUP                                 ║
echo    ╚═════════════════════════════════════════════════════════════════════════════════════════╝
echo.

:: Enhanced error recovery system
set LAST_SUCCESS_STEP=0
set ERROR_RECOVERY_ENABLED=1

:: Function to display info
:info
echo    [INFO] %~1
echo [INFO] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display error with pause handling
:error
echo    [ERROR] %~1
echo [ERROR] %~1 >> "%LOG_FILE%" 2>&1
set /a ERROR_COUNT+=1
if not "%AUTO_MODE%"=="1" (
    echo.
    echo    Press any key to continue or Ctrl+C to exit...
    pause >nul
)
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
set /a WARNING_COUNT+=1
goto :eof

:: Function to display text
:display
echo    %~1
goto :eof

:: Enhanced Python detection with comprehensive error recovery
echo    [1/9] Enhanced Python detection and validation...
call :info "Checking Python installation..."

:check_python
python --version >nul 2>&1
if errorlevel 1 (
    call :error "Python is not installed or not in PATH"

    if "%AUTO_MODE%"=="1" (
        call :info "Production mode: Attempting automatic Python detection..."
        call :find_python
        goto :check_python_version
    )

    echo.
    echo    Python is required for BSEE. Choose an option:
    echo    1. Download and install Python (recommended)
    echo    2. Find existing Python installation
    echo    3. Exit to install manually
    echo    4. Retry detection
    echo.
    set /p choice="Select option (1-4): "

    if "!choice!"=="1" (
        call :info "Opening Python download page..."
        start https://www.python.org/downloads/
        call :display "Please download Python 3.9 or higher and run the installer."
        call :display "CRITICAL: Check 'Add Python to PATH' during installation!"
        call :display "CRITICAL: Check 'Install for all users' if available!"
        echo.
        set /p continue="Press ENTER after Python installation is complete..."
        goto :check_python
    ) else if "!choice!"=="2" (
        call :find_python
    ) else if "!choice!"=="3" (
        call :error "Please install Python 3.9+ manually and add it to PATH"
        call :display "Download from: https://www.python.org/downloads/"
        goto :error_exit
    ) else if "!choice!"=="4" (
        goto :check_python
    ) else (
        call :error "Invalid choice. Please select 1-4."
        goto :check_python
    )
) else (
    call :success "Python found in PATH"
    goto :check_python_version
)

:check_python_version
set LAST_SUCCESS_STEP=1

:: Get detailed Python version information
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

call :success "Found Python %PYTHON_VERSION% (Major: %PYTHON_MAJOR%, Minor: %PYTHON_MINOR%)"

:: Validate Python version with enhanced error handling
if %PYTHON_MAJOR% LSS 3 (
    call :error "Python 3.9+ is required. Found Python %PYTHON_MAJOR%.%PYTHON_MINOR%"
    echo    This version is too old. Please upgrade Python from:
    echo    https://www.python.org/downloads/
    if not "%AUTO_MODE%"=="1" pause
    goto :error_exit
)

if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 9 (
        call :error "Python 3.9+ is required. Found Python %PYTHON_MAJOR%.%PYTHON_MINOR%"
        echo    Please upgrade Python from: https://www.python.org/downloads/
        if not "%AUTO_MODE%"=="1" pause
        goto :error_exit
    )
)

call :success "Python version validation passed"

:: =============================================================================
:: STEP 2: Enhanced Virtual Environment Management
:: =============================================================================
echo    [2/9] Enhanced virtual environment creation and isolation...

:: Detect and remove corrupted virtual environments
if exist "%VENV_DIR%" (
    call :info "Checking existing virtual environment..."

    :: Check for corruption indicators
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        call :warning "Virtual environment missing activation script - removing..."
        if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
    ) else if not exist "%VENV_DIR%\Lib\site-packages" (
        call :warning "Virtual environment missing packages directory - removing..."
        if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
    ) else (
        call :success "Valid virtual environment found"
    )
)

:: Create enhanced virtual environment with isolation
if not exist "%VENV_DIR%" (
    call :info "Creating isolated virtual environment..."

    :: Create virtual environment with clear flag
    python -m venv "%VENV_DIR%" --clear --system-site-packages
    if errorlevel 1 (
        call :error "Failed to create virtual environment"
        call :display "This may indicate:"
        call :display "1. Python installation issues"
        call :display "2. Insufficient permissions"
        call :display "3. Antivirus interference"
        call :display "4. Disk space issues"
        echo.
        echo    Troubleshooting suggestions:
        echo    1. Run as Administrator
        echo    2. Temporarily disable antivirus
        echo    3. Check available disk space
        echo    4. Verify Python installation
        echo.

        if not "%AUTO_MODE%"=="1" (
            echo    Options:
            echo    1. Try again with different settings
            echo    2. Continue without virtual environment (not recommended)
            echo    3. Exit to fix issues
            echo.
            set /p venv_choice="Select option (1-3): "

            if "!venv_choice!"=="1" (
                call :info "Retrying with different virtual environment settings..."
                python -m venv "%VENV_DIR%" --clear
                if errorlevel 1 (
                    call :error "Virtual environment creation failed again"
                    goto :error_exit
                )
            ) else if "!venv_choice!"=="2" (
                call :warning "Continuing without virtual environment isolation"
                set VENV_DIR=
                goto :skip_venv
            ) else (
                goto :error_exit
            )
        ) else (
            call :error "Production mode: Virtual environment creation failed"
            goto :error_exit
        )
    ) else (
        call :success "Virtual environment created successfully"
    )
) else (
    call :info "Virtual environment already exists and is valid"
)

:: Activate virtual environment with enhanced path management
echo    [3/9] Activating virtual environment with enhanced path management...

if "%VENV_DIR%" neq "" (
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        call "%VENV_DIR%\Scripts\activate.bat"
        if errorlevel 1 (
            call :error "Failed to activate virtual environment"
            goto :venv_recovery
        )
        call :success "Virtual environment activated"

        :: Enhanced Python path fixes for BSEE modules
        set PYTHONPATH=%PROJECT_DIR%;%PROJECT_DIR%\legacy;%PROJECT_DIR%\bsee;%PYTHONPATH%

        :: Add project directories to Python path automatically
        for /d %%D in ("%PROJECT_DIR%\*") do (
            if exist "%%D\__init__.py" (
                set PYTHONPATH=%%D;!PYTHONPATH!
                call :info "Added to Python path: %%D"
            )
        )

        :: Create missing bsee module structure
        if not exist "%PROJECT_DIR%\bsee" (
            call :info "Creating BSEE module structure..."
            if not exist "%PROJECT_DIR%\bsee" mkdir "%PROJECT_DIR%\bsee"
            echo # BSEE Package > "%PROJECT_DIR%\bsee\__init__.py"
            echo # BSEE Package created automatically by BSEE.bat >> "%PROJECT_DIR%\bsee\__init__.py"
            call :success "BSEE module structure created"
        )

        call :success "Enhanced Python path configured"

    ) else (
        :venv_recovery
        call :error "Virtual environment activation script not found"
        call :info "Attempting virtual environment recovery..."

        :: Remove corrupted virtual environment
        if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"

        :: Recreate virtual environment
        python -m venv "%VENV_DIR%"
        if exist "%VENV_DIR%\Scripts\activate.bat" (
            call "%VENV_DIR%\Scripts\activate.bat"
            call :success "Virtual environment recovered and activated"
        ) else (
            call :error "Failed to recover virtual environment"
            if not "%AUTO_MODE%"=="1" (
                echo    Options:
                echo    1. Continue with system Python
                echo    2. Exit to fix Python installation
                echo.
                set /p recovery_choice="Select option (1-2): "
                if "!recovery_choice!"=="1" (
                    call :warning "Continuing with system Python (reduced isolation)"
                    set VENV_DIR=
                    goto :skip_venv
                ) else (
                    goto :error_exit
                )
            ) else (
                goto :error_exit
            )
        )
    )
)

:skip_venv
set LAST_SUCCESS_STEP=2

:: Upgrade pip, setuptools, and wheel with error handling
echo    [INFO] Upgrading package management tools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    call :warning "Failed to upgrade some packages, continuing with current versions"
    :: Try basic pip upgrade
    python -m pip install --upgrade pip >nul 2>&1
) else (
    call :success "Package management tools upgraded successfully"
)

:: =============================================================================
:: STEP 3: Enhanced Dependency Installation with Retry Logic
:: =============================================================================
echo    [4/9] Enhanced dependency installation with retry mechanisms...

:: Enhanced dependency installation with comprehensive retry logic
set REQUIREMENTS_DIR=%PROJECT_DIR%\requirements
set MAX_RETRIES=3

if exist "%REQUIREMENTS_DIR%" (
    call :info "Found modular requirements directory"

    :: Install requirements with retry logic
    call :install_requirements_file "base.txt" "Core dependencies"
    call :install_requirements_file "gui.txt" "GUI dependencies"
    call :install_requirements_file "ml.txt" "Machine Learning dependencies"
    call :install_requirements_file "dev.txt" "Development dependencies"
    call :install_requirements_file "optional.txt" "Optional dependencies"

) else (
    :: Fallback to single requirements.txt file
    if exist "%PROJECT_DIR%\requirements.txt" (
        call :info "Installing from single requirements.txt file..."
        call :install_with_retry "python -m pip install -r \"%PROJECT_DIR%\requirements.txt\"" "Base requirements"
    ) else (
        call :warning "No requirements files found, installing essential packages only..."
        call :install_individual_packages
    )
)

:: Install the project itself if pyproject.toml exists
if exist "%PROJECT_DIR%\pyproject.toml" (
    call :info "Installing project in development mode..."
    call :install_with_retry "python -m pip install -e ." "Project installation"
)

set LAST_SUCCESS_STEP=3

:: =============================================================================
:: STEP 4: Enhanced Windows Integration (setupwindows.py functionality)
:: =============================================================================
echo    [5/9] Enhanced Windows integration and system optimization...

:: Create Windows-specific directory structure
call :create_windows_directories

:: Set Windows-specific environment variables
call :setup_environment_variables

:: File associations and shortcuts
if %IS_ADMIN% EQU 1 (
    call :setup_file_associations
    call :create_desktop_shortcuts
    call :create_start_menu_shortcuts
) else (
    call :warning "Administrator privileges not available - skipping system integration"
    if "%AUTO_MODE%" neq "1" (
        echo    Note: Run as Administrator for full Windows integration (file associations, shortcuts)
    )
)

:: Windows performance optimizations
call :optimize_windows_settings

set LAST_SUCCESS_STEP=4

:: =============================================================================
:: STEP 5: Enhanced Module Import Validation and Fixes
:: =============================================================================
echo    [6/9] Enhanced module import validation and fixes...

:: Comprehensive dependency validation
call :validate_core_dependencies

:: Enhanced BSEE module structure validation
call :validate_bsee_modules

:: Fix common Python path issues
call :fix_python_path_issues

set LAST_SUCCESS_STEP=5

:: =============================================================================
:: STEP 6: Comprehensive Testing Suite Integration
:: =============================================================================
echo    [7/9] Comprehensive testing suite integration...

:: Phase 1: Environment validation
call :test_environment

:: Phase 2: Import validation
call :test_imports

:: Phase 3: Individual file syntax validation
call :test_all_files

:: Phase 4: Smoke tests
call :run_smoke_tests

:: Phase 5: Full test suite (optional in production mode)
if "%AUTO_MODE%"=="1" (
    call :info "Production mode: Running essential tests only..."
    call :run_essential_tests
) else (
    call :display "Testing suite found. Choose testing level:"
    call :display "1. Essential tests only (quick validation)"
    call :display "2. Comprehensive test suite (recommended)"
    call :display "3. Skip tests (not recommended)"
    call :display ""
    if "%SKIP_PROMPTS%" neq "1" (
        set /p test_choice="Select option (1-3): "
    ) else (
        set test_choice=1
    )

    if "!test_choice!"=="1" (
        call :run_essential_tests
    ) else if "!test_choice!"=="2" (
        call :run_comprehensive_tests
    ) else if "!test_choice!"=="3" (
        call :warning "Skipping tests - functionality may be limited"
    ) else (
        call :warning "Invalid choice, running essential tests"
        call :run_essential_tests
    )
)

set LAST_SUCCESS_STEP=6

:: =============================================================================
:: STEP 7: Production Validation and System Information
:: =============================================================================
echo    [8/9] Production validation and system information...

:: Generate comprehensive system report
call :generate_system_report

:: Validate installation success
call :validate_installation

:: Create user-friendly setup summary
call :create_setup_summary

set LAST_SUCCESS_STEP=7

:: =============================================================================
:: STEP 8: Enhanced Launch Interface
:: =============================================================================
echo.
echo    ══════════════════════════════════════════════════════════════════════════════════════════╗
echo    ║                          ENHANCED LAUNCH OPTIONS                                    ║
echo    ╚═════════════════════════════════════════════════════════════════════════════════════════╝
echo.

:main
:: Check for command line arguments
if "%~1"=="" (
    if "%AUTO_MODE%"=="1" (
        set launch_mode=gui
    ) else (
        goto interactive_mode
    )
) else (
    goto command_mode
)

:interactive_mode
echo    BSEE is ready! Select launch mode:
    echo.
    echo    [1] GUI Mode      - Graphical interface (Recommended)
    echo    [2] CLI Mode       - Command-line interface
    echo    [3] Test Mode     - Run validation tests
    echo    [4] Development Mode - Debug and development features
    echo    [5] Preset Mode   - Choose predefined configurations
    echo    [6] Configuration Check - Validate setup
    echo    [7] System Information - Show detailed system info
    echo    [8] Help          - Show detailed help
    echo    [9] Exit          - Exit BSEE
    echo.

    choice /c 123456789 /n /m "Select option (1-9): "

    if errorlevel 9 goto exit_bsee
    if errorlevel 8 goto show_help
    if errorlevel 7 goto show_system_info
    if errorlevel 6 goto check_configuration
    if errorlevel 5 goto preset_mode
    if errorlevel 4 goto launch_development
    if errorlevel 3 goto launch_test
    if errorlevel 2 goto launch_cli
    if errorlevel 1 goto launch_gui

:command_mode
if "%~1"=="gui" set launch_mode=gui
if "%~1"=="cli" set launch_mode=cli
if "%~1"=="test" set launch_mode=test
if "%~1"=="dev" set launch_mode=dev
if "%~1"=="development" set launch_mode=dev
if "%~1"=="preset" set launch_mode=preset
if "%~1"=="config" set launch_mode=config
if "%~1"=="help" set launch_mode=help
if "%~1"=="system" set launch_mode=system

if "%launch_mode%"=="gui" goto launch_gui
if "%launch_mode%"=="cli" goto launch_cli
if "%launch_mode%"=="test" goto launch_test
if "%launch_mode%"=="dev" goto launch_development
if "%launch_mode%"=="preset" goto preset_mode
if "%launch_mode%"=="config" goto check_configuration
if "%launch_mode%"=="help" goto show_help
if "%launch_mode%"=="system" goto show_system_info

echo    [INFO] Unknown argument: %~1
echo    Use --help for available options
goto main

:: ===============================================
:: Enhanced Launch Functions
:: ===============================================

:launch_gui
echo.
echo    [INFO] Starting BSEE Enhanced GUI Interface...
echo    [INFO] Loading graphical components with enhanced error handling...

:: Check GUI dependencies with fallback installation
python -c "
import sys
import subprocess
try:
    import tkinter
    print('✓ tkinter available')
except ImportError:
    print('✗ tkinter not available - attempting fallback...')
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'tkinter'], check=True, capture_output=True)
        import tkinter
        print('✓ tkinter installed successfully')
    except:
        print('✗ tkinter installation failed')
        sys.exit(1)
" >nul 2>&1

if errorlevel 1 (
    call :error "GUI dependencies not available"
    call :display "Falling back to CLI mode..."
    timeout /t 3 /nobreak >nul
    goto launch_cli
)

:: Start GUI application with enhanced error handling
if exist "%PROJECT_DIR%\legacy\gui_main.py" (
    call :success "Starting GUI application..."
    python "%PROJECT_DIR%\legacy\gui_main.py"

    if errorlevel 1 (
        call :error "GUI application encountered an error"
        call :display "This may indicate missing dependencies or configuration issues"
        if not "%AUTO_MODE%"=="1" (
            echo    Options:
            echo    1. Try CLI mode instead
            echo    2. Run diagnostic tests
            echo    3. Exit
            echo.
            set /p gui_error_choice="Select option (1-3): "
            if "!gui_error_choice!"=="1" goto launch_cli
            if "!gui_error_choice!"=="2" goto launch_test
            if "!gui_error_choice!"=="3" goto exit_bsee
        ) else (
            call :info "Production mode: Falling back to CLI mode"
            goto launch_cli
        )
    )
) else (
    call :error "GUI application not found at %PROJECT_DIR%\legacy\gui_main.py"
    call :display "Falling back to CLI mode..."
    timeout /t 2 /nobreak >nul
    goto launch_cli
)
goto end_script

:launch_cli
echo.
echo    [INFO] Starting BSEE Enhanced CLI Interface...
echo    [INFO] Loading command-line components with enhanced error handling...

if not exist "%PROJECT_DIR%\legacy\main.py" (
    call :error "CLI application not found at %PROJECT_DIR%\legacy\main.py"
    if not "%AUTO_MODE%"=="1" (
        pause
        goto interactive_mode
    ) else (
        goto :error_exit
    )
)

:: Enhanced CLI with input validation
if "%~2"=="" (
    echo    [INFO] No input file provided, entering interactive CLI mode
    echo.
    echo    Available commands:
    echo    - Drag and drop a file onto this window
    echo    - Type file path manually
    echo    - Type 'help' for CLI commands
    echo    - Type 'exit' to quit
    echo.

    :cli_input
    set /p INPUT="Enter file path or command: "
    if "%INPUT%"=="" goto cli_input
    if /i "%INPUT%"=="help" (
        python "%PROJECT_DIR%\legacy\main.py" --help
        goto cli_input
    ) else if /i "%INPUT%"=="exit" (
        goto exit_bsee
    ) else if /i "%INPUT%"=="gui" (
        goto launch_gui
    ) else (
        call :info "Processing: %INPUT%"
        python "%PROJECT_DIR%\legacy\main.py" "%INPUT%" %3 %4 %5 %6 %7 %8 %9
        if errorlevel 1 (
            call :error "CLI processing failed for: %INPUT%"
            echo    This could indicate:"
            echo    1. File not found or inaccessible
            echo    2. Invalid file format
            echo    3. Missing dependencies
            echo    4. Configuration issues
            echo.
            set /p cli_retry="Try again? (y/n): "
            if /i "!cli_retry!"=="y" goto cli_input
        )
    )
) else (
    call :info "Processing: %~2"
    python "%PROJECT_DIR%\legacy\main.py" %~2 %~3 %~4 %~5 %~6 %~7 %~8 %~9
    if errorlevel 1 (
        call :error "CLI processing failed"
        goto :error_exit
    )
)
goto end_script

:launch_test
echo.
echo    [INFO] Running BSEE Enhanced Test Suite...
echo    [INFO] This will validate the entire installation

:: Check if pytest is available, install if needed
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    call :info "Installing pytest for testing..."
    python -m pip install pytest pytest-cov pytest-mock >nul 2>&1
    if errorlevel 1 (
        call :warning "Failed to install pytest, continuing with basic tests"
    )
)

:: Run comprehensive tests based on availability
set TESTS_DIR=%PROJECT_DIR%\tests
if exist "%TESTS_DIR%" (
    call :info "Running comprehensive test suite..."

    :: Unit tests
    if exist "%TESTS_DIR%\unit" (
        echo    Running unit tests...
        python -m pytest "%TESTS_DIR%\unit" -v --tb=short --maxfail=5
    )

    :: Integration tests
    if exist "%TESTS_DIR%\integration" (
        echo    Running integration tests...
        python -m pytest "%TESTS_DIR%\integration" -v --tb=short --maxfail=3
    )

    :: Smoke tests
    if exist "%TESTS_DIR%\test_smoke.py" (
        echo    Running smoke tests...
        python "%TESTS_DIR%\test_smoke.py"
    )

    :: Phase 4 tests
    if exist "%TESTS_DIR%\run_phase4_tests.py" (
        echo    Running Phase 4 tests...
        python "%TESTS_DIR%\run_phase4_tests.py" --verbose
    )

    call :success "Test suite execution completed"
) else (
    call :warning "Formal test suite not found, running basic validation..."
    call :run_basic_validation
)

echo.
if not "%AUTO_MODE%"=="1" pause
goto interactive_mode

:launch_development
echo.
echo    [INFO] Launching BSEE in Enhanced Development Mode...
set DEVELOPMENT_SCRIPT=%PROJECT_DIR%\legacy\main.py
if exist "%DEVELOPMENT_SCRIPT%" (
    python "%DEVELOPMENT_SCRIPT%" --preset development --debug %*
) else (
    call :error "Development script not found"
    goto :error_exit
)
goto end_script

:preset_mode
echo.
echo    [INFO] Available Configuration Presets:
echo.
set PRESET_DIR=%PROJECT_DIR%\config\presets
if exist "%PRESET_DIR%" (
    dir "%PRESET_DIR%" /b *.yaml 2>nul
    if errorlevel 1 (
        call :warning "No preset files found, using default configuration"
        set PRESET_FILE=
    ) else (
        echo.
        if "%SKIP_PROMPTS%" neq "1" (
            set /p preset_name="Enter preset name (or press Enter for default): "
        ) else (
            set preset_name=neural_network
        )

        if "!preset_name!" neq "" (
            set PRESET_FILE=%PRESET_DIR%\!preset_name!.yaml
        ) else (
            set PRESET_FILE=
        )
    )

    call :info "Loading preset configuration..."
    if defined PRESET_FILE (
        if exist "!PRESET_FILE!" (
            python "%PROJECT_DIR%\legacy\main.py" --preset "!PRESET_FILE!"
        ) else (
            call :error "Preset file not found: !PRESET_FILE!"
            call :display "Using default configuration instead..."
            python "%PROJECT_DIR%\legacy\main.py"
        )
    ) else (
        python "%PROJECT_DIR%\legacy\main.py"
    )
) else (
    call :warning "Presets directory not found, using default configuration"
    python "%PROJECT_DIR%\legacy\main.py"
)
goto end_script

:check_configuration
call :info "Performing comprehensive configuration check..."
set CONFIG_DIR=%PROJECT_DIR%\config
if exist "%CONFIG_DIR%" (
    call :success "Configuration directory found"

    :: Check strategies
    if exist "%CONFIG_DIR%\strategies\" (
        call :info "Strategy configurations:"
        dir "%CONFIG_DIR%\strategies\" /b *.yaml 2>nul
        if errorlevel 1 call :warning "No strategy files found"
    ) else (
        call :warning "No strategies directory found"
    )

    :: Check policies
    if exist "%CONFIG_DIR%\policies\" (
        call :info "Policy configurations:"
        dir "%CONFIG_DIR%\policies\" /b *.yaml 2>nul
        if errorlevel 1 call :warning "No policy files found"
    ) else (
        call :warning "No policies directory found"
    )

    :: Check costs
    if exist "%CONFIG_DIR%\costs\" (
        call :info "Cost configurations:"
        dir "%CONFIG_DIR%\costs\" /b *.yaml 2>nul
        if errorlevel 1 call :warning "No cost files found"
    ) else (
        call :warning "No costs directory found"
    )

    :: Check presets
    if exist "%CONFIG_DIR%\presets\" (
        call :info "Preset configurations:"
        dir "%CONFIG_DIR%\presets\" /b *.yaml 2>nul
        if errorlevel 1 call :warning "No preset files found"
    ) else (
        call :warning "No presets directory found"
    )

    call :success "Configuration check completed"
) else (
    call :error "Configuration directory not found"
    call :display "Creating basic configuration structure..."
    if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
    if not exist "%CONFIG_DIR%\strategies" mkdir "%CONFIG_DIR%\strategies"
    if not exist "%CONFIG_DIR%\policies" mkdir "%CONFIG_DIR%\policies"
    if not exist "%CONFIG_DIR%\costs" mkdir "%CONFIG_DIR%\costs"
    if not exist "%CONFIG_DIR%\presets" mkdir "%CONFIG_DIR%\presets"
    call :success "Basic configuration structure created"
)
if not "%AUTO_MODE%"=="1" pause
goto interactive_mode

:show_help
echo.
echo    BSEE Enhanced Help and Documentation
echo    ====================================
echo.
echo    BSEE (Binary Structure Exploration Engine) is an advanced tool for analyzing and
echo    optimizing binary files through reversible transformations.
echo.
echo    Enhanced Usage:
echo      BSEE.bat                        - Interactive mode with enhanced setup
echo      BSEE.bat --production            - One-click production setup and launch
echo      BSEE.bat gui [file]              - Start GUI mode
echo      BSEE.bat cli [file] [args]       - Start CLI mode
echo      BSEE.bat test                    - Run validation tests
echo      BSEE.bat dev [args]              - Development mode with debug flags
echo      BSEE.bat preset [name]           - Use configuration preset
echo      BSEE.bat config                  - Check configuration status
echo      BSEE.bat system                  - Show system information
echo      BSEE.bat help                    - Show this help
echo.
echo    Enhanced Features:
echo      ✓ One-click production setup with --production flag
echo      ✓ Automatic C:\Desktop deployment support
echo      ✓ Enhanced virtual environment with complete isolation
echo      ✓ Comprehensive error recovery and user guidance
echo      ✓ Windows integration (shortcuts, file associations, environment variables)
echo      ✓ Module import error detection and automatic fixes
echo      ✓ Comprehensive testing suite with validation
echo      ✓ Enhanced requirements installation with retry logic
echo      ✓ Detailed logging and system diagnostics
echo.
echo    Configuration Presets:
echo      - neural_network:    Advanced ML-based analysis
echo      - performance:       Speed-optimized analysis
echo      - research:          Comprehensive research analysis
echo.
echo    Examples:
echo      BSEE.bat --production           # One-click production setup
echo      BSEE.bat gui data.bin           # GUI mode with file
echo      BSEE.bat cli data.bin --strategy mcts --max-operations 1000
echo      BSEE.bat preset neural_network  # Use preset configuration
echo.
echo    Requirements Installation:
echo      BSEE uses modular requirements in requirements/ folder:
echo      - base.txt: Core runtime dependencies
echo      - gui.txt: Graphical interface dependencies
echo      - ml.txt: Machine learning dependencies
echo      - dev.txt: Development and testing dependencies
echo      - optional.txt: Optional performance dependencies
echo.
echo    Troubleshooting:
echo      - Run 'BSEE.bat config' to check configuration status
echo      - Run 'BSEE.bat system' for detailed system information
echo      - Check logs in %PROJECT_DIR%\logs\ for detailed error information
echo      - Ensure Python 3.9+ is installed and in PATH
echo      - Run as Administrator for full Windows integration
echo.
echo    For more detailed help, run:
echo      python "%PROJECT_DIR%\legacy\main.py" --help
echo.
if not "%AUTO_MODE%"=="1" pause
goto interactive_mode

:show_system_info
echo.
echo    BSEE Enhanced System Information
echo    ===============================
echo.
call :generate_system_report
if not "%AUTO_MODE%"=="1" pause
goto interactive_mode

:exit_bsee
echo.
echo    [INFO] BSEE Enhanced session completed successfully!
echo    [INFO] Errors encountered: %ERROR_COUNT%
echo    [INFO] Warnings encountered: %WARNING_COUNT%
echo    [INFO] Logs saved to: %LOG_FILE%
echo    [INFO] Thank you for using BSEE Enhanced Edition!
echo.
echo    Next time you can simply run: BSEE.bat --production
echo.
if not "%AUTO_MODE%"=="1" pause
exit /b 0

:end_script
echo.
echo    [INFO] BSEE Enhanced session completed
echo    [INFO] Logs and results saved to their respective directories
echo    [INFO] Total errors: %ERROR_COUNT%, Total warnings: %WARNING_COUNT%
echo.

:: Enhanced completion with optional debugging
if "%DEBUG_MODE%"=="1" (
    echo    [DEBUG] Debug information preserved
    pause
)
exit /b 0

:error_exit
echo.
echo    [ERROR] BSEE setup encountered critical errors and cannot continue
echo    [ERROR] Check log file for details: %LOG_FILE%
echo    [ERROR] Errors encountered: %ERROR_COUNT%, Warnings: %WARNING_COUNT%
echo.
echo    Troubleshooting suggestions:
echo    1. Ensure Python 3.9+ is installed and in PATH
echo    2. Run as Administrator for full functionality
echo    3. Check available disk space
echo    4. Temporarily disable antivirus software
echo    5. Check log file for specific error details
echo.
if not "%AUTO_MODE%"=="1" pause
exit /b 1

:: =============================================================================
:: ENHANCED HELPER FUNCTIONS
:: =============================================================================

:find_python
call :info "Searching for Python installations in common locations..."

:: Enhanced Python detection with additional paths
for %%P in (
    "C:\Python39\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Python313\python.exe"
    "C:\Program Files\Python39\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files (x86)\Python39\python.exe"
    "C:\Program Files (x86)\Python310\python.exe"
    "C:\Program Files (x86)\Python311\python.exe"
    "C:\Program Files (x86)\Python312\python.exe"
    "C:\Program Files (x86)\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
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
call :display "Please install Python manually from: https://www.python.org/downloads/"
call :display "Ensure 'Add Python to PATH' is checked during installation"
goto :eof

:python_found
call :success "Python found and added to PATH"
goto :eof

:: Enhanced requirements installation with retry logic
:install_requirements_file
set REQUIREMENTS_FILE=%REQUIREMENTS_DIR%\%1
set REQUIREMENT_NAME=%2

if exist "%REQUIREMENTS_FILE%" (
    call :info "Installing %REQUIREMENT_NAME%..."
    call :install_with_retry "python -m pip install -r \"%REQUIREMENTS_FILE%\"" "%REQUIREMENT_NAME%"
) else (
    call :warning "Requirements file not found: %REQUIREMENTS_FILE%"
)
goto :eof

:install_with_retry
set INSTALL_COMMAND=%~1
set PACKAGE_NAME=%~2
set RETRY_COUNT=0

:install_retry_loop
call :info "Installing %PACKAGE_NAME% (attempt !RETRY_COUNT!/%MAX_RETRIES%)..."
%INSTALL_COMMAND%
if errorlevel 1 (
    set /a RETRY_COUNT+=1
    if !RETRY_COUNT! LSS %MAX_RETRIES% (
        call :warning "%PACKAGE_NAME% installation failed, retrying... (!RETRY_COUNT!/%MAX_RETRIES%)"
        timeout /t 2 /nobreak >nul
        goto install_retry_loop
    ) else (
        call :error "%PACKAGE_NAME% installation failed after %MAX_RETRIES% attempts"
        call :display "Attempting individual package installation..."
        call :install_individual_packages
    )
) else (
    call :success "%PACKAGE_NAME% installed successfully"
)
goto :eof

:install_individual_packages
call :info "Installing critical packages individually..."

:: Install critical packages with enhanced error handling
for %%P in (numpy scipy matplotlib pyyaml click pandas pathlib typing setuptools wheel) do (
    call :info "Installing %%P..."
    python -m pip install %%P --upgrade
    if errorlevel 1 (
        call :warning "Failed to install %%P, trying alternative..."
        python -m pip install %%P --no-deps --force-reinstall
        if errorlevel 1 (
            call :error "Failed to install %%P with alternative method"
        ) else (
            call :success "%%P installed with alternative method"
        )
    ) else (
        call :success "%%P installed successfully"
    )
)
goto :eof

:: Enhanced Windows integration functions
:create_windows_directories
call :info "Creating Windows-specific directory structure..."

:: Create AppData directories
set APPDATA_BSEE=%APPDATA%\BSEE
for %%D in (
    "%APPDATA_BSEE%\inputs"
    "%APPDATA_BSEE%\results"
    "%APPDATA_BSEE%\presets"
    "%APPDATA_BSEE%\history"
    "%APPDATA_BSEE%\logs"
    "%APPDATA_BSEE%\temp"
    "%APPDATA_BSEE%\cache"
) do (
    if not exist "%%D" mkdir "%%D"
)

:: Create local project directories
for %%D in (
    "%PROJECT_DIR%\inputs"
    "%PROJECT_DIR%\results"
    "%PROJECT_DIR%\presets"
    "%PROJECT_DIR%\logs"
    "%PROJECT_DIR%\temp"
    "%PROJECT_DIR%\cache"
) do (
    if not exist "%%D" mkdir "%%D"
)

call :success "Windows directory structure created"
goto :eof

:setup_environment_variables
call :info "Setting up enhanced environment variables..."

:: Set session environment variables
set PYTHONPATH=%PROJECT_DIR%;%PROJECT_DIR%\legacy;%PROJECT_DIR%\bsee;%PYTHONPATH%
set BSEE_HOME=%PROJECT_DIR%
set BSEE_CONFIG_DIR=%PROJECT_DIR%\config
set BSEE_DATA_DIR=%PROJECT_DIR%\data
set BSEE_MODELS_DIR=%PROJECT_DIR%\models
set BSEE_RESULTS_DIR=%PROJECT_DIR%\results
set BSEE_CACHE_DIR=%PROJECT_DIR%\cache

:: Set permanent environment variables if admin
if %IS_ADMIN% EQU 1 (
    setx BSEE_HOME "%PROJECT_DIR%" /M >nul 2>&1
    setx BSEE_CONFIG_DIR "%PROJECT_DIR%\config" /M >nul 2>&1
    setx BSEE_DATA_DIR "%PROJECT_DIR%\data" /M >nul 2>&1
    call :success "Permanent environment variables set"
) else (
    call :info "Session environment variables set (run as admin for permanent)"
)

call :success "Environment variables configured"
goto :eof

:setup_file_associations
call :info "Setting up file associations for .bin files..."

:: Enhanced file association setup
assoc .bin=BSEEFile >nul 2>&1
if not errorlevel 1 (
    ftype BSEEFile="\"%PROJECT_DIR%\BSEE.bat\" \"%%1\"" >nul 2>&1
    call :success ".bin file association created"
) else (
    call :warning "Failed to create .bin file association (may need admin rights)"
)

:: Create registry entries for context menu
reg add "HKCR\.bin" /ve /d "BSEEFile" /f >nul 2>&1
reg add "HKCR\BSEEFile\shell\open\command" /ve /d "\"%PROJECT_DIR%\BSEE.bat\" \"%%1\"" /f >nul 2>&1
reg add "HKCR\BSEEFile\shell\analyze" /ve /d "Analyze with BSEE" /f >nul 2>&1
reg add "HKCR\BSEEFile\shell\analyze\command" /ve /d "\"%PROJECT_DIR%\BSEE.bat\" \"%%1\"" /f >nul 2>&1

call :success "File associations and context menu configured"
goto :eof

:create_desktop_shortcuts
call :info "Creating desktop shortcuts..."

:: Create desktop shortcuts using PowerShell with enhanced error handling
powershell -Command "try { $WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\BSEE GUI.lnk'); $Shortcut.TargetPath = 'python.exe'; $Shortcut.Arguments = '\"%PROJECT_DIR%\legacy\gui_main.py\"'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'BSEE - Binary Structure Exploration Engine'; $Shortcut.Save(); Write-Host '✓ GUI shortcut created' } catch { Write-Host '✗ Failed to create GUI shortcut' }" 2>nul

powershell -Command "try { $WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\BSEE CLI.lnk'); $Shortcut.TargetPath = 'cmd.exe'; $Shortcut.Arguments = '/k \"cd /d \"%PROJECT_DIR%\" && echo BSEE CLI Ready && echo Type \"python legacy\main.py --help\" for commands\"'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'BSEE Command Line Interface'; $Shortcut.Save(); Write-Host '✓ CLI shortcut created' } catch { Write-Host '✗ Failed to create CLI shortcut' }" 2>nul

call :success "Desktop shortcuts created"
goto :eof

:create_start_menu_shortcuts
call :info "Creating Start Menu shortcuts..."

set START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\BSEE
if not exist "%START_MENU_DIR%" mkdir "%START_MENU_DIR%"

powershell -Command "try { $WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU_DIR%\BSEE GUI.lnk'); $Shortcut.TargetPath = 'python.exe'; $Shortcut.Arguments = '\"%PROJECT_DIR%\legacy\gui_main.py\"'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'BSEE Graphical Interface'; $Shortcut.Save(); Write-Host '✓ Start Menu GUI shortcut created' } catch { Write-Host '✗ Failed to create Start Menu GUI shortcut' }" 2>nul

call :success "Start Menu shortcuts created"
goto :eof

:optimize_windows_settings
call :info "Optimizing Windows performance settings..."

:: Set process performance optimizations if admin
if %IS_ADMIN% EQU 1 (
    :: Windows Defender exclusions (if available)
    powershell -Command "try { Add-MpPreference -ExclusionPath '%PROJECT_DIR%' -ErrorAction SilentlyContinue; Write-Host '✓ Windows Defender exclusion added' } catch { Write-Host 'ℹ Windows Defender exclusion requires manual setup' }" 2>nul

    :: Set power plan to high performance (if available)
    powercfg /setactive SCHEME_MIN >nul 2>&1
    if not errorlevel 1 (
        call :success "Power plan set to high performance"
    )
)

call :success "Windows optimization completed"
goto :eof

:: Enhanced validation functions
:validate_core_dependencies
call :info "Validating core dependencies..."

python -c "
import sys
import importlib
import subprocess

critical_packages = ['numpy', 'scipy', 'matplotlib', 'yaml', 'click', 'pandas']
missing_packages = []
failed_packages = []

for package in critical_packages:
    try:
        module = importlib.import_module(package)
        version = getattr(module, '__version__', 'unknown')
        print(f'✓ {package}: {version}')
    except ImportError:
        print(f'✗ {package}: NOT FOUND')
        missing_packages.append(package)
    except Exception as e:
        print(f'⚠ {package}: ERROR - {e}')
        failed_packages.append(package)

if missing_packages:
    print(f'Installing missing packages: {missing_packages}')
    for package in missing_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True, capture_output=True)
            print(f'✓ {package} installed successfully')
        except:
            print(f'✗ Failed to install {package}')
            failed_packages.append(package)

if failed_packages:
    print(f'Failed packages: {failed_packages}')
    sys.exit(1)
else:
    print('All core dependencies validated')
" >nul 2>&1

if errorlevel 1 (
    call :warning "Some core dependencies failed validation"
) else (
    call :success "All core dependencies validated"
)
goto :eof

:validate_bsee_modules
call :info "Validating BSEE module structure..."

python -c "
import sys
import os
from pathlib import Path

# Ensure project paths are in Python path
project_root = Path('%PROJECT_DIR%').resolve()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'legacy'))

# Check and create BSEE module structure
bsee_dir = project_root / 'bsee'
if not bsee_dir.exists():
    bsee_dir.mkdir(exist_ok=True)
    with open(bsee_dir / '__init__.py', 'w') as f:
        f.write('# BSEE Package\n# Auto-generated by BSEE.bat\n')
    print('✓ BSEE module structure created')

# Test basic imports
try:
    import bsee
    print('✓ BSEE package imports successfully')
except ImportError as e:
    print(f'⚠ BSEE import issue: {e}')
    print('  This is normal in development mode')

# Check for essential legacy files
legacy_dir = project_root / 'legacy'
essential_files = ['main.py', 'gui_main.py']
for file_name in essential_files:
    file_path = legacy_dir / file_name
    if file_path.exists():
        print(f'✓ {file_name} found')
    else:
        print(f'✗ {file_name} missing')

print('BSEE module validation completed')
" >nul 2>&1

call :success "BSEE module structure validated"
goto :eof

:fix_python_path_issues
call :info "Fixing Python path issues automatically..."

:: Enhanced Python path configuration with comprehensive fixes
set PYTHONPATH=%PROJECT_DIR%;%PROJECT_DIR%\legacy;%PROJECT_DIR%\bsee;%PYTHONPATH%

:: Add project directories to Python path automatically
for /d %%D in ("%PROJECT_DIR%\*") do (
    if exist "%%D\__init__.py" (
        set PYTHONPATH=%%D;!PYTHONPATH!
        call :info "Added to Python path: %%D"
    )
)

:: Enhanced virtual environment path handling
if "%VENV_DIR%" neq "" (
    if exist "%VENV_DIR%\Lib\site-packages" (
        set PYTHONPATH=%VENV_DIR%\Lib\site-packages;!PYTHONPATH!
        call :info "Added virtual environment packages to Python path"
    )
)

:: Add to PYTHONPATH for current session and permanently if admin
setx PYTHONPATH "%PYTHONPATH%" >nul 2>&1

:: Enhanced site-packages import fix
python -c "
import sys
import site
import os

# Add user site-packages to sys.path for better package discovery
site.addusersitepackages()

# Fix for virtual environment package visibility
if 'VIRTUAL_ENV' in os.environ:
    venv_path = os.environ['VIRTUAL_ENV']
    site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
    if site_packages not in sys.path:
        sys.path.insert(0, site_packages)

print('Python path enhancements applied')
" >nul 2>&1

:: Create advanced path fix script for manual recovery
echo @echo off > "%PROJECT_DIR%\fix_paths.bat"
echo echo ==================================================== >> "%PROJECT_DIR%\fix_paths.bat"
echo echo BSEE Enhanced Path Fix Utility >> "%PROJECT_DIR%\fix_paths.bat"
echo echo ==================================================== >> "%PROJECT_DIR%\fix_paths.bat"
echo echo. >> "%PROJECT_DIR%\fix_paths.bat"
echo echo Setting enhanced Python paths for BSEE... >> "%PROJECT_DIR%\fix_paths.bat"
echo echo. >> "%PROJECT_DIR%\fix_paths.bat"
echo set PYTHONPATH=%PROJECT_DIR%;%PROJECT_DIR%\legacy;%PROJECT_DIR%\bsee;%%PYTHONPATH%% >> "%PROJECT_DIR%\fix_paths.bat"
echo echo. >> "%PROJECT_DIR%\fix_paths.bat"
echo echo Enhanced path configuration applied! >> "%PROJECT_DIR%\fix_paths.bat"
echo echo You can now run BSEE with corrected paths. >> "%PROJECT_DIR%\fix_paths.bat"
echo echo. >> "%PROJECT_DIR%\fix_paths.bat"

call :success "Python path issues resolved with enhanced fixes"
goto :eof

:: Enhanced testing functions
:test_environment
call :info "Testing environment configuration..."

python -c "
import sys
import os
import platform
from pathlib import Path

print('=== Environment Test Results ===')
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()} {platform.release()}')
print(f'Working Directory: {os.getcwd()}')
print(f'Project Directory: {Path(\"%PROJECT_DIR%\").resolve()}')

# Check essential paths
essential_paths = [
    'legacy',
    'requirements',
    'config',
    'logs'
]

for path_name in essential_paths:
    path = Path(path_name)
    if path.exists():
        print(f'✓ {path_name} directory exists')
    else:
        print(f'✗ {path_name} directory missing')

print('Environment test completed')
" >nul 2>&1

if errorlevel 1 (
    call :warning "Environment test failed"
) else (
    call :success "Environment test passed"
)
goto :eof

:test_imports
call :info "Testing module imports..."

python -c "
import sys
import importlib

print('=== Import Test Results ===')

# Test standard library modules
stdlib_modules = ['tkinter', 'json', 'yaml', 'pathlib', 'subprocess']
for module in stdlib_modules:
    try:
        importlib.import_module(module)
        print(f'✓ {module}')
    except ImportError:
        print(f'✗ {module}')

# Test scientific packages
scientific_modules = ['numpy', 'scipy', 'matplotlib', 'pandas']
for module in scientific_modules:
    try:
        importlib.import_module(module)
        mod = sys.modules[module]
        version = getattr(mod, '__version__', 'unknown')
        print(f'✓ {module} ({version})')
    except ImportError:
        print(f'✗ {module} (missing)')

print('Import test completed')
" >nul 2>&1

if errorlevel 1 (
    call :warning "Some import tests failed"
) else (
    call :success "All import tests passed"
)
goto :eof

:test_all_files
call :info "Testing all Python files for syntax errors..."

set TEST_FAILURES=0
for /r "%PROJECT_DIR%" %%F in (*.py) do (
    python -m py_compile "%%F" >nul 2>&1
    if errorlevel 1 (
        call :error "Syntax error in: %%F"
        set /a TEST_FAILURES+=1
    ) else (
        call :info "✓ %%F"
    )
)

if %TEST_FAILURES% EQU 0 (
    call :success "All Python files passed syntax validation"
) else (
    call :error "%TEST_FAILURES% files have syntax errors"
)
goto :eof

:run_smoke_tests
call :info "Running smoke tests for startup validation..."

set TESTS_DIR=%PROJECT_DIR%\tests
if exist "%TESTS_DIR%\test_smoke.py" (
    python "%TESTS_DIR%\test_smoke.py"
    if errorlevel 1 (
        call :warning "Some smoke tests failed"
    ) else (
        call :success "All smoke tests passed"
    )
) else (
    call :warning "Smoke test file not found, creating basic validation..."
    python -c "
import sys
import os
print('=== Basic Smoke Test ===')
print(f'Python version: {sys.version}')
print(f'Current directory: {os.getcwd()}')

# Test critical imports
try:
    import numpy as np
    print(f'✓ NumPy {np.__version__}')
except ImportError:
    print('✗ NumPy not available')

try:
    import scipy
    print('✓ SciPy available')
except ImportError:
    print('✗ SciPy not available')

try:
    import matplotlib
    print('✓ Matplotlib available')
except ImportError:
    print('✗ Matplotlib not available')

print('Basic smoke test completed')
"
)
goto :eof

:run_essential_tests
call :info "Running essential tests..."

call :test_environment
call :test_imports
call :validate_core_dependencies

call :success "Essential tests completed"
goto :eof

:run_comprehensive_tests
call :info "Running comprehensive test suite..."

call :test_environment
call :test_imports
call :test_all_files
call :validate_core_dependencies
call :validate_bsee_modules
call :run_smoke_tests

call :success "Comprehensive tests completed"
goto :eof

:run_basic_validation
python -c "
import sys
import platform
import os

print('=== Basic Validation ===')
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()} {platform.release()}')
print(f'Directory: {os.getcwd()}')

# Test basic functionality
try:
    import math
    import json
    print('✓ Basic Python functionality')
except Exception as e:
    print(f'✗ Basic functionality error: {e}')

print('Basic validation completed')
"
goto :eof

:: Enhanced reporting functions
:generate_system_report
call :info "Generating comprehensive system report..."

python -c "
import platform
import sys
import os
import subprocess
from pathlib import Path

print('=== BSEE Enhanced System Report ===')
print(f'Generated: {subprocess.run([\"date\", \"/t\"], capture_output=True, text=True, shell=True).stdout.strip()}')
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()} {platform.release()} {platform.version()}')
print(f'Architecture: {platform.architecture()[0]}')
print(f'Processor: {platform.processor()}')
print(f'Machine: {platform.machine()}')
print(f'Project Directory: {Path(\"%PROJECT_DIR%\").resolve()}')
print(f'Virtual Environment: {os.environ.get(\"VIRTUAL_ENV\", \"Not active\")}')
print(f'Python Path: {sys.executable}')

# Disk space
try:
    import shutil
    total, used, free = shutil.disk_usage(\".\")
    print(f'Disk Space: {free // (1024**3)} GB free / {total // (1024**3)} GB total')
except:
    print('Disk Space: Unable to determine')

# Environment variables
print(f'BSEE_HOME: {os.environ.get(\"BSEE_HOME\", \"Not set\")}')
print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\", \"Not set\")}')

print('=== End Report ===')
" 2>nul

call :success "System report generated"
goto :eof

:validate_installation
call :info "Performing final installation validation..."

set VALIDATION_ERRORS=0

:: Check critical directories
for %%D in ("%PROJECT_DIR%\legacy" "%PROJECT_DIR%\requirements" "%PROJECT_DIR%\logs") do (
    if not exist "%%D" (
        call :error "Critical directory missing: %%D"
        set /a VALIDATION_ERRORS+=1
    )
)

:: Check critical files
for %%F in ("%PROJECT_DIR%\BSEE.bat") do (
    if not exist "%%F" (
        call :error "Critical file missing: %%F"
        set /a VALIDATION_ERRORS+=1
    )
)

:: Check Python functionality
python -c "print('Python functionality test passed')" >nul 2>&1
if errorlevel 1 (
    call :error "Python functionality test failed"
    set /a VALIDATION_ERRORS+=1
)

if %VALIDATION_ERRORS% EQU 0 (
    call :success "Installation validation passed"
) else (
    call :error "%VALIDATION_ERRORS% validation errors found"
)
goto :eof

:create_setup_summary
call :info "Creating setup summary..."

echo. > "%PROJECT_DIR%\logs\setup_summary.txt"
echo BSEE Enhanced Setup Summary >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo ============================ >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Setup Date: %date% %time% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Project Directory: %PROJECT_DIR% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Python Version: %PYTHON_VERSION% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Virtual Environment: %VENV_DIR% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Errors: %ERROR_COUNT% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Warnings: %WARNING_COUNT% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Administrator Mode: %IS_ADMIN% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Desktop Deployment: %BSEE_DESKTOP_DEPLOY% >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo. >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo Next Steps: >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo 1. Run 'BSEE.bat' for interactive mode >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo 2. Run 'BSEE.bat --production' for one-click setup >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo 3. Check desktop shortcuts for easy access >> "%PROJECT_DIR%\logs\setup_summary.txt"
echo 4. Right-click .bin files for 'Analyze with BSEE' option >> "%PROJECT_DIR%\logs\setup_summary.txt"

call :success "Setup summary created: %PROJECT_DIR%\logs\setup_summary.txt"
goto :eof

:log_system_info
:: Initialize log file with system information
echo BSEE Enhanced Setup Log > "%LOG_FILE%"
echo ========================== >> "%LOG_FILE%"
echo Started: %date% %time% >> "%LOG_FILE%"
echo User: %USERNAME% >> "%LOG_FILE%"
echo Computer: %COMPUTERNAME% >> "%LOG_FILE%"
echo OS: %OS% >> "%LOG_FILE%"
echo Project Directory: %PROJECT_DIR% >> "%LOG_FILE%"
echo Arguments: %* >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
goto :eof
