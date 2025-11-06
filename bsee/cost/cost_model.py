"""
Dynamic cost model for BSEE operations.
"""

from typing import Dict, List, Any
from bsee.engine.history import OperationEntry


class CostModel:
    """Dynamic cost calculation for operations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize cost model with configuration."""
        self.config = config
        self.base_costs = config.get('base_costs', {})
        self.cost_modifiers = config.get('cost_modifiers', {})

        # Default costs if not specified in config
        self._setup_default_costs()

    def _setup_default_costs(self) -> None:
        """Setup default operation costs."""
        default_costs = {
            # Bitwise operations
            'xor_constant': 1.0,
            'xor_range': 2.0,
            'not_bytes': 1.0,
            'and_constant': 1.5,
            'or_constant': 1.5,
            'rotate_left': 1.5,
            'rotate_right': 1.5,
            'shift_left': 1.0,
            'shift_right': 1.0,
            'swap_nibbles': 2.0,
            'swap_bits': 2.5,
            'reverse_bits': 2.0,
            'clear_bit': 1.0,
            'set_bit': 1.0,
            'toggle_bit': 1.5,
            'mask_bits': 1.5,
            'extract_high_nibble': 3.0,
            'extract_low_nibble': 3.0,
            'interleave_bits': 5.0,
            'deinterleave_bits': 5.0,

            # Reordering operations
            'reverse_bytes': 2.0,
            'shuffle_bytes': 4.0,
            'byte_swap': 3.0,
            'block_reverse': 3.0,
            'rotate_bytes': 2.5,
            'transpose_2d': 4.0,
            'perfect_shuffle': 4.0,
            'unshuffle': 4.0,
            'block_shuffle': 5.0,
            'interleave_blocks': 5.0,
            'deinterleave_blocks': 5.0,

            # Delta operations
            'delta_encode': 3.0,
            'delta_decode': 3.0,
            'adaptive_delta': 4.0,
            'block_delta': 3.5,
            'windowed_delta': 4.0,

            # Substitution operations
            'caesar_cipher': 2.5,
            'xor_key': 3.0,
            'byte_substitution': 4.0,
            'sbox_substitution': 4.0,
            'vigenere_cipher': 3.5,
            'affine_transform': 4.0,

            # Transform operations
            'burrows_wheeler': 6.0,
            'bitplane_extract': 5.0,
            'move_to_front': 4.0,
            'walsh_hadamard': 5.5,

            # Custom operations
            'base64_encode': 4.0,
            'base64_decode': 4.0,
            'dna_encoding': 6.0,
            'dna_decoding': 6.0,
            'data_embedding': 7.0
        }

        # Merge with user-provided costs
        for op_name, cost in default_costs.items():
            if op_name not in self.base_costs:
                self.base_costs[op_name] = cost

    def calculate_cost(self, operation_name: str, history: List[OperationEntry]) -> float:
        """Calculate dynamic cost for an operation."""
        # Get base cost
        base_cost = self.base_costs.get(operation_name, 2.0)

        # Apply cost modifiers
        modified_cost = self._apply_cost_modifiers(operation_name, base_cost, history)

        return modified_cost

    def _apply_cost_modifiers(self, operation_name: str, base_cost: float, history: List[OperationEntry]) -> float:
        """Apply dynamic cost modifiers."""
        cost = base_cost
        modifiers = self.cost_modifiers

        # Frequency penalty
        if modifiers.get('frequency_penalty', {}).get('enabled', True):
            frequency_rate = modifiers.get('frequency_penalty', {}).get('rate', 0.1)
            use_count = self._count_operation_uses(operation_name, history)
            penalty_multiplier = 1.0 + (use_count * frequency_rate)
            cost *= penalty_multiplier

        # Diminishing returns
        if modifiers.get('diminishing_return', {}).get('enabled', True):
            diminishing_rate = modifiers.get('diminishing_return', {}).get('rate', 0.05)
            if not self._was_effective_recently(operation_name, history):
                diminishing_multiplier = 1.0 + diminishing_rate
                cost *= diminishing_multiplier

        # Novelty bonus
        if modifiers.get('novelty_bonus', {}).get('enabled', True):
            novelty_rate = modifiers.get('novelty_bonus', {}).get('rate', -0.2)
            if use_count < 5:  # Rarely used operations
                novelty_multiplier = 1.0 + novelty_rate
                cost *= novelty_multiplier

        return cost

    def _count_operation_uses(self, operation_name: str, history: List[OperationEntry]) -> int:
        """Count how many times an operation has been used."""
        return sum(1 for entry in history if entry.operation_name == operation_name)

    def _was_effective_recently(self, operation_name: str, history: List[OperationEntry]) -> bool:
        """Check if operation was effective recently."""
        recent_entries = history[-10:]  # Last 10 operations
        for entry in recent_entries:
            if entry.operation_name == operation_name and entry.effectiveness_score > 0:
                return True
        return False

    def get_operation_cost(self, operation_name: str) -> float:
        """Get base cost for an operation."""
        return self.base_costs.get(operation_name, 2.0)

    def update_costs(self, performance_data: Dict[str, float]) -> None:
        """Update costs based on performance data."""
        for operation_name, performance in performance_data.items():
            if operation_name in self.base_costs:
                # Adjust cost based on performance (lower cost = better performance)
                adjustment = 1.0 - (performance / 100.0)  # Normalize performance
                new_cost = self.base_costs[operation_name] * (0.5 + adjustment)
                self.base_costs[operation_name] = max(0.1, new_cost)  # Minimum cost of 0.1

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get summary of current costs."""
        return {
            'total_operations': len(self.base_costs),
            'min_cost': min(self.base_costs.values()),
            'max_cost': max(self.base_costs.values()),
            'avg_cost': sum(self.base_costs.values()) / len(self.base_costs),
            'costs': self.base_costs.copy()
        }