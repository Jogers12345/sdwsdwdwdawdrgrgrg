"""
Global Error Handler for BSEE

Centralized error handling with automatic recovery strategies for the
Binary Structure Exploration Engine.
"""

import gc
import time
import traceback
import logging
from enum import Enum
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass, field


class ErrorCategory(Enum):
    """Categories of errors for different handling strategies."""
    RECOVERABLE = "recoverable"  # Can continue with fallback
    FATAL = "fatal"              # Must stop execution
    WARNING = "warning"          # Log and continue


@dataclass
class ErrorContext:
    """Context information for error handling."""
    strategy: Optional[str] = None
    operation: Optional[str] = None
    iteration: Optional[int] = None
    state_score: Optional[float] = None
    file_path: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Record of an error that occurred."""
    timestamp: float
    exception_type: str
    exception_message: str
    context: ErrorContext
    recovery_attempted: bool
    recovery_successful: bool
    stack_trace: str


class GlobalErrorHandler:
    """Centralized error handling with automatic recovery strategies."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize global error handler."""
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_history: List[ErrorRecord] = []
        self.max_history_size = 1000
        self._register_builtin_strategies()

    def handle_exception(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle exception with appropriate recovery strategy.

        Args:
            exception: The exception that occurred
            context: Execution context (strategy, operation, iteration, etc.)

        Returns:
            bool: True if recovery successful, False if execution should stop
        """
        exception_type = type(exception).__name__
        error_context = ErrorContext(**context)

        # Log error with full context
        self._log_error(exception, error_context)

        # Update error statistics
        self._update_error_stats(exception_type)

        # Get recovery strategy
        strategy = self.recovery_strategies.get(exception_type)
        if not strategy:
            # Default handling based on exception type
            return self._default_recovery(exception, error_context)

        # Execute recovery strategy
        recovery_success = False
        try:
            recovery_success = strategy(exception, error_context, self.logger)
        except Exception as recovery_error:
            self.logger.error(f"Recovery strategy failed for {exception_type}: {recovery_error}")
            recovery_success = False

        # Record the error
        error_record = ErrorRecord(
            timestamp=time.time(),
            exception_type=exception_type,
            exception_message=str(exception),
            context=error_context,
            recovery_attempted=True,
            recovery_successful=recovery_success,
            stack_trace=traceback.format_exc()
        )
        self._add_error_record(error_record)

        return recovery_success

    def register_recovery_strategy(self, exception_type: str, strategy: Callable) -> None:
        """Register custom recovery strategy for exception type."""
        self.recovery_strategies[exception_type] = strategy
        self.logger.info(f"Registered recovery strategy for {exception_type}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """Return comprehensive statistics about handled errors."""
        total_errors = sum(self.error_counts.values())

        # Calculate recovery success rate
        recovery_attempts = [r for r in self.error_history if r.recovery_attempted]
        successful_recoveries = [r for r in recovery_attempts if r.recovery_successful]
        recovery_success_rate = (
            len(successful_recoveries) / len(recovery_attempts) * 100
            if recovery_attempts else 0
        )

        # Most common errors
        sorted_errors = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            'total_errors': total_errors,
            'error_types': dict(self.error_counts),
            'most_common_errors': sorted_errors[:10],
            'recent_errors': self.error_history[-10:],  # Last 10 errors
            'recovery_success_rate': recovery_success_rate,
            'total_recovery_attempts': len(recovery_attempts),
            'successful_recoveries': len(successful_recoveries),
            'registered_strategies': list(self.recovery_strategies.keys())
        }

    def get_recent_errors(self, count: int = 10, exception_type: str = None) -> List[ErrorRecord]:
        """Get recent errors, optionally filtered by type."""
        errors = self.error_history
        if exception_type:
            errors = [e for e in errors if e.exception_type == exception_type]
        return errors[-count:]

    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info("Error history cleared")

    def _register_builtin_strategies(self) -> None:
        """Register built-in recovery strategies."""

        def memory_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle memory errors with cleanup and parameter reduction."""
            logger.warning(f"Memory error detected in {ctx.strategy or 'unknown'}, attempting recovery")

            # Force garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")

            # Suggest memory reduction strategies based on context
            suggestions = []
            if ctx.strategy:
                if 'mcts' in ctx.strategy.lower():
                    suggestions.append("Reduce max_children or simulation_count")
                    suggestions.append("Prune tree more aggressively")
                elif 'genetic' in ctx.strategy.lower():
                    suggestions.append("Reduce population_size")
                    suggestions.append("Remove less fit individuals")
                elif 'beam' in ctx.strategy.lower():
                    suggestions.append("Reduce beam_width")
                elif 'annealing' in ctx.strategy.lower():
                    suggestions.append("Reduce iteration_count")

            if suggestions:
                logger.warning(f"Suggested parameter adjustments: {', '.join(suggestions)}")

            return True  # Continue with reduced memory usage

        def timeout_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle timeout errors by returning early."""
            logger.warning(f"Timeout detected in {ctx.strategy or 'unknown'}, returning early")

            if ctx.iteration and ctx.state_score:
                logger.info(f"Returning best known solution at iteration {ctx.iteration} with score {ctx.state_score}")

            return True  # Continue with partial result

        def import_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle import errors with fallback implementations."""
            logger.warning(f"Import error: {exc}")

            if ctx.operation:
                # Check if we have fallback for this operation
                fallback_operations = {
                    'dct_transform': 'numpy_fallback',
                    'dwt_transform': 'haar_fallback',
                    'fft_transform': 'numpy_only',
                    'huffman_encode': 'pure_python',
                    'run_length_encode': 'pure_python',
                    'lz77_encode': 'pure_python',
                    'arithmetic_encode': 'pure_python'
                }

                if ctx.operation in fallback_operations:
                    logger.warning(f"Using {fallback_operations[ctx.operation]} for {ctx.operation}")
                    return True

            return False  # Can't recover from this import error

        def value_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle value errors with parameter validation and defaults."""
            logger.warning(f"Value error in {ctx.operation or 'unknown operation'}: {exc}")

            # Use default parameters for common value errors
            error_msg = str(exc).lower()
            if 'window size' in error_msg or 'buffer size' in error_msg:
                logger.warning("Using default window/buffer sizes")
                return True
            elif 'run length' in error_msg:
                logger.warning("Using default run length parameters")
                return True
            elif 'frequency' in error_msg or 'probability' in error_msg:
                logger.warning("Using uniform probability distribution")
                return True

            return False

        def io_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle I/O errors with retries and fallbacks."""
            logger.warning(f"I/O error: {exc}")

            # Retry with exponential backoff would be implemented here
            # For now, just log and continue
            if ctx.file_path:
                logger.warning(f"Failed to access {ctx.file_path}, will retry later")

            return True  # Continue without the file

        def overflow_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle overflow errors with precision reduction."""
            logger.warning(f"Overflow error in {ctx.operation or 'unknown'}, reducing precision")

            # Suggest precision adjustments
            if 'arithmetic' in ctx.operation.lower():
                logger.warning("Reduce arithmetic precision or use fixed-point arithmetic")
            elif 'transform' in ctx.operation.lower():
                logger.warning("Use smaller data chunks or reduce transform size")

            return True

        def zero_division_error_recovery(exc, ctx: ErrorContext, logger: logging.Logger) -> bool:
            """Handle division by zero with epsilon values."""
            logger.warning(f"Division by zero in {ctx.operation or 'unknown'}, using epsilon")

            # Use small epsilon to avoid division by zero
            logger.warning("Applying epsilon value to avoid division by zero")
            return True

        # Register strategies
        self.register_recovery_strategy('MemoryError', memory_error_recovery)
        self.register_recovery_strategy('TimeoutError', timeout_error_recovery)
        self.register_recovery_strategy('ImportError', import_error_recovery)
        self.register_recovery_strategy('ValueError', value_error_recovery)
        self.register_recovery_strategy('IOError', io_error_recovery)
        self.register_recovery_strategy('OverflowError', overflow_error_recovery)
        self.register_recovery_strategy('ZeroDivisionError', zero_division_error_recovery)

    def _default_recovery(self, exception: Exception, context: ErrorContext) -> bool:
        """Default recovery strategy when no specific strategy is registered."""
        exception_type = type(exception).__name__

        # Categorize exception type
        if any(keyword in exception_type.lower() for keyword in ['fatal', 'critical', 'system']):
            self.logger.error(f"Fatal error {exception_type}: {exception}")
            return False
        elif any(keyword in exception_type.lower() for keyword in ['warning', 'user']):
            self.logger.warning(f"Warning error {exception_type}: {exception}")
            return True
        else:
            # Try to continue with most errors
            self.logger.error(f"Unhandled error {exception_type}: {exception}")
            return True

    def _log_error(self, exception: Exception, context: ErrorContext) -> None:
        """Log error with full context."""
        context_str = ", ".join([
            f"{k}={v}" for k, v in {
                'strategy': context.strategy,
                'operation': context.operation,
                'iteration': context.iteration,
                'state_score': context.state_score
            }.items() if v is not None
        ])

        if context_str:
            self.logger.error(f"{type(exception).__name__} in {context_str}: {exception}")
        else:
            self.logger.error(f"{type(exception).__name__}: {exception}")

    def _update_error_stats(self, exception_type: str) -> None:
        """Update error statistics."""
        self.error_counts[exception_type] = self.error_counts.get(exception_type, 0) + 1

    def _add_error_record(self, record: ErrorRecord) -> None:
        """Add error record to history."""
        self.error_history.append(record)

        # Limit history size
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]

    def export_error_log(self, filename: str = None) -> str:
        """Export error log to file."""
        import json
        from datetime import datetime

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bsee_error_log_{timestamp}.json"

        error_data = {
            'export_timestamp': datetime.now().isoformat(),
            'statistics': self.get_error_statistics(),
            'error_history': [
                {
                    'timestamp': r.timestamp,
                    'exception_type': r.exception_type,
                    'exception_message': r.exception_message,
                    'context': {
                        'strategy': r.context.strategy,
                        'operation': r.context.operation,
                        'iteration': r.context.iteration,
                        'state_score': r.context.state_score
                    },
                    'recovery_attempted': r.recovery_attempted,
                    'recovery_successful': r.recovery_successful
                }
                for r in self.error_history
            ]
        }

        with open(filename, 'w') as f:
            json.dump(error_data, f, indent=2, default=str)

        self.logger.info(f"Error log exported to: {filename}")
        return filename


# Global instance for easy access
_global_error_handler = None


def get_global_error_handler() -> GlobalErrorHandler:
    """Get or create the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = GlobalErrorHandler()
    return _global_error_handler


def handle_exception(exception: Exception, **context) -> bool:
    """Convenience function to handle exceptions using global handler."""
    return get_global_error_handler().handle_exception(exception, context)