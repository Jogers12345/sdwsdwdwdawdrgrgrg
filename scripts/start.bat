@echo off
title BSEE Launcher
color 0A
setlocal enabledelayedexpansion

:: ===============================================
:: Enhanced BSEE Windows Launcher
:: Comprehensive installation and execution script
:: ===============================================

:: Configuration
set PROJECT_NAME=BSEE
set PROJECT_DIR=%~dp0..
set VENV_DIR=%PROJECT_DIR%\venv
set MIN_PYTHON_VERSION=3.9
set LOG_FILE=%PROJECT_DIR%\logs\install.log

:: Create logs directory if it doesn't exist
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

:: Function to display colored output
:display
echo %~1
goto :eof

:: Function to display error
:error
echo [ERROR] %~1
echo [ERROR] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display success
:success
echo [SUCCESS] %~1
echo [INFO] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display info
:info
echo [INFO] %~1
echo [INFO] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: Function to display warning
:warning
echo [WARNING] %~1
echo [WARNING] %~1 >> "%LOG_FILE%" 2>&1
goto :eof

:: ===============================================
:: STEP 1: Python Detection and Installation
:: ===============================================
call :display "========================================"
call :display "BSEE Enhanced Launcher v2.0"
call :display "========================================"
call :display ""

:: Check if Python is installed
call :info "Checking Python installation..."
python --version >nul 2>&1
if errorlevel 1 (
    call :error "Python is not installed or not in PATH"
    call :display ""
    call :display "Would you like to download and install Python?"
    call :display "1. Yes (recommended)"
    call :display "2. No (I'll install manually)"
    call :display "3. Try to find existing Python installation"
    call :display ""
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
call :info "Checking Python version..."
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
call :info "Found Python version: %PYTHON_VERSION%"

:: Extract major.minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

:: Check if version meets minimum requirements
if %PYTHON_MAJOR% gtr 3 goto :python_version_ok
if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% geq 9 goto :python_version_ok

call :error "Python %MIN_PYTHON_VERSION%+ is required. Found version %PYTHON_VERSION%"
call :display "Please upgrade Python and try again."
pause
exit /b 1

:python_version_ok
call :success "Python version check passed"

:: ===============================================
:: STEP 2: Virtual Environment Setup
:: ===============================================
call :display ""
call :info "Setting up virtual environment..."

if not exist "%VENV_DIR%" (
    call :info "Creating virtual environment in %VENV_DIR%..."
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        call :error "Failed to create virtual environment"
        pause
        exit /b 1
    )
    call :success "Virtual environment created"
) else (
    call :info "Virtual environment already exists"
)

:: Activate virtual environment
call :info "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    call :error "Failed to activate virtual environment"
    pause
    exit /b 1
)
call :success "Virtual environment activated"

:: Upgrade pip
call :info "Upgrading pip..."
python -m pip install --upgrade pip
if errorlevel 1 (
    call :warning "Failed to upgrade pip, continuing with current version"
) else (
    call :success "Pip upgraded successfully"
)

:: ===============================================
:: STEP 3: Comprehensive Dependency Installation
:: ===============================================
call :display ""
call :info "Installing dependencies..."

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

:: ===============================================
:: STEP 4: Testing Suite Integration
:: ===============================================
call :display ""
call :info "Testing suite integration..."

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

:: ===============================================
:: STEP 5: Launch Mode Selection
:: ===============================================
call :display ""
call :display "========================================"
call :display "Select Launch Mode:"
call :display "========================================"
call :display "1. GUI Mode (default)"
call :display "2. CLI Mode"
call :display "3. Test Mode"
call :display "4. Development Mode"
call :display "5. Preset Mode"
call :display "6. Configuration Check"
call :display "7. Exit"
call :display ""

set /p mode_choice="Select mode (1-7): "

if "%mode_choice%"=="1" (
    call :launch_gui
) else if "%mode_choice%"=="2" (
    call :launch_cli
) else if "%mode_choice%"=="3" (
    call :launch_test
) else if "%mode_choice%"=="4" (
    call :launch_development
) else if "%mode_choice%"=="5" (
    call :launch_preset
) else if "%mode_choice%"=="6" (
    call :check_configuration
) else if "%mode_choice%"=="7" (
    call :display "Goodbye!"
    exit /b 0
) else (
    call :warning "Invalid choice, launching GUI mode"
    call :launch_gui
)

:: ===============================================
:: Launch Functions
:: ===============================================

:launch_gui
call :info "Launching BSEE in GUI mode..."
set GUI_SCRIPT=%PROJECT_DIR%\legacy\gui_main.py
if exist "%GUI_SCRIPT%" (
    python "%GUI_SCRIPT%" %*
) else (
    call :error "GUI script not found: %GUI_SCRIPT%"
    call :info "Trying alternative path..."
    set ALT_GUI_SCRIPT=%PROJECT_DIR%\src\gui_main.py
    if exist "%ALT_GUI_SCRIPT%" (
        python "%ALT_GUI_SCRIPT%" %*
    ) else (
        call :error "GUI script not found in either location"
        pause
        exit /b 1
    )
)
goto :eof

:launch_cli
call :info "Launching BSEE in CLI mode..."
set CLI_SCRIPT=%PROJECT_DIR%\legacy\main.py
if exist "%CLI_SCRIPT%" (
    python "%CLI_SCRIPT%" %*
) else (
    call :error "CLI script not found: %CLI_SCRIPT%"
    pause
    exit /b 1
)
goto :eof

:launch_test
call :info "Launching BSEE in test mode..."
if exist "%TESTS_DIR%\run_tests.py" (
    python "%TESTS_DIR%\run_tests.py" %*
) else (
    call :error "Test runner not found"
    pause
    exit /b 1
)
goto :eof

:launch_development
call :info "Launching BSEE in development mode..."
set DEVELOPMENT_SCRIPT=%PROJECT_DIR%\legacy\main.py
if exist "%DEVELOPMENT_SCRIPT%" (
    python "%DEVELOPMENT_SCRIPT%" --preset development --debug %*
) else (
    call :error "Development script not found"
    pause
    exit /b 1
)
goto :eof

:launch_preset
call :info "Available presets:"
call :display ""
if exist "%PROJECT_DIR%\config\presets\" (
    dir "%PROJECT_DIR%\config\presets\" /b *.yaml
    call :display ""
    set /p preset_name="Enter preset name: "
    call :info "Launching BSEE with preset: !preset_name!"
    set PRESET_SCRIPT=%PROJECT_DIR%\legacy\main.py
    if exist "%PRESET_SCRIPT%" (
        python "%PRESET_SCRIPT%" --preset "!preset_name!" %*
    ) else (
        call :error "Main script not found"
        pause
        exit /b 1
    )
) else (
    call :error "No presets directory found"
    pause
    exit /b 1
)
goto :eof

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
:: Helper Functions
:: ===============================================

:find_python
call :info "Searching for Python installations in common locations..."

:: Check common Python installation paths
set PYTHON_PATHS[
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
]

for %%P in (%PYTHON_PATHS%) do (
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
:: Error Recovery
:: ===============================================
:error_recovery
call :error "An error occurred during execution"
call :display ""
call :display "Error recovery options:"
call :display "1. Retry the last operation"
call :display "2. Continue with default settings"
call :display "3. Exit"
call :display ""
set /p recovery_choice="Select option (1-3): "

if "!recovery_choice!"=="1" (
    call :info "Retrying..."
    goto :eof
) else if "!recovery_choice!"=="2" (
    call :info "Continuing with default settings..."
    goto :eof
) else (
    call :info "Exiting..."
    exit /b 1
)

:: ===============================================
:: End of Script
:: ===============================================

call :success "BSEE launcher completed successfully"
pause