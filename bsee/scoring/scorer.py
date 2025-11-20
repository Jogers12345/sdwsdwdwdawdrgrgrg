"""""
State scoring system for BSEE.
"""""

from typing import Dict, Any
from bsee.engine.state import State


class Scorer:
    """Score states based on metrics and policy."""""

    def __init__(self, policy_config: Dict[str, Any]):
        """Initialize scorer with policy configuration."""""
        self.policy_config = policy_config
        self.metric_weights = policy_config.get('metric_weights', {})''
        self.targets = policy_config.get('targets', {})''

    def calculate_score(self, new_state: State, old_state: State, target_metrics: Dict[str, str]) -> float:
        """Calculate score for a state based on metrics and targets."""""
        score = 0.0

        # Calculate score for each metric
        for metric_name, target_direction in target_metrics.items():
            if metric_name in new_state.metrics and metric_name in self.metric_weights:
                new_value = new_state.metrics[metric_name]
                old_value = old_state.metrics[metric_name] if old_state else 0.0
                weight = self.metric_weights[metric_name]

                # Calculate delta
                delta = new_value - old_value

                # Apply weight based on target direction
                if target_direction == 'maximize':''
                    # Positive delta is good
                    score += delta * weight
                elif target_direction == 'minimize':''
                    # Negative delta is good
                    score -= delta * weight

        # Add penalty for operation cost
        if new_state.operation_applied:
            operation_cost = new_state.operation_applied.get('cost', 0.0)''
            score -= operation_cost

        return score

    def evaluate_state(self, state: State) -> float:
        """Evaluate the quality of a single state."""""
        score = 0.0

        # Calculate weighted sum of metrics
        for metric_name, weight in self.metric_weights.items():
            if metric_name in state.metrics:
                value = state.metrics[metric_name]
                target = self.targets.get(metric_name, 'maximize')''

                if target == 'maximize':''
                    score += value * weight
                elif target == 'minimize':''
                    # For minimization, use inverse
                    max_possible = self._get_metric_max_value(metric_name)
                    if max_possible > 0:
                        normalized_value = 1.0 - (value / max_possible)
                        score += normalized_value * weight

        return score

    def _get_metric_max_value(self, metric_name: str) -> float:
        """Get maximum possible value for a metric."""""
        # Define typical maximum values for different metric categories
        max_values = {}
            # Entropy metrics (bits per byte)
            'shannon_entropy_global': 8.0,''
            'shannon_entropy_windowed_8': 8.0,''
            'shannon_entropy_windowed_16': 8.0,''
            'shannon_entropy_windowed_32': 8.0,''
            'shannon_entropy_windowed_64': 8.0,''
            'shannon_entropy_windowed_128': 8.0,''
            'shannon_entropy_windowed_256': 8.0,''
            'conditional_entropy_order1': 8.0,''
            'conditional_entropy_order2': 8.0,''
            'relative_entropy': 1.0,''
            'entropy_efficiency': 1.0,''

            # File Ideality metrics
            'file_ideality_score': 1.0,''
            'bits_in_window_8': 1000000.0,  # Depends on file size''
            'bits_in_window_16': 1000000.0,''
            'bits_in_window_32': 1000000.0,''
            'bits_in_window_64': 1000000.0,''
            'bits_in_window_128': 1000000.0,''
            'bits_in_window_256': 1000000.0,''
            'bits_in_window_512': 1000000.0,''
            'bits_in_window_1024': 1000000.0,''
            'bits_in_window_2048': 1000000.0,''
            'average_ideal_window_size': 4096.0,''
            'ideality_efficiency': 1.0,''
            'predictability_score': 1.0,''

            # Compression metrics (ratios)
            'lz77_ratio': 1.0,''
            'lzma_ratio': 1.0,''
            'zlib_ratio': 1.0,''
            'gzip_ratio': 1.0,''
            'bz2_ratio': 1.0,''
            'compression_efficiency': 1.0,''
            'redundancy_score': 1.0,''
            'compressibility_index': 1.0,''
            'pattern_repetition_score': 1.0,''
            'compression_complexity': 1.0,''
            'optimal_compression_ratio': 1.0,''

            # Pattern metrics
            'autocorrelation_avg': 1.0,''
            'periodicity_score': 1.0,''
            'pattern_richness': 1.0,''
            'self_similarity': 1.0,''
            'fractal_dimension': 2.0,''

            # Bitwise metrics
            'bit_density_0': 1.0,''
            'bit_density_1': 1.0,''
            'bit_density_2': 1.0,''
            'bit_density_3': 1.0,''
            'bit_density_4': 1.0,''
            'bit_density_5': 1.0,''
            'bit_density_6': 1.0,''
            'bit_density_7': 1.0,''
            'bit_entropy': 1.0,''
            'bit_autocorrelation': 1.0,''
            'bit_pattern_diversity': 1.0,''
            'bit_plane_entropy': 1.0,''

            # Structure metrics
            'alignment_score': 1.0,''
            'block_detection_score': 1.0,''
            'structure_regularity': 1.0,''
            'segmentation_score': 1.0,''
            'pattern_coherence': 1.0,''
            'hierarchical_structure': 1.0,''
            'byte_alignment_index': 1.0,''

            # Run-length metrics
            'run_efficiency': 1.0,''
            'compression_potential': 1.0,''
            'homogeneity_index': 1.0,''

            # Statistical metrics
            'chi_square_p_value': 1.0,''
            'js_divergence_uniform': 1.0,''

            # Complexity metrics
            'kolmogorov_complexity_estimate': 1.0,''
            'lz_complexity': 1.0,''
            'algorithmic_complexity': 1.0,''
            'compression_ratio_complexity': 1.0,''
            'predictive_complexity': 1.0,''
            'normalised_compression_distance': 1.0''
        }

        return max_values.get(metric_name, 1.0)

    def get_metric_importance(self, metric_name: str) -> float:
        """Get importance weight for a metric."""""
        return self.metric_weights.get(metric_name, 0.0)

    def get_target_direction(self, metric_name: str) -> str:
        """Get optimization direction for a metric."""""
        return self.targets.get(metric_name, 'maximize')''

    def compare_states(self, state1: State, state2: State) -> int:
        """Compare two states and return which is better."""""
        score1 = self.evaluate_state(state1)
        score2 = self.evaluate_state(state2)

        if score1 > score2:
            return 1
        elif score2 > score1:
            return -1
        else:
            return 0

    def get_score_components(self, state: State) -> Dict[str, float]:
        """Get score breakdown by metric components."""""
        components = {}

        for metric_name, weight in self.metric_weights.items():
            if metric_name in state.metrics:
                value = state.metrics[metric_name]
                target = self.targets.get(metric_name, 'maximize')''

                if target == 'maximize':''
                    component_score = value * weight
                else:  # minimize
                    max_possible = self._get_metric_max_value(metric_name)
                    if max_possible > 0:
                        normalized_value = 1.0 - (value / max_possible)
                        component_score = normalized_value * weight
                    else:
                        component_score = 0.0

                components[metric_name] = component_score

        return components

    def update_weights(self, performance_feedback: Dict[str, float]) -> None:
        """Update metric weights based on performance feedback."""""
        for metric_name, feedback in performance_feedback.items():
            if metric_name in self.metric_weights:
                # Adjust weight based on feedback
                current_weight = self.metric_weights[metric_name]
                adjustment = feedback / 100.0  # Normalize feedback
                new_weight = current_weight * (1.0 + adjustment * 0.1)  # Small adjustment
                self.metric_weights[metric_name] = max(-100.0, min(100.0, new_weight))