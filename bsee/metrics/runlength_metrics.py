"""
Run-length metrics for binary analysis.
"""

from typing import Dict, List


class RunLengthMetrics:
    """Collection of run-length based metrics."""

    def __init__(self):
        """Initialize run-length metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all run-length metrics."""
        return {
            'run_count_total': self.run_count_total,
            'average_run_length': self.average_run_length,
            'max_run_length': self.max_run_length,
            'run_length_variance': self.run_length_variance,
            'run_length_entropy': self.run_length_entropy,
            'homogeneity_index': self.homogeneity_index,
            'run_efficiency': self.run_efficiency,
            'compression_potential': self.compression_potential
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'run_count_total': {
                'category': 'runlength',
                'description': 'Total number of runs',
                'range': [0, 'file_size'],
                'higher_better': False
            },
            'average_run_length': {
                'category': 'runlength',
                'description': 'Average length of runs',
                'range': [1, 'file_size'],
                'higher_better': True
            },
            'max_run_length': {
                'category': 'runlength',
                'description': 'Maximum run length',
                'range': [1, 'file_size'],
                'higher_better': True
            },
            'run_length_variance': {
                'category': 'runlength',
                'description': 'Variance of run lengths',
                'range': [0, 'file_size²'],
                'higher_better': False
            },
            'run_length_entropy': {
                'category': 'runlength',
                'description': 'Entropy of run length distribution',
                'range': [0, 'log2(max_run_length)'],
                'higher_better': False
            },
            'homogeneity_index': {
                'category': 'runlength',
                'description': 'Index of data homogeneity',
                'range': [0, 1],
                'higher_better': True
            },
            'run_efficiency': {
                'category': 'runlength',
                'description': 'Efficiency of run structure',
                'range': [0, 1],
                'higher_better': True
            },
            'compression_potential': {
                'category': 'runlength',
                'description': 'Potential for run-length compression',
                'range': [0, 1],
                'higher_better': True
            }
        }
        return metadata_map.get(metric_name, {})

    def _analyze_runs(self, binary_data: bytes) -> List[int]:
        """Analyze runs in binary data."""
        if not binary_data:
            return []

        runs = []
        current_value = binary_data[0]
        current_length = 1

        for i in range(1, len(binary_data)):
            if binary_data[i] == current_value:
                current_length += 1
            else:
                runs.append(current_length)
                current_value = binary_data[i]
                current_length = 1

        runs.append(current_length)  # Add last run
        return runs

    def run_count_total(self, binary_data: bytes) -> float:
        """Total number of runs."""
        runs = self._analyze_runs(binary_data)
        return float(len(runs))

    def average_run_length(self, binary_data: bytes) -> float:
        """Average length of runs."""
        runs = self._analyze_runs(binary_data)
        if not runs:
            return 0.0
        return sum(runs) / len(runs)

    def max_run_length(self, binary_data: bytes) -> float:
        """Maximum run length."""
        runs = self._analyze_runs(binary_data)
        return float(max(runs)) if runs else 0.0

    def run_length_variance(self, binary_data: bytes) -> float:
        """Variance of run lengths."""
        runs = self._analyze_runs(binary_data)
        if len(runs) < 2:
            return 0.0

        mean_length = sum(runs) / len(runs)
        variance = sum((length - mean_length) ** 2 for length in runs) / len(runs)
        return variance

    def run_length_entropy(self, binary_data: bytes) -> float:
        """Entropy of run length distribution."""
        runs = self._analyze_runs(binary_data)
        if not runs:
            return 0.0

        # Count frequency of each run length
        from collections import Counter
        run_counts = Counter(runs)
        total_runs = len(runs)

        # Calculate entropy
        import math
        entropy = 0.0
        for count in run_counts.values():
            probability = count / total_runs
            entropy -= probability * math.log2(probability)

        return entropy

    def homogeneity_index(self, binary_data: bytes) -> float:
        """Index of data homogeneity."""
        if not binary_data:
            return 0.0

        runs = self._analyze_runs(binary_data)
        total_bytes = len(binary_data)
        max_possible_runs = total_bytes  # Alternating bytes
        actual_runs = len(runs)

        # Homogeneity = 1 - (actual_runs / max_possible_runs)
        homogeneity = 1.0 - (actual_runs / max_possible_runs)
        return max(0.0, homogeneity)

    def run_efficiency(self, binary_data: bytes) -> float:
        """Efficiency of run structure."""
        runs = self._analyze_runs(binary_data)
        if not runs:
            return 0.0

        # Efficiency based on average run length relative to maximum
        max_run = max(runs)
        avg_run = sum(runs) / len(runs)

        efficiency = avg_run / max_run if max_run > 0 else 0.0
        return efficiency

    def compression_potential(self, binary_data: bytes) -> float:
        """Potential for run-length compression."""
        runs = self._analyze_runs(binary_data)
        if not runs:
            return 0.0

        # Estimate compression ratio if run-length encoded
        # Each run needs: count byte + value byte = 2 bytes minimum
        compressed_size = len(runs) * 2  # Simplified
        original_size = len(binary_data)

        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        potential = max(0.0, 1.0 - compression_ratio)

        return potential