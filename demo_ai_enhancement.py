#!/usr/bin/env python3
"""
BSEE AI/ML Enhancement Demo
Demonstrates the AI-powered operation sequence optimization.
"""

import logging
import time
import random
from typing import Dict, Any, List

from bsee.ai import SequencePredictor, LearningPipeline, OptimizationPipeline
from bsee.ai.data import DataCollector, TrainingExample
from bsee.features import FeatureExtractor
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def mock_operation_executor(data: bytes, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Mock executor that simulates operation execution.
    In a real implementation, this would use the actual BSEE operations.
    """
    start_time = time.time()
    current_data = data

    try:
        for operation in operations:
            op_type = operation.get('type', 'unknown')
            params = operation.get('parameters', {})

            # Simulate different operations
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
            elif op_type in ['burrows_wheeler', 'move_to_front', 'huffman_encode']:
                # Simulate compression/transform operations
                current_data = current_data[::-1] + bytes([random.randint(0, 255) for _ in range(10)])

            # Add some processing delay
            time.sleep(0.001)

        execution_time = time.time() - start_time

        # Calculate a mock score based on data properties and operations
        feature_extractor = FeatureExtractor()
        features = feature_extractor.extract_data_features(current_data)

        # Mock scoring - in reality this would use the actual scoring system
        score = min(1.0, features.entropy / 8.0 + random.uniform(-0.1, 0.1))
        score = max(0.0, score)

        return {
            'success': True,
            'score': score,
            'execution_time': execution_time,
            'data': current_data,
            'metadata': {
                'operations_applied': len(operations),
                'final_entropy': features.entropy,
                'final_size': len(current_data)
            }
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'execution_time': time.time() - start_time,
            'score': 0.0
        }


def generate_sample_training_data():
    """Generate sample training data for demonstration."""
    logger.info("Generating sample training data...")

    data_collector = DataCollector()
    feature_extractor = FeatureExtractor()

    # Generate different types of sample data
    sample_data_types = [
        b"Hello world! This is a text sample for testing." * 10,  # Text data
        b"\x00\x01\x02\x03" * 256,  # Low entropy binary
        bytes([random.randint(0, 255) for _ in range(1024)]),  # High entropy
        b"AAAA" * 256,  # Repetitive data
        b"Structured data with patterns: " + b"ABCD" * 64,  # Structured
    ]

    operation_sequences = [
        [{'type': 'xor', 'parameters': {'key': 42}}],
        [{'type': 'add_constant', 'parameters': {'value': 10}}],
        [{'type': 'rotate_left', 'parameters': {'bits': 2}}],
        [{'type': 'xor', 'parameters': {'key': 42}}, {'type': 'add_constant', 'parameters': {'value': 10}}],
        [{'type': 'burrows_wheeler', 'parameters': {}}],
        [{'type': 'move_to_front', 'parameters': {}}],
        [{'type': 'huffman_encode', 'parameters': {}}],
    ]

    training_examples = []

    for data in sample_data_types:
        data_features = feature_extractor.extract_data_features(data)

        for sequence in operation_sequences:
            # Execute the sequence
            result = mock_operation_executor(data, sequence)

            if result['success']:
                # Extract sequence features
                sequence_features = feature_extractor.extract_sequence_features(sequence, data_features)

                # Create training example
                example = TrainingExample(
                    input_data_hash=hash(data),
                    data_features=data_features.__dict__,
                    operation_sequence=sequence,
                    sequence_features=sequence_features,
                    performance_score=result['score'],
                    execution_time=result['execution_time'],
                    memory_usage=0.0,  # Not tracked in mock
                    success=True,
                    timestamp=datetime.now(),
                    metadata=result['metadata']
                )

                training_examples.append(example)

    # Save training examples
    saved_count = 0
    for example in training_examples:
        if data_collector.record_training_example(example):
            saved_count += 1

    logger.info(f"Generated and saved {saved_count} training examples")
    return saved_count


def demo_feature_extraction():
    """Demonstrate feature extraction capabilities."""
    logger.info("=== Feature Extraction Demo ===")

    feature_extractor = FeatureExtractor()

    # Test different data types
    test_cases = [
        ("Text data", b"Hello, World! This is a sample text for testing the BSEE system."),
        ("Binary data", bytes(range(256))),
        ("Random data", bytes([random.randint(0, 255) for _ in range(512)])),
        ("Repetitive data", b"ABCD" * 128),
        ("Empty data", b""),
    ]

    for name, data in test_cases:
        logger.info(f"\nAnalyzing {name} ({len(data)} bytes):")
        features = feature_extractor.extract_data_features(data)

        logger.info(f"  Entropy: {features.entropy:.3f}")
        logger.info(f"  Pattern repetition: {features.pattern_repetition:.3f}")
        logger.info(f"  Compression ratio estimate: {features.compression_ratio_estimate:.3f}")
        logger.info(f"  Data type classification: {features.data_type_score}")


def demo_prediction_without_training():
    """Demonstrate prediction without trained model."""
    logger.info("\n=== Prediction Without Training Demo ===")

    predictor = SequencePredictor()

    test_data = b"Hello, BSEE AI Enhancement!"

    if not predictor.is_model_available():
        logger.info("No trained model available - using fallback predictions")

        # Test sequence prediction
        sequence = [{'type': 'xor', 'parameters': {'key': 42}}]
        score, confidence = predictor.predict_sequence_performance(sequence, test_data)
        logger.info(f"Sequence {sequence}: Score={score:.3f}, Confidence={confidence:.3f}")

        # Test data analysis
        analysis = predictor.analyze_input_data(test_data)
        logger.info(f"Data analysis: {analysis}")


def demo_model_training():
    """Demonstrate model training."""
    logger.info("\n=== Model Training Demo ===")

    # Generate training data
    training_count = generate_sample_training_data()

    if training_count < 50:
        logger.warning("Insufficient training data generated")
        return False

    # Train the model
    trainer = LearningPipeline()

    logger.info("Starting model training...")
    result = trainer.start_learning_cycle(force=True)

    logger.info(f"Training completed in {result.learning_time:.2f}s")
    logger.info(f"Models trained: {result.models_trained}")
    logger.info(f"Training examples: {result.training_examples_count}")
    logger.info(f"Improvement detected: {result.improvement_detected}")

    return result.models_trained.get('sequence_optimizer', False)


def demo_optimization_with_ai():
    """Demonstrate AI-powered optimization."""
    logger.info("\n=== AI-Powered Optimization Demo ===")

    predictor = SequencePredictor()
    optimization_pipeline = OptimizationPipeline(predictor)

    # Test with different data types
    test_cases = [
        ("Text file", b"This is a sample text file that contains readable ASCII characters and words." * 5),
        ("Binary data", bytes([random.randint(0, 255) for _ in range(256)])),
        ("Structured data", b"HEADER: " + b"DATA" * 32 + b"FOOTER"),
        ("Compressed-like", bytes([random.randint(0, 255) for _ in range(512)])),  # High entropy
    ]

    for name, data in test_cases:
        logger.info(f"\nOptimizing {name} ({len(data)} bytes):")

        try:
            result = optimization_pipeline.optimize_and_execute(data, mock_operation_executor)

            logger.info(f"  Best sequence: {result.best_sequence}")
            logger.info(f"  Predicted score: {result.predicted_score:.3f}")
            logger.info(f"  Actual score: {result.actual_score:.3f}")
            logger.info(f"  Confidence: {result.confidence:.3f}")
            logger.info(f"  Optimization time: {result.optimization_time:.3f}s")
            logger.info(f"  Execution time: {result.actual_execution_time:.3f}s")

            if result.alternatives:
                logger.info(f"  Alternatives available: {len(result.alternatives)}")

        except Exception as e:
            logger.error(f"  Optimization failed: {e}")


def demo_batch_optimization():
    """Demonstrate batch optimization."""
    logger.info("\n=== Batch Optimization Demo ===")

    predictor = SequencePredictor()
    optimization_pipeline = OptimizationPipeline(predictor)

    # Generate batch of test data
    batch_data = [
        f"Batch item {i}: ".encode() + bytes([random.randint(0, 255) for _ in range(100)])
        for i in range(5)
    ]

    logger.info(f"Processing batch of {len(batch_data)} items...")

    results = optimization_pipeline.batch_optimize(batch_data, mock_operation_executor)

    # Get statistics
    stats = optimization_pipeline.get_optimization_statistics()
    logger.info(f"Batch optimization statistics:")
    logger.info(f"  Success rate: {stats['success_rate']:.2%}")
    logger.info(f"  Average score: {stats.get('average_actual_score', 'N/A')}")
    logger.info(f"  Average time: {stats['average_optimization_time']:.3f}s")


def demo_learning_pipeline():
    """Demonstrate continuous learning pipeline."""
    logger.info("\n=== Learning Pipeline Demo ===")

    # Add more training data and trigger learning
    generate_sample_training_data()

    learning_pipeline = LearningPipeline(auto_train=True, training_interval_hours=0)  # Immediate training

    # Get status
    status = learning_pipeline.get_learning_status()
    logger.info(f"Learning pipeline status: {status}")

    # Run learning cycle
    result = learning_pipeline.start_learning_cycle(force=True)
    logger.info(f"Learning cycle result: {result}")

    # Get learning history
    history = learning_pipeline.get_learning_history()
    logger.info(f"Learning history: {len(history)} cycles")


def main():
    """Main demo function."""
    logger.info("🚀 BSEE AI/ML Enhancement Demo")
    logger.info("=" * 50)

    try:
        # Demo feature extraction
        demo_feature_extraction()

        # Demo prediction without training
        demo_prediction_without_training()

        # Demo model training
        training_success = demo_model_training()

        if training_success:
            # Demo AI-powered optimization
            demo_optimization_with_ai()

            # Demo batch optimization
            demo_batch_optimization()

            # Demo learning pipeline
            demo_learning_pipeline()

        logger.info("\n✅ Demo completed successfully!")
        logger.info("\nThe BSEE AI/ML Enhancement provides:")
        logger.info("• Automatic feature extraction from binary data")
        logger.info("• ML-based prediction of operation sequence performance")
        logger.info("• Intelligent optimization of operation sequences")
        logger.info("• Continuous learning from execution results")
        logger.info("• Batch processing capabilities")
        logger.info("• Performance monitoring and improvement")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        logger.error("This is expected in a demo environment without full BSEE operations.")


if __name__ == "__main__":
    main()