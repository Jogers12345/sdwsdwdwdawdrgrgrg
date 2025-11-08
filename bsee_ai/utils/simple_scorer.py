"""
Simple Homogeneity Scorer for AI Integration
Lightweight scoring system that works without external dependencies
"""

import math
from typing import Dict, Any, List, Tuple
from collections import Counter


class SimpleHomogeneityScorer:
    """
    Lightweight homogeneity scorer that doesn't require external libraries
    Calculates how uniform and predictable binary data is
    """

    def __init__(self, segment_size: int = 64):
        self.segment_size = segment_size

    def calculate_score(self, data: bytes) -> float:
        """
        Calculate overall homogeneity score (0.0 to 1.0, higher = more homogeneous)
        """
        if len(data) == 0:
            return 0.0

        # Calculate multiple homogeneity indicators
        entropy_score = self._calculate_entropy_score(data)
        pattern_score = self._calculate_pattern_score(data)
        repetition_score = self._calculate_repetition_score(data)
        uniformity_score = self._calculate_uniformity_score(data)

        # Combine scores with weights
        overall_score = (
            entropy_score * 0.3 +
            pattern_score * 0.3 +
            repetition_score * 0.2 +
            uniformity_score * 0.2
        )

        return max(0.0, min(1.0, overall_score))

    def _calculate_entropy_score(self, data: bytes) -> float:
        """
        Calculate entropy-based homogeneity score
        Lower entropy = more homogeneous = higher score
        """
        if len(data) == 0:
            return 0.0

        # Count byte frequencies
        byte_counts = Counter(data)
        data_len = len(data)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in byte_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * math.log2(probability)

        # Normalize to [0, 1] where 1 = most homogeneous (lowest entropy)
        max_entropy = 8.0  # Maximum entropy for byte data
        normalized_entropy = entropy / max_entropy
        entropy_score = 1.0 - normalized_entropy

        return entropy_score

    def _calculate_pattern_score(self, data: bytes) -> float:
        """
        Calculate pattern-based homogeneity score
        More consistent patterns = higher score
        """
        if len(data) < 4:
            return 0.5

        # Look for repeating patterns of different lengths
        pattern_scores = []

        for pattern_len in [2, 4, 8]:
            if len(data) < pattern_len * 2:
                continue

            patterns = {}
            pattern_consistency = 0

            # Count pattern occurrences
            for i in range(len(data) - pattern_len + 1):
                pattern = data[i:i + pattern_len]
                patterns[pattern] = patterns.get(pattern, 0) + 1

            # Calculate pattern consistency
            if patterns:
                most_common = max(patterns.values())
                total_patterns = len(patterns)
                pattern_consistency = most_common / (len(data) - pattern_len + 1)

            pattern_scores.append(pattern_consistency)

        # Average pattern scores
        if pattern_scores:
            return sum(pattern_scores) / len(pattern_scores)
        else:
            return 0.0

    def _calculate_repetition_score(self, data: bytes) -> float:
        """
        Calculate repetition-based homogeneity score
        More repetitions = higher homogeneity
        """
        if len(data) < 2:
            return 0.0

        # Count consecutive repetitions
        consecutive_repetitions = 0
        for i in range(len(data) - 1):
            if data[i] == data[i + 1]:
                consecutive_repetitions += 1

        # Count pattern repetitions
        pattern_repetitions = 0
        for pattern_len in [2, 4]:
            if len(data) < pattern_len * 2:
                continue

            pattern_counts = {}
            for i in range(len(data) - pattern_len + 1):
                pattern = data[i:i + pattern_len]
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

            # Count patterns that appear more than once
            repeated_patterns = sum(1 for count in pattern_counts.values() if count > 1)
            pattern_repetitions += repeated_patterns

        # Combine repetition metrics
        consecutive_score = consecutive_repetitions / max(1, len(data) - 1)
        pattern_score = pattern_repetitions / max(1, len(data))

        return (consecutive_score * 0.7 + pattern_score * 0.3)

    def _calculate_uniformity_score(self, data: bytes) -> float:
        """
        Calculate byte distribution uniformity
        More skewed distribution = higher homogeneity
        """
        if len(data) == 0:
            return 0.0

        # Count byte frequencies
        byte_counts = Counter(data)
        total_bytes = len(data)

        # Calculate how skewed the distribution is
        # Perfectly uniform (all bytes equal) = 1.0
        # Perfectly diverse (all 256 bytes equally) = 0.0

        if len(byte_counts) == 1:
            return 1.0  # Perfectly uniform

        # Calculate Gini coefficient (measure of inequality)
        frequencies = sorted([count / total_bytes for count in byte_counts.values()])
        n = len(frequencies)
        cumsum = 0
        sum_frequencies = sum(frequencies)

        for i, freq in enumerate(frequencies):
            cumsum += (i + 1) * freq

        if sum_frequencies == 0:
            return 0.0

        gini = (2 * cumsum) / (n * sum_frequencies) - (n + 1) / n
        return max(0.0, gini)

    def analyze_data(self, data: bytes) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of data homogeneity
        """
        if len(data) == 0:
            return {
                'overall_score': 0.0,
                'length': 0,
                'unique_bytes': 0,
                'entropy_score': 0.0,
                'pattern_score': 0.0,
                'repetition_score': 0.0,
                'uniformity_score': 0.0,
                'characteristics': 'empty'
            }

        overall_score = self.calculate_score(data)

        # Detailed metrics
        entropy_score = self._calculate_entropy_score(data)
        pattern_score = self._calculate_pattern_score(data)
        repetition_score = self._calculate_repetition_score(data)
        uniformity_score = self._calculate_uniformity_score(data)

        # Data characteristics
        unique_bytes = len(set(data))
        unique_ratio = unique_bytes / 256.0

        if unique_bytes == 1:
            characteristics = 'uniform'
        elif unique_ratio < 0.1:
            characteristics = 'near_uniform'
        elif repetition_score > 0.3:
            characteristics = 'repetitive'
        elif pattern_score > 0.3:
            characteristics = 'patterned'
        elif unique_ratio > 0.8:
            characteristics = 'random'
        else:
            characteristics = 'mixed'

        return {
            'overall_score': overall_score,
            'length': len(data),
            'unique_bytes': unique_bytes,
            'entropy_score': entropy_score,
            'pattern_score': pattern_score,
            'repetition_score': repetition_score,
            'uniformity_score': uniformity_score,
            'characteristics': characteristics,
            'unique_ratio': unique_ratio
        }