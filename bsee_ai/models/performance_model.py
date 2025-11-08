"""
Performance Model for Tracking AI Learning and Operation Effectiveness
Tracks which operations work best for different types of binary data
"""

import json
import time
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class OperationResult:
    """Stores the result of an operation application"""
    operation: str
    parameters: Dict[str, Any]
    data_type: str
    initial_score: float
    final_score: float
    improvement: float
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PerformanceModel:
    """
    Tracks and learns from operation performance to improve recommendations
    """

    def __init__(self):
        # Storage for all operation results
        self.operation_history: List[OperationResult] = []

        # Performance statistics by operation type
        self.operation_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'total_uses': 0,
            'total_improvement': 0.0,
            'best_improvement': 0.0,
            'success_rate': 0.0,
            'avg_improvement': 0.0,
            'last_used': 0.0
        })

        # Performance by data characteristics
        self.data_type_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'best_operations': [],
            'avg_improvement': 0.0,
            'total_tests': 0
        })

        # Learning parameters
        self.learning_rate = 0.1
        self.min_samples_for_learning = 5

    def add_result(self, operation: str, parameters: Dict[str, Any],
                   data_type: str, initial_score: float, final_score: float):
        """Add a new operation result to learn from"""

        improvement = final_score - initial_score
        timestamp = time.time()

        # Create operation result
        result = OperationResult(
            operation=operation,
            parameters=parameters,
            data_type=data_type,
            initial_score=initial_score,
            final_score=final_score,
            improvement=improvement,
            timestamp=timestamp
        )

        # Store result
        self.operation_history.append(result)

        # Update operation statistics
        stats = self.operation_stats[operation]
        stats['total_uses'] += 1
        stats['total_improvement'] += improvement
        stats['best_improvement'] = max(stats['best_improvement'], improvement)
        stats['avg_improvement'] = stats['total_improvement'] / stats['total_uses']
        stats['success_rate'] = len([r for r in self.operation_history[-100:]
                                   if r.operation == operation and r.improvement > 0]) / min(100, stats['total_uses'])
        stats['last_used'] = timestamp

        # Update data type performance
        data_stats = self.data_type_performance[data_type]
        data_stats['total_tests'] += 1
        data_stats['avg_improvement'] = sum(r.improvement for r in self.operation_history
                                           if r.data_type == data_type) / data_stats['total_tests']

        # Update best operations for this data type
        if improvement > 0:
            data_stats['best_operations'].append({
                'operation': operation,
                'parameters': parameters,
                'improvement': improvement,
                'timestamp': timestamp
            })
            # Keep only top 10 operations
            data_stats['best_operations'].sort(key=lambda x: x['improvement'], reverse=True)
            data_stats['best_operations'] = data_stats['best_operations'][:10]

    def get_best_operations(self, data_type: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """Get the best performing operations for a specific data type"""

        if data_type not in self.data_type_performance:
            # Fallback to overall best operations
            return self.get_overall_best_operations(top_k)

        best_ops = self.data_type_performance[data_type]['best_operations'][:top_k]
        return [(op['operation'], op['parameters'], op['improvement']) for op in best_ops]

    def get_overall_best_operations(self, top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """Get the overall best performing operations"""

        # Sort all operations by average improvement
        sorted_ops = sorted(self.operation_stats.items(),
                          key=lambda x: x[1]['avg_improvement'], reverse=True)

        result = []
        for operation, stats in sorted_ops[:top_k]:
            if stats['total_uses'] >= self.min_samples_for_learning:
                # Get best parameters for this operation
                best_result = max([r for r in self.operation_history if r.operation == operation],
                                key=lambda x: x.improvement)
                result.append((operation, best_result.parameters, stats['avg_improvement']))

        return result

    def predict_best_operation(self, data_type: str, current_score: float) -> Tuple[str, Dict[str, Any]]:
        """Predict the best operation for current data"""

        # Get data-specific recommendations
        data_ops = self.get_best_operations(data_type, 3)

        if data_ops:
            # Choose from data-specific operations
            operation, params, expected_improvement = data_ops[0]
        else:
            # Fallback to overall best
            overall_ops = self.get_overall_best_operations(1)
            if overall_ops:
                operation, params, expected_improvement = overall_ops[0]
            else:
                # Default recommendation if no learning data
                operation = 'xor_constant'
                params = {'constant': 0x55}
                expected_improvement = 0.0

        return operation, params

    def get_learning_progress(self) -> Dict[str, Any]:
        """Get statistics about learning progress"""

        total_operations = len(self.operation_history)
        successful_operations = len([r for r in self.operation_history if r.improvement > 0])

        return {
            'total_operations_tested': total_operations,
            'successful_operations': successful_operations,
            'overall_success_rate': successful_operations / max(1, total_operations),
            'unique_operations_learned': len(self.operation_stats),
            'data_types_analyzed': len(self.data_type_performance),
            'best_overall_improvement': max([r.improvement for r in self.operation_history], default=0.0),
            'average_improvement': sum([r.improvement for r in self.operation_history]) / max(1, total_operations)
        }

    def save_model(self, filepath: str):
        """Save the performance model to file"""

        model_data = {
            'operation_history': [r.to_dict() for r in self.operation_history],
            'operation_stats': dict(self.operation_stats),
            'data_type_performance': dict(self.data_type_performance),
            'learning_rate': self.learning_rate,
            'min_samples_for_learning': self.min_samples_for_learning
        }

        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)

    def load_model(self, filepath: str):
        """Load the performance model from file"""

        try:
            with open(filepath, 'r') as f:
                model_data = json.load(f)

            # Restore operation history
            self.operation_history = [OperationResult(**r) for r in model_data['operation_history']]

            # Restore statistics
            self.operation_stats = defaultdict(lambda: {
                'total_uses': 0, 'total_improvement': 0.0, 'best_improvement': 0.0,
                'success_rate': 0.0, 'avg_improvement': 0.0, 'last_used': 0.0
            })
            self.operation_stats.update(model_data['operation_stats'])

            self.data_type_performance = defaultdict(lambda: {
                'best_operations': [], 'avg_improvement': 0.0, 'total_tests': 0
            })
            self.data_type_performance.update(model_data['data_type_performance'])

            self.learning_rate = model_data.get('learning_rate', 0.1)
            self.min_samples_for_learning = model_data.get('min_samples_for_learning', 5)

        except Exception as e:
            print(f"Error loading model: {e}")
            # Continue with empty model if loading fails