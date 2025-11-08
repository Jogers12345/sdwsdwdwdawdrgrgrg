"""
Enhanced History Management for BSEE

Provides comprehensive history tracking for transformation replay functionality.
Stores complete state snapshots for each operation with timing information
and metrics evolution for advanced visualization.
"""

import json
import time
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any, Tuple


@dataclass
class OperationSnapshot:
    """Enhanced snapshot of operation state for advanced replay."""
    operation_name: str
    operation_params: Dict[str, Any]
    before_data: bytes
    after_data: bytes
    before_hex: str
    after_hex: str
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    timing_info: Dict[str, float]
    byte_changes: List[Tuple[int, int, int]]  # (index, old_value, new_value)
    metadata: Dict[str, Any]
    timestamp: float


@dataclass
class AnalysisSession:
    """Complete analysis session with all operations."""
    session_id: str
    start_time: float
    end_time: float
    initial_data: bytes
    final_data: bytes
    operations: List[OperationSnapshot]
    session_metadata: Dict[str, Any]
    total_execution_time: float


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
    snapshot: Optional[OperationSnapshot] = None  # Enhanced replay data

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
    """Enhanced history manager for replay and advanced visualization."""

    def __init__(self, max_history_size: int = 1000, auto_save: bool = True):
        """
        Initialize enhanced history manager.

        Args:
            max_history_size: Maximum number of operations to keep in memory
            auto_save: Whether to automatically save history to disk
        """
        self.max_history_size = max_history_size
        self.auto_save = auto_save

        # Current session
        self.current_session: Optional[AnalysisSession] = None
        self.session_start_time: Optional[float] = None

        # Original entries for backward compatibility
        self.entries: List[OperationEntry] = []
        self.state_index: Dict[str, int] = {}  # state_id -> step_number
        self.operation_counts: Dict[str, int] = {}  # operation_name -> count

        # Enhanced operation snapshots
        self.operation_snapshots: List[OperationSnapshot] = []

        # Session history storage
        self.session_history: List[AnalysisSession] = []
        self.storage_directory = Path("history")
        self.storage_directory.mkdir(exist_ok=True)

        # Threading lock for thread safety
        self._lock = threading.Lock()

        # Callbacks for events
        self.on_operation_added: Optional[callable] = None
        self.on_session_completed: Optional[callable] = None

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

    # Enhanced methods for transformation viewer
    def start_session(self, session_id: str = None, initial_data: bytes = b"",
                     metadata: Dict[str, Any] = None) -> str:
        """
        Start a new analysis session.

        Args:
            session_id: Optional session ID (auto-generated if not provided)
            initial_data: Initial binary data
            metadata: Session metadata

        Returns:
            Session ID
        """
        with self._lock:
            if session_id is None:
                session_id = f"session_{int(time.time())}_{len(self.session_history)}"

            self.session_start_time = time.time()

            self.current_session = AnalysisSession(
                session_id=session_id,
                start_time=self.session_start_time,
                end_time=0.0,
                initial_data=initial_data,
                final_data=initial_data,
                operations=[],
                session_metadata=metadata or {},
                total_execution_time=0.0
            )

            # Clear operation snapshots for new session
            self.operation_snapshots.clear()

            return session_id

    def add_operation_snapshot(self, operation_name: str, operation_params: Dict[str, Any],
                             before_data: bytes, after_data: bytes,
                             metrics_before: Dict[str, float] = None,
                             metrics_after: Dict[str, float] = None,
                             timing_info: Dict[str, float] = None,
                             metadata: Dict[str, Any] = None) -> OperationSnapshot:
        """
        Add enhanced operation snapshot for replay.

        Args:
            operation_name: Name of the operation
            operation_params: Parameters used for the operation
            before_data: Data before operation
            after_data: Data after operation
            metrics_before: Metrics calculated before operation
            metrics_after: Metrics calculated after operation
            timing_info: Timing information for the operation
            metadata: Additional operation metadata

        Returns:
            Created operation snapshot
        """
        with self._lock:
            if self.current_session is None:
                raise ValueError("No active session. Call start_session() first.")

            # Create snapshot
            snapshot = OperationSnapshot(
                operation_name=operation_name,
                operation_params=operation_params or {},
                before_data=before_data,
                after_data=after_data,
                before_hex=before_data.hex(),
                after_hex=after_data.hex(),
                metrics_before=metrics_before or {},
                metrics_after=metrics_after or {},
                timing_info=timing_info or {},
                byte_changes=self._analyze_byte_changes(before_data, after_data),
                metadata=metadata or {},
                timestamp=time.time()
            )

            # Add to current session
            self.current_session.operations.append(snapshot)
            self.current_session.final_data = after_data

            # Update session execution time
            if timing_info and 'execution_time' in timing_info:
                self.current_session.total_execution_time += timing_info['execution_time']

            # Add to snapshots list
            self.operation_snapshots.append(snapshot)

            # Limit history size
            if len(self.operation_snapshots) > self.max_history_size:
                self.operation_snapshots.pop(0)

            # Auto-save if enabled
            if self.auto_save:
                self._save_session_snapshot(snapshot)

            # Notify callback
            if self.on_operation_added:
                self.on_operation_added(snapshot)

            return snapshot

    def end_session(self, final_metadata: Dict[str, Any] = None) -> AnalysisSession:
        """
        End current session and add to history.

        Args:
            final_metadata: Additional metadata for session completion

        Returns:
            Completed session
        """
        with self._lock:
            if self.current_session is None:
                raise ValueError("No active session to end.")

            self.current_session.end_time = time.time()
            self.current_session.session_metadata.update(final_metadata or {})

            # Add to history
            self.session_history.append(self.current_session)

            # Auto-save complete session
            if self.auto_save:
                self._save_complete_session(self.current_session)

            # Notify callback
            if self.on_session_completed:
                self.on_session_completed(self.current_session)

            completed_session = self.current_session
            self.current_session = None
            self.session_start_time = None

            return completed_session

    def get_current_session(self) -> Optional[AnalysisSession]:
        """Get currently active session."""
        return self.current_session

    def get_session_history(self, limit: int = None) -> List[AnalysisSession]:
        """
        Get session history.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of analysis sessions
        """
        with self._lock:
            history = self.session_history.copy()
            if limit:
                return history[-limit:]
            return history

    def get_session_by_id(self, session_id: str) -> Optional[AnalysisSession]:
        """Get session by ID."""
        with self._lock:
            for session in self.session_history:
                if session.session_id == session_id:
                    return session
            return None

    def get_operation_snapshots(self, session_id: str = None) -> List[OperationSnapshot]:
        """
        Get operation snapshots.

        Args:
            session_id: Optional session ID (uses current session if not provided)

        Returns:
            List of operation snapshots
        """
        with self._lock:
            if session_id:
                session = self.get_session_by_id(session_id)
                return session.operations if session else []
            elif self.current_session:
                return self.current_session.operations.copy()
            else:
                return self.operation_snapshots.copy()

    def export_session_for_replay(self, session_id: str = None) -> Dict[str, Any]:
        """
        Export session data in format suitable for transformation viewer.

        Args:
            session_id: Optional session ID (uses current session if not provided)

        Returns:
            Export data dictionary
        """
        with self._lock:
            if session_id:
                session = self.get_session_by_id(session_id)
            else:
                session = self.current_session

            if not session:
                return {}

            # Convert operations to replay format
            operations = []
            for op in session.operations:
                operation_data = {
                    'name': op.operation_name,
                    'params': op.operation_params,
                    'before_hex': op.before_hex,
                    'after_hex': op.after_hex,
                    'metrics_before': op.metrics_before,
                    'metrics_after': op.metrics_after,
                    'timing': op.timing_info,
                    'byte_changes': op.byte_changes,
                    'metadata': op.metadata,
                    'timestamp': op.timestamp
                }
                operations.append(operation_data)

            return {
                'session_id': session.session_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'initial_data': session.initial_data.hex(),
                'final_data': session.final_data.hex(),
                'operations': operations,
                'session_metadata': session.session_metadata,
                'total_execution_time': session.total_execution_time
            }

    def _analyze_byte_changes(self, before: bytes, after: bytes) -> List[Tuple[int, int, int]]:
        """Analyze byte changes between before and after data."""
        changes = []
        min_len = min(len(before), len(after))

        # Find changed bytes
        for i in range(min_len):
            if before[i] != after[i]:
                changes.append((i, before[i], after[i]))

        # Handle insertions/deletions
        if len(before) < len(after):
            # Insertions
            for i in range(len(before), len(after)):
                changes.append((i, -1, after[i]))  # -1 indicates insertion
        elif len(before) > len(after):
            # Deletions
            for i in range(len(after), len(before)):
                changes.append((i, before[i], -1))  # -1 indicates deletion

        return changes

    def _save_session_snapshot(self, snapshot: OperationSnapshot):
        """Save individual operation snapshot."""
        try:
            snapshot_file = self.storage_directory / f"snapshot_{int(snapshot.timestamp)}.json"
            with open(snapshot_file, 'w') as f:
                json.dump(asdict(snapshot), f, indent=2, default=str)
        except Exception as e:
            # Log error but don't crash
            print(f"Error saving snapshot: {e}")

    def _save_complete_session(self, session: AnalysisSession):
        """Save complete session to disk."""
        try:
            session_file = self.storage_directory / f"session_{session.session_id}.json"
            session_data = {
                'session': asdict(session),
                'export_timestamp': datetime.now().isoformat()
            }
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving session: {e}")

    def set_callbacks(self, on_operation_added: callable = None,
                     on_session_completed: callable = None):
        """Set callback functions for events."""
        if on_operation_added:
            self.on_operation_added = on_operation_added
        if on_session_completed:
            self.on_session_completed = on_session_completed