"""
Integration Tests for End-to-End Pipeline
Test complete analysis workflows from file input to results output
"""

import pytest
import tempfile
import os
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch

from tests.conftest import TestDataGenerator, TestResultValidator


class TestCompleteAnalysisPipeline:
    """Test complete analysis pipeline end-to-end"""

    @pytest.mark.integration
    def test_load_file_through_full_pipeline(self, temp_dir, test_data_generator):
        """Load test file through full pipeline"""
        # Create test file
        test_file = temp_dir / "test_input.bin"
        test_data = test_data_generator.generate_structured_data(1024)
        test_file.write_bytes(test_data)

        # Mock pipeline components
        class MockFileLoader:
            def load(self, file_path: Path) -> bytes:
                return file_path.read_bytes()

        class MockAnalyzer:
            def __init__(self):
                self.strategies = ["mcts", "genetic", "beam_search"]

            def analyze(self, data: bytes, strategy: str) -> Dict[str, Any]:
                return {
                    "strategy": strategy,
                    "score": 0.7 + self.strategies.index(strategy) * 0.05,
                    "operations": ["xor_42", "add_10"],
                    "metadata": {
                        "file_size": len(data),
                        "analysis_time": 1.5,
                        "iterations": 50
                    }
                }

        class MockReporter:
            def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
                return {
                    "summary": {
                        "total_analyses": len(results),
                        "best_strategy": max(results, key=lambda x: x["score"])["strategy"],
                        "best_score": max(r["score"] for r in results)
                    },
                    "detailed_results": results,
                    "timestamp": time.time()
                }

        # Execute pipeline
        loader = MockFileLoader()
        analyzer = MockAnalyzer()
        reporter = MockReporter()

        # Load file
        loaded_data = loader.load(test_file)
        assert loaded_data == test_data

        # Analyze with all strategies
        results = []
        for strategy in analyzer.strategies:
            result = analyzer.analyze(loaded_data, strategy)
            results.append(result)

        # Generate report
        report = reporter.generate_report(results)

        # Verify results
        assert len(results) == 3
        assert all("strategy" in result for result in results)
        assert all("score" in result for result in results)
        assert report["summary"]["total_analyses"] == 3
        assert report["summary"]["best_strategy"] == "beam_search"  # Highest score

    @pytest.mark.integration
    def test_pipeline_with_all_strategies(self, sample_binary_data):
        """Test pipeline with all available strategies"""
        class MockPipeline:
            def __init__(self):
                self.strategies = ["mcts", "genetic", "beam_search", "simulated_annealing", "heuristic"]

            def run_analysis(self, data: bytes, max_iterations: int = 100) -> Dict[str, Any]:
                results = {}
                for strategy in self.strategies:
                    # Mock different behaviors for different strategies
                    if strategy == "mcts":
                        score = 0.85
                        iterations_used = max_iterations
                    elif strategy == "genetic":
                        score = 0.78
                        iterations_used = max_iterations // 2
                    elif strategy == "beam_search":
                        score = 0.72
                        iterations_used = max_iterations // 4
                    elif strategy == "simulated_annealing":
                        score = 0.80
                        iterations_used = int(max_iterations * 0.7)
                    else:  # heuristic
                        score = 0.65
                        iterations_used = 1

                    results[strategy] = {
                        "score": score,
                        "iterations": iterations_used,
                        "converged": iterations_used > 0,
                        "operations": [f"op_by_{strategy}"],
                        "execution_time": 0.1 + iterations_used * 0.01
                    }

                return {
                    "input_data_size": len(data),
                    "results": results,
                    "best_strategy": max(results.keys(), key=lambda k: results[k]["score"]),
                    "total_execution_time": sum(r["execution_time"] for r in results.values())
                }

        pipeline = MockPipeline()
        result = pipeline.run_analysis(sample_binary_data, max_iterations=100)

        # Verify all strategies were executed
        assert len(result["results"]) == 5
        assert set(result["results"].keys()) == set(pipeline.strategies)

        # Verify best strategy identification
        assert result["best_strategy"] == "mcts"  # Highest score
        assert result["results"]["mcts"]["score"] == 0.85

        # Verify all strategies converged
        assert all(r["converged"] for r in result["results"].values())

    @pytest.mark.integration
    def test_pipeline_error_recovery(self, temp_dir):
        """Test error handling in complete workflows"""
        class FailingOperation:
            def __init__(self, always_fail: bool = False):
                self.call_count = 0
                self.always_fail = always_fail

            def apply(self, data: bytes) -> bytes:
                self.call_count += 1
                if self.always_fail or self.call_count == 1:
                    raise RuntimeError(f"Simulated failure on call {self.call_count}")
                return data

        class ResilientPipeline:
            def __init__(self):
                self.operations = [
                    FailingOperation(always_fail=True),   # Always fails
                    FailingOperation(always_fail=False),  # Fails on first call, succeeds on retry
                ]

            def process_with_retry(self, data: bytes, max_retries: int = 3) -> Dict[str, Any]:
                results = {}
                errors = []

                for i, op in enumerate(self.operations):
                    success = False
                    last_error = None

                    for attempt in range(max_retries):
                        try:
                            result = op.apply(data)
                            results[f"op_{i}"] = {
                                "success": True,
                                "result_size": len(result),
                                "attempts": attempt + 1
                            }
                            success = True
                            break
                        except Exception as e:
                            last_error = str(e)
                            if attempt == max_retries - 1:
                                errors.append(f"Operation {i} failed after {max_retries} attempts: {last_error}")

                    if not success:
                        results[f"op_{i}"] = {
                            "success": False,
                            "error": last_error,
                            "attempts": max_retries
                        }

                return {
                    "successful_operations": sum(1 for r in results.values() if r["success"]),
                    "failed_operations": len(errors),
                    "errors": errors,
                    "detailed_results": results
                }

        pipeline = ResilientPipeline()
        test_data = b"error recovery test"

        result = pipeline.process_with_retry(test_data, max_retries=3)

        # Verify error handling
        assert result["successful_operations"] >= 1  # At least first operation should succeed
        assert result["failed_operations"] >= 1  # Some operations should fail
        assert len(result["errors"]) > 0
        assert "detailed_results" in result

    @pytest.mark.integration
    def test_pipeline_configuration_integration(self, temp_dir, sample_json_data):
        """Test config loading and application in pipeline"""
        # Create test config file
        config_file = temp_dir / "test_config.json"
        config_data = {
            "strategies": {
                "enabled": ["mcts", "genetic"],
                "mcts": {
                    "max_iterations": 100,
                    "exploration_constant": 1.41
                },
                "genetic": {
                    "population_size": 50,
                    "mutation_rate": 0.1
                }
            },
            "operations": {
                "allowed_operations": ["xor", "add_constant", "rotate_left"],
                "max_depth": 10
            },
            "output": {
                "format": "json",
                "include_metadata": True
            }
        }

        config_file.write_text(json.dumps(config_data, indent=2))

        class ConfigurablePipeline:
            def __init__(self, config_path: Path):
                self.config = self._load_config(config_path)
                self.validate_config()

            def _load_config(self, config_path: Path) -> Dict[str, Any]:
                with open(config_path, 'r') as f:
                    return json.load(f)

            def validate_config(self):
                required_sections = ["strategies", "operations", "output"]
                for section in required_sections:
                    if section not in self.config:
                        raise ValueError(f"Missing required config section: {section}")

            def run_with_config(self, data: bytes) -> Dict[str, Any]:
                enabled_strategies = self.config["strategies"]["enabled"]
                results = {}

                for strategy in enabled_strategies:
                    if strategy == "mcts":
                        max_iter = self.config["strategies"]["mcts"]["max_iterations"]
                        results[strategy] = {
                            "score": 0.8,
                            "iterations": max_iter,
                            "config_used": self.config["strategies"]["mcts"]
                        }
                    elif strategy == "genetic":
                        pop_size = self.config["strategies"]["genetic"]["population_size"]
                        results[strategy] = {
                            "score": 0.75,
                            "population_size": pop_size,
                            "config_used": self.config["strategies"]["genetic"]
                        }

                # Apply output configuration
                output_format = self.config["output"]["format"]
                include_metadata = self.config["output"]["include_metadata"]

                final_result = {
                    "results": results,
                    "format": output_format
                }

                if include_metadata:
                    final_result["metadata"] = {
                        "config_file": str(config_file),
                        "data_size": len(data),
                        "timestamp": time.time()
                    }

                return final_result

        # Test with valid config
        pipeline = ConfigurablePipeline(config_file)
        result = pipeline.run_with_config(b"config test data")

        assert len(result["results"]) == 2  # Two enabled strategies
        assert "mcts" in result["results"]
        assert "genetic" in result["results"]
        assert result["results"]["mcts"]["iterations"] == 100
        assert result["results"]["genetic"]["population_size"] == 50
        assert result["format"] == "json"
        assert "metadata" in result

        # Test with invalid config
        invalid_config_file = temp_dir / "invalid_config.json"
        invalid_config_file.write_text('{"invalid": "config"}')

        with pytest.raises(ValueError, match="Missing required config section"):
            ConfigurablePipeline(invalid_config_file)


class TestStrategyIntegration:
    """Test strategy integration components"""

    @pytest.mark.integration
    def test_strategies_integration(self, sample_binary_data):
        """Test strategy integration and comparison"""
        class StrategyManager:
            def __init__(self):
                self.strategies = {
                    "mcts": MockMCTSStrategy(),
                    "genetic": MockGeneticStrategy(),
                    "heuristic": MockHeuristicStrategy()
                }

            def run_comparative_analysis(self, data: bytes) -> Dict[str, Any]:
                results = {}
                for name, strategy in self.strategies.items():
                    result = strategy.analyze(data)
                    results[name] = result

                # Rank strategies by score
                ranked_strategies = sorted(results.items(),
                                        key=lambda x: x[1]["score"],
                                        reverse=True)

                return {
                    "individual_results": results,
                    "ranking": [{"strategy": name, **result} for name, result in ranked_strategies],
                    "best_strategy": ranked_strategies[0][0],
                    "score_difference": ranked_strategies[0][1]["score"] - ranked_strategies[-1][1]["score"]
                }

        class MockMCTSStrategy:
            def analyze(self, data: bytes) -> Dict[str, Any]:
                return {
                    "score": 0.85,
                    "iterations": 100,
                    "tree_nodes": 150,
                    "convergence_time": 2.5
                }

        class MockGeneticStrategy:
            def analyze(self, data: bytes) -> Dict[str, Any]:
                return {
                    "score": 0.78,
                    "iterations": 50,
                    "population_size": 30,
                    "convergence_time": 1.8
                }

        class MockHeuristicStrategy:
            def analyze(self, data: bytes) -> Dict[str, Any]:
                return {
                    "score": 0.65,
                    "iterations": 1,
                    "evaluation_time": 0.1
                }

        manager = StrategyManager()
        result = manager.run_comparative_analysis(sample_binary_data)

        # Verify integration results
        assert len(result["individual_results"]) == 3
        assert len(result["ranking"]) == 3
        assert result["best_strategy"] == "mcts"
        assert result["ranking"][0]["score"] > result["ranking"][-1]["score"]

        # Verify all strategies have required fields
        for strategy_result in result["individual_results"].values():
            assert "score" in strategy_result
            assert "iterations" in strategy_result

    @pytest.mark.integration
    def test_strategy_parameter_integration(self, sample_binary_data):
        """Test strategy parameter configuration and integration"""
        class ParameterizedStrategyManager:
            def __init__(self):
                self.default_configs = {
                    "mcts": {
                        "max_iterations": 100,
                        "exploration_constant": 1.41,
                        "simulation_count": 10
                    },
                    "genetic": {
                        "population_size": 50,
                        "mutation_rate": 0.1,
                        "crossover_rate": 0.7,
                        "max_generations": 100
                    }
                }

            def run_with_configs(self, data: bytes,
                               config_overrides: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
                results = {}
                config_overrides = config_overrides or {}

                for strategy_name, default_config in self.default_configs.items():
                    # Merge default config with overrides
                    config = default_config.copy()
                    if strategy_name in config_overrides:
                        config.update(config_overrides[strategy_name])

                    # Run strategy with config
                    if strategy_name == "mcts":
                        result = self._run_mcts(data, config)
                    elif strategy_name == "genetic":
                        result = self._run_genetic(data, config)

                    results[strategy_name] = {
                        "result": result,
                        "config_used": config,
                        "config_overridden": strategy_name in config_overrides
                    }

                return results

            def _run_mcts(self, data: bytes, config: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "score": 0.8 + config["exploration_constant"] * 0.05,
                    "iterations": min(config["max_iterations"], 80),
                    "simulations": config["simulation_count"]
                }

            def _run_genetic(self, data: bytes, config: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "score": 0.7 + (1.0 - config["mutation_rate"]) * 0.2,
                    "generations": config["max_generations"],
                    "population": config["population_size"]
                }

        manager = ParameterizedStrategyManager()

        # Test with default configs
        default_result = manager.run_with_configs(sample_binary_data)
        assert len(default_result) == 2
        assert not default_result["mcts"]["config_overridden"]
        assert not default_result["genetic"]["config_overridden"]

        # Test with config overrides
        overrides = {
            "mcts": {"exploration_constant": 2.0, "max_iterations": 50},
            "genetic": {"mutation_rate": 0.2}
        }

        override_result = manager.run_with_configs(sample_binary_data, overrides)
        assert override_result["mcts"]["config_overridden"]
        assert override_result["genetic"]["config_overridden"]
        assert override_result["mcts"]["config_used"]["exploration_constant"] == 2.0
        assert override_result["mcts"]["config_used"]["max_iterations"] == 50
        assert override_result["genetic"]["config_used"]["mutation_rate"] == 0.2


class TestOperationIntegration:
    """Test operation integration and chaining"""

    @pytest.mark.integration
    def test_operation_chaining(self, result_validator):
        """Test chaining multiple operations"""
        class OperationChain:
            def __init__(self):
                self.operations = []

            def add_operation(self, operation_func, *args, **kwargs):
                self.operations.append((operation_func, args, kwargs))

            def apply_chain(self, data: bytes) -> bytes:
                current_data = data
                operation_log = []

                for i, (op_func, args, kwargs) in enumerate(self.operations):
                    try:
                        current_data = op_func(current_data, *args, **kwargs)
                        operation_log.append({
                            "step": i,
                            "operation": op_func.__name__,
                            "success": True,
                            "output_size": len(current_data)
                        })
                    except Exception as e:
                        operation_log.append({
                            "step": i,
                            "operation": op_func.__name__,
                            "success": False,
                            "error": str(e)
                        })
                        break

                return current_data, operation_log

        # Define operations
        def xor_operation(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        def add_operation(data: bytes, value: int) -> bytes:
            return bytes((b + value) % 256 for b in data)

        def rotate_operation(data: bytes, bits: int) -> bytes:
            bits = bits % 8
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        # Create and test operation chain
        chain = OperationChain()
        chain.add_operation(xor_operation, 0x42)
        chain.add_operation(add_operation, 10)
        chain.add_operation(rotate_operation, 2)

        original_data = b"operation_chain_test"
        result_data, operation_log = chain.apply_chain(original_data)

        # Verify chain execution
        assert len(operation_log) == 3
        assert all(log["success"] for log in operation_log)
        assert result_data != original_data

        # Test reversibility of the entire chain
        class ReversibleChain:
            def __init__(self):
                self.forward_chain = OperationChain()
                self.reverse_chain = OperationChain()

            def add_reversible_operation(self, op_func, reverse_op_func, *args, **kwargs):
                self.forward_chain.add_operation(op_func, *args, **kwargs)
                self.reverse_chain.add_operation(reverse_op_func, *args, **kwargs)

            def apply_forward(self, data: bytes) -> bytes:
                result, _ = self.forward_chain.apply_chain(data)
                return result

            def apply_reverse(self, data: bytes) -> bytes:
                result, _ = self.reverse_chain.apply_chain(data)
                return result

        reversible_chain = ReversibleChain()
        reversible_chain.add_reversible_operation(
            xor_operation, xor_operation, 0x5A
        )
        reversible_chain.add_reversible_operation(
            add_operation,
            lambda data, value: bytes((b - value) % 256 for b in data),
            25
        )

        forward_result = reversible_chain.apply_forward(original_data)
        reverse_result = reversible_chain.apply_reverse(forward_result)

        # Verify reversibility
        assert reverse_result == original_data

    @pytest.mark.integration
    def test_operation_parameter_integration(self):
        """Test operations with complex parameter integration"""
        class ParameterizedOperationManager:
            def __init__(self):
                self.operation_registry = {
                    "xor": self._xor_with_params,
                    "add": self._add_with_params,
                    "substitute": self._substitute_with_params
                }

            def execute_operation_sequence(self, data: bytes,
                                         operation_sequence: List[Dict[str, Any]]) -> bytes:
                current_data = data

                for op_config in operation_sequence:
                    op_name = op_config["name"]
                    op_params = op_config.get("parameters", {})

                    if op_name not in self.operation_registry:
                        raise ValueError(f"Unknown operation: {op_name}")

                    current_data = self.operation_registry[op_name](current_data, op_params)

                return current_data

            def _xor_with_params(self, data: bytes, params: Dict[str, Any]) -> bytes:
                key = params.get("key", 0)
                key = key & 0xFF  # Ensure single byte
                return bytes(b ^ key for b in data)

            def _add_with_params(self, data: bytes, params: Dict[str, Any]) -> bytes:
                value = params.get("value", 0)
                value = value % 256  # Ensure single byte range
                return bytes((b + value) % 256 for b in data)

            def _substitute_with_params(self, data: bytes, params: Dict[str, Any]) -> bytes:
                mapping = params.get("mapping", {})
                result = bytearray()
                for byte in data:
                    replacement = mapping.get(byte, byte)
                    result.append(replacement & 0xFF)
                return bytes(result)

        manager = ParameterizedOperationManager()

        # Test simple sequence
        test_data = b"parameter_test"
        sequence = [
            {"name": "xor", "parameters": {"key": 0x42}},
            {"name": "add", "parameters": {"value": 10}}
        ]

        result = manager.execute_operation_sequence(test_data, sequence)
        assert len(result) == len(test_data)
        assert result != test_data

        # Test complex sequence with substitution
        complex_sequence = [
            {"name": "xor", "parameters": {"key": 0x5A}},
            {"name": "substitute", "parameters": {"mapping": {65: 90, 66: 89}}},  # A->Z, B->Y
            {"name": "add", "parameters": {"value": 5}}
        ]

        test_data_with_letters = b"ABCDtest"
        complex_result = manager.execute_operation_sequence(test_data_with_letters, complex_sequence)

        assert len(complex_result) == len(test_data_with_letters)

        # Test invalid operation
        invalid_sequence = [
            {"name": "invalid_operation", "parameters": {}}
        ]

        with pytest.raises(ValueError, match="Unknown operation"):
            manager.execute_operation_sequence(test_data, invalid_sequence)


class TestGUIWorkflowIntegration:
    """Test complete GUI workflows"""

    @pytest.mark.integration
    @pytest.mark.gui
    def test_gui_file_loading_workflow(self, temp_dir, test_data_generator):
        """Test GUI file loading and initial setup workflow"""
        # Mock GUI components
        class MockFilePanel:
            def __init__(self):
                self.loaded_file = None
                self.file_info = {}

            def load_file(self, file_path: Path) -> bool:
                try:
                    self.loaded_file = file_path
                    self.file_info = {
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    }
                    return True
                except Exception:
                    return False

            def get_file_data(self) -> bytes:
                if self.loaded_file:
                    return self.loaded_file.read_bytes()
                return b""

        class MockMainPanel:
            def __init__(self):
                self.file_panel = MockFilePanel()
                self.analysis_config = {}
                self.current_analysis = None

            def setup_analysis(self, strategies: List[str], max_iterations: int) -> Dict[str, Any]:
                self.analysis_config = {
                    "strategies": strategies,
                    "max_iterations": max_iterations,
                    "setup_time": time.time()
                }
                return self.analysis_config

            def run_analysis(self) -> Dict[str, Any]:
                if not self.file_panel.loaded_file:
                    raise ValueError("No file loaded")

                data = self.file_panel.get_file_data()
                strategies = self.analysis_config.get("strategies", ["mcts"])
                max_iter = self.analysis_config.get("max_iterations", 100)

                # Mock analysis
                results = {}
                for strategy in strategies:
                    results[strategy] = {
                        "score": 0.7 + random.random() * 0.2,
                        "iterations": random.randint(10, max_iter),
                        "status": "completed"
                    }

                self.current_analysis = {
                    "file_info": self.file_panel.file_info,
                    "results": results,
                    "completion_time": time.time()
                }

                return self.current_analysis

        # Create test file
        test_file = temp_dir / "gui_test_file.bin"
        test_data = test_data_generator.generate_random_data(2048, seed=789)
        test_file.write_bytes(test_data)

        # Execute GUI workflow
        main_panel = MockMainPanel()

        # Step 1: Load file
        load_success = main_panel.file_panel.load_file(test_file)
        assert load_success
        assert main_panel.file_panel.file_info["size"] == 2048

        # Step 2: Setup analysis
        strategies = ["mcts", "genetic"]
        setup_result = main_panel.setup_analysis(strategies, max_iterations=50)
        assert setup_result["strategies"] == strategies
        assert setup_result["max_iterations"] == 50

        # Step 3: Run analysis
        analysis_result = main_panel.run_analysis()
        assert "file_info" in analysis_result
        assert "results" in analysis_result
        assert len(analysis_result["results"]) == 2
        assert all(result["status"] == "completed" for result in analysis_result["results"].values())

    @pytest.mark.integration
    @pytest.mark.gui
    def test_gui_transformation_viewer_workflow(self, sample_binary_data):
        """Test GUI transformation viewer workflow"""
        class MockTransformationViewer:
            def __init__(self):
                self.transformations = []
                self.current_index = -1
                self.is_playing = False

            def add_transformation(self, operation_name: str, original_data: bytes,
                                transformed_data: bytes, metadata: Dict[str, Any] = None):
                transformation = {
                    "id": len(self.transformations),
                    "operation": operation_name,
                    "original": original_data,
                    "transformed": transformed_data,
                    "metadata": metadata or {},
                    "timestamp": time.time()
                }
                self.transformations.append(transformation)
                self.current_index = len(self.transformations) - 1
                return transformation["id"]

            def get_transformation(self, index: int) -> Optional[Dict[str, Any]]:
                if 0 <= index < len(self.transformations):
                    return self.transformations[index]
                return None

            def play_transformations(self, start_index: int = 0, speed: float = 1.0):
                """Mock playback functionality"""
                self.is_playing = True
                playback_log = []

                for i in range(start_index, len(self.transformations)):
                    if not self.is_playing:
                        break
                    playback_log.append(f"Playing transformation {i}: {self.transformations[i]['operation']}")
                    # Simulate delay based on speed
                    time.sleep(0.01 / speed)

                self.is_playing = False
                return playback_log

        class MockGUIController:
            def __init__(self):
                self.transformation_viewer = MockTransformationViewer()
                self.selected_operations = []

            def apply_operation(self, operation_name: str, data: bytes, **params) -> bytes:
                """Mock operation application"""
                if operation_name == "xor":
                    key = params.get("key", 0)
                    return bytes(b ^ key for b in data)
                elif operation_name == "add":
                    value = params.get("value", 0)
                    return bytes((b + value) % 256 for b in data)
                else:
                    return data

            def create_transformation_sequence(self, data: bytes,
                                            operations: List[Dict[str, Any]]) -> List[int]:
                """Create a sequence of transformations"""
                transformation_ids = []
                current_data = data

                for op_config in operations:
                    op_name = op_config["name"]
                    op_params = op_config.get("parameters", {})

                    transformed_data = self.apply_operation(op_name, current_data, **op_params)
                    trans_id = self.transformation_viewer.add_transformation(
                        op_name, current_data, transformed_data, op_params
                    )
                    transformation_ids.append(trans_id)
                    current_data = transformed_data

                return transformation_ids

        # Execute GUI transformation workflow
        controller = MockGUIController()
        operations = [
            {"name": "xor", "parameters": {"key": 0x42}},
            {"name": "add", "parameters": {"value": 10}},
            {"name": "xor", "parameters": {"key": 0x42}}  # Should reverse first XOR
        ]

        # Create transformation sequence
        transformation_ids = controller.create_transformation_sequence(sample_binary_data, operations)

        # Verify transformations
        assert len(transformation_ids) == 3
        assert len(controller.transformation_viewer.transformations) == 3

        # Test transformation playback
        playback_log = controller.transformation_viewer.play_transformations(speed=2.0)
        assert len(playback_log) == 3
        assert "xor" in playback_log[0]
        assert "add" in playback_log[1]
        assert "xor" in playback_log[2]

        # Verify transformation data
        first_transform = controller.transformation_viewer.get_transformation(0)
        assert first_transform["operation"] == "xor"
        assert first_transform["original"] == sample_binary_data
        assert len(first_transform["transformed"]) == len(sample_binary_data)

    @pytest.mark.integration
    @pytest.mark.gui
    def test_gui_export_workflow(self, temp_dir, sample_binary_data):
        """Test GUI export functionality workflow"""
        class MockExportManager:
            def __init__(self):
                self.export_history = []

            def export_analysis_results(self, results: Dict[str, Any],
                                     format_type: str, output_path: Path) -> bool:
                try:
                    if format_type == "json":
                        with open(output_path, 'w') as f:
                            json.dump(results, f, indent=2, default=str)
                    elif format_type == "csv":
                        with open(output_path, 'w') as f:
                            f.write("Strategy,Score,Iterations\n")
                            for strategy, result in results.get("results", {}).items():
                                f.write(f"{strategy},{result['score']},{result['iterations']}\n")
                    else:
                        raise ValueError(f"Unsupported format: {format_type}")

                    export_record = {
                        "format": format_type,
                        "path": str(output_path),
                        "timestamp": time.time(),
                        "size": output_path.stat().st_size
                    }
                    self.export_history.append(export_record)
                    return True

                except Exception:
                    return False

            def export_transformation_sequence(self, transformations: List[Dict[str, Any]],
                                           output_path: Path) -> bool:
                try:
                    with open(output_path, 'w') as f:
                        json.dump(transformations, f, indent=2, default=str)

                    export_record = {
                        "format": "transformations",
                        "path": str(output_path),
                        "transformations_count": len(transformations),
                        "timestamp": time.time()
                    }
                    self.export_history.append(export_record)
                    return True

                except Exception:
                    return False

        class MockGUIController:
            def __init__(self, export_dir: Path):
                self.export_dir = export_dir
                self.export_manager = MockExportManager()
                self.current_results = None
                self.current_transformations = []

            def set_analysis_results(self, results: Dict[str, Any]):
                self.current_results = results

            def set_transformations(self, transformations: List[Dict[str, Any]]):
                self.current_transformations = transformations

            def export_current_analysis(self, format_type: str) -> Optional[Path]:
                if not self.current_results:
                    return None

                timestamp = int(time.time())
                filename = f"analysis_{timestamp}.{format_type}"
                output_path = self.export_dir / filename

                success = self.export_manager.export_analysis_results(
                    self.current_results, format_type, output_path
                )

                return output_path if success else None

            def export_current_transformations(self) -> Optional[Path]:
                if not self.current_transformations:
                    return None

                timestamp = int(time.time())
                filename = f"transformations_{timestamp}.json"
                output_path = self.export_dir / filename

                success = self.export_manager.export_transformation_sequence(
                    self.current_transformations, output_path
                )

                return output_path if success else None

        # Execute GUI export workflow
        controller = MockGUIController(temp_dir)

        # Set up mock data
        analysis_results = {
            "results": {
                "mcts": {"score": 0.85, "iterations": 100},
                "genetic": {"score": 0.78, "iterations": 50}
            },
            "timestamp": time.time()
        }

        transformations = [
            {"id": 0, "operation": "xor", "timestamp": time.time()},
            {"id": 1, "operation": "add", "timestamp": time.time()}
        ]

        controller.set_analysis_results(analysis_results)
        controller.set_transformations(transformations)

        # Test analysis export
        json_export_path = controller.export_current_analysis("json")
        assert json_export_path is not None
        assert json_export_path.exists()

        csv_export_path = controller.export_current_analysis("csv")
        assert csv_export_path is not None
        assert csv_export_path.exists()

        # Test transformation export
        transform_export_path = controller.export_current_transformations()
        assert transform_export_path is not None
        assert transform_export_path.exists()

        # Verify export history
        assert len(controller.export_manager.export_history) == 3
        assert any(export["format"] == "json" for export in controller.export_manager.export_history)
        assert any(export["format"] == "csv" for export in controller.export_manager.export_history)
        assert any(export["format"] == "transformations" for export in controller.export_manager.export_history)

        # Verify exported content
        with open(json_export_path, 'r') as f:
            exported_json = json.load(f)
        assert "results" in exported_json
        assert "mcts" in exported_json["results"]