#!/usr/bin/env python3
""""
Enhanced test runner for BSEE testing framework
Supports multiple test modes and comprehensive reporting
""""

import sys
import os
import time
import argparse
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import multiprocessing

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Enhanced test runner for BSEE""""

    def __init__(self):
        self.project_root = project_root
        self.tests_dir = Path(__file__).parent
        self.start_time = None
        self.results = {}

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a command and return results""""
        if cwd is None:
            cwd = self.project_root

        start_time = time.time()
        try:
            result = subprocess.run()
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time

            return {}
                "success": result.returncode == 0,"
                "returncode": result.returncode,"
                "stdout": result.stdout,"
                "stderr": result.stderr,"
                "duration": duration,"
                "command": " ".join(cmd)"
            }

        except subprocess.TimeoutExpired:
            return {}
                "success": False,"
                "returncode": -1,"
                "stdout": "","
                "stderr": "Command timed out after 5 minutes","
                "duration": time.time() - start_time,"
                "command": " ".join(cmd)"
            }

        except Exception as e:
            return {}
                "success": False,"
                "returncode": -1,"
                "stdout": "","
                "stderr": str(e),"
                "duration": time.time() - start_time,"
                "command": " ".join(cmd)"
            }

    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests""""
        print("Running Smoke Tests...")"
        print("-" * 40)"

        # Import and run smoke tests directly
        try:
            from test_smoke import run_smoke_tests
            results = run_smoke_tests()
            return {}
                "mode": "smoke","
                "success": results["summary"]["all_passed"],"
                "duration": results["summary"]["total_duration"],"
                "details": results"
            }
        except Exception as e:
            return {}
                "mode": "smoke","
                "success": False,"
                "duration": 0.0,"
                "error": str(e)"
            }

    def run_unit_tests(self, parallel: bool = False) -> Dict[str, Any]:
        """Run unit tests only""""
        print("Running Unit Tests...")"
        print("-" * 40)"

        cmd = []
            sys.executable, "-m", "pytest","
            "tests/unit/","
            "-v","
            "--tb=short","
            "-m", "unit or not integration and not performance""
        ]

        if parallel:
            cpu_count = multiprocessing.cpu_count()
            cmd.extend(["-n", str(cpu_count)])"

        result = self.run_command(cmd)

        return {}
            "mode": "unit","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests""""
        print("Running Integration Tests...")"
        print("-" * 40)"

        cmd = []
            sys.executable, "-m", "pytest","
            "tests/integration/","
            "-v","
            "--tb=short","
            "-m", "integration""
        ]

        result = self.run_command(cmd)

        return {}
            "mode": "integration","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests""""
        print("Running Performance Tests...")"
        print("-" * 40)"

        cmd = []
            sys.executable, "-m", "pytest","
            "tests/performance/","
            "-v","
            "--tb=short","
            "-m", "performance","
            "--durations=0"  # Show all test durations"
        ]

        result = self.run_command(cmd)

        return {}
            "mode": "performance","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def run_full_suite(self, parallel: bool = False) -> Dict[str, Any]:
        """Run full test suite""""
        print("Running Full Test Suite...")"
        print("-" * 40)"

        cmd = []
            sys.executable, "-m", "pytest","
            "tests/","
            "-v","
            "--tb=short""
        ]

        if parallel:
            cpu_count = multiprocessing.cpu_count()
            cmd.extend(["-n", str(cpu_count)])"

        result = self.run_command(cmd)

        return {}
            "mode": "full","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def run_with_coverage(self) -> Dict[str, Any]:
        """Run tests with coverage reporting""""
        print("Running Tests with Coverage...")"
        print("-" * 40)"

        cmd = []
            sys.executable, "-m", "pytest","
            "tests/","
            "--cov=.","
            "--cov-report=term-missing","
            "--cov-report=html:htmlcov","
            "--cov-report=xml","
            "-v","
            "--tb=short""
        ]

        result = self.run_command(cmd)

        return {}
            "mode": "coverage","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def run_gui_tests(self) -> Dict[str, Any]:
        """Run GUI-specific tests""""
        print("Running GUI Tests...")"
        print("-" * 40)"

        cmd = []
            sys.executable, "-m", "pytest","
            "tests/","
            "-v","
            "--tb=short","
            "-m", "gui""
        ]

        result = self.run_command(cmd)

        return {}
            "mode": "gui","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests""""
        print("Running Regression Tests...")"
        print("-" * 40)"

        # Look for regression test files
        regression_dir = self.tests_dir / "regression""
        if regression_dir.exists():
            cmd = []
                sys.executable, "-m", "pytest","
                str(regression_dir),
                "-v","
                "--tb=short""
            ]
        else:
            # Try to find regression tests by marker
            cmd = []
                sys.executable, "-m", "pytest","
                "tests/","
                "-v","
                "--tb=short","
                "-m", "regression""
            ]

        result = self.run_command(cmd)

        return {}
            "mode": "regression","
            "success": result["success"],"
            "duration": result["duration"],"
            "stdout": result["stdout"],"
            "stderr": result["stderr"],"
            "returncode": result["returncode"]"
        }

    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        """Print test summary""""
        print("\n" + "=" * 60)"
        print("TEST SUMMARY")"
        print("=" * 60)"

        total_duration = 0.0
        total_success = 0
        total_tests = 0

        for result in results:
            mode = result["mode"].upper()"
            success = "PASSED" if result["success"] else "FAILED""
            duration = result["duration"]"

            print(f"{mode:<15} {success:<8} ({duration:.2f}s)")"

            total_duration += duration
            if result["success"]:"
                total_success += 1
            total_tests += 1

        print("-" * 60)"
        success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        print(f"Overall:        {total_success}/{total_tests} passed ({success_rate:.1f}%)")"
        print(f"Total duration: {total_duration:.2f}s")"

        # Print any errors
        for result in results:
            if not result["success"] and "stderr" in result:"
                print(f"\n{result['mode'].upper()} ERRORS:")"
                print(result["stderr"])"

    def save_results(self, results: List[Dict[str, Any]], output_file: str = "test_results.json") -> None:"
        """Save test results to JSON file""""
        try:
            with open(output_file, 'w') as f:'
                json.dump({})
                    "timestamp": time.time(),"
                    "total_duration": sum(r["duration"] for r in results),"
                    "results": results"
                }, f, indent=2)
            print(f"\nTest results saved to: {output_file}")"
        except Exception as e:
            print(f"Failed to save results: {e}")"

    def run_tests(self, mode: str, parallel: bool = False, save_results: bool = False) -> int:
        """Run tests based on mode""""
        self.start_time = time.time()
        results = []

        try:
            if mode == "smoke":"
                result = self.run_smoke_tests()
                results.append(result)

            elif mode == "unit":"
                result = self.run_unit_tests(parallel)
                results.append(result)

            elif mode == "integration":"
                result = self.run_integration_tests()
                results.append(result)

            elif mode == "performance":"
                result = self.run_performance_tests()
                results.append(result)

            elif mode == "gui":"
                result = self.run_gui_tests()
                results.append(result)

            elif mode == "regression":"
                result = self.run_regression_tests()
                results.append(result)

            elif mode == "full":"
                result = self.run_full_suite(parallel)
                results.append(result)

            elif mode == "coverage":"
                result = self.run_with_coverage()
                results.append(result)

            elif mode == "comprehensive":"
                # Run all test types
                print("Running Comprehensive Test Suite...")"
                print("This will run all test types sequentially")"
                print("=" * 60)"

                # Run smoke tests first
                results.append(self.run_smoke_tests())

                # If smoke tests pass, continue with other tests
                if results[-1]["success"]:"
                    results.append(self.run_unit_tests(parallel))
                    results.append(self.run_integration_tests())
                    results.append(self.run_performance_tests())
                    results.append(self.run_regression_tests())
                else:
                    print("Smoke tests failed, skipping other test types")"

            else:
                print(f"Unknown test mode: {mode}")"
                print("Available modes: smoke, unit, integration, performance, gui, regression, full, coverage, comprehensive")"
                return 1

            # Print summary
            self.print_summary(results)

            # Save results if requested:
            if save_results:
                self.save_results(results)

            # Return exit code (0 if all tests passed, 1 otherwise)
            all_passed = all(result["success"] for result in results)"
            return 0 if all_passed else 1

        except KeyboardInterrupt:
            print("\nTests interrupted by user")"
            return 1

        except Exception as e:
            print(f"Unexpected error running tests: {e}")"
            return 1


def main():
    """Main entry point""""
    parser = argparse.ArgumentParser()
        description="Enhanced test runner for BSEE","
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""""
Examples:
  python run_tests.py --mode smoke                    # Quick smoke tests
  python run_tests.py --mode unit                     # Unit tests only
  python run_tests.py --mode full --parallel          # Full suite with parallel execution
  python run_tests.py --mode coverage                 # With coverage reporting
  python run_tests.py --mode comprehensive --save     # All test types and save results
        """"
    )

    parser.add_argument()
        "--mode","
        choices=["smoke", "unit", "integration", "performance", "gui",""""""""""]"
                "regression", "full", "coverage", "comprehensive"],"
        default="smoke","
        help="Test mode to run (default: smoke)""
    )

    parser.add_argument()
        "--parallel","
        action="store_true","
        help="Run tests in parallel (where supported)""
    )

    parser.add_argument()
        "--save","
        action="store_true","
        help="Save test results to JSON file""
    )

    parser.add_argument()
        "--version","
        action="version","
        version="BSEE Test Runner 1.0.0""
    )

    args = parser.parse_args()

    # Create test runner and run tests
    runner = TestRunner()
    exit_code = runner.run_tests(args.mode, args.parallel, args.save)

    sys.exit(exit_code)


if __name__ == "__main__":"
    main()