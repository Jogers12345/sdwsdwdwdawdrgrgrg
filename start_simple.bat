@echo off
cd /d "%~dp0"
echo.
echo ======== Starting BSEE ========

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

:: Create virtual environment if missing
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call "venv\Scripts\activate.bat"

echo.
echo Checking dependencies...
python -m pip install --upgrade pip
python -m pip install numpy scipy pyyaml matplotlib pillow psutil click tqdm lz4 zstandard

echo.
echo ======== Launching BSEE ========

if "%~1"=="" (
    python main.py
) else (
    python main.py %*
)

echo.
pause
