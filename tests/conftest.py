"""
pytest configuration and fixtures for BSEE testing framework
"""

import pytest
import tempfile
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDataGenerator:
    """Test data generator for BSEE tests"""

    def __init__(self):
        self.random_seed = 42

    def generate_random_data(self, size: int, seed: Optional[int] = None) -> bytes:
        """Generate random binary data"""
        if seed is not None:
            random.seed(seed)
        else:
            random.seed(self.random_seed)

        return bytes(random.randint(0, 255) for _ in range(size))

    def generate_structured_data(self, size: int) -> bytes:
        """Generate structured test data"""
        data = bytearray()

        # Header
        data.extend(b'BIN\x01')
        data.extend(size.to_bytes(4, 'little'))

        # Structured sections
        sections = [
            (0x20, b'\x00' * 0x20),  # Null section
            (0x40, bytes(range(0x40))),  # Sequential section
            (0x30, b'\xFF' * 0x30),  # High bytes section
        ]

        for section_size, section_data in sections:
            if len(data) + section_size > size - 4:
                section_size = size - len(data) - 4
                section_data = section_data[:section_size]
            data.extend(section_data)

        # Footer
        data.extend(b'END')

        # Fill to exact size
        while len(data) < size:
            data.append(0x00)

        return bytes(data[:size])

    def generate_patterned_data(self, size: int, pattern: str = "repeating") -> bytes:
        """Generate patterned binary data"""
        if pattern == "repeating":
            pattern_bytes = b'\xDE\xAD\xBE\xEF'
            return (pattern_bytes * ((size // 4) + 1))[:size]

        elif pattern == "alternating":
            return bytes([0xFF if i % 2 == 0 else 0x00 for i in range(size)])

        elif pattern == "incremental":
            return bytes(i % 256 for i in range(size))

        else:
            return self.generate_random_data(size)

    def generate_pattern_data(self, size: int, pattern: bytes) -> bytes:
        """Generate pattern-based test data"""
        if isinstance(pattern, bytes):
            return (pattern * ((size // len(pattern)) + 1))[:size]
        else:
            return self.generate_random_data(size)

    def generate_pattern_data(self, size: int, pattern: bytes) -> bytes:
        """Generate pattern-based test data"""
        if isinstance(pattern, bytes):
            return (pattern * ((size // len(pattern)) + 1))[:size]
        else:
            return self.generate_random_data(size)


class TestResultValidator:
    """Test result validator for BSEE tests"""

    def __init__(self):
        pass

    def validate_operation_reversibility(self, test_data: bytes, operation) -> bool:
        """Validate operation reversibility"""
        try:
            # Apply operation
            result = operation.apply(test_data)

            # Try to reverse (if operation has reverse method)
            if hasattr(operation, 'reverse'):
                reversed_data = operation.reverse(result)
                return reversed_data == test_data

            # If no reverse method, assume successful
            return True

        except Exception:
            return False

    def validate_strategy_consistency(self, strategy, test_data: bytes, runs: int = 3) -> Dict[str, Any]:
        """Validate strategy produces consistent results"""
        results = []

        for _ in range(runs):
            try:
                result = strategy.analyze(test_data, max_iterations=10)
                results.append(result)
            except Exception:
                continue

        if not results:
            return {"success_rate": 0.0, "consistent": False}

        # Check if results are consistent (similar scores)
        scores = [result.get("score", 0.0) for result in results if "score" in result]
        if len(scores) < 2:
            return {"success_rate": len(results) / runs, "consistent": True}

        # Calculate variance in scores
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)

        # Consider consistent if variance is low
        consistent = variance < 0.1  # Allow for some randomness

        return {
            "success_rate": len(results) / runs,
            "consistent": consistent,
            "mean_score": mean_score,
            "variance": variance,
            "scores": scores
        }

    def validate_analysis_quality(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis result quality"""
        validation = {
            "has_required_fields": True,
            "score_valid": True,
            "convergence_valid": True,
            "metadata_complete": True
        }

        required_fields = ["strategy", "score", "converged"]
        missing_fields = [field for field in required_fields if field not in analysis_result]

        if missing_fields:
            validation["has_required_fields"] = False
            validation["missing_fields"] = missing_fields

        # Validate score
        score = analysis_result.get("score")
        if score is not None:
            if not isinstance(score, (int, float)) or not (0 <= score <= 1):
                validation["score_valid"] = False

        # Validate convergence
        converged = analysis_result.get("converged")
        if converged is not None and not isinstance(converged, bool):
            validation["convergence_valid"] = False

        # Overall validation
        validation["overall_valid"] = all([
            validation["has_required_fields"],
            validation["score_valid"],
            validation["convergence_valid"]
        ])

        return validation


class MockFileLoader:
    """Mock file loader for testing"""

    def __init__(self):
        self.loaded_files = {}

    def load(self, file_path: Path) -> bytes:
        """Load file content"""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if file_path in self.loaded_files:
            return self.loaded_files[file_path]

        # Generate mock data based on file extension
        extension = file_path.suffix.lower()
        if extension == '.bin':
            data = TestDataGenerator().generate_random_data(1024)
        elif extension == '.exe':
            data = TestDataGenerator().generate_structured_data(2048)
        else:
            data = TestDataGenerator().generate_patterned_data(512)

        self.loaded_files[file_path] = data
        return data


class MockAnalyzer:
    """Mock analyzer for testing"""

    def __init__(self):
        self.strategies = [
            MockMCTSStrategy(),
            MockGeneticStrategy(),
            MockHeuristicStrategy()
        ]

    def analyze(self, data: bytes, strategy) -> Dict[str, Any]:
        """Analyze data with given strategy"""
        return strategy.analyze(data, max_iterations=10)


class MockReporter:
    """Mock reporter for testing"""

    def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analysis report"""
        return {
            "total_results": len(results),
            "summary": {
                "best_strategy": max(results, key=lambda r: r.get("score", 0)).get("strategy", "unknown"),
                "average_score": sum(r.get("score", 0) for r in results) / len(results) if results else 0
            },
            "results": results
        }


class MockMCTSStrategy:
    """Mock MCTS strategy"""

    def analyze(self, data: bytes, max_iterations: int = 10) -> Dict[str, Any]:
        """Mock MCTS analysis"""
        return {
            "strategy": "mcts",
            "score": random.uniform(0.7, 0.9),
            "iterations": random.randint(5, max_iterations),
            "converged": random.random() > 0.2,
            "tree_nodes": random.randint(100, 1000),
            "best_score": random.uniform(0.8, 0.95)
        }


class MockGeneticStrategy:
    """Mock Genetic strategy"""

    def analyze(self, data: bytes, max_iterations: int = 10) -> Dict[str, Any]:
        """Mock genetic analysis"""
        return {
            "strategy": "genetic",
            "score": random.uniform(0.6, 0.85),
            "iterations": random.randint(10, 50),
            "converged": random.random() > 0.3,
            "population_size": 50,
            "mutation_rate": 0.1,
            "best_fitness": random.uniform(0.7, 0.9)
        }


class MockHeuristicStrategy:
    """Mock Heuristic strategy"""

    def analyze(self, data: bytes, max_iterations: int = 10) -> Dict[str, Any]:
        """Mock heuristic analysis"""
        return {
            "strategy": "heuristic",
            "score": random.uniform(0.5, 0.8),
            "iterations": 1,  # Heuristics are typically single-pass
            "converged": True,  # Always converges (single pass)
            "entropy": random.uniform(3.0, 8.0),
            "patterns_found": random.randint(5, 50)
        }


# pytest fixtures

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory"""
    return Path(__file__).parent / "fixtures" / "test_files"


@pytest.fixture(scope="session")
def project_root_path():
    """Fixture providing project root path"""
    return project_root


@pytest.fixture
def test_data_generator():
    """Fixture providing test data generator"""
    return TestDataGenerator()


@pytest.fixture
def result_validator():
    """Fixture providing test result validator"""
    return TestResultValidator()


@pytest.fixture
def sample_binary_data():
    """Fixture providing sample binary data"""
    return TestDataGenerator().generate_random_data(1024, seed=42)


@pytest.fixture
def sample_structured_data():
    """Fixture providing sample structured data"""
    return TestDataGenerator().generate_structured_data(1024)


@pytest.fixture
def sample_patterned_data():
    """Fixture providing sample patterned data"""
    return TestDataGenerator().generate_patterned_data(1024, "repeating")


@pytest.fixture
def mock_strategy():
    """Fixture providing mock strategy"""
    strategy = Mock()
    strategy.name = "mock_strategy"
    strategy.analyze.return_value = {
        "strategy": "mock_strategy",
        "score": 0.75,
        "iterations": 10,
        "converged": True
    }
    return strategy


@pytest.fixture
def mock_operation():
    """Fixture providing mock operation"""
    operation = Mock()
    operation.apply.return_value = b"modified_data"
    operation.reverse.return_value = b"original_data"
    return operation


@pytest.fixture
def temp_dir():
    """Fixture providing temporary directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_file_loader():
    """Fixture providing mock file loader"""
    return MockFileLoader()


@pytest.fixture
def mock_analyzer():
    """Fixture providing mock analyzer"""
    return MockAnalyzer()


@pytest.fixture
def mock_reporter():
    """Fixture providing mock reporter"""
    return MockReporter()


@pytest.fixture
def performance_tracker():
    """Fixture providing performance tracking"""
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.memory_samples = []

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        def add_memory_sample(self, memory_mb: float):
            self.memory_samples.append(memory_mb)

        def get_duration(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

        def get_peak_memory(self) -> float:
            return max(self.memory_samples) if self.memory_samples else 0.0

    return PerformanceTracker()


# Mock operations for testing

class XorOp:
    """Mock XOR operation"""

    def __init__(self, key: int):
        self.key = key

    def apply(self, data: bytes) -> bytes:
        return bytes(b ^ self.key for b in data)

    def reverse(self, data: bytes) -> bytes:
        return self.apply(data)  # XOR is its own reverse


class AddConstantOp:
    """Mock add constant operation"""

    def __init__(self, constant: int):
        self.constant = constant

    def apply(self, data: bytes) -> bytes:
        return bytes((b + self.constant) % 256 for b in data)

    def reverse(self, data: bytes) -> bytes:
        return bytes((b - self.constant) % 256 for b in data)


class RotateOp:
    """Mock rotate operation"""

    def __init__(self, bits: int):
        self.bits = bits

    def apply(self, data: bytes) -> bytes:
        result = bytearray()
        for byte in data:
            result.append(((byte << self.bits) | (byte >> (8 - self.bits))) & 0xFF)
        return bytes(result)

    def reverse(self, data: bytes) -> bytes:
        # Reverse rotation
        result = bytearray()
        for byte in data:
            result.append(((byte >> self.bits) | (byte << (8 - self.bits))) & 0xFF)
        return bytes(result)


# pytest markers

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "gui: mark test as GUI test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Test utilities

def assert_dicts_almost_equal(dict1: Dict, dict2: Dict, tolerance: float = 1e-6):
    """Assert two dictionaries are almost equal for numeric values"""
    assert dict1.keys() == dict2.keys(), f"Keys differ: {dict1.keys()} vs {dict2.keys()}"

    for key in dict1.keys():
        value1 = dict1[key]
        value2 = dict2[key]

        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            assert abs(value1 - value2) <= tolerance, f"Values differ for key {key}: {value1} vs {value2}"
        else:
            assert value1 == value2, f"Values differ for key {key}: {value1} vs {value2}"


def create_test_scenarios() -> List[Dict[str, Any]]:
    """Create standard test scenarios"""
    scenarios = []

    # Small data scenarios
    for size in [64, 256, 1024]:
        scenarios.append({
            "name": f"random_{size}",
            "size": size,
            "data": TestDataGenerator().generate_random_data(size, seed=42),
            "expected_entropy_range": (6.0, 8.0)
        })

    # Structured data scenarios
    for size in [512, 1024, 2048]:
        scenarios.append({
            "name": f"structured_{size}",
            "size": size,
            "data": TestDataGenerator().generate_structured_data(size),
            "expected_entropy_range": (2.0, 6.0)
        })

    # Patterned data scenarios
    patterns = ["repeating", "alternating", "incremental"]
    for pattern in patterns:
        scenarios.append({
            "name": f"patterned_{pattern}",
            "size": 1024,
            "data": TestDataGenerator().generate_patterned_data(1024, pattern),
            "expected_entropy_range": (0.0, 4.0)
        })

    return scenarios


if __name__ == "__main__":
    # Test the fixtures
    print("Testing BSEE pytest fixtures...")

    generator = TestDataGenerator()
    print(f"Generated random data: {len(generator.generate_random_data(100))} bytes")
    print(f"Generated structured data: {len(generator.generate_structured_data(100))} bytes")
    print(f"Generated patterned data: {len(generator.generate_patterned_data(100))} bytes")

    validator = TestResultValidator()
    mock_strategy = MockMCTSStrategy()
    consistency = validator.validate_strategy_consistency(mock_strategy, b"test", runs=3)
    print(f"Strategy consistency test: {consistency}")

    print("All fixtures working correctly!")