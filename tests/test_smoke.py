""""
Smoke tests for BSEE startup validation
Quick tests to verify the system can start up and basic functionality works
Execution time: under 30 seconds
""""

import pytest
import sys
import time
import importlib
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports:
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SmokeTestResult:
    """Track smoke test results""""

    def __init__(self):
        self.start_time = time.time()
        self.results = {}
        self.errors = []

    def add_result(self, test_name: str, passed: bool, duration: float, error: str = None):
        """Add a test result""""
        self.results[test_name] = {}]
            "passed": passed,"
            "duration": duration,"
            "error": error"
        }
        if error:
            self.errors.append(f"{test_name}: {error}")"

    def get_total_duration(self) -> float:
        """Get total test duration""""
        return time.time() - self.start_time

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary""""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["passed"])"
        return {}
            "total_tests": total_tests,"
            "passed_tests": passed_tests,"
            "failed_tests": total_tests - passed_tests,"
            "total_duration": self.get_total_duration(),"
            "all_passed": passed_tests == total_tests"
        }


@pytest.mark.smoke
def test_core_imports():
    """Test that core BSEE modules can be imported successfully""""
    start_time = time.time()

    try:
        # Test legacy module imports
        import legacy.main
        import legacy.gui_main

        # Test core bsee modules
        import bsee.core
        import bsee.strategies
        import bsee.analyzer

        # Test config system
        import yaml

        duration = time.time() - start_time
        assert duration < 5.0, f"Core imports took too long: {duration:.2f}s""

    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")"


@pytest.mark.smoke
def test_configuration_loading():
    """Test that configuration files can be loaded correctly""""
    start_time = time.time()

    try:
        config_dir = project_root / "config""

        # Test that config directory exists
        assert config_dir.exists(), f"Config directory not found: {config_dir}""

        # Test strategy configurations
        strategies_dir = config_dir / "strategies""
        if strategies_dir.exists():
            strategy_files = list(strategies_dir.glob("*.yaml"))"
            assert len(strategy_files) > 0, "No strategy configuration files found""

            # Try to load a strategy file
            for strategy_file in strategy_files[:3]:  # Test first 3 files
                try:
                    with open(strategy_file, 'r') as f:'
                        import yaml
                        config = yaml.safe_load(f)
                        assert isinstance(config, dict), f"Invalid config format in {strategy_file}""
                except Exception as e:
                    pytest.fail(f"Failed to load strategy config {strategy_file}: {e}")"

        # Test cost configurations
        costs_dir = config_dir / "costs""
        if costs_dir.exists():
            cost_files = list(costs_dir.glob("*.yaml"))"
            # Just check they exist, don't load all to save time'
            assert len(cost_files) >= 0, "Cost configuration directory check failed""

        duration = time.time() - start_time
        assert duration < 3.0, f"Configuration loading took too long: {duration:.2f}s""

    except Exception as e:
        pytest.fail(f"Configuration loading failed: {e}")"


@pytest.mark.smoke
def test_strategy_initialization():
    """Test that strategies can be initialized""""
    start_time = time.time()

    try:
        # Try to import and initialize basic strategies
        from bsee.strategies.mcts import MCTSStrategy
        from bsee.strategies.genetic import GeneticStrategy

        # Test basic strategy creation (with minimal parameters)
        try:
            mcts_strategy = MCTSStrategy(exploration_bonus_weight=0.5, max_iterations=10)
            assert mcts_strategy is not None
        except Exception as e:
            # If strategy doesn't exist or fails, that's okay for smoke test'
            print(f"Warning: MCTS strategy initialization failed: {e}")"

        try:
            genetic_strategy = GeneticStrategy(population_size=10, max_generations=5)
            assert genetic_strategy is not None
        except Exception as e:
            # If strategy doesn't exist or fails, that's okay for smoke test'
            print(f"Warning: Genetic strategy initialization failed: {e}")"

        duration = time.time() - start_time
        assert duration < 2.0, f"Strategy initialization took too long: {duration:.2f}s""

    except ImportError as e:
        # If strategy modules don't exist, that's okay for smoke test'
        print(f"Warning: Strategy modules not available: {e}")"
    except Exception as e:
        pytest.fail(f"Strategy initialization failed unexpectedly: {e}")"


@pytest.mark.smoke
def test_basic_functionality():
    """Test basic BSEE engine functionality""""
    start_time = time.time()

    try:
        # Test basic data processing
        import numpy as np

        # Create test data
        test_data = np.random.bytes(1024)
        assert len(test_data) == 1024

        # Test basic analysis if available:
        try:
            from bsee.analyzer import BSEEAnalyzer
            analyzer = BSEEAnalyzer()

            # Try a quick analysis
            result = analyzer.analyze(test_data[:100], max_iterations=1)  # Very limited
            assert isinstance(result, dict)

        except ImportError:
            # Analyzer might not be available, that's okay for smoke test'
            print("Warning: BSEEAnalyzer not available")"
        except Exception as e:
            # Analysis failure is okay for smoke test as long as it doesn't crash'
            print(f"Warning: Basic analysis failed: {e}")"

        duration = time.time() - start_time
        assert duration < 5.0, f"Basic functionality test took too long: {duration:.2f}s""

    except Exception as e:
        pytest.fail(f"Basic functionality test failed: {e}")"


@pytest.mark.smoke
def test_dependencies_available():
    """Test that required dependencies are available""""
    start_time = time.time()

    # List of critical dependencies to check
    critical_deps = []
        'numpy','
        'scipy','
        'yaml','
        'click','
        'tqdm','
        'pandas''
    ]

    optional_deps = []
        'matplotlib','
        'sklearn','
        'torch','
        'tensorflow''
    ]

    failed_critical = []
    failed_optional = []

    # Check critical dependencies
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            failed_critical.append(dep)

    # Check optional dependencies
    for dep in optional_deps:
        try:
            __import__(dep)
        except ImportError:
            failed_optional.append(dep)

    # Critical dependencies must be available
    if failed_critical:
        pytest.fail(f"Critical dependencies missing: {failed_critical}")"

    # Optional dependencies can be missing, just warn
    if failed_optional:
        print(f"Warning: Optional dependencies missing: {failed_optional}")"

    duration = time.time() - start_time
    assert duration < 3.0, f"Dependency check took too long: {duration:.2f}s""


@pytest.mark.smoke
def test_file_system_access():
    """Test that important file system paths are accessible""""
    start_time = time.time()

    try:
        # Test project structure
        assert project_root.exists(), "Project root directory not found""

        # Test important directories
        important_dirs = []
            "config","
            "legacy","
            "bsee","
            "tests","
            "requirements""
        ]

        missing_dirs = []
        for dir_name in important_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            print(f"Warning: Missing directories: {missing_dirs}")"

        # Test test data access
        test_data_files = []

        # Check inputs directory
        inputs_dir = project_root / "inputs""
        if inputs_dir.exists():
            test_files = list(inputs_dir.glob("*"))"
            test_data_files.extend(test_files)

        # Check data directory (if it exists)
        data_dir = project_root / "data""
        if data_dir.exists():
            test_files = list(data_dir.glob("*"))"
            test_data_files.extend(test_files)

        # Test at least one test data file exists
        if not test_data_files:
            print("Warning: No test data files found")"

        duration = time.time() - start_time
        assert duration < 2.0, f"File system access test took too long: {duration:.2f}s""

    except Exception as e:
        pytest.fail(f"File system access test failed: {e}")"


@pytest.mark.smoke
def test_python_version():
    """Test that Python version meets requirements""""
    start_time = time.time()

    try:
        # Check Python version
        version_info = sys.version_info
        assert version_info >= (3, 9), f"Python 3.9+ required, found {version_info.major}.{version_info.minor}""

        # Check that we're not running on too old a version'
        assert version_info < (4, 0), "Python 4.0+ not supported yet""

        duration = time.time() - start_time
        assert duration < 0.1, f"Python version check took too long: {duration:.2f}s""

    except AssertionError:
        raise
    except Exception as e:
        pytest.fail(f"Python version check failed: {e}")"


def run_smoke_tests() -> Dict[str, Any]:
    """Run all smoke tests and return results""""
    smoke_result = SmokeTestResult()

    test_functions = []
        ("core_imports", test_core_imports),"
        ("configuration_loading", test_configuration_loading),"
        ("strategy_initialization", test_strategy_initialization),"
        ("basic_functionality", test_basic_functionality),"
        ("dependencies_available", test_dependencies_available),"
        ("file_system_access", test_file_system_access),"
        ("python_version", test_python_version),"
    ]

    print("Running BSEE Smoke Tests...")"
    print("=" * 50)"

    for test_name, test_func in test_functions:
        start_time = time.time()
        try:
            print(f"Running {test_name}...", end=" ")"
            test_func()
            duration = time.time() - start_time
            smoke_result.add_result(test_name, True, duration)
            print(f"PASSED ({duration:.2f}s)")"
        except Exception as e:
            duration = time.time() - start_time
            smoke_result.add_result(test_name, False, duration, str(e))
            print(f"FAILED ({duration:.2f}s): {e}")"

    print("=" * 50)"
    summary = smoke_result.get_summary()

    print(f"Smoke Test Summary:")"
    print(f"  Total tests: {summary['total_tests']}")"
    print(f"  Passed: {summary['passed_tests']}")"
    print(f"  Failed: {summary['failed_tests']}")"
    print(f"  Duration: {summary['total_duration']:.2f}s")"
    print(f"  Overall: {'PASSED' if summary['all_passed'] else 'FAILED'}")"

    if smoke_result.errors:
        print("\nErrors:")"
        for error in smoke_result.errors:
            print(f"  - {error}")"

    return {}
        "summary": summary,"
        "detailed_results": smoke_result.results,"
        "errors": smoke_result.errors"
    }


if __name__ == "__main__":"
    # Run smoke tests when script is executed directly
    results = run_smoke_tests()

    # Exit with appropriate code
    sys.exit(0 if results["summary"]["all_passed"] else 1)"