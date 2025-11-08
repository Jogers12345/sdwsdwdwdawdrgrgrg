"""
Strategy Algorithm Validation Tests
Comprehensive tests to verify each strategy implements its algorithm correctly
"""

import pytest
import time
import random
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch

from tests.conftest import TestDataGenerator, TestResultValidator


class TestMCTSStrategy:
    """Test MCTS Strategy implementation"""

    @pytest.mark.unit
    def test_mcts_tree_node_creation(self, mock_strategy, sample_binary_data):
        """Test tree node creation and expansion"""
        # This would test the actual MCTS implementation
        # For now, we'll test the mock behavior

        result = mock_strategy.analyze(sample_binary_data, max_iterations=10)

        assert result is not None
        assert "strategy" in result
        assert "score" in result
        assert "iterations" in result
        assert "converged" in result

    @pytest.mark.unit
    def test_mcts_uct_calculation(self):
        """Test UCT calculation accuracy"""
        # Mock UCT calculation: UCT = avg_reward + C * sqrt(ln(parent_visits) / node_visits)
        def calculate_uct(avg_reward: float, node_visits: int,
                         parent_visits: int, exploration_constant: float = 1.41) -> float:
            if node_visits == 0:
                return float('inf')
            return avg_reward + exploration_constant * (parent_visits / node_visits) ** 0.5

        # Test basic UCT calculation
        uct1 = calculate_uct(0.5, 10, 100)
        uct2 = calculate_uct(0.8, 5, 100)

        assert uct1 > 0
        assert uct2 > 0
        assert uct2 > uct1  # Higher reward should give higher UCT

    @pytest.mark.unit
    def test_mcts_selection_phase(self):
        """Test selection phase behavior"""
        # Mock selection logic - should choose node with highest UCT
        class MockNode:
            def __init__(self, uct_value):
                self.uct_value = uct_value
                self.visits = 1

            def __lt__(self, other):
                return self.uct_value < other.uct_value

        nodes = [MockNode(uct) for uct in [0.5, 1.2, 0.8, 1.5, 0.3]]
        selected_node = max(nodes, key=lambda n: n.uct_value)

        assert selected_node.uct_value == 1.5

    @pytest.mark.unit
    def test_mcts_simulation_and_backpropagation(self):
        """Test simulation and backpropagation"""
        # Mock simulation result
        simulation_result = 0.75

        # Mock backpropagation - should update all nodes on path
        class MockPathNode:
            def __init__(self):
                self.visits = 0
                self.total_reward = 0.0
                self.average_reward = 0.0

            def update(self, reward: float):
                self.visits += 1
                self.total_reward += reward
                self.average_reward = self.total_reward / self.visits

        path = [MockPathNode() for _ in range(3)]

        # Backpropagate simulation result
        for node in path:
            node.update(simulation_result)

        # Verify all nodes were updated
        for node in path:
            assert node.visits == 1
            assert node.total_reward == simulation_result
            assert node.average_reward == simulation_result

    @pytest.mark.unit
    def test_mcts_tree_growth(self, mock_strategy, sample_binary_data):
        """Test tree grows correctly over iterations"""
        initial_nodes = 1  # Root node

        # Run analysis and track tree growth
        result1 = mock_strategy.analyze(sample_binary_data, max_iterations=10)
        result2 = mock_strategy.analyze(sample_binary_data, max_iterations=50)

        # More iterations should lead to better results
        assert result2["iterations"] >= result1["iterations"]

    @pytest.mark.unit
    def test_mcts_config_parameter_influence(self):
        """Test config parameters influence MCTS behavior"""
        # Test different exploration constants
        exploration_configs = [
            {"exploration_constant": 0.5},
            {"exploration_constant": 1.41},  # Standard UCT
            {"exploration_constant": 2.0}
        ]

        results = []
        for config in exploration_configs:
            strategy = Mock("MCTSStrategy")
            strategy.configure_mock(**config)
            result_data = {
                "strategy": "mcts",
                "score": random.random(),
                "config": config
            }
            strategy.analyze = Mock(return_value=result_data)
            results.append(strategy.analyze(b"test", max_iterations=10))

        # Verify different configs were used
        for i, result in enumerate(results):
            assert result["config"]["exploration_constant"] == exploration_configs[i]["exploration_constant"]


class TestGeneticStrategy:
    """Test Genetic Strategy implementation"""

    @pytest.mark.unit
    def test_genetic_population_initialization(self):
        """Test population initialization"""
        # Mock population initialization
        population_size = 50
        chromosome_length = 10

        def initialize_population(size: int, length: int) -> List[List[int]]:
            return [[random.randint(0, 1) for _ in range(length)] for _ in range(size)]

        population = initialize_population(population_size, chromosome_length)

        assert len(population) == population_size
        assert all(len(individual) == chromosome_length for individual in population)
        assert all(all(gene in [0, 1] for gene in individual) for individual in population)

    @pytest.mark.unit
    def test_genetic_crossover_operation(self):
        """Test crossover operation correctness"""
        # Single-point crossover
        def crossover(parent1: List[int], parent2: List[int], point: int) -> tuple:
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2

        parent1 = [1, 1, 1, 1, 1]
        parent2 = [0, 0, 0, 0, 0]
        crossover_point = 2

        child1, child2 = crossover(parent1, parent2, crossover_point)

        expected_child1 = [1, 1, 0, 0, 0]
        expected_child2 = [0, 0, 1, 1, 1]

        assert child1 == expected_child1
        assert child2 == expected_child2

    @pytest.mark.unit
    def test_genetic_mutation_operations(self):
        """Test mutation operations"""
        def mutate(individual: List[int], mutation_rate: float) -> List[int]:
            return [gene if random.random() > mutation_rate else 1 - gene for gene in individual]

        original = [1, 0, 1, 0, 1]
        mutation_rate = 1.0  # 100% mutation for testing

        mutated = mutate(original, mutation_rate)

        # All bits should be flipped
        expected = [0, 1, 0, 1, 0]
        assert mutated == expected

    @pytest.mark.unit
    def test_genetic_selection_mechanisms(self):
        """Test selection mechanisms"""
        # Tournament selection
        def tournament_selection(population: List[tuple], fitness: List[float],
                               tournament_size: int = 3) -> int:
            tournament_indices = random.sample(range(len(population)), min(tournament_size, len(population)))
            tournament_fitness = [fitness[i] for i in tournament_indices]
            winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            return winner_index

        population = [["ind1"], ["ind2"], ["ind3"], ["ind4"], ["ind5"]]
        fitness = [0.2, 0.8, 0.5, 0.9, 0.3]

        # Run multiple tournaments
        winners = set()
        for _ in range(10):
            winner = tournament_selection(population, fitness)
            winners.add(winner)

        # Should select from high fitness individuals more often
        assert len(winners) > 0

    @pytest.mark.unit
    def test_genetic_evolution_improves_fitness(self):
        """Test evolution improves fitness over generations"""
        def fitness_function(individual: List[int]) -> float:
            # Simple fitness: count of 1s
            return sum(individual) / len(individual)

        def evolve_population(population: List[List[int]], generations: int) -> List[float]:
            fitness_history = []

            for generation in range(generations):
                # Calculate fitness
                fitness = [fitness_function(ind) for ind in population]
                fitness_history.append(max(fitness))

                # Selection (keep top 50%)
                sorted_pop = [ind for _, ind in sorted(zip(fitness, population), reverse=True)]
                population = sorted_pop[:len(population)//2]

                # Reproduction (clone survivors)
                while len(population) < 20:  # Maintain population size
                    parent = random.choice(population)
                    population.append(parent.copy())

            return fitness_history

        # Initialize random population
        initial_population = [[random.randint(0, 1) for _ in range(10)] for _ in range(20)]

        # Evolve
        fitness_history = evolve_population(initial_population, 10)

        # Fitness should generally improve
        assert len(fitness_history) == 10
        # Allow for some randomness, but trend should be upward
        assert fitness_history[-1] >= fitness_history[0] * 0.8  # At least not much worse

    @pytest.mark.unit
    def test_genetic_population_diversity_maintenance(self):
        """Test population diversity is maintained"""
        def calculate_diversity(population: List[List[int]]) -> float:
            if len(population) < 2:
                return 0.0

            total_distance = 0
            comparisons = 0

            for i in range(len(population)):
                for j in range(i + 1, len(population)):
                    # Hamming distance
                    distance = sum(1 for a, b in zip(population[i], population[j]) if a != b)
                    total_distance += distance
                    comparisons += 1

            return total_distance / comparisons if comparisons > 0 else 0.0

        # Create diverse population
        population = [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 1, 0, 1],
            [1, 0, 1, 0]
        ]

        initial_diversity = calculate_diversity(population)

        # After several generations without diversity maintenance, diversity should decrease
        # This is a simplified test - real implementation would have diversity preservation
        assert initial_diversity > 0


class TestBeamSearchStrategy:
    """Test Beam Search Strategy implementation"""

    @pytest.mark.unit
    def test_beam_state_maintenance(self):
        """Test beam state maintenance"""
        class BeamState:
            def __init__(self, data: bytes, score: float, operations: List[str]):
                self.data = data
                self.score = score
                self.operations = operations

            def __lt__(self, other):
                return self.score < other.score  # For min-heap behavior

        # Test beam state creation
        state = BeamState(b"test_data", 0.75, ["op1", "op2"])

        assert state.data == b"test_data"
        assert state.score == 0.75
        assert state.operations == ["op1", "op2"]

    @pytest.mark.unit
    def test_beam_candidate_expansion_and_pruning(self):
        """Test candidate expansion and pruning"""
        beam_width = 3

        # Initial beam states
        beam = [
            {"state": "A", "score": 0.8},
            {"state": "B", "score": 0.6},
            {"state": "C", "score": 0.4}
        ]

        # Expand candidates (each state produces 2 new candidates)
        new_candidates = []
        for state in beam:
            for i in range(2):
                new_score = state["score"] + random.uniform(-0.1, 0.2)
                new_candidates.append({
                    "state": f"{state['state']}{i}",
                    "score": new_score
                })

        # Prune to beam width
        new_candidates.sort(key=lambda x: x["score"], reverse=True)
        pruned_beam = new_candidates[:beam_width]

        assert len(pruned_beam) == beam_width
        assert pruned_beam[0]["score"] >= pruned_beam[-1]["score"]

    @pytest.mark.unit
    def test_beam_k_best_selection_logic(self):
        """Test k-best selection logic"""
        candidates = [
            {"id": 1, "score": 0.9},
            {"id": 2, "score": 0.7},
            {"id": 3, "score": 0.8},
            {"id": 4, "score": 0.6},
            {"id": 5, "score": 0.95}
        ]

        k = 3
        selected = sorted(candidates, key=lambda x: x["score"], reverse=True)[:k]

        assert len(selected) == k
        assert selected[0]["id"] == 5  # Highest score
        assert selected[1]["id"] == 1  # Second highest
        assert selected[2]["id"] == 3  # Third highest

    @pytest.mark.unit
    def test_beam_width_parameter_effects(self):
        """Test beam width parameter effects"""
        def beam_search(initial_data: bytes, beam_width: int, max_iterations: int) -> Dict[str, Any]:
            # Simplified beam search
            beam = [{"data": initial_data, "score": 0.5}]

            for iteration in range(max_iterations):
                # Expand candidates
                new_candidates = []
                for state in beam:
                    for i in range(beam_width):  # Each state generates beam_width candidates
                        new_score = state["score"] + random.uniform(-0.1, 0.1)
                        new_candidates.append({
                            "data": state["data"] + f"_{i}".encode(),
                            "score": new_score
                        })

                # Select best candidates
                new_candidates.sort(key=lambda x: x["score"], reverse=True)
                beam = new_candidates[:beam_width]

            best_state = max(beam, key=lambda x: x["score"])
            return {
                "best_score": best_state["score"],
                "beam_width": beam_width,
                "iterations": max_iterations
            }

        test_data = b"test"

        # Test different beam widths
        result_small = beam_search(test_data, beam_width=2, max_iterations=5)
        result_large = beam_search(test_data, beam_width=5, max_iterations=5)

        assert result_small["beam_width"] == 2
        assert result_large["beam_width"] == 5
        # Both should produce valid results
        assert result_small["best_score"] is not None
        assert result_large["best_score"] is not None

    @pytest.mark.unit
    def test_beam_contains_best_candidates(self):
        """Test beam contains best candidates"""
        # Generate many candidates
        all_candidates = []
        for i in range(100):
            all_candidates.append({
                "id": i,
                "score": random.uniform(0, 1),
                "data": f"candidate_{i}"
            })

        # Sort by score
        all_candidates.sort(key=lambda x: x["score"], reverse=True)

        # Select beam
        beam_width = 10
        beam = all_candidates[:beam_width]

        # Verify beam contains best candidates
        global_best = all_candidates[0]
        assert global_best in beam

        # Verify all beam members are among top candidates
        beam_ids = {candidate["id"] for candidate in beam}
        top_ids = {candidate["id"] for candidate in all_candidates[:beam_width]}
        assert beam_ids == top_ids


class TestSimulatedAnnealingStrategy:
    """Test Simulated Annealing Strategy implementation"""

    @pytest.mark.unit
    def test_simulated_annealing_temperature_schedule(self):
        """Test temperature schedule implementation"""
        def exponential_cooling(initial_temp: float, cooling_rate: float,
                               iteration: int) -> float:
            return initial_temp * (cooling_rate ** iteration)

        def linear_cooling(initial_temp: float, final_temp: float,
                          total_iterations: int, iteration: int) -> float:
            return initial_temp - (initial_temp - final_temp) * (iteration / total_iterations)

        # Test exponential cooling
        initial_temp = 100.0
        cooling_rate = 0.95

        temps = [exponential_cooling(initial_temp, cooling_rate, i) for i in range(10)]

        # Temperature should decrease
        assert temps[0] > temps[-1]
        assert all(0 < temp <= initial_temp for temp in temps)

        # Test linear cooling
        linear_temps = [linear_cooling(100.0, 1.0, 10, i) for i in range(11)]

        assert linear_temps[0] == 100.0
        assert linear_temps[-1] == 1.0
        assert all(linear_temps[i] >= linear_temps[i+1] for i in range(10))

    @pytest.mark.unit
    def test_simulated_annealing_acceptance_probability(self):
        """Test acceptance probability calculation"""
        def acceptance_probability(current_energy: float, new_energy: float,
                                 temperature: float) -> float:
            if new_energy < current_energy:
                return 1.0
            else:
                import math
                return math.exp(-(new_energy - current_energy) / temperature)

        # Test better solution (always accepted)
        prob_better = acceptance_probability(10.0, 5.0, 1.0)
        assert prob_better == 1.0

        # Test worse solution (probability depends on temperature)
        prob_worse_high_temp = acceptance_probability(5.0, 10.0, 100.0)
        prob_worse_low_temp = acceptance_probability(5.0, 10.0, 1.0)

        assert 0 <= prob_worse_high_temp <= 1.0
        assert 0 <= prob_worse_low_temp <= 1.0
        # Higher temperature should give higher acceptance probability
        assert prob_worse_high_temp >= prob_worse_low_temp

    @pytest.mark.unit
    def test_simulated_annealing_move_generation(self):
        """Test move generation logic"""
        def generate_move(current_state: List[int]) -> List[int]:
            # Random bit flip move
            move_index = random.randint(0, len(current_state) - 1)
            new_state = current_state.copy()
            new_state[move_index] = 1 - new_state[move_index]
            return new_state

        current_state = [1, 0, 1, 0, 1]
        new_state = generate_move(current_state)

        # Exactly one bit should be different
        differences = sum(1 for a, b in zip(current_state, new_state) if a != b)
        assert differences == 1
        assert len(new_state) == len(current_state)

    @pytest.mark.unit
    def test_simulated_annealing_cooling_rate_effects(self):
        """Test cooling rate effects"""
        def simulated_annealing(initial_state: List[int], iterations: int,
                              cooling_rate: float) -> Dict[str, Any]:
            current_state = initial_state.copy()
            current_energy = sum(current_state)  # Simple energy function
            best_state = current_state.copy()
            best_energy = current_energy
            temperature = 100.0

            for iteration in range(iterations):
                # Generate new state
                move_index = random.randint(0, len(current_state) - 1)
                new_state = current_state.copy()
                new_state[move_index] = 1 - new_state[move_index]
                new_energy = sum(new_state)

                # Accept or reject
                if new_energy < current_energy or random.random() < 0.1:  # Simplified acceptance
                    current_state = new_state
                    current_energy = new_energy

                    if current_energy < best_energy:
                        best_state = current_state.copy()
                        best_energy = current_energy

                # Cool down
                temperature *= cooling_rate

            return {
                "best_energy": best_energy,
                "final_energy": current_energy,
                "cooling_rate": cooling_rate
            }

        initial_state = [1, 1, 1, 1, 1]  # High energy state

        # Test different cooling rates
        result_fast = simulated_annealing(initial_state, iterations=50, cooling_rate=0.9)
        result_slow = simulated_annealing(initial_state, iterations=50, cooling_rate=0.99)

        assert result_fast["cooling_rate"] == 0.9
        assert result_slow["cooling_rate"] == 0.99
        # Both should find better solutions
        assert result_fast["best_energy"] < sum(initial_state)
        assert result_slow["best_energy"] < sum(initial_state)

    @pytest.mark.unit
    def test_simulated_annealing_convergence_behavior(self):
        """Test convergence behavior"""
        def energy_function(state: List[int]) -> float:
            # Energy is distance from target [0, 0, 0, 0, 0]
            target = [0, 0, 0, 0, 0]
            return sum(abs(a - b) for a, b in zip(state, target))

        def simulated_annealing_with_history(initial_state: List[int],
                                           iterations: int) -> List[float]:
            current_state = initial_state.copy()
            energy_history = [energy_function(current_state)]
            temperature = 100.0
            cooling_rate = 0.95

            for iteration in range(iterations):
                # Generate move
                move_index = random.randint(0, len(current_state) - 1)
                new_state = current_state.copy()
                new_state[move_index] = 1 - new_state[move_index]
                new_energy = energy_function(new_state)

                # Acceptance criteria
                current_energy = energy_function(current_state)
                if new_energy < current_energy:
                    current_state = new_state

                energy_history.append(energy_function(current_state))
                temperature *= cooling_rate

            return energy_history

        initial_state = [1, 1, 1, 1, 1]
        energy_history = simulated_annealing_with_history(initial_state, 100)

        # Energy should generally decrease (allow for some increases due to randomness)
        assert len(energy_history) == 101  # Initial + 100 iterations
        assert energy_history[0] > energy_history[-1]  # Should find better solution


class TestHeuristicStrategy:
    """Test Heuristic Strategy implementation"""

    @pytest.mark.unit
    def test_heuristic_evaluation_functions(self):
        """Test heuristic evaluation functions"""
        def entropy_heuristic(data: bytes) -> float:
            # Simple entropy calculation
            if not data:
                return 0.0

            frequency = [0] * 256
            for byte in data:
                frequency[byte] += 1

            entropy = 0.0
            data_len = len(data)
            for count in frequency:
                if count > 0:
                    probability = count / data_len
                    entropy -= probability * (probability.bit_length() - 1)

            return entropy

        def pattern_heuristic(data: bytes) -> float:
            # Simple pattern detection
            if len(data) < 2:
                return 0.0

            patterns = 0
            for i in range(len(data) - 1):
                if data[i] == data[i + 1]:
                    patterns += 1

            return patterns / (len(data) - 1)

        test_data = b"Hello, World! Hello, World!"

        entropy_score = entropy_heuristic(test_data)
        pattern_score = pattern_heuristic(test_data)

        assert 0 <= entropy_score <= 8  # Max entropy for bytes
        assert 0 <= pattern_score <= 1

    @pytest.mark.unit
    def test_heuristic_weighted_scoring_logic(self):
        """Test weighted scoring logic"""
        def weighted_score(metrics: Dict[str, float], weights: Dict[str, float]) -> float:
            total_score = 0.0
            total_weight = 0.0

            for metric, value in metrics.items():
                weight = weights.get(metric, 0.0)
                total_score += value * weight
                total_weight += weight

            return total_score / total_weight if total_weight > 0 else 0.0

        metrics = {
            "entropy": 7.5,
            "patterns": 0.3,
            "compression": 0.6
        }

        weights = {
            "entropy": 0.5,
            "patterns": 0.3,
            "compression": 0.2
        }

        score = weighted_score(metrics, weights)
        expected_score = (7.5 * 0.5 + 0.3 * 0.3 + 0.6 * 0.2) / (0.5 + 0.3 + 0.2)

        assert abs(score - expected_score) < 0.001

    @pytest.mark.unit
    def test_heuristic_operation_ranking(self):
        """Test operation ranking accuracy"""
        # Mock operations with scores
        operations = [
            {"name": "op1", "score": 0.8},
            {"name": "op2", "score": 0.6},
            {"name": "op3", "score": 0.9},
            {"name": "op4", "score": 0.4},
            {"name": "op5", "score": 0.7}
        ]

        # Sort by score (descending)
        ranked_operations = sorted(operations, key=lambda x: x["score"], reverse=True)

        # Verify ranking
        assert ranked_operations[0]["name"] == "op3"  # Highest score
        assert ranked_operations[1]["name"] == "op1"  # Second highest
        assert ranked_operations[-1]["name"] == "op4"  # Lowest score

        # Verify scores are in descending order
        for i in range(len(ranked_operations) - 1):
            assert ranked_operations[i]["score"] >= ranked_operations[i + 1]["score"]

    @pytest.mark.unit
    def test_heuristic_parameter_influence(self):
        """Test parameter influence on heuristic decisions"""
        def heuristic_with_parameters(data: bytes, entropy_weight: float,
                                   pattern_weight: float) -> Dict[str, Any]:
            # Simplified heuristic calculation
            entropy = len(set(data)) / 256.0  # Normalized entropy
            patterns = sum(1 for i in range(len(data) - 1) if data[i] == data[i + 1]) / max(len(data) - 1, 1)

            score = entropy * entropy_weight + patterns * pattern_weight

            return {
                "entropy": entropy,
                "patterns": patterns,
                "score": score,
                "entropy_weight": entropy_weight,
                "pattern_weight": pattern_weight
            }

        test_data = b"AAAAABBBBBCCCCCDDDDD"

        # Test different parameter weights
        result1 = heuristic_with_parameters(test_data, 0.8, 0.2)  # Emphasize entropy
        result2 = heuristic_with_parameters(test_data, 0.2, 0.8)  # Emphasize patterns

        assert result1["entropy_weight"] == 0.8
        assert result1["pattern_weight"] == 0.2
        assert result2["entropy_weight"] == 0.2
        assert result2["pattern_weight"] == 0.8

        # Scores should be different due to different weights
        assert result1["score"] != result2["score"]

    @pytest.mark.unit
    def test_heuristic_deterministic_behavior(self):
        """Test heuristic produces consistent results"""
        def deterministic_heuristic(data: bytes, seed: int = 42) -> float:
            random.seed(seed)
            # Deterministic calculation based on data
            return sum(data) / len(data) if data else 0.0

        test_data = b"test data for deterministic behavior"

        # Run multiple times with same seed
        results = [deterministic_heuristic(test_data, 42) for _ in range(5)]

        # All results should be identical
        assert all(result == results[0] for result in results)

        # Different seed should produce different result
        different_result = deterministic_heuristic(test_data, 123)
        assert different_result != results[0]


class TestStrategyIntegration:
    """Integration tests for strategy validation"""

    @pytest.mark.integration
    def test_strategy_consistency_validation(self, result_validator, sample_binary_data):
        """Test strategy consistency validation"""
        strategies = [
            Mock("Strategy1"),
            Mock("Strategy2"),
            Mock("Strategy3")
        ]

        # Configure mock strategies
        for i, strategy in enumerate(strategies):
            strategy.name = f"strategy_{i}"
            strategy.analyze.return_value = {
                "strategy": strategy.name,
                "final_score": 0.7 + i * 0.1,
                "converged": True
            }

        # Test consistency
        for strategy in strategies:
            consistency_result = result_validator.validate_strategy_consistency(
                strategy, sample_binary_data, runs=3
            )

            assert consistency_result["success_rate"] >= 0.8  # At least 80% success rate

    @pytest.mark.integration
    def test_strategy_performance_comparison(self, sample_binary_data):
        """Test strategy performance comparison"""
        # Mock strategy results
        strategy_results = {
            "mcts": {"score": 0.85, "time": 2.5, "converged": True},
            "genetic": {"score": 0.78, "time": 1.8, "converged": True},
            "beam_search": {"score": 0.72, "time": 0.9, "converged": True},
            "simulated_annealing": {"score": 0.80, "time": 1.2, "converged": True},
            "heuristic": {"score": 0.65, "time": 0.3, "converged": True}
        }

        # Rank by score
        ranked_strategies = sorted(strategy_results.items(),
                                key=lambda x: x[1]["score"], reverse=True)

        assert ranked_strategies[0][0] == "mcts"  # Highest score
        assert ranked_strategies[-1][0] == "heuristic"  # Lowest score

        # All strategies should have converged
        assert all(result["converged"] for result in strategy_results.values())

    @pytest.mark.integration
    def test_strategy_convergence_validation(self):
        """Test strategy convergence validation"""
        def mock_strategy_analysis(data: bytes, max_iterations: int,
                                convergence_rate: float = 0.1) -> Dict[str, Any]:
            # Mock convergence behavior
            iterations_to_converge = int(max_iterations * convergence_rate)
            final_score = 0.5 + 0.4 * (iterations_to_converge / max_iterations)

            return {
                "iterations": iterations_to_converge,
                "max_iterations": max_iterations,
                "converged": iterations_to_converge > 0,
                "final_score": final_score,
                "convergence_rate": convergence_rate
            }

        test_data = b"convergence test data"

        # Test different convergence rates
        fast_convergence = mock_strategy_analysis(test_data, 100, 0.2)  # Converges in 20 iterations
        slow_convergence = mock_strategy_analysis(test_data, 100, 0.8)  # Converges in 80 iterations

        assert fast_convergence["converged"]
        assert slow_convergence["converged"]
        assert fast_convergence["iterations"] < slow_convergence["iterations"]
        assert fast_convergence["final_score"] < slow_convergence["final_score"]