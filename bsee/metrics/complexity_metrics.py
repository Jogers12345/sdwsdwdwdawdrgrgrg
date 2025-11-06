"""
Complexity metrics for binary analysis.
"""

import zlib
from typing import Dict, List


class ComplexityMetrics:
    """Collection of complexity-based metrics."""

    def __init__(self):
        """Initialize complexity metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all complexity metrics."""
        return {
            'kolmogorov_complexity_estimate': self.kolmogorov_complexity_estimate,
            'lz_complexity': self.lz_complexity,
            'lempel_ziv_complexity': self.lempel_ziv_complexity,
            'algorithmic_complexity': self.algorithmic_complexity,
            'compression_ratio_complexity': self.compression_ratio_complexity,
            'entropy_rate': self.entropy_rate,
            'predictive_complexity': self.predictive_complexity,
            'normalised_compression_distance': self.normalised_compression_distance
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'kolmogorov_complexity_estimate': {
                'category': 'complexity',
                'description': 'Estimated Kolmogorov complexity',
                'range': [0, 'file_size'],
                'higher_better': False
            },
            'lz_complexity': {
                'category': 'complexity',
                'description': 'Lempel-Ziv complexity',
                'range': [0, 'file_size'],
                'higher_better': False
            },
            'lempel_ziv_complexity': {
                'category': 'complexity',
                'description': 'Lempel-Ziv complexity measure',
                'range': [0, 'file_size'],
                'higher_better': False
            },
            'algorithmic_complexity': {
                'category': 'complexity',
                'description': 'Algorithmic complexity estimate',
                'range': [0, 'file_size'],
                'higher_better': False
            },
            'compression_ratio_complexity': {
                'category': 'complexity',
                'description': 'Complexity based on compression ratio',
                'range': [0, 1],
                'higher_better': False
            },
            'entropy_rate': {
                'category': 'complexity',
                'description': 'Entropy rate of the sequence',
                'range': [0, 8],
                'higher_better': False
            },
            'predictive_complexity': {
                'category': 'complexity',
                'description': 'Complexity based on predictability',
                'range': [0, 1],
                'higher_better': False
            },
            'normalised_compression_distance': {
                'category': 'complexity',
                'description': 'Normalised compression distance',
                'range': [0, 1],
                'higher_better': False
            }
        }
        return metadata_map.get(metric_name, {})

    def kolmogorov_complexity_estimate(self, binary_data: bytes) -> float:
        """Estimated Kolmogorov complexity using compression."""
        if len(binary_data) == 0:
            return 0.0

        # Use compression as an approximation of Kolmogorov complexity
        compressed = zlib.compress(binary_data, level=9)
        complexity = len(compressed)

        # Normalize by original size
        normalized_complexity = complexity / len(binary_data)
        return normalized_complexity

    def lz_complexity(self, binary_data: bytes) -> float:
        """Lempel-Ziv complexity."""
        if len(binary_data) == 0:
            return 0.0

        # Simple LZ complexity implementation
        n = len(binary_data)
        complexity = 0
        i = 0

        while i < n:
            # Find longest prefix not seen before
            max_length = 0
            for j in range(1, n - i + 1):
                substring = binary_data[i:i + j]
                if substring in binary_data[:i]:
                    max_length = j
                else:
                    break

            if max_length > 0:
                i += max_length
            else:
                i += 1
            complexity += 1

        # Normalize by n
        return complexity / n if n > 0 else 0.0

    def lempel_ziv_complexity(self, binary_data: bytes) -> float:
        """Lempel-Ziv complexity measure."""
        return self.lz_complexity(binary_data)

    def algorithmic_complexity(self, binary_data: bytes) -> float:
        """Algorithmic complexity estimate."""
        # Combine multiple complexity measures
        kolmogorov = self.kolmogorov_complexity_estimate(binary_data)
        lz = self.lz_complexity(binary_data)

        # Weighted average
        complexity = (kolmogorov * 0.6 + lz * 0.4)
        return complexity

    def compression_ratio_complexity(self, binary_data: bytes) -> float:
        """Complexity based on compression ratio."""
        if len(binary_data) == 0:
            return 0.0

        compressed = zlib.compress(binary_data)
        compression_ratio = len(compressed) / len(binary_data)

        # Higher compression ratio indicates lower complexity
        complexity = compression_ratio
        return complexity

    def entropy_rate(self, binary_data: bytes) -> float:
        """Entropy rate of the sequence."""
        if len(binary_data) < 2:
            return 0.0

        # Calculate conditional entropy
        from bsee.metrics.entropy_metrics import EntropyMetrics
        entropy_metrics = EntropyMetrics()

        conditional_entropy = entropy_metrics.conditional_entropy_order1(binary_data)
        return conditional_entropy

    def predictive_complexity(self, binary_data: bytes) -> float:
        """Complexity based on predictability."""
        if len(binary_data) < 8:
            return 1.0  # Maximum complexity for very small data

        # Use simple predictability test
        correct_predictions = 0
        total_predictions = 0

        for i in range(1, len(binary_data)):
            # Predict next byte based on previous byte
            predicted = binary_data[i - 1]
            actual = binary_data[i]

            if predicted == actual:
                correct_predictions += 1
            total_predictions += 1

        # Predictability = correct / total
        predictability = correct_predictions / total_predictions if total_predictions > 0 else 0.0

        # Complexity = 1 - predictability
        complexity = 1.0 - predictability
        return complexity

    def normalised_compression_distance(self, binary_data: bytes) -> float:
        """Normalised compression distance."""
        if len(binary_data) == 0:
            return 0.0

        # Compress the data
        c_x = len(zlib.compress(binary_data))
        n = len(binary_data)

        # NCD = C(x) / |x|
        ncd = c_x / n
        return ncd