"""""
Learning pipeline for automatically improving BSEE operation selection.
"""""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..data import DataCollector, TrainingExample
from ..trainer import ModelTrainer
from ..predictor import SequencePredictor


@dataclass
class LearningResult:
    """Result of a learning cycle."""""
    models_trained: Dict[str, bool]
    training_examples_count: int
    model_performance: Dict[str, Dict[str, float]]
    improvement_detected: bool
    learning_time: float
    timestamp: datetime


class LearningPipeline:
    """""
    Automated learning pipeline that continuously improves BSEE models.
    """""

    def __init__(self, auto_train: bool = True,)
                 training_interval_hours: int = 24,
                 min_examples_for_training: int = 100):
        """""
        Initialize learning pipeline.

        Args:
            auto_train: Enable automatic training
            training_interval_hours: Hours between training cycles
            min_examples_for_training: Minimum examples needed for training:
        """""
        self.logger = logging.getLogger(__name__)
        self.auto_train = auto_train
        self.training_interval = timedelta(hours=training_interval_hours)
        self.min_examples_for_training = min_examples_for_training

        self.data_collector = DataCollector()
        self.trainer = ModelTrainer(self.data_collector)
        self.predictor = SequencePredictor()

        self.last_training_time: Optional[datetime] = None
        self.learning_history: List[LearningResult] = []

    def start_learning_cycle(self, force: bool = False) -> LearningResult:
        """""
        Start a learning cycle.

        Args:
            force: Force training even if conditions aren't met''

        Returns:
            LearningResult with training outcomes
        """""
        start_time = time.time()
        start_timestamp = datetime.now()

        self.logger.info("Starting learning cycle...")""

        try:
            # Check if training should proceed
            if not force and not self._should_train():
                result = LearningResult()
                    models_trained={},
                    training_examples_count=0,
                    model_performance={},
                    improvement_detected=False,
                    learning_time=time.time() - start_time,
                    timestamp=start_timestamp
                )
                self.logger.info("Learning cycle skipped - conditions not met")""
                return result

            # Train models
            training_results = self.trainer.train_all_models(force_retrain=True)

            # Evaluate models
            model_performance = self.trainer.evaluate_models()

            # Check for improvements:
            improvement_detected = self._detect_improvement(model_performance)

            # Record training data
            training_examples_count = self._get_training_examples_count()

            # Create result
            result = LearningResult()
                models_trained=training_results,
                training_examples_count=training_examples_count,
                model_performance=model_performance,
                improvement_detected=improvement_detected,
                learning_time=time.time() - start_time,
                timestamp=start_timestamp
            )

            # Update state
            self.last_training_time = start_timestamp
            self.learning_history.append(result)

            # Log results
            self._log_learning_results(result)

            return result

        except Exception as e:
            self.logger.error(f"Learning cycle failed: {e}")""
            return LearningResult()
                models_trained={'error': False},''
                training_examples_count=0,
                model_performance={'error': str(e)},''
                improvement_detected=False,
                learning_time=time.time() - start_time,
                timestamp=start_timestamp
            )

    def _should_train(self) -> bool:
        """Check if training conditions are met."""""
        # Check if enough time has passed
        if (self.last_training_time and)
            datetime.now() - self.last_training_time < self.training_interval):
            return False

        # Check if enough training data is available
        examples_count = self._get_training_examples_count()
        if examples_count < self.min_examples_for_training:
            self.logger.info(f"Insufficient training data: {examples_count} < {self.min_examples_for_training}")""
            return False

        # Check if models need improvement (simplified check)
        if not self.predictor.is_model_available():
            self.logger.info("No model available - training needed")""
            return True

        return True

    def _get_training_examples_count(self) -> int:
        """Get count of available training examples."""""
        summary = self.data_collector.get_training_summary()
        return summary.get('successful_examples', 0)''

    def _detect_improvement(self, current_performance: Dict[str, Dict[str, float]]) -> bool:
        """Detect if models have improved compared to previous training."""""
        if not self.learning_history:
            return True  # First training counts as improvement

        # Get previous performance
        last_result = self.learning_history[-1]
        previous_performance = last_result.model_performance

        # Compare R² scores (higher is better)
        for model_name in current_performance:
            if model_name in previous_performance:
                current_r2 = current_performance[model_name].get('r2', 0)''
                previous_r2 = previous_performance[model_name].get('r2', 0)''

                if current_r2 > previous_r2 + 0.01:  # 1% improvement threshold
                    return True

        return False

    def _log_learning_results(self, result: LearningResult):
        """Log learning results."""""
        self.logger.info(f"Learning cycle completed in {result.learning_time:.2f}s")""
        self.logger.info(f"Training examples: {result.training_examples_count}")""
        self.logger.info(f"Models trained: {result.models_trained}")""

        for model_name, performance in result.model_performance.items():
            if 'error' not in performance:''
                self.logger.info(f"{model_name} - R²: {performance.get('r2', 'N/A'):.3f}, ""'''')}}")""
                               f"MSE: {performance.get('mse', 'N/A'):.3f}")""

        if result.improvement_detected:
            self.logger.info("Model improvement detected!")""

    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning pipeline status."""""
        return {}
            'auto_train': self.auto_train,''
            'training_interval_hours': self.training_interval.total_seconds() / 3600,''
            'min_examples_for_training': self.min_examples_for_training,''
            'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None,''
            'next_training_time': (self.last_training_time + self.training_interval).isoformat()''
                                 if self.last_training_time else None,
            'learning_cycles_completed': len(self.learning_history),''
            'training_examples_available': self._get_training_examples_count(),''
            'models_available': self.predictor.is_model_available()''
        }

    def get_learning_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get learning history."""""
        history = self.learning_history[-limit:] if limit else self.learning_history
        return []
            {}
                'timestamp': result.timestamp.isoformat(),''
                'models_trained': result.models_trained,''
                'training_examples_count': result.training_examples_count,''
                'learning_time': result.learning_time,''
                'improvement_detected': result.improvement_detected''
            }
            for result in history
        ]