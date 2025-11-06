"""
Pattern metrics for binary analysis.
"""

import numpy as np
from typing import Dict, List


class PatternMetrics:
    """Collection of pattern-based metrics."""

    def __init__(self):
        """Initialize pattern metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all pattern metrics."""
        return {
            'autocorrelation_avg': self.autocorrelation_avg,
            'autocorrelation_lag1': self.autocorrelation_lag1,
            'autocorrelation_lag2': self.autocorrelation_lag2,
            'autocorrelation_lag4': self.autocorrelation_lag4,
            'autocorrelation_lag8': self.autocorrelation_lag8,
            'autocorrelation_lag16': self.autocorrelation_lag16,
            'autocorrelation_lag32': self.autocorrelation_lag32,
            'autocorrelation_lag64': self.autocorrelation_lag64,
            'autocorrelation_lag128': self.autocorrelation_lag128,
            'periodicity_score': self.periodicity_score,
            'dominant_frequency': self.dominant_frequency,
            'frequency_spectrum_entropy': self.frequency_spectrum_entropy,
            'pattern_richness': self.pattern_richness,
            'repetition_factor': self.repetition_factor,
            'self_similarity': self.self_similarity,
            'fractal_dimension': self.fractal_dimension,
            'long_range_correlation': self.long_range_correlation
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'autocorrelation_avg': {
                'category': 'pattern',
                'description': 'Average autocorrelation across lags',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag1': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 1',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag2': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 2',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag4': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 4',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag8': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 8',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag16': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 16',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag32': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 32',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag64': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 64',
                'range': [-1, 1],
                'higher_better': False
            },
            'autocorrelation_lag128': {
                'category': 'pattern',
                'description': 'Autocorrelation at lag 128',
                'range': [-1, 1],
                'higher_better': False
            },
            'periodicity_score': {
                'category': 'pattern',
                'description': 'Overall periodicity score',
                'range': [0, 1],
                'higher_better': True
            },
            'dominant_frequency': {
                'category': 'pattern',
                'description': 'Dominant frequency in signal',
                'range': [0, 'nyquist'],
                'higher_better': False
            },
            'frequency_spectrum_entropy': {
                'category': 'pattern',
                'description': 'Entropy of frequency spectrum',
                'range': [0, 'log2(fft_size)'],
                'higher_better': False
            },
            'pattern_richness': {
                'category': 'pattern',
                'description': 'Richness of patterns in data',
                'range': [0, 1],
                'higher_better': True
            },
            'repetition_factor': {
                'category': 'pattern',
                'description': 'Factor of pattern repetition',
                'range': [0, 1],
                'higher_better': True
            },
            'self_similarity': {
                'category': 'pattern',
                'description': 'Self-similarity measure',
                'range': [0, 1],
                'higher_better': True
            },
            'fractal_dimension': {
                'category': 'pattern',
                'description': 'Fractal dimension of data',
                'range': [1, 2],
                'higher_better': False
            },
            'long_range_correlation': {
                'category': 'pattern',
                'description': 'Long-range correlation coefficient',
                'range': [-1, 1],
                'higher_better': False
            }
        }
        return metadata_map.get(metric_name, {})

    def autocorrelation_lag(self, binary_data: bytes, lag: int) -> float:
        """Calculate autocorrelation at specific lag."""
        if len(binary_data) <= lag:
            return 0.0

        # Convert bytes to values
        data = np.array(list(binary_data), dtype=float)

        # Calculate mean
        mean = np.mean(data)

        # Calculate autocorrelation
        if lag == 0:
            return 1.0

        n = len(data) - lag
        if n <= 0:
            return 0.0

        numerator = np.sum((data[:n] - mean) * (data[lag:] - mean))
        denominator = np.sum((data - mean) ** 2)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def autocorrelation_avg(self, binary_data: bytes) -> float:
        """Calculate average autocorrelation across multiple lags."""
        if len(binary_data) < 2:
            return 0.0

        lags = [1, 2, 4, 8, 16, 32, 64, 128]
        correlations = []

        for lag in lags:
            if lag < len(binary_data):
                corr = self.autocorrelation_lag(binary_data, lag)
                correlations.append(abs(corr))

        return np.mean(correlations) if correlations else 0.0

    def autocorrelation_lag1(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 1."""
        return self.autocorrelation_lag(binary_data, 1)

    def autocorrelation_lag2(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 2."""
        return self.autocorrelation_lag(binary_data, 2)

    def autocorrelation_lag4(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 4."""
        return self.autocorrelation_lag(binary_data, 4)

    def autocorrelation_lag8(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 8."""
        return self.autocorrelation_lag(binary_data, 8)

    def autocorrelation_lag16(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 16."""
        return self.autocorrelation_lag(binary_data, 16)

    def autocorrelation_lag32(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 32."""
        return self.autocorrelation_lag(binary_data, 32)

    def autocorrelation_lag64(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 64."""
        return self.autocorrelation_lag(binary_data, 64)

    def autocorrelation_lag128(self, binary_data: bytes) -> float:
        """Autocorrelation at lag 128."""
        return self.autocorrelation_lag(binary_data, 128)

    def periodicity_score(self, binary_data: bytes) -> float:
        """Calculate overall periodicity score."""
        if len(binary_data) < 16:
            return 0.0

        # Calculate autocorrelation for multiple lags
        correlations = []
        for lag in range(1, min(64, len(binary_data) // 4)):
            corr = abs(self.autocorrelation_lag(binary_data, lag))
            correlations.append(corr)

        # Periodicity score based on peak correlations
        if not correlations:
            return 0.0

        max_corr = max(correlations)
        mean_corr = np.mean(correlations)

        # Score based on how much peak exceeds mean
        periodicity = max(0, (max_corr - mean_corr) / (1 - mean_corr + 0.001))
        return min(1.0, periodicity)

    def dominant_frequency(self, binary_data: bytes) -> float:
        """Find dominant frequency in signal."""
        if len(binary_data) < 8:
            return 0.0

        try:
            # Convert bytes to signal
            signal = np.array(list(binary_data), dtype=float)

            # Apply FFT
            fft = np.fft.fft(signal)
            freqs = np.fft.fftfreq(len(signal))

            # Find dominant frequency (excluding DC component)
            magnitude = np.abs(fft[1:len(fft)//2])
            if len(magnitude) == 0:
                return 0.0

            dominant_idx = np.argmax(magnitude)
            dominant_freq = abs(freqs[dominant_idx + 1])

            return dominant_freq
        except Exception:
            return 0.0

    def frequency_spectrum_entropy(self, binary_data: bytes) -> float:
        """Calculate entropy of frequency spectrum."""
        if len(binary_data) < 8:
            return 0.0

        try:
            # Convert bytes to signal
            signal = np.array(list(binary_data), dtype=float)

            # Apply FFT
            fft = np.fft.fft(signal)
            magnitude = np.abs(fft[:len(fft)//2])

            # Normalize
            if np.sum(magnitude) == 0:
                return 0.0

            magnitude = magnitude / np.sum(magnitude)

            # Calculate entropy
            entropy = -np.sum(magnitude * np.log2(magnitude + 1e-10))
            return entropy
        except Exception:
            return 0.0

    def pattern_richness(self, binary_data: bytes) -> float:
        """Calculate richness of patterns in data."""
        if len(binary_data) < 4:
            return 0.0

        # Count unique patterns of different lengths
        pattern_lengths = [2, 4, 8]
        total_patterns = 0
        unique_patterns = 0

        for length in pattern_lengths:
            if len(binary_data) >= length:
                patterns = set()
                for i in range(len(binary_data) - length + 1):
                    pattern = binary_data[i:i+length]
                    patterns.add(pattern)

                total_patterns += len(binary_data) - length + 1
                unique_patterns += len(patterns)

        if total_patterns == 0:
            return 0.0

        richness = unique_patterns / total_patterns
        return richness

    def repetition_factor(self, binary_data: bytes) -> float:
        """Calculate factor of pattern repetition."""
        return 1.0 - self.pattern_richness(binary_data)

    def self_similarity(self, binary_data: bytes) -> float:
        """Calculate self-similarity measure."""
        if len(binary_data) < 16:
            return 0.0

        # Compare different parts of the data
        mid_point = len(binary_data) // 2
        first_half = binary_data[:mid_point]
        second_half = binary_data[mid_point:2*mid_point]

        if len(first_half) != len(second_half):
            min_len = min(len(first_half), len(second_half))
            first_half = first_half[:min_len]
            second_half = second_half[:min_len]

        # Calculate similarity
        matches = sum(1 for a, b in zip(first_half, second_half) if a == b)
        similarity = matches / len(first_half) if first_half else 0.0

        return similarity

    def fractal_dimension(self, binary_data: bytes) -> float:
        """Estimate fractal dimension of data."""
        if len(binary_data) < 8:
            return 1.0

        try:
            # Convert bytes to signal
            signal = np.array(list(binary_data), dtype=float)

            # Simple box-counting method
            scales = [2, 4, 8, 16]
            counts = []

            for scale in scales:
                if scale < len(signal):
                    # Divide signal into boxes of size scale
                    num_boxes = len(signal) // scale
                    if num_boxes > 0:
                        counts.append(num_boxes)

            if len(counts) < 2:
                return 1.0

            # Estimate dimension from log-log plot
            log_scales = np.log(scales[:len(counts)])
            log_counts = np.log(counts)

            # Linear regression to estimate slope (negative fractal dimension)
            if len(log_scales) >= 2:
                slope = np.polyfit(log_scales, log_counts, 1)[0]
                dimension = max(1.0, min(2.0, -slope))
                return dimension

            return 1.0
        except Exception:
            return 1.0

    def long_range_correlation(self, binary_data: bytes) -> float:
        """Calculate long-range correlation coefficient."""
        if len(binary_data) < 32:
            return 0.0

        # Calculate correlations at long lags
        long_lags = [len(binary_data)//8, len(binary_data)//4, len(binary_data)//2]
        correlations = []

        for lag in long_lags:
            if lag > 0 and lag < len(binary_data):
                corr = self.autocorrelation_lag(binary_data, lag)
                correlations.append(corr)

        return np.mean(correlations) if correlations else 0.0