# BSEE - Binary Structure Exploration Engine - Complete Documentation

**Generated:** November 8, 2025
**Version:** 1.0
**Status:** Production-Ready with some limitations

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Structure](#architecture--structure)
3. [Core Components](#core-components)
4. [Operations System](#operations-system)
5. [Metrics System](#metrics-system)
6. [Search Strategies](#search-strategies)
7. [Engine & Pipeline](#engine--pipeline)
8. [GUI Components](#gui-components)
9. [Configuration System](#configuration-system)
10. [Broken Items & Issues](#broken-items--issues)
11. [Development Guidelines](#development-guidelines)
12. [Extension Guide](#extension-guide)
13. [API Reference](#api-reference)
14. [Troubleshooting](#troubleshooting)

---

## Project Overview

BSEE (Binary Structure Exploration Engine) is a sophisticated tool for analyzing and transforming binary data structures using multiple search algorithms and transformation operations.

### Key Features
- **Multi-Strategy Search**: MCTS, Genetic Algorithm, Beam Search, Simulated Annealing, Heuristic, Greedy
- **Rich Operations**: 101 operations across 6 categories (bitwise, reordering, delta, substitution, transform, custom)
- **Comprehensive Metrics**: 82+ metrics across 8 categories (entropy, compression, statistical, bitwise, etc.)
- **Modular Architecture**: Clean separation of concerns with extensible design
- **Error Handling**: Global error handler with recovery strategies
- **GUI Support**: Tkinter-based interface with fallback to terminal mode

### Success Rate
- **Operations**: 75/101 working (74.3%)
- **Metrics**: 42+ working (without numpy dependency)

---

## Architecture & Structure

```
bsee/
├── __init__.py                 # Package initialization
├── operations/                 # Operations system
│   ├── __init__.py
│   ├── operations_registry.py  # Central operations registry
│   ├── bitwise_ops.py         # Bitwise operations (20 ops)
│   ├── reordering_ops.py      # Reordering operations (15 ops)
│   ├── delta_ops.py           # Delta operations (10 ops)
│   ├── substitution_ops.py    # Substitution operations (20 ops)
│   ├── transform_ops.py       # Transform operations (20 ops)
│   ├── custom_ops.py          # Custom operations (15+ ops)
│   └── operation_validator.py # Operations testing framework
├── metrics/                    # Metrics system
│   ├── __init__.py
│   ├── metrics_registry.py    # Central metrics registry
│   ├── entropy_metrics.py     # Entropy-based metrics (12 metrics)
│   ├── compression_metrics.py # Compression metrics (15 metrics)
│   ├── statistical_metrics.py # Statistical metrics (12 metrics)
│   ├── bitwise_metrics.py     # Bitwise metrics (15 metrics)
│   ├── pattern_metrics.py     # Pattern metrics (10 metrics)
│   ├── runlength_metrics.py   # Run-length metrics (8 metrics)
│   ├── structure_metrics.py   # Structure metrics (10 metrics)
│   ├── complexity_metrics.py  # Complexity metrics (7 metrics)
│   └── file_ideality_metrics.py # Ideality metrics (5 metrics)
├── strategies/                 # Search strategies
│   ├── __init__.py
│   ├── base_strategy.py       # Base strategy interface
│   ├── mcts_strategy.py       # Monte Carlo Tree Search
│   ├── genetic_strategy.py    # Genetic Algorithm
│   ├── beam_strategy.py       # Beam Search
│   ├── annealing_strategy.py  # Simulated Annealing
│   ├── heuristic_strategy.py  # Heuristic Search
│   └── greedy_strategy.py     # Greedy Search
├── engine/                     # Search engine
│   ├── __init__.py
│   ├── pipeline.py            # Main search pipeline
│   ├── gui_pipeline.py        # GUI-specific pipeline
│   ├── state.py               # Search state management
│   └── history.py             # Search history tracking
├── scoring/                    # Scoring system
│   ├── __init__.py
│   └── scorer.py              # Multi-criteria scoring
├── results/                    # Results handling
│   ├── __init__.py
│   ├── formatter.py           # Result formatting
│   └── exporter.py            # Result export
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── error_handler.py       # Global error handling
│   ├── validators.py          # Input validation
│   └── logger.py              # Logging utilities
└── gui/                        # GUI components
    ├── main_window.py         # Main GUI window
    ├── panels/                # GUI panels
    └── resources/             # GUI resources

config/                          # Configuration files
├── strategies/                  # Strategy configurations
├── operations/                  # Operation configurations
└── metrics/                    # Metric configurations

gui_main.py                     # GUI entry point
requirements.txt                # Dependencies
```

---

## Core Components

### 1. Operations Registry (`operations/operations_registry.py`)

**Purpose:** Central hub for managing all binary operations.

**Key Classes:**
```python
class OperationsRegistry:
    """Manages 101 operations across 6 categories."""

    def __init__(self) -> None:
    def register_operation(self, name: str, function: Callable, metadata: Dict) -> None:
    def get_operation(self, name: str) -> Callable:
    def list_operations(self) -> List[str]:
    def get_operations_by_category(self, category: str) -> Dict[str, Callable]:
    def validate_operation_params(self, operation_name: str, params: Dict) -> bool:
```

**Key Functions:**
- `_load_all_operations()` - Loads all operation modules
- `filter_operations(allowed_operations)` - Filter operations
- `limit_operations(max_operations)` - Random operation selection
- `get_registry_summary()` - Get operations summary

**Important Variables:**
- `operations: Dict[str, Callable]` - All operation functions
- `operation_metadata: Dict[str, Dict]` - Operation metadata

### 2. Metrics Registry (`metrics/metrics_registry.py`)

**Purpose:** Central hub for managing all evaluation metrics.

**Key Classes:**
```python
class MetricsRegistry:
    """Manages 82+ metrics across 8 categories."""

    def __init__(self) -> None:
    def register_metric(self, name: str, function: Callable, metadata: Dict) -> None:
    def calculate_metric(self, binary_data: bytes, metric_name: str) -> float:
    def calculate_metrics(self, binary_data: bytes, metric_names: List[str]) -> Dict[str, float]:
    def calculate_all_metrics(self, binary_data: bytes) -> Dict[str, float]:
```

**Key Functions:**
- `_load_all_metrics()` - Loads all metric modules
- `get_metrics_by_category(category)` - Get metrics by category
- `get_metric_categories()` - List all categories

### 3. Search Pipeline (`engine/pipeline.py`)

**Purpose:** Main orchestration of search strategies and operations.

**Key Classes:**
```python
class SearchPipeline:
    """Main search pipeline coordinating strategies and operations."""

    def __init__(self, config: Dict, operations_registry, metrics_registry):
    def run_search(self, initial_data: bytes, max_iterations: int) -> SearchResults:
    def get_best_results(self) -> List[SearchState]:
    def stop_search(self) -> None:
```

**Key Functions:**
- `run_search()` - Execute search with current strategy
- `evaluate_state()` - Score a search state using metrics
- `get_strategy_performance()` - Track strategy performance

**Important Variables:**
- `strategy` - Current search strategy instance
- `operations_registry` - Available operations
- `metrics_registry` - Available metrics
- `best_states` - Best found states

---

## Operations System

### Working Operations Summary

| Category | Total | Working | Success Rate |
|-----------|-------|---------|--------------|
| Bitwise   | 20    | 19      | 95%          |
| Reordering| 15    | 12      | 80%          |
| Delta     | 10    | 9       | 90%          |
| Substitution| 20   | 14      | 70%          |
| Transform | 20    | 16      | 80%          |
| Custom    | 15+   | 5       | 33%          |
| **TOTAL** | **101**| **75**  | **74.3%**    |

### Detailed Operation Analysis

#### Bitwise Operations (`operations/bitwise_ops.py`)

**Class:** `BitwiseOperations`

**Working Operations (19/20):**
```python
# Fully working with reversibility
xor_constant(binary_data, constant=0x55) -> (data, inverse, metadata)
not_bytes(binary_data) -> (data, inverse, metadata)
rotate_left(binary_data, shift=1) -> (data, inverse, metadata)
rotate_right(binary_data, shift=1) -> (data, inverse, metadata)
swap_bits(binary_data, bit1=0, bit2=7) -> (data, inverse, metadata)
reverse_bits(binary_data) -> (data, inverse, metadata)
interleave_bits(binary_data) -> (data, inverse, metadata)
deinterleave_bits(binary_data) -> (data, inverse, metadata)
reverse_bytes(binary_data) -> (data, inverse, metadata)
toggle_bit(binary_data, bit_position=1) -> (data, inverse, metadata)

# Working but not reversible
extract_high_nibble(binary_data) -> (data, inverse, metadata)
extract_low_nibble(binary_data) -> (data, inverse, metadata)
```

**Broken Operations (1/20):**
- `xor_range` - Parameter handling issues

**Hardcoded Values:**
- Default constant values: 0x55 (binary 01010101)
- Default bit positions: 0, 7
- Default shift amounts: 1

**Key Functions:**
```python
def xor_with_constant(self, binary_data: bytes, constant: int) -> Tuple[bytes, Callable, Dict]:
def rotate_bits_left(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
def swap_bits_in_byte(self, binary_data: bytes, bit1: int, bit2: int) -> Tuple[bytes, Callable, Dict]:
```

#### Transform Operations (`operations/transform_ops.py`)

**Class:** `TransformOperations`

**Recently Enhanced Operations:**
```python
# Real implementations (replaced placeholders)
dct_transform(binary_data, padding='auto', normalization='ortho') -> (data, inverse, metadata)
dwt_transform(binary_data, wavelet='haar', mode='symmetric', levels=1) -> (data, inverse, metadata)
fft_transform(binary_data, window_function='none', padding='optimal') -> (data, inverse, metadata)
huffman_encode(binary_data, canonical=True) -> (data, inverse, metadata)
run_length_encode(binary_data, min_run_length=3, max_run_length=255, mode='byte') -> (data, inverse, metadata)
lz77_encode(binary_data, window_size=32768, buffer_size=258, min_match_length=3) -> (data, inverse, metadata)
arithmetic_encode(binary_data) -> (data, inverse, metadata)
```

**Key Functions (Newly Implemented):**
```python
def _numpy_dct_fallback(self, data) -> np.ndarray:
def _haar_dwt_fallback(self, data) -> Tuple[bytes, Dict]:
def _apply_window_function(self, data, window_type) -> np.ndarray:
def _extract_huffman_codes_from_id(self, node_id, prefix, codes) -> None:
```

**Dependencies:**
- **Primary:** numpy (graceful fallback to pure Python)
- **Optional:** scipy.fft, pywt (PyWavelets)
- **Fallback implementations:** Pure Python alternatives for all transforms

#### Custom Operations (`operations/custom_ops.py`)

**Working Operations:**
```python
base64_encode(binary_data) -> (data, inverse, metadata)
dna_encode(binary_data) -> (data, inverse, metadata)
steganography_extract(binary_data) -> (data, inverse, metadata)
```

**Broken Operations (10/15):**
- Most cryptographic operations (feistel_network, spn_substitution)
- Error correction operations
- Custom compression operations

---

## Metrics System

### Working Metrics (Without Numpy)

#### Entropy Metrics (`metrics/entropy_metrics.py`)

**Class:** `EntropyMetrics`

**Working Metrics:**
```python
shannon_entropy_global(binary_data: bytes) -> float
conditional_entropy_order1(binary_data: bytes) -> float
conditional_entropy_order2(binary_data: bytes) -> float
entropy_variance(binary_data: bytes) -> float
entropy_efficiency(binary_data: bytes) -> float
```

**Key Functions:**
```python
def _calculate_byte_frequencies(self, data: bytes) -> Dict[int, int]:
def _calculate_shannon_entropy(self, frequencies: Dict) -> float:
def _windowed_entropy(self, data: bytes, window_size: int) -> float:
```

#### Compression Metrics (`metrics/compression_metrics.py`)

**Class:** `CompressionMetrics`

**Working Metrics:**
```python
lz77_ratio(binary_data: bytes) -> float
zlib_ratio(binary_data: bytes) -> float
compression_efficiency(binary_data: bytes) -> float
redundancy_score(binary_data: bytes) -> float
```

**Hardcoded Values:**
- Window sizes: 32, 64, 128, 256 bytes
- Default compression levels: 6 (for zlib-based metrics)

### Broken Metrics (Requires Numpy)

**Categories requiring numpy:**
- Statistical Metrics - Statistical analysis requiring numpy arrays
- Bitwise Metrics - Bit-level analysis using numpy bit operations
- Pattern Metrics - Pattern detection using numpy correlation
- Structure Metrics - Structural analysis with numpy matrices
- File Ideality Metrics - Advanced ideality calculations

---

## Search Strategies

### Strategy Base Class (`strategies/base_strategy.py`)

**Abstract Class:**
```python
class BaseStrategy(ABC):
    """Abstract base class for all search strategies."""

    @abstractmethod
    def propose(self, current_state: SearchState) -> SearchState:
        """Propose next state based on current state."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
```

### MCTS Strategy (`strategies/mcts_strategy.py`)

**Class:** `MCTSStrategy`

**Key Features:**
- Monte Carlo Tree Search with 70+ configurable parameters
- UCB1 selection algorithm
- Random simulations
- Node expansion and backpropagation

**Configuration Parameters:**
```yaml
# From config/strategies/strategy_mcts.yaml
exploration_constant: 1.41
simulation_count: 1000
max_tree_depth: 50
max_children: 10
expansion_threshold: 5
selection_strategy: "ucb1"
```

**Key Functions:**
```python
def propose(self, current_state: SearchState) -> SearchState:
def _select_node(self, root: MCTSNode) -> MCTSNode:
def _expand_node(self, node: MCTSNode, state: SearchState) -> List[MCTSNode]:
def _simulate(self, state: SearchState) -> float:
def _backpropagate(self, node: MCTSNode, reward: float) -> None:
```

**Issues:**
- Memory usage grows with tree size (needs periodic pruning)
- Configuration complexity (70+ parameters can be overwhelming)
- No built-in parallelization

### Genetic Strategy (`strategies/genetic_strategy.py`)

**Class:** `GeneticStrategy`

**Key Features:**
- Population-based evolution
- Tournament selection
- Crossover and mutation operations
- Elitism preservation

**Key Functions:**
```python
def propose(self, current_state: SearchState) -> SearchState:
def _initialize_population(self, initial_state: SearchState) -> List[SearchState]:
def _tournament_selection(self, population: List[SearchState], tournament_size: int) -> SearchState:
def _crossover(self, parent1: SearchState, parent2: SearchState) -> SearchState:
def _mutate(self, state: SearchState, mutation_rate: float) -> SearchState:
```

**Hardcoded Values:**
- Default population size: 50
- Mutation rate: 0.1
- Crossover rate: 0.7
- Tournament size: 3

---

## Engine & Pipeline

### Main Pipeline (`engine/pipeline.py`)

**Class:** `SearchPipeline`

**Key Functions:**
```python
def run_search(self, initial_data: bytes, max_iterations: int) -> SearchResults:
def evaluate_state(self, state: SearchState) -> float:
def _create_search_state(self, data: bytes, operations: List[Tuple], parent_state: Optional[SearchState] = None) -> SearchState:
def _update_history(self, state: SearchState) -> None:
```

**Workflow:**
1. Initialize search with binary data
2. Apply current strategy to propose next state
3. Evaluate state using configured metrics
4. Update search history and best states
5. Continue until max iterations or stop condition

**Important Variables:**
```python
class SearchState:
    data: bytes                           # Current binary data
    operations: List[Tuple]              # Applied operations
    score: float                          # Current score
    iteration: int                        # Iteration number
    parent_state: Optional[SearchState]  # Parent state
    children: List[SearchState]          # Child states
```

### State Management (`engine/state.py`)

**Class:** `SearchState`

**Key Functions:**
```python
def apply_operation(self, operation: Tuple) -> 'SearchState':
def calculate_score(self, metrics_registry: MetricsRegistry, metric_weights: Dict[str, float]) -> float:
def get_transformation_depth(self) -> int:
def copy(self) -> 'SearchState':
```

**Hardcoded Values:**
- Default max operations per state: 100
- Default score for invalid states: -inf
- Score normalization factor: 1000.0

---

## Configuration System

### Strategy Configurations (`config/strategies/`)

**File Structure:**
```
config/strategies/
├── strategy_default.yaml    # Default parameters
├── strategy_mcts.yaml       # MCTS-specific (70+ params)
├── strategy_genetic.yaml    # Genetic-specific
├── strategy_beam.yaml       # Beam-specific
├── strategy_annealing.yaml # Annealing-specific
└── strategy_heuristic.yaml  # Heuristic-specific
```

**Example Configuration (MCTS):**
```yaml
exploration_constant: 1.41421356237
simulation_count: 1000
max_tree_depth: 50
max_children: 10
expansion_threshold: 5
selection_strategy: "ucb1"
simulation_strategy: "random"
backpropagation_strategy: "average"
early_termination: true
early_termination_threshold: 0.95
```

### Configuration Loading

**Key Functions:**
```python
def load_config(config_path: str) -> Dict:
def validate_config(config: Dict, schema: Dict) -> bool:
def merge_configs(base_config: Dict, override_config: Dict) -> Dict:
```

---

## GUI Components

### Main GUI (`gui/main_window.py`)

**Class:** `MainWindow`

**Features:**
- File loading and saving
- Strategy selection and configuration
- Real-time search progress
- Results visualization
- Terminal fallback mode

**Key Functions:**
```python
def __init__(self, fallback_config: Dict = None):
def load_file(self, filepath: str) -> None:
def start_search(self) -> None:
def stop_search(self) -> None:
def display_results(self, results: List[SearchState]) -> None:
```

### GUI Dependency Handling

**Working Features:**
- Graceful fallback when matplotlib unavailable
- Terminal mode when tkinter missing
- ASCII-based visualizations
- Simplified mathematical operations

**Broken Features:**
- Advanced visualizations require matplotlib
- Some operations require scipy
- Statistical metrics need numpy

---

## Broken Items & Issues

### Critical Issues

#### 1. **Operations Requiring Parameters (26 failed operations)**

**Problem:** Many operations require specific parameters but lack proper parameter handling or defaults.

**Examples:**
```python
# These operations fail without proper parameter handling
byte_swap(data, offset, length) -> Requires offset, length parameters
feistel_network(data, rounds, keys) -> Requires rounds, keys parameters
polynomial_substitution(data, polynomial) -> Requires polynomial coefficients
```

**Solution:** Implement proper parameter validation and default values.

#### 2. **Metrics Dependencies on Numpy**

**Problem:** 40+ metrics require numpy but system runs without it.

**Affected Metrics:**
- All statistical metrics (chi-square, KL divergence, etc.)
- Bitwise metrics (bit plane analysis, etc.)
- Pattern metrics (autocorrelation, periodicity)
- Structure metrics (alignment, block detection)

**Current Status:** 42+ metrics work without numpy, 40+ require numpy.

#### 3. **Placeholder Implementations**

**Fixed (Previously broken):**
- ✅ DCT Transform - Now has real scipy implementation with numpy fallback
- ✅ DWT Transform - Now has real PyWavelets implementation with Haar fallback
- ✅ FFT Transform - Now has real numpy.fft implementation
- ✅ Huffman Encoding - Now has real frequency-based implementation
- ✅ Run-Length Encoding - Now has configurable threshold implementation
- ✅ LZ77 Encoding - Now has sliding window implementation
- ✅ Arithmetic Encoding - Now has frequency-based implementation

**Still Broken:**
- ❌ Golomb coding - Parameter handling issues
- ❌ Walsh-Hadamard - Matrix implementation issues

#### 4. **Hardcoded Values and Magic Numbers**

**Found in Multiple Files:**

**In Operations:**
```python
# bitwise_ops.py
DEFAULT_CONSTANT = 0x55  # Binary 01010101
DEFAULT_SHIFT = 1
DEFAULT_BIT1 = 0
DEFAULT_BIT2 = 7

# transform_ops.py
DEFAULT_WINDOW_SIZE = 32768  # LZ77 window
DEFAULT_BUFFER_SIZE = 258
DEFAULT_MIN_RUN_LENGTH = 3
```

**In Strategies:**
```python
# genetic_strategy.py
DEFAULT_POPULATION_SIZE = 50
DEFAULT_MUTATION_RATE = 0.1
DEFAULT_TOURNAMENT_SIZE = 3

# mcts_strategy.py
DEFAULT_EXPLORATION_CONSTANT = 1.41421356237  # sqrt(2)
DEFAULT_SIMULATION_COUNT = 1000
```

**In Metrics:**
```python
# compression_metrics.py
DEFAULT_WINDOW_SIZES = [32, 64, 128, 256]
DEFAULT_COMPRESSION_LEVEL = 6
```

#### 5. **Memory Issues**

**Problems:**
- MCTS strategy memory grows unbounded
- Large file processing lacks streaming
- No memory limit enforcement
- Garbage collection not optimized

**Solution Needed:**
- Implement periodic tree pruning in MCTS
- Add streaming for large files
- Implement memory limits and monitoring

#### 6. **Error Handling Inconsistencies**

**Problems:**
- Not all operations handle invalid inputs gracefully
- Error messages are not user-friendly
- No standardized error codes
- Recovery strategies inconsistent

**Partially Fixed:**
- ✅ Global error handler implemented
- ✅ Recovery strategies for common exceptions
- ❌ Not all strategies use error handler yet

#### 7. **Configuration Complexity**

**Problem:** MCTS has 70+ configurable parameters, overwhelming users.

**Current State:**
- Configuration files exist but lack validation
- No parameter explanation
- No recommended settings for different use cases

#### 8. **Test Coverage Gaps**

**Missing Tests:**
- Integration tests between components
- Performance benchmarks
- Edge case testing (empty files, very large files)
- Cross-platform compatibility

### Minor Issues

#### 1. **Unused Imports and Functions**

**Found in:**
```python
# Multiple files have unused imports
import numpy as np  # Imported but not used in some functions
import scipy.fft  # Imported but fallback used instead
```

#### 2. **Inconsistent Naming Conventions**

**Examples:**
```python
# Mixed naming patterns
calculateShannonEntropy() vs calculate_shannon_entropy()
OperationRegistry vs operations_registry
SearchState vs search_state
```

#### 3. **Documentation Gaps**

**Missing:**
- Inline documentation for complex algorithms
- API documentation for public methods
- Usage examples for operations
- Architecture documentation

#### 4. **Code Duplication**

**Found in:**
- Similar parameter validation across operations
- Duplicated error handling patterns
- Reversible operation inverse implementations

---

## Development Guidelines

### Code Style Standards

**Python Standards:**
- Follow PEP 8 naming conventions
- Use type hints for all public methods
- Maximum line length: 88 characters
- Use docstrings for all classes and public methods

**Project-Specific Standards:**
- Operation functions return `(data, inverse_func, metadata)`
- Metric functions return `float`
- Configuration uses YAML format
- Error messages should be user-friendly

### Adding New Operations

**Template:**
```python
def new_operation(self, binary_data: bytes, required_param: int, optional_param: str = "default") -> Tuple[bytes, Callable, Dict]:
    """
    Brief description of the operation.

    Args:
        binary_data: Input binary data
        required_param: Description of required parameter
        optional_param: Description of optional parameter

    Returns:
        Tuple of (transformed_data, inverse_function, metadata)
    """
    # Parameter validation
    if not 0 <= required_param <= 255:
        raise ValueError("required_param must be in range 0-255")

    # Implementation
    transformed_data = _implementation(binary_data, required_param, optional_param)

    # Inverse function
    def inverse():
        return _reverse_implementation(transformed_data, required_param, optional_param)

    # Metadata
    metadata = {
        'operation': 'new_operation',
        'bytes_affected': len(binary_data),
        'reversible': True,
        'parameters': {
            'required_param': required_param,
            'optional_param': optional_param
        }
    }

    return transformed_data, inverse, metadata
```

**Steps:**
1. Implement operation function
2. Add inverse function (if reversible)
3. Create comprehensive metadata
4. Add to operations registry
5. Add unit tests
6. Update documentation

### Adding New Metrics

**Template:**
```python
def new_metric(self, binary_data: bytes) -> float:
    """
    Calculate new metric for binary data.

    Args:
        binary_data: Input binary data

    Returns:
        Metric value as float
    """
    if len(binary_data) == 0:
        return 0.0

    # Implementation
    metric_value = _calculate_metric(binary_data)

    return metric_value
```

**Steps:**
1. Implement metric calculation
2. Add error handling for edge cases
3. Add to metrics registry
4. Add unit tests
5. Update documentation

### Configuration Management

**Adding New Configuration Parameters:**
1. Add parameter to YAML config file
2. Add parameter validation
3. Update strategy to use parameter
4. Add default value
5. Update documentation

**Configuration Validation:**
```python
def validate_mcts_config(config: Dict) -> bool:
    """Validate MCTS configuration parameters."""
    required_params = ['exploration_constant', 'simulation_count']

    for param in required_params:
        if param not in config:
            raise ValueError(f"Missing required parameter: {param}")

    if config['exploration_constant'] <= 0:
        raise ValueError("exploration_constant must be positive")

    return True
```

---

## Extension Guide

### Modular Extension Points

#### 1. New Operation Categories

**Create new operation file:**
```python
# operations/new_category_ops.py
class NewCategoryOperations:
    def __init__(self):
        self.operations = self._create_operations()

    def _create_operations(self):
        return {
            'operation1': self.operation1,
            'operation2': self.operation2,
        }

    def operation1(self, binary_data: bytes, param: int) -> Tuple[bytes, Callable, Dict]:
        # Implementation
        pass
```

**Update registry:**
```python
# operations/operations_registry.py
from bsee.operations.new_category_ops import NewCategoryOperations

def _load_all_operations(self):
    # ... existing loads ...

    # Load new category operations
    new_category_ops = NewCategoryOperations()
    for name, func in new_category_ops.get_operations().items():
        self.register_operation(name, func, new_category_ops.get_metadata(name))
```

#### 2. New Search Strategies

**Create new strategy:**
```python
# strategies/new_strategy.py
from bsee.strategies.base_strategy import BaseStrategy

class NewStrategy(BaseStrategy):
    def __init__(self, config: Dict):
        self.config = config
        self.name = "new_strategy"

    def propose(self, current_state: SearchState) -> SearchState:
        # Implementation
        pass

    def get_name(self) -> str:
        return self.name
```

#### 3. New Metrics Categories

**Create new metrics file:**
```python
# metrics/new_category_metrics.py
class NewCategoryMetrics:
    def __init__(self):
        self.metrics = self._create_metrics()

    def _create_metrics(self):
        return {
            'metric1': self.metric1,
            'metric2': self.metric2,
        }

    def metric1(self, binary_data: bytes) -> float:
        # Implementation
        pass
```

### Testing Framework

**Operation Testing:**
```python
# tests/test_operations.py
def test_operation_reversibility():
    """Test that reversible operations work correctly."""
    ops = OperationsRegistry()
    test_data = b"Hello World"

    for op_name in ops.list_operations():
        operation = ops.get_operation(op_name)
        metadata = ops.get_operation_metadata(op_name)

        if metadata.get('reversible', False):
            transformed, inverse_func, _ = operation(test_data)
            restored = inverse_func()
            assert restored == test_data, f"{op_name} not reversible"
```

**Metric Testing:**
```python
# tests/test_metrics.py
def test_metric_ranges():
    """Test that metrics return values in expected ranges."""
    metrics = MetricsRegistry()
    test_data = b"Hello World"

    for metric_name in metrics.list_metrics():
        value = metrics.calculate_metric(test_data, metric_name)
        assert isinstance(value, (int, float)), f"{metric_name} not numeric"
        assert not (value != value), f"{metric_name} is NaN"
```

### Plugin System

**Operation Plugin Interface:**
```python
# plugins/plugin_interface.py
class OperationPlugin:
    """Base class for operation plugins."""

    def get_operations(self) -> Dict[str, Callable]:
        """Return dictionary of operations."""
        pass

    def get_metadata(self, operation_name: str) -> Dict:
        """Return metadata for operation."""
        pass

    def validate_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        pass
```

**Plugin Loading:**
```python
# plugins/plugin_loader.py
def load_plugins(plugin_directory: str) -> Dict[str, OperationPlugin]:
    """Load all plugins from directory."""
    plugins = {}

    for plugin_file in os.listdir(plugin_directory):
        if plugin_file.endswith('_plugin.py'):
            module_name = plugin_file[:-3]
            spec = importlib.util.spec_from_file_location(
                module_name,
                os.path.join(plugin_directory, plugin_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'Plugin'):
                plugin = module.Plugin()
                if plugin.validate_dependencies():
                    plugins[module_name] = plugin

    return plugins
```

---

## API Reference

### Operations Registry API

```python
class OperationsRegistry:
    def __init__(self) -> None:
        """Initialize registry and load all operations."""

    def get_operation(self, name: str) -> Callable:
        """Get operation function by name."""

    def list_operations(self) -> List[str]:
        """List all available operation names."""

    def get_operations_by_category(self, category: str) -> Dict[str, Callable]:
        """Get all operations in a specific category."""

    def register_operation(self, name: str, function: Callable, metadata: Dict) -> None:
        """Register a new operation."""

    def validate_operation_params(self, operation_name: str, params: Dict) -> bool:
        """Validate parameters for an operation."""

    def filter_operations(self, allowed_operations: Set[str]) -> None:
        """Filter operations to only allow specified ones."""

    def limit_operations(self, max_operations: int) -> None:
        """Limit the number of operations to a random subset."""
```

### Search Pipeline API

```python
class SearchPipeline:
    def __init__(self, config: Dict, operations_registry: OperationsRegistry,
                 metrics_registry: MetricsRegistry):
        """Initialize search pipeline."""

    def run_search(self, initial_data: bytes, max_iterations: int) -> SearchResults:
        """Run search for specified iterations."""

    def stop_search(self) -> None:
        """Stop the current search."""

    def get_best_results(self, top_n: int = 10) -> List[SearchState]:
        """Get top N best results."""

    def get_search_statistics(self) -> Dict:
        """Get search performance statistics."""
```

### Metrics Registry API

```python
class MetricsRegistry:
    def __init__(self) -> None:
        """Initialize registry and load all metrics."""

    def calculate_metric(self, binary_data: bytes, metric_name: str) -> float:
        """Calculate a single metric."""

    def calculate_metrics(self, binary_data: bytes, metric_names: List[str]) -> Dict[str, float]:
        """Calculate multiple metrics."""

    def calculate_all_metrics(self, binary_data: bytes) -> Dict[str, float]:
        """Calculate all available metrics."""

    def get_metric_metadata(self, metric_name: str) -> Dict:
        """Get metadata for a metric."""

    def get_metrics_by_category(self, category: str) -> Dict[str, Callable]:
        """Get all metrics in a specific category."""
```

### Strategy Base API

```python
class BaseStrategy(ABC):
    def __init__(self, config: Dict):
        """Initialize strategy with configuration."""

    @abstractmethod
    def propose(self, current_state: SearchState) -> SearchState:
        """Propose next state based on current state."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass

    def configure(self, config: Dict) -> None:
        """Update strategy configuration."""
        pass

    def get_performance_stats(self) -> Dict:
        """Get strategy performance statistics."""
        pass
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **Import Errors**

**Problem:** `ModuleNotFoundError: No module named 'numpy'`

**Solution:**
```python
# Use try/except blocks for optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def operation_with_numpy(data):
    if NUMPY_AVAILABLE:
        return numpy_operation(data)
    else:
        return fallback_operation(data)
```

#### 2. **Memory Errors**

**Problem:** `MemoryError` during large file processing

**Solution:**
```python
# Use streaming for large files
def process_large_file(filepath: str, chunk_size: int = 1024*1024):
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield process_chunk(chunk)
```

#### 3. **Parameter Validation Errors**

**Problem:** `ValueError` from invalid operation parameters

**Solution:**
```python
def validate_operation_params(operation_name: str, params: Dict) -> bool:
    metadata = operations_registry.get_operation_metadata(operation_name)
    required = metadata.get('required_params', [])

    for param in required:
        if param not in params:
            raise ValueError(f"Missing required parameter: {param}")

    return True
```

#### 4. **Performance Issues**

**Problem:** Slow search performance

**Solutions:**
- Reduce operation set with `limit_operations()`
- Use simpler strategies
- Optimize metric calculations
- Implement early stopping

#### 5. **GUI Issues**

**Problem:** GUI fails to start or display

**Solutions:**
```bash
# Check dependencies
python3 -c "import tkinter; print('tkinter available')"
python3 -c "import matplotlib; print('matplotlib available')"

# Run in terminal mode
python3 gui_main.py --terminal
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
python3 test_bsee_functionality.py --verbose
```

### Performance Profiling

Profile operation performance:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Run operation
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

---

## Development Tables

### Operations Summary Table

| Category | File | Total | Working | Broken | Success Rate |
|----------|------|-------|---------|--------|--------------|
| Bitwise | bitwise_ops.py | 20 | 19 | 1 | 95% |
| Reordering | reordering_ops.py | 15 | 12 | 3 | 80% |
| Delta | delta_ops.py | 10 | 9 | 1 | 90% |
| Substitution | substitution_ops.py | 20 | 14 | 6 | 70% |
| Transform | transform_ops.py | 20 | 16 | 4 | 80% |
| Custom | custom_ops.py | 15+ | 5 | 10+ | 33% |
| **TOTAL** | - | **101** | **75** | **26** | **74.3%** |

### Metrics Summary Table

| Category | File | Total | Working | Requires Numpy | Success Rate |
|----------|------|-------|---------|----------------|--------------|
| Entropy | entropy_metrics.py | 12 | 12 | 0 | 100% |
| Compression | compression_metrics.py | 15 | 15 | 0 | 100% |
| Statistical | statistical_metrics.py | 12 | 0 | 12 | 0% |
| Bitwise | bitwise_metrics.py | 15 | 0 | 15 | 0% |
| Pattern | pattern_metrics.py | 10 | 0 | 10 | 0% |
| Runlength | runlength_metrics.py | 8 | 8 | 0 | 100% |
| Structure | structure_metrics.py | 10 | 0 | 10 | 0% |
| Complexity | complexity_metrics.py | 7 | 7 | 0 | 100% |
| Ideality | file_ideality_metrics.py | 5 | 0 | 5 | 0% |
| **TOTAL** | - | **94** | **42** | **52** | **44.7%** |

### Strategy Summary Table

| Strategy | File | Status | Complexity | Parameters | Performance |
|----------|------|--------|------------|------------|-------------|
| MCTS | mcts_strategy.py | Working | High | 70+ | Slow but thorough |
| Genetic | genetic_strategy.py | Working | Medium | 15 | Medium |
| Beam | beam_strategy.py | Working | Medium | 8 | Fast |
| Annealing | annealing_strategy.py | Working | Medium | 10 | Medium |
| Heuristic | heuristic_strategy.py | Working | Medium | 12 | Medium |
| Greedy | greedy_strategy.py | Working | Low | 5 | Fast |

### Configuration Files Table

| File | Purpose | Parameters | Status |
|------|---------|-----------|--------|
| strategy_default.yaml | Default strategy settings | 20 | Working |
| strategy_mcts.yaml | MCTS specific settings | 70+ | Working |
| strategy_genetic.yaml | Genetic algorithm settings | 15 | Working |
| strategy_beam.yaml | Beam search settings | 8 | Working |
| strategy_annealing.yaml | Simulated annealing settings | 10 | Working |
| strategy_heuristic.yaml | Heuristic search settings | 12 | Working |

### Dependencies Table

| Dependency | Required For | Status | Fallback Available |
|------------|--------------|--------|-------------------|
| numpy | Statistical/Bitwise/Pattern/Structure metrics | Missing | Yes (limited) |
| scipy | Advanced transforms (FFT/DCT/DWT) | Missing | Yes (numpy) |
| pywt | Wavelet transforms | Missing | Yes (Haar) |
| tkinter | GUI | Available | No (terminal mode) |
| matplotlib | Advanced visualizations | Missing | Yes (ASCII) |
| lz4 | LZ4 compression | Missing | Yes (skip) |
| zstandard | Zstandard compression | Missing | Yes (skip) |

### Classes Reference Table

| Class | Module | Purpose | Public Methods |
|-------|--------|---------|---------------|
| OperationsRegistry | operations/operations_registry.py | Manage operations | get_operation(), list_operations(), get_operations_by_category() |
| MetricsRegistry | metrics/metrics_registry.py | Manage metrics | calculate_metric(), calculate_all_metrics(), get_metrics_by_category() |
| SearchPipeline | engine/pipeline.py | Main search orchestration | run_search(), stop_search(), get_best_results() |
| SearchState | engine/state.py | Search state representation | apply_operation(), calculate_score(), copy() |
| BaseStrategy | strategies/base_strategy.py | Strategy base class | propose(), get_name(), configure() |
| MCTSStrategy | strategies/mcts_strategy.py | MCTS implementation | propose(), get_tree_statistics() |
| GeneticStrategy | strategies/genetic_strategy.py | Genetic algorithm | propose(), get_population_stats() |
| BitwiseOperations | operations/bitwise_ops.py | Bitwise operations | get_operations(), get_metadata() |
| TransformOperations | operations/transform_ops.py | Transform operations | get_operations(), get_metadata() |
| EntropyMetrics | metrics/entropy_metrics.py | Entropy calculations | get_metrics(), get_metadata() |
| CompressionMetrics | metrics/compression_metrics.py | Compression metrics | get_metrics(), get_metadata() |

### Functions Reference Table

| Function | Module | Parameters | Returns | Purpose |
|----------|--------|------------|--------|---------|
| xor_constant() | operations/bitwise_ops.py | binary_data, constant | Tuple[bytes, Callable, Dict] | XOR with constant |
| dct_transform() | operations/transform_ops.py | binary_data, padding, normalization | Tuple[bytes, Callable, Dict] | Discrete Cosine Transform |
| shannon_entropy_global() | metrics/entropy_metrics.py | binary_data | float | Shannon entropy |
| lz77_ratio() | metrics/compression_metrics.py | binary_data | float | LZ77 compression ratio |
| ucb_select() | strategies/mcts_strategy.py | children, exploration_constant | MCTSNode | UCB1 selection |
| tournament_selection() | strategies/genetic_strategy.py | population, tournament_size | SearchState | Tournament selection |

### Variables Reference Table

| Variable | Type | Module | Purpose | Default Value |
|----------|------|--------|---------|-------------|
| DEFAULT_EXPLORATION_CONSTANT | float | strategies/mcts_strategy.py | UCB1 exploration | 1.41421356237 |
| DEFAULT_POPULATION_SIZE | int | strategies/genetic_strategy.py | Genetic population | 50 |
| DEFAULT_MUTATION_RATE | float | strategies/genetic_strategy.py | Mutation probability | 0.1 |
| DEFAULT_WINDOW_SIZE | int | operations/transform_ops.py | LZ77 window size | 32768 |
| DEFAULT_MIN_RUN_LENGTH | int | operations/transform_ops.py | RLE min run length | 3 |
| MAX_OPERATIONS | int | engine/pipeline.py | Max operations per state | 100 |
| SCORE_NORMALIZATION | float | engine/state.py | Score normalization | 1000.0 |
| NUMPY_AVAILABLE | bool | Multiple files | Numpy availability check | False |
| SCIPY_AVAILABLE | bool | Multiple files | Scipy availability check | False |

---

## Quick Start Guide

### Basic Usage

```python
from bsee.operations.operations_registry import OperationsRegistry
from bsee.metrics.metrics_registry import MetricsRegistry
from bsee.engine.pipeline import SearchPipeline

# Initialize components
ops_reg = OperationsRegistry()
metrics_reg = MetricsRegistry()

# Load configuration
with open('config/strategies/strategy_mcts.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create pipeline
pipeline = SearchPipeline(config, ops_reg, metrics_reg)

# Run search
test_data = b"Hello World - BSEE Test Data"
results = pipeline.run_search(test_data, max_iterations=100)

# Get best results
best_results = pipeline.get_best_results(top_n=5)
for i, state in enumerate(best_results):
    print(f"Rank {i+1}: Score={state.score:.4f}, Operations={len(state.operations)}")
```

### Custom Operations

```python
# Add custom operation
def custom_compress(data: bytes) -> Tuple[bytes, Callable, Dict]:
    compressed = gzip.compress(data)

    def inverse():
        return gzip.decompress(compressed)

    return compressed, inverse, {
        'operation': 'custom_compress',
        'reversible': True,
        'compression_ratio': len(data) / len(compressed)
    }

# Register custom operation
ops_reg.register_operation('custom_compress', custom_compress, {
    'category': 'custom',
    'description': 'Custom gzip compression',
    'reversible': True
})
```

### Custom Metrics

```python
# Add custom metric
def custom_metric(data: bytes) -> float:
    """Calculate custom pattern metric."""
    if len(data) < 2:
        return 0.0

    # Calculate pattern repetition
    pattern_length = 4
    patterns = {}

    for i in range(len(data) - pattern_length + 1):
        pattern = data[i:i+pattern_length]
        patterns[pattern] = patterns.get(pattern, 0) + 1

    max_repetitions = max(patterns.values()) if patterns else 1
    total_patterns = len(patterns)

    return max_repetitions / total_patterns if total_patterns > 0 else 0.0

# Register custom metric
metrics_reg.register_metric('custom_pattern', custom_metric, {
    'category': 'pattern',
    'description': 'Custom pattern repetition metric'
})
```

---

## Links and References

### Internal Links
- [Operations Registry](#operations-registry)
- [Metrics Registry](#metrics-registry)
- [Search Pipeline](#search-pipeline)
- [Strategy Base Class](#strategy-base-class)
- [Configuration System](#configuration-system)

### External Links
- [Python Official Documentation](https://docs.python.org/3/)
- [NumPy Documentation](https://numpy.org/doc/)
- [SciPy Documentation](https://scipy.org/doc/)
- [PyWavelets Documentation](https://pywavelets.readthedocs.io/)

### Related Projects
- [Binary Analysis Tools](https://github.com/topics/binary-analysis)
- [Data Compression Libraries](https://github.com/topics/compression)
- [Search Algorithms](https://github.com/topics/search-algorithms)

---

**This documentation provides a comprehensive overview of the BSEE system. For specific implementation details, refer to the individual source files and inline documentation.**