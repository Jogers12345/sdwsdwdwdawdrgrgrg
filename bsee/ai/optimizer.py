"""
AI/ML-based operation sequence optimizer for BSEE.
Learns optimal operation sequences from historical data.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from pathlib import Path

from .features import FeatureExtractor, DataFeatures
from .data import DataCollector, DataLoader, TrainingExample


@dataclass
class OptimizationResult:
    """Result of operation sequence optimization."""
    best_sequence: List[Dict[str, Any]]
    predicted_score: float
    confidence: float
    alternative_sequences: List[Tuple[List[Dict[str, Any]], float]]
    optimization_time: float
    metadata: Dict[str, Any]


@dataclass
class SequenceCandidate:
    """Candidate operation sequence with predicted performance."""
    sequence: List[Dict[str, Any]]
    predicted_score: float
    confidence: float
    features: Dict[str, Any]


class OperationSequenceOptimizer:
    """
    AI-powered optimizer for operation sequences.
    Learns from historical data to predict optimal sequences.
    """

    def __init__(self, model_path: Optional[str] = None,
                 data_collector: Optional[DataCollector] = None):
        """
        Initialize the optimizer.

        Args:
            model_path: Path to saved model file
            data_collector: Data collector for training data
        """
        self.logger = logging.getLogger(__name__)
        self.feature_extractor = FeatureExtractor()
        self.data_collector = data_collector or DataCollector()
        self.data_loader = DataLoader(self.data_collector)

        # ML models
        self.performance_model = None
        self.scaler = None
        self.model_trained = False

        # Available operations
        self.available_operations = self._get_available_operations()

        # Optimization parameters
        self.max_sequence_length = 10
        self.candidate_count = 100
        self.diversity_threshold = 0.3

        # Load model if provided
        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    def _get_available_operations(self) -> List[Dict[str, Any]]:
        """Get list of available operations with parameters."""
        # This should be integrated with the actual BSEE operations registry
        operations = [
            {'type': 'xor', 'parameters': {'key': 42}},
            {'type': 'xor', 'parameters': {'key': 0xFF}},
            {'type': 'add_constant', 'parameters': {'value': 10}},
            {'type': 'add_constant', 'parameters': {'value': 100}},
            {'type': 'rotate_left', 'parameters': {'bits': 1}},
            {'type': 'rotate_left', 'parameters': {'bits': 2}},
            {'type': 'rotate_left', 'parameters': {'bits': 4}},
            {'type': 'substitute', 'parameters': {'mapping': {0: 1, 1: 0}}},
            {'type': 'burrows_wheeler', 'parameters': {}},
            {'type': 'move_to_front', 'parameters': {}},
            {'type': 'huffman_encode', 'parameters': {}},
            {'type': 'run_length_encode', 'parameters': {}},
            {'type': 'distance_coding', 'parameters': {}},
        ]
        return operations

    def train_model(self, min_examples: int = 100) -> bool:
        """
        Train the performance prediction model.

        Args:
            min_examples: Minimum number of training examples required

        Returns:
            True if training was successful, False otherwise
        """
        try:
            self.logger.info("Starting model training...")

            # Load training data
            X_train, y_train, X_val, y_val = self.data_loader.load_training_data(
                limit=10000,
                min_score=0.3,
                validation_split=0.2
            )

            if len(X_train) < min_examples:
                self.logger.warning(f"Insufficient training data: {len(X_train)} < {min_examples}")
                return False

            self.logger.info(f"Training with {len(X_train)} examples")

            # Train multiple models and select the best
            models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                ),
                'gradient_boosting': GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            }

            best_model = None
            best_score = -float('inf')
            best_name = ""

            for name, model in models.items():
                # Cross-validation
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                avg_score = cv_scores.mean()

                self.logger.info(f"{name} CV R² score: {avg_score:.3f}")

                if avg_score > best_score:
                    # Train on full training set
                    model.fit(X_train, y_train)

                    # Evaluate on validation set
                    val_pred = model.predict(X_val)
                    val_r2 = r2_score(y_val, val_pred)
                    val_mse = mean_squared_error(y_val, val_pred)

                    self.logger.info(f"{name} validation R²: {val_r2:.3f}, MSE: {val_mse:.3f}")

                    if val_r2 > best_score:
                        best_score = val_r2
                        best_model = model
                        best_name = name

            if best_model is None:
                self.logger.error("No model could be trained successfully")
                return False

            self.performance_model = best_model
            self.scaler = self.data_loader.scaler
            self.model_trained = True

            self.logger.info(f"Best model: {best_name} with R²: {best_score:.3f}")

            # Record model performance
            from .data import ModelPerformance
            performance = ModelPerformance(
                model_name=f"sequence_optimizer_{best_name}",
                model_version="1.0",
                accuracy=best_score,
                precision=0.0,  # Not applicable for regression
                recall=0.0,     # Not applicable for regression
                f1_score=best_score,
                mse=mean_squared_error(y_val, best_model.predict(X_val))
            )
            self.data_collector.record_model_performance(performance)

            return True

        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
            return False

    def predict_sequence_performance(self, sequence: List[Dict[str, Any]],
                                   data_features: DataFeatures) -> Tuple[float, float]:
        """
        Predict performance of an operation sequence.

        Args:
            sequence: Operation sequence to evaluate
            data_features: Features of input data

        Returns:
            Tuple of (predicted_score, confidence)
        """
        if not self.model_trained:
            self.logger.warning("Model not trained, returning default score")
            return 0.5, 0.0

        try:
            # Extract sequence features
            sequence_features = self.feature_extractor.extract_sequence_features(
                sequence, data_features
            )

            # Create feature vector
            feature_vector = self.data_loader.load_prediction_data(
                data_features.__dict__, sequence_features
            )

            # Predict performance
            predicted_score = self.performance_model.predict(feature_vector)[0]

            # Estimate confidence based on prediction variance (if available)
            if hasattr(self.performance_model, 'estimators_'):
                # For Random Forest - use prediction variance
                predictions = np.array([
                    estimator.predict(feature_vector)[0]
                    for estimator in self.performance_model.estimators_
                ])
                confidence = 1.0 - np.std(predictions) / (np.abs(predicted_score) + 1e-6)
                confidence = max(0.0, min(1.0, confidence))
            else:
                # Default confidence based on training data similarity
                confidence = 0.7

            # Clamp score to valid range
            predicted_score = max(0.0, min(1.0, predicted_score))

            return predicted_score, confidence

        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return 0.5, 0.0

    def optimize_sequence(self, input_data: bytes,
                         constraints: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Find optimal operation sequence for given input data.

        Args:
            input_data: Input binary data
            constraints: Optimization constraints

        Returns:
            OptimizationResult with best sequence and alternatives
        """
        start_time = datetime.now()

        try:
            # Extract data features
            data_features = self.feature_extractor.extract_data_features(input_data)

            # Generate candidate sequences
            candidates = self._generate_candidates(data_features, constraints)

            # Evaluate candidates
            evaluated_candidates = []
            for candidate in candidates:
                score, confidence = self.predict_sequence_performance(
                    candidate.sequence, data_features
                )
                evaluated_candidates.append(SequenceCandidate(
                    sequence=candidate.sequence,
                    predicted_score=score,
                    confidence=confidence,
                    features=candidate.features
                ))

            # Sort by predicted performance
            evaluated_candidates.sort(
                key=lambda x: x.predicted_score * x.confidence,
                reverse=True
            )

            if not evaluated_candidates:
                # Fallback to simple sequence
                fallback_sequence = [{'type': 'xor', 'parameters': {'key': 42}}]
                return OptimizationResult(
                    best_sequence=fallback_sequence,
                    predicted_score=0.5,
                    confidence=0.0,
                    alternative_sequences=[],
                    optimization_time=(datetime.now() - start_time).total_seconds(),
                    metadata={'fallback': True}
                )

            # Select best and alternatives
            best_candidate = evaluated_candidates[0]
            alternatives = [
                (c.sequence, c.predicted_score * c.confidence)
                for c in evaluated_candidates[1:6]  # Top 5 alternatives
            ]

            optimization_time = (datetime.now() - start_time).total_seconds()

            result = OptimizationResult(
                best_sequence=best_candidate.sequence,
                predicted_score=best_candidate.predicted_score,
                confidence=best_candidate.confidence,
                alternative_sequences=alternatives,
                optimization_time=optimization_time,
                metadata={
                    'candidates_evaluated': len(evaluated_candidates),
                    'data_features': {
                        'size': data_features.size,
                        'entropy': data_features.entropy,
                        'data_type': max(data_features.data_type_score.items(),
                                        key=lambda x: x[1])[0] if data_features.data_type_score else 'unknown'
                    }
                }
            )

            self.logger.info(f"Optimization completed in {optimization_time:.2f}s, "
                           f"best score: {best_candidate.predicted_score:.3f}")

            return result

        except Exception as e:
            self.logger.error(f"Sequence optimization failed: {e}")
            # Return fallback
            fallback_sequence = [{'type': 'xor', 'parameters': {'key': 42}}]
            return OptimizationResult(
                best_sequence=fallback_sequence,
                predicted_score=0.5,
                confidence=0.0,
                alternative_sequences=[],
                optimization_time=(datetime.now() - start_time).total_seconds(),
                metadata={'error': str(e), 'fallback': True}
            )

    def _generate_candidates(self, data_features: DataFeatures,
                           constraints: Optional[Dict[str, Any]] = None) -> List[SequenceCandidate]:
        """Generate candidate operation sequences."""
        candidates = []
        constraints = constraints or {}

        # Adapt sequence length based on data size
        data_size = data_features.size
        if data_size < 1024:  # < 1KB
            max_length = 3
        elif data_size < 10240:  # < 10KB
            max_length = 5
        else:
            max_length = min(8, self.max_sequence_length)

        # Generate candidates based on data type
        data_type = max(data_features.data_type_score.items(),
                       key=lambda x: x[1])[0] if data_features.data_type_score else 'binary'

        if data_type == 'text':
            candidates.extend(self._generate_text_candidates(max_length))
        elif data_type == 'compressed':
            candidates.extend(self._generate_decompression_candidates(max_length))
        elif data_type == 'encrypted':
            candidates.extend(self._generate_crypto_candidates(max_length))
        elif data_type == 'structured':
            candidates.extend(self._generate_structured_candidates(max_length))
        else:
            candidates.extend(self._generate_general_candidates(max_length))

        # Add some random candidates for diversity
        candidates.extend(self._generate_random_candidates(
            count=max(10, self.candidate_count // 4),
            max_length=max_length
        ))

        # Filter by constraints
        if constraints:
            candidates = self._filter_candidates_by_constraints(candidates, constraints)

        # Ensure diversity
        candidates = self._ensure_diversity(candidates)

        return candidates[:self.candidate_count]

    def _generate_text_candidates(self, max_length: int) -> List[SequenceCandidate]:
        """Generate candidates optimized for text data."""
        candidates = []

        # Simple transformations for text
        text_ops = [
            [{'type': 'xor', 'parameters': {'key': 32}}],  # Toggle case
            [{'type': 'xor', 'parameters': {'key': 0x20}}],  # Space manipulation
            [{'type': 'add_constant', 'parameters': {'value': 1}}],  # Simple shift
            [{'type': 'move_to_front', 'parameters': {}}],  # Local optimization
            [{'type': 'distance_coding', 'parameters': {}}],  # Position encoding
        ]

        for ops in text_ops:
            for length in range(1, min(max_length, 3) + 1):
                if length == 1:
                    candidates.append(SequenceCandidate(
                        sequence=ops,
                        predicted_score=0.0,
                        confidence=0.0,
                        features={'type': 'text', 'length': length}
                    ))
                else:
                    # Add compression for longer sequences
                    extended_ops = ops + [{'type': 'huffman_encode', 'parameters': {}}]
                    candidates.append(SequenceCandidate(
                        sequence=extended_ops,
                        predicted_score=0.0,
                        confidence=0.0,
                        features={'type': 'text_compressed', 'length': length}
                    ))

        return candidates

    def _generate_decompression_candidates(self, max_length: int) -> List[SequenceCandidate]:
        """Generate candidates for compressed data."""
        candidates = []

        decompression_ops = [
            [{'type': 'huffman_decode', 'parameters': {}}],
            [{'type': 'lz77_decode', 'parameters': {}}],
            [{'type': 'run_length_decode', 'parameters': {}}],
        ]

        for ops in decompression_ops:
            candidates.append(SequenceCandidate(
                sequence=ops,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'decompression', 'length': 1}
            ))

            # Add follow-up transformations
            follow_up_ops = ops + [{'type': 'burrows_wheeler_inverse', 'parameters': {}}]
            candidates.append(SequenceCandidate(
                sequence=follow_up_ops,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'decompression_followup', 'length': 2}
            ))

        return candidates

    def _generate_crypto_candidates(self, max_length: int) -> List[SequenceCandidate]:
        """Generate candidates for encrypted data."""
        candidates = []

        # Common crypto patterns
        crypto_patterns = [
            [{'type': 'xor', 'parameters': {'key': 0x42}}],  # Common XOR key
            [{'type': 'xor', 'parameters': {'key': 0xFF}}],  # Inversion
            [{'type': 'xor', 'parameters': {'key': 0xAA}}],  # Alternating pattern
            [{'type': 'add_constant', 'parameters': {'value': 1}}],  # Simple shift
            [{'type': 'rotate_left', 'parameters': {'bits': 1}}],  # Bit rotation
        ]

        for ops in crypto_patterns:
            candidates.append(SequenceCandidate(
                sequence=ops,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'crypto', 'length': 1}
            ))

        # Multi-step crypto analysis
        for i in range(2, min(max_length, 4) + 1):
            multi_step = crypto_patterns[:i]
            candidates.append(SequenceCandidate(
                sequence=multi_step,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'multi_crypto', 'length': i}
            ))

        return candidates

    def _generate_structured_candidates(self, max_length: int) -> List[SequenceCandidate]:
        """Generate candidates for structured data."""
        candidates = []

        structured_ops = [
            [{'type': 'burrows_wheeler', 'parameters': {}}],
            [{'type': 'move_to_front', 'parameters': {}}],
            [{'type': 'distance_coding', 'parameters': {}}],
        ]

        for ops in structured_ops:
            candidates.append(SequenceCandidate(
                sequence=ops,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'structured', 'length': 1}
            ))

            # Add compression for structured data
            extended_ops = ops + [{'type': 'arithmetic_coding', 'parameters': {}}]
            candidates.append(SequenceCandidate(
                sequence=extended_ops,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'structured_compressed', 'length': 2}
            ))

        return candidates

    def _generate_general_candidates(self, max_length: int) -> List[SequenceCandidate]:
        """Generate general-purpose candidates."""
        candidates = []

        # Simple operation combinations
        base_sequences = [
            [{'type': 'xor', 'parameters': {'key': 42}}],
            [{'type': 'add_constant', 'parameters': {'value': 10}}],
            [{'type': 'rotate_left', 'parameters': {'bits': 2}}],
            [{'type': 'burrows_wheeler', 'parameters': {}}],
            [{'type': 'move_to_front', 'parameters': {}}],
        ]

        # Single operations
        for ops in base_sequences:
            candidates.append(SequenceCandidate(
                sequence=ops,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'single', 'operation': ops[0]['type']}
            ))

        # Two-operation combinations
        for i, ops1 in enumerate(base_sequences):
            for ops2 in base_sequences[i+1:]:
                combined = ops1 + ops2
                candidates.append(SequenceCandidate(
                    sequence=combined,
                    predicted_score=0.0,
                    confidence=0.0,
                    features={'type': 'double', 'ops': [ops1[0]['type'], ops2[0]['type']]}
                ))

        return candidates

    def _generate_random_candidates(self, count: int, max_length: int) -> List[SequenceCandidate]:
        """Generate random candidates for diversity."""
        candidates = []

        for _ in range(count):
            length = np.random.randint(1, max_length + 1)
            sequence = []

            for _ in range(length):
                op = np.random.choice(self.available_operations)
                sequence.append(op.copy())

            candidates.append(SequenceCandidate(
                sequence=sequence,
                predicted_score=0.0,
                confidence=0.0,
                features={'type': 'random', 'length': length}
            ))

        return candidates

    def _filter_candidates_by_constraints(self, candidates: List[SequenceCandidate],
                                        constraints: Dict[str, Any]) -> List[SequenceCandidate]:
        """Filter candidates based on constraints."""
        filtered = []

        max_time = constraints.get('max_time', float('inf'))
        max_complexity = constraints.get('max_complexity', float('inf'))
        allowed_operations = constraints.get('allowed_operations', None)

        for candidate in candidates:
            # Check time constraint
            total_time = sum(
                self.feature_extractor._estimate_operation_runtime(
                    op['type'], op.get('parameters', {})
                ) for op in candidate.sequence
            )
            if total_time > max_time:
                continue

            # Check complexity constraint
            total_complexity = sum(
                self.feature_extractor._calculate_operation_complexity(
                    op['type'], op.get('parameters', {})
                ) for op in candidate.sequence
            )
            if total_complexity > max_complexity:
                continue

            # Check allowed operations
            if allowed_operations:
                sequence_ops = [op['type'] for op in candidate.sequence]
                if not any(op in allowed_operations for op in sequence_ops):
                    continue

            filtered.append(candidate)

        return filtered

    def _ensure_diversity(self, candidates: List[SequenceCandidate]) -> List[SequenceCandidate]:
        """Ensure diversity in candidate pool."""
        if len(candidates) <= 10:
            return candidates

        diverse_candidates = [candidates[0]]  # Always keep the best one

        for candidate in candidates[1:]:
            # Check if this candidate is sufficiently different from existing ones
            is_diverse = True

            for existing in diverse_candidates:
                similarity = self._calculate_similarity(candidate, existing)
                if similarity > self.diversity_threshold:
                    is_diverse = False
                    break

            if is_diverse:
                diverse_candidates.append(candidate)

            if len(diverse_candidates) >= self.candidate_count:
                break

        return diverse_candidates

    def _calculate_similarity(self, candidate1: SequenceCandidate,
                            candidate2: SequenceCandidate) -> float:
        """Calculate similarity between two candidates."""
        # Compare operation types
        ops1 = [op['type'] for op in candidate1.sequence]
        ops2 = [op['type'] for op in candidate2.sequence]

        # Jaccard similarity
        set1, set2 = set(ops1), set(ops2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union

    def save_model(self, model_path: str) -> bool:
        """
        Save trained model to file.

        Args:
            model_path: Path to save model

        Returns:
            True if successful, False otherwise
        """
        if not self.model_trained:
            self.logger.warning("No trained model to save")
            return False

        try:
            model_data = {
                'model': self.performance_model,
                'scaler': self.scaler,
                'feature_names': self.data_loader.feature_names,
                'metadata': {
                    'trained_at': datetime.now().isoformat(),
                    'model_type': type(self.performance_model).__name__
                }
            }

            joblib.dump(model_data, model_path)
            self.logger.info(f"Model saved to {model_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            return False

    def load_model(self, model_path: str) -> bool:
        """
        Load trained model from file.

        Args:
            model_path: Path to model file

        Returns:
            True if successful, False otherwise
        """
        try:
            model_data = joblib.load(model_path)

            self.performance_model = model_data['model']
            self.scaler = model_data['scaler']
            self.data_loader.scaler = self.scaler
            self.data_loader.feature_names = model_data['feature_names']
            self.model_trained = True

            self.logger.info(f"Model loaded from {model_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.model_trained:
            return {'trained': False}

        return {
            'trained': True,
            'model_type': type(self.performance_model).__name__,
            'feature_count': len(self.data_loader.feature_names) if self.data_loader.feature_names else 0,
            'available_operations': len(self.available_operations),
            'max_sequence_length': self.max_sequence_length
        }