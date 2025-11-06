"""
File Ideality metrics for binary analysis.
"""

import numpy as np
from typing import Dict, List, Tuple


class FileIdealityMetrics:
    """Collection of File Ideality metrics."""

    def __init__(self):
        """Initialize File Ideality metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all File Ideality metrics."""
        return {
            'file_ideality_score': self.file_ideality_score,
            'bits_in_window_8': self.bits_in_window_8,
            'bits_in_window_16': self.bits_in_window_16,
            'bits_in_window_32': self.bits_in_window_32,
            'bits_in_window_64': self.bits_in_window_64,
            'bits_in_window_128': self.bits_in_window_128,
            'bits_in_window_256': self.bits_in_window_256,
            'bits_in_window_512': self.bits_in_window_512,
            'bits_in_window_1024': self.bits_in_window_1024,
            'bits_in_window_2048': self.bits_in_window_2048,
            'average_ideal_window_size': self.average_ideal_window_size,
            'ideality_efficiency': self.ideality_efficiency,
            'predictability_score': self.predictability_score
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'file_ideality_score': {
                'category': 'file_ideality',
                'description': 'Overall File Ideality score (0-1)',
                'range': [0, 1],
                'higher_better': True
            },
            'bits_in_window_8': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 8-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_16': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 16-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_32': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 32-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_64': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 64-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_128': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 128-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_256': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 256-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_512': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 512-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_1024': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 1024-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'bits_in_window_2048': {
                'category': 'file_ideality',
                'description': 'Number of bits predictable with 2048-bit context',
                'range': [0, 'total_bits'],
                'higher_better': True
            },
            'average_ideal_window_size': {
                'category': 'file_ideality',
                'description': 'Average ideal window size for predictable bits',
                'range': [0, 'max_window'],
                'higher_better': True
            },
            'ideality_efficiency': {
                'category': 'file_ideality',
                'description': 'Efficiency of File Ideality distribution',
                'range': [0, 1],
                'higher_better': True
            },
            'predictability_score': {
                'category': 'file_ideality',
                'description': 'Overall predictability score',
                'range': [0, 1],
                'higher_better': True
            }
        }
        return metadata_map.get(metric_name, {})

    def file_ideality_score(self, binary_data: bytes) -> float:
        """Calculate overall File Ideality score."""
        if len(binary_data) == 0:
            return 0.0

        # Window sizes to test
        window_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

        # Convert bytes to bits
        total_bits = len(binary_data) * 8
        classified_bits = 0

        # Analyze each bit position
        for bit_pos in range(total_bits):
            ideal_windows = []

            # Test each window size
            for window_size in window_sizes:
                if self._is_bit_predictable(binary_data, bit_pos, window_size):
                    ideal_windows.append(window_size)

            # Assign to largest ideal window (exclusive assignment rule)
            if ideal_windows:
                classified_bits += 1

        # Calculate ideality score
        file_ideality_score = classified_bits / total_bits
        return file_ideality_score

    def _is_bit_predictable(self, binary_data: bytes, bit_position: int, window_size: int) -> bool:
        """Check if a bit is predictable from its context window."""
        if window_size <= 0 or window_size > bit_position:
            return False

        # Get the bit value
        byte_pos = bit_position // 8
        bit_in_byte = bit_position % 8
        bit_value = (binary_data[byte_pos] >> (7 - bit_in_byte)) & 1

        # Extract context window
        context = self._extract_context(binary_data, bit_position, window_size)

        # Find similar contexts and check predictability
        threshold = 0.8  # 80% predictability threshold
        predictability = self._calculate_predictability(bit_value, context, binary_data)
        return predictability >= threshold

    def _extract_context(self, binary_data: bytes, bit_position: int, window_size: int) -> str:
        """Extract context window around a bit position."""
        # Get window_size bits before the current bit
        start_bit = max(0, bit_position - window_size)
        context_bits = []

        for bit_pos in range(start_bit, bit_position):
            byte_pos = bit_pos // 8
            bit_in_byte = bit_pos % 8
            bit_value = (binary_data[byte_pos] >> (7 - bit_in_byte)) & 1
            context_bits.append(str(bit_value))

        return ''.join(context_bits)

    def _calculate_predictability(self, bit_value: int, context: str, binary_data: bytes) -> float:
        """Calculate predictability of a bit given its context."""
        if len(context) == 0:
            return 0.0

        # Find all occurrences of this context in the binary data
        matches = 0
        correct_predictions = 0

        # Convert binary data to bit string for easier searching
        bit_string = ''.join(
            str((byte_val >> (7 - bit_pos)) & 1)
            for byte_val in binary_data
            for bit_pos in range(8)
        )

        # Search for context pattern
        context_len = len(context)
        for i in range(len(bit_string) - context_len):
            if bit_string[i:i + context_len] == context:
                matches += 1
                # Check if next bit matches our target bit value
                next_bit_pos = i + context_len
                if next_bit_pos < len(bit_string):
                    actual_next_bit = int(bit_string[next_bit_pos])
                    if actual_next_bit == bit_value:
                        correct_predictions += 1

        # Calculate predictability
        if matches == 0:
            return 0.0

        return correct_predictions / matches

    def bits_in_window(self, binary_data: bytes, window_size: int) -> int:
        """Count bits predictable with specified window size."""
        if len(binary_data) == 0:
            return 0

        total_bits = len(binary_data) * 8
        predictable_bits = 0

        for bit_pos in range(total_bits):
            if self._is_bit_predictable(binary_data, bit_pos, window_size):
                predictable_bits += 1

        return predictable_bits

    def bits_in_window_8(self, binary_data: bytes) -> int:
        """Number of bits predictable with 8-bit context."""
        return self.bits_in_window(binary_data, 8)

    def bits_in_window_16(self, binary_data: bytes) -> int:
        """Number of bits predictable with 16-bit context."""
        return self.bits_in_window(binary_data, 16)

    def bits_in_window_32(self, binary_data: bytes) -> int:
        """Number of bits predictable with 32-bit context."""
        return self.bits_in_window(binary_data, 32)

    def bits_in_window_64(self, binary_data: bytes) -> int:
        """Number of bits predictable with 64-bit context."""
        return self.bits_in_window(binary_data, 64)

    def bits_in_window_128(self, binary_data: bytes) -> int:
        """Number of bits predictable with 128-bit context."""
        return self.bits_in_window(binary_data, 128)

    def bits_in_window_256(self, binary_data: bytes) -> int:
        """Number of bits predictable with 256-bit context."""
        return self.bits_in_window(binary_data, 256)

    def bits_in_window_512(self, binary_data: bytes) -> int:
        """Number of bits predictable with 512-bit context."""
        return self.bits_in_window(binary_data, 512)

    def bits_in_window_1024(self, binary_data: bytes) -> int:
        """Number of bits predictable with 1024-bit context."""
        return self.bits_in_window(binary_data, 1024)

    def bits_in_window_2048(self, binary_data: bytes) -> int:
        """Number of bits predictable with 2048-bit context."""
        return self.bits_in_window(binary_data, 2048)

    def average_ideal_window_size(self, binary_data: bytes) -> float:
        """Calculate average ideal window size for predictable bits."""
        if len(binary_data) == 0:
            return 0.0

        window_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        total_bits = len(binary_data) * 8
        total_window_size = 0
        classified_bits = 0

        for bit_pos in range(total_bits):
            ideal_windows = []

            for window_size in window_sizes:
                if self._is_bit_predictable(binary_data, bit_pos, window_size):
                    ideal_windows.append(window_size)

            if ideal_windows:
                # Assign to largest ideal window
                largest_window = max(ideal_windows)
                total_window_size += largest_window
                classified_bits += 1

        return total_window_size / classified_bits if classified_bits > 0 else 0.0

    def ideality_efficiency(self, binary_data: bytes) -> float:
        """Calculate efficiency of File Ideality distribution."""
        if len(binary_data) == 0:
            return 0.0

        # Calculate distribution of bits across window sizes
        window_counts = {}
        total_classified = 0

        window_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        total_bits = len(binary_data) * 8

        for bit_pos in range(total_bits):
            ideal_windows = []

            for window_size in window_sizes:
                if self._is_bit_predictable(binary_data, bit_pos, window_size):
                    ideal_windows.append(window_size)

            if ideal_windows:
                # Assign to largest ideal window
                largest_window = max(ideal_windows)
                window_counts[largest_window] = window_counts.get(largest_window, 0) + 1
                total_classified += 1

        if total_classified == 0:
            return 0.0

        # Calculate entropy of window size distribution
        import math
        entropy = 0.0
        for count in window_counts.values():
            if count > 0:
                probability = count / total_classified
                entropy -= probability * math.log2(probability)

        # Maximum possible entropy with 10 window sizes
        max_entropy = math.log2(len(window_sizes))

        # Efficiency = actual entropy / max entropy
        efficiency = entropy / max_entropy if max_entropy > 0 else 0.0

        # Combine with overall ideality score
        overall_score = self.file_ideality_score(binary_data)
        return (efficiency + overall_score) / 2

    def predictability_score(self, binary_data: bytes) -> float:
        """Calculate overall predictability score."""
        if len(binary_data) == 0:
            return 0.0

        # Calculate predictability for different window sizes
        window_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048]
        predictability_scores = []

        for window_size in window_sizes:
            predictable_bits = self.bits_in_window(binary_data, window_size)
            total_bits = len(binary_data) * 8
            if total_bits > 0:
                score = predictable_bits / total_bits
                predictability_scores.append(score)

        # Return average predictability across all window sizes
        return sum(predictability_scores) / len(predictability_scores) if predictability_scores else 0.0