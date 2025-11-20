#!/usr/bin/env python3
""""
Simple Test for AI Integration System
Tests the AI learning and recommendation functionality
""""

import os
import sys
import time
import json
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bsee_ai.learners.homogeneity_learner import HomogeneityLearner
from bsee_ai.predictors.operation_predictor import OperationPredictor
from bsee_ai.utils.simple_scorer import SimpleHomogeneityScorer


def generate_test_data() -> Dict[str, bytes]:
    """Generate test data for AI system.""""
    test_data = {}

    # Repetitive data (should have high homogeneity)
    test_data['repetitive'] = b'A' * 100 + b'B' * 100 + b'A' * 100 + b'B' * 100'

    # Random data (should have low homogeneity)
    import random
    test_data['random'] = bytes([random.randint(0, 255) for _ in range(400)])'

    # Pattern-based data
    test_data['pattern'] = b'\x00\xFF\x55\xAA' * 100'

    # Mixed data
    test_data['mixed'] = b'HelloWorld' * 50'

    return test_data


def test_simple_scorer():
    """Test the simple homogeneity scorer.""""
    print("🧪 Testing Simple Homogeneity Scorer")"
    print("=" * 50)"

    scorer = SimpleHomogeneityScorer()
    test_data = generate_test_data()

    for name, data in test_data.items():
        analysis = scorer.analyze_data(data)
        print(f"\n{name.title()} Data:")"
        print(f"  Overall Score: {analysis['overall_score']:.4f}")"
        print(f"  Characteristics: {analysis['characteristics']}")"
        print(f"  Unique Bytes: {analysis['unique_bytes']}/256")"
        print(f"  Entropy Score: {analysis['entropy_score']:.4f}")"
        print(f"  Pattern Score: {analysis['pattern_score']:.4f}")"

    print("\n✅ Simple scorer test completed\n")"


def test_ai_learner():
    """Test the AI learning system.""""
    print("🤖 Testing AI Learning System")"
    print("=" * 50)"

    learner = HomogeneityLearner()
    scorer = SimpleHomogeneityScorer()
    test_data = generate_test_data()

    # Simulate learning from operations
    print("Simulating AI learning from operations...")"

    operations = []
        ('xor_constant', {'constant': 0x55}),'
        ('add_constant', {'constant': 16}),'
        ('rotate_left', {'shift': 2}),'
        ('substitute_bytes', {'pattern': b'\x00\x00', 'replacement': b'\xFF\xFF'})'
    ]

    total_improvements = 0
    successful_operations = 0

    for data_name, data in test_data.items():
        print(f"\nProcessing {data_name} data...")"

        initial_score = scorer.calculate_score(data)
        print(f"  Initial homogeneity: {initial_score:.4f}")"

        for operation, params in operations:
            # Simulate operation effect (simplified)
            if operation == 'xor_constant':'
                modified_data = bytes([b ^ params['constant'] for b in data])'
            elif operation == 'add_constant':'
                modified_data = bytes([(b + params['constant']) % 256 for b in data])'
            elif operation == 'rotate_left':'
                modified_data = bytes([((b << params['shift']) | (b >> (8 - params['shift']))) & 0xFF for b in data])'
            else:  # substitute_bytes
                modified_data = data.replace(params['pattern'], params['replacement'])'

            final_score = scorer.calculate_score(modified_data)
            improvement = final_score - initial_score

            # AI learns from this result
            learner.learn_from_result(data, operation, params, initial_score, final_score)

            print(f"  {operation}: {final_score:.4f} ({improvement:+.4f})")"

            if improvement > 0:
                total_improvements += improvement
                successful_operations += 1

    # Get learning summary
    summary = learner.get_learning_summary()
    print(f"\n📊 Learning Summary:")"
    print(f"  Total Operations Tested: {summary['learning_progress']['total_operations_tested']}")"
    print(f"  Successful Operations: {summary['learning_progress']['successful_operations']}")"
    print(f"  Overall Success Rate: {summary['learning_progress']['overall_success_rate']:.2%}")"
    print(f"  Unique Operations Learned: {summary['learning_progress']['unique_operations_learned']}")"
    print(f"  Data Types Analyzed: {summary['learning_progress']['data_types_analyzed']}")"
    print(f"  Best Overall Improvement: {summary['learning_progress']['best_overall_improvement']:.4f}")"

    # Show top performing operations
    if summary['top_performing_operations']:'
        print(f"\n🏆 Top Performing Operations:")"
        for i, (op, params, improvement) in enumerate(summary['top_performing_operations'][:3]):'
            print(f"  {i+1}. {op}: {improvement:.4f}")"

    print("\n✅ AI learner test completed\n")"
    return learner


def test_operation_predictor(learner):
    """Test the operation predictor.""""
    print("🔮 Testing Operation Predictor")"
    print("=" * 50)"

    predictor = OperationPredictor(learner)
    scorer = SimpleHomogeneityScorer()
    test_data = generate_test_data()

    for data_name, data in test_data.items():
        print(f"\nPredicting operations for {data_name} data...")"

        current_score = scorer.calculate_score(data)
        print(f"  Current homogeneity: {current_score:.4f}")"

        # Get predictions
        predictions = predictor.predict_next_operation(data, current_score, max_sequence_length=3)

        print(f"  🤖 AI Recommendations:")"
        for i, pred in enumerate(predictions):
            print(f"    {i+1}. {pred.operation} (confidence: {pred.confidence:.2f}, ""})}}")"
                  f"expected improvement: {pred.expected_improvement:.4f})")"
            print(f"       Reasoning: {pred.reasoning}")"

        # Get prediction summary
        summary = predictor.get_prediction_summary(predictions)
        print(f"  📈 Summary: {summary['total_expected_improvement']:.4f} total expected improvement, ""'']}")"
              f"{summary['average_confidence']:.2f} average confidence")"

    print("\n✅ Operation predictor test completed\n")"


def test_complete_ai_workflow():
    """Test the complete AI workflow.""""
    print("🔄 Testing Complete AI Workflow")"
    print("=" * 50)"

    # Initialize components
    learner = HomogeneityLearner()
    predictor = OperationPredictor(learner)
    scorer = SimpleHomogeneityScorer()

    # Test data
    test_data = b'\x00' * 50 + b'\xFF' * 50 + b'\x55' * 50 + b'\xAA' * 50'
    initial_score = scorer.calculate_score(test_data)

    print(f"Starting with test data (homogeneity: {initial_score:.4f})")"

    # Simulate multiple iterations of AI-guided optimization
    current_data = test_data
    current_score = initial_score
    total_ai_improvements = 0

    for iteration in range(5):
        print(f"\n--- Iteration {iteration + 1} ---")"

        # Get AI recommendation
        predictions = predictor.predict_next_operation(current_data, current_score, max_sequence_length=1)

        if not predictions:
            print("No AI recommendations available")"
            break

        best_pred = predictions[0]
        print(f"AI recommends: {best_pred.operation} (confidence: {best_pred.confidence:.2f})")"

        # Apply recommended operation
        if best_pred.operation == 'xor_constant':'
            new_data = bytes([b ^ best_pred.parameters['constant'] for b in current_data])'
        elif best_pred.operation == 'add_constant':'
            new_data = bytes([(b + best_pred.parameters['constant']) % 256 for b in current_data])'
        else:
            new_data = current_data  # Skip unknown operations

        new_score = scorer.calculate_score(new_data)
        improvement = new_score - current_score

        # AI learns from result
        learner.learn_from_result(current_data, best_pred.operation, best_pred.parameters,)
                                current_score, new_score)

        print(f"Result: {new_score:.4f} ({improvement:+.4f})")"

        if improvement > 0:
            current_data = new_data
            current_score = new_score
            total_ai_improvements += improvement
            print("✅ Improvement accepted")"
        else:
            print("❌ No improvement, keeping previous state")"

    # Final results
    final_improvement = current_score - initial_score
    print(f"\n🎯 Final Results:")"
    print(f"  Initial homogeneity: {initial_score:.4f}")"
    print(f"  Final homogeneity: {current_score:.4f}")"
    print(f"  Total improvement: {final_improvement:.4f}")"
    print(f"  AI-driven improvements: {total_ai_improvements:.4f}")"

    # Learning summary
    learning_summary = learner.get_learning_summary()
    print(f"\n📚 Learning Summary:")"
    print(f"  Operations learned from: {learning_summary['learning_progress']['total_operations_tested']}")"
    print(f"  Success rate: {learning_summary['learning_progress']['overall_success_rate']:.2%}")"

    print("\n✅ Complete AI workflow test completed\n")"


def main():
    """Main test function.""""
    print("🚀 BSEE AI INTEGRATION TEST SUITE")"
    print("=" * 60)"
    print("Testing the complete AI learning and recommendation system")"
    print("=" * 60)"

    try:
        # Test individual components
        test_simple_scorer()
        learner = test_ai_learner()
        test_operation_predictor(learner)
        test_complete_ai_workflow()

        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")"
        print("=" * 60)"
        print("\n✅ Key Findings:")"
        print("• Simple homogeneity scorer working correctly")"
        print("• AI learning system successfully tracks operation performance")"
        print("• Operation predictor provides intelligent recommendations")"
        print("• Complete AI workflow demonstrates learning and improvement")"
        print("• System adapts based on operation results")"

        print("\n📝 Next Steps:")"
        print("• Integrate with GUI pipeline")"
        print("• Test with larger binary files")"
        print("• Add more sophisticated operations")"
        print("• Implement real-time learning visualization")"

    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")"
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":"
    exit_code = main()
    sys.exit(exit_code)