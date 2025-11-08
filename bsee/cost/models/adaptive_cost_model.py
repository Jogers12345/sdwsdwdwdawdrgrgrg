"""
Adaptive Cost Model for BSEE
Dynamic cost calculation that learns from analysis performance
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path
from collections import defaultdict
import time

from bsee.cost.cost_model import CostModel
from bsee.engine.state import State


class AdaptiveCostModel(CostModel):
    """
    Adaptive cost model that adjusts operation costs based on:
    - Historical effectiveness
    - Current data characteristics
    - Performance feedback
    - Resource constraints
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Base costs for operations
        self.base_costs = config.get('base_costs', {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 2.0,
            'reverse': 3.0,
            'substitute': 5.0,
            'compress': 10.0,
            'decompress': 10.0,
            'transpose': 8.0,
            'bit_swap': 4.0
        })

        # Adaptive parameters
        self.learning_rate = config.get('learning_rate', 0.1)
        self.adaptation_factor = config.get('adaptation_factor', 0.2)
        self.min_cost = config.get('min_cost', 0.1)
        self.max_cost = config.get('max_cost', 50.0)

        # Performance tracking
        self.operation_history = defaultdict(list)
        self.effectiveness_scores = defaultdict(lambda: 1.0)
        self.usage_counts = defaultdict(int)
        self.data_type_costs = defaultdict(lambda: defaultdict(float))

        # Context factors
        self.context_weights = {
            'data_size': config.get('data_size_weight', 0.3),
            'entropy': config.get('entropy_weight', 0.2),
            'pattern_density': config.get('pattern_weight', 0.2),
            'complexity': config.get('complexity_weight', 0.3)
        }

        # Resource monitoring
        self.resource_costs = {
            'time_per_kb': config.get('time_per_kb', 0.01),
            'memory_per_kb': config.get('memory_per_kb', 0.001),
            'cpu_intensity': config.get('cpu_intensity', 1.0)
        }

        # Learning history
        self.learning_history = []
        self.performance_trends = defaultdict(list)

    def calculate_base_cost(self, operation: str, state: State) -> float:
        """Calculate base cost for operation"""
        if operation not in self.base_costs:
            return self.base_costs.get('default', 1.0)

        return self.base_costs[operation]

    def calculate_adaptive_factor(self, operation: str, state: State) -> float:
        """Calculate adaptive factor based on historical performance"""
        # Effectiveness factor
        effectiveness = self.effectiveness_scores[operation]

        # Usage penalty (discourage overused operations)
        usage_factor = 1.0 + (self.usage_counts[operation] / 100.0) * 0.1

        # Data type specific factor
        data_type = self._classify_data_type(state.data)
        data_factor = self.data_type_costs[data_type][operation]

        # Recent performance factor
        recent_factor = self._get_recent_performance_factor(operation)

        adaptive_factor = effectiveness / (usage_factor * data_factor * recent_factor)
        return max(0.1, min(3.0, adaptive_factor))

    def calculate_context_factor(self, operation: str, state: State) -> float:
        """Calculate context factor based on current state characteristics"""
        factors = {}

        # Data size factor
        data_size = len(state.data)
        factors['data_size'] = 1.0 + (data_size / 10000.0)

        # Entropy factor
        entropy = self._calculate_entropy(state.data)
        factors['entropy'] = 1.0 + entropy

        # Pattern density factor
        pattern_density = self._calculate_pattern_density(state.data)
        factors['pattern_density'] = 1.0 + pattern_density

        # Complexity factor
        complexity = self._calculate_complexity(state.data)
        factors['complexity'] = 1.0 + complexity

        # Operation-specific adjustments
        operation_factor = self._get_operation_context_factor(operation, state)
        factors['operation_specific'] = operation_factor

        # Weighted combination
        context_factor = (
            self.context_weights['data_size'] * factors['data_size'] +
            self.context_weights['entropy'] * factors['entropy'] +
            self.context_weights['pattern_density'] * factors['pattern_density'] +
            self.context_weights['complexity'] * factors['complexity']
        ) * factors['operation_specific']

        return max(0.1, context_factor)

    def calculate_resource_factor(self, operation: str, state: State) -> float:
        """Calculate resource-based cost factor"""
        # Estimate resource requirements
        data_size_kb = len(state.data) / 1024.0

        # Time cost (based on operation complexity)
        time_cost = self._estimate_time_cost(operation, data_size_kb)

        # Memory cost
        memory_cost = self._estimate_memory_cost(operation, data_size_kb)

        # CPU intensity
        cpu_cost = self._get_cpu_intensity(operation)

        resource_factor = (time_cost + memory_cost) * cpu_cost
        return max(0.1, resource_factor)

    def calculate_operation_cost(self, operation: str, state: State,
                                parameters: Dict[str, Any] = None) -> float:
        """Calculate total operation cost"""
        # Base cost
        base_cost = self.calculate_base_cost(operation, state)

        # Adaptive factor
        adaptive_factor = self.calculate_adaptive_factor(operation, state)

        # Context factor
        context_factor = self.calculate_context_factor(operation, state)

        # Resource factor
        resource_factor = self.calculate_resource_factor(operation, state)

        # Parameter-specific cost
        parameter_factor = self._calculate_parameter_factor(operation, parameters)

        # Total cost
        total_cost = base_cost * adaptive_factor * context_factor * resource_factor * parameter_factor

        # Ensure cost is within bounds
        total_cost = max(self.min_cost, min(self.max_cost, total_cost))

        return total_cost

    def _classify_data_type(self, data: bytes) -> str:
        """Classify data type for cost adjustment"""
        if len(data) == 0:
            return 'empty'

        # Calculate characteristics
        entropy = self._calculate_entropy(data)
        unique_bytes = len(set(data))
        pattern_density = self._calculate_pattern_density(data)

        # Classification rules
        if entropy < 0.3:
            return 'structured'
        elif entropy > 0.8:
            return 'random'
        elif pattern_density > 0.5:
            return 'patterned'
        elif unique_bytes < 16:
            return 'low_diversity'
        else:
            return 'mixed'

    def _get_recent_performance_factor(self, operation: str) -> float:
        """Get recent performance factor for operation"""
        if operation not in self.performance_trends:
            return 1.0

        recent_trends = self.performance_trends[operation][-10:]  # Last 10 uses
        if not recent_trends:
            return 1.0

        avg_performance = np.mean(recent_trends)
        return max(0.5, min(2.0, avg_performance))

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

        return entropy / 8.0  # Normalize to [0, 1]

    def _calculate_pattern_density(self, data: bytes) -> float:
        """Calculate pattern density"""
        if len(data) < 4:
            return 0.0

        patterns = set()
        for i in range(len(data) - 3):
            pattern = data[i:i+4]
            patterns.add(pattern)

        return 1.0 - (len(patterns) / (len(data) - 3))

    def _calculate_complexity(self, data: bytes) -> float:
        """Calculate data complexity score"""
        if len(data) < 8:
            return 0.0

        # Simple complexity measure based on byte transitions
        transitions = 0
        for i in range(len(data) - 1):
            if data[i] != data[i+1]:
                transitions += 1

        complexity = transitions / (len(data) - 1)
        return complexity

    def _get_operation_context_factor(self, operation: str, state: State) -> float:
        """Get operation-specific context factor"""
        factors = {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 1.2,
            'reverse': 1.5,
            'substitute': 1.8,
            'compress': 2.0,
            'decompress': 2.5,
            'transpose': 1.6,
            'bit_swap': 1.3
        }

        # Adjust based on data characteristics
        entropy = self._calculate_entropy(state.data)
        pattern_density = self._calculate_pattern_density(state.data)

        if operation in ['compress', 'decompress']:
            # Compression operations are more expensive on random data
            if entropy > 0.8:
                return factors[operation] * 1.5
            elif pattern_density > 0.5:
                return factors[operation] * 0.8

        elif operation in ['xor', 'add', 'sub']:
            # Simple operations are cheaper on patterned data
            if pattern_density > 0.5:
                return factors[operation] * 0.9

        return factors.get(operation, 1.0)

    def _estimate_time_cost(self, operation: str, data_size_kb: float) -> float:
        """Estimate time cost for operation"""
        time_complexity = {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 1.2,
            'reverse': 1.0,
            'substitute': 1.5,
            'compress': 10.0,
            'decompress': 15.0,
            'transpose': 2.0,
            'bit_swap': 1.3
        }

        complexity = time_complexity.get(operation, 1.0)
        return data_size_kb * self.resource_costs['time_per_kb'] * complexity

    def _estimate_memory_cost(self, operation: str, data_size_kb: float) -> float:
        """Estimate memory cost for operation"""
        memory_multiplier = {
            'xor': 1.0,
            'add': 1.0,
            'sub': 1.0,
            'rotate': 1.0,
            'reverse': 1.0,
            'substitute': 1.2,
            'compress': 0.5,  # Compression reduces memory
            'decompress': 2.0,  # Decompression increases memory
            'transpose': 1.5,
            'bit_swap': 1.0
        }

        multiplier = memory_multiplier.get(operation, 1.0)
        return data_size_kb * self.resource_costs['memory_per_kb'] * multiplier

    def _get_cpu_intensity(self, operation: str) -> float:
        """Get CPU intensity factor for operation"""
        cpu_intensities = {
            'xor': 0.5,
            'add': 0.5,
            'sub': 0.5,
            'rotate': 0.8,
            'reverse': 0.6,
            'substitute': 1.0,
            'compress': 2.0,
            'decompress': 2.5,
            'transpose': 1.5,
            'bit_swap': 0.8
        }

        return cpu_intensities.get(operation, 1.0)

    def _calculate_parameter_factor(self, operation: str, parameters: Dict[str, Any]) -> float:
        """Calculate parameter-specific cost factor"""
        if not parameters:
            return 1.0

        factor = 1.0

        if operation in ['xor', 'add', 'sub']:
            # Cost based on parameter magnitude
            value = parameters.get('key') or parameters.get('value', 0)
            factor *= (1.0 + abs(value) / 255.0)

        elif operation == 'rotate':
            bits = parameters.get('bits', 1)
            factor *= (bits / 4.0)  # Normalize to 4-bit rotation

        elif operation == 'substitute':
            pattern = parameters.get('pattern', b'')
            replacement = parameters.get('replacement', b'')
            factor *= (1.0 + len(pattern) + len(replacement)) / 8.0

        elif operation in ['compress', 'decompress']:
            level = parameters.get('level', 6)
            factor *= (level / 6.0)

        return max(0.1, factor)

    def update_operation_performance(self, operation: str, state: State,
                                   result_state: State, execution_time: float):
        """Update operation performance based on results"""
        # Calculate effectiveness
        score_improvement = result_state.current_score - state.current_score
        cost_incurred = self.calculate_operation_cost(operation, state)
        effectiveness = score_improvement / (cost_incurred + 0.001)

        # Update effectiveness score with learning rate
        old_effectiveness = self.effectiveness_scores[operation]
        new_effectiveness = old_effectiveness + self.learning_rate * (effectiveness - old_effectiveness)
        self.effectiveness_scores[operation] = max(0.1, min(3.0, new_effectiveness))

        # Update usage count
        self.usage_counts[operation] += 1

        # Store in history
        self.operation_history[operation].append({
            'score_improvement': score_improvement,
            'cost': cost_incurred,
            'effectiveness': effectiveness,
            'execution_time': execution_time,
            'data_size': len(state.data),
            'timestamp': time.time()
        })

        # Update performance trends
        self.performance_trends[operation].append(effectiveness)

        # Update data type specific costs
        data_type = self._classify_data_type(state.data)
        old_data_cost = self.data_type_costs[data_type][operation]
        new_data_cost = old_data_cost + self.learning_rate * (1.0 / (effectiveness + 0.001) - old_data_cost)
        self.data_type_costs[data_type][operation] = max(0.1, min(3.0, new_data_cost))

        # Store learning record
        self.learning_history.append({
            'operation': operation,
            'data_type': data_type,
            'effectiveness': effectiveness,
            'cost_adjustment': new_effectiveness - old_effectiveness,
            'timestamp': time.time()
        })

    def get_cost_analysis(self) -> Dict[str, Any]:
        """Get comprehensive cost analysis"""
        analysis = {
            'base_costs': self.base_costs.copy(),
            'current_effectiveness': dict(self.effectiveness_scores),
            'usage_statistics': dict(self.usage_counts),
            'data_type_costs': {dt: dict(costs) for dt, costs in self.data_type_costs.items()},
            'learning_statistics': {
                'total_updates': len(self.learning_history),
                'average_effectiveness': np.mean(list(self.effectiveness_scores.values())),
                'most_used_operation': max(self.usage_counts.items(), key=lambda x: x[1])[0] if self.usage_counts else None,
                'most_effective_operation': max(self.effectiveness_scores.items(), key=lambda x: x[1])[0]
            },
            'context_weights': self.context_weights.copy(),
            'resource_costs': self.resource_costs.copy()
        }

        return analysis

    def save_model(self, filepath: str):
        """Save adaptive cost model"""
        model_data = {
            'base_costs': self.base_costs,
            'effectiveness_scores': dict(self.effectiveness_scores),
            'usage_counts': dict(self.usage_counts),
            'data_type_costs': {dt: dict(costs) for dt, costs in self.data_type_costs.items()},
            'context_weights': self.context_weights,
            'resource_costs': self.resource_costs,
            'learning_history': self.learning_history[-100:],  # Save last 100 records
            'performance_trends': {op: trends[-20:] for op, trends in self.performance_trends.items()},
            'config': {
                'learning_rate': self.learning_rate,
                'adaptation_factor': self.adaptation_factor,
                'min_cost': self.min_cost,
                'max_cost': self.max_cost
            }
        }

        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)

    def load_model(self, filepath: str):
        """Load adaptive cost model"""
        with open(filepath, 'r') as f:
            model_data = json.load(f)

        self.base_costs = model_data['base_costs']
        self.effectiveness_scores = defaultdict(float, model_data['effectiveness_scores'])
        self.usage_counts = defaultdict(int, model_data['usage_counts'])
        self.data_type_costs = defaultdict(lambda: defaultdict(float))
        for dt, costs in model_data['data_type_costs'].items():
            self.data_type_costs[dt] = defaultdict(float, costs)

        self.context_weights = model_data['context_weights']
        self.resource_costs = model_data['resource_costs']
        self.learning_history = model_data['learning_history']

        # Rebuild performance trends
        self.performance_trends = defaultdict(list)
        for op, trends in model_data['performance_trends'].items():
            self.performance_trends[op] = trends

        # Load config
        config = model_data['config']
        self.learning_rate = config['learning_rate']
        self.adaptation_factor = config['adaptation_factor']
        self.min_cost = config['min_cost']
        self.max_cost = config['max_cost']

    def reset_learning(self):
        """Reset learning statistics"""
        self.effectiveness_scores = defaultdict(lambda: 1.0)
        self.usage_counts = defaultdict(int)
        self.data_type_costs = defaultdict(lambda: defaultdict(float))
        self.learning_history = []
        self.performance_trends = defaultdict(list)

    def export_performance_report(self, filepath: str):
        """Export detailed performance report"""
        report = {
            'timestamp': time.time(),
            'model_type': 'AdaptiveCostModel',
            'analysis': self.get_cost_analysis(),
            'operation_details': {}
        }

        # Add detailed operation information
        for operation in self.base_costs.keys():
            history = self.operation_history[operation]
            if history:
                recent_history = history[-20:]  # Last 20 uses
                report['operation_details'][operation] = {
                    'total_uses': len(history),
                    'average_effectiveness': np.mean([h['effectiveness'] for h in history]),
                    'average_cost': np.mean([h['cost'] for h in history]),
                    'average_improvement': np.mean([h['score_improvement'] for h in history]),
                    'recent_trend': 'improving' if len(recent_history) > 1 and
                                   recent_history[-1]['effectiveness'] > recent_history[0]['effectiveness'] else 'stable'
                }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)