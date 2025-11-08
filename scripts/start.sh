#!/bin/bash

echo "========================================"
echo "BSEE - Binary Structure Exploration Engine"
echo "========================================"
echo

# Check if Python is installed
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.9+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "Found $PYTHON_VERSION"

# Check if virtual environment exists
echo "[2/5] Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "Virtual environment found"
fi

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Check and install required dependencies
echo "[4/5] Checking dependencies..."
echo "Checking required packages..."

PACKAGES="numpy scipy pyyaml"
for package in $PACKAGES; do
    if ! python -c "import $package" &> /dev/null; then
        echo "Installing $package..."
        pip install $package
        if [ $? -ne 0 ]; then
            echo "WARNING: Failed to install $package, continuing anyway..."
        else
            echo "$package installed successfully"
        fi
    else
        echo "$package is already installed"
    fi
done

# Check optional packages
echo "Checking optional packages..."
OPTIONAL_PACKAGES="lz4 zstandard"
for package in $OPTIONAL_PACKAGES; do
    if ! python -c "import $package" &> /dev/null; then
        echo "Installing optional package $package..."
        pip install $package
        if [ $? -ne 0 ]; then
            echo "WARNING: Failed to install $package (not critical)"
        else
            echo "Optional package $package installed successfully"
        fi
    else
        echo "Optional package $package is already installed"
    fi
done

# Display usage information
echo "[5/5] Ready to start BSEE"
echo
echo "Usage Examples:"
echo "  python main.py input_file.bin --strategy greedy --max-operations 100"
echo "  python main.py data.bin --policy policy_ideality.yaml --strategy annealing"
echo "  python main.py test.bin --help"
echo

# Check if user provided arguments
if [ $# -eq 0 ]; then
    echo "No arguments provided. BSEE will show help options."
    echo "You can also run: ./start.sh \"your arguments here\""
    echo
    echo "Example: ./start.sh \"test.bin --strategy greedy --max-operations 50\""
    echo

    # Run BSEE with help to show available options
    python main.py --help
else
    echo "Starting BSEE with arguments: $*"
    echo

    # Run BSEE with user-provided arguments
    python main.py "$@"

    if [ $? -ne 0 ]; then
        echo
        echo "BSEE encountered an error. Check the error message above."
        echo "Make sure the input file exists and arguments are correct."
    fi
fi

echo
echo "BSEE execution completed."
echo "Results are saved in the 'results' directory."
echo