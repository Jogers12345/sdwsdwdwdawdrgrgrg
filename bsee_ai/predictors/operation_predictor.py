"""
Operation Predictor - Predicts optimal operation sequences for homogeneity improvement
Uses learned patterns to recommend the best operations
"""

from typing import Dict, List, Any, Tuple, Optional
from ..learners.homogeneity_learner import HomogeneityLearner


class OperationPrediction:
    """Container for operation prediction results"""

    def __init__(self, operation: str, parameters: Dict[str, Any], confidence: float,
                 expected_improvement: float, reasoning: str):
        self.operation = operation
        self.parameters = parameters
        self.confidence = confidence
        self.expected_improvement = expected_improvement
        self.reasoning = reasoning


class OperationPredictor:
    """
    Predicts optimal operations for improving binary homogeneity
    Uses historical learning and pattern recognition
    """

    def __init__(self, learner: HomogeneityLearner):
        self.learner = learner

    def predict_next_operation(self, data: bytes, current_score: float,
                              max_sequence_length: int = 3) -> List[OperationPrediction]:
        """
        Predict the next best operations for homogeneity improvement
        Returns multiple ranked predictions
        """

        predictions = []
        data_type = self.learner.analyze_data_characteristics(data)

        # Get primary recommendation from learner
        primary_op, primary_params, confidence = self.learner.recommend_operation(data, current_score)

        # Create primary prediction
        expected_improvement = self._estimate_improvement(primary_op, data_type, current_score)
        reasoning = self._generate_reasoning(primary_op, data_type, confidence)

        primary_prediction = OperationPrediction(
            operation=primary_op,
            parameters=primary_params,
            confidence=confidence,
            expected_improvement=expected_improvement,
            reasoning=reasoning
        )
        predictions.append(primary_prediction)

        # Generate alternative predictions
        alternatives = self._generate_alternative_predictions(data, data_type, current_score, primary_op)
        predictions.extend(alternatives)

        # Sort by expected improvement and confidence
        predictions.sort(key=lambda p: (p.expected_improvement * p.confidence), reverse=True)

        return predictions[:max_sequence_length]

    def _estimate_improvement(self, operation: str, data_type: str, current_score: float) -> float:
        """Estimate expected improvement for an operation"""

        # Use historical performance if available
        if operation in self.learner.performance_model.operation_stats:
            stats = self.learner.performance_model.operation_stats[operation]
            return stats['avg_improvement']

        # Use heuristic estimation based on operation type and data type
        heuristic_improvements = {
            ('xor_constant', 'random'): 0.05,
            ('xor_constant', 'mixed'): 0.03,
            ('add_constant', 'near_uniform'): 0.08,
            ('add_constant', 'random'): 0.04,
            ('rotate_left', 'pattern'): 0.06,
            ('rotate_left', 'repetitive'): 0.04,
            ('substitute_bytes', 'repetitive'): 0.10,
            ('substitute_bytes', 'structured'): 0.07,
            ('move_to_front', 'mixed'): 0.05,
            ('reverse_bytes', 'pattern'): 0.06,
            ('shuffle_bytes', 'random'): 0.03
        }

        return heuristic_improvements.get((operation, data_type), 0.02)

    def _generate_reasoning(self, operation: str, data_type: str, confidence: float) -> str:
        """Generate human-readable reasoning for operation recommendation"""

        operation_descriptions = {
            'xor_constant': 'XOR operation creates or enhances patterns',
            'add_constant': 'Addition shifts byte values toward uniformity',
            'rotate_left': 'Rotation reorganizes bit patterns',
            'substitute_bytes': 'Substitution replaces patterns with more uniform ones',
            'move_to_front': 'Move-to-front groups similar bytes together',
            'reverse_bytes': 'Reversal can reveal hidden patterns',
            'shuffle_bytes': 'Shuffling reorganizes data structure'
        }

        data_type_insights = {
            'random': 'Random data benefits from pattern-creating operations',
            'repetitive': 'Repetitive data needs structure reorganization',
            'pattern': 'Patterned data benefits from transformation operations',
            'near_uniform': 'Near-uniform data needs gentle modifications',
            'mixed': 'Mixed data benefits from organization operations'
        }

        base_reasoning = operation_descriptions.get(operation, 'Operation selected based on learned patterns')
        data_insight = data_type_insights.get(data_type, 'Optimized for current data characteristics')

        confidence_qualifier = 'high confidence' if confidence > 0.7 else 'moderate confidence' if confidence > 0.4 else 'low confidence'

        return f"{base_reasoning}. {data_insight}. Recommendation based on {confidence_qualifier}."

    def _generate_alternative_predictions(self, data: bytes, data_type: str,
                                        current_score: float, exclude_operation: str) -> List[OperationPrediction]:
        """Generate alternative operation predictions"""

        alternatives = []
        operation_library = self.learner.operation_library

        # Get operations that are effective for this data type
        effective_operations = []
        for op, info in operation_library.items():
            if op != exclude_operation and data_type in info.get('effective_for', []):
                effective_operations.append(op)

        # If no specific effective operations, use general ones
        if not effective_operations:
            effective_operations = list(operation_library.keys())[:3]
            if exclude_operation in effective_operations:
                effective_operations.remove(exclude_operation)

        # Generate predictions for alternatives
        for operation in effective_operations[:2]:  # Limit to 2 alternatives
            params = self._get_default_parameters(operation)
            confidence = 0.3  # Lower confidence for alternatives
            expected_improvement = self._estimate_improvement(operation, data_type, current_score)
            reasoning = self._generate_reasoning(operation, data_type, confidence)

            alternative = OperationPrediction(
                operation=operation,
                parameters=params,
                confidence=confidence,
                expected_improvement=expected_improvement,
                reasoning=reasoning
            )
            alternatives.append(alternative)

        return alternatives

    def _get_default_parameters(self, operation: str) -> Dict[str, Any]:
        """Get default parameters for an operation"""

        operation_library = self.learner.operation_library
        if operation not in operation_library:
            return {}

        param_ranges = operation_library[operation].get('parameter_ranges', {})
        default_params = {}

        for param, values in param_ranges.items():
            if isinstance(values, list) and values:
                default_params[param] = values[0]  # Use first value as default
            else:
                default_params[param] = values

        return default_params

    def predict_sequence(self, data: bytes, current_score: float,
                        max_length: int = 3) -> List[OperationPrediction]:
        """
        Predict a sequence of operations for maximum homogeneity improvement
        """

        sequence = []
        remaining_length = max_length
        current_data = data
        current_homogeneity = current_score

        while remaining_length > 0:
            # Predict next operation
            predictions = self.predict_next_operation(current_data, current_homogeneity, 1)

            if not predictions:
                break

            best_prediction = predictions[0]

            # Only add operation if it's expected to improve
            if best_prediction.expected_improvement > 0.01:
                sequence.append(best_prediction)

                # Simulate the operation effect for next prediction
                current_homogeneity += best_prediction.expected_improvement
                remaining_length -= 1
            else:
                break

        return sequence

    def get_prediction_summary(self, predictions: List[OperationPrediction]) -> Dict[str, Any]:
        """Get a summary of operation predictions"""

        if not predictions:
            return {
                'total_predictions': 0,
                'top_operation': None,
                'total_expected_improvement': 0.0,
                'average_confidence': 0.0
            }

        return {
            'total_predictions': len(predictions),
            'top_operation': {
                'operation': predictions[0].operation,
                'parameters': predictions[0].parameters,
                'confidence': predictions[0].confidence,
                'expected_improvement': predictions[0].expected_improvement,
                'reasoning': predictions[0].reasoning
            },
            'all_predictions': [
                {
                    'operation': p.operation,
                    'parameters': p.parameters,
                    'confidence': p.confidence,
                    'expected_improvement': p.expected_improvement,
                    'reasoning': p.reasoning
                }
                for p in predictions
            ],
            'total_expected_improvement': sum(p.expected_improvement for p in predictions),
            'average_confidence': sum(p.confidence for p in predictions) / len(predictions)
        }