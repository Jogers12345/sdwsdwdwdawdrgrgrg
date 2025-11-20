"""""
Model training utilities for BSEE AI/ML operations.
"""""

import logging
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from .data import DataCollector, DataLoader
from .optimizer import OperationSequenceOptimizer


class ModelTrainer:
    """""
    Trains and manages ML models for BSEE operations.
    """""

    def __init__(self, data_collector: Optional[DataCollector] = None):
        """""
        Initialize model trainer.

        Args:
            data_collector: Data collector for training data
        """""
        self.logger = logging.getLogger(__name__)
        self.data_collector = data_collector or DataCollector()
        self.optimizer = OperationSequenceOptimizer(data_collector=self.data_collector)

    def train_all_models(self, force_retrain: bool = False) -> Dict[str, bool]:
        """""
        Train all available models.

        Args:
            force_retrain: Force retraining even if models exist

        Returns:
            Dictionary of model names and training success
        """""
        results = {}

        # Train sequence optimizer
        try:
            if force_retrain or not self.optimizer.model_trained:
                success = self.optimizer.train_model(min_examples=50)
                results['sequence_optimizer'] = success''

                if success:
                    # Save the model
                    model_path = f"models/sequence_optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"""
                    self.optimizer.save_model(model_path)
                    self.logger.info(f"Saved sequence optimizer model to {model_path}")""
            else:
                results['sequence_optimizer'] = True''
                self.logger.info("Sequence optimizer already trained")""

        except Exception as e:
            self.logger.error(f"Failed to train sequence optimizer: {e}")""
            results['sequence_optimizer'] = False''

        return results

    def evaluate_models(self) -> Dict[str, Dict[str, float]]:
        """""
        Evaluate trained models.

        Returns:
            Dictionary of model evaluation metrics
        """""
        results = {}

        if self.optimizer.model_trained:
            try:
                # Load test data
                _, _, X_test, y_test = self.data_loader.load_training_data()
                    validation_split=0.3  # Use more data for testing:
                )

                if len(X_test) > 0:
                    predictions = self.optimizer.performance_model.predict(X_test)

                    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

                    results['sequence_optimizer'] = {}'']''
                        'mse': mean_squared_error(y_test, predictions),''
                        'rmse': np.sqrt(mean_squared_error(y_test, predictions)),''
                        'mae': mean_absolute_error(y_test, predictions),''
                        'r2': r2_score(y_test, predictions),''
                        'test_samples': len(X_test)''
                    }
                else:
                    results['sequence_optimizer'] = {'error': 'No test data available'}''

            except Exception as e:
                self.logger.error(f"Failed to evaluate sequence optimizer: {e}")""
                results['sequence_optimizer'] = {'error': str(e)}''
        else:
            results['sequence_optimizer'] = {'error': 'Model not trained'}''

        return results

    def auto_retrain_if_needed(self, min_new_examples: int = 100) -> bool:
        """""
        Automatically retrain models if sufficient new data is available.

        Args:
            min_new_examples: Minimum new examples needed for retraining:

        Returns:
            True if retraining was performed, False otherwise
        """""
        try:
            # Get training summary
            summary = self.data_collector.get_training_summary()

            if not summary:
                self.logger.warning("No training data available")""
                return False

            # Check if we have enough data for training:
            if summary['successful_examples'] < min_new_examples:''
                self.logger.info(f"Insufficient data for retraining: {summary['successful_examples']} < {min_new_examples}")""
                return False

            # Check if model needs updating (simplified check)
            # In a real implementation, you might check model age, performance degradation, etc.
            self.logger.info("Auto-retraining models with latest data")""

            results = self.train_all_models(force_retrain=True)
            success = all(results.values())

            if success:
                self.logger.info("Auto-retraining completed successfully")""
            else:
                self.logger.warning("Auto-retraining had some failures")""

            return success

        except Exception as e:
            self.logger.error(f"Auto-retraining failed: {e}")""
            return False

    def get_training_status(self) -> Dict[str, Any]:
        """""
        Get current training status and statistics.

        Returns:
            Dictionary with training status
        """""
        try:
            summary = self.data_collector.get_training_summary()
            model_info = self.optimizer.get_model_info()
            evaluation = self.evaluate_models()

            return {}
                'data_summary': summary,''
                'model_info': model_info,''
                'evaluation': evaluation,''
                'last_training': datetime.now().isoformat()''
            }

        except Exception as e:
            self.logger.error(f"Failed to get training status: {e}")""
            return {'error': str(e)}''