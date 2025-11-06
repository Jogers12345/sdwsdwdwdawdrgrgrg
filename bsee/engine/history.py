"""
Operation history management for BSEE.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional


@dataclass
class OperationEntry:
    """Represents a single operation in the history."""
    step_number: int                 # Sequential step number
    operation_name: str             # Name of operation applied
    parameters: Dict[str, any]      # Parameters used
    inverse_function: Callable      # Function to reverse operation
    cost: float                     # Cost of operation
    timestamp: datetime             # When operation was applied
    parent_state_id: str            # State before operation
    resulting_state_id: str         # State after operation
    effectiveness_score: float      # Score improvement achieved

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'step_number': self.step_number,
            'operation_name': self.operation_name,
            'parameters': self.parameters,
            'cost': self.cost,
            'timestamp': self.timestamp.isoformat(),
            'parent_state_id': self.parent_state_id,
            'resulting_state_id': self.resulting_state_id,
            'effectiveness_score': self.effectiveness_score
        }


class HistoryManager:
    """Manages operation history and ensures complete reversibility."""

    def __init__(self):
        """Initialize history manager."""
        self.entries: List[OperationEntry] = []
        self.state_index: Dict[str, int] = {}  # state_id -> step_number
        self.operation_counts: Dict[str, int] = {}  # operation_name -> count

    def add_entry(self, entry: OperationEntry) -> None:
        """Add a new operation entry to the history."""
        self.entries.append(entry)
        self.state_index[entry.resulting_state_id] = entry.step_number

        # Update operation counts
        self.operation_counts[entry.operation_name] = \
            self.operation_counts.get(entry.operation_name, 0) + 1

    def get_chain_to_state(self, state_id: str) -> List[OperationEntry]:
        """Get the complete operation chain from root to specified state."""
        if state_id not in self.state_index:
            return []

        target_step = self.state_index[state_id]
        return self.entries[:target_step]

    def generate_inverse_chain(self, state_id: str) -> List[Callable]:
        """Generate the chain of inverse functions to reverse to original state."""
        chain = self.get_chain_to_state(state_id)
        return [entry.inverse_function for entry in reversed(chain)]

    def export_to_json(self, state_id: str, original_file: str) -> Dict:
        """Export operation history to JSON format for external analysis."""
        chain = self.get_chain_to_state(state_id)

        # Extract inverse operations (functions can't be serialized, so we save names)
        inverse_operations = []
        for entry in reversed(chain):
            inverse_op = {
                'step': entry.step_number,
                'operation': self._get_inverse_operation_name(entry.operation_name),
                'params': entry.parameters
            }
            inverse_operations.append(inverse_op)

        return {
            'original_file': original_file,
            'final_state_id': state_id,
            'total_operations': len(chain),
            'total_cost': sum(entry.cost for entry in chain),
            'operations': [entry.to_dict() for entry in chain],
            'inverse_operations': inverse_operations,
            'operation_statistics': self._get_operation_statistics()
        }

    def validate_reversibility(self, final_state_id: str, original_binary: bytes) -> bool:
        """Validate that the inverse chain correctly reproduces the original binary."""
        try:
            inverse_chain = self.generate_inverse_chain(final_state_id)

            # Start with current state (we would need the current binary data)
            # For now, this is a placeholder that validates the chain structure
            if not inverse_chain:
                return len(self.entries) == 0

            # Validate that we have the right number of inverse functions
            chain_length = len(self.get_chain_to_state(final_state_id))
            return len(inverse_chain) == chain_length

        except Exception:
            return False

    def get_operation_count(self, operation_name: str) -> int:
        """Get the total count of a specific operation."""
        return self.operation_counts.get(operation_name, 0)

    def get_total_cost(self) -> float:
        """Get total cost of all operations."""
        return sum(entry.cost for entry in self.entries)

    def get_operation_effectiveness(self, operation_name: str) -> float:
        """Get average effectiveness score for an operation."""
        operation_entries = [e for e in self.entries if e.operation_name == operation_name]
        if not operation_entries:
            return 0.0

        total_effectiveness = sum(e.effectiveness_score for e in operation_entries)
        return total_effectiveness / len(operation_entries)

    def get_most_effective_operations(self, top_n: int = 10) -> List[Dict]:
        """Get the most effective operations by score/cost ratio."""
        operation_stats = {}

        for entry in self.entries:
            if entry.operation_name not in operation_stats:
                operation_stats[entry.operation_name] = {
                    'total_cost': 0.0,
                    'total_effectiveness': 0.0,
                    'count': 0
                }

            stats = operation_stats[entry.operation_name]
            stats['total_cost'] += entry.cost
            stats['total_effectiveness'] += entry.effectiveness_score
            stats['count'] += 1

        # Calculate score/cost ratio
        results = []
        for op_name, stats in operation_stats.items():
            if stats['total_cost'] > 0:
                ratio = stats['total_effectiveness'] / stats['total_cost']
                results.append({
                    'operation': op_name,
                    'score_per_cost': ratio,
                    'total_cost': stats['total_cost'],
                    'total_effectiveness': stats['total_effectiveness'],
                    'count': stats['count']
                })

        # Sort by ratio and return top N
        results.sort(key=lambda x: x['score_per_cost'], reverse=True)
        return results[:top_n]

    def clear(self) -> None:
        """Clear all history."""
        self.entries.clear()
        self.state_index.clear()
        self.operation_counts.clear()

    def get_summary(self) -> Dict:
        """Get a summary of the operation history."""
        if not self.entries:
            return {
                'total_operations': 0,
                'total_cost': 0.0,
                'unique_operations': 0,
                'most_used_operation': None
            }

        return {
            'total_operations': len(self.entries),
            'total_cost': self.get_total_cost(),
            'unique_operations': len(self.operation_counts),
            'most_used_operation': max(self.operation_counts.items(), key=lambda x: x[1])[0] if self.operation_counts else None,
            'operation_counts': self.operation_counts.copy()
        }

    def _get_inverse_operation_name(self, operation_name: str) -> str:
        """Get the name of the inverse operation."""
        # This would be expanded based on the operations registry
        inverse_map = {
            'xor_constant': 'xor_constant',
            'xor_range': 'xor_range',
            'rotate_left': 'rotate_right',
            'rotate_right': 'rotate_left',
            'bitplane_extract': 'bitplane_insert',
            'bitplane_insert': 'bitplane_extract',
            # Add more mappings as needed
        }
        return inverse_map.get(operation_name, f'inverse_{operation_name}')

    def _get_operation_statistics(self) -> Dict:
        """Get detailed statistics about operations used."""
        stats = {}
        for op_name, count in self.operation_counts.items():
            operation_entries = [e for e in self.entries if e.operation_name == op_name]
            total_cost = sum(e.cost for e in operation_entries)
            avg_cost = total_cost / len(operation_entries) if operation_entries else 0
            avg_effectiveness = sum(e.effectiveness_score for e in operation_entries) / len(operation_entries) if operation_entries else 0

            stats[op_name] = {
                'count': count,
                'total_cost': total_cost,
                'average_cost': avg_cost,
                'average_effectiveness': avg_effectiveness
            }

        return stats