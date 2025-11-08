"""
Homogeneity Learner - Core AI learning system for binary homogeneity optimization
Learns from each operation application to improve future recommendations
"""

import time
import json
from typing import Dict, List, Any, Tuple, Optional
from ..models.performance_model import PerformanceModel, OperationResult


class HomogeneityLearner:
    """
    Main AI learning system that continuously improves operation recommendations
    based on observed performance with different binary data types
    """

    def __init__(self, model_file: str = "bsee_ai/models/homogeneity_learner.json"):
        self.model_file = model_file
        self.performance_model = PerformanceModel()
        self.session_id = int(time.time())

        # Operation library with parameters
        self.operation_library = {
            'xor_constant': {
                'description': 'XOR with constant value',
                'parameter_ranges': {'constant': [0x55, 0xAA, 0xFF, 0x00, 0x33, 0xCC]},
                'effective_for': ['random', 'mixed']
            },
            'add_constant': {
                'description': 'Add constant value',
                'parameter_ranges': {'constant': [1, 16, 32, 64, 128, 255]},
                'effective_for': ['random', 'near_uniform']
            },
            'rotate_left': {
                'description': 'Rotate bits left',
                'parameter_ranges': {'shift': [1, 2, 4, 8]},
                'effective_for': ['pattern', 'structured']
            },
            'substitute_bytes': {
                'description': 'Replace byte patterns',
                'parameter_ranges': {'pattern': [b'\x00\x00', b'\xFF\xFF'], 'replacement': [b'\xAA\xAA', b'\x55\x55']},
                'effective_for': ['repetitive', 'structured']
            },
            'move_to_front': {
                'description': 'Move unique bytes to front',
                'parameter_ranges': {},
                'effective_for': ['mixed', 'structured']
            },
            'reverse_bytes': {
                'description': 'Reverse byte order',
                'parameter_ranges': {},
                'effective_for': ['pattern', 'repetitive']
            },
            'shuffle_bytes': {
                'description': 'Shuffle bytes in blocks',
                'parameter_ranges': {'block_size': [4, 8, 16]},
                'effective_for': ['random', 'mixed']
            }
        }

        # Try to load existing model
        self.load_learning()

    def analyze_data_characteristics(self, data: bytes) -> str:
        """Analyze data to determine its characteristics for learning"""

        if len(data) == 0:
            return 'empty'

        # Calculate basic metrics
        unique_bytes = len(set(data))
        unique_ratio = unique_bytes / 256.0
        data_len = len(data)

        # Calculate repetition patterns
        repetitions = 0
        for i in range(data_len - 1):
            if data[i] == data[i + 1]:
                repetitions += 1
        repetition_ratio = repetitions / max(1, data_len - 1)

        # Calculate pattern complexity
        pattern_changes = 0
        for i in range(data_len - 4):
            if data[i:i+4] != data[i+1:i+5]:
                pattern_changes += 1
        pattern_complexity = pattern_changes / max(1, data_len - 4)

        # Classify data type
        if repetition_ratio > 0.5:
            return 'repetitive'
        elif unique_ratio < 0.1:
            return 'near_uniform'
        elif pattern_complexity < 0.2:
            return 'pattern'
        elif unique_ratio > 0.8 and repetition_ratio < 0.1:
            return 'random'
        else:
            return 'mixed'

    def recommend_operation(self, data: bytes, current_score: float) -> Tuple[str, Dict[str, Any], float]:
        """
        Recommend the best operation based on learned performance
        Returns: (operation_name, parameters, confidence_score)
        """

        data_type = self.analyze_data_characteristics(data)

        # Get learned recommendation
        operation, params = self.performance_model.predict_best_operation(data_type, current_score)

        # Calculate confidence based on learning data
        confidence = self._calculate_confidence(operation, data_type)

        # If confidence is low, use heuristic approach
        if confidence < 0.3:
            operation, params = self._heuristic_recommendation(data_type)

        return operation, params, confidence

    def _calculate_confidence(self, operation: str, data_type: str) -> float:
        """Calculate confidence in operation recommendation"""

        if operation not in self.performance_model.operation_stats:
            return 0.0

        stats = self.performance_model.operation_stats[operation]

        # Base confidence from success rate
        confidence = stats['success_rate']

        # Adjust for sample size (more samples = higher confidence)
        sample_factor = min(1.0, stats['total_uses'] / 20.0)
        confidence *= sample_factor

        # Boost if operation is known to work well for this data type
        if data_type in self.operation_library.get(operation, {}).get('effective_for', []):
            confidence *= 1.2

        return min(1.0, confidence)

    def _heuristic_recommendation(self, data_type: str) -> Tuple[str, Dict[str, Any]]:
        """Provide heuristic recommendations when learning data is insufficient"""

        recommendations = {
            'random': [
                ('xor_constant', {'constant': 0x55}),
                ('add_constant', {'constant': 16}),
                ('shuffle_bytes', {'block_size': 8})
            ],
            'repetitive': [
                ('substitute_bytes', {'pattern': b'\x00\x00', 'replacement': b'\xAA\xAA'}),
                ('move_to_front', {}),
                ('reverse_bytes', {})
            ],
            'pattern': [
                ('rotate_left', {'shift': 2}),
                ('shuffle_bytes', {'block_size': 4}),
                ('xor_constant', {'constant': 0xAA})
            ],
            'near_uniform': [
                ('add_constant', {'constant': 1}),
                ('xor_constant', {'constant': 0xFF}),
                ('rotate_left', {'shift': 1})
            ],
            'mixed': [
                ('move_to_front', {}),
                ('xor_constant', {'constant': 0x55}),
                ('add_constant', {'constant': 32})
            ]
        }

        operations = recommendations.get(data_type, recommendations['mixed'])
        return operations[0]  # Return first recommendation

    def learn_from_result(self, data: bytes, operation: str, parameters: Dict[str, Any],
                         initial_score: float, final_score: float):
        """Learn from the result of an operation application"""

        data_type = self.analyze_data_characteristics(data)
        self.performance_model.add_result(operation, parameters, data_type,
                                         initial_score, final_score)

        # Save learning after each significant improvement
        if final_score - initial_score > 0.01:
            self.save_learning()

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of learning progress"""

        learning_progress = self.performance_model.get_learning_progress()

        # Add operation-specific insights
        operation_insights = {}
        for operation, stats in self.performance_model.operation_stats.items():
            if stats['total_uses'] >= 3:  # Only include operations with sufficient data
                operation_insights[operation] = {
                    'total_uses': stats['total_uses'],
                    'success_rate': stats['success_rate'],
                    'avg_improvement': stats['avg_improvement'],
                    'best_improvement': stats['best_improvement'],
                    'description': self.operation_library.get(operation, {}).get('description', 'Unknown operation')
                }

        return {
            'session_id': self.session_id,
            'learning_progress': learning_progress,
            'operation_insights': operation_insights,
            'data_types_analyzed': list(self.performance_model.data_type_performance.keys()),
            'top_performing_operations': self.performance_model.get_overall_best_operations(5)
        }

    def save_learning(self):
        """Save learned model to file"""
        try:
            self.performance_model.save_model(self.model_file)
        except Exception as e:
            print(f"Error saving learning model: {e}")

    def load_learning(self):
        """Load learned model from file"""
        try:
            self.performance_model.load_model(self.model_file)
        except Exception as e:
            print(f"Error loading learning model: {e}")

    def reset_learning(self):
        """Reset all learning data"""
        self.performance_model = PerformanceModel()
        self.session_id = int(time.time())

    def export_learning_data(self, filepath: str):
        """Export learning data for analysis"""

        export_data = {
            'session_id': self.session_id,
            'export_timestamp': time.time(),
            'learning_summary': self.get_learning_summary(),
            'operation_history': [r.to_dict() for r in self.performance_model.operation_history],
            'operation_library': self.operation_library
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)