"""
Multi-Objective Policy for BSEE
Policy that balances multiple optimization objectives simultaneously
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import json
from pathlib import Path
from collections import defaultdict, deque
import time
from enum import Enum
from dataclasses import dataclass

from bsee.engine.state import State


class ObjectiveType(Enum):
    """Different optimization objectives"""
    SCORE_IMPROVEMENT = "score_improvement"
    COST_EFFICIENCY = "cost_efficiency"
    TIME_EFFICIENCY = "time_efficiency"
    MEMORY_EFFICIENCY = "memory_efficiency"
    CONVERGENCE_SPEED = "convergence_speed"
    STABILITY = "stability"
    EXPLORATION = "exploration"
    QUALITY = "quality"


@dataclass
class ObjectiveWeight:
    """Weight for optimization objective"""
    objective: ObjectiveType
    weight: float
    direction: str  # 'maximize' or 'minimize'
    priority: int   # Lower number = higher priority


class MultiObjectivePolicy:
    """
    Multi-objective policy that optimizes across multiple dimensions
    using Pareto optimality and weighted sum approaches.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Objectives configuration
        self.objectives = self._initialize_objectives(config.get('objectives', {}))
        self.optimization_method = config.get('optimization_method', 'pareto')
        self.pareto_epsilon = config.get('pareto_epsilon', 0.01)

        # Strategy selection parameters
        self.strategy_scores = defaultdict(lambda: defaultdict(float))
        self.performance_history = defaultdict(list)
        self.pareto_solutions = []

        # Dynamic weight adjustment
        self.adaptive_weights = config.get('adaptive_weights', True)
        self.weight_adaptation_rate = config.get('weight_adaptation_rate', 0.05)
        self.performance_window = config.get('performance_window', 30)

        # Constraint handling
        self.constraints = self._initialize_constraints(config.get('constraints', {}))
        self.constraint_mode = config.get('constraint_mode', 'soft')

        # Exploration vs exploitation
        self.exploration_rate = config.get('exploration_rate', 0.1)
        self.exploration_decay = config.get('exploration_decay', 0.995)
        self.min_exploration_rate = config.get('min_exploration_rate', 0.01)

        # Performance tracking
        self.objective_values = defaultdict(list)
        self.strategy_effectiveness = defaultdict(lambda: 1.0)
        self.learning_history = []

    def _initialize_objectives(self, objectives_config: Dict[str, Any]) -> List[ObjectiveWeight]:
        """Initialize optimization objectives"""
        default_objectives = [
            ObjectiveWeight(ObjectiveType.SCORE_IMPROVEMENT, 0.4, 'maximize', 1),
            ObjectiveWeight(ObjectiveType.COST_EFFICIENCY, 0.2, 'maximize', 2),
            ObjectiveWeight(ObjectiveType.TIME_EFFICIENCY, 0.15, 'maximize', 3),
            ObjectiveWeight(ObjectiveType.MEMORY_EFFICIENCY, 0.1, 'maximize', 4),
            ObjectiveWeight(ObjectiveType.STABILITY, 0.1, 'maximize', 5),
            ObjectiveWeight(ObjectiveType.EXPLORATION, 0.05, 'maximize', 6)
        ]

        # Override with config if provided
        if objectives_config:
            configured_objectives = []
            for obj_config in objectives_config:
                try:
                    obj_type = ObjectiveType(obj_config['type'])
                    weight = obj_config.get('weight', 0.1)
                    direction = obj_config.get('direction', 'maximize')
                    priority = obj_config.get('priority', 5)

                    configured_objectives.append(
                        ObjectiveWeight(obj_type, weight, direction, priority)
                    )
                except (KeyError, ValueError):
                    continue

            if configured_objectives:
                default_objectives = configured_objectives

        # Normalize weights
        total_weight = sum(obj.weight for obj in default_objectives)
        if total_weight > 0:
            for obj in default_objectives:
                obj.weight /= total_weight

        return default_objectives

    def _initialize_constraints(self, constraints_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize optimization constraints"""
        default_constraints = {
            'max_cost_per_operation': 100.0,
            'max_time_per_operation': 5.0,
            'min_improvement_threshold': 0.001,
            'max_consecutive_failures': 10,
            'memory_limit_mb': 512.0
        }

        default_constraints.update(constraints_config)
        return default_constraints

    def calculate_objective_scores(self, initial_state: State, final_state: State,
                                execution_time: float, operations_used: List[str],
                                memory_usage: float = 0) -> Dict[ObjectiveType, float]:
        """Calculate scores for all optimization objectives"""
        scores = {}

        for obj_weight in self.objectives:
            obj_type = obj_weight.objective

            if obj_type == ObjectiveType.SCORE_IMPROVEMENT:
                score = final_state.current_score - initial_state.current_score

            elif obj_type == ObjectiveType.COST_EFFICIENCY:
                total_cost = sum(getattr(op, 'cost', 1.0) for op in operations_used)
                score_improvement = final_state.current_score - initial_state.current_score
                score = score_improvement / (total_cost + 0.001)

            elif obj_type == ObjectiveType.TIME_EFFICIENCY:
                score_improvement = final_state.current_score - initial_state.current_score
                score = score_improvement / (execution_time + 0.001)

            elif obj_type == ObjectiveType.MEMORY_EFFICIENCY:
                score_improvement = final_state.current_score - initial_state.current_score
                score = score_improvement / (memory_usage + 0.001)

            elif obj_type == ObjectiveType.CONVERGENCE_SPEED:
                # How quickly we reached the final state
                score = 1.0 / (len(operations_used) + 1.0)

            elif obj_type == ObjectiveType.STABILITY:
                # How consistent the improvements were
                if len(operations_used) > 1:
                    # Simplified stability calculation
                    score = 1.0 - np.std([1.0] * len(operations_used))  # Placeholder
                else:
                    score = 1.0

            elif obj_type == ObjectiveType.EXPLORATION:
                # Diversity of operations used
                unique_operations = len(set(operations_used))
                score = unique_operations / max(1, len(operations_used))

            elif obj_type == ObjectiveType.QUALITY:
                # Overall quality of the solution
                score = final_state.current_score / 100.0  # Normalize

            else:
                score = 0.0

            scores[obj_type] = score

        return scores

    def calculate_composite_score(self, objective_scores: Dict[ObjectiveType, float]) -> float:
        """Calculate composite score from objective scores"""
        if self.optimization_method == 'weighted_sum':
            return self._weighted_sum_score(objective_scores)
        elif self.optimization_method == 'pareto_optimal':
            return self._pareto_optimal_score(objective_scores)
        elif self.optimization_method == 'lexicographic':
            return self._lexicographic_score(objective_scores)
        else:
            return self._weighted_sum_score(objective_scores)

    def _weighted_sum_score(self, objective_scores: Dict[ObjectiveType, float]) -> float:
        """Calculate weighted sum score"""
        total_score = 0.0

        for obj_weight in self.objectives:
            obj_type = obj_weight.objective
            if obj_type in objective_scores:
                score = objective_scores[obj_type]

                # Handle minimization objectives
                if obj_weight.direction == 'minimize':
                    score = -score

                total_score += obj_weight.weight * score

        return total_score

    def _pareto_optimal_score(self, objective_scores: Dict[ObjectiveType, float]) -> float:
        """Calculate Pareto-optimal score"""
        # Check if current solution is Pareto-optimal
        is_pareto = self._is_pareto_optimal(objective_scores)

        if is_pareto:
            self.pareto_solutions.append({
                'scores': objective_scores.copy(),
                'timestamp': time.time()
            })

        # Apply Pareto bonus
        pareto_bonus = 1.1 if is_pareto else 1.0

        return self._weighted_sum_score(objective_scores) * pareto_bonus

    def _lexicographic_score(self, objective_scores: Dict[ObjectiveType, float]) -> float:
        """Calculate lexicographic score (prioritize by priority)"""
        # Sort objectives by priority
        sorted_objectives = sorted(self.objectives, key=lambda x: x.priority)

        # Find first objective with different scores
        for obj_weight in sorted_objectives:
            obj_type = obj_weight.objective
            if obj_type in objective_scores:
                score = objective_scores[obj_type]

                if obj_weight.direction == 'minimize':
                    score = -score

                return obj_weight.weight * score

        return 0.0

    def _is_pareto_optimal(self, objective_scores: Dict[ObjectiveType, float]) -> bool:
        """Check if solution is Pareto-optimal"""
        if not self.pareto_solutions:
            return True

        # Check against recent Pareto solutions
        recent_solutions = self.pareto_solutions[-20:]

        for solution in recent_solutions:
            other_scores = solution['scores']
            dominates = True

            for obj_weight in self.objectives:
                obj_type = obj_weight.objective
                if obj_type in objective_scores and obj_type in other_scores:
                    current_score = objective_scores[obj_type]
                    other_score = other_scores[obj_type]

                    if obj_weight.direction == 'maximize':
                        if current_score < other_score - self.pareto_epsilon:
                            dominates = False
                            break
                    else:  # minimize
                        if current_score > other_score + self.pareto_epsilon:
                            dominates = False
                            break

            if dominates:
                return False

        return True

    def select_strategy(self, available_strategies: List[str], state: State) -> str:
        """Select strategy based on multi-objective optimization"""
        if not available_strategies:
            return "greedy"  # Default fallback

        # Exploration vs exploitation
        if np.random.random() < self.exploration_rate:
            return np.random.choice(available_strategies)

        # Calculate expected scores for each strategy
        strategy_scores = {}

        for strategy in available_strategies:
            # Get historical performance
            historical_scores = self.strategy_scores.get(strategy, {})

            # Calculate expected composite score
            expected_objective_scores = {}
            for obj_weight in self.objectives:
                obj_type = obj_weight.objective
                historical_score = historical_scores.get(obj_type, 0.0)
                expected_objective_scores[obj_type] = historical_score

            composite_score = self.calculate_composite_score(expected_objective_scores)
            strategy_scores[strategy] = composite_score

        # Select best strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]

        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration_rate,
                                  self.exploration_rate * self.exploration_decay)

        return best_strategy

    def update_strategy_performance(self, strategy: str, initial_state: State,
                                 final_state: State, execution_time: float,
                                 operations_used: List[str], memory_usage: float = 0):
        """Update strategy performance based on results"""
        # Calculate objective scores
        objective_scores = self.calculate_objective_scores(
            initial_state, final_state, execution_time, operations_used, memory_usage
        )

        # Update strategy scores
        for obj_type, score in objective_scores.items():
            current_score = self.strategy_scores[strategy][obj_type]
            # Exponential moving average
            alpha = 0.1  # Learning rate
            new_score = alpha * score + (1 - alpha) * current_score
            self.strategy_scores[strategy][obj_type] = new_score

        # Store in performance history
        performance_record = {
            'strategy': strategy,
            'objective_scores': objective_scores,
            'composite_score': self.calculate_composite_score(objective_scores),
            'execution_time': execution_time,
            'operations_count': len(operations_used),
            'memory_usage': memory_usage,
            'timestamp': time.time()
        }

        self.performance_history[strategy].append(performance_record)

        # Update objective values tracking
        for obj_type, score in objective_scores.items():
            self.objective_values[obj_type].append(score)

        # Adapt weights if enabled
        if self.adaptive_weights:
            self._adapt_weights(objective_scores)

        # Record learning history
        self.learning_history.append(performance_record)

    def _adapt_weights(self, current_objective_scores: Dict[ObjectiveType, float]):
        """Adapt objective weights based on performance"""
        # Calculate recent performance trends
        for obj_weight in self.objectives:
            obj_type = obj_weight.objective
            if obj_type in self.objective_values:
                recent_values = self.objective_values[obj_type][-self.performance_window:]

                if len(recent_values) >= 5:
                    # Calculate trend
                    trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]

                    # Adjust weight based on trend
                    if trend < 0:  # Performance declining
                        # Increase weight to focus more on this objective
                        adjustment = self.weight_adaptation_rate * abs(trend)
                        obj_weight.weight = min(1.0, obj_weight.weight + adjustment)
                    elif trend > 0:  # Performance improving
                        # Can slightly decrease weight
                        adjustment = self.weight_adaptation_rate * trend * 0.1
                        obj_weight.weight = max(0.01, obj_weight.weight - adjustment)

        # Re-normalize weights
        total_weight = sum(obj.weight for obj in self.objectives)
        if total_weight > 0:
            for obj_weight in self.objectives:
                obj_weight.weight /= total_weight

    def check_constraints(self, strategy: str, state: State, proposed_operations: List[str]) -> bool:
        """Check if proposed operations violate constraints"""
        if self.constraint_mode == 'none':
            return True

        violations = []

        # Cost constraint
        estimated_cost = sum(getattr(op, 'cost', 10.0) for op in proposed_operations)
        if estimated_cost > self.constraints['max_cost_per_operation'] * len(proposed_operations):
            violations.append('cost')

        # Time constraint
        estimated_time = len(proposed_operations) * self.constraints['max_time_per_operation']
        if estimated_time > self.constraints['max_time_per_operation'] * len(proposed_operations):
            violations.append('time')

        # Memory constraint
        if state.current_cost > self.constraints['memory_limit_mb']:
            violations.append('memory')

        # Improvement constraint
        if state.current_score < self.constraints['min_improvement_threshold']:
            violations.append('improvement')

        if violations and self.constraint_mode == 'hard':
            return False
        elif violations:
            # Soft constraints - apply penalty
            return True

        return True

    def get_objective_analysis(self) -> Dict[str, Any]:
        """Get analysis of objective performance"""
        analysis = {}

        for obj_weight in self.objectives:
            obj_type = obj_weight.objective
            values = self.objective_values[obj_type]

            if values:
                recent_values = values[-30:] if len(values) > 30 else values

                analysis[obj_type.value] = {
                    'current_weight': obj_weight.weight,
                    'direction': obj_weight.direction,
                    'priority': obj_weight.priority,
                    'current_value': recent_values[-1] if recent_values else 0,
                    'average': np.mean(recent_values),
                    'std_dev': np.std(recent_values),
                    'trend': 'improving' if len(recent_values) > 1 and recent_values[-1] > recent_values[0] else 'stable',
                    'values': recent_values[-10:]  # Last 10 values
                }

        analysis['optimization_method'] = self.optimization_method
        analysis['pareto_solutions_count'] = len(self.pareto_solutions)
        analysis['exploration_rate'] = self.exploration_rate

        return analysis

    def get_strategy_ranking(self) -> List[Tuple[str, float]]:
        """Get strategies ranked by composite performance"""
        strategy_rankings = []

        for strategy in self.strategy_scores:
            # Calculate average composite score
            historical_scores = self.strategy_scores[strategy]
            expected_scores = {}

            for obj_weight in self.objectives:
                obj_type = obj_weight.objective
                expected_scores[obj_type] = historical_scores.get(obj_type, 0.0)

            composite_score = self.calculate_composite_score(expected_scores)
            strategy_rankings.append((strategy, composite_score))

        # Sort by composite score (descending)
        strategy_rankings.sort(key=lambda x: x[1], reverse=True)

        return strategy_rankings

    def save_policy(self, filepath: str):
        """Save multi-objective policy"""
        policy_data = {
            'config': self.config,
            'objectives': [
                {
                    'type': obj.objective.value,
                    'weight': obj.weight,
                    'direction': obj.direction,
                    'priority': obj.priority
                } for obj in self.objectives
            ],
            'strategy_scores': {
                strategy: dict(scores) for strategy, scores in self.strategy_scores.items()
            },
            'constraints': self.constraints,
            'constraint_mode': self.constraint_mode,
            'optimization_method': self.optimization_method,
            'pareto_solutions': self.pareto_solutions[-50:],  # Last 50
            'learning_history': self.learning_history[-100:],  # Last 100
            'exploration_rate': self.exploration_rate
        }

        with open(filepath, 'w') as f:
            json.dump(policy_data, f, indent=2)

    def load_policy(self, filepath: str):
        """Load multi-objective policy"""
        with open(filepath, 'r') as f:
            policy_data = json.load(f)

        self.config = policy_data['config']

        # Load objectives
        self.objectives = []
        for obj_data in policy_data['objectives']:
            try:
                obj_type = ObjectiveType(obj_data['type'])
                obj = ObjectiveWeight(
                    objective=obj_type,
                    weight=obj_data['weight'],
                    direction=obj_data['direction'],
                    priority=obj_data['priority']
                )
                self.objectives.append(obj)
            except (ValueError, KeyError):
                continue

        # Load strategy scores
        self.strategy_scores = defaultdict(lambda: defaultdict(float))
        for strategy, scores in policy_data['strategy_scores'].items():
            self.strategy_scores[strategy] = scores

        # Load other parameters
        self.constraints = policy_data['constraints']
        self.constraint_mode = policy_data['constraint_mode']
        self.optimization_method = policy_data['optimization_method']
        self.pareto_solutions = policy_data.get('pareto_solutions', [])
        self.learning_history = policy_data.get('learning_history', [])
        self.exploration_rate = policy_data.get('exploration_rate', 0.1)

    def export_analysis_report(self, filepath: str):
        """Export comprehensive analysis report"""
        report = {
            'timestamp': time.time(),
            'policy_type': 'MultiObjectivePolicy',
            'objective_analysis': self.get_objective_analysis(),
            'strategy_ranking': self.get_strategy_ranking(),
            'pareto_analysis': self._analyze_pareto_solutions(),
            'constraint_analysis': self._analyze_constraints(),
            'recommendations': self._generate_recommendations()
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

    def _analyze_pareto_solutions(self) -> Dict[str, Any]:
        """Analyze Pareto-optimal solutions"""
        if not self.pareto_solutions:
            return {'total_solutions': 0, 'analysis': 'No Pareto solutions found'}

        recent_solutions = self.pareto_solutions[-20:]

        # Calculate objective ranges
        objective_ranges = {}
        for obj_weight in self.objectives:
            obj_type = obj_weight.objective
            values = [sol['scores'].get(obj_type, 0) for sol in recent_solutions if obj_type in sol['scores']]

            if values:
                objective_ranges[obj_type.value] = {
                    'min': min(values),
                    'max': max(values),
                    'average': np.mean(values),
                    'std_dev': np.std(values)
                }

        return {
            'total_solutions': len(self.pareto_solutions),
            'recent_solutions': len(recent_solutions),
            'objective_ranges': objective_ranges,
            'solution_frequency': len(recent_solutions) / max(1, recent_solutions[-1]['timestamp'] - recent_solutions[0]['timestamp']) * 3600  # per hour
        }

    def _analyze_constraints(self) -> Dict[str, Any]:
        """Analyze constraint violations"""
        total_analyses = len(self.learning_history)
        if total_analyses == 0:
            return {'total_analyses': 0, 'violation_rate': 0}

        # Estimate violations based on performance patterns
        estimated_violations = sum(1 for record in self.learning_history
                                 if record.get('composite_score', 0) < 0)

        return {
            'total_analyses': total_analyses,
            'estimated_violations': estimated_violations,
            'violation_rate': estimated_violations / total_analyses,
            'constraint_mode': self.constraint_mode,
            'active_constraints': list(self.constraints.keys())
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate policy recommendations"""
        recommendations = []

        objective_analysis = self.get_objective_analysis()

        # Check for poorly performing objectives
        for obj_name, obj_data in objective_analysis.items():
            if isinstance(obj_data, dict) and 'trend' in obj_data:
                if obj_data['trend'] == 'stable' and obj_data.get('current_weight', 0) > 0.2:
                    recommendations.append(f"Consider adjusting weight for {obj_name} - performance is stable")

        # Check exploration rate
        if self.exploration_rate > 0.2:
            recommendations.append("High exploration rate - consider reducing for more consistent results")
        elif self.exploration_rate < 0.05:
            recommendations.append("Low exploration rate - consider increasing for better discovery")

        # Check Pareto solutions
        if len(self.pareto_solutions) < 5:
            recommendations.append("Few Pareto solutions found - consider adjusting objectives or constraints")

        # Check strategy diversity
        strategy_ranking = self.get_strategy_ranking()
        if len(strategy_ranking) > 1:
            top_score = strategy_ranking[0][1]
            second_score = strategy_ranking[1][1]
            if top_score > second_score * 2:
                recommendations.append("Strategy dominance detected - consider balancing strategy selection")

        return recommendations