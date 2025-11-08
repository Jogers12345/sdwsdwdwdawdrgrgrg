"""
Operation Validator for BSEE Transform Operations

This module provides comprehensive validation of transform operations to ensure
they work as claimed and detect inconsistencies or broken implementations.
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

from bsee.operations.transform_ops import TransformOperations


class OperationValidator:
    """Comprehensive operation validation system."""

    def __init__(self, operations_registry: Optional[TransformOperations] = None):
        """Initialize validator with operations registry."""
        self.operations_registry = operations_registry or TransformOperations()
        self.validation_results = {}
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for validation."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def validate_all_operations(self) -> Dict[str, Any]:
        """Test all operations with comprehensive test cases."""
        self.logger.info("Starting comprehensive operation validation...")
        start_time = time.time()

        # Test cases covering various scenarios
        test_cases = [
            b'',                                    # Empty data
            b'\x00',                                # Single byte
            b'Hello World!',                       # ASCII text
            bytes(range(256)),                     # All byte values
            b'\x00' * 1000 + b'\xFF' * 1000,      # Repeated patterns
            os.urandom(1024),                      # Random data
            b'\x00\x01\x02\x03' * 256,             # Small pattern repeated
            b'A' * 5000,                           # Large repeated data
            b'\xFF\xFE\xFD\xFC\xFB\xFA\xF9\xF8',   # Descending sequence
            b'Mixed DATA with 123 numbers!@#',     # Mixed content
        ]

        operations = self.operations_registry.get_operations()

        for operation_name in operations:
            if operation_name not in ['bitplane_extract', 'bitplane_insert']:  # Skip operations requiring params
                self.logger.info(f"Validating operation: {operation_name}")
                self.validation_results[operation_name] = self._validate_operation(
                    operation_name, test_cases
                )

        validation_time = time.time() - start_time
        self.logger.info(f"Validation completed in {validation_time:.2f} seconds")

        return self.validation_results

    def _validate_operation(self, operation_name: str, test_cases: List[bytes]) -> Dict[str, Any]:
        """Validate a single operation against test cases."""
        operation = getattr(self.operations_registry, operation_name)
        metadata = self.operations_registry.get_metadata(operation_name)

        results = {
            'operation': operation_name,
            'valid': True,
            'errors': [],
            'warnings': [],
            'performance': [],
            'reversibility_tests': [],
            'metadata_consistency': True
        }

        for i, test_data in enumerate(test_cases):
            test_name = f"test_case_{i}_{len(test_data)}_bytes"

            try:
                # Test operation execution
                start_time = time.time()
                transformed_data, inverse_func, operation_metadata = operation(test_data)
                execution_time = time.time() - start_time

                results['performance'].append({
                    'test_case': test_name,
                    'execution_time': execution_time,
                    'input_size': len(test_data),
                    'output_size': len(transformed_data),
                    'compression_ratio': len(test_data) / len(transformed_data) if len(transformed_data) > 0 else 1.0
                })

                # Test reversibility if claimed
                if metadata.get('reversible', False):
                    reversibility_result = self._test_reversibility(
                        test_data, transformed_data, inverse_func, test_name
                    )
                    results['reversibility_tests'].append(reversibility_result)

                    if not reversibility_result['passed']:
                        results['valid'] = False
                        results['errors'].append(
                            f"Reversibility test failed for {test_name}: "
                            f"{reversibility_result['error']}"
                        )

                # Validate metadata consistency
                metadata_consistency = self._validate_metadata_consistency(
                    metadata, operation_metadata, test_name
                )
                if not metadata_consistency['consistent']:
                    results['metadata_consistency'] = False
                    results['warnings'].extend(metadata_consistency['issues'])

            except Exception as e:
                results['valid'] = False
                results['errors'].append(f"Exception in {test_name}: {str(e)}")
                self.logger.error(f"Operation {operation_name} failed on {test_name}: {e}")

        return results

    def _test_reversibility(self, original_data: bytes, transformed_data: bytes,
                          inverse_func: callable, test_name: str) -> Dict[str, Any]:
        """Test if inverse function perfectly restores original data."""
        try:
            start_time = time.time()
            restored_data = inverse_func()
            inverse_time = time.time() - start_time

            # Check if restoration is perfect
            if restored_data == original_data:
                return {
                    'passed': True,
                    'test_case': test_name,
                    'inverse_time': inverse_time,
                    'original_size': len(original_data),
                    'restored_size': len(restored_data)
                }
            else:
                # Find differences
                differences = []
                min_len = min(len(original_data), len(restored_data))
                for i in range(min_len):
                    if original_data[i] != restored_data[i]:
                        differences.append(i)

                return {
                    'passed': False,
                    'test_case': test_name,
                    'inverse_time': inverse_time,
                    'error': f"Data mismatch at {len(differences)} positions, first diff at index {differences[0] if differences else 'N/A'}",
                    'differences': differences[:10],  # First 10 differences
                    'original_size': len(original_data),
                    'restored_size': len(restored_data)
                }

        except Exception as e:
            return {
                'passed': False,
                'test_case': test_name,
                'error': f"Inverse function failed: {str(e)}"
            }

    def _validate_metadata_consistency(self, declared_metadata: Dict,
                                      operation_metadata: Dict,
                                      test_name: str) -> Dict[str, Any]:
        """Check if operation metadata matches actual implementation."""
        issues = []

        # Check reversible flag consistency
        declared_reversible = declared_metadata.get('reversible', False)
        if 'reversible' in operation_metadata:
            actual_reversible = operation_metadata['reversible']
            if declared_reversible != actual_reversible:
                issues.append(
                    f"Reversible flag mismatch: declared={declared_reversible}, "
                    f"actual={actual_reversible}"
                )

        # Check operation name consistency
        if operation_metadata.get('operation') != declared_metadata.get('description', '').lower():
            issues.append("Operation name inconsistency in metadata")

        # Check if bytes_affected is reasonable
        if 'bytes_affected' in operation_metadata:
            affected = operation_metadata['bytes_affected']
            if not isinstance(affected, int) or affected < 0:
                issues.append(f"Invalid bytes_affected value: {affected}")

        return {
            'consistent': len(issues) == 0,
            'issues': issues,
            'test_case': test_name
        }

    def validate_specific_operation(self, operation_name: str,
                                  test_data: Optional[bytes] = None) -> Dict[str, Any]:
        """Validate a specific operation with optional custom test data."""
        if not hasattr(self.operations_registry, operation_name):
            return {
                'operation': operation_name,
                'valid': False,
                'errors': [f"Operation {operation_name} not found"]
            }

        # Use provided test data or default test cases
        test_cases = [test_data] if test_data else [
            b'Hello World!',
            bytes(range(256)),
            os.urandom(512)
        ]

        return self._validate_operation(operation_name, test_cases)

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_operations': len(self.validation_results),
            'valid_operations': 0,
            'invalid_operations': 0,
            'warnings': [],
            'errors': [],
            'performance_summary': {},
            'reversibility_summary': {},
            'details': self.validation_results
        }

        # Count valid/invalid operations
        for op_name, results in self.validation_results.items():
            if results.get('valid', False):
                report['valid_operations'] += 1
            else:
                report['invalid_operations'] += 1

            # Collect all errors and warnings
            report['errors'].extend(results.get('errors', []))
            report['warnings'].extend(results.get('warnings', []))

        # Performance summary
        all_performance = []
        for results in self.validation_results.values():
            all_performance.extend(results.get('performance', []))

        if all_performance:
            execution_times = [p['execution_time'] for p in all_performance]
            compression_ratios = [p['compression_ratio'] for p in all_performance]

            report['performance_summary'] = {
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'max_execution_time': max(execution_times),
                'min_execution_time': min(execution_times),
                'avg_compression_ratio': sum(compression_ratios) / len(compression_ratios),
                'best_compression': max(compression_ratios),
                'worst_compression': min(compression_ratios)
            }

        # Reversibility summary
        all_reversibility_tests = []
        for results in self.validation_results.values():
            all_reversibility_tests.extend(results.get('reversibility_tests', []))

        if all_reversibility_tests:
            passed_tests = [r for r in all_reversibility_tests if r.get('passed', False)]
            report['reversibility_summary'] = {
                'total_tests': len(all_reversibility_tests),
                'passed_tests': len(passed_tests),
                'failed_tests': len(all_reversibility_tests) - len(passed_tests),
                'success_rate': len(passed_tests) / len(all_reversibility_tests) * 100
            }

        return report

    def save_validation_report(self, filename: str = None) -> str:
        """Save validation report to file."""
        import json

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bsee_validation_report_{timestamp}.json"

        report = self.generate_validation_report()

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Validation report saved to: {filename}")
        return filename

    def quick_health_check(self) -> Dict[str, Any]:
        """Perform quick health check on all operations."""
        health_results = {}
        test_data = b'Hello World! Test Data 123'

        for operation_name in self.operations_registry.get_operations():
            if operation_name not in ['bitplane_extract', 'bitplane_insert']:
                try:
                    operation = getattr(self.operations_registry, operation_name)
                    transformed_data, inverse_func, _ = operation(test_data)

                    # Test inverse if available
                    if hasattr(inverse_func, '__call__'):
                        try:
                            restored_data = inverse_func()
                            health_results[operation_name] = {
                                'status': 'healthy',
                                'execution_successful': True,
                                'reversibility_successful': restored_data == test_data
                            }
                        except Exception as e:
                            health_results[operation_name] = {
                                'status': 'warning',
                                'execution_successful': True,
                                'reversibility_successful': False,
                                'error': str(e)
                            }
                    else:
                        health_results[operation_name] = {
                            'status': 'warning',
                            'execution_successful': True,
                            'reversibility_successful': False,
                            'note': 'No inverse function available'
                        }

                except Exception as e:
                    health_results[operation_name] = {
                        'status': 'unhealthy',
                        'execution_successful': False,
                        'error': str(e)
                    }

        return health_results


if __name__ == "__main__":
    # Run validation when executed directly
    validator = OperationValidator()

    print("BSEE Operation Validator")
    print("=" * 40)

    # Quick health check
    print("Performing quick health check...")
    health_results = validator.quick_health_check()

    for op_name, result in health_results.items():
        status_symbol = {
            'healthy': '✓',
            'warning': '⚠',
            'unhealthy': '✗'
        }.get(result['status'], '?')
        print(f"{status_symbol} {op_name}: {result['status']}")

    print(f"\nOperations: {len([r for r in health_results.values() if r['status'] == 'healthy'])} healthy, "
          f"{len([r for r in health_results.values() if r['status'] == 'warning'])} warnings, "
          f"{len([r for r in health_results.values() if r['status'] == 'unhealthy'])} unhealthy")

    # Full validation (optional)
    response = input("\nRun full validation? (y/n): ")
    if response.lower() == 'y':
        print("Running full validation...")
        validator.validate_all_operations()

        report = validator.generate_validation_report()
        print(f"\nValidation Results:")
        print(f"Total Operations: {report['total_operations']}")
        print(f"Valid: {report['valid_operations']}")
        print(f"Invalid: {report['invalid_operations']}")
        print(f"Total Errors: {len(report['errors'])}")
        print(f"Total Warnings: {len(report['warnings'])}")

        # Save report
        filename = validator.save_validation_report()
        print(f"Detailed report saved to: {filename}")