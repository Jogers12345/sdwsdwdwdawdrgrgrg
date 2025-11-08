"""
Data collection and loading for BSEE AI/ML operations.
Handles historical data, training data, and model data persistence.
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from contextlib import contextmanager

from .features import DataFeatures, SequenceFeatures


@dataclass
class TrainingExample:
    """Single training example for ML models."""
    input_data_hash: str
    data_features: Dict[str, Any]
    operation_sequence: List[Dict[str, Any]]
    sequence_features: Dict[str, Any]
    performance_score: float
    execution_time: float
    memory_usage: float
    success: bool
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class ModelPerformance:
    """Model performance metrics."""
    model_name: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: Optional[float] = None
    training_time: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class DataCollector:
    """Collects and stores training data from BSEE operations."""

    def __init__(self, db_path: str = "bsee_training_data.db"):
        """
        Initialize data collector.

        Args:
            db_path: Path to SQLite database for storing training data
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Training examples table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_data_hash TEXT NOT NULL,
                    data_features TEXT NOT NULL,
                    operation_sequence TEXT NOT NULL,
                    sequence_features TEXT NOT NULL,
                    performance_score REAL NOT NULL,
                    execution_time REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    UNIQUE(input_data_hash, operation_sequence)
                )
            ''')

            # Model performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    accuracy REAL NOT NULL,
                    precision REAL NOT NULL,
                    recall REAL NOT NULL,
                    f1_score REAL NOT NULL,
                    mse REAL,
                    training_time REAL,
                    timestamp TEXT NOT NULL
                )
            ''')

            # Feature statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feature_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_name TEXT NOT NULL,
                    mean REAL NOT NULL,
                    std REAL NOT NULL,
                    min_val REAL NOT NULL,
                    max_val REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def record_training_example(self, example: TrainingExample) -> bool:
        """
        Record a training example in the database.

        Args:
            example: Training example to record

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO training_examples
                    (input_data_hash, data_features, operation_sequence, sequence_features,
                     performance_score, execution_time, memory_usage, success, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    example.input_data_hash,
                    json.dumps(example.data_features),
                    json.dumps(example.operation_sequence),
                    json.dumps(example.sequence_features),
                    example.performance_score,
                    example.execution_time,
                    example.memory_usage,
                    example.success,
                    example.timestamp.isoformat(),
                    json.dumps(example.metadata)
                ))

                conn.commit()
                self.logger.debug(f"Recorded training example: {example.input_data_hash}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to record training example: {e}")
            return False

    def record_model_performance(self, performance: ModelPerformance) -> bool:
        """
        Record model performance metrics.

        Args:
            performance: Model performance metrics

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO model_performance
                    (model_name, model_version, accuracy, precision, recall, f1_score,
                     mse, training_time, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    performance.model_name,
                    performance.model_version,
                    performance.accuracy,
                    performance.precision,
                    performance.recall,
                    performance.f1_score,
                    performance.mse,
                    performance.training_time,
                    performance.timestamp.isoformat()
                ))

                conn.commit()
                self.logger.debug(f"Recorded model performance: {performance.model_name}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to record model performance: {e}")
            return False

    def get_training_examples(self, limit: Optional[int] = None,
                            success_only: bool = True,
                            min_score: Optional[float] = None) -> List[TrainingExample]:
        """
        Get training examples from the database.

        Args:
            limit: Maximum number of examples to return
            success_only: Only return successful examples
            min_score: Minimum performance score filter

        Returns:
            List of training examples
        """
        examples = []

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM training_examples WHERE 1=1"
                params = []

                if success_only:
                    query += " AND success = 1"
                if min_score is not None:
                    query += " AND performance_score >= ?"
                    params.append(min_score)

                query += " ORDER BY timestamp DESC"
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)

                for row in cursor.fetchall():
                    example = TrainingExample(
                        input_data_hash=row['input_data_hash'],
                        data_features=json.loads(row['data_features']),
                        operation_sequence=json.loads(row['operation_sequence']),
                        sequence_features=json.loads(row['sequence_features']),
                        performance_score=row['performance_score'],
                        execution_time=row['execution_time'],
                        memory_usage=row['memory_usage'],
                        success=bool(row['success']),
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                    examples.append(example)

        except Exception as e:
            self.logger.error(f"Failed to get training examples: {e}")

        return examples

    def get_feature_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all features in the training data.

        Returns:
            Dictionary of feature statistics
        """
        stats = {}

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT feature_name, mean, std, min_val, max_val, sample_count
                    FROM feature_statistics
                    ORDER BY feature_name
                ''')

                for row in cursor.fetchall():
                    stats[row['feature_name']] = {
                        'mean': row['mean'],
                        'std': row['std'],
                        'min': row['min_val'],
                        'max': row['max_val'],
                        'count': row['sample_count']
                    }

        except Exception as e:
            self.logger.error(f"Failed to get feature statistics: {e}")

        return stats

    def update_feature_statistics(self, features: np.ndarray, feature_names: List[str]):
        """
        Update feature statistics based on new data.

        Args:
            features: Feature array
            feature_names: Names of features
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                for i, feature_name in enumerate(feature_names):
                    if i < features.shape[1]:
                        feature_values = features[:, i]
                        mean = float(np.mean(feature_values))
                        std = float(np.std(feature_values))
                        min_val = float(np.min(feature_values))
                        max_val = float(np.max(feature_values))
                        count = len(feature_values)

                        cursor.execute('''
                            INSERT OR REPLACE INTO feature_statistics
                            (feature_name, mean, std, min_val, max_val, sample_count, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            feature_name, mean, std, min_val, max_val, count,
                            datetime.now().isoformat()
                        ))

                conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to update feature statistics: {e}")

    def export_training_data(self, output_path: str, format: str = "csv") -> bool:
        """
        Export training data to file.

        Args:
            output_path: Output file path
            format: Export format ("csv", "json", "parquet")

        Returns:
            True if successful, False otherwise
        """
        try:
            examples = self.get_training_examples()

            if not examples:
                self.logger.warning("No training data to export")
                return False

            # Convert to DataFrame
            data = []
            for example in examples:
                row = {
                    'input_data_hash': example.input_data_hash,
                    'performance_score': example.performance_score,
                    'execution_time': example.execution_time,
                    'memory_usage': example.memory_usage,
                    'success': example.success,
                    'timestamp': example.timestamp.isoformat()
                }

                # Add data features
                for key, value in example.data_features.items():
                    if isinstance(value, (int, float, str, bool)):
                        row[f'data_{key}'] = value

                # Add sequence features
                for key, value in example.sequence_features.items():
                    if isinstance(value, (int, float, str, bool)):
                        row[f'seq_{key}'] = value

                data.append(row)

            df = pd.DataFrame(data)

            # Export based on format
            if format.lower() == "csv":
                df.to_csv(output_path, index=False)
            elif format.lower() == "json":
                df.to_json(output_path, orient='records', indent=2)
            elif format.lower() == "parquet":
                df.to_parquet(output_path, index=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            self.logger.info(f"Exported {len(examples)} training examples to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export training data: {e}")
            return False

    def import_training_data(self, input_path: str, format: str = "csv") -> bool:
        """
        Import training data from file.

        Args:
            input_path: Input file path
            format: Import format ("csv", "json")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load data based on format
            if format.lower() == "csv":
                df = pd.read_csv(input_path)
            elif format.lower() == "json":
                df = pd.read_json(input_path)
            else:
                raise ValueError(f"Unsupported import format: {format}")

            imported_count = 0

            for _, row in df.iterrows():
                try:
                    # Extract data features
                    data_features = {}
                    sequence_features = {}
                    metadata = {}

                    for col in df.columns:
                        if col.startswith('data_'):
                            data_features[col[5:]] = row[col]
                        elif col.startswith('seq_'):
                            sequence_features[col[4:]] = row[col]
                        elif col not in ['input_data_hash', 'performance_score',
                                       'execution_time', 'memory_usage', 'success', 'timestamp']:
                            metadata[col] = row[col]

                    example = TrainingExample(
                        input_data_hash=row['input_data_hash'],
                        data_features=data_features,
                        operation_sequence=[],  # Not available in export
                        sequence_features=sequence_features,
                        performance_score=row['performance_score'],
                        execution_time=row['execution_time'],
                        memory_usage=row['memory_usage'],
                        success=row['success'],
                        timestamp=pd.to_datetime(row['timestamp']).to_pydatetime(),
                        metadata=metadata
                    )

                    if self.record_training_example(example):
                        imported_count += 1

                except Exception as e:
                    self.logger.warning(f"Failed to import row: {e}")
                    continue

            self.logger.info(f"Imported {imported_count} training examples from {input_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import training data: {e}")
            return False

    def get_training_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of training data.

        Returns:
            Dictionary with summary statistics
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Total examples
                cursor.execute("SELECT COUNT(*) as total FROM training_examples")
                total_examples = cursor.fetchone()['total']

                # Successful examples
                cursor.execute("SELECT COUNT(*) as successful FROM training_examples WHERE success = 1")
                successful_examples = cursor.fetchone()['successful']

                # Average performance
                cursor.execute("SELECT AVG(performance_score) as avg_score FROM training_examples WHERE success = 1")
                avg_score = cursor.fetchone()['avg_score'] or 0

                # Date range
                cursor.execute("SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM training_examples")
                date_range = cursor.fetchone()

                # Models trained
                cursor.execute("SELECT COUNT(DISTINCT model_name) as model_count FROM model_performance")
                model_count = cursor.fetchone()['model_count']

                return {
                    'total_examples': total_examples,
                    'successful_examples': successful_examples,
                    'success_rate': successful_examples / total_examples if total_examples > 0 else 0,
                    'average_score': avg_score,
                    'date_range': {
                        'start': date_range['min_date'],
                        'end': date_range['max_date']
                    },
                    'models_trained': model_count,
                    'database_size_mb': Path(self.db_path).stat().st_size / (1024 * 1024)
                }

        except Exception as e:
            self.logger.error(f"Failed to get training summary: {e}")
            return {}


class DataLoader:
    """Loads and prepares data for ML model training."""

    def __init__(self, data_collector: DataCollector):
        """
        Initialize data loader.

        Args:
            data_collector: Data collector instance
        """
        self.data_collector = data_collector
        self.feature_names = []
        self.scaler = None

    def load_training_data(self, limit: Optional[int] = None,
                          min_score: float = 0.5,
                          validation_split: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Load training data and split into train/validation sets.

        Args:
            limit: Maximum number of examples to load
            min_score: Minimum performance score
            validation_split: Fraction of data for validation

        Returns:
            Tuple of (X_train, y_train, X_val, y_val)
        """
        examples = self.data_collector.get_training_examples(
            limit=limit,
            success_only=True,
            min_score=min_score
        )

        if not examples:
            raise ValueError("No training data available")

        # Extract features and targets
        X = []
        y = []

        for example in examples:
            # Create feature vector
            feature_vector = self._create_feature_vector(example)
            X.append(feature_vector)

            # Target is performance score
            y.append(example.performance_score)

        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)

        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        # Normalize features
        X_train, X_val = self._normalize_features(X_train, X_val)

        return X_train, y_train, X_val, y_val

    def _create_feature_vector(self, example: TrainingExample) -> np.ndarray:
        """Create feature vector from training example."""
        features = []

        # Data features
        data_features = example.data_features
        features.extend([
            data_features.get('size', 0),
            data_features.get('entropy', 0),
            data_features.get('pattern_repetition', 0),
            data_features.get('compression_ratio_estimate', 1.0)
        ])

        # Data type scores
        for data_type in ['text', 'binary', 'compressed', 'encrypted', 'structured']:
            features.append(data_features.get('data_type_score', {}).get(data_type, 0.0))

        # Sequence features
        seq_features = example.sequence_features
        sequence_feature_keys = [
            'operation_count', 'unique_operations', 'diversity_ratio',
            'total_complexity', 'avg_complexity', 'reversibility_ratio',
            'entropy_compatibility', 'size_efficiency', 'has_transform_ops',
            'has_compress_ops', 'has_encrypt_ops', 'estimated_total_runtime'
        ]

        for key in sequence_feature_keys:
            features.append(seq_features.get(key, 0.0))

        return np.array(features, dtype=np.float32)

    def _normalize_features(self, X_train: np.ndarray, X_val: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Normalize features using statistics from training data."""
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)

        self.scaler = scaler
        self.feature_names = [f'feature_{i}' for i in range(X_train.shape[1])]

        # Update feature statistics
        self.data_collector.update_feature_statistics(X_train, self.feature_names)

        return X_train_scaled, X_val_scaled

    def load_prediction_data(self, data_features: Dict[str, Any],
                           sequence_features: Dict[str, Any]) -> np.ndarray:
        """
        Load data for prediction.

        Args:
            data_features: Features of input data
            sequence_features: Features of operation sequence

        Returns:
            Normalized feature vector
        """
        # Create feature vector
        feature_vector = self._create_feature_vector_from_features(
            data_features, sequence_features
        )

        # Normalize if scaler is available
        if self.scaler is not None:
            feature_vector = self.scaler.transform(feature_vector.reshape(1, -1))

        return feature_vector

    def _create_feature_vector_from_features(self, data_features: Dict[str, Any],
                                          sequence_features: Dict[str, Any]) -> np.ndarray:
        """Create feature vector from feature dictionaries."""
        features = []

        # Data features
        features.extend([
            data_features.get('size', 0),
            data_features.get('entropy', 0),
            data_features.get('pattern_repetition', 0),
            data_features.get('compression_ratio_estimate', 1.0)
        ])

        # Data type scores
        for data_type in ['text', 'binary', 'compressed', 'encrypted', 'structured']:
            features.append(data_features.get('data_type_score', {}).get(data_type, 0.0))

        # Sequence features
        sequence_feature_keys = [
            'operation_count', 'unique_operations', 'diversity_ratio',
            'total_complexity', 'avg_complexity', 'reversibility_ratio',
            'entropy_compatibility', 'size_efficiency', 'has_transform_ops',
            'has_compress_ops', 'has_encrypt_ops', 'estimated_total_runtime'
        ]

        for key in sequence_feature_keys:
            features.append(sequence_features.get(key, 0.0))

        return np.array(features, dtype=np.float32)