"""
Benchmarking Framework
Standardized performance benchmarking for BSEE components
"""

import time
import os
import json
import statistics
import threading
import tempfile
import random
import gzip
import pickle
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
import concurrent.futures

from ..engine.state import BinaryState
from ..engine.operations import Operation
from ..engine.strategies import Strategy
from ..caching.operation_cache import OperationCache
from ..caching.metrics_cache import MetricsCache
from ..processing.parallel_processor import ParallelProcessor


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution"""
    iterations: int = 10
    warmup_iterations: int = 3
    timeout_seconds: float = 300.0
    enable_profiling: bool = False
    enable_memory_tracking: bool = True
    parallel_workers: Optional[int] = None
    output_directory: str = "benchmark_results"
    save_intermediate_results: bool = True


@dataclass
class BenchmarkResult:
    """Result of a single benchmark execution"""
    benchmark_name: str
    component_name: str
    test_data_name: str
    data_size_bytes: int
    iterations: int
    execution_times: List[float] = field(default_factory=list)
    memory_usage_mb: List[float] = field(default_factory=list)
    success_count: int = 0
    error_count: int = 0
    errors: List[str] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    def __post_init__(self):
        if not self.start_time:
            self.start_time = time.time()

    @property
    def total_time(self) -> float:
        """Total execution time"""
        return self.end_time - self.start_time

    @property
    def average_time(self) -> float:
        """Average execution time"""
        return statistics.mean(self.execution_times) if self.execution_times else 0.0

    @property
    def median_time(self) -> float:
        """Median execution time"""
        return statistics.median(self.execution_times) if self.execution_times else 0.0

    @property
    def min_time(self) -> float:
        """Minimum execution time"""
        return min(self.execution_times) if self.execution_times else 0.0

    @property
    def max_time(self) -> float:
        """Maximum execution time"""
        return max(self.execution_times) if self.execution_times else 0.0

    @property
    def std_deviation(self) -> float:
        """Standard deviation of execution times"""
        return statistics.stdev(self.execution_times) if len(self.execution_times) > 1 else 0.0

    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0.0

    @property
    def average_memory_mb(self) -> float:
        """Average memory usage in MB"""
        return statistics.mean(self.memory_usage_mb) if self.memory_usage_mb else 0.0

    @property
    def peak_memory_mb(self) -> float:
        """Peak memory usage in MB"""
        return max(self.memory_usage_mb) if self.memory_usage_mb else 0.0

    def throughput_ops_per_second(self) -> float:
        """Operations per second"""
        if self.total_time > 0:
            return self.success_count / self.total_time
        return 0.0

    def throughput_mb_per_second(self) -> float:
        """Throughput in MB per second"""
        if self.total_time > 0:
            total_mb = (self.data_size_bytes * self.success_count) / (1024 * 1024)
            return total_mb / self.total_time
        return 0.0


class TestDataGenerator:
    """Generate test data for benchmarking"""

    @staticmethod
    def generate_random_data(size: int, seed: Optional[int] = None) -> bytes:
        """Generate random binary data"""
        if seed is not None:
            random.seed(seed)
        return bytes([random.randint(0, 255) for _ in range(size)])

    @staticmethod
    def generate_repeating_pattern(size: int, pattern: bytes, seed: Optional[int] = None) -> bytes:
        """Generate data with repeating pattern"""
        if seed is not None:
            random.seed(seed)

        result = bytearray()
        pattern_len = len(pattern)
        for i in range(size):
            result.append(pattern[i % pattern_len])
        return bytes(result)

    @staticmethod
    def generate_structured_data(size: int) -> bytes:
        """Generate structured data with headers and patterns"""
        # Create a structured binary format
        header = b'BEEF' + size.to_bytes(4, 'big')  # Magic number + size
        footer = b'\x00\xFF\x00\xFF'  # Footer pattern

        # Fill middle with semi-random data
        middle_size = size - len(header) - len(footer)
        if middle_size > 0:
            # Create blocks of structured data
            block_size = 256
            middle = bytearray()
            for i in range(0, middle_size, block_size):
                block_header = i.to_bytes(4, 'big')
                block_data = TestDataGenerator.generate_random_data(min(block_size - 4, middle_size - i))
                middle.extend(block_header + block_data)

            return header + bytes(middle[:middle_size]) + footer
        else:
            return header + footer

    @staticmethod
    def generate_compressed_data(size: int) -> bytes:
        """Generate data that compresses well"""
        # Start with a small base pattern
        base_pattern = b'Hello, World! This is a repeating pattern for compression testing. '
        base_size = len(base_pattern)

        # Repeat the pattern to reach desired size
        result = bytearray()
        for i in range(size):
            result.append(base_pattern[i % base_size])

        # Compress it
        return gzip.compress(bytes(result))

    @staticmethod
    def generate_entropy_gradient(size: int) -> bytes:
        """Generate data with entropy gradient (low to high)"""
        result = bytearray()
        for i in range(size):
            # Gradually increase entropy
            entropy_factor = i / size
            if random.random() < entropy_factor:
                result.append(random.randint(0, 255))
            else:
                result.append(0)  # Low entropy bytes
        return bytes(result)


class BenchmarkSuite:
    """Main benchmarking suite for BSEE"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.test_data = self._generate_test_data()
        self.results = []
        self.current_benchmark = None

        # Ensure output directory exists
        os.makedirs(config.output_directory, exist_ok=True)

    def _generate_test_data(self) -> Dict[str, Dict[str, bytes]]:
        """Generate standardized test data"""
        test_data = {}

        # Size categories
        sizes = {
            'tiny': 256,           # 256 bytes
            'small': 4096,         # 4KB
            'medium': 65536,       # 64KB
            'large': 1048576,      # 1MB
            'xlarge': 16777216,    # 16MB
        }

        # Pattern categories
        patterns = {
            'random': lambda size: TestDataGenerator.generate_random_data(size),
            'structured': lambda size: TestDataGenerator.generate_structured_data(size),
            'compressed': lambda size: TestDataGenerator.generate_compressed_data(size),
            'repeating': lambda size: TestDataGenerator.generate_repeating_pattern(size, b'ABCD'),
            'entropy_gradient': lambda size: TestDataGenerator.generate_entropy_gradient(size),
        }

        # Generate combinations
        for size_name, size in sizes.items():
            test_data[size_name] = {}
            for pattern_name, generator in patterns.items():
                try:
                    data = generator(size)
                    test_data[size_name][pattern_name] = data
                except Exception as e:
                    print(f"Error generating {size_name}_{pattern_name}: {e}")

        return test_data

    def benchmark_operations(self, operations: List[Operation]) -> Dict[str, BenchmarkResult]:
        """Benchmark operations performance"""
        results = {}

        for operation in operations:
            for size_name, size_data in self.test_data.items():
                for pattern_name, test_data in size_data.items():
                    benchmark_name = f"{operation.name}_{size_name}_{pattern_name}"
                    print(f"Benchmarking: {benchmark_name}")

                    result = self._benchmark_operation(operation, test_data, benchmark_name)
                    results[benchmark_name] = result

                    # Save intermediate results if enabled
                    if self.config.save_intermediate_results:
                        self._save_result(result)

        return results

    def _benchmark_operation(self, operation: Operation, test_data: bytes, benchmark_name: str) -> BenchmarkResult:
        """Benchmark a single operation"""
        result = BenchmarkResult(
            benchmark_name=benchmark_name,
            component_name=operation.name,
            test_data_name=benchmark_name.split('_', 2)[-1],
            data_size_bytes=len(test_data),
            iterations=self.config.iterations
        )

        try:
            # Warmup iterations
            for _ in range(self.config.warmup_iterations):
                try:
                    state = BinaryState(test_data)
                    operation.apply(state)
                except:
                    pass  # Ignore warmup errors

            # Benchmark iterations
            for i in range(self.config.iterations):
                iteration_start = time.time()

                # Memory tracking
                start_memory = self._get_memory_usage() if self.config.enable_memory_tracking else 0

                try:
                    # Execute operation
                    state = BinaryState(test_data)
                    result_state = operation.apply(state)

                    # Verify reversibility if operation is reversible
                    if hasattr(operation, 'inverse') and operation.inverse:
                        try:
                            original_state = result_state.apply(operation.inverse)
                            # Note: Would need to verify data matches original
                        except:
                            pass  # Ignore verification errors in benchmarks

                    result.success_count += 1

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(str(e))

                # Memory tracking
                if self.config.enable_memory_tracking:
                    end_memory = self._get_memory_usage()
                    result.memory_usage_mb.append(end_memory - start_memory)

                # Time tracking
                iteration_time = time.time() - iteration_start
                result.execution_times.append(iteration_time)

                # Check timeout
                if time.time() - result.start_time > self.config.timeout_seconds:
                    print(f"Benchmark {benchmark_name} timed out")
                    break

        except Exception as e:
            result.errors.append(f"Benchmark setup error: {e}")

        result.end_time = time.time()
        return result

    def benchmark_strategies(self, strategies: List[Strategy]) -> Dict[str, BenchmarkResult]:
        """Benchmark strategies performance"""
        results = {}

        for strategy in strategies:
            for size_name, size_data in self.test_data.items():
                # Use only a subset of patterns for strategy benchmarks (they're more expensive)
                patterns_to_test = ['random', 'structured', 'repeating']

                for pattern_name in patterns_to_test:
                    if pattern_name not in size_data:
                        continue

                    test_data = size_data[pattern_name]
                    benchmark_name = f"{strategy.name}_{size_name}_{pattern_name}"
                    print(f"Benchmarking strategy: {benchmark_name}")

                    result = self._benchmark_strategy(strategy, test_data, benchmark_name)
                    results[benchmark_name] = result

                    # Save intermediate results if enabled
                    if self.config.save_intermediate_results:
                        self._save_result(result)

        return results

    def _benchmark_strategy(self, strategy: Strategy, test_data: bytes, benchmark_name: str) -> BenchmarkResult:
        """Benchmark a single strategy"""
        result = BenchmarkResult(
            benchmark_name=benchmark_name,
            component_name=strategy.name,
            test_data_name=benchmark_name.split('_', 2)[-1],
            data_size_bytes=len(test_data),
            iterations=self.config.iterations
        )

        try:
            # Reduce iterations for strategy benchmarks (they're expensive)
            strategy_iterations = max(1, self.config.iterations // 10)

            # Warmup iteration
            try:
                state = BinaryState(test_data)
                strategy.analyze(state, max_iterations=10)
            except:
                pass  # Ignore warmup errors

            # Benchmark iterations
            for i in range(strategy_iterations):
                iteration_start = time.time()

                # Memory tracking
                start_memory = self._get_memory_usage() if self.config.enable_memory_tracking else 0

                try:
                    # Execute strategy
                    state = BinaryState(test_data)
                    analysis_result = strategy.analyze(state, max_iterations=100)

                    result.success_count += 1

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(str(e))

                # Memory tracking
                if self.config.enable_memory_tracking:
                    end_memory = self._get_memory_usage()
                    result.memory_usage_mb.append(end_memory - start_memory)

                # Time tracking
                iteration_time = time.time() - iteration_start
                result.execution_times.append(iteration_time)

                # Check timeout
                if time.time() - result.start_time > self.config.timeout_seconds:
                    print(f"Strategy benchmark {benchmark_name} timed out")
                    break

        except Exception as e:
            result.errors.append(f"Strategy benchmark setup error: {e}")

        result.end_time = time.time()
        return result

    def benchmark_caching(self, operation_cache: OperationCache, metrics_cache: MetricsCache) -> Dict[str, BenchmarkResult]:
        """Benchmark caching performance"""
        results = {}

        # Operation cache benchmark
        print("Benchmarking operation cache...")
        op_cache_result = self._benchmark_operation_cache(operation_cache)
        results['operation_cache'] = op_cache_result

        # Metrics cache benchmark
        print("Benchmarking metrics cache...")
        metrics_cache_result = self._benchmark_metrics_cache(metrics_cache)
        results['metrics_cache'] = metrics_cache_result

        return results

    def _benchmark_operation_cache(self, cache: OperationCache) -> BenchmarkResult:
        """Benchmark operation cache performance"""
        result = BenchmarkResult(
            benchmark_name="operation_cache_performance",
            component_name="OperationCache",
            test_data_name="mixed_operations",
            data_size_bytes=0,  # Not applicable for cache benchmark
            iterations=self.config.iterations
        )

        try:
            # Test data for caching
            test_data = self.test_data['medium']['random']
            from ..engine.operations import XorOperation, AddConstantOperation

            operations = [XorOperation(42), AddConstantOperation(10)]

            # Cache warmup
            for op in operations:
                cache.cache_result(op.name, test_data, {}, test_data, 0.001)

            # Benchmark cache hits
            for i in range(self.config.iterations):
                iteration_start = time.time()

                try:
                    op = operations[i % len(operations)]
                    cached_result = cache.get_cached_result(op.name, test_data, {})

                    if cached_result is not None:
                        result.success_count += 1
                    else:
                        result.error_count += 1
                        result.errors.append("Cache miss")

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(str(e))

                iteration_time = time.time() - iteration_start
                result.execution_times.append(iteration_time)

        except Exception as e:
            result.errors.append(f"Cache benchmark setup error: {e}")

        result.end_time = time.time()
        return result

    def _benchmark_metrics_cache(self, cache: MetricsCache) -> BenchmarkResult:
        """Benchmark metrics cache performance"""
        result = BenchmarkResult(
            benchmark_name="metrics_cache_performance",
            component_name="MetricsCache",
            test_data_name="entropy_calculations",
            data_size_bytes=0,  # Not applicable for cache benchmark
            iterations=self.config.iterations
        )

        try:
            # Test data for metrics caching
            test_data = self.test_data['medium']['random']

            # Cache warmup
            cache.cache_metric_result('entropy', test_data, {}, 7.5, 0.01)

            # Benchmark cache hits
            for i in range(self.config.iterations):
                iteration_start = time.time()

                try:
                    cached_result = cache.get_cached_metric('entropy', test_data, {})

                    if cached_result is not None:
                        result.success_count += 1
                    else:
                        result.error_count += 1
                        result.errors.append("Cache miss")

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(str(e))

                iteration_time = time.time() - iteration_start
                result.execution_times.append(iteration_time)

        except Exception as e:
            result.errors.append(f"Metrics cache benchmark setup error: {e}")

        result.end_time = time.time()
        return result

    def benchmark_parallel_processing(self, processor: ParallelProcessor) -> Dict[str, BenchmarkResult]:
        """Benchmark parallel processing performance"""
        results = {}

        # Sequential vs parallel comparison
        print("Benchmarking parallel processing...")

        test_data = self.test_data['large']['random']
        from ..engine.operations import XorOperation, AddConstantOperation

        operations = [XorOperation(i) for i in range(10)]

        # Sequential benchmark
        sequential_result = self._benchmark_sequential_operations(operations, test_data)
        results['sequential_operations'] = sequential_result

        # Parallel benchmark
        parallel_result = self._benchmark_parallel_operations(processor, operations, test_data)
        results['parallel_operations'] = parallel_result

        return results

    def _benchmark_sequential_operations(self, operations: List[Operation], test_data: bytes) -> BenchmarkResult:
        """Benchmark sequential operation execution"""
        result = BenchmarkResult(
            benchmark_name="sequential_operations",
            component_name="SequentialProcessor",
            test_data_name="large_random",
            data_size_bytes=len(test_data),
            iterations=self.config.iterations
        )

        try:
            for i in range(self.config.iterations):
                iteration_start = time.time()

                try:
                    state = BinaryState(test_data)
                    for op in operations:
                        state = op.apply(state)

                    result.success_count += 1

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(str(e))

                iteration_time = time.time() - iteration_start
                result.execution_times.append(iteration_time)

        except Exception as e:
            result.errors.append(f"Sequential benchmark setup error: {e}")

        result.end_time = time.time()
        return result

    def _benchmark_parallel_operations(self, processor: ParallelProcessor, operations: List[Operation], test_data: bytes) -> BenchmarkResult:
        """Benchmark parallel operation execution"""
        result = BenchmarkResult(
            benchmark_name="parallel_operations",
            component_name="ParallelProcessor",
            test_data_name="large_random",
            data_size_bytes=len(test_data),
            iterations=max(1, self.config.iterations // 5)  # Fewer iterations for parallel tests
        )

        try:
            for i in range(result.iterations):
                iteration_start = time.time()

                try:
                    # Evaluate operations in parallel
                    state = BinaryState(test_data)
                    results = processor.evaluate_operations_parallel(state, operations)

                    if all(r.success for r in results.values()):
                        result.success_count += 1
                    else:
                        result.error_count += 1
                        result.errors.append("Some parallel operations failed")

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(str(e))

                iteration_time = time.time() - iteration_start
                result.execution_times.append(iteration_time)

        except Exception as e:
            result.errors.append(f"Parallel benchmark setup error: {e}")

        result.end_time = time.time()
        return result

    def run_scaling_benchmark(self, component: Any, component_name: str,
                            size_range: List[int] = None) -> Dict[str, BenchmarkResult]:
        """Run scaling benchmark across different data sizes"""
        if size_range is None:
            size_range = [1024, 4096, 16384, 65536, 262144, 1048576]  # 1KB to 1MB

        results = {}

        for size in size_range:
            test_data = TestDataGenerator.generate_random_data(size)
            benchmark_name = f"{component_name}_scaling_{size}"

            if hasattr(component, 'apply'):  # It's an operation
                result = self._benchmark_operation(component, test_data, benchmark_name)
            elif hasattr(component, 'analyze'):  # It's a strategy
                result = self._benchmark_strategy(component, test_data, benchmark_name)
            else:
                continue

            results[benchmark_name] = result

            if self.config.save_intermediate_results:
                self._save_result(result)

        return results

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0

    def _save_result(self, result: BenchmarkResult):
        """Save benchmark result to file"""
        try:
            filename = f"{result.benchmark_name}_{int(time.time())}.json"
            filepath = os.path.join(self.config.output_directory, filename)

            with open(filepath, 'w') as f:
                json.dump(result.__dict__, f, indent=2, default=str)

        except Exception as e:
            print(f"Error saving benchmark result: {e}")

    def generate_report(self, format: str = 'html') -> str:
        """Generate comprehensive benchmark report"""
        if format.lower() == 'html':
            return self._generate_html_report()
        elif format.lower() == 'json':
            return self._generate_json_report()
        elif format.lower() == 'csv':
            return self._generate_csv_report()
        else:
            raise ValueError(f"Unsupported report format: {format}")

    def _generate_html_report(self) -> str:
        """Generate HTML benchmark report"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BSEE Benchmark Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { margin: 20px 0; }
                .table { border-collapse: collapse; width: 100%; }
                .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .table th { background-color: #f2f2f2; }
                .chart { margin: 20px 0; }
                .fast { color: green; }
                .medium { color: orange; }
                .slow { color: red; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BSEE Performance Benchmark Report</h1>
                <p><strong>Generated:</strong> {time}</p>
                <p><strong>Total Benchmarks:</strong> {total_benchmarks}</p>
            </div>
        """.format(
            time=time.strftime('%Y-%m-%d %H:%M:%S'),
            total_benchmarks=len(self.results)
        )

        # Summary table
        html += """
        <div class="summary">
            <h2>Summary</h2>
            <table class="table">
                <tr><th>Benchmark</th><th>Component</th><th>Avg Time (s)</th><th>Throughput (MB/s)</th><th>Success Rate</th><th>Status</th></tr>
        """

        for result in self.results:
            throughput = result.throughput_mb_per_second()
            status_class = 'fast' if throughput > 10 else 'medium' if throughput > 1 else 'slow'
            status_text = 'Fast' if throughput > 10 else 'Medium' if throughput > 1 else 'Slow'

            html += f"""
                <tr>
                    <td>{result.benchmark_name}</td>
                    <td>{result.component_name}</td>
                    <td>{result.average_time:.4f}</td>
                    <td>{throughput:.2f}</td>
                    <td>{result.success_rate:.1f}%</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
            """

        html += """
            </table>
        </div>
        </body>
        </html>
        """

        return html

    def _generate_json_report(self) -> str:
        """Generate JSON benchmark report"""
        report_data = {
            'metadata': {
                'generated_time': time.time(),
                'total_benchmarks': len(self.results),
                'config': self.config.__dict__
            },
            'results': [
                {
                    'benchmark_name': result.benchmark_name,
                    'component_name': result.component_name,
                    'data_size_bytes': result.data_size_bytes,
                    'iterations': result.iterations,
                    'average_time': result.average_time,
                    'median_time': result.median_time,
                    'min_time': result.min_time,
                    'max_time': result.max_time,
                    'std_deviation': result.std_deviation,
                    'success_rate': result.success_rate,
                    'throughput_ops_per_sec': result.throughput_ops_per_second(),
                    'throughput_mb_per_sec': result.throughput_mb_per_second(),
                    'average_memory_mb': result.average_memory_mb,
                    'peak_memory_mb': result.peak_memory_mb,
                    'errors': result.errors
                }
                for result in self.results
            ]
        }

        return json.dumps(report_data, indent=2)

    def _generate_csv_report(self) -> str:
        """Generate CSV benchmark report"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Benchmark Name', 'Component', 'Data Size (bytes)', 'Iterations',
            'Avg Time (s)', 'Median Time (s)', 'Min Time (s)', 'Max Time (s)',
            'Std Dev', 'Success Rate (%)', 'Throughput (ops/s)', 'Throughput (MB/s)',
            'Avg Memory (MB)', 'Peak Memory (MB)'
        ])

        # Data rows
        for result in self.results:
            writer.writerow([
                result.benchmark_name,
                result.component_name,
                result.data_size_bytes,
                result.iterations,
                result.average_time,
                result.median_time,
                result.min_time,
                result.max_time,
                result.std_deviation,
                result.success_rate,
                result.throughput_ops_per_second(),
                result.throughput_mb_per_second(),
                result.average_memory_mb,
                result.peak_memory_mb
            ])

        return output.getvalue()

    def save_report(self, filename: str, format: str = 'html'):
        """Save benchmark report to file"""
        report = self.generate_report(format)
        filepath = os.path.join(self.config.output_directory, filename)

        with open(filepath, 'w') as f:
            f.write(report)

        print(f"Report saved to: {filepath}")
        return filepath

    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result to the suite"""
        self.results.append(result)

    def clear_results(self):
        """Clear all benchmark results"""
        self.results.clear()