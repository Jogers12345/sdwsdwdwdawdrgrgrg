# BSEE GUI - Binary Structure Exploration Engine (Windows GUI)

## Overview

BSEE GUI is a professional Windows application that transforms the command-line BSEE tool into an interactive graphical interface with real-time visualization, bit-level operation tracking, and comprehensive performance monitoring.

## Features

### 🖥️ Professional Windows Interface
- **Modern GUI Design**: Native Windows styling with intuitive layout
- **Real-time Visualization**: See binary data and operation effects as they happen
- **Interactive Panels**: File selection, visualization, metrics, and terminal output
- **Windows Integration**: File associations, desktop shortcuts, and Start Menu integration

### 🔍 Bit-Level Analysis
- **Binary Visualization**: Hex, binary, decimal, and ASCII display modes
- **Operation Tracking**: See exactly which bits are changed by each operation
- **Change Highlighting**: Visual indicators for modified bytes
- **Scrollable Display**: Navigate through large binary files efficiently

### 📊 Real-time Metrics
- **Live Score Updates**: Watch optimization scores change in real-time
- **Metric Trends**: Interactive charts showing metric progression
- **Performance Monitoring**: CPU and memory usage tracking
- **Progress Indicators**: Visual feedback for analysis progress

### ⚙️ Advanced Configuration
- **Strategy Selection**: Choose from 6 different optimization strategies
- **Preset Management**: Save and load analysis configurations
- **Parameter Controls**: Fine-tune analysis limits and constraints
- **Recent Files**: Quick access to previously analyzed files

### 📝 Professional Output
- **Terminal Logging**: Real-time operation logging with search and filtering
- **Results Export**: Comprehensive analysis reports in multiple formats
- **Timeline Tracking**: Complete operation history with timing data
- **Performance Analytics**: Detailed complexity and performance analysis

## Installation

### Requirements
- Windows 10 or later
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 100MB disk space

### Quick Install
1. Extract BSEE to a folder (e.g., `C:\BSEE\`)
2. Run `start.bat` - it will automatically:
   - Check Python installation
   - Create virtual environment
   - Install all dependencies
   - Launch the application

### Manual Install
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run GUI
python gui_main.py
```

## Usage

### Starting the Application

#### Method 1: Using start.bat (Recommended)
1. Double-click `start.bat`
2. Choose option 1 for GUI mode
3. Follow the on-screen prompts

#### Method 2: Direct GUI Launch
```bash
python gui_main.py
```

#### Method 3: Using File Association
1. Right-click any `.bin` file
2. Select "Analyze with BSEE"

### Basic Workflow

1. **Select Input File**
   - Click "Browse..." to select a binary file
   - Choose from recent files dropdown
   - Or drag and drop files onto the interface

2. **Configure Analysis**
   - Choose optimization strategy (Greedy, Beam, Annealing, etc.)
   - Set analysis limits (max operations, max cost)
   - Select metrics to optimize
   - Choose output directory

3. **Start Analysis**
   - Click "Start Analysis"
   - Watch real-time visualization
   - Monitor metrics and progress
   - Review terminal output

4. **Review Results**
   - Check final scores and metrics
   - Browse exported reports
   - Analyze operation timeline
   - View performance statistics

### Advanced Features

#### Presets
- Save commonly used configurations
- Quick access to analysis templates
- Share presets between team members

#### Visualization Modes
- **Hex**: Traditional hexadecimal display
- **Binary**: Individual bit representation
- **Decimal**: Numeric values
- **ASCII**: Text representation

#### Performance Monitoring
- Operations per second
- Memory usage tracking
- Time complexity analysis
- Bottleneck identification

## Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Menu: File | Edit | View | Tools | Help                      │
├─────────────────────────────────────────────────────────────┤
│ File Panel        │ Visualization Panel    │ Metrics Panel     │
│ [Browse...]       │ Current Operation:     │ Score: 0.241      │
│ Strategy: [Greedy]│ Bit-level Display      │ File Ideality: ↑  │
│ Max Ops: [1000]   │ Before: 1011...       │ Entropy: ↓        │
│ [Start] [Stop]    │ After:  1101...       │ Time: 00:02:34    │
├─────────────────────────────────────────────────────────────┤
│ Terminal Output Panel                                          │
│ > Processing operation 47/1000...                            │
│ [15:32:04] XOR_Rotate_Right applied at indices 5-7           │
├─────────────────────────────────────────────────────────────┤
│ Status: Running | Ops: 47/1000 | Score: 0.241 | Memory: 245MB │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
C:\BSEE\
├── gui_main.py              # GUI entry point
├── main.py                  # CLI entry point
├── start.bat                # Windows launcher
├── setup_windows.py         # Windows setup script
├── requirements.txt         # Python dependencies
├── gui\                     # GUI package
│   ├── main_window.py       # Main application window
│   ├── app_controller.py    # Application controller
│   └── panels\              # GUI panels
│       ├── file_panel.py    # File selection & configuration
│       ├── visualization_panel.py  # Binary visualization
│       ├── metrics_panel.py # Metrics display
│       └── terminal_panel.py # Terminal output
├── bsee\                    # Core BSEE engine
├── config\                  # Configuration files
├── inputs\                  # Default input folder
├── results\                 # Analysis results
├── presets\                 # Saved configurations
├── logs\                    # Application logs
└── tests\                   # Test suite
```

## Configuration

### Strategies
- **Greedy**: Always selects the best available operation
- **Beam**: Maintains multiple candidate solutions
- **Annealing**: Uses simulated annealing for exploration
- **MCTS**: Monte Carlo Tree Search for decision making
- **Genetic**: Evolutionary algorithm approach
- **Heuristic**: Rule-based operation selection

### Metrics
- **File Ideality Score**: Primary optimization metric
- **Entropy**: Information theory metrics
- **Compression**: Compressibility metrics
- **Statistical**: Statistical analysis metrics
- **Complexity**: Algorithmic complexity metrics

### Performance Tuning
- Adjust `max_operations` for thoroughness vs. speed
- Modify `max_cost` for resource constraints
- Choose specific metrics for focused optimization
- Use operation limits for targeted analysis

## Troubleshooting

### Common Issues

**GUI won't start**
- Ensure Python 3.8+ is installed
- Run `start.bat` to check dependencies
- Try running as administrator

**Analysis is slow**
- Reduce `max_operations`
- Use a less intensive strategy (e.g., Greedy)
- Close other applications to free memory

**Out of memory errors**
- Reduce analysis limits
- Use chunked processing for large files
- Close other memory-intensive applications

**File association not working**
- Run `setup_windows.py` as administrator
- Check file permissions
- Manually associate .bin files with BSEE

### Getting Help

1. Check terminal output for error messages
2. Review logs in the `logs` folder
3. Try the CLI version for comparison
4. Check the GitHub issues page
5. Contact support with error details

## Advanced Usage

### Command Line Integration
The GUI can also be launched with command line arguments:
```bash
python gui_main.py --file input.bin --strategy greedy --max-ops 1000
```

### Batch Processing
For multiple files, consider using the CLI version:
```bash
for file in *.bin; do
    python main.py "$file" --max-operations 500 --strategy greedy
done
```

### Custom Presets
Create custom presets by saving frequently used configurations:
1. Configure analysis parameters
2. Click "Save" in the Presets section
3. Enter a descriptive name
4. Load presets quickly for future analyses

## Development

### Running Tests
```bash
# GUI tests
python tests/gui_test_suite.py

# File handling tests
python tests/file_handling_tests.py
```

### Building for Distribution
1. Run `setup_windows.py` for full Windows integration
2. Create installer package (optional)
3. Test on clean Windows system
4. Document any system-specific requirements

## License

BSEE GUI is licensed under the same terms as the BSEE engine. See LICENSE file for details.

## Support

For support, please:
1. Check this README and documentation
2. Review the troubleshooting section
3. Check GitHub issues
4. Contact the development team with specific error details

---

**BSEE GUI** - Making binary analysis accessible and professional.