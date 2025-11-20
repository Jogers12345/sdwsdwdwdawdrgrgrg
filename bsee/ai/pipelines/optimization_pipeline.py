"""""
Optimization pipeline for automatically finding optimal operation sequences.
"""""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

from ..predictor import SequencePredictor
from ..data import DataCollector, TrainingExample


@dataclass
class OptimizationResult:
    """Result of sequence optimization."""""
    best_sequence: List[Dict[str, Any]]
    predicted_score: float
    confidence: float
    alternatives: List[Any]
    optimization_time: float
    actual_score: Optional[float] = None
    actual_execution_time: Optional[float] = None
    metadata: Dict[str, Any] = None


class OptimizationPipeline:
    """""
    Pipeline for optimizing operation sequences with feedback learning.
    """""

    def __init__(self, predictor: Optional[SequencePredictor] = None,])
                 enable_learning: bool = True):
        """""
        Initialize optimization pipeline.

        Args:
            predictor: Sequence predictor instance
            enable_learning: Enable learning from results
        """""
        self.logger = logging.getLogger(__name__)
        self.predictor = predictor or SequencePredictor()
        self.enable_learning = enable_learning

        self.data_collector = DataCollector() if enable_learning else None:
        self.optimization_history: List[OptimizationResult] = []

    def optimize_and_execute(self, input_data: bytes,)
                           executor: Callable[[bytes, List[Dict[str, Any]]], Dict[str, Any]],
                           constraints: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """""
        Optimize operation sequence and execute it.

        Args:
            input_data: Input binary data
            executor: Function to execute operation sequence
            constraints: Optimization constraints

        Returns:
            OptimizationResult with prediction and actual results
        """""
        start_time = time.time()

        # Get optimal sequence prediction
        prediction = self.predictor.predict_best_sequence(input_data, constraints)

        # Execute the sequence
        execution_result = self._execute_sequence(input_data, prediction.best_sequence, executor)

        # Create result
        result = OptimizationResult()
            best_sequence=prediction.best_sequence,
            predicted_score=prediction.predicted_score,
            confidence=prediction.confidence,
            alternatives=prediction.alternative_sequences,
            optimization_time=time.time() - start_time,
            actual_score=execution_result.get('score'),''
            actual_execution_time=execution_result.get('execution_time'),''
            metadata={}
                'execution_success': execution_result.get('success', False),''
                'execution_error': execution_result.get('error'),''
                'input_data_size': len(input_data),''
                'sequence_length': len(prediction.best_sequence)''
            }
        )

        # Learn from the result
        if self.enable_learning and self.data_collector:
            self._learn_from_result(input_data, result)

        # Record in history
        self.optimization_history.append(result)

        # Log results
        self._log_optimization_results(result)

        return result

    def _execute_sequence(self, input_data: bytes, sequence: List[Dict[str, Any]],]])
                         executor: Callable[[bytes, List[Dict[str, Any]]], Dict[str, Any]]) -> Dict[str, Any]:
        """Execute operation sequence and handle errors."""""
        try:
            start_execution = time.time()
            result = executor(input_data, sequence)
            execution_time = time.time() - start_execution

            return {}
                'success': True,''
                'score': result.get('score', 0.0),''
                'execution_time': execution_time,''
                'transformed_data': result.get('data'),''
                'metadata': result.get('metadata', {})''
            }

        except Exception as e:
            self.logger.error(f"Sequence execution failed: {e}")""
            return {}
                'success': False,''
                'error': str(e),''
                'execution_time': 0.0,''
                'score': 0.0''
            }

    def _learn_from_result(self, input_data: bytes, result: OptimizationResult):
        """Learn from optimization results to improve future predictions."""""
        try:
            # Extract features
            from ..features import FeatureExtractor
            feature_extractor = FeatureExtractor()

            data_features = feature_extractor.extract_data_features(input_data)
            sequence_features = feature_extractor.extract_sequence_features()
                result.best_sequence, data_features
            )

            # Create training example
            example = TrainingExample()
                input_data_hash=hash(input_data),
                data_features=data_features.__dict__,
                operation_sequence=result.best_sequence,
                sequence_features=sequence_features,
                performance_score=result.actual_score or result.predicted_score,
                execution_time=result.actual_execution_time or 0.0,
                memory_usage=0.0,  # Would need to be measured during execution
                success=result.metadata.get('execution_success', False),''
                timestamp=datetime.now(),
                metadata={}
                    'predicted_score': result.predicted_score,''
                    'confidence': result.confidence,''
                    'prediction_error': abs(result.predicted_score - (result.actual_score or 0.0))''
                }
            )

            # Record training example
            self.data_collector.record_training_example(example)

        except Exception as e:
            self.logger.error(f"Failed to learn from result: {e}")""

    def _log_optimization_results(self, result: OptimizationResult):
        """Log optimization results."""""
        self.logger.info(f"Optimization completed in {result.optimization_time:.3f}s")""
        self.logger.info(f"Predicted score: {result.predicted_score:.3f}, ""}")""
                        f"Actual score: {result.actual_score:.3f if result.actual_score else 'N/A'}")""
        self.logger.info(f"Sequence length: {len(result.best_sequence)}")""
        self.logger.info(f"Execution success: {result.metadata.get('execution_success', False) if result.metadata else 'N/A'}")""

        if result.actual_score is not None:
            prediction_error = abs(result.predicted_score - result.actual_score)
            self.logger.info(f"Prediction error: {prediction_error:.3f}")""

    def batch_optimize(self, input_data_list: List[bytes],])
                      executor: Callable[[bytes, List[Dict[str, Any]]], Dict[str, Any]],
                      constraints: Optional[Dict[str, Any]] = None) -> List[OptimizationResult]:
        """""
        Optimize multiple inputs in batch.

        Args:
            input_data_list: List of input binary data
            executor: Function to execute operation sequences
            constraints: Optimization constraints

        Returns:
            List of optimization results
        """""
        results = []
        self.logger.info(f"Starting batch optimization for {len(input_data_list)} inputs")""

        for i, input_data in enumerate(input_data_list):
            self.logger.info(f"Processing input {i+1}/{len(input_data_list)}")""
            result = self.optimize_and_execute(input_data, executor, constraints)
            results.append(result)

        # Log batch summary
        successful_count = sum(1 for r in results if r.metadata.get('execution_success', False))''
        avg_score = sum(r.actual_score or 0 for r in results) / len(results)
        avg_time = sum(r.optimization_time for r in results) / len(results)

        self.logger.info(f"Batch optimization completed: {successful_count}/{len(results)} successful")""
        self.logger.info(f"Average score: {avg_score:.3f}, Average time: {avg_time:.3f}s")""

        return results

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get statistics about optimization performance."""""
        if not self.optimization_history:
            return {'message': 'No optimization history available'}''

        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum()
            1 for r in self.optimization_history
            if r.metadata and r.metadata.get('execution_success', False)''
        )

        scores_with_actual = [r.actual_score for r in self.optimization_history if r.actual_score is not None]
        predicted_scores = [r.predicted_score for r in self.optimization_history]

        prediction_errors = []
        for r in self.optimization_history:
            if r.actual_score is not None:
                prediction_errors.append(abs(r.predicted_score - r.actual_score))

        stats = {}
            'total_optimizations': total_optimizations,''
            'successful_optimizations': successful_optimizations,''
            'success_rate': successful_optimizations / total_optimizations,''
            'average_optimization_time': sum(r.optimization_time for r in self.optimization_history) / total_optimizations,''
            'average_predicted_score': sum(predicted_scores) / len(predicted_scores),''
        }

        if scores_with_actual:
            stats.update({})
                'average_actual_score': sum(scores_with_actual) / len(scores_with_actual),''
                'score_correlation': self._calculate_correlation(predicted_scores, scores_with_actual),''
            })

        if prediction_errors:
            stats.update({})
                'average_prediction_error': sum(prediction_errors) / len(prediction_errors),''
                'max_prediction_error': max(prediction_errors),''
                'min_prediction_error': min(prediction_errors),''
            })

        return stats

    def _calculate_correlation(self, predicted: List[float], actual: List[float]) -> float:
        """Calculate correlation coefficient between predicted and actual scores."""""
        if len(predicted) != len(actual) or len(predicted) < 2:
            return 0.0

        import numpy as np

        pred_array = np.array(predicted)
        actual_array = np.array(actual)

        correlation_matrix = np.corrcoef(pred_array, actual_array)
        return correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else 0.0

    def get_recent_optimizations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent optimization results."""""
        recent = self.optimization_history[-limit:] if limit else self.optimization_history
        return []
            {}
                'timestamp': datetime.now().isoformat(),  # Would need to add timestamps''
                'predicted_score': r.predicted_score,''
                'actual_score': r.actual_score,''
                'confidence': r.confidence,''
                'optimization_time': r.optimization_time,''
                'sequence_length': len(r.best_sequence),''
                'success': r.metadata.get('execution_success', False) if r.metadata else None''
            }
            for r in recent
        ]