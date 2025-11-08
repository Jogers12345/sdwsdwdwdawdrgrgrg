"""
Operation Performance Tests
Test operation speed, memory usage, and scalability under various loads
"""

import pytest
import time
import statistics
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

from tests.conftest import TestDataGenerator, performance_test_config


@dataclass
class OperationPerformanceResult:
    """Result of operation performance testing"""
    operation_name: str
    test_type: str
    data_size_bytes: int
    iterations: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    std_deviation: float
    memory_usage_mb: float
    throughput_mb_per_second: float
    operations_per_second: float
    threads_used: int
    success_rate: float
    error_count: int


class OperationPerformanceTester:
    """Comprehensive operation performance testing system"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or performance_test_config()
        self.results = []

    def create_mock_operations(self):
        """Create mock operations for testing"""
        class MockOperation:
            def __init__(self, name: str, work_complexity: float = 1.0):
                self.name = name
                self.work_complexity = work_complexity

            def apply(self, data: bytes) -> bytes:
                # Simulate work based on data size and complexity
                work_units = len(data) * self.work_complexity
                # Simulate processing with sleep
                import time
                time.sleep(work_units / 100000)  # Scale to reasonable time
                # Simple transformation to ensure work is done
                return data[::-1] + data[:len(data)//2]

            def __repr__(self):
                return f"MockOperation({self.name})"

        return {
            "xor": MockOperation("xor", 1.0),
            "add_constant": MockOperation("add_constant", 1.0),
            "rotate": MockOperation("rotate", 1.5),
            "substitute": MockOperation("substitute", 2.0),
            "compress": MockOperation("compress", 5.0),
            "encrypt": MockOperation("encrypt", 10.0)
        }

    def test_operation_performance(self, operation, test_data: bytes,
                                iterations: int = 10) -> OperationPerformanceResult:
        """Test performance of a single operation"""
        print(f"  Testing {operation.name} ({len(test_data)} bytes, {iterations} iterations)")

        execution_times = []
        memory_samples = []
        errors = 0

        for iteration in range(iterations):
            # Track memory before operation
            start_memory = self._get_memory_usage()

            try:
                start_time = time.time()
                result = operation.apply(test_data)
                end_time = time.time()

                execution_time = end_time - start_time
                execution_times.append(execution_time)

                # Verify result
                if not isinstance(result, bytes):
                    raise ValueError(f"Operation did not return bytes: {type(result)}")

                # Track memory after operation
                end_memory = self._get_memory_usage()
                memory_samples.append(end_memory - start_memory)

            except Exception as e:
                errors += 1
                execution_times.append(float('inf'))  # Mark as failed
                print(f"    Error in iteration {iteration + 1}: {e}")

        # Calculate statistics
        valid_times = [t for t in execution_times if t != float('inf')]
        if valid_times:
            avg_time = statistics.mean(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
            std_dev = statistics.stdev(valid_times) if len(valid_times) > 1 else 0.0
            total_time = sum(valid_times)
        else:
            avg_time = min_time = max_time = std_dev = total_time = 0.0

        memory_usage_mb = statistics.mean(memory_samples) if memory_samples else 0.0
        success_rate = (iterations - errors) / iterations
        data_size_mb = len(test_data) / (1024 * 1024)

        return OperationPerformanceResult(
            operation_name=operation.name,
            test_type="single_threaded",
            data_size_bytes=len(test_data),
            iterations=iterations,
            total_time=total_time,
            average_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_deviation=std_dev,
            memory_usage_mb=memory_usage_mb,
            throughput_mb_per_second=data_size_mb / avg_time if avg_time > 0 else 0.0,
            operations_per_second=iterations / total_time if total_time > 0 else 0.0,
            threads_used=1,
            success_rate=success_rate,
            error_count=errors
        )

    def test_parallel_operation_performance(self, operation, test_data: bytes,
                                         thread_count: int = 4,
                                         iterations_per_thread: int = 5) -> OperationPerformanceResult:
        """Test operation performance with multiple threads"""
        print(f"  Testing {operation.name} with {thread_count} threads ({len(test_data)} bytes)")

        def worker_thread(thread_id: int):
            """Worker thread for parallel testing"""
            thread_execution_times = []
            thread_errors = 0

            for iteration in range(iterations_per_thread):
                start_memory = self._get_memory_usage()

                try:
                    start_time = time.time()
                    result = operation.apply(test_data)
                    end_time = time.time()

                    execution_time = end_time - start_time
                    thread_execution_times.append(execution_time)

                    if not isinstance(result, bytes):
                        thread_errors += 1
                        thread_execution_times.append(float('inf'))

                except Exception as e:
                    thread_errors += 1
                    thread_execution_times.append(float('inf'))
                    print(f"    Thread {thread_id} error: {e}")

            return {
                "thread_id": thread_id,
                "execution_times": thread_execution_times,
                "errors": thread_errors,
                "iterations": iterations_per_thread
            }

        # Execute threads
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [
                executor.submit(worker_thread, i)
                for i in range(thread_count)
            ]

            # Collect results
            thread_results = []
            for future in futures:
                try:
                    thread_results.append(future.result())
                except Exception as e:
                    print(f"    Thread failed: {e}")
                    thread_results.append({
                        "thread_id": -1,
                        "execution_times": [float('inf')],
                        "errors": 1,
                        "iterations": 0
                    })

        end_time = time.time()

        # Combine results
        all_execution_times = []
        total_errors = 0
        total_iterations = 0

        for result in thread_results:
            all_execution_times.extend(result["execution_times"])
            total_errors += result["errors"]
            total_iterations += result["iterations"]

        # Calculate statistics
        valid_times = [t for t in all_execution_times if t != float('inf')]
        if valid_times:
            avg_time = statistics.mean(valid_times)
            total_time = sum(valid_times)
        else:
            avg_time = total_time = 0.0

        memory_usage_mb = self._get_memory_usage()  # Current total memory usage
        success_rate = (total_iterations - total_errors) / total_iterations if total_iterations > 0 else 0.0
        data_size_mb = len(test_data) / (1024 * 1024)

        return OperationPerformanceResult(
            operation_name=operation.name,
            test_type=f"parallel_{thread_count}_threads",
            data_size_bytes=len(test_data),
            iterations=total_iterations,
            total_time=total_time,
            average_time=avg_time,
            min_time=min(valid_times) if valid_times else 0.0,
            max_time=max(valid_times) if valid_times else 0.0,
            std_deviation=statistics.stdev(valid_times) if len(valid_times) > 1 else 0.0,
            memory_usage_mb=memory_usage_mb,
            throughput_mb_per_second=data_size_mb * total_iterations / end_time - start_time if end_time > start_time else 0.0,
            operations_per_second=total_iterations / (end_time - start_time) if end_time > start_time else 0.0,
            threads_used=thread_count,
            success_rate=success_rate,
            error_count=total_errors
        )

    def test_operation_scalability(self, operation, data_sizes: List[int],
                                   iterations: int = 5) -> Dict[str, OperationPerformanceResult]:
        """Test operation scalability across different data sizes"""
        print(f"  Testing {operation.name} scalability across {len(data_sizes)} data sizes")

        results = {}

        for size in data_sizes:
            test_data = TestDataGenerator.generate_random_data(size, seed=size)
            result = self.test_operation_performance(
                operation, test_data, iterations=iterations
            )
            results[f"size_{size}"] = result

            # Check if performance degrades significantly
            if size > data_sizes[0]:  # Compare with first (smallest) size
                base_result = results[f"size_{data_sizes[0]}"]
                size_ratio = size / data_sizes[0]
                time_ratio = result.average_time / base_result.average_time if base_result.average_time > 0 else 1.0

                # Performance should be at least somewhat scalable (not O(n²))
                if size_ratio > 100 and time_ratio > size_ratio ** 1.5:
                    print(f"    WARNING: Poor scalability detected for size {size}")

        return results

    def test_memory_usage(self, operation, max_memory_mb: float = 256.0) -> Dict[str, Any]:
        """Test operation memory usage and limits"""
        print(f"  Testing {operation.name} memory usage (limit: {max_memory_mb} MB)")

        # Test with increasing data sizes
        data_sizes = [1024, 4096, 16384, 65536, 262144, 1048576]  # 1KB to 1MB
        results = []

        for size in data_sizes:
            test_data = TestDataGenerator.generate_random_data(size, seed=size)

            # Monitor memory before test
            baseline_memory = self._get_memory_usage()

            try:
                start_memory = self._get_memory_usage()
                result = operation.apply(test_data)
                end_memory = self._get_memory_usage()

                memory_overhead = end_memory - start_memory
                memory_per_byte = memory_overhead / size if size > 0 else 0

                # Check if within limits
                is_within_limit = memory_overhead <= max_memory_mb

                results.append({
                    "data_size": size,
                    "memory_overhead_mb": memory_overhead,
                    "memory_per_byte": memory_per_byte,
                    "within_limit": is_within_limit,
                    "result_size": len(result)
                })

                if not is_within_limit:
                    print(f"    WARNING: Memory usage ({memory_overhead:.2f} MB) exceeds limit ({max_memory_mb} MB)")

            except Exception as e:
                print(f"    ERROR: Memory test at size {size} failed: {e}")
                results.append({
                    "data_size": size,
                    "memory_overhead_mb": 0.0,
                    "memory_per_byte": 0.0,
                    "within_limit": False,
                    "result_size": 0,
                    "error": str(e)
                })

        # Calculate memory efficiency metrics
        if results:
            avg_memory_per_byte = statistics.mean(
                r["memory_per_byte"] for r in results if r["memory_per_byte"] > 0
            )
            max_memory_per_byte = max(
                r["memory_per_byte"] for r in results if r["memory_per_byte"] > 0
            )
            min_memory_per_byte = min(
                r["memory_per_byte"] for r in results if r["memory_per_byte"] > 0
            )

            # Check if memory usage is efficient
            is_efficient = avg_memory_per_byte < 0.001  # Less than 1KB per MB

            return {
                "results": results,
                "efficiency_metrics": {
                    "average_bytes_per_mb": 1.0 / avg_memory_per_byte if avg_memory_per_byte > 0 else 0,
                    "max_bytes_per_mb": 1.0 / min_memory_per_byte if min_memory_per_byte > 0 else 0,
                    "min_bytes_per_mb": 1.0 / max_memory_per_byte if max_memory_per_byte > 0 else 0
                },
                "is_efficient": is_efficient
            }

        return {
            "results": [],
            "efficiency_metrics": {},
            "is_efficient": False
        }

    def test_error_handling(self, operation, invalid_inputs: List[bytes],
                                  expected_error_type: type = Exception) -> Dict[str, Any]:
        """Test operation error handling"""
        print(f"  Testing {operation.name} error handling")

        error_results = []

        for i, invalid_input in enumerate(invalid_inputs):
            try:
                start_time = time.time()
                result = operation.apply(invalid_input)
                end_time = time.time()

                # Operation should have raised an error
                error_results.append({
                    "input_index": i,
                    "error_raised": False,
                    "execution_time": end_time - start_time,
                    "result_type": type(result),
                    "result_size": len(result) if isinstance(result, bytes) else 0
                })

                print(f"    WARNING: Expected error not raised for input {i}")

            except expected_error_type as e:
                error_results.append({
                    "input_index": i,
                    "error_raised": True,
                    "error_type": type(e),
                    "error_message": str(e),
                    "execution_time": 0.0  # Error handling should be fast
                })

            except Exception as e:
                # Different error type than expected
                error_results.append({
                    "input_index": i,
                    "error_raised": True,
                    "error_type": type(e),
                    "error_message": str(e),
                    "unexpected_error_type": True,
                    "expected_type": expected_error_type.__name__
                })

        # Analyze error handling performance
        total_inputs = len(invalid_inputs)
        errors_raised = sum(1 for r in error_results if r["error_raised"])
        correct_error_type = sum(1 for r in error_results if r.get("error_raised") and not r.get("unexpected_error_type", False))
        incorrect_error_type = sum(1 for r in error_results if r.get("unexpected_error_type", False))

        return {
            "total_inputs_tested": total_inputs,
            "errors_raised": errors_raised,
            "correct_error_type": correct_error_type,
            "incorrect_error_type": incorrect_error_type,
            "error_handling_rate": errors_raised / total_inputs if total_inputs > 0 else 0,
            "error_type_accuracy": correct_error_type / errors_raised if errors_raised > 0 else 0,
            "results": error_results
        }

    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report_lines = [
            "=" * 70,
            "Operation Performance Test Report",
            "=" * 70,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # Determine report type based on results structure
        if "average_time" in results:
            # Single operation result
            self._format_single_operation_report(report_lines, results)
        elif "results" in results:
            # Scalability results
            self._format_scalability_report(report_lines, results)
        elif "efficiency_metrics" in results:
            # Memory results
            self._format_memory_report(report_lines, results)
        elif "total_inputs_tested" in results:
            # Error handling results
            self._format_error_handling_report(report_lines, results)
        else:
            # Complex results
            self._format_complex_report(report_lines, results)

        return "\n".join(report_lines)

    def _format_single_operation_report(self, lines: List[str], result: OperationPerformanceResult):
        """Format report for single operation"""
        lines.extend([
            f"Operation: {result.operation_name}",
            f"Test Type: {result.test_type}",
            f"Data Size: {result.data_size_bytes:,} bytes ({result.data_size_bytes/1024:.1f} KB)",
            f"Iterations: {result.iterations}",
            "",
            "Performance Metrics:",
            f"  Average Time: {result.average_time:.6f} seconds",
            f"  Min Time: {result.min_time:.6f} seconds",
            f"  Max Time: {result.max_time:.6f} seconds",
            f"  Std Deviation: {result.std_deviation:.6f} seconds",
            f"  Memory Usage: {result.memory_usage_mb:.2f} MB",
            f"  Throughput: {result.throughput_mb_per_second:.2f} MB/s",
            f"  Operations/sec: {result.operations_per_second:.0f}",
            "",
            "Quality Metrics:",
            f"  Success Rate: {result.success_rate*100:.1f}%",
            f"  Error Count: {result.error_count}",
            f"  Threads Used: {result.threads_used}",
            ""
        ])

        # Performance assessment
        ops_per_sec_mb = result.operations_per_second / (result.data_size_bytes / (1024 * 1024)) if result.data_size_bytes > 0 else 0

        lines.extend([
            "Performance Assessment:",
            f"  Operations/Second/MB: {ops_per_sec_mb:,.0f}",
        ])

        if result.success_rate < 0.9:
            lines.append("  ⚠️  Low success rate detected")
        if result.std_deviation > result.average_time * 0.2:
            lines.append("  ⚠️  High execution time variance")
        if result.memory_usage_mb > 100:
            lines.append("  ⚠️  High memory usage")
        else:
            lines.append("  ✅  Performance looks good")

    def _format_scalability_report(self, lines: List[str], results: Dict[str, OperationPerformanceResult]):
        """Format report for scalability tests"""
        lines.extend([
            "Scalability Test Results",
            "",
            "Performance by Data Size:",
            "-" * 50
        ])

        # Create comparison table
        header = f"{'Size':12s} {'Avg Time':12s} {'Ops/Sec':12s} {'Memory':12s} {'Success':8s}}"
        lines.append(header)
        lines.append("-" * len(header))

        for size_key in sorted(results.keys()):
            result = results[size_key]
            size = int(size_key.split('_')[1])
            lines.append(
                f"{size:9d}B {result.average_time:12.6f}s "
                f"{result.operations_per_second:12.0f} "
                f"{result.memory_usage_mb:12.2f}MB "
                f"{result.success_rate*100:6.1f}%"
            )

        # Calculate scaling efficiency
        sizes = sorted([int(key.split('_')[1]) for key in results.keys()])
        if len(sizes) > 1:
            smallest_size = sizes[0]
            largest_size = sizes[-1]
            size_ratio = largest_size / smallest_size

            if f"size_{smallest_size}" in results and f"size_{largest_size}" in results:
                small_result = results[f"size_{smallest_size}"]
                large_result = results[f"size_{largest_size}"]
                time_ratio = large_result.average_time / small_result.average_time if small_result.average_time > 0 else 0

                lines.extend([
                    "",
                    "Scaling Analysis:",
                    f"  Size Ratio: {size_ratio}x",
                    f"  Time Ratio: {time_ratio:.2f}x (larger/smaller)",
                ])

                # Check scaling efficiency
                if time_ratio > size_ratio * 1.5:
                    lines.append("  ⚠️  Poor scaling detected (time grows faster than data)")
                elif time_ratio > size_ratio:
                    lines.append("  ⚠️  Sub-linear scaling detected")
                else:
                    lines.append("  ✅  Good linear or better scaling")

    def _format_memory_report(self, lines: List[str], results: Dict[str, Any]):
        """Format report for memory tests"""
        lines.extend([
            "Memory Usage Test Results",
            "",
            "Memory Usage by Data Size:",
            "-" * 40
        ])

        for result in results["results"]:
            lines.append(
                f"  {result['data_size']:9d}B: {result['memory_overhead_mb']:8.2f} MB "
                f"({result['memory_per_byte']:.3f} bytes/byte)"
            )

        if "efficiency_metrics" in results:
            metrics = results["efficiency_metrics"]
            lines.extend([
                "",
                "Memory Efficiency Metrics:",
                f"  Average: {metrics['average_bytes_per_mb']:,.0f} bytes/MB",
                f"  Maximum: {metrics['max_bytes_per_mb']:,.0f} bytes/MB",
                f"  Minimum: {metrics['min_bytes_per_mb']:,.0f} bytes/MB",
                "",
            ])

            if results["is_efficient"]:
                lines.append("  ✅  Memory usage is efficient")
            else:
                lines.append("  ⚠️  Memory usage could be improved")

    def _format_error_handling_report(self, lines: List[str], results: Dict[str, Any]):
        """Format report for error handling tests"""
        lines.extend([
            "Error Handling Test Results",
            f"Expected Error Type: {results['total_inputs_tested']} inputs tested",
            "",
            "Summary:",
            f"  Errors Raised: {results['errors_raised']}/{results['total_inputs_tested']} "
            f"({results['error_handling_rate']*100:.1f}%)",
            f"  Correct Error Type: {results['correct_error_type']}/{results['errors_raised']} "
            f"({results['error_type_accuracy']*100:.1f}%)",
            f"  Incorrect Error Type: {results['incorrect_error_type']}",
            "",
        ])

        if results["error_handling_rate"] > 0.9:
            lines.append("  ✅  Good error handling (most inputs properly trigger errors)")
        elif results["error_handling_rate"] > 0.5:
            lines.append("  ⚠️  Moderate error handling")
        else:
            lines.append("  ❌  Poor error handling")

        if results["error_type_accuracy"] < 0.8:
            lines.append("  ⚠️  Wrong error types being raised")

    def _format_complex_report(self, lines: List[str], results: Dict[str, Any]):
        """Format complex benchmark results"""
        lines.append("Complex Benchmark Results:")
        for key, value in results.items():
            lines.append(f"{key}: {value}")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0

    def save_results(self, output_path: str, format: str = "json"):
        """Save benchmark results to file"""
        if format.lower() == "json":
            # Convert results to JSON-serializable format
            json_results = {}
            for key, value in self.results.items():
                if isinstance(value, OperationPerformanceResult):
                    json_results[key] = value.__dict__
                else:
                    json_results[key] = str(value)

            import json
            with open(output_path, 'w') as f:
                json.dump(json_results, f, indent=2, default=str)
        elif format.lower() == "csv":
            # Export as CSV
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            if self.results:
                first_result = list(self.results.values())[0]
                header = [
                    "Operation", "Test Type", "Data Size", "Iterations",
                    "Total Time", "Average Time", "Min Time", "Max Time",
                    "Std Deviation", "Memory MB", "Throughput MB/s", "Ops/Second",
                    "Threads", "Success Rate", "Error Count"
                ]
                writer.writerow(header)

                # Write data
                for result in self.results.values():
                    writer.writerow([
                        result.operation_name,
                        result.test_type,
                        result.data_size_bytes,
                        result.iterations,
                        result.total_time,
                        result.average_time,
                        result.min_time,
                        result.max_time,
                        result.std_deviation,
                        result.memory_usage_mb,
                        result.throughput_mb_per_second,
                        result.operations_per_second,
                        result.threads_used,
                        result.success_rate,
                        result.error_count
                    ])

            with open(output_path, 'w') as f:
                f.write(output.getvalue())

        print(f"Performance test results exported to: {output_path}")

    def add_result(self, result: OperationPerformanceResult):
        """Add a test result"""
        self.results.append(result)

    def clear_results(self):
        """Clear all test results"""
        self.results.clear()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all performance tests"""
        if not self.results:
            return {"message": "No test results available"}

        # Calculate summary statistics
        total_tests = len(self.results)
        total_time = sum(r.total_time for r in self.results)
        average_time = total_time / total_tests if total_tests > 0 else 0

        all_ops_per_sec = [r.operations_per_second for r in self.results]
        avg_ops_per_sec = sum(all_ops_per_sec) / len(all_ops_per_sec) if all_ops_per_sec else 0

        all_success_rates = [r.success_rate for r in self.results]
        avg_success_rate = sum(all_success_rates) / len(all_success_rates) if all_success_rates else 0

        all_memory_usage = [r.memory_usage_mb for r in self.results]
        avg_memory_usage = sum(all_memory_usage) / len(all_memory_usage) if all_memory_usage else 0

        return {
            "total_tests": total_tests,
            "total_execution_time": total_time,
            "average_execution_time": average_time,
            "average_operations_per_second": avg_ops_per_sec,
            "average_success_rate": avg_success_rate,
            "average_memory_usage_mb": avg_memory_usage,
            "worst_performing_operation": min(self.results, key=lambda x: x.operations_per_second).operation_name,
            "best_performing_operation": max(self.results, key=lambda x: x.operations_per_second).operation_name,
            "total_errors": sum(r.error_count for r in self.results)
        }


# Test data generators for various test scenarios
class TestDataGenerators:
    """Generate test data for various scenarios"""

    @staticmethod
    def create_edge_case_data() -> List[bytes]:
        """Create edge case test data"""
        return [
            b"",  # Empty
            b"\x00",  # Single null byte
            b"\xFF",  # Single max byte
            b"\x00" * 1000,  # All nulls
            b"\xFF" * 1000,  # All max values
            bytes(range(256)),  # All possible bytes once
            bytes(range(256)) * 4,  # All bytes repeated 4 times
        ]

    @staticmethod
    def create_large_data(size_mb: int = 10) -> bytes:
        """Create large test data"""
        size_bytes = size_mb * 1024 * 1024
        return TestDataGenerator.generate_random_data(size_bytes, seed=12345)

    @staticmethod
    def create_unicode_data() -> bytes:
        """Create data with Unicode characters"""
        # UTF-8 encoded test string with various Unicode characters
        test_string = "Hello 🌍 World! 🚀🎉🤖 Test Data with emojis and unicode: αβγδεζηθ"
        return test_string.encode('utf-8')

    @staticmethod
    def create_binary_structure_data() -> bytes:
        """Create structured binary data"""
        # Create data with headers, footers, and patterns
        header = b"BSEE" + (1024).to_bytes(4, 'big')
        content = TestDataGenerator.generate_random_data(8192, seed=54321)
        footer = b"END" + (1024).to_bytes(4, 'big')
        return header + content + footer

    @staticmethod
    def create_compressible_data() -> bytes:
        """Create highly compressible data"""
        # Repeating pattern that compresses well
        pattern = b"COMPRESS_TEST_DATA_PATTERN_" * 100
        return pattern[:4096]  # 4KB of repeating pattern

    @staticmethod
    def create_random_high_entropy_data() -> bytes:
        """Create random data with high entropy"""
        return TestDataGenerator.generate_random_data(4096, seed=98765)


# Test fixtures
@pytest.fixture
def mock_operations():
    """Fixture providing mock operations"""
    tester = OperationPerformanceTester()
    return tester.create_mock_operations()


@pytest.fixture
def performance_tester():
    """Fixture providing performance tester"""
    return OperationPerformanceTester()


@pytest.fixture
def edge_case_data():
    """Fixture providing edge case test data"""
    return TestDataGenerators.create_edge_case_data()


@pytest.fixture
def large_data():
    """Fixture providing large test data"""
    return TestDataGenerators.create_large_data(5)  # 5MB


@pytest.fixture
def unicode_data():
    """Fixture providing Unicode test data"""
    return TestDataGenerators.create_unicode_data()


@pytest.fixture
def structured_data():
    """Fixture providing structured binary data"""
    return TestDataGenerators.create_binary_structure_data()


@pytest.fixture
def compressible_data():
    """Fixture providing compressible test data"""
    return TestDataGenerators.create_compressible_data()


@pytest.fixture
def high_entropy_data():
    """Fixture providing high entropy test data"""
    return TestDataGenerators.create_random_high_entropy_data()


@pytest.fixture
def test_data_sizes():
    """Fixture providing various data sizes for testing"""
    return [1024, 4096, 16384, 65536, 262144]  # 1KB to 256KB


# Test functions
@pytest.mark.performance
def test_operation_basic_performance(mock_operations, performance_tester):
    """Test basic operation performance"""
    operation = mock_operations["xor"]
    test_data = TestDataGenerator.generate_random_data(2048, seed=42)

    result = performance_tester.test_operation_performance(
        operation, test_data, iterations=5
    )

    # Verify basic performance expectations
    assert result.iterations == 5
    assert result.success_rate >= 0.8  # At least 80% success rate
    assert result.average_time < 1.0  # Should complete within 1 second
    assert result.memory_usage_mb < 50.0  # Should use less than 50MB memory

    # Verify result structure
    assert hasattr(result, 'operation_name')
    assert result.operation_name == "xor"
    assert hasattr(result, 'operations_per_second')
    assert result.operations_per_second > 0


@pytest.mark.performance
def test_operation_error_handling(mock_operations, performance_tester):
    """Test operation error handling"""
    operation = mock_operations["xor"]

    # Create various invalid inputs
    invalid_inputs = [
        b"",  # Empty input
        b"\x00" * 1000,  # Large null data
        b"\xFF" * 1000,  # Large max value data
    ]

    result = performance_tester.test_error_handling(
        operation, invalid_inputs, ValueError
    )

    # Verify error handling
    assert result["total_inputs_tested"] == len(invalid_inputs)
    assert result["errors_raised"] > 0  # Should raise errors for some inputs
    assert result["error_handling_rate"] > 0.8  # Should handle errors correctly
    assert result["correct_error_type"] > 0.8  # Should raise correct error types


@pytest.mark.performance
def test_operation_memory_usage(mock_operations, performance_tester):
    """Test operation memory usage"""
    operation = mock_operations["substitute"]  # More memory-intensive operation

    result = performance_tester.test_memory_usage(
        operation, max_memory_mb=64.0
    )

    # Verify memory usage
    assert "results" in result
    assert len(result["results"]) > 0
    assert "is_efficient" in result

    # At least some tests should be within limits
    within_limit_count = sum(1 for r in result["results"] if r["within_limit"])
    assert within_limit_count > len(result["results"]) / 2  # At least half should be within limits


@pytest.mark.performance
def test_operation_scalability(mock_operations, performance_tester, test_data_sizes):
    """Test operation scalability"""
    operation = mock_operations["compress"]  # Complex operation

    results = performance_tester.test_operation_scalability(
        operation, test_data_sizes, iterations=3
    )

    # Verify scalability results
    assert len(results) == len(test_data_sizes)

    # Check that larger data takes longer (generally)
    sizes = sorted(test_data_sizes)
    times = [results[f"size_{size}"].average_time for size in sizes]

    # Allow for some non-linearity but generally increasing trend
    for i in range(1, len(times)):
        if sizes[i] > sizes[i-1] * 2:  # Size doubled
            # Time shouldn't be significantly less than previous
            assert times[i] >= times[i-1] * 0.1  # At least 10% of previous time


@pytest.mark.performance
def test_parallel_operation_performance(mock_operations, performance_tester):
    """Test parallel operation performance"""
    operation = mock_operations["xor"]  # Simple operation

    test_data = TestDataGenerator.generate_random_data(4096, seed=123)

    # Test with different thread counts
    thread_counts = [1, 2, 4, 8]
    parallel_results = {}

    for thread_count in thread_counts:
        result = performance_tester.test_parallel_operation_performance(
            operation, test_data, thread_count=thread_count, iterations_per_thread=3
        )
        parallel_results[thread_count] = result

        # Verify parallel execution
        assert result.threads_used == thread_count
        assert result.iterations == thread_count * 3  # threads * iterations_per_thread

        # Parallel should be faster for simple operations
        if thread_count > 1 and "single_threaded" in parallel_results:
            speedup = parallel_results[1].average_time / result.average_time
            # For simple operations, parallel may not be faster due to overhead
            # But it should not be much slower
            assert speedup > 0.5  # At least 50% efficiency

    # Calculate speedup efficiency
    max_threads = max(thread_counts)
    max_result = parallel_results[max_threads]
    single_result = parallel_results[1]

    if max_result.average_time > 0:
        speedup = single_result.average_time / max_result.average_time
        efficiency = speedup / max_threads
        assert efficiency > 0.2  # At least 20% efficiency


@pytest.mark.performance
def test_large_data_performance(mock_operations, performance_tester, large_data):
    """Test performance with large data"""
    operation = mock_operations["encrypt"]  # Most complex operation

    result = performance_tester.test_operation_performance(
        operation, large_data, iterations=3
    )

    # Verify large data handling
    assert result.iterations == 3
    assert result.data_size_bytes == len(large_data)
    assert result.success_rate >= 0.7  # May have issues with large data

    # Large data may take longer and use more memory
    assert result.average_time < 5.0  # Should complete within 5 seconds
    assert result.memory_usage_mb < 200.0  # Should use less than 200MB


@pytest.mark.performance
def test_unicode_data_performance(mock_operations, performance_tester, unicode_data):
    """Test performance with Unicode data"""
    operation = mock_operations["xor"]

    result = performance_tester.test_operation_performance(
        operation, unicode_data, iterations=5
    )

    # Verify Unicode data handling
    assert result.success_rate >= 0.8
    assert result.average_time < 1.0
    assert len(result.execution_times) == 5


@pytest.mark.performance
def test_structured_data_performance(mock_operations, performance_tester, structured_data):
    """Test performance with structured data"""
    operation = mock_operations["xor"]

    result = performance_tester.test_operation_performance(
        operation, structured_data, iterations=5
    )

    # Verify structured data handling
    assert result.success_rate >= 0.8
    assert result.average_time < 1.0
    assert result.data_size_bytes == len(structured_data)


@pytest.mark.performance
def test_compressible_data_performance(mock_operations, performance_tester, compressible_data):
    """Test performance with highly compressible data"""
    operation = mock_operations["compress"]

    result = performance_tester.test_operation_performance(
        operation, compressible_data, iterations=5
    )

    # Verify compressible data handling
    assert result.success_rate >= 0.8
    assert result.average_time < 1.0
    assert result.data_size_bytes == len(compressible_data)


@pytest.mark.performance
def test_high_entropy_data_performance(mock_operations, performance_tester, high_entropy_data):
    """Test performance with high entropy data"""
    operation = mock_operations["xor"]

    result = performance_tester.test_operation_performance(
        operation, high_entropy_data, iterations=5
    )

    # Verify high entropy data handling
    assert result.success_rate >= 0.8
    assert result.average_time < 1.0
    assert result.data_size_bytes == len(high_entropy_data)


@pytest.mark.performance
def test_edge_case_performance(mock_operations, performance_tester, edge_case_data):
    """Test performance with edge cases"""
    operation = mock_operations["xor"]

    # Test each edge case
    for i, test_data in enumerate(edge_case_data):
        print(f"  Testing edge case {i+1}: {len(test_data)} bytes")

        result = performance_tester.test_operation_performance(
            operation, test_data, iterations=3
        )

        # Verify edge case handling
        if len(test_data) == 0:
            # Empty data should either pass or be handled gracefully
            assert result.success_rate >= 0.5  # May or may not handle empty data
        else:
            assert result.success_rate >= 0.8

        # Memory usage should be reasonable for edge cases
        assert result.memory_usage_mb < 50.0


@pytest.mark.performance
def test_performance_summary(performance_tester):
    """Test performance summary generation"""
    # Add some test results
    operations = performance_tester.create_mock_operations()
    test_data = b"summary_test_data"

    for operation in operations.values():
        result = performance_tester.test_operation_performance(
            operation, test_data, iterations=2
        )
        performance_tester.add_result(result)

    # Generate summary
    summary = performance_tester.get_performance_summary()

    # Verify summary contains expected fields
    assert "total_tests" in summary
    assert "average_execution_time" in summary
    assert "average_operations_per_second" in summary
    assert "average_success_rate" in summary

    # Verify all tests are included
    assert summary["total_tests"] == len(performance_tester.results)

    # Verify basic statistics
    assert summary["total_execution_time"] > 0
    assert summary["average_execution_time"] >= 0
    assert summary["average_operations_per_second"] >= 0
    assert 0 <= summary["average_success_rate"] <= 1.0


def _create_benchmark_suite():
    """Helper to create a comprehensive benchmark suite"""
    return {
        "tester": OperationPerformanceTester(),
        "operations": OperationPerformanceTester().create_mock_operations(),
        "test_data_generators": TestDataGenerators(),
        "data_sizes": [1024, 4096, 16384, 65536, 262144],
        "thread_counts": [1, 2, 4, 8],
        "max_memory_mb": 256.0
    }


@pytest.mark.performance
def test_comprehensive_benchmark_suite():
    """Run comprehensive performance benchmark suite"""
    suite = _create_benchmark_suite()

    operations = suite["operations"]
    tester = suite["tester"]
    data_sizes = suite["data_sizes"]

    # Test each operation type
    for op_name, operation in operations.items():
        test_data = TestDataGenerator.generate_random_data(4096, seed=hash(op_name))
        result = tester.test_operation_performance(
            operation, test_data, iterations=5
        )
        tester.add_result(result)

    # Test scalability
    for op_name, operation in ["xor", "add_constant"]:  # Test simpler operations
        scaling_results = tester.test_operation_scalability(
            operation, data_sizes, iterations=3
        )
        for size_key, result in scaling_results.items():
            tester.add_result(result)

    # Test memory usage
    operation = operations["substitute"]  # More memory-intensive
    memory_results = tester.test_memory_usage(operation, max_memory_mb=128.0)
    tester.add_result(memory_results)

    # Get performance summary
    summary = tester.get_performance_summary()

    # Verify comprehensive testing
    assert summary["total_tests"] >= 15  # Should have multiple test results
    assert summary["average_success_rate"] >= 0.8  # Good overall success rate
    assert summary["average_operations_per_second"] > 1000  # Should be fast
    assert summary["average_memory_usage_mb"] < 100  # Reasonable memory usage

    # Export results
    output_path = "/tmp/operation_performance_results.json"
    tester.save_results(output_path)
    assert Path(output_path).exists()