"""
Adaptive Policy for BSEE
Policy that dynamically adjusts based on data characteristics and performance feedback
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import json
from pathlib import Path
from collections import defaultdict, deque
import time
from enum import Enum
from dataclasses import dataclass

from bsee.engine.state import State


class PolicyMode(Enum):
    """Different policy operating modes"""
    EXPLORATORY = "exploratory"
    OPTIMIZATION = "optimization"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"


@dataclass
class PolicyMetrics:
    """Policy performance metrics"""
    success_rate: float
    average_improvement: float
    convergence_speed: float
    resource_efficiency: float
    stability_score: float


class AdaptivePolicy:
    """
    Adaptive policy that learns from analysis results and adjusts its behavior
    based on data characteristics, performance feedback, and resource constraints.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Policy parameters
        self.mode = PolicyMode(config.get('mode', 'balanced'))
        self.adaptation_rate = config.get('adaptation_rate', 0.1)
        self.performance_window = config.get('performance_window', 50)
        self.exploration_rate = config.get('exploration_rate', 0.1)

        # Data classification parameters
        self.data_type_thresholds = {
            'entropy_low': 0.3,
            'entropy_high': 0.8,
            'pattern_low': 0.2,
            'pattern_high': 0.7,
            'size_small': 1024,
            'size_large': 1048576
        }

        # Strategy preferences for different data types
        self.strategy_preferences = self._initialize_strategy_preferences()

        # Performance tracking
        self.performance_history = defaultdict(list)
        self.strategy_effectiveness = defaultdict(lambda: 1.0)
        self.mode_performance = defaultdict(list)
        self.adaptation_history = []

        # Resource constraints
        self.resource_limits = {
            'max_operations': config.get('max_operations', 10000),
            'max_cost': config.get('max_cost', 100000),
            'max_time': config.get('max_time', 300),  # seconds
            'max_memory': config.get('max_memory', 1024)  # MB
        }

        # Current policy state
        self.current_preferences = {}
        self.current_constraints = {}
        self.learning_enabled = config.get('learning_enabled', True)

    def _initialize_strategy_preferences(self) -> Dict[str, Dict[str, float]]:
        """Initialize strategy preferences for different data types"""
        return {
            'structured': {
                'heuristic': 0.8,
                'mcts': 0.6,
                'genetic': 0.4,
                'beam': 0.5,
                'annealing': 0.3,
                'greedy': 0.7
            },
            'random': {
                'mcts': 0.8,
                'genetic': 0.7,
                'annealing': 0.6,
                'beam': 0.4,
                'heuristic': 0.3,
                'greedy': 0.2
            },
            'patterned': {
                'heuristic': 0.9,
                'greedy': 0.8,
                'beam': 0.7,
                'annealing': 0.5,
                'genetic': 0.4,
                'mcts': 0.6
            },
            'compressed': {
                'genetic': 0.8,
                'mcts': 0.7,
                'annealing': 0.6,
                'beam': 0.5,
                'heuristic': 0.4,
                'greedy': 0.3
            },
            'mixed': {
                'mcts': 0.7,
                'genetic': 0.6,
                'heuristic': 0.6,
                'beam': 0.5,
                'annealing': 0.5,
                'greedy': 0.4
            }
        }

    def classify_data(self, data: bytes) -> str:
        """Classify data type for policy adaptation"""
        if not data:
            return 'empty'

        # Calculate characteristics
        entropy = self._calculate_entropy(data)
        pattern_density = self._calculate_pattern_density(data)
        size = len(data)

        # Classification logic
        if entropy < self.data_type_thresholds['entropy_low']:
            if pattern_density > self.data_type_thresholds['pattern_high']:
                return 'structured'
            else:
                return 'low_entropy'
        elif entropy > self.data_type_thresholds['entropy_high']:
            return 'random'
        elif pattern_density > self.data_type_thresholds['pattern_high']:
            return 'patterned'
        elif size < self.data_type_thresholds['size_small']:
            return 'small'
        elif size > self.data_type_thresholds['size_large']:
            return 'large'
        else:
            return 'mixed'

    def get_strategy_preferences(self, data: bytes) -> Dict[str, float]:
        """Get strategy preferences based on data type and current mode"""
        data_type = self.classify_data(data)

        # Base preferences from data type
        base_preferences = self.strategy_preferences.get(
            data_type, self.strategy_preferences['mixed']
        ).copy()

        # Adjust based on current mode
        mode_adjustments = self._get_mode_adjustments()
        for strategy, adjustment in mode_adjustments.items():
            if strategy in base_preferences:
                base_preferences[strategy] *= adjustment

        # Apply learned effectiveness
        for strategy in base_preferences:
            effectiveness = self.strategy_effectiveness.get(strategy, 1.0)
            base_preferences[strategy] *= effectiveness

        # Normalize preferences
        total = sum(base_preferences.values())
        if total > 0:
            base_preferences = {k: v/total for k, v in base_preferences.items()}

        return base_preferences

    def _get_mode_adjustments(self) -> Dict[str, float]:
        """Get strategy adjustments based on current mode"""
        adjustments = {
            PolicyMode.EXPLORATORY: {
                'mcts': 1.3, 'genetic': 1.2, 'annealing': 1.2,
                'heuristic': 0.8, 'greedy': 0.7, 'beam': 0.9
            },
            PolicyMode.OPTIMIZATION: {
                'mcts': 1.4, 'genetic': 1.3, 'beam': 1.2,
                'heuristic': 0.9, 'greedy': 0.8, 'annealing': 1.0
            },
            PolicyMode.CONSERVATIVE: {
                'heuristic': 1.3, 'greedy': 1.2, 'beam': 1.1,
                'mcts': 0.8, 'genetic': 0.7, 'annealing': 0.6
            },
            PolicyMode.AGGRESSIVE: {
                'genetic': 1.4, 'mcts': 1.3, 'annealing': 1.3,
                'beam': 1.1, 'heuristic': 0.7, 'greedy': 0.6
            },
            PolicyMode.BALANCED: {}  # No adjustments
        }

        return adjustments.get(self.mode, {})

    def get_operation_constraints(self, data: bytes, current_state: State) -> Dict[str, Any]:
        """Get operation constraints based on current state and policy"""
        data_type = self.classify_data(data)

        # Base constraints from resource limits
        constraints = {
            'max_operations': self.resource_limits['max_operations'],
            'max_cost': self.resource_limits['max_cost'],
            'max_time': self.resource_limits['max_time'],
            'allowed_operations': self._get_allowed_operations(data_type),
            'operation_preferences': self._get_operation_preferences(data_type),
            'quality_thresholds': self._get_quality_thresholds(data_type)
        }

        # Adjust based on current progress
        progress_factor = current_state.operations_count / constraints['max_operations']
        if progress_factor > 0.8:  # Near limit
            constraints['max_cost'] *= 0.5  # Reduce remaining budget
            constraints['allowed_operations'] = self._get_safe_operations()

        # Adjust based on current mode
        if self.mode == PolicyMode.CONSERVATIVE:
            constraints['max_cost'] *= 0.7
            constraints['max_operations'] = int(constraints['max_operations'] * 0.8)
        elif self.mode == PolicyMode.AGGRESSIVE:
            constraints['max_cost'] *= 1.3
            constraints['max_operations'] = int(constraints['max_operations'] * 1.2)

        return constraints

    def _get_allowed_operations(self, data_type: str) -> List[str]:
        """Get allowed operations based on data type"""
        operations_by_type = {
            'structured': ['xor', 'add', 'sub', 'rotate', 'substitute'],
            'random': ['xor', 'add', 'sub', 'rotate', 'substitute', 'compress'],
            'patterned': ['xor', 'substitute', 'compress', 'pattern_match'],
            'compressed': ['decompress', 'substitute', 'pattern_match'],
            'mixed': ['xor', 'add', 'sub', 'rotate', 'substitute', 'compress', 'decompress']
        }

        return operations_by_type.get(data_type, operations_by_type['mixed'])

    def _get_operation_preferences(self, data_type: str) -> Dict[str, float]:
        """Get operation preferences based on data type"""
        preferences = {
            'structured': {'substitute': 1.2, 'rotate': 1.1, 'xor': 1.0},
            'random': {'xor': 1.1, 'add': 1.0, 'sub': 1.0, 'compress': 1.3},
            'patterned': {'substitute': 1.4, 'pattern_match': 1.5, 'compress': 1.3},
            'compressed': {'decompress': 1.5, 'substitute': 1.1},
            'mixed': {'xor': 1.0, 'add': 1.0, 'sub': 1.0, 'substitute': 1.1}
        }

        return preferences.get(data_type, preferences['mixed'])

    def _get_quality_thresholds(self, data_type: str) -> Dict[str, float]:
        """Get quality thresholds based on data type"""
        thresholds = {
            'structured': {'min_improvement': 0.01, 'convergence_threshold': 0.001},
            'random': {'min_improvement': 0.005, 'convergence_threshold': 0.0005},
            'patterned': {'min_improvement': 0.02, 'convergence_threshold': 0.002},
            'compressed': {'min_improvement': 0.01, 'convergence_threshold': 0.001},
            'mixed': {'min_improvement': 0.008, 'convergence_threshold': 0.0008}
        }

        return thresholds.get(data_type, thresholds['mixed'])

    def _get_safe_operations(self) -> List[str]:
        """Get safe operations for conservative mode"""
        return ['xor', 'add', 'sub', 'rotate']

    def update_performance(self, strategy: str, initial_state: State, final_state: State,
                          execution_time: float, operations_used: List[str]):
        """Update policy based on performance feedback"""
        if not self.learning_enabled:
            return

        # Calculate performance metrics
        score_improvement = final_state.current_score - initial_state.current_score
        efficiency = score_improvement / (execution_time + 0.001)
        operation_diversity = len(set(operations_used)) / max(1, len(operations_used))

        # Update strategy effectiveness
        current_effectiveness = self.strategy_effectiveness[strategy]
        new_effectiveness = current_effectiveness + self.adaptation_rate * (efficiency - current_effectiveness)
        self.strategy_effectiveness[strategy] = max(0.1, min(3.0, new_effectiveness))

        # Record performance
        performance_record = {
            'strategy': strategy,
            'score_improvement': score_improvement,
            'efficiency': efficiency,
            'execution_time': execution_time,
            'operations_used': len(operations_used),
            'operation_diversity': operation_diversity,
            'data_type': self.classify_data(initial_state.data),
            'mode': self.mode.value,
            'timestamp': time.time()
        }

        self.performance_history[strategy].append(performance_record)
        self.mode_performance[self.mode].append(performance_record)

        # Adapt policy if needed
        self._adapt_policy(performance_record)

    def _adapt_policy(self, performance_record: Dict[str, Any]):
        """Adapt policy based on performance feedback"""
        # Calculate recent performance
        recent_performance = self._calculate_recent_performance()

        # Consider mode adaptation
        if self._should_change_mode(recent_performance):
            self._change_mode(recent_performance)

        # Consider strategy preference adaptation
        if self._should_adapt_preferences(recent_performance):
            self._adapt_strategy_preferences(recent_performance)

        # Record adaptation
        self.adaptation_history.append({
            'performance': performance_record,
            'old_mode': self.mode.value,
            'new_mode': self.mode.value if not self._should_change_mode(recent_performance) else self._get_best_mode(recent_performance),
            'timestamp': time.time()
        })

    def _calculate_recent_performance(self) -> PolicyMetrics:
        """Calculate recent performance metrics"""
        all_recent = []
        for strategy_records in self.performance_history.values():
            all_recent.extend(strategy_records[-10:])  # Last 10 records per strategy

        if not all_recent:
            return PolicyMetrics(0, 0, 0, 0, 0)

        success_rate = sum(1 for r in all_recent if r['score_improvement'] > 0) / len(all_recent)
        avg_improvement = np.mean([r['score_improvement'] for r in all_recent])
        convergence_speed = np.mean([r['efficiency'] for r in all_recent])
        resource_efficiency = np.mean([r['operation_diversity'] for r in all_recent])
        stability_score = 1.0 - np.std([r['score_improvement'] for r in all_recent]) / (abs(avg_improvement) + 0.001)

        return PolicyMetrics(
            success_rate=success_rate,
            average_improvement=avg_improvement,
            convergence_speed=convergence_speed,
            resource_efficiency=resource_efficiency,
            stability_score=stability_score
        )

    def _should_change_mode(self, performance: PolicyMetrics) -> bool:
        """Determine if policy mode should be changed"""
        # Change mode if performance is poor
        if performance.success_rate < 0.3:
            return True
        if performance.average_improvement < 0.001:
            return True
        if performance.stability_score < 0.5:
            return True

        return False

    def _get_best_mode(self, performance: PolicyMetrics) -> PolicyMode:
        """Get best mode based on current performance"""
        if performance.success_rate < 0.3:
            return PolicyMode.EXPLORATORY
        elif performance.average_improvement < 0.001:
            return PolicyMode.AGGRESSIVE
        elif performance.stability_score < 0.5:
            return PolicyMode.CONSERVATIVE
        else:
            return PolicyMode.OPTIMIZATION

    def _change_mode(self, performance: PolicyMetrics):
        """Change policy mode"""
        old_mode = self.mode
        self.mode = self._get_best_mode(performance)

        if old_mode != self.mode:
            print(f"Policy mode changed from {old_mode.value} to {self.mode.value}")

    def _should_adapt_preferences(self, performance: PolicyMetrics) -> bool:
        """Determine if strategy preferences should be adapted"""
        # Adapt if there's significant performance variation
        return performance.success_rate > 0.1 and performance.stability_score < 0.8

    def _adapt_strategy_preferences(self, performance: PolicyMetrics):
        """Adapt strategy preferences based on performance"""
        # Update strategy preferences for different data types
        for data_type in self.strategy_preferences:
            # Get recent performance for this data type
            type_performance = [
                r for r in self.performance_history.get('heuristic', [])
                if r.get('data_type') == data_type
            ]

            if len(type_performance) >= 5:  # Have enough data
                # Calculate effectiveness by strategy for this data type
                strategy_effects = defaultdict(list)
                for record in type_performance[-20:]:  # Last 20 records
                    strategy_effects[record['strategy']].append(record['efficiency'])

                # Update preferences
                for strategy, effects in strategy_effects.items():
                    if effects and strategy in self.strategy_preferences[data_type]:
                        avg_effect = np.mean(effects)
                        current_pref = self.strategy_preferences[data_type][strategy]
                        new_pref = current_pref + self.adaptation_rate * (avg_effect - current_pref)
                        self.strategy_preferences[data_type][strategy] = max(0.1, min(2.0, new_pref))

    def set_mode(self, mode: Union[str, PolicyMode]):
        """Manually set policy mode"""
        if isinstance(mode, str):
            try:
                self.mode = PolicyMode(mode)
            except ValueError:
                print(f"Invalid mode: {mode}, using balanced")
                self.mode = PolicyMode.BALANCED
        else:
            self.mode = mode

    def set_resource_limits(self, limits: Dict[str, Any]):
        """Set resource constraints"""
        for key, value in limits.items():
            if key in self.resource_limits:
                self.resource_limits[key] = value

    def enable_learning(self, enabled: bool = True):
        """Enable or disable policy learning"""
        self.learning_enabled = enabled

    def get_policy_summary(self) -> Dict[str, Any]:
        """Get comprehensive policy summary"""
        recent_performance = self._calculate_recent_performance()

        return {
            'current_mode': self.mode.value,
            'learning_enabled': self.learning_enabled,
            'adaptation_rate': self.adaptation_rate,
            'exploration_rate': self.exploration_rate,
            'resource_limits': self.resource_limits.copy(),
            'strategy_effectiveness': dict(self.strategy_effectiveness),
            'recent_performance': {
                'success_rate': recent_performance.success_rate,
                'average_improvement': recent_performance.average_improvement,
                'convergence_speed': recent_performance.convergence_speed,
                'resource_efficiency': recent_performance.resource_efficiency,
                'stability_score': recent_performance.stability_score
            },
            'adaptation_history_size': len(self.adaptation_history),
            'performance_records': sum(len(records) for records in self.performance_history.values())
        }

    def save_policy(self, filepath: str):
        """Save policy state"""
        policy_data = {
            'config': self.config,
            'mode': self.mode.value,
            'strategy_preferences': {
                data_type: dict(prefs) for data_type, prefs in self.strategy_preferences.items()
            },
            'strategy_effectiveness': dict(self.strategy_effectiveness),
            'resource_limits': self.resource_limits,
            'adaptation_history': self.adaptation_history[-50:],  # Last 50
            'performance_summary': {
                strategy: records[-10:] if records else []  # Last 10 per strategy
                for strategy, records in self.performance_history.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(policy_data, f, indent=2)

    def load_policy(self, filepath: str):
        """Load policy state"""
        with open(filepath, 'r') as f:
            policy_data = json.load(f)

        self.config = policy_data['config']
        self.mode = PolicyMode(policy_data['mode'])

        # Load strategy preferences
        for data_type, prefs in policy_data['strategy_preferences'].items():
            self.strategy_preferences[data_type] = prefs

        # Load strategy effectiveness
        self.strategy_effectiveness = defaultdict(float, policy_data['strategy_effectiveness'])

        # Load resource limits
        self.resource_limits = policy_data['resource_limits']

        # Load adaptation history
        self.adaptation_history = policy_data.get('adaptation_history', [])

        # Note: Full performance history not loaded for memory efficiency

    def export_analysis_report(self, filepath: str):
        """Export detailed policy analysis report"""
        report = {
            'timestamp': time.time(),
            'policy_type': 'AdaptivePolicy',
            'summary': self.get_policy_summary(),
            'strategy_analysis': self._analyze_strategy_performance(),
            'mode_analysis': self._analyze_mode_performance(),
            'adaptation_analysis': self._analyze_adaptations(),
            'recommendations': self._generate_recommendations()
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

    def _analyze_strategy_performance(self) -> Dict[str, Any]:
        """Analyze strategy performance"""
        analysis = {}

        for strategy, records in self.performance_history.items():
            if records:
                recent_records = records[-20:]  # Last 20 records
                analysis[strategy] = {
                    'total_uses': len(records),
                    'recent_uses': len(recent_records),
                    'average_improvement': np.mean([r['score_improvement'] for r in recent_records]),
                    'average_efficiency': np.mean([r['efficiency'] for r in recent_records]),
                    'success_rate': sum(1 for r in recent_records if r['score_improvement'] > 0) / len(recent_records),
                    'preferred_data_types': list(set(r['data_type'] for r in recent_records))
                }

        return analysis

    def _analyze_mode_performance(self) -> Dict[str, Any]:
        """Analyze performance by policy mode"""
        analysis = {}

        for mode, records in self.mode_performance.items():
            if records:
                recent_records = records[-20:]
                analysis[mode] = {
                    'total_uses': len(records),
                    'average_improvement': np.mean([r['score_improvement'] for r in recent_records]),
                    'average_efficiency': np.mean([r['efficiency'] for r in recent_records]),
                    'success_rate': sum(1 for r in recent_records if r['score_improvement'] > 0) / len(recent_records)
                }

        return analysis

    def _analyze_adaptations(self) -> Dict[str, Any]:
        """Analyze policy adaptations"""
        if not self.adaptation_history:
            return {'total_adaptations': 0, 'adaptation_frequency': 0}

        recent_adaptations = self.adaptation_history[-20:]
        mode_changes = [a for a in recent_adaptations if a['old_mode'] != a['new_mode']]

        return {
            'total_adaptations': len(self.adaptation_history),
            'recent_adaptations': len(recent_adaptations),
            'mode_changes': len(mode_changes),
            'adaptation_frequency': len(recent_adaptations) / max(1, recent_adaptations[-1]['timestamp'] - recent_adaptations[0]['timestamp']) * 3600,  # per hour
            'most_common_new_mode': max(set(a['new_mode'] for a in mode_changes), key=lambda x: sum(1 for a in mode_changes if a['new_mode'] == x)) if mode_changes else None
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate policy recommendations"""
        recommendations = []
        recent_performance = self._calculate_recent_performance()

        if recent_performance.success_rate < 0.5:
            recommendations.append("Consider switching to exploratory mode for better discovery")

        if recent_performance.average_improvement < 0.01:
            recommendations.append("Try aggressive mode to find larger improvements")

        if recent_performance.stability_score < 0.6:
            recommendations.append("Enable conservative mode for more stable results")

        if len(self.adaptation_history) > 100:
            recommendations.append("Policy is adapting frequently - consider tuning adaptation rate")

        if recent_performance.resource_efficiency < 0.5:
            recommendations.append("Diversify operation usage for better resource efficiency")

        return recommendations

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