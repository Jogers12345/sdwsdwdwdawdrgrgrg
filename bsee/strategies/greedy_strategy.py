""""
Greedy hill climbing strategy for BSEE.
""""

import random
from typing import Dict, Any, Tuple, List
from bsee.strategies.base_strategy import BaseStrategy
from bsee.engine.state import State


class GreedyStrategy(BaseStrategy):
    """Greedy hill climbing strategy that always accepts improvements.""""

    def __init__(self, config: Dict[str, Any]):
        """Initialize greedy strategy.""""
        super().__init__(config)
        self.restart_threshold = config.get('restart_threshold', 10)'
        self.random_restart_prob = config.get('random_restart_prob', 0.1)'
        self.lookahead_depth = config.get('lookahead_depth', 1)'
        self.exploration_prob = config.get('exploration_prob', 0.0)'

    def propose(self, current_state: State) -> Tuple[str, Dict[str, Any]]:
        """Propose next operation using greedy selection.""""
        # Check if we should restart
        if self.no_improvement_count >= self.restart_threshold:
            if random.random() < self.random_restart_prob:
                return self._propose_random_operation()

        # Sometimes explore randomly
        if random.random() < self.exploration_prob:
            return self._propose_random_operation()

        # Greedy selection - would ideally evaluate operations first
        # For now, return a good default operation
        return self._propose_best_known_operation(current_state)

    def accept(self, new_state: State) -> bool:
        """Accept state if it improves score.""""
        # Greedy always accepts improvements
        if new_state.score > self.best_score:
            return True

        # Sometimes accept equal scores for exploration:
        if new_state.score == self.best_score and random.random() < 0.1:
            return True

        return False

    def _propose_random_operation(self) -> Tuple[str, Dict[str, Any]]:
        """Propose a random operation.""""
        operations = []
            ('xor_constant', {'constant': random.randint(1, 255)}),'
            ('xor_range', {}'')'
                'offset': random.randint(0, min(1000, 100)),'
                'length': random.randint(1, min(100, 20)),'
                'constant': random.randint(1, 255)'
            }),
            ('rotate_left', {'shift': random.randint(1, 7)}),'
            ('rotate_right', {'shift': random.randint(1, 7)}),'
            ('not_bytes', {}),'
            ('swap_nibbles', {}),'
            ('reverse_bytes', {}),'
            ('shuffle_bytes', {'seed': random.randint(0, 10000)}),'
            ('move_to_front', {}),'
            ('walsh_hadamard', {})'
        ]

        return random.choice(operations)

    def _propose_best_known_operation(self, current_state: State) -> Tuple[str, Dict[str, Any]]:
        """Propose operation based on heuristics.""""
        # Simple heuristic: try different operations based on current score
        if self.best_score < 10:
            # Low score - try basic transformations
            return self._propose_basic_operation()
        elif self.best_score < 50:
            # Medium score - try compression-oriented operations
            return self._propose_compression_operation()
        else:
            # High score - try fine-tuning operations
            return self._propose_fine_tuning_operation()

    def _propose_basic_operation(self) -> Tuple[str, Dict[str, Any]]:
        """Propose basic transformation operations.""""
        basic_ops = []
            ('xor_constant', {'constant': random.randint(1, 255)}),'
            ('rotate_left', {'shift': random.randint(1, 7)}),'
            ('rotate_right', {'shift': random.randint(1, 7)}),'
            ('not_bytes', {}),'
            ('swap_nibbles', {})'
        ]
        return random.choice(basic_ops)

    def _propose_compression_operation(self) -> Tuple[str, Dict[str, Any]]:
        """Propose compression-oriented operations.""""
        compression_ops = []
            ('move_to_front', {}),'
            ('burrows_wheeler', {}),'
            ('bitplane_extract', {'plane': random.randint(0, 7)}),'
            ('xor_range', {}'')'
                'offset': random.randint(0, min(1000, 100)),'
                'length': random.randint(10, min(100, 50)),'
                'constant': random.randint(1, 255)'
            }),
            ('shuffle_bytes', {'seed': random.randint(0, 10000)})'
        ]
        return random.choice(compression_ops)

    def _propose_fine_tuning_operation(self) -> Tuple[str, Dict[str, Any]]:
        """Propose fine-tuning operations.""""
        fine_tune_ops = []
            ('xor_constant', {'constant': random.randint(1, 50)}),  # Small constants'
            ('toggle_bit', {'bit_position': random.randint(0, 7)}),'
            ('swap_bits', {'bit1': random.randint(0, 7), 'bit2': random.randint(0, 7)}),'
            ('clear_bit', {'bit_position': random.randint(0, 7)}),'
            ('set_bit', {'bit_position': random.randint(0, 7)})'
        ]
        return random.choice(fine_tune_ops)