# BSEE Creator's Guide

## Overview
This comprehensive guide covers how to create custom strategies, policies, cost models, metrics, and operations for BSEE (Binary Structure Exploration Engine).

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Creating Custom Strategies](#creating-custom-strategies)
3. [Creating Custom Policies](#creating-custom-policies)
4. [Creating Custom Cost Models](#creating-custom-cost-models)
5. [Creating Custom Metrics](#creating-custom-metrics)
6. [Creating Custom Operations](#creating-custom-operations)
7. [Configuration System](#configuration-system)
8. [Testing and Validation](#testing-and-validation)
9. [Best Practices](#best-practices)

---

## Architecture Overview

### Core Components

#### Strategy System
- **Location**: `bsee/strategies/`
- **Base Class**: `bsee.strategies.base_strategy.BaseStrategy`
- **Purpose**: Define how BSEE explores the search space

#### Policy System
- **Location**: `bsee/policies/`
- **Purpose**: Define optimization objectives and constraints

#### Cost Model System
- **Location**: `bsee/cost/`
- **Purpose**: Calculate dynamic costs for operations

#### Metrics System
- **Location**: `bsee/metrics/`
- **Purpose**: Measure binary properties and optimization progress

#### Operations System
- **Location**: `bsee/operations/`
- **Purpose**: Define reversible transformations

### Registration System
All components register with their respective registries:
- `OperationsRegistry`: Registers available operations
- `MetricsRegistry`: Registers available metrics
- Strategy discovery: Automatic strategy loading

---

## Creating Custom Strategies

### Strategy Template

Create a new file: `bsee/strategies/my_custom_strategy.py`

```python
"""
Custom Strategy Example
Implements your novel optimization approach.
"""

from typing import Dict, Any, Optional, List, Tuple
from bsee.strategies.base_strategy import BaseStrategy
from bsee.engine.state import State

class MyCustomStrategy(BaseStrategy):
    """Custom strategy with novel optimization approach."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.

        Args:
            config: Strategy configuration dictionary
        """
        super().__init__(config)
        self.name = "my_custom_strategy"
        self.description = "My custom optimization approach"

        # Load strategy-specific parameters
        self.exploration_rate = config.get('exploration_rate', 0.1)
        self.convergence_threshold = config.get('convergence_threshold', 0.001)
        self.max_iterations = config.get('max_iterations', 1000)

        # Initialize strategy state
        self.current_temperature = 1.0
        self.best_score = float('-inf')
        self.iteration_count = 0

    def propose(self, current_state: State) -> Tuple[str, Dict[str, Any]]:
        """
        Propose next operation.

        Args:
            current_state: Current binary state

        Returns:
            Tuple of (operation_name, parameters)
        """
        # Strategy logic here
        operations = self._get_available_operations()

        if self.iteration_count < self.max_iterations * 0.3:
            # Exploration phase
            operation = self._exploration_proposal(current_state, operations)
        else:
            # Exploitation phase
            operation = self._exploitation_proposal(current_state, operations)

        self.iteration_count += 1
        return operation

    def accept(self, new_state: State) -> bool:
        """
        Decide whether to accept the new state.

        Args:
            new_state: Proposed new state

        Returns:
            Boolean indicating acceptance
        """
        # Simple acceptance criteria - can be sophisticated
        return new_state.score > self.best_score * (1 + self.convergence_threshold)

    def is_converged(self) -> bool:
        """
        Check if strategy has converged.

        Returns:
            Boolean indicating convergence
        """
        return self.iteration_count >= self.max_iterations

    def _get_available_operations(self) -> List[str]:
        """Get list of available operations."""
        # This would interact with the operations registry
        return ['bit_flip', 'byte_substitution', 'dct_transform']

    def _exploration_proposal(self, state: State, operations: List[str]) -> Tuple[str, Dict[str, Any]]:
        """Generate exploration proposal."""
        import random
        operation = random.choice(operations)

        if operation == 'bit_flip':
            params = {
                'bit_index': random.randint(0, state.size * 8 - 1),
                'flip_count': random.randint(1, 3)
            }
        else:
            params = {}

        return operation, params

    def _exploitation_proposal(self, state: State, operations: List[str]) -> Tuple[str, Dict[str, Any]]:
        """Generate exploitation proposal based on learned preferences."""
        # Implement your exploitation logic
        operation = self._select_best_operation(state, operations)

        if operation == 'bit_flip':
            params = {
                'bit_index': self._find_most_flippable_bit(state),
                'flip_count': 1
            }
        else:
            params = {}

        return operation, params

    def _find_most_flippable_bit(self, state: State) -> int:
        """Find the bit that provides most improvement potential."""
        # Your bit selection logic
        return 0  # Placeholder

    def _select_best_operation(self, state: State, operations: List[str]) -> str:
        """Select best operation based on historical performance."""
        # Your operation selection logic
        return operations[0]  # Placeholder
```

### Strategy Configuration

Create configuration file: `config/strategies/strategy_my_custom_strategy.yaml`

```yaml
# My Custom Strategy Configuration
name: "My Custom Strategy"
description: "Advanced optimization with adaptive parameters"

# Strategy-specific parameters
exploration_rate: 0.1
convergence_threshold: 0.001
max_iterations: 1000

# Operation preferences
preferred_operations:
  - bit_flip
  - byte_substitution
  - dct_transform

# Adaptive parameters
adaptive_exploration: true
temperature_decay: 0.995
local_search_radius: 5

# Performance tuning
parallel_evaluation: false
cache_operations: true
prune_duplicate_states: true
```

---

## Creating Custom Policies

### Policy Template

Create a new file: `bsee/policies/my_custom_policy.py`

```python
"""
Custom Policy Example
Defines optimization objectives and constraints.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PolicyConfig:
    """Configuration for custom policy."""
    name: str
    description: str
    target_metrics: Dict[str, str]  # metric_name: direction (max/min)
    constraints: Dict[str, Any]
    weights: Dict[str, float]

class MyCustomPolicy:
    """Custom optimization policy."""

    def __init__(self, config_path: str):
        """
        Initialize policy with configuration.

        Args:
            config_path: Path to policy configuration file
        """
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> PolicyConfig:
        """Load policy configuration from YAML file."""
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        return PolicyConfig(**config_data)

    def evaluate_state(self, state, target_state=None) -> float:
        """
        Evaluate state according to policy objectives.

        Args:
            state: Current state to evaluate
            target_state: Optional target for reference

        Returns:
            Policy score (higher is better)
        """
        score = 0.0

        # Apply weights to target metrics
        for metric_name, direction in self.config.target_metrics.items():
            if metric_name in state.metrics:
                metric_value = state.metrics[metric_name]
                weight = self.config.weights.get(metric_name, 1.0)

                # Normalize metric value (0-1 range)
                normalized_value = self._normalize_metric(metric_name, metric_value)

                if direction == "max":
                    score += weight * normalized_value
                else:  # min
                    score += weight * (1.0 - normalized_value)

        return score

    def _normalize_metric(self, metric_name: str, value: float) -> float:
        """Normalize metric value to 0-1 range."""
        # Implement metric-specific normalization
        if metric_name == "file_ideality_score":
            return min(1.0, max(0.0, value))
        elif metric_name == "entropy_global":
            return 1.0 - min(1.0, value / 8.0)
        else:
            return min(1.0, max(0.0, value))

    def check_constraints(self, state, operation: str) -> bool:
        """
        Check if operation violates policy constraints.

        Args:
            state: Current state
            operation: Proposed operation

        Returns:
            True if operation is allowed
        """
        # Check budget constraints
        total_cost = state.get('total_cost', 0)
        operation_cost = self._get_operation_cost(operation)

        if total_cost + operation_cost > self.config.constraints.get('max_cost', float('inf')):
            return False

        # Check operation limits
        max_operations = self.config.constraints.get('max_operations', float('inf'))
        if state.get('operation_count', 0) >= max_operations:
            return False

        # Check allowed operations
        allowed_ops = self.config.constraints.get('allowed_operations', [])
        if allowed_ops and operation not in allowed_ops:
            return False

        return True

    def _get_operation_cost(self, operation: str) -> float:
        """Get cost of operation."""
        cost_model = {
            'bit_flip': 1.0,
            'byte_substitution': 2.0,
            'dct_transform': 5.0,
            'lz77_encode': 3.0
        }
        return cost_model.get(operation, 1.0)
```

### Policy Configuration

Create configuration file: `config/policies/policy_my_custom_policy.yaml`

```yaml
# My Custom Policy Configuration
name: "My Custom Policy"
description: "Multi-objective optimization with constraints"

# Target metrics and optimization directions
target_metrics:
  file_ideality_score: "max"     # Maximize file ideality
  entropy_global: "min"           # Minimize entropy
  lz77_ratio: "max"               # Maximize compression ratio
  compression_ratio: "max"         # Maximize compression

# Metric weights (sum should typically be 1.0)
weights:
  file_ideality_score: 0.4
  entropy_global: 0.3
  lz77_ratio: 0.2
  compression_ratio: 0.1

# Constraints
constraints:
  max_cost: 10000.0                # Maximum total cost
  max_operations: 1000              # Maximum number of operations
  max_file_size_increase: 0.05      # Maximum 5% file size increase
  allowed_operations:                 # Empty = allow all
    - bit_flip
    - byte_substitution
    - dct_transform
    - lz77_encode

# Advanced options
adaptive_weights: true                 # Adapt weights during optimization
constraint_relaxation: 0.1            # Allow 10% constraint violation with penalty
early_termination_improvement: 0.001  # Stop if improvement < 0.1%
```

---

## Creating Custom Cost Models

### Cost Model Template

Create a new file: `bsee/cost/my_custom_cost_model.py`

```python
"""
Custom Cost Model Example
Implements dynamic cost calculation based on file context.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class CostConfig:
    """Configuration for custom cost model."""
    name: str
    description: str
    base_costs: Dict[str, float]
    dynamic_factors: Dict[str, Any]
    context_aware: bool

class MyCustomCostModel:
    """Custom cost model with context-aware pricing."""

    def __init__(self, config_path: str):
        """
        Initialize cost model with configuration.

        Args:
            config_path: Path to cost model configuration
        """
        self.config = self._load_config(config_path)
        self.history_window = self.config.dynamic_factors.get('history_window', 50)
        self.learning_rate = self.config.dynamic_factors.get('learning_rate', 0.01)

    def _load_config(self, config_path: str) -> CostConfig:
        """Load cost model configuration."""
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        return CostConfig(**config_data)

    def calculate_cost(self, operation: str, history: List[Dict]) -> float:
        """
        Calculate dynamic cost for operation.

        Args:
            operation: Operation name
            history: Operation history list

        Returns:
            Dynamic cost value
        """
        base_cost = self.config.base_costs.get(operation, 1.0)

        if not self.config.context_aware:
            return base_cost

        # Context-aware cost calculation
        dynamic_multiplier = self._calculate_context_factor(operation, history)
        final_cost = base_cost * dynamic_multiplier

        return final_cost

    def _calculate_context_factor(self, operation: str, history: List[Dict]) -> float:
        """Calculate context-based cost multiplier."""
        # Get recent operations
        recent_ops = [entry['operation'] for entry in history[-self.history_window:]]

        # Calculate operation frequency (inverse of frequency = higher cost)
        if operation not in recent_ops:
            return 1.5  # 50% cost increase for novel operations
        else:
            frequency = recent_ops.count(operation) / len(recent_ops)
            # Less frequent = higher cost
            return 1.0 + (1.0 - frequency) * 2.0

    def update_model(self, operation: str, actual_cost: float) -> None:
        """
        Update cost model based on actual cost feedback.

        Args:
            operation: Operation that was performed
            actual_cost: Actual cost observed
        """
        current_base = self.config.base_costs.get(operation, 1.0)

        # Simple learning rule
        error = actual_cost - current_base
        adjustment = error * self.learning_rate
        new_base = current_base + adjustment

        # Ensure costs stay positive
        self.config.base_costs[operation] = max(0.1, new_base)

    def get_operation_info(self, operation: str) -> Dict[str, Any]:
        """Get detailed information about operation cost."""
        return {
            'operation': operation,
            'base_cost': self.config.base_costs.get(operation, 1.0),
            'description': self._get_operation_description(operation),
            'complexity': self._get_operation_complexity(operation)
        }

    def _get_operation_description(self, operation: str) -> str:
        """Get human-readable description of operation."""
        descriptions = {
            'bit_flip': 'Flip individual bits in binary data',
            'byte_substitution': 'Replace bytes with alternative values',
            'dct_transform': 'Apply Discrete Cosine Transform',
            'lz77_encode': 'Apply LZ77 compression encoding',
            'huffman_encode': 'Apply Huffman encoding'
        }
        return descriptions.get(operation, 'Unknown operation')

    def _get_operation_complexity(self, operation: str) -> Dict[str, float]:
        """Get complexity metrics for operation."""
        complexity_data = {
            'bit_flip': {'time_complexity': 1.0, 'space_complexity': 1.0},
            'byte_substitution': {'time_complexity': 1.0, 'space_complexity': 1.0},
            'dct_transform': {'time_complexity': 8.0, 'space_complexity': 4.0},
            'lz77_encode': {'time_complexity': 16.0, 'space_complexity': 2.0},
            'huffman_encode': {'time_complexity': 12.0, 'space_complexity': 3.0}
        }
        return complexity_data.get(operation, {'time_complexity': 1.0, 'space_complexity': 1.0})
```

### Cost Model Configuration

Create configuration file: `config/costs/cost_my_custom_cost_model.yaml`

```yaml
# My Custom Cost Model Configuration
name: "My Custom Cost Model"
description: "Context-aware dynamic cost calculation"

# Base costs for operations
base_costs:
  bit_flip: 1.0
  byte_substitution: 2.0
  dct_transform: 5.0
  lz77_encode: 3.0
  huffman_encode: 4.0
  rle_encode: 2.0
  delta_encoding: 1.5

# Dynamic cost factors
dynamic_factors:
  context_aware: true                # Enable context-aware costing
  history_window: 50               # Operations to consider for context
  learning_rate: 0.01              # Rate of model adaptation
  frequency_penalty: 2.0            # Penalty multiplier for frequent operations
  novelty_bonus: 1.5              # Bonus multiplier for novel operations

# Operation complexity data
complexity_adjustments:
  dct_transform: 1.2              # Complexity multiplier for DCT
  lz77_encode: 1.0                # Complexity multiplier for LZ77
  huffman_encode: 0.8              # Complexity multiplier for Huffman

# Context awareness settings
context_factors:
  operation_diversity_bonus: 0.1     # Bonus for diverse operation usage
  convergence_penalty: 1.1           # Penalty when operations converge
  local_optimization_penalty: 1.2    # Penalty for local search patterns
```

---

## Creating Custom Metrics

### Metric Template

Create a new file: `bsee/metrics/my_custom_metric.py`

```python
"""
Custom Metric Example
Implements novel binary analysis metric.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats
import struct

@dataclass
class MetricConfig:
    """Configuration for custom metric."""
    name: str
    description: str
    parameters: Dict[str, Any]
    normalization: Dict[str, Any]

class MyCustomMetric:
    """Custom metric for advanced binary analysis."""

    def __init__(self, config_path: str):
        """
        Initialize metric with configuration.

        Args:
            config_path: Path to metric configuration
        """
        self.config = self._load_config(config_path)
        self.name = self.config.name
        self.description = self.config.description

    def _load_config(self, config_path: str) -> MetricConfig:
        """Load metric configuration."""
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        return MetricConfig(**config_data)

    def calculate(self, binary_data: bytes, **kwargs) -> float:
        """
        Calculate custom metric value.

        Args:
            binary_data: Binary data to analyze
            **kwargs: Additional calculation parameters

        Returns:
            Metric value
        """
        if not binary_data:
            return 0.0

        # Convert to numpy array for analysis
        data_array = np.frombuffer(binary_data, dtype=np.uint8)

        # Calculate custom metric based on configuration
        metric_type = self.config.parameters.get('type', 'entropy_analysis')

        if metric_type == 'entropy_analysis':
            return self._calculate_entropy_analysis(data_array)
        elif metric_type == 'pattern_analysis':
            return self._calculate_pattern_analysis(data_array)
        elif metric_type == 'structural_analysis':
            return self._calculate_structural_analysis(data_array)
        else:
            return self._calculate_default_metric(data_array)

    def _calculate_entropy_analysis(self, data: np.ndarray) -> float:
        """Calculate advanced entropy-based metric."""
        # Calculate byte frequency distribution
        byte_counts = np.bincount(data, minlength=256)
        byte_probs = byte_counts / len(data)

        # Shannon entropy
        entropy = -np.sum(byte_probs * np.log2(byte_probs + 1e-10))

        # Calculate entropy gradients (local complexity)
        window_size = self.config.parameters.get('window_size', 8)
        entropy_gradients = []

        for i in range(len(data) - window_size + 1):
            window = data[i:i + window_size]
            window_counts = np.bincount(window, minlength=256)
            window_probs = window_counts / window_size
            window_entropy = -np.sum(window_probs * np.log2(window_probs + 1e-10))
            entropy_gradients.append(window_entropy)

        # Calculate entropy variance (higher = more complex)
        entropy_variance = np.var(entropy_gradients) if len(entropy_gradients) > 1 else 0

        # Combine global and local entropy
        normalized_entropy = entropy / 8.0  # Normalize to [0, 1]
        normalized_variance = entropy_variance / 4.0  # Normalize variance

        # Weighted combination (adjust weights in config)
        entropy_weight = self.config.parameters.get('entropy_weight', 0.7)
        variance_weight = self.config.parameters.get('variance_weight', 0.3)

        final_score = entropy_weight * normalized_entropy + variance_weight * normalized_variance

        return float(final_score)

    def _calculate_pattern_analysis(self, data: np.ndarray) -> float:
        """Calculate pattern-based metric."""
        pattern_length = self.config.parameters.get('pattern_length', 4)

        # Calculate n-gram patterns
        patterns = {}
        for i in range(len(data) - pattern_length + 1):
            pattern = tuple(data[i:i + pattern_length])
            patterns[pattern] = patterns.get(pattern, 0) + 1

        # Calculate pattern diversity (higher = less predictable)
        pattern_values = list(patterns.values())
        pattern_entropy = stats.entropy(pattern_values)

        # Normalize to [0, 1] range
        max_possible_entropy = np.log2(min(256, len(pattern_values) + 1))
        normalized_entropy = pattern_entropy / max_possible_entropy

        return float(normalized_entropy)

    def _calculate_structural_analysis(self, data: np.ndarray) -> float:
        """Calculate structural complexity metric."""
        # Analyze byte-level patterns
        transitions = np.zeros((256, 256), dtype=int)

        for i in range(len(data) - 1):
            current_byte = data[i]
            next_byte = data[i + 1]
            transitions[current_byte, next_byte] += 1

        # Calculate transition entropy
        transition_probs = transitions / np.sum(transitions)
        transition_entropy = -np.sum(transition_probs * np.log2(transition_probs + 1e-10))

        # Normalize to [0, 1] range
        normalized_transition_entropy = transition_entropy / 8.0

        return float(normalized_transition_entropy)

    def _calculate_default_metric(self, data: np.ndarray) -> float:
        """Default metric calculation."""
        # Simple byte distribution uniformity
        byte_counts = np.bincount(data, minlength=256)
        byte_probs = byte_counts / len(data)

        # Calculate Chi-squared statistic for uniformity
        expected_count = len(data) / 256
        chi_squared = np.sum((byte_counts - expected_count) ** 2 / expected_count)

        # Convert to [0, 1] scale (lower chi-squared = more uniform)
        normalized_score = 1.0 - (chi_squared / (len(data) * 255))

        return float(normalized_score)

    def get_metric_info(self) -> Dict[str, Any]:
        """Get information about this metric."""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.config.parameters.get('type', 'entropy_analysis'),
            'range': '[0.0, 1.0]',
            'higher_is_better': self.config.normalization.get('higher_is_better', True)
        }
```

### Metric Configuration

Create configuration file: `config/metrics/metric_my_custom_metric.yaml`

```yaml
# My Custom Metric Configuration
name: "My Custom Metric"
description: "Advanced entropy and pattern analysis metric"

# Metric type
parameters:
  type: "entropy_analysis"           # Options: entropy_analysis, pattern_analysis, structural_analysis

  # Entropy analysis parameters
  entropy_weight: 0.7                 # Weight for global entropy
  variance_weight: 0.3                 # Weight for entropy variance
  window_size: 8                       # Window size for local entropy

  # Pattern analysis parameters
  pattern_length: 4                    # Length of patterns to analyze
  min_pattern_frequency: 2              # Minimum frequency for pattern significance

# Normalization settings
normalization:
  higher_is_better: true              # Whether higher values are better
  target_range: "[0.0, 1.0]"        # Target value range
  scaling_method: "min_max"            # Scaling: min_max, z_score, none

# Advanced options
cache_results: true                  # Cache expensive calculations
  parallel_computation: false          # Use parallel computation
  precision: "float32"                # Computation precision
```

---

## Creating Custom Operations

### Operation Template

Create a new file: `bsee/operations/my_custom_operation.py`

```python
"""
Custom Operation Example
Implements reversible binary transformation.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class OperationConfig:
    """Configuration for custom operation."""
    name: str
    description: str
    parameters: Dict[str, Any]
    reversibility: bool

class MyCustomOperation:
    """Custom reversible binary operation."""

    def __init__(self, config_path: str):
        """
        Initialize operation with configuration.

        Args:
            config_path: Path to operation configuration
        """
        self.config = self._load_config(config_path)
        self.name = self.config.name

    def _load_config(self, config_path: str) -> OperationConfig:
        """Load operation configuration."""
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        return OperationConfig(**config_data)

    def __call__(self, binary_data: bytes, **kwargs) -> Tuple[bytes, callable, Dict[str, Any]]:
        """
        Apply custom operation to binary data.

        Args:
            binary_data: Input binary data
            **kwargs: Operation-specific parameters

        Returns:
            Tuple of (new_binary_data, inverse_function, metadata)
        """
        if not binary_data:
            return binary_data, lambda x: x, {}

        # Apply transformation based on operation type
        operation_type = self.config.parameters.get('type', 'adaptive_filter')

        if operation_type == 'adaptive_filter':
            return self._adaptive_filter(binary_data, **kwargs)
        elif operation_type == 'frequency_substitution':
            return self._frequency_substitution(binary_data, **kwargs)
        elif operation_type == 'bit_level_transform':
            return self._bit_level_transform(binary_data, **kwargs)
        else:
            return self._default_transformation(binary_data, **kwargs)

    def _adaptive_filter(self, data: bytes, **kwargs) -> Tuple[bytes, callable, Dict[str, Any]]:
        """Apply adaptive filtering operation."""
        # Convert to numpy array
        data_array = np.frombuffer(data, dtype=np.uint8)

        # Get parameters
        filter_type = kwargs.get('filter_type', 'gaussian')
        kernel_size = kwargs.get('kernel_size', 3)
        strength = kwargs.get('strength', 1.0)

        # Create filter kernel
        if filter_type == 'gaussian':
            kernel = self._create_gaussian_kernel(kernel_size, strength)
        elif filter_type == 'median':
            kernel = self._create_median_kernel(kernel_size)
        elif filter_type == 'edge_detection':
            kernel = self._create_edge_detection_kernel(strength)
        else:
            kernel = self._create_mean_kernel(kernel_size)

        # Apply convolution
        filtered_data = self._apply_convolution(data_array, kernel)

        # Create inverse function
        def inverse_function(original_data: bytes) -> bytes:
            original_array = np.frombuffer(original_data, dtype=np.uint8)
            # Inverse filtering (deconvolution)
            recovered_data = self._apply_deconvolution(filtered_data, kernel)
            return recovered_data.tobytes()

        # Metadata
        metadata = {
            'filter_type': filter_type,
            'kernel_size': kernel_size,
            'strength': strength,
            'operation': 'adaptive_filter',
            'reversible': True
        }

        return filtered_data.tobytes(), inverse_function, metadata

    def _frequency_substitution(self, data: bytes, **kwargs) -> Tuple[bytes, callable, Dict[str, Any]]:
        """Apply frequency-based byte substitution."""
        data_array = np.frombuffer(data, dtype=np.uint8)

        # Get parameters
        frequency_table = kwargs.get('frequency_table', 'ascii_common')
        substitution_map = kwargs.get('substitution_map', {})

        # Generate frequency table
        if frequency_table == 'ascii_common':
            # Common ASCII characters frequency
            ascii_common = b'etaoinshrdlucmfpw,.,?!'  # Most common ASCII
            freq_table = {byte: i for i, byte in enumerate(ascii_common)}
        elif frequency_table == 'binary_analysis':
            # Analyze frequency in current data
            unique, counts = np.unique(data_array, return_counts=True)
            frequencies = counts / len(data_array)
            freq_table = {byte: freq for byte, freq in zip(unique, frequencies)}
        else:
            freq_table = substitution_map

        # Apply substitution
        substitution_table = {}
        for byte_val in range(256):
            substitution_table[byte_val] = self._find_substitute(byte_val, freq_table)

        # Apply substitution
        substituted_data = np.vectorize(lambda x: substitution_table[x])(data_array)

        # Create inverse function
        def inverse_function(original_data: bytes) -> bytes:
            original_array = np.frombuffer(original_data, dtype=np.uint8)
            reverse_table = {v: k for k, v in substitution_table.items()}
            recovered_data = np.vectorize(lambda x: reverse_table[x])(original_array)
            return recovered_data.tobytes()

        # Metadata
        metadata = {
            'operation': 'frequency_substitution',
            'frequency_table': frequency_table,
            'unique_substitutions': len(set(substitution_table.values())),
            'reversible': True
        }

        return substituted_data.tobytes(), inverse_function, metadata

    def _bit_level_transform(self, data: bytes, **kwargs) -> Tuple[bytes, callable, Dict[str, Any]]:
        """Apply bit-level transformation."""
        data_array = np.frombuffer(data, dtype=np.uint8)

        # Get parameters
        transform_type = kwargs.get('transform_type', 'bit_permutation')
        bit_positions = kwargs.get('bit_positions', [7, 6, 5, 4, 3, 2, 1, 0])  # MSB to LSB

        if transform_type == 'bit_permutation':
            # Permute specified bit positions
            permutation = kwargs.get('permutation', [0, 1, 2, 3, 4, 5, 6, 7])
            transformed_data = self._apply_bit_permutation(data_array, bit_positions, permutation)
        elif transform_type == 'bit_inversion':
            # Invert specified bits
            inverted_bits = kwargs.get('bits_to_invert', [0, 1])
            transformed_data = self._apply_bit_inversion(data_array, inverted_bits)
        elif transform_type == 'bit_rotation':
            # Rotate bits within bytes
            rotate_bits = kwargs.get('bits_to_rotate', 2)
            transformed_data = self._apply_bit_rotation(data_array, bit_positions, rotate_bits)
        else:
            # Default to no transformation
            transformed_data = data_array.copy()

        # Create inverse function
        def inverse_function(original_data: bytes) -> bytes:
            original_array = np.frombuffer(original_data, dtype=np.uint8)
            if transform_type == 'bit_permutation':
                reverse_permutation = np.argsort(kwargs.get('permutation', [0, 1, 2, 3, 4, 5, 6, 7]))
                recovered_data = self._apply_bit_permutation(original_array, bit_positions, reverse_permutation)
            elif transform_type == 'bit_inversion':
                recovered_data = self._apply_bit_inversion(original_array, inverted_bits)
            elif transform_type == 'bit_rotation':
                recovered_data = self._apply_bit_rotation(original_array, bit_positions, -rotate_bits)
            else:
                recovered_data = original_array.copy()
            return recovered_data.tobytes()

        # Metadata
        metadata = {
            'transform_type': transform_type,
            'bit_positions': bit_positions,
            'operation': 'bit_level_transform',
            'reversible': True
        }

        return transformed_data.tobytes(), inverse_function, metadata

    def _default_transformation(self, data: bytes, **kwargs) -> Tuple[bytes, callable, Dict[str, Any]]:
        """Default simple transformation."""
        # Simple byte complement
        data_array = np.frombuffer(data, dtype=np.uint8)
        transformed_data = ~data_array

        def inverse_function(original_data: bytes) -> bytes:
            original_array = np.frombuffer(original_data, dtype=np.uint8)
            return (~original_array).tobytes()

        return transformed_data.tobytes(), inverse_function, {
            'operation': 'bit_complement',
            'reversible': True
        }

    def _create_gaussian_kernel(self, size: int, strength: float) -> np.ndarray:
        """Create Gaussian blur kernel."""
        kernel = np.zeros((size, size), dtype=np.float32)
        center = size // 2

        for i in range(size):
            for j in range(size):
                x, y = i - center, j - center
                kernel[i, j] = np.exp(-(x*x + y*y) / (2 * strength * strength))

        return kernel / np.sum(kernel)

    def _create_median_kernel(self, size: int) -> np.ndarray:
        """Create median filter kernel."""
        kernel = np.ones((size, size), dtype=np.float32) / (size * size)
        return kernel

    def _create_edge_detection_kernel(self, strength: float) -> np.ndarray:
        """Create edge detection kernel."""
        kernel = np.array([
            [-1, -1, -1],
            [-1,  8, -1],
            [-1, -1, -1]
        ], dtype=np.float32) * strength

        return kernel

    def _create_mean_kernel(self, size: int) -> np.ndarray:
        """Create mean filter kernel."""
        kernel = np.ones((size, size), dtype=np.float32) / (size * size)
        return kernel

    def _apply_convolution(self, data: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Apply convolution to data."""
        # Pad data for convolution
        pad_size = kernel.shape[0] // 2
        padded_data = np.pad(data, pad_size, mode='reflect')

        # Apply convolution
        from scipy.signal import convolve2d
        if len(data.shape) == 1:
            convolved = convolve2d([data], kernel, mode='same')
        else:
            # Handle 2D data if necessary
            convolved = convolve2d([data], kernel, mode='same')

        # Convert back to uint8
        return np.clip(convolved[0], 0, 255).astype(np.uint8)

    def _apply_deconvolution(self, data: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Apply deconvolution for recovery."""
        # Simplified deconvolution (actual implementation would be more complex)
        return data  # Placeholder - real implementation needed

    def _apply_bit_permutation(self, data: np.ndarray, bit_positions: List[int],
                           permutation: List[int]) -> np.ndarray:
        """Apply bit permutation to data."""
        result = data.copy()

        for bit_pos in bit_positions:
            # Extract bits
            bits = (data >> bit_pos) & 1

            # Permute bits
            for i, bit_val in enumerate(bits):
                if i < len(permutation):
                    bits[i] = permutation[bit_val]

            # Reassemble bits
            for i, bit_val in enumerate(bits):
                result[i] = (result[i] & ~(1 << bit_pos)) | (bit_val << bit_pos)

        return result

    def _apply_bit_inversion(self, data: np.ndarray, bits_to_invert: List[int]) -> np.ndarray:
        """Apply bit inversion."""
        result = data.copy()

        for bit_pos in bits_to_invert:
            result ^= (1 << bit_pos)

        return result

    def _apply_bit_rotation(self, data: np.ndarray, bit_positions: List[int],
                          rotate_bits: int) -> np.ndarray:
        """Apply bit rotation."""
        result = data.copy()

        for bit_pos in bit_positions:
            # Extract and rotate bits
            bits = (data >> bit_pos) & 1

            # Rotate left by specified amount
            rotated_bits = [(bits >> i) & 1 for i in range(rotate_bits)] + [bits >> (rotate_bits - 1) & 1]

            # Reassemble bits
            for i, bit_val in enumerate(rotated_bits):
                result[i] = (result[i] & ~(1 << bit_pos)) | (bit_val << bit_pos)

        return result

    def _find_substitute(self, byte_val: int, freq_table: Dict[int, float]) -> int:
        """Find substitute byte based on frequency."""
        if not freq_table:
            return byte_val

        # Sort by frequency (ascending - least frequent first)
        sorted_bytes = sorted(freq_table.keys(), key=lambda x: freq_table[x])

        # Find least frequent byte different from current
        for candidate in sorted_bytes:
            if candidate != byte_val:
                return candidate

        return byte_val  # Fallback to original

    def get_operation_info(self) -> Dict[str, Any]:
        """Get information about this operation."""
        return {
            'name': self.name,
            'description': self.config.description,
            'reversible': self.config.reversibility,
            'parameters': self.config.parameters,
            'input_types': ['bytes'],
            'output_types': ['bytes']
        }
```

### Operation Configuration

Create configuration file: `config/operations/operation_my_custom_operation.yaml`

```yaml
# My Custom Operation Configuration
name: "My Custom Operation"
description: "Advanced reversible transformations with multiple modes"

# Operation parameters
parameters:
  type: "adaptive_filter"           # Options: adaptive_filter, frequency_substitution, bit_level_transform

  # Adaptive filter parameters
  default_filter_type: "gaussian"     # gaussian, median, edge_detection, mean
  default_kernel_size: 3               # Filter kernel size
  default_strength: 1.0                # Filter strength

  # Frequency substitution parameters
  default_frequency_table: "ascii_common"  # ascii_common, binary_analysis, custom
  default_substitution_map: {}         # Custom substitution map

  # Bit-level transform parameters
  default_transform_type: "bit_permutation"  # bit_permutation, bit_inversion, bit_rotation
  default_bit_positions: [7,6,5,4,3,2,1,0]  # MSB to LSB
  default_permutation: [0,1,2,3,4,5,6,7]     # Bit permutation
  default_bits_to_invert: [0,1]          # Bits to invert
  default_bits_to_rotate: 2              # Number of bits to rotate

# Operation properties
reversibility: true                    # Whether operation is reversible
deterministic: false                   # Whether operation has random elements
parallel_capable: true                # Can be parallelized
memory_intensive: false                # Whether operation uses significant memory

# Performance settings
cache_intermediate: false              # Cache intermediate results
vectorized_computation: true          # Use numpy vectorization
batch_processing: true                # Process data in batches
```

---

## Configuration System

### Configuration File Structure

All configuration files use YAML format and follow this structure:

```yaml
# Metadata
name: "Configuration Name"
description: "Human-readable description"
version: "1.0.0"
author: "Your Name"

# Core parameters
parameters:
  # Parameter definitions
  parameter_name: "default_value"

# Validation rules
validation:
  required_parameters: ["param1", "param2"]
  parameter_ranges:
    parameter_name:
      min: 0
      max: 100
      type: "integer"

# Default settings
defaults:
  log_level: "INFO"
  output_format: "json"
  max_iterations: 1000
```

### Configuration Loading

```python
from pathlib import Path
import yaml
from typing import Dict, Any

class ConfigManager:
    """Manages BSEE configuration loading and validation."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)

    def load_config(self, config_type: str, config_name: str) -> Dict[str, Any]:
        """Load configuration file."""
        config_path = self.config_dir / config_type / f"{config_name}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        self._validate_config(config, config_type)
        return config

    def _validate_config(self, config: Dict[str, Any], config_type: str) -> None:
        """Validate configuration structure."""
        required_sections = {
            'strategy': ['name', 'description'],
            'policy': ['target_metrics', 'constraints'],
            'cost': ['base_costs'],
            'metric': ['name', 'parameters']
        }

        if config_type in required_sections:
            required = required_sections[config_type]
            for section in required:
                if section not in config:
                    raise ValueError(f"Missing required section '{section}' in {config_type} config")
```

---

## Testing and Validation

### Unit Testing Template

```python
import unittest
import numpy as np
from typing import Dict, Any

class TestMyCustomStrategy(unittest.TestCase):
    """Test suite for custom strategy."""

    def setUp(self):
        """Set up test environment."""
        self.config = {
            'exploration_rate': 0.1,
            'convergence_threshold': 0.001,
            'max_iterations': 100
        }
        self.strategy = MyCustomStrategy(self.config)

    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.name, "my_custom_strategy")
        self.assertEqual(self.strategy.exploration_rate, 0.1)

    def test_proposal_generation(self):
        """Test operation proposal generation."""
        from bsee.engine.state import State

        # Create mock state
        mock_state = State(binary_data=b"test_binary_data_here")

        # Test proposal generation
        operation, params = self.strategy.propose(mock_state)

        # Validate proposal structure
        self.assertIsInstance(operation, str)
        self.assertIsInstance(params, dict)

    def test_convergence_detection(self):
        """Test convergence detection."""
        self.strategy.iteration_count = 1000
        self.assertTrue(self.strategy.is_converged())

        self.strategy.iteration_count = 500
        self.assertFalse(self.strategy.is_converged())

class TestMyCustomMetric(unittest.TestCase):
    """Test suite for custom metric."""

    def setUp(self):
        """Set up test environment."""
        self.config = {
            'type': 'entropy_analysis',
            'entropy_weight': 0.7,
            'variance_weight': 0.3
            'window_size': 8
        }
        self.metric = MyCustomMetric("test_config.yaml")

    def test_entropy_calculation(self):
        """Test entropy calculation."""
        # Test uniform data (entropy should be 8.0)
        uniform_data = bytes(range(256))
        entropy = self.metric.calculate(uniform_data)

        # Uniform data should have maximum entropy (8.0)
        self.assertAlmostEqual(entropy, 8.0, places=2)

    def test_calculation_range(self):
        """Test metric value range."""
        # Test with all zeros (entropy = 0)
        zero_data = bytes([0] * 100)
        zero_entropy = self.metric.calculate(zero_data)
        self.assertEqual(zero_entropy, 0.0)

        # Test with uniform data (entropy = 1.0 after normalization)
        uniform_data = bytes(range(256))
        uniform_entropy = self.metric.calculate(uniform_data)
        self.assertAlmostEqual(uniform_entropy, 1.0, places=2)
```

### Integration Testing

```python
import tempfile
from pathlib import Path

class IntegrationTestCase:
    """Integration tests for custom components."""

    def test_strategy_integration(self):
        """Test strategy integration with pipeline."""
        from bsee.engine.pipeline import Pipeline

        # Create temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
name: "test_strategy"
description: "Test strategy"
exploration_rate: 0.1
""")
            config_path = f.name

        # Test strategy loading
        args = self._create_test_args()
        pipeline = Pipeline(args)

        # Verify strategy was loaded
        self.assertIsNotNone(pipeline.strategy)

    def test_end_to_end_workflow(self):
        """Test complete workflow."""
        # Create test binary
        test_binary = bytes([0x48, 0x45, 0x4C, 0x4C, 0x4F, 0x20, 0x57, 0x6F, 0x72, 0x6C, 0x61, 0x64])

        # Run complete optimization
        args = self._create_test_args()
        args.input_file = self._create_temp_file(test_binary)

        pipeline = Pipeline(args)
        results = pipeline.run()

        # Validate results
        self.assertTrue(results.success)
        self.assertIsNotNone(results.final_state)
        self.assertGreater(results.total_operations, 0)
```

---

## Best Practices

### Code Organization

1. **File Structure**: Follow the established directory structure
2. **Naming Conventions**: Use descriptive names and consistent patterns
3. **Documentation**: Document all functions and classes thoroughly
4. **Type Hints**: Use Python type hints for better IDE support
5. **Error Handling**: Implement comprehensive error handling

### Performance Considerations

1. **Vectorization**: Use numpy operations instead of loops when possible
2. **Memory Management**: Process large files in chunks
3. **Caching**: Cache expensive computations
4. **Parallel Processing**: Use threading/multiprocessing for independent tasks

### Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Performance Tests**: Measure and optimize critical paths
4. **Edge Cases**: Test with various binary file types and sizes

### Configuration Management

1. **Validation**: Validate all configuration inputs
2. **Default Values**: Provide sensible defaults
3. **Backward Compatibility**: Maintain compatibility with older configs
4. **Documentation**: Document all configuration options

### Security Considerations

1. **Input Validation**: Validate all inputs and sanitize paths
2. **Resource Limits**: Implement resource usage limits
3. **Error Information**: Don't expose sensitive information in error messages
4. **File Operations**: Use secure file handling practices

---

## Deployment

### Distribution

1. **Package Structure**: Organize files for easy distribution
2. **Dependencies**: Clear list of required dependencies
3. **Installation**: Provide installation scripts and documentation
4. **Configuration**: Include example configurations

### Version Management

1. **Semantic Versioning**: Use semantic versioning (MAJOR.MINOR.PATCH)
2. **Changelog**: Maintain detailed changelog
3. **Compatibility**: Document breaking changes
4. **Migration**: Provide migration guides for major updates

---

This guide provides a comprehensive foundation for creating custom BSEE components. Each section includes working examples, configuration templates, and testing strategies to ensure robust, production-ready implementations.