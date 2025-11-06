"""
Bitwise metrics for binary analysis.
"""

import numpy as np
from typing import Dict, List


class BitwiseMetrics:
    """Collection of bitwise metrics."""

    def __init__(self):
        """Initialize bitwise metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all bitwise metrics."""
        return {
            'bit_density_0': self.bit_density_0,
            'bit_density_1': self.bit_density_1,
            'bit_density_2': self.bit_density_2,
            'bit_density_3': self.bit_density_3,
            'bit_density_4': self.bit_density_4,
            'bit_density_5': self.bit_density_5,
            'bit_density_6': self.bit_density_6,
            'bit_density_7': self.bit_density_7,
            'bit_entropy': self.bit_entropy,
            'bit_autocorrelation': self.bit_autocorrelation,
            'bit_run_density': self.bit_run_density,
            'alternating_bit_ratio': self.alternating_bit_ratio,
            'bit_pattern_diversity': self.bit_pattern_diversity,
            'most_significant_bit_bias': self.most_significant_bit_bias,
            'least_significant_bit_bias': self.least_significant_bit_bias,
            'bit_plane_entropy': self.bit_plane_entropy
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'bit_density_0': {
                'category': 'bitwise',
                'description': 'Density of bit 0 (MSB)',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_1': {
                'category': 'bitwise',
                'description': 'Density of bit 1',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_2': {
                'category': 'bitwise',
                'description': 'Density of bit 2',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_3': {
                'category': 'bitwise',
                'description': 'Density of bit 3',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_4': {
                'category': 'bitwise',
                'description': 'Density of bit 4',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_5': {
                'category': 'bitwise',
                'description': 'Density of bit 5',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_6': {
                'category': 'bitwise',
                'description': 'Density of bit 6',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_density_7': {
                'category': 'bitwise',
                'description': 'Density of bit 7 (LSB)',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_entropy': {
                'category': 'bitwise',
                'description': 'Entropy of bit distribution',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_autocorrelation': {
                'category': 'bitwise',
                'description': 'Autocorrelation of bit sequence',
                'range': [-1, 1],
                'higher_better': False
            },
            'bit_run_density': {
                'category': 'bitwise',
                'description': 'Density of bit runs',
                'range': [0, 1],
                'higher_better': False
            },
            'alternating_bit_ratio': {
                'category': 'bitwise',
                'description': 'Ratio of alternating bits',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_pattern_diversity': {
                'category': 'bitwise',
                'description': 'Diversity of bit patterns',
                'range': [0, 1],
                'higher_better': True
            },
            'most_significant_bit_bias': {
                'category': 'bitwise',
                'description': 'Bias in most significant bits',
                'range': [0, 1],
                'higher_better': False
            },
            'least_significant_bit_bias': {
                'category': 'bitwise',
                'description': 'Bias in least significant bits',
                'range': [0, 1],
                'higher_better': False
            },
            'bit_plane_entropy': {
                'category': 'bitwise',
                'description': 'Average entropy across bit planes',
                'range': [0, 1],
                'higher_better': False
            }
        }
        return metadata_map.get(metric_name, {})

    def _bytes_to_bits(self, binary_data: bytes) -> List[int]:
        """Convert bytes to list of bits."""
        bits = []
        for byte_val in binary_data:
            for bit_pos in range(8):
                bit = (byte_val >> (7 - bit_pos)) & 1
                bits.append(bit)
        return bits

    def bit_density(self, binary_data: bytes, bit_position: int) -> float:
        """Calculate density of specific bit position."""
        if not binary_data or bit_position < 0 or bit_position > 7:
            return 0.0

        bit_count = 0
        for byte_val in binary_data:
            bit = (byte_val >> (7 - bit_position)) & 1
            bit_count += bit

        return bit_count / len(binary_data)

    def bit_density_0(self, binary_data: bytes) -> float:
        """Density of bit 0 (MSB)."""
        return self.bit_density(binary_data, 0)

    def bit_density_1(self, binary_data: bytes) -> float:
        """Density of bit 1."""
        return self.bit_density(binary_data, 1)

    def bit_density_2(self, binary_data: bytes) -> float:
        """Density of bit 2."""
        return self.bit_density(binary_data, 2)

    def bit_density_3(self, binary_data: bytes) -> float:
        """Density of bit 3."""
        return self.bit_density(binary_data, 3)

    def bit_density_4(self, binary_data: bytes) -> float:
        """Density of bit 4."""
        return self.bit_density(binary_data, 4)

    def bit_density_5(self, binary_data: bytes) -> float:
        """Density of bit 5."""
        return self.bit_density(binary_data, 5)

    def bit_density_6(self, binary_data: bytes) -> float:
        """Density of bit 6."""
        return self.bit_density(binary_data, 6)

    def bit_density_7(self, binary_data: bytes) -> float:
        """Density of bit 7 (LSB)."""
        return self.bit_density(binary_data, 7)

    def bit_entropy(self, binary_data: bytes) -> float:
        """Entropy of bit distribution."""
        if not binary_data:
            return 0.0

        bits = self._bytes_to_bits(binary_data)
        total_bits = len(bits)

        if total_bits == 0:
            return 0.0

        # Count bits
        ones_count = sum(bits)
        zeros_count = total_bits - ones_count

        if ones_count == 0 or zeros_count == 0:
            return 0.0

        # Calculate entropy
        import math
        p_ones = ones_count / total_bits
        p_zeros = zeros_count / total_bits

        entropy = -(p_ones * math.log2(p_ones) + p_zeros * math.log2(p_zeros))
        return entropy

    def bit_autocorrelation(self, binary_data: bytes) -> float:
        """Autocorrelation of bit sequence."""
        if len(binary_data) < 2:
            return 0.0

        bits = self._bytes_to_bits(binary_data)
        if len(bits) < 2:
            return 0.0

        # Calculate autocorrelation at lag 1
        n = len(bits) - 1
        matches = sum(1 for i in range(n) if bits[i] == bits[i + 1])

        # Normalize to [-1, 1]
        autocorr = (2 * matches - n) / n
        return autocorr

    def bit_run_density(self, binary_data: bytes) -> float:
        """Density of bit runs."""
        if not binary_data:
            return 0.0

        bits = self._bytes_to_bits(binary_data)
        if len(bits) < 2:
            return 0.0

        # Count runs (sequences of consecutive identical bits)
        runs = 1
        for i in range(1, len(bits)):
            if bits[i] != bits[i - 1]:
                runs += 1

        # Density = runs / total_bits
        return runs / len(bits)

    def alternating_bit_ratio(self, binary_data: bytes) -> float:
        """Ratio of alternating bits."""
        if len(binary_data) < 2:
            return 0.0

        bits = self._bytes_to_bits(binary_data)
        if len(bits) < 2:
            return 0.0

        # Count alternating pairs (01 or 10)
        alternating_pairs = 0
        for i in range(len(bits) - 1):
            if bits[i] != bits[i + 1]:
                alternating_pairs += 1

        return alternating_pairs / (len(bits) - 1)

    def bit_pattern_diversity(self, binary_data: bytes) -> float:
        """Diversity of bit patterns."""
        if len(binary_data) < 4:
            return 0.0

        # Count unique 4-bit patterns
        patterns = set()
        bits = self._bytes_to_bits(binary_data)

        for i in range(len(bits) - 3):
            pattern = tuple(bits[i:i+4])
            patterns.add(pattern)

        total_possible_patterns = min(16, len(bits) - 3)
        diversity = len(patterns) / total_possible_patterns if total_possible_patterns > 0 else 0.0

        return diversity

    def most_significant_bit_bias(self, binary_data: bytes) -> float:
        """Bias in most significant bits."""
        if not binary_data:
            return 0.0

        # Check bits 0-3 (most significant 4 bits)
        msb_densities = []
        for bit_pos in range(4):
            density = self.bit_density(binary_data, bit_pos)
            msb_densities.append(density)

        # Calculate bias from uniform (0.5)
        bias = sum(abs(d - 0.5) for d in msb_densities) / 4
        return bias

    def least_significant_bit_bias(self, binary_data: bytes) -> float:
        """Bias in least significant bits."""
        if not binary_data:
            return 0.0

        # Check bits 4-7 (least significant 4 bits)
        lsb_densities = []
        for bit_pos in range(4, 8):
            density = self.bit_density(binary_data, bit_pos)
            lsb_densities.append(density)

        # Calculate bias from uniform (0.5)
        bias = sum(abs(d - 0.5) for d in lsb_densities) / 4
        return bias

    def bit_plane_entropy(self, binary_data: bytes) -> float:
        """Average entropy across bit planes."""
        if not binary_data:
            return 0.0

        entropies = []
        for bit_pos in range(8):
            # Extract bit plane
            bit_plane = []
            for byte_val in binary_data:
                bit = (byte_val >> (7 - bit_pos)) & 1
                bit_plane.append(bit)

            # Calculate entropy of this bit plane
            if bit_plane:
                ones_count = sum(bit_plane)
                zeros_count = len(bit_plane) - ones_count

                if ones_count > 0 and zeros_count > 0:
                    import math
                    p_ones = ones_count / len(bit_plane)
                    p_zeros = zeros_count / len(bit_plane)
                    entropy = -(p_ones * math.log2(p_ones) + p_zeros * math.log2(p_zeros))
                    entropies.append(entropy)
                else:
                    entropies.append(0.0)
            else:
                entropies.append(0.0)

        return sum(entropies) / len(entropies) if entropies else 0.0