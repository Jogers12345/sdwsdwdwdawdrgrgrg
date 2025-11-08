#!/usr/bin/env python3
"""
Comprehensive Test Suite for BSEE Operations and Metrics

This script tests all available operations and metrics in the BSEE system,
providing detailed reports on what works and what dependencies are missing.
"""

import sys
import traceback
from typing import Dict, List, Any, Tuple
import time

# Test data samples
TEST_SAMPLES = {
    'empty': b'',
    'single_byte': b'\x00',
    'text': b'Hello World! Testing BSEE operations.',
    'repeated': b'A' * 100 + b'B' * 50,
    'sequential': bytes(range(256)),
    'random': bytes([i % 256 for i in range(1024)]),
    'mixed': b'\x00\xFF\x01\xFE' * 64,
    'pattern': b'ABCDEF123456' * 20,
    'binary': b'\x00\x01\x02\x03\x04\x05' * 32
}


class BSEETester:
    """Comprehensive tester for BSEE operations and metrics."""

    def __init__(self):
        self.results = {
            'operations': {},
            'metrics': {},
            'errors': [],
            'summary': {}
        }

    def test_operations(self) -> Dict[str, Any]:
        """Test all available operations."""
        print("Testing BSEE Operations")
        print("=" * 60)

        try:
            from bsee.operations.operations_registry import OperationsRegistry
            ops_reg = OperationsRegistry()

            all_operations = ops_reg.list_operations()
            print(f"Found {len(all_operations)} operations")

            # Group operations by category
            categories = ops_reg.get_operation_categories()
            print(f"Categories: {categories}")

            # Test each operation
            for op_name in all_operations:
                print(f"\nTesting: {op_name}")
                op_result = self._test_single_operation(ops_reg, op_name)
                self.results['operations'][op_name] = op_result

            # Calculate summary
            working_ops = sum(1 for r in self.results['operations'].values() if r['status'] == 'working')
            self.results['summary']['operations'] = {
                'total': len(all_operations),
                'working': working_ops,
                'failed': len(all_operations) - working_ops,
                'success_rate': working_ops / len(all_operations) * 100
            }

        except Exception as e:
            print(f"Error loading operations registry: {e}")
            self.results['errors'].append(f"Operations registry: {e}")
            traceback.print_exc()

        return self.results['operations']

    def _test_single_operation(self, ops_reg, op_name: str) -> Dict[str, Any]:
        """Test a single operation."""
        result = {
            'status': 'unknown',
            'error': None,
            'metadata': {},
            'test_results': {},
            'reversible': False
        }

        try:
            # Get metadata
            metadata = ops_reg.get_operation_metadata(op_name)
            result['metadata'] = {
                'category': metadata.get('category', 'unknown'),
                'description': metadata.get('description', 'No description'),
                'reversible': metadata.get('reversible', False),
                'required_params': metadata.get('required_params', []),
                'optional_params': metadata.get('optional_params', {})
            }

            # Get operation function
            operation = ops_reg.get_operation(op_name)

            # Get default parameters for operations that need them
            default_params = self._get_default_parameters(op_name, metadata)

            # Test with various samples
            working_samples = 0
            total_samples = 0

            for sample_name, sample_data in TEST_SAMPLES.items():
                if sample_data == b'':  # Skip empty data for most operations
                    continue

                total_samples += 1
                sample_result = self._test_operation_sample(operation, sample_data, metadata, default_params)
                result['test_results'][sample_name] = sample_result

                if sample_result['status'] == 'success':
                    working_samples += 1
                    if sample_result.get('reversible_test_passed', False):
                        result['reversible'] = True

            # Determine overall status
            if working_samples == total_samples:
                result['status'] = 'working'
            elif working_samples > 0:
                result['status'] = 'partial'
            else:
                result['status'] = 'failed'

            print(f"  Status: {result['status']} ({working_samples}/{total_samples} samples)")
            if result['reversible']:
                print(f"  Reversible: ✓")
            if default_params:
                print(f"  Used params: {default_params}")

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"  Error: {e}")

        return result

    def _get_default_parameters(self, op_name: str, metadata: Dict) -> Dict[str, Any]:
        """Get default parameters for operations that require them."""
        required_params = metadata.get('required_params', [])
        if not required_params:
            return {}

        # Default parameters based on operation name and required parameters
        defaults = {}

        # Bitwise operations
        if 'constant' in required_params:
            defaults['constant'] = 0x55  # Binary 01010101
        elif 'bit_position' in required_params:
            defaults['bit_position'] = 1
        elif 'mask' in required_params:
            defaults['mask'] = 0xF0  # High nibble mask
        elif 'bit1' in required_params and 'bit2' in required_params:
            defaults['bit1'] = 0
            defaults['bit2'] = 7
        elif 'shift' in required_params:
            defaults['shift'] = 1
        elif 'offset' in required_params and 'length' in required_params and 'constant' in required_params:
            defaults['offset'] = 0
            defaults['length'] = 8
            defaults['constant'] = 0xAA

        # Reordering operations
        elif 'block_size' in required_params:
            defaults['block_size'] = 4
        elif 'key' in required_params:
            defaults['key'] = b'\x01\x02\x03\x04'
        elif 'seed' in required_params:
            defaults['seed'] = 42

        # Substitution operations
        elif 'key' in required_params:
            defaults['key'] = 5
        elif 'sbox' in required_params:
            defaults['sbox'] = list(range(256))  # Identity S-box
        elif 'table' in required_params:
            defaults['table'] = list(range(256))  # Identity table

        # Custom operations
        elif 'pattern' in required_params:
            defaults['pattern'] = b'PATTERN'
        elif 'data' in required_params:
            defaults['data'] = b'HIDDEN'

        # Transform operations
        elif 'plane' in required_params:
            defaults['plane'] = 0
        elif 'data' in required_params:
            defaults['data'] = b'\xFF' * 8

        return defaults

    def _test_operation_sample(self, operation, sample_data: bytes, metadata: Dict) -> Dict[str, Any]:
        """Test operation with a single sample."""
        result = {
            'status': 'unknown',
            'error': None,
            'input_size': len(sample_data),
            'output_size': 0,
            'execution_time': 0,
            'reversible_test_passed': False
        }

        try:
            start_time = time.time()

            # Handle operations that require parameters
            required_params = metadata.get('required_params', [])
            if required_params:
                # Skip operations that require parameters for now
                result['status'] = 'skipped'
                result['error'] = f"Requires parameters: {required_params}"
                return result

            # Execute operation
            transformed_data, inverse_func, op_metadata = operation(sample_data)

            execution_time = time.time() - start_time

            result.update({
                'status': 'success',
                'output_size': len(transformed_data),
                'execution_time': execution_time,
                'compression_ratio': len(sample_data) / len(transformed_data) if len(transformed_data) > 0 else 1.0
            })

            # Test reversibility if claimed
            if metadata.get('reversible', False) and hasattr(inverse_func, '__call__'):
                try:
                    restored_data = inverse_func()
                    if restored_data == sample_data:
                        result['reversible_test_passed'] = True
                    else:
                        result['reversible_test_passed'] = False
                        result['reversibility_error'] = 'Data mismatch'
                except Exception as rev_error:
                    result['reversibility_error'] = str(rev_error)

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result

    def test_metrics(self) -> Dict[str, Any]:
        """Test all available metrics."""
        print("\n\nTesting BSEE Metrics")
        print("=" * 60)

        try:
            from bsee.metrics.metrics_registry import MetricsRegistry
            metrics_reg = MetricsRegistry()

            all_metrics = metrics_reg.list_metrics()
            print(f"Found {len(all_metrics)} metrics")

            # Group metrics by category
            categories = metrics_reg.get_metric_categories()
            print(f"Categories: {categories}")

            # Test each metric
            for metric_name in all_metrics:
                print(f"\nTesting: {metric_name}")
                metric_result = self._test_single_metric(metrics_reg, metric_name)
                self.results['metrics'][metric_name] = metric_result

            # Calculate summary
            working_metrics = sum(1 for r in self.results['metrics'].values() if r['status'] == 'working')
            self.results['summary']['metrics'] = {
                'total': len(all_metrics),
                'working': working_metrics,
                'failed': len(all_metrics) - working_metrics,
                'success_rate': working_metrics / len(all_metrics) * 100
            }

        except Exception as e:
            print(f"Error loading metrics registry: {e}")
            self.results['errors'].append(f"Metrics registry: {e}")
            traceback.print_exc()

        return self.results['metrics']

    def _test_single_metric(self, metrics_reg, metric_name: str) -> Dict[str, Any]:
        """Test a single metric."""
        result = {
            'status': 'unknown',
            'error': None,
            'metadata': {},
            'test_results': {}
        }

        try:
            # Get metadata
            metadata = metrics_reg.get_metric_metadata(metric_name)
            result['metadata'] = {
                'category': metadata.get('category', 'unknown'),
                'description': metadata.get('description', 'No description')
            }

            # Get metric function
            metric_func = metrics_reg.metrics[metric_name]

            # Test with various samples
            working_samples = 0
            total_samples = 0

            for sample_name, sample_data in TEST_SAMPLES.items():
                if sample_data == b'':  # Skip empty data for most metrics
                    continue

                total_samples += 1
                sample_result = self._test_metric_sample(metric_func, sample_data)
                result['test_results'][sample_name] = sample_result

                if sample_result['status'] == 'success':
                    working_samples += 1

            # Determine overall status
            if working_samples == total_samples:
                result['status'] = 'working'
            elif working_samples > 0:
                result['status'] = 'partial'
            else:
                result['status'] = 'failed'

            print(f"  Status: {result['status']} ({working_samples}/{total_samples} samples)")

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"  Error: {e}")

        return result

    def _test_metric_sample(self, metric_func, sample_data: bytes) -> Dict[str, Any]:
        """Test metric with a single sample."""
        result = {
            'status': 'unknown',
            'error': None,
            'value': None,
            'execution_time': 0
        }

        try:
            start_time = time.time()
            value = metric_func(sample_data)
            execution_time = time.time() - start_time

            result.update({
                'status': 'success',
                'value': value,
                'execution_time': execution_time
            })

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result

    def generate_report(self) -> str:
        """Generate comprehensive report."""
        report = []
        report.append("BSEE Functionality Test Report")
        report.append("=" * 60)
        report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Operations summary
        if 'operations' in self.results['summary']:
            ops_summary = self.results['summary']['operations']
            report.append("OPERATIONS SUMMARY")
            report.append("-" * 30)
            report.append(f"Total Operations: {ops_summary['total']}")
            report.append(f"Working: {ops_summary['working']}")
            report.append(f"Failed: {ops_summary['failed']}")
            report.append(f"Success Rate: {ops_summary['success_rate']:.1f}%")
            report.append("")

        # Metrics summary
        if 'metrics' in self.results['summary']:
            metrics_summary = self.results['summary']['metrics']
            report.append("METRICS SUMMARY")
            report.append("-" * 30)
            report.append(f"Total Metrics: {metrics_summary['total']}")
            report.append(f"Working: {metrics_summary['working']}")
            report.append(f"Failed: {metrics_summary['failed']}")
            report.append(f"Success Rate: {metrics_summary['success_rate']:.1f}%")
            report.append("")

        # Working operations by category
        if self.results['operations']:
            report.append("WORKING OPERATIONS BY CATEGORY")
            report.append("-" * 40)

            categories = {}
            for op_name, op_result in self.results['operations'].items():
                if op_result['status'] == 'working':
                    category = op_result['metadata'].get('category', 'unknown')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(op_name)

            for category, ops in sorted(categories.items()):
                report.append(f"\n{category.upper()} ({len(ops)} operations):")
                for op in sorted(ops):
                    reversible = "✓" if op_result['reversible'] else ""
                    report.append(f"  - {op} {reversible}")

        # Working metrics by category
        if self.results['metrics']:
            report.append("\n\nWORKING METRICS BY CATEGORY")
            report.append("-" * 40)

            categories = {}
            for metric_name, metric_result in self.results['metrics'].items():
                if metric_result['status'] == 'working':
                    category = metric_result['metadata'].get('category', 'unknown')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(metric_name)

            for category, metrics in sorted(categories.items()):
                report.append(f"\n{category.upper()} ({len(metrics)} metrics):")
                for metric in sorted(metrics):
                    report.append(f"  - {metric}")

        # Errors
        if self.results['errors']:
            report.append("\n\nERRORS")
            report.append("-" * 30)
            for error in self.results['errors']:
                report.append(f"• {error}")

        return "\n".join(report)

    def save_report(self, filename: str = None) -> str:
        """Save report to file."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"bsee_test_report_{timestamp}.txt"

        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)

        print(f"\nReport saved to: {filename}")
        return filename


def main():
    """Main test runner."""
    print("BSEE Comprehensive Functionality Test")
    print("=" * 60)
    print("This will test all operations and metrics in the BSEE system.")
    print("")

    tester = BSEETester()

    # Test operations
    tester.test_operations()

    # Test metrics
    tester.test_metrics()

    # Generate and save report
    report_file = tester.save_report()
    print(tester.generate_report())


if __name__ == "__main__":
    main()