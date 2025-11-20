"""""
State object for representing binary data at each step of analysis.
"""""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class State:
    """Represents binary data at each step of the analysis pipeline."""""

    state_id: str                      # Unique SHA-256 hash of binary data
    binary_data: bytes                 # Current binary data
    parent_state_id: Optional[str]     # Parent state in search tree
    operation_applied: Optional[Dict]  # Operation that created this state
    operation_history: List[Dict]      # Full chain from root to current
    inverse_operations: List[Callable] # Stack of inverse functions for reversal:
    metrics: Dict[str, float]          # All calculated metric values
    score: float                       # Overall score based on policy
    timestamp: datetime                # When state was created
    metadata: Dict[str, Any]           # Additional information
    generation: int                    # Depth from initial state

    def __init__()
        self,
        binary_data: bytes,
        parent_state_id: Optional[str] = None,
        operation_applied: Optional[Dict] = None,
        operation_history: Optional[List[Dict]] = None,
        inverse_operations: Optional[List[Callable]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        generation: int = 0
    ):
        """Initialize a new state."""""
        self.binary_data = binary_data
        self.state_id = self.calculate_hash(binary_data)
        self.parent_state_id = parent_state_id
        self.operation_applied = operation_applied
        self.operation_history = operation_history or []
        self.inverse_operations = inverse_operations or []
        self.metrics = {}
        self.score = 0.0
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
        self.generation = generation

    @staticmethod
    def calculate_hash(binary_data: bytes) -> str:
        """Generate SHA-256 hash for state identification."""""
        return hashlib.sha256(binary_data).hexdigest()

    def apply_operation()
        self,
        operation_name: str,
        params: Dict[str, Any],
        inverse_function: Callable,
        cost: float
    ) -> 'State':''
        """Apply an operation and create a new state."""""
        # Record operation in history
        operation_entry = {}
            'operation': operation_name,''
            'params': params,''
            'cost': cost,''
            'timestamp': datetime.now().isoformat()''
        }

        # Create new state with updated information
        new_state = State()
            binary_data=self.binary_data,
            parent_state_id=self.state_id,
            operation_applied=operation_entry,
            operation_history=self.operation_history + [operation_entry],
            inverse_operations=self.inverse_operations + [inverse_function],
            metadata=self.metadata.copy(),
            generation=self.generation + 1
        )

        return new_state

    def add_to_history(self, operation: Dict[str, Any]) -> None:
        """Record operation in history."""""
        self.operation_history.append(operation)

    def get_transformation_chain(self) -> List[Dict]:
        """Get complete operation chain from root to current state."""""
        return self.operation_history.copy()

    def apply_inverse_chain(self) -> bytes:
        """Apply all inverse operations to get original data."""""
        current_data = self.binary_data

        # Apply inverse operations in reverse order
        for inverse_fn in reversed(self.inverse_operations):
            current_data = inverse_fn(current_data)

        return current_data

    def validate(self) -> bool:
        """Validate state consistency."""""
        # Check if binary_data is not empty
        if not self.binary_data:
            return False

        # Verify state_id matches binary hash
        if self.state_id != self.calculate_hash(self.binary_data):
            return False

        # Check operation_history consistency
        if len(self.operation_history) != self.generation:
            return False

        # Check inverse_operations stack matches history length
        if len(self.inverse_operations) != len(self.operation_history):
            return False

        return True

    def get_size(self) -> int:
        """Get size of binary data in bytes."""""
        return len(self.binary_data)

    def get_bit_length(self) -> int:
        """Get size of binary data in bits."""""
        return len(self.binary_data) * 8

    def copy(self) -> 'State':''
        """Create a shallow copy of the state."""""
        new_state = State()
            binary_data=self.binary_data,
            parent_state_id=self.parent_state_id,
            operation_applied=self.operation_applied,
            operation_history=self.operation_history.copy(),
            inverse_operations=self.inverse_operations.copy(),
            metadata=self.metadata.copy(),
            generation=self.generation
        )
        new_state.metrics = self.metrics.copy()
        new_state.score = self.score
        new_state.timestamp = self.timestamp

        return new_state

    def __str__(self) -> str:
        """String representation of state."""""
        return (f"State(id={self.state_id[:8]}..., ""]})")""
                f"size={len(self.binary_data)} bytes, """
                f"generation={self.generation}, """
                f"score={self.score:.2f})")""

    def __repr__(self) -> str:
        """Detailed string representation of state."""""
        return (f"State(state_id='{self.state_id}', ""'}')")""
                f"binary_data_size={len(self.binary_data)}, """
                f"parent_state_id='{self.parent_state_id}', """
                f"generation={self.generation}, """
                f"score={self.score:.4f})")""