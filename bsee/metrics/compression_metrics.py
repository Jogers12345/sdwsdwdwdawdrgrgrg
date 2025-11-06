"""
Compression metrics for binary analysis.
"""

import zlib
import lzma
from typing import Dict, List


class CompressionMetrics:
    """Collection of compression-based metrics."""

    def __init__(self):
        """Initialize compression metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all compression metrics."""
        return {
            'lz77_ratio': self.lz77_ratio,
            'lzma_ratio': self.lzma_ratio,
            'zlib_ratio': self.zlib_ratio,
            'gzip_ratio': self.gzip_ratio,
            'bz2_ratio': self.bz2_ratio,
            'compression_efficiency': self.compression_efficiency,
            'redundancy_score': self.redundancy_score,
            'compressibility_index': self.compressibility_index,
            'entropy_compression_gap': self.entropy_compression_gap,
            'dictionary_size_estimate': self.dictionary_size_estimate,
            'pattern_repetition_score': self.pattern_repetition_score,
            'block_compressibility_variance': self.block_compressibility_variance,
            'adaptive_compressibility': self.adaptive_compressibility,
            'compression_complexity': self.compression_complexity,
            'optimal_compression_ratio': self.optimal_compression_ratio
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'lz77_ratio': {
                'category': 'compression',
                'description': 'LZ77 compression ratio',
                'range': [0, 1],
                'higher_better': False
            },
            'lzma_ratio': {
                'category': 'compression',
                'description': 'LZMA compression ratio',
                'range': [0, 1],
                'higher_better': False
            },
            'zlib_ratio': {
                'category': 'compression',
                'description': 'Zlib compression ratio',
                'range': [0, 1],
                'higher_better': False
            },
            'gzip_ratio': {
                'category': 'compression',
                'description': 'Gzip compression ratio',
                'range': [0, 1],
                'higher_better': False
            },
            'bz2_ratio': {
                'category': 'compression',
                'description': 'Bzip2 compression ratio',
                'range': [0, 1],
                'higher_better': False
            },
            'compression_efficiency': {
                'category': 'compression',
                'description': 'Overall compression efficiency',
                'range': [0, 1],
                'higher_better': True
            },
            'redundancy_score': {
                'category': 'compression',
                'description': 'Redundancy score based on compressibility',
                'range': [0, 1],
                'higher_better': True
            },
            'compressibility_index': {
                'category': 'compression',
                'description': 'Overall compressibility index',
                'range': [0, 1],
                'higher_better': True
            },
            'entropy_compression_gap': {
                'category': 'compression',
                'description': 'Gap between theoretical entropy and actual compression',
                'range': [0, 8],
                'higher_better': False
            },
            'dictionary_size_estimate': {
                'category': 'compression',
                'description': 'Estimated dictionary size for compression',
                'range': [0, 'file_size'],
                'higher_better': False
            },
            'pattern_repetition_score': {
                'category': 'compression',
                'description': 'Score based on pattern repetition',
                'range': [0, 1],
                'higher_better': True
            },
            'block_compressibility_variance': {
                'category': 'compression',
                'description': 'Variance of compressibility across blocks',
                'range': [0, 1],
                'higher_better': False
            },
            'adaptive_compressibility': {
                'category': 'compression',
                'description': 'Adaptive compressibility score',
                'range': [0, 1],
                'higher_better': True
            },
            'compression_complexity': {
                'category': 'compression',
                'description': 'Complexity of compression patterns',
                'range': [0, 1],
                'higher_better': False
            },
            'optimal_compression_ratio': {
                'category': 'compression',
                'description': 'Estimated optimal compression ratio',
                'range': [0, 1],
                'higher_better': False
            }
        }
        return metadata_map.get(metric_name, {})

    def lz77_ratio(self, binary_data: bytes) -> float:
        """Calculate LZ77 compression ratio."""
        if len(binary_data) == 0:
            return 0.0

        try:
            compressed = zlib.compress(binary_data, level=6)
            ratio = len(compressed) / len(binary_data)
            return ratio
        except Exception:
            return 1.0

    def lzma_ratio(self, binary_data: bytes) -> float:
        """Calculate LZMA compression ratio."""
        if len(binary_data) == 0:
            return 0.0

        try:
            compressed = lzma.compress(binary_data)
            ratio = len(compressed) / len(binary_data)
            return ratio
        except Exception:
            return 1.0

    def zlib_ratio(self, binary_data: bytes) -> float:
        """Calculate Zlib compression ratio."""
        if len(binary_data) == 0:
            return 0.0

        try:
            compressed = zlib.compress(binary_data)
            ratio = len(compressed) / len(binary_data)
            return ratio
        except Exception:
            return 1.0

    def gzip_ratio(self, binary_data: bytes) -> float:
        """Calculate Gzip compression ratio."""
        if len(binary_data) == 0:
            return 0.0

        try:
            import gzip
            compressed = gzip.compress(binary_data)
            ratio = len(compressed) / len(binary_data)
            return ratio
        except Exception:
            return 1.0

    def bz2_ratio(self, binary_data: bytes) -> float:
        """Calculate Bzip2 compression ratio."""
        if len(binary_data) == 0:
            return 0.0

        try:
            import bz2
            compressed = bz2.compress(binary_data)
            ratio = len(compressed) / len(binary_data)
            return ratio
        except Exception:
            return 1.0

    def compression_efficiency(self, binary_data: bytes) -> float:
        """Calculate overall compression efficiency."""
        ratios = [
            self.lz77_ratio(binary_data),
            self.lzma_ratio(binary_data),
            self.zlib_ratio(binary_data),
            self.gzip_ratio(binary_data),
            self.bz2_ratio(binary_data)
        ]

        # Average compression ratio (lower is better, so invert for efficiency)
        avg_ratio = sum(ratios) / len(ratios)
        efficiency = max(0, 1 - avg_ratio)  # Higher efficiency means better compression
        return efficiency

    def redundancy_score(self, binary_data: bytes) -> float:
        """Calculate redundancy score based on compressibility."""
        # Use best compression ratio to estimate redundancy
        best_ratio = min(
            self.lz77_ratio(binary_data),
            self.lzma_ratio(binary_data),
            self.zlib_ratio(binary_data)
        )

        # Redundancy = 1 - compression ratio
        redundancy = max(0, 1 - best_ratio)
        return redundancy

    def compressibility_index(self, binary_data: bytes) -> float:
        """Calculate overall compressibility index."""
        # Combine multiple compression metrics
        lz77_score = 1 - self.lz77_ratio(binary_data)
        lzma_score = 1 - self.lzma_ratio(binary_data)
        zlib_score = 1 - self.zlib_ratio(binary_data)

        # Weighted average
        index = (lz77_score * 0.3 + lzma_score * 0.4 + zlib_score * 0.3)
        return max(0, min(1, index))

    def entropy_compression_gap(self, binary_data: bytes) -> float:
        """Calculate gap between theoretical entropy and actual compression."""
        from bsee.metrics.entropy_metrics import EntropyMetrics
        entropy_metrics = EntropyMetrics()

        theoretical_entropy = entropy_metrics.shannon_entropy_global(binary_data)
        actual_compression = self.lzma_ratio(binary_data) * 8  # Convert to bits

        gap = max(0, actual_compression - theoretical_entropy)
        return gap

    def dictionary_size_estimate(self, binary_data: bytes) -> float:
        """Estimate dictionary size for compression."""
        if len(binary_data) == 0:
            return 0.0

        # Simple heuristic: count unique byte sequences of different lengths
        unique_2grams = len(set(binary_data[i:i+2] for i in range(len(binary_data)-1)))
        unique_4grams = len(set(binary_data[i:i+4] for i in range(len(binary_data)-3)))
        unique_8grams = len(set(binary_data[i:i+8] for i in range(len(binary_data)-7)))

        # Weighted estimate
        dict_size = (unique_2grams * 2 + unique_4grams * 4 + unique_8grams * 8) / 3
        return min(dict_size, len(binary_data) / 2)  # Cap at half file size

    def pattern_repetition_score(self, binary_data: bytes) -> float:
        """Calculate score based on pattern repetition."""
        if len(binary_data) < 16:
            return 0.0

        # Look for repeated patterns
        pattern_counts = {}
        for length in [2, 4, 8]:
            for i in range(len(binary_data) - length):
                pattern = binary_data[i:i+length]
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Calculate repetition score
        total_patterns = sum(pattern_counts.values())
        unique_patterns = len(pattern_counts)
        repetition_ratio = (total_patterns - unique_patterns) / total_patterns if total_patterns > 0 else 0

        return repetition_ratio

    def block_compressibility_variance(self, binary_data: bytes) -> float:
        """Calculate variance of compressibility across blocks."""
        if len(binary_data) < 1024:
            return 0.0

        block_size = min(1024, len(binary_data) // 10)
        ratios = []

        for i in range(0, len(binary_data), block_size):
            block = binary_data[i:i+block_size]
            if len(block) >= 64:  # Minimum block size for meaningful compression
                ratio = self.lz77_ratio(block)
                ratios.append(ratio)

        if len(ratios) < 2:
            return 0.0

        # Calculate variance
        mean_ratio = sum(ratios) / len(ratios)
        variance = sum((r - mean_ratio) ** 2 for r in ratios) / len(ratios)
        return variance

    def adaptive_compressibility(self, binary_data: bytes) -> float:
        """Calculate adaptive compressibility score."""
        if len(binary_data) < 512:
            return self.compressibility_index(binary_data)

        # Test compressibility with different block sizes
        block_sizes = [256, 512, 1024, 2048]
        scores = []

        for block_size in block_sizes:
            if len(binary_data) >= block_size * 2:
                block = binary_data[:block_size]
                score = 1 - self.lz77_ratio(block)
                scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    def compression_complexity(self, binary_data: bytes) -> float:
        """Calculate complexity of compression patterns."""
        if len(binary_data) < 256:
            return 0.0

        # Analyze compression ratio consistency
        ratios = []
        chunk_size = min(512, len(binary_data) // 8)

        for i in range(0, len(binary_data), chunk_size):
            chunk = binary_data[i:i+chunk_size]
            if len(chunk) >= 64:
                ratio = self.lz77_ratio(chunk)
                ratios.append(ratio)

        if len(ratios) < 2:
            return 0.0

        # Complex data has inconsistent compression ratios
        mean_ratio = sum(ratios) / len(ratios)
        variance = sum((r - mean_ratio) ** 2 for r in ratios) / len(ratios)

        # Normalize to [0,1]
        complexity = min(1.0, variance / (mean_ratio ** 2 + 0.01))
        return complexity

    def optimal_compression_ratio(self, binary_data: bytes) -> float:
        """Estimate optimal compression ratio."""
        # Use the best of available compression methods
        ratios = [
            self.lz77_ratio(binary_data),
            self.lzma_ratio(binary_data),
            self.zlib_ratio(binary_data),
            self.gzip_ratio(binary_data),
            self.bz2_ratio(binary_data)
        ]

        # Account for potential improvements with better algorithms
        best_ratio = min(ratios)
        optimal_ratio = best_ratio * 0.9  # Assume 10% potential improvement

        return max(0.1, optimal_ratio)  # Minimum 10% compression