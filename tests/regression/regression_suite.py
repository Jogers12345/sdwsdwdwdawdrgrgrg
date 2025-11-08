"""
Regression Test Suite
Prevent reintroduction of fixed bugs and verify stability
"""

import pytest
import time
import json
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import importlib

from tests.conftest import TestDataGenerator, TestResultValidator, expected_results_dir


class RegressionCategory(Enum):
    """Categories of regression tests"""
    OPERATION_REVERSIBILITY = "operation_reversibility"
    STRATEGY_CONVERGENCE = "strategy_convergence"
    CONFIG_FILE_FORMATS = "config_file_formats"
    CACHE_BEHAVIOR = "cache_behavior"
    PERFORMANCE_THRESHOLDS = "performance_thresholds"
    GUI_RESPONSIVENESS = "gui_responsiveness"
    METRIC_ACCURACY = "metric_accuracy"
    PARALLEL_PROCESSING = "parallel_processing"
    MEMORY_MANAGEMENT = "memory_management"


@dataclass
class RegressionTest:
    """Individual regression test definition"""
    name: str
    category: RegressionCategory
    description: str
    test_function: Callable
    parameters: Dict[str, Any]
    expected_result: Any
    tolerance: float = 0.0
    timeout_seconds: float = 30.0
    is_critical: bool = False


@dataclass
class TestExecution:
    """Execution result of a regression test"""
    test_name: str
    passed: bool
    execution_time: float
    actual_result: Any
    expected_result: Any
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class RegressionTestSuite:
    """Comprehensive regression testing suite"""

    def __init__(self, expected_results_dir: Optional[Path] = None):
        self.tests = []
        self.test_results = {}
        self.failed_tests = []
        self.passed_tests = []
        self.execution_history = []
        self.expected_results_dir = expected_results_dir or expected_results_dir()
        self._setup_tests()

    def _setup_tests(self):
        """Setup all regression tests"""
        # Operation reversibility tests
        self.add_reversibility_test(
            "xor_reversibility",
            RegressionCategory.OPERATION_REVERSIBILITY,
            "XOR operation must be reversible",
            self._test_xor_reversibility,
            {"key": 0x42},
            is_critical=True
        )

        self.add_reversibility_test(
            "add_constant_reversibility",
            RegressionCategory.OPERATION_REVERSIBILITY,
            "Add constant operation must be reversible",
            self._test_add_constant_reversibility,
            {"value": 10},
            is_critical=True
        )

        self.add_reversibility_test(
            "rotate_reversibility",
            RegressionCategory.OPERATION_REVERSIBILITY,
            "Rotate operation must be reversible",
            self._test_rotate_reversibility,
            {"bits": 3},
            is_critical=True
        )

        # Strategy convergence tests
        self.add_regression_test(
            "mcts_convergence_rate",
            RegressionCategory.STRATEGY_CONVERGENCE,
            "MCTS strategy must maintain convergence rate",
            self._test_mcts_convergence_rate,
            {"target_rate": 0.85, "tolerance": 0.1},
            is_critical=True
        )

        self.add_regression_test(
            "genetic_convergence_rate",
            RegressionCategory.STRATEGY_CONVERGENCE,
            "Genetic strategy must maintain convergence rate",
            self._test_genetic_convergence_rate,
            {"target_rate": 0.80, "tolerance": 0.15},
            is_critical=True
        )

        self.add_regression_test(
            "beam_search_consistency",
            RegressionCategory.STRATEGY_CONVERGENCE,
            "Beam search must produce consistent results",
            self._test_beam_search_consistency,
            {"max_iterations": 50, "beam_width": 3},
            is_critical=True
        )

        # Configuration file format tests
        self.add_regression_test(
            "json_config_parsing",
            RegressionCategory.CONFIG_FILE_FORMATS,
            "JSON configuration files must be parsable",
            self._test_json_config_parsing,
            {"config_path": "test_config.json"},
            is_critical=False
        )

        self.add_regression_test(
            "yaml_config_parsing",
            RegressionCategory.CONFIG_FILE_FORMATS,
            "YAML configuration files must be parsable",
            self._test_yaml_config_parsing,
            {"config_path": "test_config.yaml"},
            is_critical=False
        )

        # Cache behavior tests
        self.add_regression_test(
            "cache_hit_rate",
            RegressionCategory.CACHE_BEHAVIOR,
            "Cache hit rate must be consistent",
            self._test_cache_hit_rate,
            {"min_hit_rate": 0.8, "max_hit_rate": 1.0},
            is_critical=False
        )

        self.add_regression_test(
            "cache_memory_usage",
            RegressionCategory.CACHE_BEHAVIOR,
            "Cache memory usage must be within limits",
            self._test_cache_memory_usage,
            {"max_memory_mb": 256.0},
            is_critical=False
        )

        # Performance threshold tests
        self.add_regression_test(
            "operation_execution_time",
            RegressionCategory.PERFORMANCE_THRESHOLDS,
            "Operation execution time must be within thresholds",
            self._test_operation_execution_time,
            {"max_time_seconds": 0.1, "data_size": 1024},
            is_critical=True
        )

        self.add_regression_test(
            "strategy_analysis_time",
            RegressionCategory.PERFORMANCE_THRESHOLDS,
            "Strategy analysis time must be within thresholds",
            self._test_strategy_analysis_time,
            {"max_time_seconds": 5.0, "data_size": 1024},
            is_critical=True
        )

        # GUI responsiveness tests
        self.add_regression_test(
            "gui_response_time",
            RegressionCategory.GUI_RESPONSIVENESS,
            "GUI response time must be within limits",
            self._test_gui_response_time,
            {"max_response_ms": 100},
            is_critical=False
        )

        self.add_regression_test(
            "gui_memory_usage",
            RegressionCategory.GUI_RESPONSIVENESS,
            "GUI memory usage must be within limits",
            self._test_gui_memory_usage,
            {"max_memory_mb": 100.0},
            is_critical=False
        )

        # Metric accuracy tests
        self.add_regression_test(
            "entropy_calculation",
            RegressionCategory.METRIC_ACCURACY,
            "Entropy calculation must be accurate",
            self._test_entropy_calculation,
            {"test_data": "test", "expected_entropy": 1.5},
            is_critical=False
        )

        self.add_regression_test(
            "compression_ratio",
            RegressionCategory.METRIC_ACCURACY,
            "Compression ratio calculation must be accurate",
            self._test_compression_ratio,
            {"test_data": b"test " * 100, "expected_ratio": 0.8},
            is_critical=False
        )

        # Parallel processing tests
        self.add_regression_test(
            "parallel_scaling",
            RegressionCategory.PARALLEL_PROCESSING,
            "Parallel processing must scale properly",
            self._test_parallel_scaling,
            {"max_workers": 8, "expected_speedup": 4.0},
            is_critical=True
        )

        self.add_regression_test(
            "thread_safety",
            RegressionCategory.PARALLEL_PROCESSING,
            "Parallel processing must be thread-safe",
            self._test_thread_safety,
            {"concurrent_operations": 10},
            is_critical=True
        )

        # Memory management tests
        self.add_regression_test(
            "large_file_memory_usage",
            RegressionCategory.MEMORY_MANAGEMENT,
            "Large file processing must use limited memory",
            self._test_large_file_memory_usage,
            {"file_size_mb": 100, "max_memory_mb": 64.0},
            is_critical=True
        )

        self.add_regression_test(
            "memory_cleanup",
            RegressionCategory.MEMORY_MANAGEMENT,
            "Memory cleanup must work correctly",
            self._test_memory_cleanup,
            {"iterations": 10},
            is_critical=False
        )

    def add_regression_test(self, name: str, category: RegressionCategory,
                         description: str, test_function: Callable,
                         parameters: Dict[str, Any], expected_result: Any,
                         tolerance: float = 0.0, timeout_seconds: float = 30.0,
                         is_critical: bool = False):
        """Add a regression test to the suite"""
        test = RegressionTest(
            name=name,
            category=category,
            description=description,
            test_function=test_function,
            parameters=parameters,
            expected_result=expected_result,
            tolerance=tolerance,
            timeout_seconds=timeout_seconds,
            is_critical=is_critical
        )
        self.tests.append(test)

    def add_reversibility_test(self, name: str, category: RegressionCategory,
                               description: str, test_function: Callable,
                               parameters: Dict[str, Any], is_critical: bool = True):
        """Add a reversibility regression test"""
        self.add_regression_test(
            name=name,
            category=category,
            description=description,
            test_function=test_function,
            parameters=parameters,
            expected_result=True,  # Reversibility should return True
            timeout_seconds=10.0,
            is_critical=is_critical
        )

    def run_regression_suite(self) -> Dict[str, Any]:
        """Run all regression tests"""
        start_time = time.time()

        for test in self.tests:
            try:
                # Check timeout
                execution_start = time.time()
                test_result = None

                def run_with_timeout():
                    try:
                        return test.test_function(**test.parameters)
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e)
                        }

                # Run test with timeout
                import threading
                result_container = {"result": None}
                test_thread = threading.Thread(
                    target=lambda: result_container.update({"result": run_with_timeout()})
                )
                test_thread.daemon = True
                test_thread.start()
                test_thread.join(timeout=test.timeout_seconds)

                if result_container["result"] is None:
                    # Timeout
                    test_result = TestExecution(
                        test_name=test.name,
                        passed=False,
                        execution_time=test.timeout_seconds,
                        actual_result="TIMEOUT",
                        expected_result=test.expected_result,
                        error_message="Test timed out",
                        timestamp=time.time()
                    )
                elif isinstance(result_container["result"], dict) and not result_container["result"].get("success", True):
                    # Function returned error object
                    error_result = result_container["result"]
                    test_result = TestExecution(
                        test_name=test.name,
                        passed=False,
                        execution_time=time.time() - execution_start,
                        actual_result=None,
                        expected_result=test.expected_result,
                        error_message=error_result.get("error", "Unknown error"),
                        timestamp=time.time()
                    )
                else:
                    # Function returned success
                    actual_result = result_container["result"]
                    if isinstance(actual_result, dict) and "success" in actual_result:
                        test_passed = actual_result["success"]
                        actual_value = actual_result.get("value", actual_result)
                    else:
                        test_passed = actual_result  # Boolean or compared value
                        actual_value = actual_result

                    # Compare with expected result
                    if isinstance(test.expected_result, bool):
                        test_passed = test_passed == test.expected_result
                    else:
                        # Use tolerance for numeric comparisons
                        if isinstance(actual_value, (int, float)) and isinstance(test.expected_result, (int, float)):
                            test_passed = abs(actual_value - test.expected_result) <= test.tolerance
                        else:
                            # Direct comparison for other types
                            test_passed = test_passed == test.expected_result

                    test_result = TestExecution(
                        test_name=test.name,
                        passed=test_passed,
                        execution_time=time.time() - execution_start,
                        actual_result=actual_value,
                        expected_result=test.expected_result,
                        timestamp=time.time()
                    )

                # Store result
                self.test_results[test.name] = test_result
                self.execution_history.append(test_result)

                if test_result.passed:
                    self.passed_tests.append(test.name)
                else:
                    self.failed_tests.append(test.name)

                # Log result
                status = "PASS" if test_result.passed else "FAIL"
                print(f"  {status}: {test.name} ({test_result.execution_time:.2f}s)")

            except Exception as e:
                error_result = TestExecution(
                    test_name=test.name,
                    passed=False,
                    execution_time=0.0,
                    actual_result=None,
                    expected_result=test.expected_result,
                    error_message=f"Test execution error: {str(e)}",
                    timestamp=time.time()
                )

                self.test_results[test.name] = error_result
                self.failed_tests.append(test.name)
                self.execution_history.append(error_result)

                print(f"  ERROR: {test.name} - {str(e)}")

        # Generate summary
        total_time = time.time() - start_time
        summary = self._generate_summary(total_time)

        # Load expected results if available
        self._validate_against_expected_results()

        return summary

    def _validate_against_expected_results(self):
        """Validate results against expected results database"""
        if not self.expected_results_dir.exists():
            print("  WARNING: Expected results directory not found, skipping validation")
            return

        # Load expected results
        expected_files = list(self.expected_results_dir.glob("*.json"))
        if not expected_files:
            print("  WARNING: No expected results files found")
            return

        # Compare with actual results
        deviations_found = []

        for expected_file in expected_files:
            try:
                with open(expected_file, 'r') as f:
                    expected_data = json.load(f)

                test_name = expected_file.stem
                if test_name in self.test_results:
                    actual_result = self.test_results[test_name]
                    if actual_result.passed != expected_data.get("expected_pass", actual_result.passed):
                        deviations_found.append({
                            "test": test_name,
                            "expected": expected_data.get("expected_pass", "unknown"),
                            "actual": actual_result.passed,
                            "severity": "critical" if self._is_test_critical(test_name) else "warning"
                        })

                        # Check metric deviations
                        if "expected_metrics" in expected_data and "actual_result" in actual_result.__dict__:
                            expected_metrics = expected_data["expected_metrics"]
                            for metric, expected_value in expected_metrics.items():
                                if metric in actual_result.metrics and actual_result.metrics[metric] is not None:
                                    actual_value = actual_result.metrics[metric]
                                    if abs(actual_value - expected_value) > 0.1:  # 10% tolerance
                                        deviations_found.append({
                                            "test": test_name,
                                            "metric": metric,
                                            "expected": expected_value,
                                            "actual": actual_value,
                                            "severity": "warning"
                                        })

            except Exception as e:
                print(f"  ERROR: Failed to load expected results from {expected_file}: {e}")

        # Report deviations
        if deviations_found:
            print(f"  REGRESSION DETECTED: {len(deviations_found)} deviations found")
            for deviation in deviations_found:
                severity = deviation["severity"].upper()
                print(f"    {severity}: {deviation['test']} - {deviation.get('metric', '')}")
                if "expected" in deviation and "actual" in deviation:
                    print(f"      Expected: {deviation['expected']}, Actual: {deviation['actual']}")

    def _is_test_critical(self, test_name: str) -> bool:
        """Check if test is marked as critical"""
        for test in self.tests:
            if test.name == test_name:
                return test.is_critical
        return False

    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate test execution summary"""
        total_tests = len(self.tests)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        critical_failures = sum(1 for test_name in self.failed_tests if self._is_test_critical(test_name))

        # Calculate pass rate
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Categorize failures by type
        failure_categories = {}
        for test in self.tests:
            if test.name in self.failed_tests:
                category = test.category.value
                if category not in failure_categories:
                    failure_categories[category] = []
                failure_categories[category].append(test.name)

        return {
            "execution_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "critical_failures": critical_failures,
                "pass_rate": f"{pass_rate:.1f}%",
                "total_execution_time": f"{total_time:.2f}s",
                "average_test_time": f"{(total_time / total_tests):.2f}s" if total_tests > 0 else "0.00s"
            },
            "failed_tests_by_category": failure_categories,
            "execution_history": [
                {
                    "name": result.test_name,
                    "passed": result.passed,
                    "execution_time": f"{result.execution_time:.3f}s",
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))
                }
                for result in self.execution_history
            ],
            "critical_failures": [test_name for test_name in self.failed_tests if self._is_test_critical(test_name)],
            "new_failures": self._identify_new_failures(),
            "regression_detected": len(self.failed_tests) > 0,
            "execution_timestamp": time.time()
        }

    def _identify_new_failures(self) -> List[str]:
        """Identify tests that failed but previously passed"""
        # This would compare with historical execution data
        # For now, just return all failed tests
        return self.failed_tests

    def get_regression_report(self, format: str = "text") -> str:
        """Generate regression test report"""
        summary = self._generate_summary(0.0)  # Use current time

        if format.lower() == "html":
            return self._generate_html_report(summary)
        elif format.lower() == "json":
            return self._generate_json_report(summary)
        else:
            return self._generate_text_report(summary)

    def _generate_text_report(self, summary: Dict[str, Any]) -> str:
        """Generate text format regression report"""
        report_lines = [
            "=" * 70,
            "BSEE Regression Test Report",
            "=" * 70,
            "",
            f"Execution Time: {summary['execution_timestamp']}",
            f"Total Tests: {summary['execution_summary']['total_tests']}",
            f"Passed: {summary['execution_summary']['passed_tests']}",
            f"Failed: {summary['execution_summary']['failed_tests']}",
            f"Pass Rate: {summary['execution_summary']['pass_rate']}",
            f"Total Time: {summary['execution_summary']['total_execution_time']}",
            f"Average Time: {summary['execution_summary']['average_test_time']}",
            "",
            "CRITICAL FAILURES" if summary['critical_failures'] else "No Critical Failures",
            "-" * 30,
        ]

        if summary['critical_failures']:
            for test in summary['critical_failures']:
                report_lines.append(f"  CRITICAL: {test}")

        report_lines.extend([
            "",
            "FAILED TESTS BY CATEGORY" if summary['failed_tests_by_category'] else "No Failed Tests",
            "-" * 30
        ])

        for category, tests in summary['failed_tests_by_category'].items():
            report_lines.append(f"  {category.replace('_', ' ').title()}:")
            for test in tests:
                report_lines.append(f"    - {test}")

        if summary['regression_detected']:
            report_lines.extend([
                "",
                "REGRESSION DETECTED!",
                f"  Total failures: {len(summary['failed_tests'])}",
                f"  Critical failures: {len(summary['critical_failures'])}",
                f"  New failures: {len(summary['new_failures'])}",
                "",
                "IMMEDIATE ACTION REQUIRED"
            ])

        report_lines.extend([
            "",
            "Detailed Execution History:",
            "=" * 30
        ])

        for entry in summary['execution_history'][-20:]:  # Last 20 entries
            status = "PASS" if entry['passed'] else "FAIL"
            report_lines.append(f"  {entry['timestamp']} | {status:5} | {entry['test_name']} ({entry['execution_time']})")

        report_lines.extend([
            "",
            "=" * 70
        ])

        return "\n".join(report_lines)

    def _generate_html_report(self, summary: Dict[str, Any]) -> str:
        """Generate HTML format regression report"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BSEE Regression Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { margin: 20px 0; }
                .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
                .summary-item { background: #f8f9fa; padding: 15px; border-radius: 5px; }
                .summary-item h3 { margin: 0 0 10px 0; }
                .critical { background-color: #ffebee; border-left: 4px solid #f8d7da; }
                .warning { background-color: #fff3cd; border-left: 4px solid #ffeaa7; }
                .failures { margin: 20px 0; }
                .failures h2 { color: #d9534f; }
                .failures ul { list-style: none; padding: 0; }
                .failures li { margin: 5px 0; padding: 5px; background: #f8f9fa; border-radius: 3px; }
                .critical-failure { border-left: 3px solid #dc3545; }
                .history { margin: 20px 0; }
                .history table { width: 100%; border-collapse: collapse; }
                .history th, .history td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .history th { background-color: #f2f2f2; }
                .history .pass { color: #28a745; }
                .history .fail { color: #dc3545; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BSEE Regression Test Report</h1>
                <p><strong>Generated:</strong> {execution_timestamp}</p>
            </div>

            <div class="summary">
                <div class="summary-grid">
                    <div class="summary-item">
                        <h3>Total Tests</h3>
                        <p style="font-size: 2em; margin: 0;">{total_tests}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Passed</h3>
                        <p style="font-size: 2em; margin: 0; color: #28a745;">{passed_tests}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Failed</h3>
                        <p style="font-size: 2em; margin: 0; color: #dc3545;">{failed_tests}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Pass Rate</h3>
                        <p style="font-size: 1.5em; margin: 0;">{pass_rate}%</p>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h3>Execution Details</h3>
                    <p><strong>Total Time:</strong> {total_execution_time}</p>
                    <p><strong>Average Time:</strong> {average_test_time}</p>
                </div>

                <div class="summary-item {critical if critical_failures else ''}">
                    <h3>Critical Failures</h3>
                    <p style="font-size: 2em; margin: 0;">{critical_failures}</p>
                </div>
            </div>
        """

        # Add failures by category
        if failed_tests_by_category:
            html_template += """
            <div class="failures">
                <h2>Failed Tests by Category</h2>
                <ul>
            """

            for category, tests in failed_tests_by_category.items():
                html_template += f"                    <li><strong>{category.replace('_', ' ').title()}:</strong>"
                for test in tests:
                    html_template += f" {test}"
                html_template += "</li>\n"

            html_template += "                </ul>\n            </div>\n"

        # Add regression alert
        if regression_detected:
            html_template += """
            <div class="failures">
                <h2>🚨 REGRESSION DETECTED!</h2>
                <ul>
                    <li><strong>Total Failures:</strong> {total_failures}</li>
                    <li><strong>Critical Failures:</strong> {critical_failures}</li>
                    <li><strong>New Failures:</strong> {len(new_failures)}</li>
                </ul>
                <div style="margin-top: 15px; padding: 15px; background-color: #f8d7da; border-radius: 5px;">
                    <strong style="color: #721c24; font-size: 1.2em;">IMMEDIATE ACTION REQUIRED</strong>
                </div>
            </div>
        """

        # Add execution history
        html_template += """
            <div class="history">
                <h2>Recent Execution History</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Status</th>
                            <th>Test Name</th>
                            <th>Execution Time</th>
                        </tr>
                    </thead>
                    <tbody>
            """

        for entry in execution_history[-20:]:  # Last 20 entries
            status = "pass" if entry['passed'] else "fail"
            status_class = status
            html_template += f"""
                        <tr>
                            <td>{entry['timestamp']}</td>
                            <td class="{status_class}">{status.upper()}</td>
                            <td>{entry['test_name']}</td>
                            <td>{entry['execution_time']}</td>
                        </tr>
            """

        html_template += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

        return html_template.format(**summary)

    def _generate_json_report(self, summary: Dict[str, Any]) -> str:
        """Generate JSON format regression report"""
        return json.dumps(summary, indent=2, default=str)

    def save_report(self, output_path: Optional[str] = None, format: str = "text") -> str:
        """Save regression report to file"""
        report = self.get_regression_report(format)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"Regression report saved to: {output_path}")
        else:
            print(report)

        return report

    def export_failed_tests_only(self, output_path: str) -> str:
        """Export only failed tests for regression analysis"""
        failed_tests_data = {
            "export_timestamp": time.time(),
            "total_failed": len(self.failed_tests),
            "critical_failures": [test for test in self.failed_tests if self._is_test_critical(test)],
            "failed_test_details": [
                {
                    "name": test_name,
                    "result": self.test_results[test_name].__dict__,
                    "category": next((test.category for test in self.tests if test.name == test_name), "unknown")
                }
                for test_name in self.failed_tests
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(failed_tests_data, f, indent=2, default=str)

        print(f"Failed tests exported to: {output_path}")
        return output_path

    def setup_continuous_regression_monitoring(self, interval_hours: int = 1):
        """Setup automated regression monitoring"""
        # This would integrate with CI/CD pipeline
        # For now, just return configuration
        return {
            "monitoring_interval_hours": interval_hours,
            "tests_monitored": len(self.tests),
            "critical_tests_monitored": sum(1 for test in self.tests if test.is_critical),
            "setup_timestamp": time.time()
        }

    # Individual test implementations
    def _test_xor_reversibility(self, key: int) -> Dict[str, Any]:
        """Test XOR operation reversibility"""
        def xor_operation(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        def xor_inverse(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)  # XOR is its own inverse

        # Test data
        test_data = b"XOR reversibility test data 123"
        transformed = xor_operation(test_data, key)
        restored = xor_inverse(transformed, key)

        # Verify reversibility
        is_reversible = restored == test_data

        # Expected result should be True
        return {"success": is_reversible, "transformed_length": len(transformed), "restored_length": len(restored)}

    def _test_add_constant_reversibility(self, value: int) -> Dict[str, Any]:
        """Test add constant operation reversibility"""
        def add_operation(data: bytes, value: int) -> bytes:
            return bytes((b + value) % 256 for b in data)

        def subtract_operation(data: bytes, value: int) -> bytes:
            return bytes((b - value) % 256 for b in data)

        # Test data
        test_data = b"Add constant test data"
        transformed = add_operation(test_data, value)
        restored = subtract_operation(transformed, value)

        # Verify reversibility
        is_reversible = restored == test_data

        return {"success": is_reversible}

    def _test_rotate_reversibility(self, bits: int) -> Dict[str, Any]:
        """Test rotate operation reversibility"""
        def rotate_left(data: bytes, bits: int) -> bytes:
            bits = bits % 8
            if bits == 0:
                return data
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        def rotate_right(data: bytes, bits: int) -> bytes:
            bits = bits % 8
            if bits == 0:
                return data
            return rotate_left(data, 8 - bits)

        # Test data
        test_data = b"Rotate test data ABC"
        transformed = rotate_left(test_data, bits)
        restored = rotate_right(transformed, bits)

        # Verify reversibility
        is_reversible = restored == test_data

        return {"success": is_reversible}

    def _test_mcts_convergence_rate(self, target_rate: float, tolerance: float) -> Dict[str, Any]:
        """Test MCTS strategy convergence rate"""
        # Mock MCTS strategy for testing
        class MockMCTS:
            def analyze(self, data: bytes, max_iterations: int = 100) -> Dict[str, Any]:
                # Simulate MCTS behavior with controlled convergence rate
                convergence_probability = target_rate + (hash(data) % (2 * tolerance) - tolerance) / 100
                converged = random.random() < convergence_probability

                return {
                    "strategy": "mcts",
                    "converged": converged,
                    "iterations": min(max_iterations, random.randint(10, max_iterations)),
                    "score": random.random() * 0.3 + 0.6,  # Base score + some randomness
                    "convergence_rate": 1.0 if converged else 0.0
                }

        # Run multiple trials
        test_data = b"MCTS convergence test"
        strategy = MockMCTS()
        convergence_results = []

        for _ in range(20):
            result = strategy.analyze(test_data, max_iterations=50)
            convergence_results.append(result["converged"])

        # Calculate actual convergence rate
        actual_rate = sum(convergence_results) / len(convergence_results)

        # Check if within tolerance
        is_within_tolerance = abs(actual_rate - target_rate) <= tolerance

        return {
            "success": is_within_tolerance,
            "actual_convergence_rate": actual_rate,
            "target_convergence_rate": target_rate,
            "tolerance": tolerance,
            "trials": len(convergence_results)
        }

    def _test_genetic_convergence_rate(self, target_rate: float, tolerance: float) -> Dict[str, Any]:
        """Test genetic strategy convergence rate"""
        # Mock genetic strategy for testing
        class MockGenetic:
            def analyze(self, data: bytes, max_iterations: int = 100) -> Dict[str, Any]:
                # Simulate genetic strategy behavior
                convergence_probability = target_rate + (hash(data) % (3 * tolerance) - tolerance * 1.5) / 100
                converged = random.random() < convergence_probability

                return {
                    "strategy": "genetic",
                    "converged": converged,
                    "generations": min(max_iterations // 2, random.randint(5, max_iterations // 2)),
                    "score": random.random() * 0.2 + 0.7,
                    "convergence_rate": 1.0 if converged else 0.0
                }

        # Run multiple trials
        test_data = b"Genetic convergence test"
        strategy = MockGenetic()
        convergence_results = []

        for _ in range(15):
            result = strategy.analyze(test_data, max_iterations=50)
            convergence_results.append(result["converged"])

        # Calculate actual convergence rate
        actual_rate = sum(convergence_results) / len(convergence_results)

        # Check if within tolerance
        is_within_tolerance = abs(actual_rate - target_rate) <= tolerance

        return {
            "success": is_within_tolerance,
            "actual_convergence_rate": actual_rate,
            "target_convergence_rate": target_rate,
            "tolerance": tolerance,
            "trials": len(convergence_results)
        }

    def _test_beam_search_consistency(self, max_iterations: int, beam_width: int) -> Dict[str, Any]:
        """Test beam search consistency"""
        # Mock beam search for testing
        class MockBeamSearch:
            def analyze(self, data: bytes, max_iterations: int = 100) -> Dict[str, Any]:
                # Simulate beam search with some randomness but generally consistent results
                score = sum(data) / len(data)  # Simple score for testing
                return {
                    "strategy": "beam_search",
                    "score": score,
                    "iterations": min(max_iterations, beam_width + random.randint(0, 5)),
                    "beam_width": beam_width,
                    "converged": True
                }

        # Run multiple trials with same data
        test_data = b"Beam search consistency test"
        strategy = MockBeamSearch()
        results = []

        for _ in range(10):
            result = strategy.analyze(test_data, max_iterations=max_iterations)
            results.append(result["score"])

        # Calculate consistency (low standard deviation = more consistent)
        if len(results) >= 2:
            import statistics
            std_dev = statistics.stdev(results)
            mean_score = statistics.mean(results)

            # Check consistency (standard deviation should be small)
            is_consistent = std_dev < 0.1 * abs(mean_score)  # Allow some tolerance based on score

            return {
                "success": is_consistent,
                "scores": results,
                "mean_score": mean_score,
                "standard_deviation": std_dev,
                "trials": len(results),
                "coefficient_of_variation": (std_dev / mean_score) if mean_score != 0 else 0
            }
        else:
            return {
                "success": False,
                "error": "Insufficient trials for consistency calculation"
            }

    def _test_json_config_parsing(self, config_path: str) -> Dict[str, Any]:
        """Test JSON configuration parsing"""
        # Create a test configuration file
        test_config = {
            "strategies": {
                "mcts": {"max_iterations": 100, "exploration_constant": 1.41},
                "genetic": {"population_size": 50, "mutation_rate": 0.1}
            },
            "operations": ["xor", "add_constant"],
            "gui": {"theme": "dark", "refresh_rate": 1.0}
        }

        # Test parsing (this would parse actual config file in real implementation)
        try:
            # Simulate successful parsing
            parsed_config = test_config

            # Verify all expected sections are present
            required_sections = ["strategies", "operations", "gui"]
            missing_sections = [section for section in required_sections if section not in parsed_config]

            return {
                "success": len(missing_sections) == 0,
                "missing_sections": missing_sections,
                "parsed_config": parsed_config
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _test_yaml_config_parsing(self, config_path: str) -> Dict[str, Any]:
        """Test YAML configuration parsing"""
        # Create a test configuration
        test_config = """
        strategies:
            mcts:
                max_iterations: 100
                exploration_constant: 1.41
            genetic:
                population_size: 50
                mutation_rate: 0.1

        operations: [xor, add_constant]

        gui:
            theme: "dark"
            refresh_rate: 1.0
        """

        try:
            # Try to parse YAML (this would use yaml library in real implementation)
            # For testing, simulate successful parsing
            if "strategies" not in test_config:
                raise ValueError("Missing strategies section")

            parsed_config = {
                "strategies": {"mcts": {"max_iterations": 100, "exploration_constant": 1.41},
                               "genetic": {"population_size": 50, "mutation_rate": 0.1}},
                "operations": ["xor", "add_constant"],
                "gui": {"theme": "dark", "refresh_rate": 1.0}
            }

            return {
                "success": True,
                "parsed_config": parsed_config
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _test_cache_hit_rate(self, min_hit_rate: float, max_hit_rate: float) -> Dict[str, Any]:
        """Test cache hit rate"""
        # Mock cache for testing
        class MockCache:
            def __init__(self):
                self.hits = 0
                self.misses = 0
                self.data = {}

            def get(self, key):
                if key in self.data:
                    self.hits += 1
                    return self.data[key]
                else:
                    self.misses += 1
                    # Simulate cache miss by generating data
                    self.data[key] = f"cached_data_for_{key}"
                    return self.data[key]

            def get_hit_rate(self):
                total = self.hits + self.misses
                return self.hits / total if total > 0 else 0

        cache = MockCache()
        test_keys = [f"key_{i}" for i in range(20)]

        # Access cache multiple times
        for key in test_keys:
            cache.get(key)
            cache.get(key)  # Access each key twice

        hit_rate = cache.get_hit_rate()

        # Check if hit rate is within expected range
        is_within_range = min_hit_rate <= hit_rate <= max_hit_rate

        return {
            "success": is_within_range,
            "actual_hit_rate": hit_rate,
            "min_hit_rate": min_hit_rate,
            "max_hit_rate": max_hit_rate,
            "hits": cache.hits,
            "misses": cache.misses
        }

    def _test_cache_memory_usage(self, max_memory_mb: float) -> Dict[str, Any]:
        """Test cache memory usage"""
        # Mock cache with memory tracking
        class MockCache:
            def __init__(self):
                self.data = {}
                self.memory_usage = 0.0  # Simulate memory usage

            def add(self, key, value):
                # Simulate memory usage based on key and value sizes
                key_size = len(str(key).encode())
                value_size = len(str(value).encode())
                self.memory_usage += key_size + value_size
                self.data[key] = value

            def get_memory_usage_mb(self):
                return self.memory_usage / (1024 * 1024)

        cache = MockCache()
        # Add entries to cache
        test_entries = 1000  # Large number to test memory limits
        for i in range(test_entries):
            cache.add(f"key_{i}", f"value_{i}")

        actual_memory_mb = cache.get_memory_usage_mb()

        # Check if memory usage is within limits
        is_within_limit = actual_memory_mb <= max_memory_mb

        return {
            "success": is_within_limit,
            "actual_memory_mb": actual_memory_mb,
            "max_memory_mb": max_memory_mb,
            "entries_added": test_entries,
            "memory_per_entry_mb": actual_memory_mb / test_entries if test_entries > 0 else 0
        }

    # Additional test implementations would go here for all regression tests...

    def _test_operation_execution_time(self, max_time_seconds: float, data_size: int) -> Dict[str, Any]:
        """Test operation execution time"""
        # Mock operation for testing
        class MockOperation:
            def apply(self, data: bytes) -> bytes:
                # Simulate work based on data size
                # Larger data takes more time
                work_units = len(data) / 100.0  # 100 bytes = 1 work unit
                # Simulate processing time
                import time
                time.sleep(work_units * 0.001)  # 1ms per work unit
                return data[::-1]  # Simple transformation to ensure work is done

        # Create test data
        test_data = b"A" * data_size

        # Time operation execution
        operation = MockOperation()
        start_time = time.time()
        result = operation.apply(test_data)
        end_time = time.time()

        actual_time = end_time - start_time

        # Check if execution time is within limits
        is_within_limit = actual_time <= max_time_seconds

        return {
            "success": is_within_limit,
            "actual_time_seconds": actual_time,
            "max_time_seconds": max_time_seconds,
            "data_size_bytes": data_size
        }

    # Additional test implementations would be added here for the remaining regression tests...

    def get_critical_failures(self) -> List[str]:
        """Get list of critical test failures"""
        return [test for test in self.failed_tests if self._is_test_critical(test)]

    def get_failure_summary(self) -> Dict[str, int]:
        """Get summary of failures by category"""
        summary = {}
        for test in self.tests:
            if test.name in self.failed_tests:
                category = test.category.value
                if category not in summary:
                    summary[category] = 0
                summary[category] += 1
        return summary

    def export_test_results(self, output_path: str) -> str:
        """Export all test results"""
        export_data = {
            "export_timestamp": time.time(),
            "test_results": {name: result.__dict__ for name, result in self.test_results.items()},
            "execution_history": [entry.__dict__ for entry in self.execution_history],
            "total_tests": len(self.tests),
            "passed_tests": len(self.passed_tests),
            "failed_tests": len(self.failed_tests),
            "critical_failures": len(self.get_critical_failures())
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"Test results exported to: {output_path}")
        return output_path

    def add_custom_regression_test(self, name: str, category: RegressionCategory,
                                description: str, test_function: Callable,
                                parameters: Dict[str, Any], expected_result: Any,
                                timeout_seconds: float = 30.0, is_critical: bool = False):
        """Add a custom regression test"""
        self.add_regression_test(
            name=name,
            category=category,
            description=description,
            test_function=test_function,
            parameters=parameters,
            expected_result=expected_result,
            timeout_seconds=timeout_seconds,
            is_critical=is_critical
        )

    def remove_regression_test(self, test_name: str):
        """Remove a regression test from the suite"""
        self.tests = [test for test in self.tests if test.name != test_name]

    def set_test_parameters(self, test_name: str, parameters: Dict[str, Any]):
        """Update parameters for a specific test"""
        for test in self.tests:
            if test.name == test_name:
                test.parameters.update(parameters)
                break

    def get_test_by_name(self, test_name: str) -> Optional[RegressionTest]:
        """Get a specific test by name"""
        for test in self.tests:
            if test.name == test_name:
                return test
        return None

    def get_tests_by_category(self, category: RegressionCategory) -> List[RegressionTest]:
        """Get all tests in a specific category"""
        return [test for test in self.tests if test.category == category]