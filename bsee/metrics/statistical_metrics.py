"""
Statistical metrics for binary analysis.
"""

import math
import numpy as np
from typing import Dict, List
from collections import Counter
from scipy import stats


class StatisticalMetrics:
    """Collection of statistical metrics."""

    def __init__(self):
        """Initialize statistical metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all statistical metrics."""
        return {
            'chi_square_uniformity': self.chi_square_uniformity,
            'chi_square_p_value': self.chi_square_p_value,
            'mean_byte_value': self.mean_byte_value,
            'median_byte_value': self.median_byte_value,
            'std_deviation': self.std_deviation,
            'skewness': self.skewness,
            'kurtosis': self.kurtosis,
            'byte_range': self.byte_range,
            'interquartile_range': self.interquartile_range,
            'coefficient_of_variation': self.coefficient_of_variation,
            'kl_divergence_uniform': self.kl_divergence_uniform,
            'js_divergence_uniform': self.js_divergence_uniform,
            'moment1': self.moment1,
            'moment2': self.moment2,
            'moment3': self.moment3,
            'moment4': self.moment4
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'chi_square_uniformity': {
                'category': 'statistical',
                'description': 'Chi-square test for uniformity',
                'range': [0, 'inf'],
                'higher_better': False
            },
            'chi_square_p_value': {
                'category': 'statistical',
                'description': 'P-value from chi-square test',
                'range': [0, 1],
                'higher_better': True
            },
            'mean_byte_value': {
                'category': 'statistical',
                'description': 'Mean of byte values',
                'range': [0, 255],
                'higher_better': False
            },
            'median_byte_value': {
                'category': 'statistical',
                'description': 'Median of byte values',
                'range': [0, 255],
                'higher_better': False
            },
            'std_deviation': {
                'category': 'statistical',
                'description': 'Standard deviation of byte values',
                'range': [0, 255],
                'higher_better': False
            },
            'skewness': {
                'category': 'statistical',
                'description': 'Skewness of byte distribution',
                'range': ['-inf', 'inf'],
                'higher_better': False
            },
            'kurtosis': {
                'category': 'statistical',
                'description': 'Kurtosis of byte distribution',
                'range': ['-inf', 'inf'],
                'higher_better': False
            },
            'byte_range': {
                'category': 'statistical',
                'description': 'Range of byte values',
                'range': [0, 255],
                'higher_better': False
            },
            'interquartile_range': {
                'category': 'statistical',
                'description': 'Interquartile range',
                'range': [0, 255],
                'higher_better': False
            },
            'coefficient_of_variation': {
                'category': 'statistical',
                'description': 'Coefficient of variation',
                'range': [0, 'inf'],
                'higher_better': False
            },
            'kl_divergence_uniform': {
                'category': 'statistical',
                'description': 'KL divergence from uniform distribution',
                'range': [0, 'inf'],
                'higher_better': False
            },
            'js_divergence_uniform': {
                'category': 'statistical',
                'description': 'Jensen-Shannon divergence from uniform',
                'range': [0, 'inf'],
                'higher_better': False
            },
            'moment1': {
                'category': 'statistical',
                'description': 'First central moment',
                'range': ['-inf', 'inf'],
                'higher_better': False
            },
            'moment2': {
                'category': 'statistical',
                'description': 'Second central moment (variance)',
                'range': [0, 'inf'],
                'higher_better': False
            },
            'moment3': {
                'category': 'statistical',
                'description': 'Third central moment',
                'range': ['-inf', 'inf'],
                'higher_better': False
            },
            'moment4': {
                'category': 'statistical',
                'description': 'Fourth central moment',
                'range': [0, 'inf'],
                'higher_better': False
            }
        }
        return metadata_map.get(metric_name, {})

    def chi_square_uniformity(self, binary_data: bytes) -> float:
        """Chi-square test for uniformity."""
        if len(binary_data) < 10:
            return 0.0

        # Count byte frequencies
        counts = Counter(binary_data)
        expected_count = len(binary_data) / 256.0

        # Calculate chi-square statistic
        chi_square = 0.0
        for byte_val in range(256):
            observed = counts.get(byte_val, 0)
            expected = expected_count
            if expected > 0:
                chi_square += ((observed - expected) ** 2) / expected

        return chi_square

    def chi_square_p_value(self, binary_data: bytes) -> float:
        """P-value from chi-square test."""
        chi_square = self.chi_square_uniformity(binary_data)

        try:
            # Degrees of freedom = 256 - 1 = 255
            p_value = 1.0 - stats.chi2.cdf(chi_square, 255)
            return p_value
        except Exception:
            return 0.5  # Default value if calculation fails

    def mean_byte_value(self, binary_data: bytes) -> float:
        """Mean of byte values."""
        if not binary_data:
            return 0.0
        return sum(binary_data) / len(binary_data)

    def median_byte_value(self, binary_data: bytes) -> float:
        """Median of byte values."""
        if not binary_data:
            return 0.0

        sorted_bytes = sorted(binary_data)
        n = len(sorted_bytes)

        if n % 2 == 0:
            return (sorted_bytes[n//2 - 1] + sorted_bytes[n//2]) / 2.0
        else:
            return float(sorted_bytes[n//2])

    def std_deviation(self, binary_data: bytes) -> float:
        """Standard deviation of byte values."""
        if len(binary_data) < 2:
            return 0.0

        mean = self.mean_byte_value(binary_data)
        variance = sum((byte_val - mean) ** 2 for byte_val in binary_data) / len(binary_data)
        return math.sqrt(variance)

    def skewness(self, binary_data: bytes) -> float:
        """Skewness of byte distribution."""
        if len(binary_data) < 3:
            return 0.0

        mean = self.mean_byte_value(binary_data)
        std_dev = self.std_deviation(binary_data)

        if std_dev == 0:
            return 0.0

        # Calculate third standardized moment
        third_moment = sum((byte_val - mean) ** 3 for byte_val in binary_data) / len(binary_data)
        skewness = third_moment / (std_dev ** 3)

        return skewness

    def kurtosis(self, binary_data: bytes) -> float:
        """Kurtosis of byte distribution."""
        if len(binary_data) < 4:
            return 0.0

        mean = self.mean_byte_value(binary_data)
        std_dev = self.std_deviation(binary_data)

        if std_dev == 0:
            return 0.0

        # Calculate fourth standardized moment
        fourth_moment = sum((byte_val - mean) ** 4 for byte_val in binary_data) / len(binary_data)
        kurtosis = (fourth_moment / (std_dev ** 4)) - 3  # Excess kurtosis

        return kurtosis

    def byte_range(self, binary_data: bytes) -> float:
        """Range of byte values."""
        if not binary_data:
            return 0.0

        min_byte = min(binary_data)
        max_byte = max(binary_data)
        return float(max_byte - min_byte)

    def interquartile_range(self, binary_data: bytes) -> float:
        """Interquartile range."""
        if len(binary_data) < 4:
            return 0.0

        sorted_bytes = sorted(binary_data)
        n = len(sorted_bytes)

        # Calculate quartiles
        q1_index = n // 4
        q3_index = 3 * n // 4

        q1 = sorted_bytes[q1_index]
        q3 = sorted_bytes[q3_index]

        return float(q3 - q1)

    def coefficient_of_variation(self, binary_data: bytes) -> float:
        """Coefficient of variation."""
        mean = self.mean_byte_value(binary_data)
        std_dev = self.std_deviation(binary_data)

        if mean == 0:
            return 0.0 if std_dev == 0 else float('inf')

        return std_dev / mean

    def kl_divergence_uniform(self, binary_data: bytes) -> float:
        """KL divergence from uniform distribution."""
        if len(binary_data) < 10:
            return 0.0

        # Calculate empirical distribution
        counts = Counter(binary_data)
        total = len(binary_data)

        # Calculate KL divergence
        kl_divergence = 0.0
        uniform_prob = 1.0 / 256.0

        for byte_val in range(256):
            empirical_prob = counts.get(byte_val, 0) / total
            if empirical_prob > 0:
                kl_divergence += empirical_prob * math.log2(empirical_prob / uniform_prob)

        return kl_divergence

    def js_divergence_uniform(self, binary_data: bytes) -> float:
        """Jensen-Shannon divergence from uniform."""
        if len(binary_data) < 10:
            return 0.0

        # Calculate empirical distribution
        counts = Counter(binary_data)
        total = len(binary_data)

        # Calculate JS divergence
        js_divergence = 0.0
        uniform_prob = 1.0 / 256.0

        for byte_val in range(256):
            empirical_prob = counts.get(byte_val, 0) / total
            mixed_prob = (empirical_prob + uniform_prob) / 2.0

            if mixed_prob > 0:
                if empirical_prob > 0:
                    js_divergence += empirical_prob * math.log2(empirical_prob / mixed_prob)
                js_divergence += uniform_prob * math.log2(uniform_prob / mixed_prob)

        return js_divergence / 2.0

    def moment(self, binary_data: bytes, order: int) -> float:
        """Calculate nth central moment."""
        if len(binary_data) < order + 1:
            return 0.0

        mean = self.mean_byte_value(binary_data)
        moment = sum((byte_val - mean) ** order for byte_val in binary_data) / len(binary_data)
        return moment

    def moment1(self, binary_data: bytes) -> float:
        """First central moment (should be 0)."""
        return self.moment(binary_data, 1)

    def moment2(self, binary_data: bytes) -> float:
        """Second central moment (variance)."""
        return self.moment(binary_data, 2)

    def moment3(self, binary_data: bytes) -> float:
        """Third central moment."""
        return self.moment(binary_data, 3)

    def moment4(self, binary_data: bytes) -> float:
        """Fourth central moment."""
        return self.moment(binary_data, 4)