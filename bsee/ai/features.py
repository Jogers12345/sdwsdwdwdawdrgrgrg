"""
Feature extraction for BSEE AI/ML operations.
Extracts meaningful features from binary data and operations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import struct
import hashlib
from collections import Counter


@dataclass
class DataFeatures:
    """Features extracted from binary data."""
    size: int
    entropy: float
    byte_frequency: Dict[int, float]
    pattern_repetition: float
    compression_ratio_estimate: float
    data_type_score: Dict[str, float]
    hash_signature: str
    structural_features: Dict[str, float]

@dataclass
class OperationFeatures:
    """Features for binary operations."""
    operation_type: str
    complexity_score: float
    reversibility: float
    parameter_count: int
    estimated_runtime: float
    memory_usage_estimate: float
    transformation_signature: str


class FeatureExtractor:
    """Extracts features from binary data and operations for ML models."""

    def __init__(self):
        self.byte_patterns = {
            'text': self._is_text_like,
            'binary': self._is_binary_like,
            'compressed': self._is_compressed_like,
            'encrypted': self._is_encrypted_like,
            'structured': self._is_structured_like
        }

    def extract_data_features(self, data: bytes) -> DataFeatures:
        """
        Extract comprehensive features from binary data.

        Args:
            data: Binary data to analyze

        Returns:
            DataFeatures object with extracted features
        """
        if not data:
            return DataFeatures(
                size=0, entropy=0.0, byte_frequency={},
                pattern_repetition=0.0, compression_ratio_estimate=1.0,
                data_type_score={}, hash_signature="",
                structural_features={}
            )

        # Basic features
        size = len(data)
        entropy = self._calculate_entropy(data)
        byte_frequency = self._calculate_byte_frequency(data)
        pattern_repetition = self._calculate_pattern_repetition(data)
        compression_ratio_estimate = self._estimate_compression_ratio(data)

        # Data type classification
        data_type_score = self._classify_data_type(data)

        # Hash signature for identification
        hash_signature = hashlib.md5(data).hexdigest()

        # Structural features
        structural_features = self._extract_structural_features(data)

        return DataFeatures(
            size=size,
            entropy=entropy,
            byte_frequency=byte_frequency,
            pattern_repetition=pattern_repetition,
            compression_ratio_estimate=compression_ratio_estimate,
            data_type_score=data_type_score,
            hash_signature=hash_signature,
            structural_features=structural_features
        )

    def extract_operation_features(self, operation_name: str, parameters: Dict[str, Any]) -> OperationFeatures:
        """
        Extract features from an operation definition.

        Args:
            operation_name: Name of the operation
            parameters: Operation parameters

        Returns:
            OperationFeatures object
        """
        complexity_score = self._calculate_operation_complexity(operation_name, parameters)
        reversibility = self._calculate_reversibility(operation_name)
        parameter_count = len(parameters)
        estimated_runtime = self._estimate_operation_runtime(operation_name, parameters)
        memory_usage_estimate = self._estimate_memory_usage(operation_name, parameters)
        transformation_signature = self._create_transformation_signature(operation_name, parameters)

        return OperationFeatures(
            operation_type=operation_name,
            complexity_score=complexity_score,
            reversibility=reversibility,
            parameter_count=parameter_count,
            estimated_runtime=estimated_runtime,
            memory_usage_estimate=memory_usage_estimate,
            transformation_signature=transformation_signature
        )

    def extract_sequence_features(self, operations: List[Dict[str, Any]], data_features: DataFeatures) -> Dict[str, float]:
        """
        Extract features from an operation sequence.

        Args:
            operations: List of operations in sequence
            data_features: Features of the input data

        Returns:
            Dictionary of sequence features
        """
        if not operations:
            return {}

        # Operation-level features
        operation_types = [op.get('type', 'unknown') for op in operations]
        operation_count = len(operations)
        unique_operations = len(set(operation_types))

        # Complexity features
        total_complexity = sum(self._calculate_operation_complexity(
            op.get('type', 'unknown'), op.get('parameters', {})
        ) for op in operations)
        avg_complexity = total_complexity / operation_count

        # Reversibility features
        reversible_count = sum(1 for op in operations
                             if self._calculate_reversibility(op.get('type', 'unknown')) > 0.5)
        reversibility_ratio = reversible_count / operation_count

        # Data-specific features
        entropy_compatibility = self._calculate_entropy_compatibility(
            data_features.entropy, operations
        )
        size_efficiency = self._calculate_size_efficiency(data_features.size, operations)

        return {
            'operation_count': operation_count,
            'unique_operations': unique_operations,
            'diversity_ratio': unique_operations / operation_count,
            'total_complexity': total_complexity,
            'avg_complexity': avg_complexity,
            'reversibility_ratio': reversibility_ratio,
            'entropy_compatibility': entropy_compatibility,
            'size_efficiency': size_efficiency,
            'has_transform_ops': any('transform' in op_type.lower() for op_type in operation_types),
            'has_compress_ops': any('compress' in op_type.lower() for op_type in operation_types),
            'has_encrypt_ops': any('encrypt' in op_type.lower() for op_type in operation_types),
            'estimated_total_runtime': sum(
                self._estimate_operation_runtime(op.get('type', 'unknown'), op.get('parameters', {}))
                for op in operations
            )
        }

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of the data."""
        if not data:
            return 0.0

        # Count byte frequencies
        byte_counts = Counter(data)
        data_len = len(data)

        # Calculate entropy
        entropy = 0.0
        for count in byte_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)

        return entropy

    def _calculate_byte_frequency(self, data: bytes) -> Dict[int, float]:
        """Calculate frequency distribution of bytes."""
        if not data:
            return {}

        byte_counts = Counter(data)
        total_bytes = len(data)

        return {byte: count / total_bytes for byte, count in byte_counts.items()}

    def _calculate_pattern_repetition(self, data: bytes) -> float:
        """Calculate how repetitive the data is."""
        if len(data) < 4:
            return 0.0

        # Look for repeated patterns of different lengths
        max_pattern_length = min(16, len(data) // 4)
        repetitions = 0
        total_checks = 0

        for pattern_length in range(2, max_pattern_length + 1):
            for i in range(len(data) - pattern_length * 2):
                pattern = data[i:i + pattern_length]
                # Check if pattern appears again
                if pattern in data[i + pattern_length:]:
                    repetitions += 1
                total_checks += 1

        return repetitions / total_checks if total_checks > 0 else 0.0

    def _estimate_compression_ratio(self, data: bytes) -> float:
        """Estimate how compressible the data is."""
        if len(data) < 100:
            return 1.0

        entropy = self._calculate_entropy(data)
        pattern_repetition = self._calculate_pattern_repetition(data)

        # Higher repetition and lower entropy = better compression
        compressibility = pattern_repetition * (1 - entropy / 8)

        # Estimate compression ratio (1.0 = no compression, <1.0 = compression)
        return max(0.3, 1.0 - compressibility * 0.7)

    def _classify_data_type(self, data: bytes) -> Dict[str, float]:
        """Classify the type of data and return confidence scores."""
        scores = {}

        for data_type, classifier in self.byte_patterns.items():
            scores[data_type] = classifier(data)

        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v / total_score for k, v in scores.items()}

        return scores

    def _is_text_like(self, data: bytes) -> float:
        """Check if data looks like text."""
        if not data:
            return 0.0

        # Count printable ASCII characters
        printable_count = sum(1 for b in data if 32 <= b <= 126 or b in [9, 10, 13])
        printable_ratio = printable_count / len(data)

        # Check for common text patterns
        text_indicators = 0
        if b' ' in data:
            text_indicators += 1
        if b'\n' in data or b'\r' in data:
            text_indicators += 1
        if any(word in data.lower() for word in [b'the', b'and', b'of', b'to', b'a']):
            text_indicators += 1

        return printable_ratio * 0.7 + min(text_indicators / 3, 1.0) * 0.3

    def _is_binary_like(self, data: bytes) -> float:
        """Check if data looks like general binary data."""
        if not data:
            return 0.0

        entropy = self._calculate_entropy(data)
        return min(entropy / 8, 1.0)

    def _is_compressed_like(self, data: bytes) -> float:
        """Check if data looks like compressed data."""
        if not data:
            return 0.0

        entropy = self._calculate_entropy(data)

        # Compressed data typically has high entropy
        entropy_score = min(entropy / 7.5, 1.0)

        # Check for common compression headers
        compression_headers = [
            b'\x1f\x8b',  # gzip
            b'\x50\x4b',  # zip
            b'\x42\x5a',  # bzip2
            b'\xfd\x37',  # xz
        ]

        header_score = 0.0
        for header in compression_headers:
            if data.startswith(header):
                header_score = 1.0
                break

        return entropy_score * 0.8 + header_score * 0.2

    def _is_encrypted_like(self, data: bytes) -> float:
        """Check if data looks like encrypted data."""
        if not data:
            return 0.0

        entropy = self._calculate_entropy(data)
        pattern_repetition = self._calculate_pattern_repetition(data)

        # Encrypted data has high entropy and low repetition
        entropy_score = min(entropy / 7.8, 1.0)
        repetition_score = 1.0 - min(pattern_repetition * 10, 1.0)

        return (entropy_score + repetition_score) / 2

    def _is_structured_like(self, data: bytes) -> float:
        """Check if data has structured patterns."""
        if len(data) < 16:
            return 0.0

        # Look for regular patterns
        pattern_scores = []

        # Check for repeated patterns at regular intervals
        for interval in [2, 4, 8, 16]:
            if len(data) >= interval * 4:
                pattern_found = True
                for i in range(len(data) - interval * 3):
                    if data[i] != data[i + interval]:
                        pattern_found = False
                        break
                if pattern_found:
                    pattern_scores.append(1.0)
                else:
                    pattern_scores.append(0.0)

        return sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0.0

    def _extract_structural_features(self, data: bytes) -> Dict[str, float]:
        """Extract structural features from data."""
        if len(data) < 8:
            return {}

        features = {}

        # Byte alignment features
        features['alignment_4'] = 1.0 if len(data) % 4 == 0 else 0.0
        features['alignment_8'] = 1.0 if len(data) % 8 == 0 else 0.0
        features['alignment_16'] = 1.0 if len(data) % 16 == 0 else 0.0

        # Zero-byte statistics
        zero_bytes = data.count(0)
        features['zero_byte_ratio'] = zero_bytes / len(data)

        # High-byte statistics
        high_bytes = sum(1 for b in data if b > 127)
        features['high_byte_ratio'] = high_bytes / len(data)

        # Byte transitions (how often bytes change)
        transitions = sum(1 for i in range(len(data) - 1) if data[i] != data[i + 1])
        features['transition_ratio'] = transitions / (len(data) - 1)

        return features

    def _calculate_operation_complexity(self, operation_name: str, parameters: Dict[str, Any]) -> float:
        """Calculate complexity score for an operation."""
        # Base complexity for different operation types
        complexity_map = {
            'xor': 1.0,
            'add_constant': 1.0,
            'rotate': 1.5,
            'substitute': 2.0,
            'burrows_wheeler': 4.0,
            'huffman': 5.0,
            'lz77': 6.0,
            'dct': 7.0,
            'fft': 8.0,
            'move_to_front': 3.0,
            'arithmetic_coding': 8.0,
        }

        base_complexity = complexity_map.get(operation_name.lower(), 3.0)

        # Adjust complexity based on parameters
        param_complexity = len(parameters) * 0.5

        # Adjust for data size impact
        if 'key' in parameters:
            param_complexity += 0.2  # Key operations add slight complexity
        if 'iterations' in parameters:
            param_complexity += parameters['iterations'] * 0.1

        return base_complexity + param_complexity

    def _calculate_reversibility(self, operation_name: str) -> float:
        """Calculate how reversible an operation is (0.0 to 1.0)."""
        reversible_ops = {
            'xor': 1.0,
            'add_constant': 1.0,
            'rotate': 1.0,
            'substitute': 0.8,
            'burrows_wheeler': 1.0,
            'move_to_front': 1.0,
        }

        partially_reversible = {
            'huffman': 0.9,
            'lz77': 0.9,
            'run_length': 0.8,
        }

        irreversibly_destructive = {
            'arithmetic_coding': 0.7,
            'hash': 0.0,
        }

        if operation_name.lower() in reversible_ops:
            return reversible_ops[operation_name.lower()]
        elif operation_name.lower() in partially_reversible:
            return partially_reversible[operation_name.lower()]
        elif operation_name.lower() in irreversibly_destructive:
            return irreversibly_destructive[operation_name.lower()]
        else:
            return 0.5  # Default assumption

    def _estimate_operation_runtime(self, operation_name: str, parameters: Dict[str, Any]) -> float:
        """Estimate runtime in milliseconds for 1KB of data."""
        runtime_map = {
            'xor': 0.1,
            'add_constant': 0.1,
            'rotate': 0.2,
            'substitute': 0.3,
            'burrows_wheeler': 5.0,
            'huffman': 10.0,
            'lz77': 15.0,
            'dct': 20.0,
            'fft': 25.0,
            'move_to_front': 2.0,
            'arithmetic_coding': 30.0,
        }

        base_runtime = runtime_map.get(operation_name.lower(), 5.0)

        # Adjust based on parameters
        if 'iterations' in parameters:
            base_runtime *= parameters['iterations']

        return base_runtime

    def _estimate_memory_usage(self, operation_name: str, parameters: Dict[str, Any]) -> float:
        """Estimate memory usage in KB for 1KB of data."""
        memory_map = {
            'xor': 2.0,
            'add_constant': 2.0,
            'rotate': 2.0,
            'substitute': 4.0,
            'burrows_wheeler': 8.0,
            'huffman': 16.0,
            'lz77': 20.0,
            'dct': 32.0,
            'fft': 32.0,
            'move_to_front': 4.0,
            'arithmetic_coding': 40.0,
        }

        return memory_map.get(operation_name.lower(), 8.0)

    def _create_transformation_signature(self, operation_name: str, parameters: Dict[str, Any]) -> str:
        """Create a unique signature for the transformation."""
        param_str = "_".join(f"{k}:{v}" for k, v in sorted(parameters.items()))
        return f"{operation_name}_{param_str}"

    def _calculate_entropy_compatibility(self, data_entropy: float, operations: List[Dict[str, Any]]) -> float:
        """Calculate how compatible the operations are with the data entropy."""
        if not operations:
            return 0.0

        # Different operations work better with different entropy levels
        entropy_scores = []

        for op in operations:
            op_type = op.get('type', '').lower()

            if op_type in ['xor', 'add_constant', 'rotate']:
                # Simple operations work well with any entropy
                entropy_scores.append(1.0)
            elif op_type in ['huffman', 'run_length']:
                # Compression operations work better with lower entropy
                entropy_scores.append(max(0, 1.0 - data_entropy / 8))
            elif op_type in ['burrows_wheeler', 'move_to_front']:
                # Transform operations work well with medium entropy
                optimal_entropy = 4.0
                distance = abs(data_entropy - optimal_entropy)
                entropy_scores.append(max(0, 1.0 - distance / 4))
            else:
                entropy_scores.append(0.5)  # Default

        return sum(entropy_scores) / len(entropy_scores)

    def _calculate_size_efficiency(self, data_size: int, operations: List[Dict[str, Any]]) -> float:
        """Calculate how efficient the operations are for the data size."""
        if not operations:
            return 0.0

        # Different operations are more efficient at different scales
        size_mb = data_size / (1024 * 1024)

        if size_mb < 0.001:  # < 1KB
            # Simple operations are more efficient for small data
            simple_ops = sum(1 for op in operations if op.get('type', '').lower() in
                           ['xor', 'add_constant', 'rotate'])
            return simple_ops / len(operations)
        elif size_mb < 1:  # < 1MB
            # Most operations are reasonably efficient
            return 0.8
        else:  # > 1MB
            # Complex operations are more efficient for large data
            complex_ops = sum(1 for op in operations if op.get('type', '').lower() in
                            ['burrows_wheeler', 'huffman', 'lz77', 'dct', 'fft'])
            return complex_ops / len(operations) if operations else 0.0

    def create_feature_vector(self, data_features: DataFeatures, sequence_features: Dict[str, float]) -> np.ndarray:
        """
        Create a numerical feature vector for ML models.

        Args:
            data_features: Features extracted from data
            sequence_features: Features extracted from operation sequence

        Returns:
            Numpy array of features
        """
        features = []

        # Data features
        features.append(data_features.size)
        features.append(data_features.entropy)
        features.append(data_features.pattern_repetition)
        features.append(data_features.compression_ratio_estimate)

        # Data type scores
        for data_type in ['text', 'binary', 'compressed', 'encrypted', 'structured']:
            features.append(data_features.data_type_score.get(data_type, 0.0))

        # Structural features
        for struct_feature in ['alignment_4', 'alignment_8', 'zero_byte_ratio',
                             'high_byte_ratio', 'transition_ratio']:
            features.append(data_features.structural_features.get(struct_feature, 0.0))

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