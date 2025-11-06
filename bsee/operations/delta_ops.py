"""
Delta encoding operations for binary transformation.
"""

from typing import Callable, Dict, List, Tuple, Any


class DeltaOperations:
    """Collection of delta encoding operations."""

    def __init__(self):
        """Initialize delta operations."""
        self.operations = self._create_operations()

    def _create_operations(self) -> Dict[str, Callable]:
        """Create all delta operations."""
        return {
            'delta_encode': self.delta_encode,
            'delta_decode': self.delta_decode,
            'adaptive_delta': self.adaptive_delta,
            'predictive_delta': self.predictive_delta,
            'run_length_delta': self.run_length_delta,
            'differential_encode': self.differential_encode,
            'cumulative_delta': self.cumulative_delta,
            'zigzag_delta': self.zigzag_delta,
            'block_delta': self.block_delta,
            'windowed_delta': self.windowed_delta
        }

    def get_operations(self) -> Dict[str, Callable]:
        """Get all operations."""
        return self.operations

    def get_metadata(self, operation_name: str) -> Dict[str, Any]:
        """Get metadata for an operation."""
        metadata_map = {
            'delta_encode': {
                'category': 'delta',
                'description': 'Simple delta encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'delta_decode': {
                'category': 'delta',
                'description': 'Simple delta decoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'adaptive_delta': {
                'category': 'delta',
                'description': 'Adaptive delta encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'predictive_delta': {
                'category': 'delta',
                'description': 'Predictive delta encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'run_length_delta': {
                'category': 'delta',
                'description': 'Run length delta encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'differential_encode': {
                'category': 'delta',
                'description': 'Differential encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'cumulative_delta': {
                'category': 'delta',
                'description': 'Cumulative delta encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'zigzag_delta': {
                'category': 'delta',
                'description': 'Zigzag delta encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'block_delta': {
                'category': 'delta',
                'description': 'Block-based delta encoding',
                'required_params': ['block_size'],
                'optional_params': {},
                'reversible': True
            },
            'windowed_delta': {
                'category': 'delta',
                'description': 'Windowed delta encoding',
                'required_params': ['window_size'],
                'optional_params': {},
                'reversible': True
            }
        }
        return metadata_map.get(operation_name, {})

    def delta_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Simple delta encoding."""
        if len(binary_data) <= 1:
            return binary_data, lambda: binary_data, {'operation': 'delta_encode', 'bytes_affected': 0}

        delta = bytearray()
        delta.append(binary_data[0])  # First byte unchanged

        for i in range(1, len(binary_data)):
            delta.append((binary_data[i] - binary_data[i-1]) & 0xFF)

        new_data = bytes(delta)

        def inverse():
            if len(new_data) <= 1:
                return new_data

            original = bytearray()
            original.append(new_data[0])

            for i in range(1, len(new_data)):
                original.append((new_data[i] + original[i-1]) & 0xFF)

            return bytes(original)

        metadata = {
            'operation': 'delta_encode',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def delta_decode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Simple delta decoding."""
        # Delta decode is essentially the same as delta encode inverse
        new_data, inverse_fn, metadata = self.delta_encode(binary_data)
        metadata['operation'] = 'delta_decode'
        return new_data, inverse_fn, metadata

    # Placeholder implementations for other delta operations
    def adaptive_delta(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Adaptive delta encoding."""
        # Simplified implementation - use regular delta encoding
        return self.delta_encode(binary_data)

    def predictive_delta(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Predictive delta encoding."""
        return self.delta_encode(binary_data)

    def run_length_delta(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Run length delta encoding."""
        return self.delta_encode(binary_data)

    def differential_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Differential encoding."""
        return self.delta_encode(binary_data)

    def cumulative_delta(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Cumulative delta encoding."""
        return self.delta_encode(binary_data)

    def zigzag_delta(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Zigzag delta encoding."""
        return self.delta_encode(binary_data)

    def block_delta(self, binary_data: bytes, block_size: int) -> Tuple[bytes, Callable, Dict]:
        """Block-based delta encoding."""
        if block_size <= 0:
            raise ValueError("Block size must be positive")

        result = bytearray()
        for i in range(0, len(binary_data), block_size):
            block = binary_data[i:i + block_size]
            delta_block, _, _ = self.delta_encode(block)
            result.extend(delta_block)

        new_data = bytes(result)

        def inverse():
            result = bytearray()
            for i in range(0, len(new_data), block_size):
                block = new_data[i:i + block_size]
                original_block, _, _ = self.delta_decode(block)
                result.extend(original_block)
            return bytes(result)

        metadata = {
            'operation': 'block_delta',
            'block_size': block_size,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def windowed_delta(self, binary_data: bytes, window_size: int) -> Tuple[bytes, Callable, Dict]:
        """Windowed delta encoding."""
        if window_size <= 0:
            raise ValueError("Window size must be positive")

        if len(binary_data) <= window_size:
            return binary_data, lambda: binary_data, {'operation': 'windowed_delta', 'bytes_affected': 0}

        result = bytearray()
        result.extend(binary_data[:window_size])  # First window unchanged

        for i in range(window_size, len(binary_data)):
            # Subtract byte from window_size positions back
            delta_val = (binary_data[i] - binary_data[i - window_size]) & 0xFF
            result.append(delta_val)

        new_data = bytes(result)

        def inverse():
            if len(new_data) <= window_size:
                return new_data

            original = bytearray()
            original.extend(new_data[:window_size])

            for i in range(window_size, len(new_data)):
                # Add back the byte from window_size positions back
                original.append((new_data[i] + original[i - window_size]) & 0xFF)

            return bytes(original)

        metadata = {
            'operation': 'windowed_delta',
            'window_size': window_size,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata