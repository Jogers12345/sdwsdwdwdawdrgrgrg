"""
Prediction interface for BSEE AI/ML operations.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from .features import FeatureExtractor, DataFeatures
from .optimizer import OperationSequenceOptimizer, OptimizationResult


class SequencePredictor:
    """
    High-level interface for predicting optimal operation sequences.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize sequence predictor.

        Args:
            model_path: Path to trained model file
        """
        self.logger = logging.getLogger(__name__)
        self.feature_extractor = FeatureExtractor()
        self.optimizer = OperationSequenceOptimizer(model_path=model_path)

    def predict_best_sequence(self, input_data: bytes,
                            constraints: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Predict the best operation sequence for given input data.

        Args:
            input_data: Input binary data
            constraints: Optional constraints for optimization

        Returns:
            OptimizationResult with best sequence and metadata
        """
        return self.optimizer.optimize_sequence(input_data, constraints)

    def predict_sequence_performance(self, sequence: List[Dict[str, Any]],
                                   input_data: bytes) -> Tuple[float, float]:
        """
        Predict performance of a specific operation sequence.

        Args:
            sequence: Operation sequence to evaluate
            input_data: Input binary data

        Returns:
            Tuple of (predicted_score, confidence)
        """
        data_features = self.feature_extractor.extract_data_features(input_data)
        return self.optimizer.predict_sequence_performance(sequence, data_features)

    def analyze_input_data(self, input_data: bytes) -> Dict[str, Any]:
        """
        Analyze input data and return characteristics.

        Args:
            input_data: Input binary data

        Returns:
            Dictionary with data analysis results
        """
        features = self.feature_extractor.extract_data_features(input_data)

        return {
            'size_bytes': features.size,
            'entropy': features.entropy,
            'compression_ratio_estimate': features.compression_ratio_estimate,
            'pattern_repetition': features.pattern_repetition,
            'data_type_classification': features.data_type_score,
            'structural_features': features.structural_features,
            'recommended_operations': self._get_recommended_operations(features),
            'processing_difficulty': self._assess_processing_difficulty(features)
        }

    def _get_recommended_operations(self, features: DataFeatures) -> List[str]:
        """Get recommended operations based on data features."""
        recommendations = []

        # Based on data type
        if features.data_type_score:
            primary_type = max(features.data_type_score.items(), key=lambda x: x[1])[0]

            if primary_type == 'text':
                recommendations.extend(['xor', 'add_constant', 'move_to_front'])
            elif primary_type == 'compressed':
                recommendations.extend(['huffman_decode', 'lz77_decode', 'burrows_wheeler_inverse'])
            elif primary_type == 'encrypted':
                recommendations.extend(['xor', 'rotate_left', 'add_constant'])
            elif primary_type == 'structured':
                recommendations.extend(['burrows_wheeler', 'move_to_front', 'distance_coding'])

        # Based on entropy
        if features.entropy > 7.0:
            recommendations.extend(['simple_transforms'])
        elif features.entropy < 3.0:
            recommendations.extend(['compression'])

        # Based on pattern repetition
        if features.pattern_repetition > 0.5:
            recommendations.extend(['run_length_encode', 'move_to_front'])

        return list(set(recommendations))

    def _assess_processing_difficulty(self, features: DataFeatures) -> str:
        """Assess processing difficulty based on data features."""
        difficulty_score = 0

        # Size-based difficulty
        if features.size > 1024 * 1024:  # > 1MB
            difficulty_score += 3
        elif features.size > 10240:  # > 10KB
            difficulty_score += 2
        elif features.size > 1024:  # > 1KB
            difficulty_score += 1

        # Entropy-based difficulty
        if features.entropy > 7.5:
            difficulty_score += 2
        elif features.entropy > 6.0:
            difficulty_score += 1

        # Pattern-based difficulty
        if features.pattern_repetition < 0.1:
            difficulty_score += 1

        if difficulty_score >= 5:
            return "hard"
        elif difficulty_score >= 3:
            return "medium"
        else:
            return "easy"

    def is_model_available(self) -> bool:
        """Check if a trained model is available."""
        return self.optimizer.model_trained

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return self.optimizer.get_model_info()