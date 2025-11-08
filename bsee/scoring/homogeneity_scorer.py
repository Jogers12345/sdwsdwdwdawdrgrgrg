"""
Homogeneity Scorer for BSEE Binary Structure Enhancement Engine.

This module provides comprehensive scoring functions to measure the homogeneity
and uniformity of binary data streams. The primary goal is to quantify how
uniform and predictable binary data is, which is essential for optimization
and analysis purposes.

Key Concepts:
- Homogeneity: Degree of uniformity in binary data patterns
- Entropy Distribution: Consistency of entropy across data segments
- Pattern Consistency: Regularity and predictability of patterns
- Structural Uniformity: Overall structural consistency in binary data
"""

import math
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import Counter, defaultdict
import numpy as np
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class HomogeneityMetrics:
    """
    Comprehensive homogeneity metrics for binary data analysis.

    This class encapsulates all the different metrics used to evaluate the
    homogeneity and uniformity of binary data streams.
    """
    # Overall scores (0.0 to 1.0, higher is more homogeneous)
    overall_homogeneity: float
    entropy_uniformity: float
    pattern_consistency: float
    structural_regularity: float

    # Detailed metrics
    entropy_std: float  # Standard deviation of entropy across segments
    pattern_repetition: float  # Repetition rate of patterns
    byte_distribution_variance: float  # Variance in byte frequency distribution
    segment_homogeneity_scores: List[float]  # Per-segment homogeneity scores

    # Data characteristics
    total_entropy: float
    entropy_gradient: float  # Rate of entropy change across data
    local_uniformity: float  # Local pattern uniformity
    global_uniformity: float  # Global pattern uniformity

    # Analysis metadata
    segment_size: int
    num_segments: int
    data_size: int

    @classmethod
    def create_empty(cls) -> 'HomogeneityMetrics':
        """Create empty metrics with default values."""
        return cls(
            overall_homogeneity=0.0,
            entropy_uniformity=0.0,
            pattern_consistency=0.0,
            structural_regularity=0.0,
            entropy_std=0.0,
            pattern_repetition=0.0,
            byte_distribution_variance=0.0,
            segment_homogeneity_scores=[],
            total_entropy=0.0,
            entropy_gradient=0.0,
            local_uniformity=0.0,
            global_uniformity=0.0,
            segment_size=0,
            num_segments=0,
            data_size=0
        )


class HomogeneityScorer:
    """
    Advanced scorer for measuring binary data homogeneity.

    This class provides comprehensive analysis of binary data streams to determine
    their homogeneity characteristics. It uses multiple metrics and algorithms
    to provide a detailed assessment of data uniformity.
    """

    def __init__(self, segment_size: int = 1024, min_segment_size: int = 64):
        """
        Initialize the homogeneity scorer.

        Args:
            segment_size: Default segment size for analysis
            min_segment_size: Minimum segment size for meaningful analysis
        """
        self.segment_size = segment_size
        self.min_segment_size = min_segment_size
        self.logger = logging.getLogger(__name__)

    def calculate_homogeneity_score(self, data: bytes,
                                   segment_size: Optional[int] = None) -> float:
        """
        Calculate overall homogeneity score for binary data.

        Args:
            data: Binary data to analyze
            segment_size: Segment size for analysis (uses default if None)

        Returns:
            Overall homogeneity score (0.0 to 1.0, higher is more homogeneous)
        """
        if not data:
            return 0.0

        metrics = self.analyze_homogeneity(data, segment_size)
        return metrics.overall_homogeneity

    def analyze_homogeneity(self, data: bytes,
                          segment_size: Optional[int] = None) -> HomogeneityMetrics:
        """
        Perform comprehensive homogeneity analysis.

        Args:
            data: Binary data to analyze
            segment_size: Segment size for analysis (uses default if None)

        Returns:
            Comprehensive homogeneity metrics
        """
        if not data:
            return HomogeneityMetrics.create_empty()

        # Determine segment size
        seg_size = segment_size or self.segment_size
        seg_size = max(seg_size, self.min_segment_size)

        # Calculate basic data characteristics
        total_entropy = self._calculate_entropy(data)

        # Segment the data
        segments = self._segment_data(data, seg_size)

        if len(segments) < 2:
            # For very small data, use simple homogeneity measures
            return self._analyze_small_data(data, seg_size)

        # Calculate per-segment metrics
        segment_entropies = []
        segment_pattern_scores = []
        segment_homogeneity_scores = []

        for segment in segments:
            entropy = self._calculate_entropy(segment)
            pattern_score = self._calculate_pattern_score(segment)
            homogeneity = self._calculate_segment_homogeneity(segment)

            segment_entropies.append(entropy)
            segment_pattern_scores.append(pattern_score)
            segment_homogeneity_scores.append(homogeneity)

        # Calculate aggregate metrics
        entropy_uniformity = self._calculate_entropy_uniformity(segment_entropies)
        pattern_consistency = self._calculate_pattern_consistency(segment_pattern_scores)
        structural_regularity = self._calculate_structural_regularity(segments)

        # Calculate advanced metrics
        entropy_std = np.std(segment_entropies) if len(segment_entropies) > 1 else 0.0
        entropy_gradient = self._calculate_entropy_gradient(segment_entropies)
        local_uniformity = np.mean(segment_homogeneity_scores) if segment_homogeneity_scores else 0.0
        global_uniformity = self._calculate_global_uniformity(data, segments)

        # Calculate byte distribution variance
        byte_distribution_variance = self._calculate_byte_distribution_variance(data)

        # Calculate pattern repetition
        pattern_repetition = self._calculate_overall_pattern_repetition(data)

        # Calculate overall homogeneity score
        overall_homogeneity = self._calculate_overall_homogeneity(
            entropy_uniformity, pattern_consistency, structural_regularity,
            local_uniformity, global_uniformity
        )

        return HomogeneityMetrics(
            overall_homogeneity=overall_homogeneity,
            entropy_uniformity=entropy_uniformity,
            pattern_consistency=pattern_consistency,
            structural_regularity=structural_regularity,
            entropy_std=entropy_std,
            pattern_repetition=pattern_repetition,
            byte_distribution_variance=byte_distribution_variance,
            segment_homogeneity_scores=segment_homogeneity_scores,
            total_entropy=total_entropy,
            entropy_gradient=entropy_gradient,
            local_uniformity=local_uniformity,
            global_uniformity=global_uniformity,
            segment_size=seg_size,
            num_segments=len(segments),
            data_size=len(data)
        )

    def _segment_data(self, data: bytes, segment_size: int) -> List[bytes]:
        """
        Segment binary data into equal-sized chunks.

        Args:
            data: Binary data to segment
            segment_size: Size of each segment

        Returns:
            List of data segments
        """
        segments = []
        for i in range(0, len(data), segment_size):
            segment = data[i:i + segment_size]
            segments.append(segment)
        return segments

    def _analyze_small_data(self, data: bytes, segment_size: int) -> HomogeneityMetrics:
        """
        Analyze homogeneity for small data sets.

        Args:
            data: Small binary data to analyze
            segment_size: Segment size used for analysis

        Returns:
            Homogeneity metrics for small data
        """
        total_entropy = self._calculate_entropy(data)
        pattern_score = self._calculate_pattern_score(data)
        byte_variance = self._calculate_byte_distribution_variance(data)

        # For small data, use simplified scoring
        entropy_uniformity = 1.0 - min(total_entropy / 8.0, 1.0)
        pattern_consistency = pattern_score
        structural_regularity = 1.0 - byte_variance

        overall_homogeneity = (entropy_uniformity + pattern_consistency + structural_regularity) / 3.0

        return HomogeneityMetrics(
            overall_homogeneity=overall_homogeneity,
            entropy_uniformity=entropy_uniformity,
            pattern_consistency=pattern_consistency,
            structural_regularity=structural_regularity,
            entropy_std=0.0,
            pattern_repetition=pattern_score,
            byte_distribution_variance=byte_variance,
            segment_homogeneity_scores=[overall_homogeneity],
            total_entropy=total_entropy,
            entropy_gradient=0.0,
            local_uniformity=overall_homogeneity,
            global_uniformity=overall_homogeneity,
            segment_size=segment_size,
            num_segments=1,
            data_size=len(data)
        )

    def _calculate_entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy of binary data.

        Args:
            data: Binary data to analyze

        Returns:
            Shannon entropy (0.0 to 8.0 for byte data)
        """
        if not data:
            return 0.0

        byte_counts = Counter(data)
        total_bytes = len(data)
        entropy = 0.0

        for count in byte_counts.values():
            probability = count / total_bytes
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _calculate_pattern_score(self, data: bytes) -> float:
        """
        Calculate pattern consistency score.

        Args:
            data: Binary data to analyze

        Returns:
            Pattern consistency score (0.0 to 1.0, higher is more consistent)
        """
        if len(data) < 4:
            return 0.0

        # Look for repeated patterns of different lengths
        max_pattern_length = min(16, len(data) // 4)
        total_patterns = 0
        repeated_patterns = 0

        for pattern_length in range(2, max_pattern_length + 1):
            patterns = set()
            pattern_counts = defaultdict(int)

            # Count all patterns of this length
            for i in range(len(data) - pattern_length + 1):
                pattern = data[i:i + pattern_length]
                patterns.add(pattern)
                pattern_counts[pattern] += 1

            total_patterns += len(patterns)

            # Count repeated patterns
            repeated_patterns += sum(1 for count in pattern_counts.values() if count > 1)

        if total_patterns == 0:
            return 0.0

        # Calculate repetition score
        repetition_rate = repeated_patterns / total_patterns
        return repetition_rate

    def _calculate_segment_homogeneity(self, segment: bytes) -> float:
        """
        Calculate homogeneity score for a single segment.

        Args:
            segment: Binary data segment to analyze

        Returns:
            Segment homogeneity score (0.0 to 1.0)
        """
        if not segment:
            return 0.0

        # Calculate multiple homogeneity indicators
        entropy = self._calculate_entropy(segment)
        pattern_score = self._calculate_pattern_score(segment)

        # Calculate byte distribution uniformity
        byte_counts = Counter(segment)
        expected_count = len(segment) / 256
        byte_variance = sum((count - expected_count) ** 2 for count in byte_counts.values()) / 256
        max_variance = ((len(segment) / 256) * (255 - len(segment) / 256) ** 2 +
                        (255 * (len(segment) / 256 - 1) ** 2))
        byte_uniformity = 1.0 - (byte_variance / max_variance if max_variance > 0 else 0.0)

        # Combine indicators
        entropy_score = 1.0 - min(entropy / 8.0, 1.0)  # Lower entropy = more homogeneous
        overall_score = (entropy_score * 0.4 + pattern_score * 0.4 + byte_uniformity * 0.2)

        return overall_score

    def _calculate_entropy_uniformity(self, segment_entropies: List[float]) -> float:
        """
        Calculate how uniform entropy is across segments.

        Args:
            segment_entropies: List of entropy values for each segment

        Returns:
            Entropy uniformity score (0.0 to 1.0, higher is more uniform)
        """
        if not segment_entropies:
            return 0.0

        if len(segment_entropies) == 1:
            return 1.0

        # Calculate coefficient of variation
        mean_entropy = np.mean(segment_entropies)
        std_entropy = np.std(segment_entropies)

        if mean_entropy == 0:
            return 1.0

        cv = std_entropy / mean_entropy
        # Lower coefficient of variation = more uniform
        uniformity = 1.0 - min(cv / 2.0, 1.0)  # Normalize to 0-1 range

        return uniformity

    def _calculate_pattern_consistency(self, pattern_scores: List[float]) -> float:
        """
        Calculate consistency of patterns across segments.

        Args:
            pattern_scores: List of pattern scores for each segment

        Returns:
            Pattern consistency score (0.0 to 1.0)
        """
        if not pattern_scores:
            return 0.0

        if len(pattern_scores) == 1:
            return pattern_scores[0]

        # Calculate standard deviation of pattern scores
        mean_pattern = np.mean(pattern_scores)
        std_pattern = np.std(pattern_scores)

        # Lower variation = more consistent
        consistency = 1.0 - min(std_pattern / 2.0, 1.0)

        # Weight by mean pattern score (high patterns should be consistent)
        consistency = consistency * (0.5 + 0.5 * mean_pattern)

        return consistency

    def _calculate_structural_regularity(self, segments: List[bytes]) -> float:
        """
        Calculate structural regularity across segments.

        Args:
            segments: List of data segments

        Returns:
            Structural regularity score (0.0 to 1.0)
        """
        if len(segments) < 2:
            return 0.0

        # Calculate similarity between consecutive segments
        similarities = []

        for i in range(len(segments) - 1):
            similarity = self._calculate_segment_similarity(segments[i], segments[i + 1])
            similarities.append(similarity)

        return np.mean(similarities) if similarities else 0.0

    def _calculate_segment_similarity(self, seg1: bytes, seg2: bytes) -> float:
        """
        Calculate similarity between two segments.

        Args:
            seg1: First segment
            seg2: Second segment

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if len(seg1) != len(seg2):
            # For different lengths, compare overlapping part
            min_len = min(len(seg1), len(seg2))
            seg1 = seg1[:min_len]
            seg2 = seg2[:min_len]

        if not seg1:
            return 1.0

        # Calculate byte-wise similarity
        matching_bytes = sum(1 for a, b in zip(seg1, seg2) if a == b)
        similarity = matching_bytes / len(seg1)

        return similarity

    def _calculate_entropy_gradient(self, segment_entropies: List[float]) -> float:
        """
        Calculate the gradient of entropy across segments.

        Args:
            segment_entropies: List of entropy values for each segment

        Returns:
            Entropy gradient score (lower = more uniform)
        """
        if len(segment_entropies) < 2:
            return 0.0

        # Calculate average absolute change in entropy between consecutive segments
        gradients = []
        for i in range(len(segment_entropies) - 1):
            gradient = abs(segment_entropies[i + 1] - segment_entropies[i])
            gradients.append(gradient)

        avg_gradient = np.mean(gradients) if gradients else 0.0

        # Normalize to 0-1 range (lower gradient = more homogeneous)
        normalized_gradient = min(avg_gradient / 4.0, 1.0)  # Max reasonable gradient is 4.0
        uniformity = 1.0 - normalized_gradient

        return uniformity

    def _calculate_global_uniformity(self, data: bytes, segments: List[bytes]) -> float:
        """
        Calculate global uniformity considering the entire data structure.

        Args:
            data: Original binary data
            segments: Segmented data

        Returns:
            Global uniformity score (0.0 to 1.0)
        """
        if not data:
            return 0.0

        # Calculate overall entropy
        total_entropy = self._calculate_entropy(data)

        # Calculate segment-wise average entropy
        if segments:
            segment_avg_entropy = np.mean([self._calculate_entropy(seg) for seg in segments])
        else:
            segment_avg_entropy = total_entropy

        # Compare total entropy with segment average
        entropy_diff = abs(total_entropy - segment_avg_entropy)

        # Lower difference = more uniform structure
        uniformity = 1.0 - min(entropy_diff / 4.0, 1.0)

        return uniformity

    def _calculate_byte_distribution_variance(self, data: bytes) -> float:
        """
        Calculate variance in byte frequency distribution.

        Args:
            data: Binary data to analyze

        Returns:
            Byte distribution variance (0.0 to 1.0, lower is more uniform)
        """
        if not data:
            return 0.0

        byte_counts = Counter(data)
        expected_count = len(data) / 256

        # Calculate variance from uniform distribution
        variance = sum((count - expected_count) ** 2 for count in byte_counts.values())

        # Normalize variance
        max_possible_variance = len(data) * (255 * len(data) / 256)
        normalized_variance = variance / max_possible_variance if max_possible_variance > 0 else 0.0

        return normalized_variance

    def _calculate_overall_pattern_repetition(self, data: bytes) -> float:
        """
        Calculate overall pattern repetition in the data.

        Args:
            data: Binary data to analyze

        Returns:
            Pattern repetition score (0.0 to 1.0)
        """
        if len(data) < 8:
            return 0.0

        repetitions = 0
        total_checks = 0

        # Check for patterns of different lengths
        for pattern_length in range(2, min(16, len(data) // 8)):
            for i in range(len(data) - pattern_length * 2):
                pattern = data[i:i + pattern_length]
                # Check if pattern repeats later
                if pattern in data[i + pattern_length:]:
                    repetitions += 1
                total_checks += 1

        return repetitions / total_checks if total_checks > 0 else 0.0

    def _calculate_overall_homogeneity(self, entropy_uniformity: float,
                                      pattern_consistency: float,
                                      structural_regularity: float,
                                      local_uniformity: float,
                                      global_uniformity: float) -> float:
        """
        Calculate overall homogeneity score from individual metrics.

        Args:
            entropy_uniformity: Entropy uniformity across segments
            pattern_consistency: Pattern consistency score
            structural_regularity: Structural regularity score
            local_uniformity: Local uniformity score
            global_uniformity: Global uniformity score

        Returns:
            Overall homogeneity score (0.0 to 1.0)
        """
        # Weighted combination of different homogeneity aspects
        # Higher weights for entropy and pattern consistency as they're most important
        weights = {
            'entropy_uniformity': 0.3,
            'pattern_consistency': 0.25,
            'structural_regularity': 0.2,
            'local_uniformity': 0.15,
            'global_uniformity': 0.1
        }

        overall_score = (
            entropy_uniformity * weights['entropy_uniformity'] +
            pattern_consistency * weights['pattern_consistency'] +
            structural_regularity * weights['structural_regularity'] +
            local_uniformity * weights['local_uniformity'] +
            global_uniformity * weights['global_uniformity']
        )

        return overall_score

    def compare_homogeneity(self, original_data: bytes,
                           transformed_data: bytes) -> Dict[str, Any]:
        """
        Compare homogeneity between original and transformed data.

        Args:
            original_data: Original binary data
            transformed_data: Transformed binary data

        Returns:
            Comparison results with improvement metrics
        """
        original_metrics = self.analyze_homogeneity(original_data)
        transformed_metrics = self.analyze_homogeneity(transformed_data)

        # Calculate improvements
        overall_improvement = transformed_metrics.overall_homogeneity - original_metrics.overall_homogeneity
        overall_improvement_percent = (overall_improvement / original_metrics.overall_homogeneity * 100) if original_metrics.overall_homogeneity > 0 else 0

        return {
            'original_score': original_metrics.overall_homogeneity,
            'transformed_score': transformed_metrics.overall_homogeneity,
            'improvement': overall_improvement,
            'improvement_percent': overall_improvement_percent,
            'original_metrics': original_metrics,
            'transformed_metrics': transformed_metrics,
            'better': overall_improvement > 0
        }

    def visualize_homogeneity(self, data: bytes, output_path: Optional[str] = None):
        """
        Create a visualization of homogeneity analysis.

        Args:
            data: Binary data to visualize
            output_path: Path to save visualization (optional)
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
        except ImportError:
            self.logger.warning("Matplotlib not available for visualization")
            return

        metrics = self.analyze_homogeneity(data)

        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Binary Homogeneity Analysis\nOverall Score: {metrics.overall_homogeneity:.3f}',
                      fontsize=16, fontweight='bold')

        # 1. Entropy across segments
        if metrics.segment_homogeneity_scores:
            axes[0, 0].plot(metrics.segment_homogeneity_scores, 'b-', linewidth=2, marker='o')
            axes[0, 0].set_title('Homogeneity Score by Segment')
            axes[0, 0].set_xlabel('Segment Index')
            axes[0, 0].set_ylabel('Homogeneity Score')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].set_ylim([0, 1])

        # 2. Metric breakdown
        metric_names = ['Entropy\nUniformity', 'Pattern\nConsistency',
                        'Structural\nRegularity', 'Local\nUniformity', 'Global\nUniformity']
        metric_values = [metrics.entropy_uniformity, metrics.pattern_consistency,
                        metrics.structural_regularity, metrics.local_uniformity,
                        metrics.global_uniformity]

        bars = axes[0, 1].bar(metric_names, metric_values, color=['skyblue', 'lightgreen',
                                 'salmon', 'gold', 'plum'])
        axes[0, 1].set_title('Homogeneity Metrics Breakdown')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].set_ylim([0, 1])
        axes[0, 1].tick_params(axis='x', rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.3f}', ha='center', va='bottom')

        # 3. Byte distribution
        byte_counts = Counter(data)
        bytes_256 = list(range(256))
        counts_256 = [byte_counts.get(b, 0) for b in bytes_256]

        axes[1, 0].hist(bytes_256, bins=32, weights=counts_256, color='steelblue', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Byte Frequency Distribution')
        axes[1, 0].set_xlabel('Byte Value')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. Summary statistics
        axes[1, 1].axis('off')
        summary_text = f"""
        Homogeneity Analysis Summary

        Data Size: {metrics.data_size:,} bytes
        Segments: {metrics.num_segments}
        Segment Size: {metrics.segment_size} bytes

        Overall Homogeneity: {metrics.overall_homogeneity:.3f}
        Total Entropy: {metrics.total_entropy:.3f}
        Entropy Std Dev: {metrics.entropy_std:.3f}

        Pattern Repetition: {metrics.pattern_repetition:.3f}
        Byte Distribution Variance: {metrics.byte_distribution_variance:.3f}
        """

        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=10,
                        verticalalignment='center', fontfamily='monospace')
        axes[1, 1].set_title('Summary Statistics')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Homogeneity visualization saved to {output_path}")
        else:
            plt.show()

        plt.close()


# Convenience function for quick analysis
def quick_homogeneity_analysis(data: bytes) -> Dict[str, Any]:
    """
    Quick homogeneity analysis for binary data.

    Args:
        data: Binary data to analyze

    Returns:
        Dictionary with analysis results
    """
    scorer = HomogeneityScorer()
    metrics = scorer.analyze_homogeneity(data)

    return {
        'overall_score': metrics.overall_homogeneity,
        'entropy_uniformity': metrics.entropy_uniformity,
        'pattern_consistency': metrics.pattern_consistency,
        'structural_regularity': metrics.structural_regularity,
        'total_entropy': metrics.total_entropy,
        'data_size': metrics.data_size,
        'num_segments': metrics.num_segments,
        'recommendations': _get_homogeneity_recommendations(metrics)
    }


def _get_homogeneity_recommendations(metrics: HomogeneityMetrics) -> List[str]:
    """
    Get recommendations based on homogeneity analysis.

    Args:
        metrics: Homogeneity metrics

    Returns:
        List of recommendations
    """
    recommendations = []

    if metrics.overall_homogeneity < 0.3:
        recommendations.append("Low homogeneity detected. Consider applying transformation operations.")

    if metrics.entropy_uniformity < 0.5:
        recommendations.append("High entropy variation across segments. Try entropy redistribution operations.")

    if metrics.pattern_consistency < 0.4:
        recommendations.append("Inconsistent patterns. Consider pattern alignment operations.")

    if metrics.structural_regularity < 0.3:
        recommendations.append("Low structural regularity. Try structural optimization operations.")

    if metrics.pattern_repetition < 0.2:
        recommendations.append("Low pattern repetition. Data may be too random for effective homogenization.")

    if metrics.total_entropy > 7.0:
        recommendations.append("Very high entropy. Consider operations that create more predictable patterns.")

    if not recommendations:
        recommendations.append("Good homogeneity achieved. Consider fine-tuning with specific target metrics.")

    return recommendations