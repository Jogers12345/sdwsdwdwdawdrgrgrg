"""
Reordering operations for binary transformation.
"""

from typing import Callable, Dict, List, Tuple, Any


class ReorderingOperations:
    """Collection of reordering operations."""

    def __init__(self):
        """Initialize reordering operations."""
        self.operations = self._create_operations()

    def _create_operations(self) -> Dict[str, Callable]:
        """Create all reordering operations."""
        return {
            'reverse_bytes': self.reverse_bytes,
            'shuffle_bytes': self.shuffle_bytes,
            'byte_swap': self.byte_swap,
            'block_reverse': self.block_reverse,
            'rotate_bytes': self.rotate_bytes,
            'transpose_2d': self.transpose_2d,
            'bit_interleave': self.bit_interleave,
            'perfect_shuffle': self.perfect_shuffle,
            'unshuffle': self.unshuffle,
            'bitonic_sort': self.bitonic_sort,
            'radix_sort': self.radix_sort,
            'frequency_sort': self.frequency_sort,
            'block_shuffle': self.block_shuffle,
            'interleave_blocks': self.interleave_blocks,
            'deinterleave_blocks': self.deinterleave_blocks
        }

    def get_operations(self) -> Dict[str, Callable]:
        """Get all operations."""
        return self.operations

    def get_metadata(self, operation_name: str) -> Dict[str, Any]:
        """Get metadata for an operation."""
        metadata_map = {
            'reverse_bytes': {
                'category': 'reordering',
                'description': 'Reverse the order of all bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'shuffle_bytes': {
                'category': 'reordering',
                'description': 'Shuffle bytes using a seed',
                'required_params': ['seed'],
                'optional_params': {},
                'reversible': True
            },
            'byte_swap': {
                'category': 'reordering',
                'description': 'Swap bytes at specified positions',
                'required_params': ['pos1', 'pos2'],
                'optional_params': {},
                'reversible': True
            },
            'block_reverse': {
                'category': 'reordering',
                'description': 'Reverse bytes within blocks',
                'required_params': ['block_size'],
                'optional_params': {},
                'reversible': True
            },
            'rotate_bytes': {
                'category': 'reordering',
                'description': 'Rotate byte sequence',
                'required_params': ['shift'],
                'optional_params': {},
                'reversible': True
            },
            'transpose_2d': {
                'category': 'reordering',
                'description': 'Transpose data as 2D matrix',
                'required_params': ['width'],
                'optional_params': {},
                'reversible': True
            },
            'bit_interleave': {
                'category': 'reordering',
                'description': 'Interleave bits from different bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'perfect_shuffle': {
                'category': 'reordering',
                'description': 'Perfect shuffle operation',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'unshuffle': {
                'category': 'reordering',
                'description': 'Unshuffle operation',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'bitonic_sort': {
                'category': 'reordering',
                'description': 'Bitonic sort of bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'radix_sort': {
                'category': 'reordering',
                'description': 'Radix sort of bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'frequency_sort': {
                'category': 'reordering',
                'description': 'Sort bytes by frequency',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'block_shuffle': {
                'category': 'reordering',
                'description': 'Shuffle blocks of bytes',
                'required_params': ['block_size', 'seed'],
                'optional_params': {},
                'reversible': True
            },
            'interleave_blocks': {
                'category': 'reordering',
                'description': 'Interleave blocks of data',
                'required_params': ['block_size'],
                'optional_params': {},
                'reversible': True
            },
            'deinterleave_blocks': {
                'category': 'reordering',
                'description': 'Deinterleave blocks of data',
                'required_params': ['block_size'],
                'optional_params': {},
                'reversible': True
            }
        }
        return metadata_map.get(operation_name, {})

    def reverse_bytes(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Reverse the order of all bytes."""
        new_data = binary_data[::-1]

        def inverse():
            return new_data[::-1]  # Reverse again to get original

        metadata = {
            'operation': 'reverse_bytes',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def shuffle_bytes(self, binary_data: bytes, seed: int) -> Tuple[bytes, Callable, Dict]:
        """Shuffle bytes using a seed."""
        import random
        random.seed(seed)

        # Create list of (byte, original_index) pairs
        indexed_bytes = list(enumerate(binary_data))
        random.shuffle(indexed_bytes)

        # Extract shuffled bytes and store original indices
        shuffled_indices = [idx for idx, _ in indexed_bytes]
        new_data = bytes([binary_data[idx] for idx, _ in indexed_bytes])

        def inverse():
            # Restore original order using stored indices
            original = [0] * len(binary_data)
            for new_pos, original_idx in enumerate(shuffled_indices):
                original[original_idx] = new_data[new_pos]
            return bytes(original)

        metadata = {
            'operation': 'shuffle_bytes',
            'seed': seed,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def byte_swap(self, binary_data: bytes, pos1: int, pos2: int) -> Tuple[bytes, Callable, Dict]:
        """Swap bytes at specified positions."""
        if pos1 < 0 or pos1 >= len(binary_data) or pos2 < 0 or pos2 >= len(binary_data):
            raise ValueError("Byte positions out of range")

        if pos1 == pos2:
            return binary_data, lambda: binary_data, {'operation': 'byte_swap', 'bytes_affected': 0}

        data_list = list(binary_data)
        data_list[pos1], data_list[pos2] = data_list[pos2], data_list[pos1]
        new_data = bytes(data_list)

        def inverse():
            inverse_list = list(new_data)
            inverse_list[pos1], inverse_list[pos2] = inverse_list[pos2], inverse_list[pos1]
            return bytes(inverse_list)

        metadata = {
            'operation': 'byte_swap',
            'pos1': pos1,
            'pos2': pos2,
            'bytes_affected': 2
        }

        return new_data, inverse, metadata

    def block_reverse(self, binary_data: bytes, block_size: int) -> Tuple[bytes, Callable, Dict]:
        """Reverse bytes within blocks."""
        if block_size <= 0:
            raise ValueError("Block size must be positive")

        result = bytearray()
        for i in range(0, len(binary_data), block_size):
            block = binary_data[i:i + block_size]
            result.extend(block[::-1])

        new_data = bytes(result)

        def inverse():
            # Apply the same operation to reverse back
            result = bytearray()
            for i in range(0, len(new_data), block_size):
                block = new_data[i:i + block_size]
                result.extend(block[::-1])
            return bytes(result)

        metadata = {
            'operation': 'block_reverse',
            'block_size': block_size,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def rotate_bytes(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
        """Rotate byte sequence."""
        if len(binary_data) == 0:
            return binary_data, lambda: binary_data, {'operation': 'rotate_bytes', 'bytes_affected': 0}

        shift = shift % len(binary_data)
        new_data = binary_data[shift:] + binary_data[:shift]

        def inverse():
            # Rotate in opposite direction
            return new_data[-shift:] + new_data[:-shift]

        metadata = {
            'operation': 'rotate_bytes',
            'shift': shift,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def transpose_2d(self, binary_data: bytes, width: int) -> Tuple[bytes, Callable, Dict]:
        """Transpose data as 2D matrix."""
        if width <= 0:
            raise ValueError("Width must be positive")

        height = (len(binary_data) + width - 1) // width
        # Pad to complete matrix
        padded_data = binary_data + b'\x00' * (height * width - len(binary_data))

        # Transpose
        transposed = bytearray()
        for col in range(width):
            for row in range(height):
                transposed.append(padded_data[row * width + col])

        new_data = bytes(transposed)

        def inverse():
            # Transpose back
            result = bytearray()
            for row in range(height):
                for col in range(width):
                    result.append(new_data[col * height + row])

            # Remove padding
            return bytes(result[:len(binary_data)])

        metadata = {
            'operation': 'transpose_2d',
            'width': width,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def perfect_shuffle(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Perfect shuffle operation."""
        if len(binary_data) <= 1:
            return binary_data, lambda: binary_data, {'operation': 'perfect_shuffle', 'bytes_affected': 0}

        # Perfect shuffle: interleave first and second halves
        mid = len(binary_data) // 2
        first_half = binary_data[:mid]
        second_half = binary_data[mid:]

        result = bytearray()
        for i in range(min(len(first_half), len(second_half))):
            result.append(first_half[i])
            result.append(second_half[i])

        # Add remaining bytes from longer half
        if len(first_half) > len(second_half):
            result.extend(first_half[len(second_half):])
        else:
            result.extend(second_half[len(first_half):])

        new_data = bytes(result)

        def inverse():
            # Perfect unshuffle
            first_part = new_data[::2]
            second_part = new_data[1::2]
            return bytes(first_part + second_part)

        metadata = {
            'operation': 'perfect_shuffle',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def unshuffle(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Unshuffle operation."""
        # Unshuffle is the inverse of perfect shuffle
        new_data, inverse_fn, metadata = self.perfect_shuffle(binary_data)
        metadata['operation'] = 'unshuffle'
        return new_data, inverse_fn, metadata

    # Placeholder implementations for other operations
    def bit_interleave(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Interleave bits from different bytes."""
        # Simplified implementation - just return original data
        return binary_data, lambda: binary_data, {'operation': 'bit_interleave', 'bytes_affected': len(binary_data)}

    def bitonic_sort(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Bitonic sort of bytes."""
        sorted_data = bytes(sorted(binary_data))
        def inverse():
            raise RuntimeError("Sort operations are not reversible")
        return sorted_data, inverse, {'operation': 'bitonic_sort', 'bytes_affected': len(binary_data), 'reversible': False}

    def radix_sort(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Radix sort of bytes."""
        sorted_data = bytes(sorted(binary_data))
        def inverse():
            raise RuntimeError("Sort operations are not reversible")
        return sorted_data, inverse, {'operation': 'radix_sort', 'bytes_affected': len(binary_data), 'reversible': False}

    def frequency_sort(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Sort bytes by frequency."""
        from collections import Counter
        counts = Counter(binary_data)
        sorted_data = bytes(sorted(binary_data, key=lambda x: counts[x]))
        def inverse():
            raise RuntimeError("Sort operations are not reversible")
        return sorted_data, inverse, {'operation': 'frequency_sort', 'bytes_affected': len(binary_data), 'reversible': False}

    def block_shuffle(self, binary_data: bytes, block_size: int, seed: int) -> Tuple[bytes, Callable, Dict]:
        """Shuffle blocks of bytes."""
        import random
        random.seed(seed)

        if block_size <= 0:
            raise ValueError("Block size must be positive")

        # Split into blocks
        blocks = [binary_data[i:i+block_size] for i in range(0, len(binary_data), block_size)]

        # Shuffle blocks
        block_indices = list(range(len(blocks)))
        random.shuffle(block_indices)

        # Create shuffled data
        shuffled_blocks = [blocks[i] for i in block_indices]
        new_data = b''.join(shuffled_blocks)

        def inverse():
            # Restore original block order
            original_blocks = [None] * len(blocks)
            for new_pos, original_idx in enumerate(block_indices):
                original_blocks[original_idx] = new_data[new_pos*block_size:(new_pos+1)*block_size]
            return b''.join(original_blocks)

        metadata = {
            'operation': 'block_shuffle',
            'block_size': block_size,
            'seed': seed,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def interleave_blocks(self, binary_data: bytes, block_size: int) -> Tuple[bytes, Callable, Dict]:
        """Interleave blocks of data."""
        if block_size <= 0:
            raise ValueError("Block size must be positive")

        # Split into blocks
        blocks = [binary_data[i:i+block_size] for i in range(0, len(binary_data), block_size)]

        if len(blocks) < 2:
            return binary_data, lambda: binary_data, {'operation': 'interleave_blocks', 'bytes_affected': 0}

        # Interleave blocks
        result = bytearray()
        max_len = max(len(block) for block in blocks)

        for i in range(max_len):
            for block in blocks:
                if i < len(block):
                    result.append(block[i])

        new_data = bytes(result)

        def inverse():
            # Deinterleave blocks back
            block_count = len(blocks)
            deinterleaved = [bytearray() for _ in range(block_count)]

            for i, byte_val in enumerate(new_data):
                block_idx = i % block_count
                deinterleaved[block_idx].append(byte_val)

            # Reconstruct original blocks
            original_blocks = []
            for block_data in deinterleaved:
                original_blocks.append(bytes(block_data))

            return b''.join(original_blocks)

        metadata = {
            'operation': 'interleave_blocks',
            'block_size': block_size,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def deinterleave_blocks(self, binary_data: bytes, block_size: int) -> Tuple[bytes, Callable, Dict]:
        """Deinterleave blocks of data."""
        new_data, inverse_fn, metadata = self.interleave_blocks(binary_data, block_size)
        metadata['operation'] = 'deinterleave_blocks'
        return new_data, inverse_fn, metadata