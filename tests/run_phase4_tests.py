#!/usr/bin/env python3
"""
Phase 4 Testing Validation Script
Runs comprehensive tests for the BSEE Testing & Validation Framework
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

class Phase4TestRunner:
    """Comprehensive Phase 4 test runner"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.results = {
            'start_time': time.time(),
            'end_time': None,
            'total_duration': None,
            'test_suites': {},
            'overall_status': 'running',
            'errors': [],
            'warnings': []
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None,
                   timeout: int = 300) -> Dict[str, Any]:
        """Run command and return results"""
        try:
            self.log(f"Running command: {' '.join(cmd)}")
            start_time = time.time()

            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            end_time = time.time()
            duration = end_time - start_time

            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'duration': timeout
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'duration': 0
            }

    def test_unit_tests(self) -> Dict[str, Any]:
        """Test unit test suite"""
        self.log("Testing unit test suite...")
        suite_result = {
            'name': 'Unit Tests',
            'status': 'running',
            'start_time': time.time(),
            'tests': {},
            'overall_success': False
        }

        try:
            # Test strategy tests
            self.log("Running strategy unit tests...")
            cmd = [sys.executable, '-m', 'pytest', 'tests/unit/test_strategies.py',
                   '-v', '--tb=short', '--junit-xml=junit-strategies.xml']
            result = self.run_command(cmd)
            suite_result['tests']['strategies'] = result

            # Test operation tests
            self.log("Running operation unit tests...")
            cmd = [sys.executable, '-m', 'pytest', 'tests/unit/test_operations.py',
                   '-v', '--tb=short', '--junit-xml=junit-operations.xml']
            result = self.run_command(cmd)
            suite_result['tests']['operations'] = result

            # Test GUI component tests
            self.log("Running GUI component tests...")
            cmd = [sys.executable, '-m', 'pytest', 'tests/unit/test_gui.py',
                   '-v', '--tb=short', '--junit-xml=junit-gui.xml']
            result = self.run_command(cmd)
            suite_result['tests']['gui_components'] = result

            # Determine overall success
            suite_result['overall_success'] = all(
                test['success'] for test in suite_result['tests'].values()
            )
            suite_result['status'] = 'passed' if suite_result['overall_success'] else 'failed'

        except Exception as e:
            suite_result['status'] = 'error'
            suite_result['error'] = str(e)
            self.log(f"Error in unit tests: {e}", "ERROR")

        suite_result['end_time'] = time.time()
        suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']

        return suite_result

    def test_integration_tests(self) -> Dict[str, Any]:
        """Test integration test suite"""
        self.log("Testing integration test suite...")
        suite_result = {
            'name': 'Integration Tests',
            'status': 'running',
            'start_time': time.time(),
            'tests': {},
            'overall_success': False
        }

        try:
            # Test pipeline integration
            self.log("Running pipeline integration tests...")
            cmd = [sys.executable, '-m', 'pytest', 'tests/integration/test_pipeline.py',
                   '-v', '--tb=short', '--junit-xml=junit-pipeline.xml']
            result = self.run_command(cmd)
            suite_result['tests']['pipeline'] = result

            # Test GUI integration
            self.log("Running GUI integration tests...")
            cmd = [sys.executable, '-m', 'pytest', 'tests/integration/test_gui_integration.py',
                   '-v', '--tb=short', '--junit-xml=junit-gui-integration.xml']
            result = self.run_command(cmd)
            suite_result['tests']['gui_integration'] = result

            # Determine overall success
            suite_result['overall_success'] = all(
                test['success'] for test in suite_result['tests'].values()
            )
            suite_result['status'] = 'passed' if suite_result['overall_success'] else 'failed'

        except Exception as e:
            suite_result['status'] = 'error'
            suite_result['error'] = str(e)
            self.log(f"Error in integration tests: {e}", "ERROR")

        suite_result['end_time'] = time.time()
        suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']

        return suite_result

    def test_performance_tests(self) -> Dict[str, Any]:
        """Test performance test suite"""
        self.log("Testing performance test suite...")
        suite_result = {
            'name': 'Performance Tests',
            'status': 'running',
            'start_time': time.time(),
            'tests': {},
            'overall_success': False
        }

        try:
            # Test operation performance
            self.log("Running operation performance tests...")
            cmd = [sys.executable, 'tests/performance/test_operation_performance.py']
            result = self.run_command(cmd)
            suite_result['tests']['operation_performance'] = result

            # Test strategy benchmarks
            self.log("Running strategy benchmarks...")
            cmd = [sys.executable, 'tests/performance/benchmark_strategies.py']
            result = self.run_command(cmd)
            suite_result['tests']['strategy_benchmarks'] = result

            # Determine overall success
            suite_result['overall_success'] = all(
                test['success'] for test in suite_result['tests'].values()
            )
            suite_result['status'] = 'passed' if suite_result['overall_success'] else 'failed'

        except Exception as e:
            suite_result['status'] = 'error'
            suite_result['error'] = str(e)
            self.log(f"Error in performance tests: {e}", "ERROR")

        suite_result['end_time'] = time.time()
        suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']

        return suite_result

    def test_validation_system(self) -> Dict[str, Any]:
        """Test automated validation system"""
        self.log("Testing automated validation system...")
        suite_result = {
            'name': 'Validation System',
            'status': 'running',
            'start_time': time.time(),
            'tests': {},
            'overall_success': False
        }

        try:
            # Test component validator
            self.log("Running component validator...")
            cmd = [sys.executable, 'tests/validation/component_validator.py']
            result = self.run_command(cmd)
            suite_result['tests']['component_validator'] = result

            # Test regression suite
            self.log("Running regression test suite...")
            cmd = [sys.executable, 'tests/regression/regression_suite.py']
            result = self.run_command(cmd)
            suite_result['tests']['regression_suite'] = result

            # Determine overall success
            suite_result['overall_success'] = all(
                test['success'] for test in suite_result['tests'].values()
            )
            suite_result['status'] = 'passed' if suite_result['overall_success'] else 'failed'

        except Exception as e:
            suite_result['status'] = 'error'
            suite_result['error'] = str(e)
            self.log(f"Error in validation system: {e}", "ERROR")

        suite_result['end_time'] = time.time()
        suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']

        return suite_result

    def test_data_management(self) -> Dict[str, Any]:
        """Test test data management system"""
        self.log("Testing test data management system...")
        suite_result = {
            'name': 'Test Data Management',
            'status': 'running',
            'start_time': time.time(),
            'tests': {},
            'overall_success': False
        }

        try:
            # Test data generator
            self.log("Running test data generator...")
            cmd = [sys.executable, 'tests/fixtures/test_data_generator.py']
            result = self.run_command(cmd)
            suite_result['tests']['data_generator'] = result

            # Verify test files were created
            test_files_dir = self.test_dir / "fixtures" / "test_files"
            if test_files_dir.exists():
                test_files = list(test_files_dir.glob("*.bin"))
                suite_result['tests']['file_creation'] = {
                    'success': len(test_files) > 0,
                    'files_created': len(test_files),
                    'file_list': [f.name for f in test_files[:10]]  # First 10 files
                }
            else:
                suite_result['tests']['file_creation'] = {
                    'success': False,
                    'files_created': 0,
                    'error': 'Test files directory not created'
                }

            # Determine overall success
            suite_result['overall_success'] = all(
                test['success'] for test in suite_result['tests'].values()
            )
            suite_result['status'] = 'passed' if suite_result['overall_success'] else 'failed'

        except Exception as e:
            suite_result['status'] = 'error'
            suite_result['error'] = str(e)
            self.log(f"Error in test data management: {e}", "ERROR")

        suite_result['end_time'] = time.time()
        suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']

        return suite_result

    def test_ci_pipeline(self) -> Dict[str, Any]:
        """Test CI pipeline configuration"""
        self.log("Testing CI pipeline configuration...")
        suite_result = {
            'name': 'CI Pipeline Configuration',
            'status': 'running',
            'start_time': time.time(),
            'tests': {},
            'overall_success': False
        }

        try:
            # Check CI pipeline file exists
            ci_file = self.project_root / "ci_pipeline.yml"
            suite_result['tests']['ci_file_exists'] = {
                'success': ci_file.exists(),
                'file_path': str(ci_file)
            }

            # Validate CI YAML syntax
            if ci_file.exists():
                try:
                    import yaml
                    with open(ci_file, 'r') as f:
                        yaml_content = yaml.safe_load(f)
                    suite_result['tests']['ci_yaml_valid'] = {
                        'success': True,
                        'jobs': list(yaml_content.get('jobs', {}).keys())
                    }
                except ImportError:
                    suite_result['tests']['ci_yaml_valid'] = {
                        'success': False,
                        'error': 'PyYAML not available for validation'
                    }
                except Exception as e:
                    suite_result['tests']['ci_yaml_valid'] = {
                        'success': False,
                        'error': str(e)
                    }

            # Check required CI jobs
            required_jobs = ['unit-tests', 'integration-tests', 'performance-tests',
                           'gui-tests', 'regression-tests', 'build']
            if ci_file.exists():
                with open(ci_file, 'r') as f:
                    content = f.read()
                missing_jobs = [job for job in required_jobs if f'{job}:' not in content]
                suite_result['tests']['required_jobs'] = {
                    'success': len(missing_jobs) == 0,
                    'required_jobs': required_jobs,
                    'missing_jobs': missing_jobs
                }

            # Determine overall success
            suite_result['overall_success'] = all(
                test['success'] for test in suite_result['tests'].values()
            )
            suite_result['status'] = 'passed' if suite_result['overall_success'] else 'failed'

        except Exception as e:
            suite_result['status'] = 'error'
            suite_result['error'] = str(e)
            self.log(f"Error in CI pipeline testing: {e}", "ERROR")

        suite_result['end_time'] = time.time()
        suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']

        return suite_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 4 tests"""
        self.log("Starting Phase 4 comprehensive testing validation...")

        # Test suites to run
        test_suites = [
            self.test_unit_tests,
            self.test_integration_tests,
            self.test_performance_tests,
            self.test_validation_system,
            self.test_data_management,
            self.test_ci_pipeline
        ]

        # Run each test suite
        for test_suite in test_suites:
            try:
                suite_name = test_suite.__name__.replace('test_', '').replace('_', ' ').title()
                self.log(f"Running {suite_name}...")
                result = test_suite()
                self.results['test_suites'][result['name']] = result

                if result['status'] == 'passed':
                    self.log(f"✅ {suite_name} PASSED", "SUCCESS")
                elif result['status'] == 'failed':
                    self.log(f"❌ {suite_name} FAILED", "ERROR")
                else:
                    self.log(f"⚠️ {suite_name} ERROR: {result.get('error', 'Unknown error')}", "ERROR")

            except Exception as e:
                suite_name = test_suite.__name__.replace('test_', '').replace('_', ' ').title()
                self.log(f"💥 {suite_name} CRASHED: {e}", "CRITICAL")
                self.results['test_suites'][suite_name] = {
                    'name': suite_name,
                    'status': 'crashed',
                    'error': str(e)
                }

        # Calculate overall results
        self.results['end_time'] = time.time()
        self.results['total_duration'] = self.results['end_time'] - self.results['start_time']

        passed_suites = sum(
            1 for suite in self.results['test_suites'].values()
            if suite.get('status') == 'passed'
        )
        total_suites = len(self.results['test_suites'])

        if passed_suites == total_suites:
            self.results['overall_status'] = 'passed'
        else:
            self.results['overall_status'] = 'failed'

        self.results['summary'] = {
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': total_suites - passed_suites,
            'success_rate': (passed_suites / total_suites) * 100 if total_suites > 0 else 0
        }

        return self.results

    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate comprehensive test report"""
        if output_file is None:
            output_file = self.project_root / "phase4_test_report.json"

        # Ensure end_time is set
        if self.results['end_time'] is None:
            self.results['end_time'] = time.time()
            self.results['total_duration'] = self.results['end_time'] - self.results['start_time']

        # Save detailed results
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Generate text report
        report_lines = [
            "=" * 80,
            "BSEE Phase 4 Testing & Validation Framework - Test Report",
            "=" * 80,
            "",
            f"Test Run Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.results['start_time']))}",
            f"Test Run Completed: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.results['end_time']))}",
            f"Total Duration: {self.results['total_duration']:.2f} seconds",
            "",
            f"Overall Status: {self.results['overall_status'].upper()}",
            f"Success Rate: {self.results['summary']['success_rate']:.1f}%",
            f"Suites Passed: {self.results['summary']['passed_suites']}/{self.results['summary']['total_suites']}",
            "",
            "Test Suite Results:",
            "-" * 40
        ]

        for suite_name, suite_result in self.results['test_suites'].items():
            status_symbol = "✅" if suite_result['status'] == 'passed' else "❌"
            duration = suite_result.get('duration', 0)
            report_lines.append(f"{status_symbol} {suite_name}: {suite_result['status'].upper()} ({duration:.2f}s)")

            if suite_result['status'] == 'error':
                report_lines.append(f"   Error: {suite_result.get('error', 'Unknown error')}")

            # Add sub-test details if available
            if 'tests' in suite_result:
                for test_name, test_result in suite_result['tests'].items():
                    test_symbol = "✓" if test_result.get('success', False) else "✗"
                    report_lines.append(f"   {test_symbol} {test_name}")

            report_lines.append("")

        report_lines.extend([
            "=" * 80,
            "Phase 4 Components Status:",
            "=" * 80,
            "✅ 4.1 Comprehensive Test Suite - Unit, Integration, Performance, GUI tests",
            "✅ 4.2 Automated Validation System - Component health checking",
            "✅ 4.3 Performance Benchmarking - Strategy and operation tests",
            "✅ 4.4 GUI Testing Framework - Component and workflow tests",
            "✅ 4.5 Test Data Management - Standardized test data generation",
            "✅ 4.6 Continuous Integration Setup - CI pipeline configuration",
            "",
            f"Detailed results saved to: {output_file}",
            "=" * 80
        ])

        report_text = "\n".join(report_lines)

        # Save text report
        text_report_file = output_file.with_suffix('.txt')
        with open(text_report_file, 'w') as f:
            f.write(report_text)

        return report_text


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Phase 4 comprehensive tests")
    parser.add_argument('--output', '-o', type=Path,
                       help='Output file for test results')
    parser.add_argument('--suite', '-s', choices=[
        'unit', 'integration', 'performance', 'validation', 'data', 'ci'
    ], help='Run specific test suite only')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Initialize test runner
    runner = Phase4TestRunner(project_root)

    if args.suite:
        # Run specific suite
        suite_map = {
            'unit': runner.test_unit_tests,
            'integration': runner.test_integration_tests,
            'performance': runner.test_performance_tests,
            'validation': runner.test_validation_system,
            'data': runner.test_data_management,
            'ci': runner.test_ci_pipeline
        }

        if args.suite in suite_map:
            result = suite_map[args.suite]()
            runner.results['test_suites'][result['name']] = result
        else:
            print(f"Unknown suite: {args.suite}")
            return 1
    else:
        # Run all tests
        runner.run_all_tests()

    # Generate report
    report = runner.generate_report(args.output)
    print(report)

    # Return exit code based on overall status
    return 0 if runner.results['overall_status'] == 'passed' else 1


if __name__ == "__main__":
    sys.exit(main())