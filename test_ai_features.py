#!/usr/bin/env python3
"""
Simple test of AI features without heavy dependencies.
"""

import logging
import time
import random
import hashlib
from collections import Counter
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleFeatureExtractor:
    """Simple feature extractor without numpy dependency."""

    def extract_data_features(self, data: bytes) -> Dict[str, Any]:
        """Extract basic features from binary data."""
        if not data:
            return {
                'size': 0,
                'entropy': 0.0,
                'byte_frequency': {},
                'pattern_repetition': 0.0,
                'compression_ratio_estimate': 1.0,
                'data_type_score': {},
                'hash_signature': hashlib.md5(data).hexdigest()
            }

        size = len(data)
        entropy = self._calculate_entropy(data)
        byte_frequency = self._calculate_byte_frequency(data)
        pattern_repetition = self._calculate_pattern_repetition(data)
        compression_ratio = self._estimate_compression_ratio(data)
        data_type_score = self._classify_data_type(data)

        return {
            'size': size,
            'entropy': entropy,
            'byte_frequency': byte_frequency,
            'pattern_repetition': pattern_repetition,
            'compression_ratio_estimate': compression_ratio,
            'data_type_score': data_type_score,
            'hash_signature': hashlib.md5(data).hexdigest()
        }

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy."""
        if not data:
            return 0.0

        byte_counts = Counter(data)
        total_bytes = len(data)
        entropy = 0.0

        for count in byte_counts.values():
            probability = count / total_bytes
            if probability > 0:
                import math
                entropy -= probability * math.log2(probability)

        return entropy

    def _calculate_byte_frequency(self, data: bytes) -> Dict[int, float]:
        """Calculate byte frequency distribution."""
        if not data:
            return {}

        byte_counts = Counter(data)
        total_bytes = len(data)

        return {byte: count / total_bytes for byte, count in byte_counts.items()}

    def _calculate_pattern_repetition(self, data: bytes) -> float:
        """Calculate how repetitive the data is."""
        if len(data) < 4:
            return 0.0

        max_pattern_length = min(16, len(data) // 4)
        repetitions = 0
        total_checks = 0

        for pattern_length in range(2, max_pattern_length + 1):
            for i in range(len(data) - pattern_length * 2):
                pattern = data[i:i + pattern_length]
                if pattern in data[i + pattern_length:]:
                    repetitions += 1
                total_checks += 1

        return repetitions / total_checks if total_checks > 0 else 0.0

    def _estimate_compression_ratio(self, data: bytes) -> float:
        """Estimate compression ratio."""
        if len(data) < 100:
            return 1.0

        entropy = self._calculate_entropy(data)
        pattern_repetition = self._calculate_pattern_repetition(data)
        compressibility = pattern_repetition * (1 - entropy / 8)
        return max(0.3, 1.0 - compressibility * 0.7)

    def _classify_data_type(self, data: bytes) -> Dict[str, float]:
        """Classify data type."""
        scores = {}

        # Text detection
        printable_count = sum(1 for b in data if 32 <= b <= 126 or b in [9, 10, 13])
        text_score = printable_count / len(data)
        scores['text'] = text_score * 0.7

        # Binary detection (high entropy)
        entropy = self._calculate_entropy(data)
        scores['binary'] = min(entropy / 8, 1.0)

        # Compressed detection
        compressed_score = min(entropy / 7.5, 1.0) * 0.8
        if data.startswith(b'\x1f\x8b'):  # gzip
            compressed_score = 1.0
        scores['compressed'] = compressed_score

        # Encrypted detection
        encrypted_score = (min(entropy / 7.8, 1.0) + (1.0 - min(pattern_repetition * 10, 1.0))) / 2
        scores['encrypted'] = encrypted_score

        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v / total_score for k, v in scores.items()}

        return scores


class SimpleOptimizer:
    """Simple operation sequence optimizer without ML."""

    def __init__(self):
        self.feature_extractor = SimpleFeatureExtractor()
        self.available_operations = [
            {'type': 'xor', 'parameters': {'key': 42}},
            {'type': 'xor', 'parameters': {'key': 0xFF}},
            {'type': 'add_constant', 'parameters': {'value': 10}},
            {'type': 'rotate_left', 'parameters': {'bits': 1}},
            {'type': 'burrows_wheeler', 'parameters': {}},
            {'type': 'move_to_front', 'parameters': {}},
        ]

    def recommend_sequence(self, data: bytes) -> List[Dict[str, Any]]:
        """Recommend operation sequence based on data analysis."""
        features = self.feature_extractor.extract_data_features(data)
        data_type = max(features['data_type_score'].items(), key=lambda x: x[1])[0] if features['data_type_score'] else 'binary'

        # Simple rule-based recommendations
        if data_type == 'text':
            return [{'type': 'xor', 'parameters': {'key': 32}}]
        elif data_type == 'compressed':
            return [{'type': 'huffman_decode', 'parameters': {}}]
        elif data_type == 'encrypted':
            return [{'type': 'xor', 'parameters': {'key': 0x42}}]
        elif data_type == 'binary':
            if features['entropy'] > 7.0:
                return [{'type': 'simple_transform', 'parameters': {}}]
            else:
                return [{'type': 'burrows_wheeler', 'parameters': {}}]
        else:
            return [{'type': 'xor', 'parameters': {'key': 42}}]

    def analyze_input(self, data: bytes) -> Dict[str, Any]:
        """Analyze input data and provide recommendations."""
        features = self.feature_extractor.extract_data_features(data)
        recommended_sequence = self.recommend_sequence(data)

        return {
            'size_bytes': features['size'],
            'entropy': features['entropy'],
            'compression_ratio_estimate': features['compression_ratio_estimate'],
            'pattern_repetition': features['pattern_repetition'],
            'data_type_classification': features['data_type_score'],
            'recommended_operations': [op['type'] for op in recommended_sequence],
            'recommended_sequence': recommended_sequence,
            'processing_difficulty': self._assess_difficulty(features)
        }

    def _assess_difficulty(self, features: Dict[str, Any]) -> str:
        """Assess processing difficulty."""
        difficulty_score = 0

        if features['size'] > 1024 * 1024:
            difficulty_score += 3
        elif features['size'] > 10240:
            difficulty_score += 2
        elif features['size'] > 1024:
            difficulty_score += 1

        if features['entropy'] > 7.5:
            difficulty_score += 2
        elif features['entropy'] > 6.0:
            difficulty_score += 1

        if features['pattern_repetition'] < 0.1:
            difficulty_score += 1

        if difficulty_score >= 5:
            return "hard"
        elif difficulty_score >= 3:
            return "medium"
        else:
            return "easy"


def mock_executor(data: bytes, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mock operation executor."""
    start_time = time.time()
    current_data = data

    for operation in operations:
        op_type = operation.get('type', 'unknown')
        params = operation.get('parameters', {})

        if op_type == 'xor':
            key = params.get('key', 0)
            current_data = bytes(b ^ key for b in current_data)
        elif op_type == 'add_constant':
            value = params.get('value', 0)
            current_data = bytes((b + value) % 256 for b in current_data)
        elif op_type == 'rotate_left':
            bits = params.get('bits', 1)
            result = bytearray()
            for byte in current_data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            current_data = bytes(result)
        elif op_type in ['burrows_wheeler', 'move_to_front', 'simple_transform']:
            current_data = current_data[::-1]

        time.sleep(0.001)  # Simulate processing time

    # Calculate mock score
    feature_extractor = SimpleFeatureExtractor()
    features = feature_extractor.extract_data_features(current_data)
    score = min(1.0, features['entropy'] / 8.0 + random.uniform(-0.1, 0.1))
    score = max(0.0, score)

    return {
        'success': True,
        'score': score,
        'execution_time': time.time() - start_time,
        'data': current_data
    }


def main():
    """Main test function."""
    logger.info("🚀 BSEE AI/ML Enhancement - Simple Feature Test")
    logger.info("=" * 60)

    # Test different data types
    test_cases = [
        ("Text data", b"Hello, World! This is a sample text for testing BSEE AI features." * 5),
        ("Binary data", bytes(range(256))),
        ("Random data", bytes([random.randint(0, 255) for _ in range(512)])),
        ("Repetitive data", b"ABCD" * 128),
        ("Structured data", b"HEADER: " + b"DATA" * 32 + b"FOOTER"),
    ]

    optimizer = SimpleOptimizer()

    for name, data in test_cases:
        logger.info(f"\n{'='*20} {name} {'='*20}")
        logger.info(f"Data size: {len(data)} bytes")

        # Analyze data
        analysis = optimizer.analyze_input(data)
        logger.info(f"Entropy: {analysis['entropy']:.3f}")
        logger.info(f"Pattern repetition: {analysis['pattern_repetition']:.3f}")
        logger.info(f"Data type: {max(analysis['data_type_classification'].items(), key=lambda x: x[1])[0] if analysis['data_type_classification'] else 'unknown'}")
        logger.info(f"Processing difficulty: {analysis['processing_difficulty']}")
        logger.info(f"Recommended operations: {analysis['recommended_operations']}")

        # Execute recommended sequence
        if analysis['recommended_sequence']:
            logger.info(f"Executing recommended sequence: {analysis['recommended_sequence']}")
            result = mock_executor(data, analysis['recommended_sequence'])
            logger.info(f"Execution score: {result['score']:.3f}")
            logger.info(f"Execution time: {result['execution_time']:.3f}s")

    logger.info(f"\n{'='*60}")
    logger.info("✅ Simple AI/ML Enhancement Test Completed!")
    logger.info("\nFeatures demonstrated:")
    logger.info("• Data type classification (text, binary, compressed, encrypted)")
    logger.info("• Entropy and pattern analysis")
    logger.info("• Intelligent operation sequence recommendation")
    logger.info("• Processing difficulty assessment")
    logger.info("• Automatic feature extraction")
    logger.info("• Mock execution with scoring")

    logger.info(f"\nTo enable full ML capabilities:")
    logger.info("• Install numpy, scikit-learn, pandas, joblib")
    logger.info("• Train models with historical data")
    logger.info("• Use ML-based sequence optimization")
    logger.info("• Enable continuous learning from execution results")


if __name__ == "__main__":
    main()