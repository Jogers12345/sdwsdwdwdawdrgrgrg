# BSEE Interactive CLI Demo

## Enhanced start.bat Features

The `start.bat` script has been enhanced with comprehensive dependency management and an interactive CLI mode that guides users through the analysis process.

### Key Improvements:

#### 1. **Complete Dependency Management**
All required packages are automatically installed:
- `numpy` - Numerical computing
- `scipy` - Scientific computing
- `pyyaml` - YAML configuration files
- `matplotlib` - GUI visualization and charts
- `pillow` - Image processing
- `psutil` - System monitoring
- `click` - Command line interface
- `tqdm` - Progress bars
- `lz4` - Fast compression
- `zstandard` - Advanced compression

#### 2. **Interactive CLI Mode**

When users choose "CLI Mode" from the menu, they get:

**File Selection:**
- Lists all .bin files in the `inputs\` folder
- Option to create a test file if no files exist
- Ability to copy files from other locations to the inputs folder

**Strategy Selection:**
1. `greedy` - Always select best operation (fast)
2. `beam` - Keep top N candidates
3. `annealing` - Simulated annealing search
4. `mcts` - Monte Carlo Tree Search
5. `genetic` - Evolutionary algorithm
6. `heuristic` - Rule-based selection

**Configuration Parameters:**
- Max operations (default: 1000)
- Max cost (default: 10000)
- Metrics selection with presets:
  - Default: file_ideality_score, entropy_global, lz77_ratio
  - Entropy focus: entropy_global, shannon_entropy_global
  - Compression focus: lz77_ratio, compression_ratio
  - Custom: User-defined metrics
- Output directory (default: results)

**Smart Test File Generation:**
When no files exist, users can create a comprehensive test file containing:
- Repeated binary patterns for testing transformations
- Random data for entropy analysis
- Structured data (integers, sequences)
- ASCII text for text analysis
- High-entropy data for compression testing

**User Experience Features:**
- Clear prompts with default values
- Input validation with helpful error messages
- Configuration summary before execution
- Confirmation prompt to start analysis
- Automatic directory creation
- Progress reporting during analysis

### Example Session:

```
BSEE - Binary Structure Exploration Engine
=======================================

[1/5] Checking Python installation...
    Found Python 3.12.0
[2/5] Checking virtual environment...
    Virtual environment found
[3/5] Activating virtual environment...
[4/5] Checking dependencies...
    Checking required packages...
    numpy is already installed
    scipy is already installed
    pyyaml is already installed
    matplotlib is already installed
    pillow is already installed
    psutil is already installed
    click is already installed
    tqdm is already installed
    lz4 is already installed
    zstandard is already installed

[5/5] Ready to start BSEE

Launch Options:
   1. GUI Mode (Recommended)       - Launch graphical interface
   2. CLI Mode                    - Command line interface
   3. Help                        - Show command line options

Choose launch mode [1-3]: 2

CLI Interactive Mode
===================

Available files in inputs\ folder:
No .bin files found in inputs\ folder

Create a test file for demonstration? [Y/n]: y
Creating test binary file...
Created test.bin (1536 bytes)

Available files in inputs\ folder:
test.bin

Enter input filename (from inputs\ folder, e.g., test.bin): test.bin
Or enter full path to file (optional):
Using file: inputs\test.bin

Available strategies:
1. greedy     - Always select best operation (fast)
2. beam       - Keep top N candidates
3. annealing - Simulated annealing search
4. mcts       - Monte Carlo Tree Search
5. genetic    - Evolutionary algorithm
6. heuristic  - Rule-based selection

Choose strategy [1-6, default=1]: 1
Strategy: greedy

Enter max operations [default=1000]: 50
Max operations: 50

Enter max cost [default=10000]: 1000
Max cost: 1000

Metric presets:
1. Default - file_ideality_score, entropy_global, lz77_ratio
2. Entropy focus - entropy_global, shannon_entropy_global
3. Compression focus - lz77_ratio, compression_ratio
4. Custom - enter your own metrics

Choose metrics preset [1-4, default=1]: 1
Metrics: file_ideality_score,entropy_global,lz77_ratio

Enter output directory [default=results]: results
Output directory: results

Configuration Summary:
====================
Input File:     inputs\test.bin
Strategy:       greedy
Max Operations: 50
Max Cost:       1000
Metrics:        file_ideality_score,entropy_global,lz77_ratio
Output Dir:     results

Start analysis with these settings? [Y/n]: y

Starting BSEE analysis...
========================

2025-11-05 16:30:00 - INFO - Starting BSEE analysis of 'inputs\test.bin'
2025-11-05 16:30:00 - INFO - Using strategy: greedy
2025-11-05 16:30:00 - INFO - Loaded binary file: inputs\test.bin (1536 bytes)
2025-11-05 16:30:00 - INFO - Initial metrics: | file_ideality_score=0.8421 | entropy_global=3.2145 | lz77_ratio=1.6500
2025-11-05 16:30:01 - INFO - Iteration 10: Score=0.8675, Cost=45.2
2025-11-05 16:30:02 - INFO - Iteration 20: Score=0.8892, Cost=89.7
...
2025-11-05 16:30:15 - INFO - Analysis completed successfully!
2025-11-05 16:30:15 - INFO - Results saved to: results/run_20251105_163015
2025-11-05 16:30:15 - INFO - Final score: 0.9123
2025-11-05 16:30:15 - INFO - Total operations: 50

Analysis completed successfully!
Results are saved in the 'results' directory.
```

### Benefits:

1. **Zero Configuration**: Users don't need to know any command line arguments
2. **Guided Process**: Step-by-step prompts with clear explanations
3. **Smart Defaults**: Sensible defaults for all parameters
4. **Error Prevention**: Input validation and helpful error messages
5. **File Management**: Automatic creation of directories and test files
6. **Professional Output**: Clear progress reporting and result summaries
7. **Dependencies**: All required packages are automatically installed

This makes BSEE accessible to both technical and non-technical users while still maintaining the power and flexibility of the original CLI tool.