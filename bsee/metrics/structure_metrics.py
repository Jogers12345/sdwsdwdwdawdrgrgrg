"""
Structure metrics for binary analysis.
"""

import numpy as np
from typing import Dict, List, Tuple


class StructureMetrics:
    """Collection of structure-based metrics."""

    def __init__(self):
        """Initialize structure metrics."""
        self.metrics = self._create_metrics()

    def _create_metrics(self) -> Dict[str, callable]:
        """Create all structure metrics."""
        return {
            'alignment_score': self.alignment_score,
            'block_detection_score': self.block_detection_score,
            'repeating_block_count': self.repeating_block_count,
            'block_size_variance': self.block_size_variance,
            'structure_regularity': self.structure_regularity,
            'segmentation_score': self.segmentation_score,
            'pattern_coherence': self.pattern_coherence,
            'hierarchical_structure': self.hierarchical_structure,
            'byte_alignment_index': self.byte_alignment_index,
            'structural_entropy': self.structural_entropy
        }

    def get_metrics(self) -> Dict[str, callable]:
        """Get all metrics."""
        return self.metrics

    def get_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""
        metadata_map = {
            'alignment_score': {
                'category': 'structure',
                'description': 'Score based on byte alignment patterns',
                'range': [0, 1],
                'higher_better': True
            },
            'block_detection_score': {
                'category': 'structure',
                'description': 'Score for detectable block structures',
                'range': [0, 1],
                'higher_better': True
            },
            'repeating_block_count': {
                'category': 'structure',
                'description': 'Count of repeating blocks',
                'range': [0, 'file_size/block_size'],
                'higher_better': True
            },
            'block_size_variance': {
                'category': 'structure',
                'description': 'Variance of detected block sizes',
                'range': [0, 'file_size²'],
                'higher_better': False
            },
            'structure_regularity': {
                'category': 'structure',
                'description': 'Regularity of structural patterns',
                'range': [0, 1],
                'higher_better': True
            },
            'segmentation_score': {
                'category': 'structure',
                'description': 'Score for natural segmentation points',
                'range': [0, 1],
                'higher_better': True
            },
            'pattern_coherence': {
                'category': 'structure',
                'description': 'Coherence of patterns across segments',
                'range': [0, 1],
                'higher_better': True
            },
            'hierarchical_structure': {
                'category': 'structure',
                'description': 'Score for hierarchical structure',
                'range': [0, 1],
                'higher_better': True
            },
            'byte_alignment_index': {
                'category': 'structure',
                'description': 'Index of byte alignment patterns',
                'range': [0, 1],
                'higher_better': True
            },
            'structural_entropy': {
                'category': 'structure',
                'description': 'Entropy of structural features',
                'range': [0, 'log2(n_structures)'],
                'higher_better': False
            }
        }
        return metadata_map.get(metric_name, {})

    def alignment_score(self, binary_data: bytes) -> float:
        """Score based on byte alignment patterns."""
        if len(binary_data) < 16:
            return 0.0

        # Check for alignment at common boundaries (4, 8, 16, 32 bytes)
        alignment_scores = []

        for alignment in [4, 8, 16, 32]:
            if len(binary_data) >= alignment * 2:
                # Count aligned positions
                aligned_positions = 0
                total_positions = len(binary_data) // alignment

                for i in range(total_positions):
                    pos = i * alignment
                    if pos < len(binary_data):
                        # Check if this position shows alignment characteristics
                        if self._is_aligned_position(binary_data, pos, alignment):
                            aligned_positions += 1

                score = aligned_positions / total_positions if total_positions > 0 else 0.0
                alignment_scores.append(score)

        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0

    def _is_aligned_position(self, binary_data: bytes, pos: int, alignment: int) -> bool:
        """Check if a position shows alignment characteristics."""
        if pos + alignment > len(binary_data):
            return False

        # Simple heuristic: check if the position starts a repeated pattern
        if pos + alignment * 2 <= len(binary_data):
            pattern1 = binary_data[pos:pos + alignment]
            pattern2 = binary_data[pos + alignment:pos + alignment * 2]
            similarity = sum(a == b for a, b in zip(pattern1, pattern2)) / alignment
            return similarity > 0.8

        return False

    def block_detection_score(self, binary_data: bytes) -> float:
        """Score for detectable block structures."""
        if len(binary_data) < 32:
            return 0.0

        # Try different block sizes
        block_sizes = [4, 8, 16, 32, 64, 128, 256]
        block_scores = []

        for block_size in block_sizes:
            if len(binary_data) >= block_size * 2:
                score = self._detect_blocks_of_size(binary_data, block_size)
                block_scores.append(score)

        return max(block_scores) if block_scores else 0.0

    def _detect_blocks_of_size(self, binary_data: bytes, block_size: int) -> float:
        """Detect blocks of a specific size."""
        # Count unique blocks
        blocks = set()
        for i in range(0, len(binary_data) - block_size + 1, block_size):
            block = binary_data[i:i + block_size]
            blocks.add(block)

        total_blocks = len(binary_data) // block_size
        unique_blocks = len(blocks)

        # Score based on repetition (fewer unique blocks = more structure)
        if total_blocks > 0:
            repetition_score = 1.0 - (unique_blocks / total_blocks)
            return repetition_score

        return 0.0

    def repeating_block_count(self, binary_data: bytes) -> float:
        """Count of repeating blocks."""
        if len(binary_data) < 8:
            return 0.0

        # Use default block size of 16 bytes
        block_size = min(16, len(binary_data) // 4)
        if block_size < 4:
            return 0.0

        block_counts = {}
        for i in range(0, len(binary_data) - block_size + 1, block_size):
            block = binary_data[i:i + block_size]
            block_counts[block] = block_counts.get(block, 0) + 1

        # Count blocks that appear more than once
        repeating_blocks = sum(1 for count in block_counts.values() if count > 1)
        return float(repeating_blocks)

    def block_size_variance(self, binary_data: bytes) -> float:
        """Variance of detected block sizes."""
        if len(binary_data) < 16:
            return 0.0

        # Detect multiple block sizes
        detected_sizes = []
        for block_size in [4, 8, 16, 32, 64]:
            if len(binary_data) >= block_size * 3:
                score = self._detect_blocks_of_size(binary_data, block_size)
                if score > 0.3:  # Threshold for considering this size significant
                    detected_sizes.append(block_size)

        if len(detected_sizes) < 2:
            return 0.0

        # Calculate variance
        mean_size = sum(detected_sizes) / len(detected_sizes)
        variance = sum((size - mean_size) ** 2 for size in detected_sizes) / len(detected_sizes)

        return variance

    def structure_regularity(self, binary_data: bytes) -> float:
        """Regularity of structural patterns."""
        if len(binary_data) < 32:
            return 0.0

        # Divide data into chunks and look for regular patterns
        chunk_size = min(32, len(binary_data) // 8)
        if chunk_size < 4:
            return 0.0

        similarities = []
        chunks = []

        # Collect chunks
        for i in range(0, len(binary_data), chunk_size):
            chunk = binary_data[i:i + chunk_size]
            if len(chunk) == chunk_size:
                chunks.append(chunk)

        # Compare consecutive chunks
        for i in range(len(chunks) - 1):
            similarity = sum(a == b for a, b in zip(chunks[i], chunks[i + 1])) / chunk_size
            similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def segmentation_score(self, binary_data: bytes) -> float:
        """Score for natural segmentation points."""
        if len(binary_data) < 64:
            return 0.0

        # Look for natural break points based on byte distribution changes
        window_size = min(32, len(binary_data) // 8)
        if window_size < 8:
            return 0.0

        segment_scores = []
        for i in range(window_size, len(binary_data) - window_size, window_size // 2):
            # Compare distributions before and after this point
            before_window = binary_data[i - window_size:i]
            after_window = binary_data[i:i + window_size]

            # Simple distribution similarity
            before_counts = [0] * 256
            after_counts = [0] * 256

            for byte_val in before_window:
                before_counts[byte_val] += 1
            for byte_val in after_window:
                after_counts[byte_val] += 1

            # Calculate similarity
            similarity = sum(min(before_counts[j], after_counts[j]) for j in range(256))
            total_before = sum(before_counts)
            total_after = sum(after_counts)
            total_min = min(total_before, total_after)

            if total_min > 0:
                segment_score = 1.0 - (similarity / total_min)
                segment_scores.append(segment_score)

        return sum(segment_scores) / len(segment_scores) if segment_scores else 0.0

    def pattern_coherence(self, binary_data: bytes) -> float:
        """Coherence of patterns across segments."""
        if len(binary_data) < 64:
            return 0.0

        # Divide into segments and check for consistent patterns
        num_segments = min(8, len(binary_data) // 16)
        if num_segments < 2:
            return 0.0

        segment_size = len(binary_data) // num_segments
        patterns = []

        for i in range(num_segments):
            start = i * segment_size
            end = start + segment_size
            segment = binary_data[start:end]

            # Extract simple pattern (first 8 bytes)
            if len(segment) >= 8:
                pattern = segment[:8]
                patterns.append(pattern)

        if len(patterns) < 2:
            return 0.0

        # Calculate coherence based on pattern similarity
        total_similarity = 0
        comparisons = 0

        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                similarity = sum(a == b for a, b in zip(patterns[i], patterns[j])) / len(patterns[i])
                total_similarity += similarity
                comparisons += 1

        return total_similarity / comparisons if comparisons > 0 else 0.0

    def hierarchical_structure(self, binary_data: bytes) -> float:
        """Score for hierarchical structure."""
        if len(binary_data) < 64:
            return 0.0

        # Look for structure at multiple scales
        scale_scores = []

        for scale in [8, 16, 32, 64]:
            if len(binary_data) >= scale * 4:
                score = self._analyze_scale_structure(binary_data, scale)
                scale_scores.append(score)

        return sum(scale_scores) / len(scale_scores) if scale_scores else 0.0

    def _analyze_scale_structure(self, binary_data: bytes, scale: int) -> float:
        """Analyze structure at a specific scale."""
        # Count patterns at this scale
        patterns = set()
        for i in range(0, len(binary_data) - scale + 1, scale):
            pattern = binary_data[i:i + scale]
            patterns.add(pattern)

        total_patterns = len(binary_data) // scale
        unique_patterns = len(patterns)

        if total_patterns == 0:
            return 0.0

        # Structure score based on pattern repetition
        structure_score = 1.0 - (unique_patterns / total_patterns)
        return structure_score

    def byte_alignment_index(self, binary_data: bytes) -> float:
        """Index of byte alignment patterns."""
        # Similar to alignment_score but focused on common alignments
        common_alignments = [2, 4, 8, 16]  # Powers of 2

        alignment_indices = []
        for alignment in common_alignments:
            if len(binary_data) >= alignment * 4:
                # Check for periodicity at this alignment
                periodic_score = self._check_periodicity_at_alignment(binary_data, alignment)
                alignment_indices.append(periodic_score)

        return sum(alignment_indices) / len(alignment_indices) if alignment_indices else 0.0

    def _check_periodicity_at_alignment(self, binary_data: bytes, alignment: int) -> float:
        """Check for periodicity at a specific alignment."""
        if len(binary_data) < alignment * 2:
            return 0.0

        # Compare bytes at alignment offsets
        matches = 0
        total_comparisons = 0

        for i in range(len(binary_data) - alignment):
            if binary_data[i] == binary_data[i + alignment]:
                matches += 1
            total_comparisons += 1

        return matches / total_comparisons if total_comparisons > 0 else 0.0

    def structural_entropy(self, binary_data: bytes) -> float:
        """Entropy of structural features."""
        if len(binary_data) < 32:
            return 0.0

        # Extract structural features (byte changes, runs, etc.)
        features = []

        # Add byte change positions
        for i in range(1, len(binary_data)):
            if binary_data[i] != binary_data[i - 1]:
                features.append(('change', i % 256))

        # Add run lengths
        current_run = 1
        for i in range(1, len(binary_data)):
            if binary_data[i] == binary_data[i - 1]:
                current_run += 1
            else:
                features.append(('run_length', min(current_run, 255)))
                current_run = 1

        if current_run > 1:
            features.append(('run_length', min(current_run, 255)))

        if not features:
            return 0.0

        # Calculate entropy of features
        from collections import Counter
        feature_counts = Counter(features)
        total_features = len(features)

        import math
        entropy = 0.0
        for count in feature_counts.values():
            probability = count / total_features
            entropy -= probability * math.log2(probability)

        return entropy