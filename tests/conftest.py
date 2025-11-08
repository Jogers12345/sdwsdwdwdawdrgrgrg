"""
pytest configuration and fixtures for BSEE testing framework
"""

import pytest
import os
import sys
import tempfile
import shutil
import random
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory"""
    return project_root / "tests" / "fixtures" / "test_files"


@pytest.fixture(scope="session")
def test_config_dir():
    """Fixture providing path to test config directory"""
    return project_root / "tests" / "fixtures" / "configs"


@pytest.fixture(scope="session")
def expected_results_dir():
    """Fixture providing path to expected results directory"""
    return project_root / "tests" / "fixtures" / "expected_results"


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def random_seed():
    """Fixture providing a consistent random seed for reproducible tests"""
    return 42


@pytest.fixture
def sample_binary_data():
    """Fixture providing sample binary data for testing"""
    return b"BSEE Test Data: " + bytes(range(256)) * 4


@pytest.fixture
def sample_text_data():
    """Fixture providing sample text data for testing"""
    return "The quick brown fox jumps over the lazy dog. " * 20


@pytest.fixture
def sample_json_data():
    """Fixture providing sample JSON data for testing"""
    return {
        "name": "BSEE Test",
        "version": "1.0.0",
        "operations": ["xor", "add", "subtract"],
        "strategies": ["mcts", "genetic", "beam_search"],
        "metrics": {
            "entropy": 7.5,
            "ideality": 0.8,
            "compression_ratio": 0.6
        }
    }


@pytest.fixture
def mock_operation():
    """Fixture providing a mock operation for testing"""
    class MockOperation:
        def __init__(self, name="mock_op"):
            self.name = name
            self.parameters = {}

        def apply(self, data):
            """Simple mock operation that inverts bits"""
            return bytes(~b & 0xFF for b in data)

        def inverse(self):
            """Return inverse operation"""
            return MockOperation(self.name + "_inverse")

        def __eq__(self, other):
            return isinstance(other, MockOperation) and self.name == other.name

    return MockOperation()


@pytest.fixture
def mock_strategy():
    """Fixture providing a mock strategy for testing"""
    class MockStrategy:
        def __init__(self, name="mock_strategy", config=None):
            self.name = name
            self.config = config or {}

        def analyze(self, data, max_iterations=100):
            """Simple mock analysis that returns basic metrics"""
            return {
                "strategy": self.name,
                "score": random.random(),
                "iterations": min(max_iterations, 50),
                "converged": True,
                "operations_applied": ["mock_op"],
                "final_score": random.uniform(0.5, 1.0)
            }

    return MockStrategy()


@pytest.fixture
def performance_test_config():
    """Fixture providing configuration for performance tests"""
    return {
        "iterations": 10,
        "warmup_iterations": 3,
        "timeout_seconds": 30.0,
        "max_memory_mb": 512.0,
        "min_ops_per_second": 1.0,
        "max_execution_time": 5.0
    }


@pytest.fixture
def gui_test_config():
    """Fixture providing configuration for GUI tests"""
    return {
        "test_delay": 0.1,  # seconds between GUI actions
        "screenshot_on_failure": True,
        "headless_mode": True,
        "timeout_seconds": 10.0
    }


class TestDataGenerator:
    """Utility class for generating test data"""

    @staticmethod
    def generate_random_data(size: int, seed: Optional[int] = None) -> bytes:
        """Generate random binary data"""
        if seed is not None:
            random.seed(seed)
        return bytes([random.randint(0, 255) for _ in range(size)])

    @staticmethod
    def generate_pattern_data(size: int, pattern: bytes) -> bytes:
        """Generate data with repeating pattern"""
        result = bytearray()
        pattern_len = len(pattern)
        for i in range(size):
            result.append(pattern[i % pattern_len])
        return bytes(result)

    @staticmethod
    def generate_structured_data(size: int) -> bytes:
        """Generate structured binary data with headers"""
        header = b"BSEE" + size.to_bytes(4, 'big')
        content = TestDataGenerator.generate_random_data(size - 8)
        footer = b"END"
        return header + content + footer

    @staticmethod
    def generate_compressed_data(size: int) -> bytes:
        """Generate data that compresses well"""
        base_pattern = b"Hello, BSEE! Testing compression. "
        result = bytearray()
        for i in range(size):
            result.append(base_pattern[i % len(base_pattern)])
        return bytes(result)

    @staticmethod
    def generate_entropy_gradient(size: int) -> bytes:
        """Generate data with entropy gradient"""
        result = bytearray()
        for i in range(size):
            entropy_factor = i / size
            if random.random() < entropy_factor:
                result.append(random.randint(0, 255))
            else:
                result.append(0)
        return bytes(result)


@pytest.fixture
def test_data_generator():
    """Fixture providing test data generator"""
    return TestDataGenerator()


class TestConfigManager:
    """Utility class for managing test configurations"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.configs = {}

    def load_config(self, name: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if name not in self.configs:
            config_file = self.config_dir / f"{name}.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.configs[name] = json.load(f)
            else:
                self.configs[name] = self._get_default_config(name)
        return self.configs[name]

    def _get_default_config(self, name: str) -> Dict[str, Any]:
        """Get default configuration for test type"""
        defaults = {
            "unit_tests": {
                "max_assertions": 100,
                "timeout_seconds": 5.0,
                "require_coverage": False
            },
            "integration_tests": {
                "timeout_seconds": 30.0,
                "setup_time": 5.0,
                "cleanup_time": 2.0
            },
            "performance_tests": {
                "iterations": 10,
                "warmup_iterations": 3,
                "timeout_seconds": 60.0,
                "max_memory_mb": 1024.0
            },
            "gui_tests": {
                "headless": True,
                "test_delay": 0.1,
                "screenshot_on_failure": True,
                "timeout_seconds": 15.0
            }
        }
        return defaults.get(name, {})


@pytest.fixture(scope="session")
def config_manager(test_config_dir):
    """Fixture providing test configuration manager"""
    return TestConfigManager(test_config_dir)


class TestResultValidator:
    """Utility class for validating test results"""

    @staticmethod
    def validate_operation_reversibility(original_data: bytes,
                                      operation,
                                      tolerance: float = 0.0) -> bool:
        """Validate that operation is properly reversible"""
        try:
            # Apply operation
            transformed = operation.apply(original_data)

            # Apply inverse if available
            if hasattr(operation, 'inverse') and operation.inverse:
                inverse_op = operation.inverse()
                restored = inverse_op.apply(transformed)

                # Check if restoration is exact (or within tolerance)
                if tolerance == 0.0:
                    return restored == original_data
                else:
                    # Calculate difference percentage
                    differences = sum(1 for a, b in zip(restored, original_data) if a != b)
                    max_len = max(len(restored), len(original_data))
                    difference_ratio = differences / max_len if max_len > 0 else 0
                    return difference_ratio <= tolerance

            return True  # No inverse to test

        except Exception:
            return False

    @staticmethod
    def validate_strategy_consistency(strategy, test_data: bytes,
                                   runs: int = 5) -> Dict[str, Any]:
        """Validate strategy produces consistent results"""
        results = []

        for _ in range(runs):
            try:
                result = strategy.analyze(test_data, max_iterations=50)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})

        # Analyze consistency
        successful_results = [r for r in results if "error" not in r]

        if len(successful_results) < 2:
            return {
                "consistent": False,
                "success_rate": len(successful_results) / runs,
                "error": "Too few successful runs"
            }

        # Check score variance
        scores = [r.get("final_score", 0) for r in successful_results]
        avg_score = sum(scores) / len(scores)
        score_variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

        return {
            "consistent": score_variance < 0.01,  # Low variance indicates consistency
            "success_rate": len(successful_results) / runs,
            "average_score": avg_score,
            "score_variance": score_variance,
            "total_runs": runs
        }

    @staticmethod
    def validate_metric_calculation(metric_name: str, data: bytes,
                                  expected_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Validate metric calculation produces expected results"""
        try:
            # Import and calculate metric
            from bsee.metrics.metrics import calculate_metric
            value = calculate_metric(data, metric_name)

            result = {
                "metric_name": metric_name,
                "value": value,
                "valid": True
            }

            # Check against expected range if provided
            if expected_range:
                min_val, max_val = expected_range
                result["in_range"] = min_val <= value <= max_val
                result["expected_range"] = expected_range
            else:
                result["in_range"] = True

            return result

        except Exception as e:
            return {
                "metric_name": metric_name,
                "valid": False,
                "error": str(e)
            }


@pytest.fixture
def result_validator():
    """Fixture providing test result validator"""
    return TestResultValidator()


class PerformanceTracker:
    """Utility class for tracking test performance"""

    def __init__(self):
        self.measurements = []

    def start_measurement(self, name: str):
        """Start a performance measurement"""
        import time
        return {
            "name": name,
            "start_time": time.time(),
            "start_memory": self._get_memory_usage()
        }

    def end_measurement(self, measurement: Dict[str, Any]) -> Dict[str, Any]:
        """End a performance measurement"""
        import time
        measurement["end_time"] = time.time()
        measurement["duration"] = measurement["end_time"] - measurement["start_time"]
        measurement["end_memory"] = self._get_memory_usage()
        measurement["memory_delta"] = measurement["end_memory"] - measurement["start_memory"]

        self.measurements.append(measurement)
        return measurement

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.measurements:
            return {}

        durations = [m["duration"] for m in self.measurements]
        memory_deltas = [m["memory_delta"] for m in self.measurements]

        return {
            "total_measurements": len(self.measurements),
            "total_duration": sum(durations),
            "average_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "total_memory_delta": sum(memory_deltas),
            "average_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "max_memory_delta": max(memory_deltas)
        }


@pytest.fixture
def performance_tracker():
    """Fixture providing performance tracker"""
    return PerformanceTracker()


# Pytest configuration and hooks
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and configure"""
    # Add slow marker to tests that might take a long time
    for item in items:
        # Mark performance tests as slow
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)

        # Mark GUI tests
        if "gui" in item.nodeid:
            item.add_marker(pytest.mark.gui)

        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set random seed for reproducible tests
    random.seed(42)

    # Configure any global test settings
    import os
    os.environ['BSEE_TEST_MODE'] = '1'

    yield

    # Cleanup after test
    if 'BSEE_TEST_MODE' in os.environ:
        del os.environ['BSEE_TEST_MODE']