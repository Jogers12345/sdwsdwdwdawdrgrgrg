"""
Multi-Objective Cost Model for BSEE
Balances multiple cost dimensions: computational, memory, time, and quality
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import json
from pathlib import Path
import time
from enum import Enum
from dataclasses import dataclass

from bsee.cost.cost_model import CostModel
from bsee.engine.state import State


class CostDimension(Enum):
    """Different cost dimensions to consider"""
    COMPUTATIONAL = "computational"
    MEMORY = "memory"
    TIME = "time"
    QUALITY = "quality"
    RESOURCE = "resource"


@dataclass
class CostWeights:
    """Weights for different cost dimensions"""
    computational: float = 0.3
    memory: float = 0.2
    time: float = 0.2
    quality: float = 0.2
    resource: float = 0.1

    def normalize(self):
        """Normalize weights to sum to 1.0"""
        total = sum([self.computational, self.memory, self.time, self.quality, self.resource])
        if total > 0:
            self.computational /= total
            self.memory /= total
            self.time /= total
            self.quality /= total
            self.resource /= total


class MultiObjectiveCostModel(CostModel):
    """
    Multi-objective cost model that considers multiple cost dimensions
    and provides Pareto-optimal solutions for operation selection.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Cost weights
        weights_config = config.get('weights', {})
        self.weights = CostWeights(
            computational=weights_config.get('computational', 0.3),
            memory=weights_config.get('memory', 0.2),
            time=weights_config.get('time', 0.2),
            quality=weights_config.get('quality', 0.2),
            resource=weights_config.get('resource', 0.1)
        )
        self.weights.normalize()

        # Dimension-specific cost functions
        self.computational_costs = self._initialize_computational_costs()
        self.memory_costs = self._initialize_memory_costs()
        self.time_costs = self._initialize_time_costs()
        self.quality_costs = self._initialize_quality_costs()
        self.resource_costs = self._initialize_resource_costs()

        # Optimization parameters
        self.optimization_mode = config.get('optimization_mode', 'weighted_sum')
        self.pareto_epsilon = config.get('pareto_epsilon', 0.01)
        self.constraint_mode = config.get('constraint_mode', 'soft')

        # Performance tracking
        self.dimension_history = {dim: [] for dim in CostDimension}
        self.pareto_solutions = []
        self.constraint_violations = []

        # Adaptive parameters
        self.adaptive_learning = config.get('adaptive_learning', True)
        self.learning_rate = config.get('learning_rate', 0.05)
        self.performance_window = config.get('performance_window', 50)

    def _initialize_computational_costs(self) -> Dict[str, float]:
        """Initialize computational cost base values"""
        return {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 2.0,
            'reverse': 3.0,
            'substitute': 5.0,
            'compress': 15.0,
            'decompress': 20.0,
            'transpose': 8.0,
            'bit_swap': 4.0,
            'pattern_match': 12.0,
            'entropy_encode': 18.0
        }

    def _initialize_memory_costs(self) -> Dict[str, float]:
        """Initialize memory cost base values (per KB)"""
        return {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 1.0,
            'reverse': 1.0,
            'substitute': 1.5,
            'compress': 0.3,  # Compression reduces memory
            'decompress': 2.5,  # Decompression increases memory
            'transpose': 2.0,
            'bit_swap': 1.0,
            'pattern_match': 3.0,
            'entropy_encode': 2.0
        }

    def _initialize_time_costs(self) -> Dict[str, float]:
        """Initialize time cost base values (per KB)"""
        return {
            'xor': 0.01,
            'add': 0.01,
            'sub': 0.01,
            'rotate': 0.02,
            'reverse': 0.01,
            'substitute': 0.05,
            'compress': 0.2,
            'decompress': 0.3,
            'transpose': 0.08,
            'bit_swap': 0.03,
            'pattern_match': 0.15,
            'entropy_encode': 0.25
        }

    def _initialize_quality_costs(self) -> Dict[str, float]:
        """Initialize quality impact costs (negative = quality improvement)"""
        return {
            'xor': 0.1,
            'add': 0.1,
            'sub': 0.1,
            'rotate': 0.05,
            'reverse': 0.02,
            'substitute': 0.15,
            'compress': -0.5,  # Compression improves quality
            'decompress': -0.3,
            'transpose': 0.08,
            'bit_swap': 0.12,
            'pattern_match': -0.4,
            'entropy_encode': -0.6
        }

    def _initialize_resource_costs(self) -> Dict[str, float]:
        """Initialize resource utilization costs"""
        return {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 1.2,
            'reverse': 1.0,
            'substitute': 1.8,
            'compress': 3.0,
            'decompress': 4.0,
            'transpose': 2.2,
            'bit_swap': 1.3,
            'pattern_match': 2.8,
            'entropy_encode': 3.5
        }

    def calculate_dimensional_cost(self, dimension: CostDimension, operation: str,
                                  state: State, parameters: Dict[str, Any] = None) -> float:
        """Calculate cost for specific dimension"""
        data_size_kb = len(state.data) / 1024.0 if state.data else 0.001

        if dimension == CostDimension.COMPUTATIONAL:
            return self._calculate_computational_cost(operation, state, parameters)
        elif dimension == CostDimension.MEMORY:
            return self._calculate_memory_cost(operation, data_size_kb, parameters)
        elif dimension == CostDimension.TIME:
            return self._calculate_time_cost(operation, data_size_kb, parameters)
        elif dimension == CostDimension.QUALITY:
            return self._calculate_quality_cost(operation, state, parameters)
        elif dimension == CostDimension.RESOURCE:
            return self._calculate_resource_cost(operation, data_size_kb, parameters)
        else:
            return 1.0

    def _calculate_computational_cost(self, operation: str, state: State,
                                    parameters: Dict[str, Any]) -> float:
        """Calculate computational complexity cost"""
        base_cost = self.computational_costs.get(operation, 1.0)

        # Adjust for data characteristics
        data_size_factor = 1.0 + (len(state.data) / 100000.0)  # Scale with data size

        # Adjust for operation complexity based on parameters
        parameter_factor = self._get_computational_parameter_factor(operation, parameters)

        # Adjust for data entropy (more complex data = higher cost)
        entropy = self._calculate_entropy(state.data)
        entropy_factor = 1.0 + entropy

        return base_cost * data_size_factor * parameter_factor * entropy_factor

    def _calculate_memory_cost(self, operation: str, data_size_kb: float,
                             parameters: Dict[str, Any]) -> float:
        """Calculate memory usage cost"""
        base_cost = self.memory_costs.get(operation, 1.0)

        # Adjust for parameter memory requirements
        parameter_factor = self._get_memory_parameter_factor(operation, parameters)

        # Consider temporary memory needs
        temp_memory_factor = self._get_temp_memory_factor(operation, parameters)

        return base_cost * data_size_kb * parameter_factor * temp_memory_factor

    def _calculate_time_cost(self, operation: str, data_size_kb: float,
                           parameters: Dict[str, Any]) -> float:
        """Calculate execution time cost"""
        base_cost = self.time_costs.get(operation, 0.01)

        # Adjust for operation complexity
        complexity_factor = self._get_time_complexity_factor(operation, parameters)

        # Adjust for system load (simplified)
        system_load_factor = 1.0  # Could be enhanced with actual system monitoring

        return base_cost * data_size_kb * complexity_factor * system_load_factor

    def _calculate_quality_cost(self, operation: str, state: State,
                              parameters: Dict[str, Any]) -> float:
        """Calculate quality impact cost (negative = improvement)"""
        base_cost = self.quality_costs.get(operation, 0.0)

        # Adjust based on expected quality improvement
        data_type_factor = self._get_quality_data_type_factor(operation, state.data)

        # Adjust for parameter quality impact
        parameter_factor = self._get_quality_parameter_factor(operation, parameters)

        return base_cost * data_type_factor * parameter_factor

    def _calculate_resource_cost(self, operation: str, data_size_kb: float,
                               parameters: Dict[str, Any]) -> float:
        """Calculate resource utilization cost"""
        base_cost = self.resource_costs.get(operation, 1.0)

        # CPU utilization
        cpu_factor = self._get_cpu_utilization_factor(operation, parameters)

        # I/O operations
        io_factor = self._get_io_factor(operation, parameters)

        # System call overhead
        syscall_factor = self._get_syscall_factor(operation, parameters)

        return base_cost * cpu_factor * io_factor * syscall_factor

    def _get_computational_parameter_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get computational parameter factor"""
        if not parameters:
            return 1.0

        if operation in ['xor', 'add', 'sub']:
            value = parameters.get('key') or parameters.get('value', 0)
            return 1.0 + (abs(value) / 255.0) * 0.2

        elif operation == 'rotate':
            bits = parameters.get('bits', 1)
            return bits / 4.0

        elif operation == 'substitute':
            pattern_len = len(parameters.get('pattern', b''))
            return 1.0 + (pattern_len / 16.0)

        return 1.0

    def _get_memory_parameter_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get memory parameter factor"""
        if not parameters:
            return 1.0

        if operation in ['compress', 'decompress']:
            level = parameters.get('level', 6)
            return 1.0 + (level / 9.0) * 0.5

        return 1.0

    def _get_temp_memory_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get temporary memory factor"""
        temp_multipliers = {
            'compress': 2.0,  # May need buffer for compression
            'decompress': 1.5,
            'transpose': 1.8,
            'pattern_match': 2.2,
            'entropy_encode': 2.5
        }

        return temp_multipliers.get(operation, 1.0)

    def _get_time_complexity_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get time complexity factor"""
        complexity_factors = {
            'xor': 1.0,      # O(n)
            'add': 1.0,      # O(n)
            'sub': 1.0,      # O(n)
            'rotate': 1.0,   # O(n)
            'reverse': 1.0,  # O(n)
            'substitute': 1.2,  # O(n*m) where m is pattern length
            'compress': 2.0,   # O(n log n)
            'decompress': 2.5, # O(n log n)
            'transpose': 1.5,  # O(n*m)
            'pattern_match': 3.0,  # O(n*m)
            'entropy_encode': 2.8  # O(n log n)
        }

        return complexity_factors.get(operation, 1.0)

    def _get_quality_data_type_factor(self, operation: str, data: bytes) -> float:
        """Get quality factor based on data type"""
        if not data:
            return 1.0

        entropy = self._calculate_entropy(data)
        pattern_density = self._calculate_pattern_density(data)

        if operation in ['compress', 'entropy_encode']:
            # Compression operations work better on low entropy, high pattern density
            return 1.0 + (1.0 - entropy) * 0.5 + pattern_density * 0.3

        elif operation in ['xor', 'add', 'sub']:
            # Simple operations have consistent quality impact
            return 1.0

        return 1.0

    def _get_quality_parameter_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get quality parameter factor"""
        if not parameters:
            return 1.0

        if operation in ['compress', 'decompress']:
            level = parameters.get('level', 6)
            return level / 6.0  # Higher compression level = better quality

        return 1.0

    def _get_cpu_utilization_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get CPU utilization factor"""
        cpu_factors = {
            'xor': 0.8,
            'add': 0.8,
            'sub': 0.8,
            'rotate': 1.0,
            'reverse': 0.9,
            'substitute': 1.2,
            'compress': 2.0,
            'decompress': 2.5,
            'transpose': 1.5,
            'pattern_match': 2.2,
            'entropy_encode': 2.8
        }

        return cpu_factors.get(operation, 1.0)

    def _get_io_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get I/O factor"""
        io_factors = {
            'compress': 1.5,   # May write compressed data
            'decompress': 1.8, # May read compressed data
            'pattern_match': 1.2,
            'entropy_encode': 1.3
        }

        return io_factors.get(operation, 1.0)

    def _get_syscall_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Get system call overhead factor"""
        syscall_factors = {
            'compress': 1.2,
            'decompress': 1.3,
            'transpose': 1.1,
            'pattern_match': 1.1
        }

        return syscall_factors.get(operation, 1.0)

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate normalized entropy"""
        if not data:
            return 0.0

        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1

        entropy = 0.0
        data_len = len(data)

        for count in byte_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)

        return entropy / 8.0

    def _calculate_pattern_density(self, data: bytes) -> float:
        """Calculate pattern density"""
        if len(data) < 4:
            return 0.0

        patterns = set()
        for i in range(len(data) - 3):
            pattern = data[i:i+4]
            patterns.add(pattern)

        return 1.0 - (len(patterns) / (len(data) - 3))

    def calculate_operation_cost(self, operation: str, state: State,
                                parameters: Dict[str, Any] = None) -> float:
        """Calculate multi-objective operation cost"""
        # Calculate costs for all dimensions
        costs = {}
        for dimension in CostDimension:
            costs[dimension.value] = self.calculate_dimensional_cost(dimension, operation, state, parameters)

        # Apply optimization method
        if self.optimization_mode == 'weighted_sum':
            total_cost = self._weighted_sum_cost(costs)
        elif self.optimization_mode == 'pareto_optimal':
            total_cost = self._pareto_optimal_cost(costs, operation)
        elif self.optimization_mode == 'constraint_based':
            total_cost = self._constraint_based_cost(costs, operation)
        else:
            total_cost = self._weighted_sum_cost(costs)

        # Store dimensional costs for analysis
        self.dimension_history[CostDimension.COMPUTATIONAL].append(costs['computational'])
        self.dimension_history[CostDimension.MEMORY].append(costs['memory'])
        self.dimension_history[CostDimension.TIME].append(costs['time'])
        self.dimension_history[CostDimension.QUALITY].append(costs['quality'])
        self.dimension_history[CostDimension.RESOURCE].append(costs['resource'])

        return total_cost

    def _weighted_sum_cost(self, costs: Dict[str, float]) -> float:
        """Calculate weighted sum of dimensional costs"""
        total_cost = (
            self.weights.computational * costs['computational'] +
            self.weights.memory * costs['memory'] +
            self.weights.time * costs['time'] +
            self.weights.quality * costs['quality'] +
            self.weights.resource * costs['resource']
        )
        return total_cost

    def _pareto_optimal_cost(self, costs: Dict[str, float], operation: str) -> float:
        """Calculate Pareto-optimal cost"""
        # Check if this solution is Pareto-optimal
        is_pareto = self._is_pareto_optimal(costs, operation)

        if is_pareto:
            self.pareto_solutions.append({
                'operation': operation,
                'costs': costs.copy(),
                'timestamp': time.time()
            })

        # For Pareto-optimal solutions, apply a discount
        pareto_discount = 0.9 if is_pareto else 1.0

        return self._weighted_sum_cost(costs) * pareto_discount

    def _constraint_based_cost(self, costs: Dict[str, float], operation: str) -> float:
        """Calculate constraint-based cost"""
        constraints = {
            'computational': 50.0,
            'memory': 100.0,
            'time': 10.0,
            'resource': 20.0
        }

        violations = []
        penalty = 0.0

        for dimension, limit in constraints.items():
            if costs[dimension] > limit:
                violations.append(dimension)
                if self.constraint_mode == 'hard':
                    return float('inf')  # Reject operation
                else:  # soft constraints
                    penalty += (costs[dimension] - limit) * 0.5

        if violations:
            self.constraint_violations.append({
                'operation': operation,
                'violations': violations,
                'costs': costs.copy(),
                'timestamp': time.time()
            })

        return self._weighted_sum_cost(costs) + penalty

    def _is_pareto_optimal(self, costs: Dict[str, float], operation: str) -> bool:
        """Check if solution is Pareto-optimal"""
        if not self.pareto_solutions:
            return True

        for solution in self.pareto_solutions[-20:]:  # Check against recent solutions
            other_costs = solution['costs']

            # Check if other solution dominates this one
            dominates = True
            for dimension in CostDimension:
                if other_costs[dimension.value] > costs[dimension.value] + self.pareto_epsilon:
                    dominates = False
                    break

            if dominates:
                return False

        return True

    def get_dimensional_analysis(self) -> Dict[str, Any]:
        """Get analysis of cost dimensions"""
        analysis = {}

        for dimension in CostDimension:
            history = self.dimension_history[dimension]
            if history:
                analysis[dimension.value] = {
                    'current': history[-1] if history else 0,
                    'average': np.mean(history),
                    'std_dev': np.std(history),
                    'min': min(history),
                    'max': max(history),
                    'trend': 'increasing' if len(history) > 1 and history[-1] > history[-10:] else 'stable'
                }
            else:
                analysis[dimension.value] = {
                    'current': 0,
                    'average': 0,
                    'std_dev': 0,
                    'min': 0,
                    'max': 0,
                    'trend': 'stable'
                }

        analysis['weights'] = {
            'computational': self.weights.computational,
            'memory': self.weights.memory,
            'time': self.weights.time,
            'quality': self.weights.quality,
            'resource': self.weights.resource
        }

        analysis['optimization_mode'] = self.optimization_mode
        analysis['pareto_solutions_count'] = len(self.pareto_solutions)
        analysis['constraint_violations_count'] = len(self.constraint_violations)

        return analysis

    def adapt_weights(self, performance_feedback: Dict[str, float]):
        """Adapt weights based on performance feedback"""
        if not self.adaptive_learning:
            return

        # Adjust weights based on which dimensions need improvement
        for dimension in CostDimension:
            dimension_name = dimension.value
            if dimension_name in performance_feedback:
                feedback = performance_feedback[dimension_name]

                # Get current weight
                if dimension == CostDimension.COMPUTATIONAL:
                    current_weight = self.weights.computational
                elif dimension == CostDimension.MEMORY:
                    current_weight = self.weights.memory
                elif dimension == CostDimension.TIME:
                    current_weight = self.weights.time
                elif dimension == CostDimension.QUALITY:
                    current_weight = self.weights.quality
                else:  # RESOURCE
                    current_weight = self.weights.resource

                # Adjust weight based on feedback
                if feedback < 0:  # Need to reduce cost in this dimension
                    adjustment = self.learning_rate * abs(feedback)
                else:  # Performance is good, can reduce weight
                    adjustment = -self.learning_rate * feedback * 0.1

                new_weight = current_weight + adjustment

                # Update weight
                if dimension == CostDimension.COMPUTATIONAL:
                    self.weights.computational = max(0.01, min(1.0, new_weight))
                elif dimension == CostDimension.MEMORY:
                    self.weights.memory = max(0.01, min(1.0, new_weight))
                elif dimension == CostDimension.TIME:
                    self.weights.time = max(0.01, min(1.0, new_weight))
                elif dimension == CostDimension.QUALITY:
                    self.weights.quality = max(0.01, min(1.0, new_weight))
                else:  # RESOURCE
                    self.weights.resource = max(0.01, min(1.0, new_weight))

        # Re-normalize weights
        self.weights.normalize()

    def save_model(self, filepath: str):
        """Save multi-objective cost model"""
        model_data = {
            'weights': {
                'computational': self.weights.computational,
                'memory': self.weights.memory,
                'time': self.weights.time,
                'quality': self.weights.quality,
                'resource': self.weights.resource
            },
            'computational_costs': self.computational_costs,
            'memory_costs': self.memory_costs,
            'time_costs': self.time_costs,
            'quality_costs': self.quality_costs,
            'resource_costs': self.resource_costs,
            'config': {
                'optimization_mode': self.optimization_mode,
                'pareto_epsilon': self.pareto_epsilon,
                'constraint_mode': self.constraint_mode,
                'adaptive_learning': self.adaptive_learning,
                'learning_rate': self.learning_rate,
                'performance_window': self.performance_window
            },
            'pareto_solutions': self.pareto_solutions[-50:],  # Save last 50
            'constraint_violations': self.constraint_violations[-50:],  # Save last 50
            'dimension_history': {
                dim.value: history[-100:] for dim, history in self.dimension_history.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)

    def load_model(self, filepath: str):
        """Load multi-objective cost model"""
        with open(filepath, 'r') as f:
            model_data = json.load(f)

        # Load weights
        weights_data = model_data['weights']
        self.weights = CostWeights(
            computational=weights_data['computational'],
            memory=weights_data['memory'],
            time=weights_data['time'],
            quality=weights_data['quality'],
            resource=weights_data['resource']
        )

        # Load cost tables
        self.computational_costs = model_data['computational_costs']
        self.memory_costs = model_data['memory_costs']
        self.time_costs = model_data['time_costs']
        self.quality_costs = model_data['quality_costs']
        self.resource_costs = model_data['resource_costs']

        # Load config
        config = model_data['config']
        self.optimization_mode = config['optimization_mode']
        self.pareto_epsilon = config['pareto_epsilon']
        self.constraint_mode = config['constraint_mode']
        self.adaptive_learning = config['adaptive_learning']
        self.learning_rate = config['learning_rate']
        self.performance_window = config['performance_window']

        # Load history
        self.pareto_solutions = model_data.get('pareto_solutions', [])
        self.constraint_violations = model_data.get('constraint_violations', [])

        # Load dimension history
        history_data = model_data.get('dimension_history', {})
        for dim_name, history in history_data.items():
            try:
                dimension = CostDimension(dim_name)
                self.dimension_history[dimension] = history
            except ValueError:
                continue

    def export_cost_analysis(self, filepath: str):
        """Export detailed cost analysis"""
        analysis = {
            'timestamp': time.time(),
            'model_type': 'MultiObjectiveCostModel',
            'dimensional_analysis': self.get_dimensional_analysis(),
            'pareto_solutions': self.pareto_solutions[-10:],  # Last 10
            'recent_constraint_violations': self.constraint_violations[-10:],  # Last 10
            'cost_distribution': self._get_cost_distribution(),
            'optimization_effectiveness': self._calculate_optimization_effectiveness()
        }

        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2)

    def _get_cost_distribution(self) -> Dict[str, Any]:
        """Get cost distribution statistics"""
        distributions = {}

        for dimension in CostDimension:
            history = self.dimension_history[dimension]
            if history:
                recent_costs = history[-50:] if len(history) > 50 else history

                distributions[dimension.value] = {
                    'mean': np.mean(recent_costs),
                    'median': np.median(recent_costs),
                    'std_dev': np.std(recent_costs),
                    'percentiles': {
                        '25': np.percentile(recent_costs, 25),
                        '50': np.percentile(recent_costs, 50),
                        '75': np.percentile(recent_costs, 75),
                        '90': np.percentile(recent_costs, 90),
                        '95': np.percentile(recent_costs, 95)
                    }
                }

        return distributions

    def _calculate_optimization_effectiveness(self) -> Dict[str, Any]:
        """Calculate optimization effectiveness metrics"""
        effectiveness = {
            'pareto_efficiency': len(self.pareto_solutions) / max(1, len(self.pareto_solutions) + len(self.constraint_violations)),
            'constraint_satisfaction_rate': 1.0 - (len(self.constraint_violations) / max(1, len(self.pareto_solutions) + len(self.constraint_violations))),
            'cost_stability': {}
        }

        # Calculate cost stability for each dimension
        for dimension in CostDimension:
            history = self.dimension_history[dimension]
            if len(history) > 10:
                recent = history[-10:]
                older = history[-20:-10] if len(history) > 20 else history[:-10]

                recent_std = np.std(recent) if len(recent) > 1 else 0
                older_std = np.std(older) if len(older) > 1 else 0

                stability = max(0, 1.0 - (recent_std - older_std) / (older_std + 0.001))
                effectiveness['cost_stability'][dimension.value] = stability

        return effectiveness