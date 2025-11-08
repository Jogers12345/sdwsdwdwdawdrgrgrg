"""
Strategy Performance Benchmarks
Comprehensive strategy performance analysis and benchmarking
"""

import pytest
import time
import threading
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

from tests.conftest import TestDataGenerator, performance_test_config


@dataclass
class StrategyBenchmarkResult:
    """Result of strategy benchmarking"""
    strategy_name: str
    file_type: str
    data_size_bytes: int
    iterations: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    std_deviation: float
    operations_per_second: float
    memory_usage_mb: float
    success_rate: float
    best_score: float
    worst_score: float
    average_score: float
    convergence_iterations: Dict[str, float]
    execution_times: List[float]


class StrategyBenchmarker:
    """Comprehensive strategy performance benchmarking system"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or performance_test_config()
        self.results = []
        self.benchmark_history = []

    def benchmark_strategy_performance(self, strategy, test_files: Dict[str, bytes],
                                     iterations: int = 5) -> StrategyBenchmarkResult:
        """Benchmark a single strategy against multiple file types"""
        all_results = []
        memory_usage_samples = []
        scores = []

        for file_type, test_data in test_files.items():
            print(f"  Benchmarking {strategy.name} on {file_type} ({len(test_data)} bytes)...")

            execution_times = []
            convergence_iterations = []

            for iteration in range(iterations):
                # Track memory usage before test
                start_memory = self._get_memory_usage()

                # Execute strategy
                start_time = time.time()
                try:
                    result = strategy.analyze(test_data, max_iterations=100)
                    end_time = time.time()

                    execution_time = end_time - start_time
                    execution_times.append(execution_time)

                    # Collect metrics
                    scores.append(result.get("score", 0.0))
                    convergence_iterations.append(result.get("iterations", 0))

                    # Track memory usage after test
                    end_memory = self._get_memory_usage()
                    memory_usage_samples.append(end_memory - start_memory)

                except Exception as e:
                    print(f"    Error in iteration {iteration + 1}: {e}")
                    execution_times.append(float('inf'))  # Mark as failed

            # Calculate statistics
            valid_times = [t for t in execution_times if t != float('inf')]
            if not valid_times:
                print(f"    ERROR: All iterations failed for {file_type}")
                continue

            avg_time = statistics.mean(valid_times)
            std_dev = statistics.stdev(valid_times) if len(valid_times) > 1 else 0.0
            min_time = min(valid_times)
            max_time = max(valid_times)

            result = StrategyBenchmarkResult(
                strategy_name=strategy.name,
                file_type=file_type,
                data_size_bytes=len(test_data),
                iterations=iterations,
                total_time=sum(valid_times),
                average_time=avg_time,
                min_time=min_time,
                max_time=max_time,
                std_deviation=std_dev,
                operations_per_second=len(test_data) / avg_time if avg_time > 0 else 0.0,
                memory_usage_mb=statistics.mean(memory_usage_samples) if memory_usage_samples else 0.0,
                success_rate=len(valid_times) / iterations,
                best_score=max(scores) if scores else 0.0,
                worst_score=min(scores) if scores else 0.0,
                average_score=statistics.mean(scores) if scores else 0.0,
                convergence_iterations={
                    "average": statistics.mean(convergence_iterations) if convergence_iterations else 0.0,
                    "min": min(convergence_iterations) if convergence_iterations else 0.0,
                    "max": max(convergence_iterations) if convergence_iterations else 0.0
                },
                execution_times=valid_times
            )

            all_results.append(result)

        # Combine results across file types
        if all_results:
            combined_result = self._combine_results(all_results)
            return combined_result
        else:
            # Return empty result if all tests failed
            return StrategyBenchmarkResult(
                strategy_name=strategy.name,
                file_type="all",
                data_size_bytes=0,
                iterations=iterations,
                total_time=0.0,
                average_time=0.0,
                min_time=0.0,
                max_time=0.0,
                std_deviation=0.0,
                operations_per_second=0.0,
                memory_usage_mb=0.0,
                success_rate=0.0,
                best_score=0.0,
                worst_score=0.0,
                average_score=0.0,
                convergence_iterations={},
                execution_times=[]
            )

    def benchmark_strategies_comparison(self, strategies: List,
                                     test_data: bytes,
                                     max_iterations: int = 100) -> Dict[str, StrategyBenchmarkResult]:
        """Benchmark multiple strategies on the same data"""
        results = {}
        test_files = {"comparison_data": test_data}

        for strategy in strategies:
            print(f"Benchmarking strategy: {strategy.name}")
            try:
                result = self.benchmark_strategy_performance(
                    strategy, test_files, iterations=3
                )
                results[strategy.name] = result
            except Exception as e:
                print(f"    ERROR: Strategy {strategy.name} failed: {e}")
                # Create failed result
                results[strategy.name] = StrategyBenchmarkResult(
                    strategy_name=strategy.name,
                    file_type="comparison_data",
                    data_size_bytes=len(test_data),
                    iterations=3,
                    total_time=0.0,
                    average_time=0.0,
                    min_time=0.0,
                    max_time=0.0,
                    std_deviation=0.0,
                    operations_per_second=0.0,
                    memory_usage_mb=0.0,
                    success_rate=0.0,
                    best_score=0.0,
                    worst_score=0.0,
                    average_score=0.0,
                    convergence_iterations={},
                    execution_times=[]
                )

        return results

    def benchmark_scaling_performance(self, strategy, data_sizes: List[int],
                                    max_iterations: int = 100) -> Dict[str, StrategyBenchmarkResult]:
        """Benchmark strategy performance across different data sizes"""
        results = {}

        for size in data_sizes:
            print(f"  Testing size: {size} bytes")
            test_data = TestDataGenerator.generate_random_data(size, seed=size)
            test_files = {f"size_{size}": test_data}

            try:
                result = self.benchmark_strategy_performance(
                    strategy, test_files, iterations=3
                )
                results[f"size_{size}"] = result
            except Exception as e:
                print(f"    ERROR: Size {size} failed: {e}")
                results[f"size_{size}"] = StrategyBenchmarkResult(
                    strategy_name=strategy.name,
                    file_type=f"size_{size}",
                    data_size_bytes=size,
                    iterations=3,
                    total_time=0.0,
                    average_time=0.0,
                    min_time=0.0,
                    max_time=0.0,
                    std_deviation=0.0,
                    operations_per_second=0.0,
                    memory_usage_mb=0.0,
                    success_rate=0.0,
                    best_score=0.0,
                    worst_score=0.0,
                    average_score=0.0,
                    convergence_iterations={},
                    execution_times=[]
                )

        return results

    def benchmark_concurrent_strategies(self, strategies: List,
                                        test_data: bytes,
                                        concurrent_runs: int = 4) -> Dict[str, Any]:
        """Benchmark strategies running concurrently"""
        print(f"Benchmarking {len(strategies)} strategies concurrently ({concurrent_runs} runs each)")

        def benchmark_single_strategy(strategy):
            test_files = {"concurrent_data": test_data}
            return self.benchmark_strategy_performance(strategy, test_files, iterations=2)

        start_time = time.time()

        # Run strategies concurrently
        with ThreadPoolExecutor(max_workers=min(concurrent_runs, len(strategies))) as executor:
            # Submit all benchmark tasks
            future_to_strategy = {
                executor.submit(benchmark_single_strategy, strategy): strategy
                for strategy in strategies
            }

            # Collect results
            results = {}
            for future in as_completed(future_to_strategy):
                strategy = future_to_strategy[future]
                try:
                    result = future.result()
                    results[strategy.name] = result
                except Exception as e:
                    print(f"    ERROR: Concurrent benchmark for {strategy.name} failed: {e}")

        total_time = time.time() - start_time

        return {
            "individual_results": results,
            "total_concurrent_time": total_time,
            "concurrent_runs": concurrent_runs,
            "strategies_tested": len(strategies),
            "strategies_successful": len(results)
        }

    def benchmark_memory_scaling(self, strategy, max_memory_mb: float = 512.0) -> Dict[str, Any]:
        """Benchmark strategy memory usage and scaling"""
        results = {
            "memory_tests": [],
            "memory_usage_vs_size": [],
            "memory_efficiency": {}
        }

        test_sizes = [1024, 4096, 16384, 65536, 262144]  # 1KB to 256KB

        for size in test_sizes:
            print(f"  Testing memory usage at size: {size} bytes")

            # Test with increasing data sizes
            test_data = TestDataGenerator.generate_random_data(size, seed=size)
            test_files = {f"memory_test_{size}": test_data}

            try:
                # Measure memory before benchmark
                baseline_memory = self._get_memory_usage()

                result = self.benchmark_strategy_performance(
                    strategy, test_files, iterations=2
                )

                # Calculate memory overhead
                memory_overhead = result.memory_usage_mb
                memory_per_byte = memory_overhead / size if size > 0 else 0

                results["memory_tests"].append({
                    "data_size": size,
                    "memory_usage_mb": memory_overhead,
                    "memory_per_byte": memory_per_byte,
                    "operations_per_second": result.operations_per_second
                })

                results["memory_usage_vs_size"].append({
                    "data_size": size,
                    "memory_mb": memory_overhead
                })

                # Check if memory usage is within limits
                if memory_overhead > max_memory_mb:
                    print(f"    WARNING: Memory usage ({memory_overhead:.2f} MB) exceeds limit ({max_memory_mb} MB)")

            except Exception as e:
                print(f"    ERROR: Memory test at size {size} failed: {e}")

        # Calculate memory efficiency metrics
        if results["memory_tests"]:
            avg_memory_per_byte = statistics.mean(
                test["memory_per_byte"] for test in results["memory_tests"]
            )
            max_memory_per_byte = max(
                test["memory_per_byte"] for test in results["memory_tests"]
            )
            min_memory_per_byte = min(
                test["memory_per_byte"] for test in results["memory_tests"]
            )

            results["memory_efficiency"] = {
                "average_bytes_per_mb": 1.0 / avg_memory_per_byte if avg_memory_per_byte > 0 else 0,
                "max_bytes_per_mb": 1.0 / min_memory_per_byte if min_memory_per_byte > 0 else 0,
                "min_bytes_per_mb": 1.0 / max_memory_per_byte if max_memory_per_byte > 0 else 0
            }

        return results

    def benchmark_parallel_vs_sequential(self, strategy, test_data: bytes,
                                         parallel_workers: int = 4) -> Dict[str, Any]:
        """Compare parallel vs sequential strategy execution"""
        print(f"Comparing parallel vs sequential execution for {strategy.name}")

        # Sequential benchmark
        print("  Running sequential benchmark...")
        sequential_start = time.time()
        test_files = {"sequential_data": test_data}
        sequential_result = self.benchmark_strategy_performance(
            strategy, test_files, iterations=3
        )
        sequential_time = time.time() - sequential_start

        # Parallel benchmark
        print(f"  Running parallel benchmark ({parallel_workers} workers)...")
        parallel_start = time.time()
        parallel_results = self.benchmark_concurrent_strategies(
            [strategy], test_data, concurrent_runs=parallel_workers
        )
        parallel_time = time.time() - parallel_start

        # Calculate speedup
        if strategy.name in parallel_results["individual_results"]:
            parallel_strategy_time = parallel_results["individual_results"][strategy.name].average_time
            speedup = sequential_result.average_time / parallel_strategy_time if parallel_strategy_time > 0 else 0

            efficiency = speedup / parallel_workers  # Parallel efficiency

            return {
                "sequential_result": sequential_result,
                "parallel_result": parallel_results["individual_results"][strategy.name],
                "sequential_time": sequential_time,
                "parallel_time": parallel_time,
                "speedup": speedup,
                "efficiency": efficiency,
                "parallel_workers": parallel_workers
            }
        else:
            return {
                "sequential_result": sequential_result,
                "parallel_result": None,
                "sequential_time": sequential_time,
                "parallel_time": parallel_time,
                "speedup": 0.0,
                "efficiency": 0.0,
                "parallel_workers": parallel_workers,
                "error": "Parallel benchmark failed"
            }

    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report_lines = [
            "=" * 70,
            "Strategy Performance Benchmark Report",
            "=" * 70,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # Single strategy results
        if len(results) == 1 and "strategy_name" in results[results]:
            result = results[results["strategy_name"]]
            self._format_single_strategy_report(report_lines, result)

        # Comparison results
        elif all(isinstance(r, StrategyBenchmarkResult) for r in results.values()):
            self._format_comparison_report(report_lines, results)

        # Complex results (concurrent, memory, etc.)
        else:
            self._format_complex_report(report_lines, results)

        return "\n".join(report_lines)

    def _format_single_strategy_report(self, lines: List[str], result: StrategyBenchmarkResult):
        """Format report for single strategy"""
        lines.extend([
            f"Strategy: {result.strategy_name}",
            f"Data Size: {result.data_size_bytes:,} bytes",
            f"Iterations: {result.iterations}",
            "",
            "Performance Metrics:",
            f"  Average Time: {result.average_time:.4f} seconds",
            f"  Min Time: {result.min_time:.4f} seconds",
            f"  Max Time: {result.max_time:.4f} seconds",
            f"  Std Deviation: {result.std_deviation:.4f} seconds",
            f"  Operations/Second: {result.operations_per_second:,.0f}",
            f"  Memory Usage: {result.memory_usage_mb:.2f} MB",
            f"  Success Rate: {result.success_rate*100:.1f}%",
            "",
            "Performance Scores:",
            f"  Best Score: {result.best_score:.4f}",
            f"  Average Score: {result.average_score:.4f}",
            f"  Worst Score: {result.worst_score:.4f}",
            "",
            "Convergence Analysis:",
            f"  Average Iterations: {result.convergence_iterations['average']:.1f}",
            f"  Min Iterations: {result.convergence_iterations['min']:.1f}",
            f"  Max Iterations: {result.convergence_iterations['max']:.1f}",
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

    def _format_comparison_report(self, lines: List[str], results: Dict[str, StrategyBenchmarkResult]):
        """Format report for strategy comparison"""
        lines.extend([
            "Strategy Performance Comparison",
            f"Number of Strategies: {len(results)}",
            ""
        ])

        # Sort strategies by average score
        sorted_strategies = sorted(
            results.items(),
            key=lambda x: x[1].average_score,
            reverse=True
        )

        lines.append("Ranking by Average Score:")
        lines.append("-" * 40)
        for rank, (name, result) in enumerate(sorted_strategies, 1):
            lines.append(
                f"{rank:2d}. {name:20s} {result.average_score:6.3f} "
                f"({result.average_time:.4f}s, {result.operations_per_second:,.0f} ops/s)"
            )

        lines.extend([
            "",
            "Performance Comparison Table:",
            "-" * 60
        ])

        # Create comparison table
        header = f"{'Strategy':20s} {'Score':8s} {'Time':10s} {'Ops/s':12s} {'Memory':10s} {'Success':8s}"
        lines.append(header)
        lines.append("-" * len(header))

        for name, result in sorted_strategies:
            line = f"{name:20s} {result.average_score:8.3f} "
            line += f"{result.average_time:10.4f} "
            line += f"{result.operations_per_second:12,.0f} "
            line += f"{result.memory_usage_mb:10.2f} "
            line += f"{result.success_rate*100:6.1f}%"
            lines.append(line)

        lines.extend([
            "",
            "Performance Recommendations:",
        ])

        # Find best and worst performing strategies
        best_strategy = sorted_strategies[0]
        worst_strategy = sorted_strategies[-1]

        lines.extend([
            f"  Best Overall: {best_strategy[0]} (score: {best_strategy[1].average_score:.3f})",
            f"  Fastest: {min(results.items(), key=lambda x: x[1].average_time)[0]} "
            f"({min(results.items(), key=lambda x: x[1].average_time)[1].average_time:.4f}s)",
            f"  Most Efficient: {max(results.items(), key=lambda x: x[1].operations_per_second)[0]} "
            f"({max(results.items(), key=lambda x: x[1].operations_per_second)[1].operations_per_second:,.0f} ops/s)",
        ])

        if worst_strategy[1].average_score < best_strategy[1].average_score * 0.5:
            lines.append(f"  ⚠️  Performance gap detected between best and worst strategies")

    def _format_complex_report(self, lines: List[str], results: Dict[str, Any]):
        """Format report for complex benchmark results"""
        if "individual_results" in results:
            lines.extend([
                "Concurrent Strategy Benchmark Results",
                f"Total Concurrent Time: {results['total_concurrent_time']:.2f}s",
                f"Strategies Tested: {results['strategies_tested']}",
                f"Strategies Successful: {results['strategies_successful']}",
                f"Success Rate: {results['strategies_successful']/results['strategies_tested']*100:.1f}%",
                ""
            ])
            # Would format individual results here...

        elif "memory_tests" in results:
            lines.extend([
                "Memory Scaling Benchmark Results",
                "",
                "Memory Usage by Data Size:",
                "-" * 40
            ])
            for test in results["memory_tests"]:
                lines.append(
                    f"  {test['data_size']:8d} bytes: {test['memory_usage_mb']:8.2f} MB "
                    f"({test['operations_per_second']:8.0f} ops/s)"
                )
            # Would add memory efficiency analysis here...

        else:
            lines.append("Complex benchmark results (detailed formatting needed)")

    def export_results(self, output_path: str, format: str = "json"):
        """Export benchmark results to file"""
        if format.lower() == "json":
            # Convert results to JSON-serializable format
            json_results = {}
            for key, value in self.results.items():
                if isinstance(value, StrategyBenchmarkResult):
                    json_results[key] = value.__dict__
                else:
                    # For complex results, convert to string for now
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
            writer.writerow([
                "Strategy", "File Type", "Data Size", "Avg Time", "Min Time",
                "Max Time", "Std Dev", "Ops/Second", "Memory MB", "Success Rate",
                "Best Score", "Avg Score", "Worst Score"
            ])

            # Write data
            for key, value in self.results.items():
                if isinstance(value, StrategyBenchmarkResult):
                    writer.writerow([
                        value.strategy_name,
                        value.file_type,
                        value.data_size_bytes,
                        value.average_time,
                        value.min_time,
                        value.max_time,
                        value.std_deviation,
                        value.operations_per_second,
                        value.memory_usage_mb,
                        value.success_rate,
                        value.best_score,
                        value.average_score,
                        value.worst_score
                    ])

            with open(output_path, 'w') as f:
                f.write(output.getvalue())

        print(f"Benchmark results exported to: {output_path}")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0

    def _combine_results(self, results: List[StrategyBenchmarkResult]) -> StrategyBenchmarkResult:
        """Combine results from multiple file types"""
        if not results:
            raise ValueError("No results to combine")

        strategy_name = results[0].strategy_name
        total_iterations = sum(r.iterations for r in results)
        total_time = sum(r.total_time for r in results)
        weighted_avg_time = sum(r.total_time * r.iterations for r in results) / total_iterations
        memory_usage_mb = sum(r.memory_usage_mb for r in results) / len(results)

        all_execution_times = []
        for result in results:
            all_execution_times.extend(result.execution_times)

        if all_execution_times:
            min_time = min(all_execution_times)
            max_time = max(all_execution_times)
            avg_time = statistics.mean(all_execution_times)
            std_dev = statistics.stdev(all_execution_times) if len(all_execution_times) > 1 else 0.0
        else:
            min_time = max_time = avg_time = std_dev = 0.0

        total_data_size = sum(r.data_size_bytes for r in results)
        avg_operations_per_second = sum(r.operations_per_second for r in results) / len(results)

        success_rates = [r.success_rate for r in results]
        avg_success_rate = sum(success_rates) / len(success_rates)

        scores = []
        for result in results:
            scores.extend([result.best_score, result.worst_score, result.average_score])

        if scores:
            best_score = max(scores)
            worst_score = min(scores)
            average_score = sum(scores) / len(scores)
        else:
            best_score = worst_score = average_score = 0.0

        # Combine convergence iterations
        avg_convergence = {
            "average": sum(r.convergence_iterations["average"] for r in results) / len(results),
            "min": min(r.convergence_iterations["min"] for r in results),
            "max": max(r.convergence_iterations["max"] for r in results)
        }

        return StrategyBenchmarkResult(
            strategy_name=strategy_name,
            file_type="combined",
            data_size_bytes=total_data_size,
            iterations=total_iterations,
            total_time=total_time,
            average_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_deviation=std_dev,
            operations_per_second=avg_operations_per_second,
            memory_usage_mb=memory_usage_mb,
            success_rate=avg_success_rate,
            best_score=best_score,
            worst_score=worst_score,
            average_score=average_score,
            convergence_iterations=avg_convergence,
            execution_times=all_execution_times
        )

    def save_results(self):
        """Save benchmark results to history"""
        self.benchmark_history.append({
            "timestamp": time.time(),
            "results": [r.__dict__ if isinstance(r, StrategyBenchmarkResult) else r
                        for r in self.results]
        })

        # Keep only last 10 benchmark runs
        if len(self.benchmark_history) > 10:
            self.benchmark_history = self.benchmark_history[-10:]

    def get_historical_trends(self) -> Dict[str, Any]:
        """Analyze performance trends from historical data"""
        if not self.benchmark_history:
            return {}

        trends = {
            "execution_time_trends": {},
            "score_trends": {},
            "memory_trends": {}
        }

        # Calculate trends for each strategy
        strategy_names = set()
        for run in self.benchmark_history:
            for result in run["results"]:
                if isinstance(result, dict) and "strategy_name" in result:
                    strategy_names.add(result["strategy_name"])

        for strategy_name in strategy_names:
            times = []
            scores = []
            memories = []

            for run in self.benchmark_history:
                for result in run["results"]:
                    if isinstance(result, dict) and result.get("strategy_name") == strategy_name:
                        times.append(result.get("average_time", 0))
                        scores.append(result.get("average_score", 0))
                        memories.append(result.get("memory_usage_mb", 0))

            if len(times) > 1:
                # Calculate trend (simple linear regression slope)
                time_trend = (times[-1] - times[0]) / len(times)
                score_trend = (scores[-1] - scores[0]) / len(scores) if len(scores) > 1 else 0
                memory_trend = (memories[-1] - memories[0]) / len(memories)

                trends["execution_time_trends"][strategy_name] = time_trend
                trends["score_trends"][strategy_name] = score_trend
                trends["memory_trends"][strategy_name] = memory_trend

        return trends


# Mock strategies for testing
class MockMCTSStrategy:
    def __init__(self, config=None):
        self.name = "MockMCTS"
        self.config = config or {}

    def analyze(self, data: bytes, max_iterations: int = 100):
        # Simulate MCTS analysis
        time.sleep(0.1)  # Simulate processing time
        return {
            "strategy": "mcts",
            "score": 0.75 + (len(data) / len(data)) * 0.1,  # Score varies with data
            "iterations": min(max_iterations, random.randint(10, 50)),
            "converged": True
        }


class MockGeneticStrategy:
    def __init__(self, config=None):
        self.name = "MockGenetic"
        self.config = config or {}

    def analyze(self, data: bytes, max_iterations: int = 100):
        # Simulate genetic analysis
        time.sleep(0.05)  # Simulate processing time
        return {
            "strategy": "genetic",
            "score": 0.65 + (len(data) % 20) * 0.01,
            "iterations": min(max_iterations // 2, random.randint(5, 25)),
            "converged": True
        }


class MockBeamSearchStrategy:
    def __init__(self, config=None):
        self.name = "MockBeamSearch"
        self.config = config or {}

    def analyze(self, data: bytes, max_iterations: int = 100):
        # Simulate beam search analysis
        time.sleep(0.02)  # Fast processing time
        return {
            "strategy": "beam_search",
            "score": 0.55 + (len(data) % 15) * 0.01,
            "iterations": min(max_iterations // 4, random.randint(3, 15)),
            "converged": True
        }


# Test functions
def create_test_benchmark_suite():
    """Create a comprehensive test benchmark suite"""
    benchmarker = StrategyBenchmarker()

    # Create test data
    test_files = {
        "random_small": TestDataGenerator.generate_random_data(1024, seed=1),
        "random_medium": TestDataGenerator.generate_random_data(16384, seed=2),
        "structured": TestDataGenerator.generate_structured_data(8192),
        "repeating": TestDataGenerator.generate_pattern_data(4096, b"PATTERN"),
        "compressed": TestDataGenerator.generate_compressed_data(4096)
    }

    # Create mock strategies
    strategies = [
        MockMCTSStrategy({"exploration_constant": 1.41}),
        MockGeneticStrategy({"population_size": 50}),
        MockBeamSearchStrategy({"beam_width": 3})
    ]

    return {
        "benchmarker": benchmarker,
        "test_files": test_files,
        "strategies": strategies,
        "data_sizes": [1024, 4096, 16384, 65536, 262144]
    }


@pytest.mark.performance
def test_strategy_performance_benchmark(test_benchmark_suite):
    """Test strategy performance benchmarking"""
    benchmarker, test_files, strategies, data_sizes = (
        test_benchmark_suite["benchmarker"],
        test_benchmark_suite["test_files"],
        test_benchmark_suite["strategies"],
        test_benchmark_suite["data_sizes"]
    )

    # Benchmark each strategy
    for strategy in strategies:
        result = benchmarker.benchmark_strategy_performance(
            strategy, test_files, iterations=3
        )

        # Verify basic metrics
        assert result.iterations == 3
        assert result.success_rate >= 0.8  # At least 80% success rate
        assert result.average_time < 1.0  # Should complete within 1 second
        assert result.memory_usage_mb < 100.0  # Should use less than 100MB memory

        # Verify result structure
        assert hasattr(result, 'strategy_name')
        assert hasattr(result, 'average_score')
        assert hasattr(result, 'operations_per_second')


@pytest.mark.performance
def test_strategy_comparison_benchmark(test_benchmark_suite):
    """Test strategy comparison benchmarking"""
    benchmarker, test_files, strategies = (
        test_benchmark_suite["benchmarker"],
        test_benchmark_suite["test_files"],
        test_benchmark_suite["strategies"]
    )

    test_data = TestDataGenerator.generate_random_data(8192, seed=42)

    comparison_results = benchmarker.benchmark_strategies_comparison(
        strategies, test_data
    )

    # Verify comparison results
    assert len(comparison_results) == len(strategies)
    assert all(
        hasattr(result, 'strategy_name') and
        hasattr(result, 'average_time')
        for result in comparison_results.values()
    )


@pytest.mark.performance
def test_scaling_benchmark(test_benchmark_suite):
    """Test scaling performance benchmarking"""
    benchmarker, strategies, data_sizes = (
        test_benchmark_suite["benchmarker"],
        test_benchmark_suite["strategies"],
        test_benchmark_suite["data_sizes"]
    )

    strategy = strategies[0]  # Test with MCTS

    scaling_results = benchmarker.benchmark_scaling_performance(
        strategy, data_sizes, max_iterations=50
    )

    # Verify scaling results
    assert len(scaling_results) == len(data_sizes)

    # Check that larger data takes longer (generally)
    sizes = sorted([int(key.split('_')[1]) for key in scaling_results.keys()])
    times = [scaling_results[f"size_{size}"].average_time for size in sizes]

    # Allow for some non-linearity but generally increasing trend
    for i in range(1, len(times)):
        if sizes[i] > sizes[i-1] * 2:  # Size doubled
            # Time shouldn't be significantly less than previous
            assert times[i] >= times[i-1] * 0.5


@pytest.mark.performance
def test_concurrent_benchmark(test_benchmark_suite):
    """Test concurrent benchmarking"""
    benchmarker, strategies = (
        test_benchmark_suite["benchmarker"],
        test_benchmark_suite["strategies"]
    )

    test_data = TestDataGenerator.generate_random_data(4096, seed=100)

    concurrent_results = benchmarker.benchmark_concurrent_strategies(
        strategies, test_data, concurrent_runs=3
    )

    # Verify concurrent results
    assert concurrent_results["strategies_tested"] == len(strategies)
    assert concurrent_results["strategies_successful"] > 0
    assert concurrent_results["concurrent_runs"] == 3
    assert "individual_results" in concurrent_results


@pytest.mark.performance
def test_memory_benchmark(test_benchmark_suite):
    """Test memory usage benchmarking"""
    benchmarker, strategies = (
        test_benchmark_suite["benchmarker"],
        test_benchmark_suite["strategies"]
    )

    strategy = strategies[0]  # Test with MCTS

    memory_results = benchmarker.benchmark_memory_scaling(
        strategy, max_memory_mb=256.0
    )

    # Verify memory results
    assert "memory_tests" in memory_results
    assert "memory_usage_vs_size" in memory_results
    assert "memory_efficiency" in memory_results
    assert len(memory_results["memory_tests"]) > 0


@pytest.mark.performance
def test_parallel_vs_sequential_benchmark(test_benchmark_suite):
    """Test parallel vs sequential benchmarking"""
    benchmarker, strategies = (
        test_benchmark_suite["benchmarker"],
        test_benchmark_suite["strategies"]
    )

    strategy = strategies[0]  # Test with MCTS
    test_data = TestDataGenerator.generate_random_data(4096, seed=200)

    comparison_results = benchmarker.benchmark_parallel_vs_sequential(
        strategy, test_data, parallel_workers=2
    )

    # Verify comparison results
    assert "sequential_result" in comparison_results
    assert "parallel_result" in comparison_results
    assert "speedup" in comparison_results
    assert "efficiency" in comparison_results

    # Speedup should be positive (parallel faster)
    if comparison_results["parallel_result"] is not None:
        assert comparison_results["speedup"] > 0
        # Efficiency should be reasonable (not too low)
        assert comparison_results["efficiency"] > 0.1  # At least 10% efficiency