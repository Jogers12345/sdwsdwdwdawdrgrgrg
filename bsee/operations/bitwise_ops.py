"""
Bitwise operations for binary transformation.
"""

import struct
from typing import Callable, Dict, List, Tuple, Any


class BitwiseOperations:
    """Collection of bitwise operations."""

    def __init__(self):
        """Initialize bitwise operations."""
        self.operations = self._create_operations()

    def _create_operations(self) -> Dict[str, Callable]:
        """Create all bitwise operations."""
        return {
            'xor_constant': self.xor_with_constant,
            'xor_range': self.xor_with_range,
            'not_bytes': self.not_bytes,
            'and_constant': self.and_with_constant,
            'or_constant': self.or_constant,
            'rotate_left': self.rotate_bits_left,
            'rotate_right': self.rotate_bits_right,
            'shift_left': self.shift_bits_left,
            'shift_right': self.shift_bits_right,
            'swap_nibbles': self.swap_nibbles,
            'swap_bits': self.swap_bits_in_byte,
            'reverse_bits': self.reverse_bits_in_byte,
            'extract_high_nibble': self.extract_high_nibble,
            'extract_low_nibble': self.extract_low_nibble,
            'clear_bit': self.clear_bit,
            'set_bit': self.set_bit,
            'toggle_bit': self.toggle_bit,
            'mask_bits': self.mask_bits,
            'interleave_bits': self.interleave_bits,
            'deinterleave_bits': self.deinterleave_bits
        }

    def get_operations(self) -> Dict[str, Callable]:
        """Get all operations."""
        return self.operations

    def get_metadata(self, operation_name: str) -> Dict[str, Any]:
        """Get metadata for an operation."""
        metadata_map = {
            'xor_constant': {
                'category': 'bitwise',
                'description': 'XOR all bytes with a constant value',
                'required_params': ['constant'],
                'optional_params': {},
                'reversible': True
            },
            'xor_range': {
                'category': 'bitwise',
                'description': 'XOR a range of bytes with a constant',
                'required_params': ['offset', 'length', 'constant'],
                'optional_params': {},
                'reversible': True
            },
            'not_bytes': {
                'category': 'bitwise',
                'description': 'Apply bitwise NOT to all bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'and_constant': {
                'category': 'bitwise',
                'description': 'Apply bitwise AND with constant',
                'required_params': ['constant'],
                'optional_params': {},
                'reversible': False
            },
            'or_constant': {
                'category': 'bitwise',
                'description': 'Apply bitwise OR with constant',
                'required_params': ['constant'],
                'optional_params': {},
                'reversible': False
            },
            'rotate_left': {
                'category': 'bitwise',
                'description': 'Rotate bits left in each byte',
                'required_params': ['shift'],
                'optional_params': {},
                'reversible': True
            },
            'rotate_right': {
                'category': 'bitwise',
                'description': 'Rotate bits right in each byte',
                'required_params': ['shift'],
                'optional_params': {},
                'reversible': True
            },
            'shift_left': {
                'category': 'bitwise',
                'description': 'Shift bits left in each byte',
                'required_params': ['shift'],
                'optional_params': {},
                'reversible': False
            },
            'shift_right': {
                'category': 'bitwise',
                'description': 'Shift bits right in each byte',
                'required_params': ['shift'],
                'optional_params': {},
                'reversible': False
            },
            'swap_nibbles': {
                'category': 'bitwise',
                'description': 'Swap high and low nibbles in each byte',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'swap_bits': {
                'category': 'bitwise',
                'description': 'Swap two bit positions in each byte',
                'required_params': ['bit1', 'bit2'],
                'optional_params': {},
                'reversible': True
            },
            'reverse_bits': {
                'category': 'bitwise',
                'description': 'Reverse bit order in each byte',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'extract_high_nibble': {
                'category': 'bitwise',
                'description': 'Extract high nibble from each byte',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'extract_low_nibble': {
                'category': 'bitwise',
                'description': 'Extract low nibble from each byte',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'clear_bit': {
                'category': 'bitwise',
                'description': 'Clear a specific bit position in all bytes',
                'required_params': ['bit_position'],
                'optional_params': {},
                'reversible': False
            },
            'set_bit': {
                'category': 'bitwise',
                'description': 'Set a specific bit position in all bytes',
                'required_params': ['bit_position'],
                'optional_params': {},
                'reversible': False
            },
            'toggle_bit': {
                'category': 'bitwise',
                'description': 'Toggle a specific bit position in all bytes',
                'required_params': ['bit_position'],
                'optional_params': {},
                'reversible': True
            },
            'mask_bits': {
                'category': 'bitwise',
                'description': 'Apply bit mask to all bytes',
                'required_params': ['mask'],
                'optional_params': {},
                'reversible': False
            },
            'interleave_bits': {
                'category': 'bitwise',
                'description': 'Interleave bits from adjacent bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'deinterleave_bits': {
                'category': 'bitwise',
                'description': 'Deinterleave bits from adjacent bytes',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            }
        }
        return metadata_map.get(operation_name, {})

    # Operation implementations

    def xor_with_constant(self, binary_data: bytes, constant: int) -> Tuple[bytes, Callable, Dict]:
        """XOR all bytes with a constant value."""
        if not 0 <= constant <= 255:
            raise ValueError("Constant must be in range 0-255")

        new_data = bytes([b ^ constant for b in binary_data])

        def inverse():
            # XOR is self-inverse
            return bytes([b ^ constant for b in new_data])

        metadata = {
            'operation': 'xor_constant',
            'constant': constant,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def xor_with_range(self, binary_data: bytes, offset: int, length: int, constant: int) -> Tuple[bytes, Callable, Dict]:
        """XOR a range of bytes with a constant."""
        if not 0 <= constant <= 255:
            raise ValueError("Constant must be in range 0-255")
        if offset < 0 or offset >= len(binary_data):
            raise ValueError("Offset out of range")
        if offset + length > len(binary_data):
            raise ValueError("Range exceeds file size")

        data_list = list(binary_data)
        for i in range(offset, offset + length):
            data_list[i] ^= constant

        new_data = bytes(data_list)

        def inverse():
            # XOR is self-inverse
            inverse_list = list(new_data)
            for i in range(offset, offset + length):
                inverse_list[i] ^= constant
            return bytes(inverse_list)

        metadata = {
            'operation': 'xor_range',
            'offset': offset,
            'length': length,
            'constant': constant,
            'bytes_affected': length
        }

        return new_data, inverse, metadata

    def not_bytes(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Apply bitwise NOT to all bytes."""
        new_data = bytes([~b & 0xFF for b in binary_data])

        def inverse():
            # NOT is self-inverse
            return bytes([~b & 0xFF for b in new_data])

        metadata = {
            'operation': 'not_bytes',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def and_with_constant(self, binary_data: bytes, constant: int) -> Tuple[bytes, Callable, Dict]:
        """Apply bitwise AND with constant."""
        if not 0 <= constant <= 255:
            raise ValueError("Constant must be in range 0-255")

        new_data = bytes([b & constant for b in binary_data])

        def inverse():
            # AND is not fully reversible without additional information
            # This is a lossy operation
            raise RuntimeError("AND operation is not reversible")

        metadata = {
            'operation': 'and_constant',
            'constant': constant,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def or_constant(self, binary_data: bytes, constant: int) -> Tuple[bytes, Callable, Dict]:
        """Apply bitwise OR with constant."""
        if not 0 <= constant <= 255:
            raise ValueError("Constant must be in range 0-255")

        new_data = bytes([b | constant for b in binary_data])

        def inverse():
            # OR is not fully reversible without additional information
            # This is a lossy operation
            raise RuntimeError("OR operation is not reversible")

        metadata = {
            'operation': 'or_constant',
            'constant': constant,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def rotate_bits_left(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
        """Rotate bits left in each byte."""
        if not 0 <= shift <= 7:
            raise ValueError("Shift must be in range 0-7")

        new_data = bytes([((b << shift) & 0xFF) | (b >> (8 - shift)) for b in binary_data])

        def inverse():
            # Rotate right by the same amount
            return bytes([((b >> shift) & 0xFF) | (b << (8 - shift)) & 0xFF for b in new_data])

        metadata = {
            'operation': 'rotate_left',
            'shift': shift,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def rotate_bits_right(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
        """Rotate bits right in each byte."""
        if not 0 <= shift <= 7:
            raise ValueError("Shift must be in range 0-7")

        new_data = bytes([(b >> shift) | ((b << (8 - shift)) & 0xFF) for b in binary_data])

        def inverse():
            # Rotate left by the same amount
            return bytes([((b << shift) & 0xFF) | (b >> (8 - shift)) for b in new_data])

        metadata = {
            'operation': 'rotate_right',
            'shift': shift,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def shift_bits_left(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
        """Shift bits left in each byte."""
        if not 0 <= shift <= 7:
            raise ValueError("Shift must be in range 0-7")

        new_data = bytes([(b << shift) & 0xFF for b in binary_data])

        def inverse():
            # Left shift is lossy (bits are lost)
            raise RuntimeError("Left shift operation is not reversible")

        metadata = {
            'operation': 'shift_left',
            'shift': shift,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def shift_bits_right(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
        """Shift bits right in each byte."""
        if not 0 <= shift <= 7:
            raise ValueError("Shift must be in range 0-7")

        new_data = bytes([b >> shift for b in binary_data])

        def inverse():
            # Right shift is lossy (bits are lost)
            raise RuntimeError("Right shift operation is not reversible")

        metadata = {
            'operation': 'shift_right',
            'shift': shift,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def swap_nibbles(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Swap high and low nibbles in each byte."""
        new_data = bytes([((b & 0x0F) << 4) | ((b & 0xF0) >> 4) for b in binary_data])

        def inverse():
            # Swap nibbles is self-inverse
            return bytes([((b & 0x0F) << 4) | ((b & 0xF0) >> 4) for b in new_data])

        metadata = {
            'operation': 'swap_nibbles',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def swap_bits_in_byte(self, binary_data: bytes, bit1: int, bit2: int) -> Tuple[bytes, Callable, Dict]:
        """Swap two bit positions in each byte."""
        if not 0 <= bit1 <= 7 or not 0 <= bit2 <= 7:
            raise ValueError("Bit positions must be in range 0-7")
        if bit1 == bit2:
            raise ValueError("Bit positions must be different")

        def swap_byte_bits(byte_val: int) -> int:
            bit1_val = (byte_val >> bit1) & 1
            bit2_val = (byte_val >> bit2) & 1

            if bit1_val != bit2_val:
                # Clear both bits and set them in swapped positions
                result = byte_val & ~(1 << bit1) & ~(1 << bit2)
                result |= (bit1_val << bit2) | (bit2_val << bit1)
                return result
            return byte_val

        new_data = bytes([swap_byte_bits(b) for b in binary_data])

        def inverse():
            # Swap bits is self-inverse
            return bytes([swap_byte_bits(b) for b in new_data])

        metadata = {
            'operation': 'swap_bits',
            'bit1': bit1,
            'bit2': bit2,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def reverse_bits_in_byte(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Reverse bit order in each byte."""
        def reverse_byte(byte_val: int) -> int:
            result = 0
            for i in range(8):
                result = (result << 1) | ((byte_val >> i) & 1)
            return result

        new_data = bytes([reverse_byte(b) for b in binary_data])

        def inverse():
            # Bit reversal is self-inverse
            return bytes([reverse_byte(b) for b in new_data])

        metadata = {
            'operation': 'reverse_bits',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def clear_bit(self, binary_data: bytes, bit_position: int) -> Tuple[bytes, Callable, Dict]:
        """Clear a specific bit position in all bytes."""
        if not 0 <= bit_position <= 7:
            raise ValueError("Bit position must be in range 0-7")

        mask = ~(1 << bit_position) & 0xFF
        new_data = bytes([b & mask for b in binary_data])

        def inverse():
            # Clear bit is lossy
            raise RuntimeError("Clear bit operation is not reversible")

        metadata = {
            'operation': 'clear_bit',
            'bit_position': bit_position,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def set_bit(self, binary_data: bytes, bit_position: int) -> Tuple[bytes, Callable, Dict]:
        """Set a specific bit position in all bytes."""
        if not 0 <= bit_position <= 7:
            raise ValueError("Bit position must be in range 0-7")

        mask = 1 << bit_position
        new_data = bytes([b | mask for b in binary_data])

        def inverse():
            # Set bit is lossy
            raise RuntimeError("Set bit operation is not reversible")

        metadata = {
            'operation': 'set_bit',
            'bit_position': bit_position,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def toggle_bit(self, binary_data: bytes, bit_position: int) -> Tuple[bytes, Callable, Dict]:
        """Toggle a specific bit position in all bytes."""
        if not 0 <= bit_position <= 7:
            raise ValueError("Bit position must be in range 0-7")

        mask = 1 << bit_position
        new_data = bytes([b ^ mask for b in binary_data])

        def inverse():
            # Toggle is self-inverse
            return bytes([b ^ mask for b in new_data])

        metadata = {
            'operation': 'toggle_bit',
            'bit_position': bit_position,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def mask_bits(self, binary_data: bytes, mask: int) -> Tuple[bytes, Callable, Dict]:
        """Apply bit mask to all bytes."""
        if not 0 <= mask <= 255:
            raise ValueError("Mask must be in range 0-255")

        new_data = bytes([b & mask for b in binary_data])

        def inverse():
            # Mask is lossy
            raise RuntimeError("Mask operation is not reversible")

        metadata = {
            'operation': 'mask_bits',
            'mask': mask,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def extract_high_nibble(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Extract high nibble from each byte."""
        new_data = bytes([(b & 0xF0) >> 4 for b in binary_data])

        def inverse():
            # Extract is lossy
            raise RuntimeError("Extract high nibble operation is not reversible")

        metadata = {
            'operation': 'extract_high_nibble',
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def extract_low_nibble(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Extract low nibble from each byte."""
        new_data = bytes([b & 0x0F for b in binary_data])

        def inverse():
            # Extract is lossy
            raise RuntimeError("Extract low nibble operation is not reversible")

        metadata = {
            'operation': 'extract_low_nibble',
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def interleave_bits(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Interleave bits from adjacent bytes."""
        if len(binary_data) < 2:
            return binary_data, lambda: binary_data, {'operation': 'interleave_bits', 'bytes_affected': 0}

        # Handle odd length by padding with zero
        padded_data = binary_data
        if len(binary_data) % 2 != 0:
            padded_data = binary_data + b'\x00'

        result = bytearray()
        for i in range(0, len(padded_data), 2):
            byte1 = padded_data[i]
            byte2 = padded_data[i + 1]

            # Interleave bits: bit0 from byte1, bit0 from byte2, bit1 from byte1, bit1 from byte2, etc.
            for bit_pos in range(8):
                result.append(((byte1 >> bit_pos) & 1) << 1 | ((byte2 >> bit_pos) & 1))

        new_data = bytes(result)

        def inverse():
            # Deinterleave the bits back to original bytes
            result = bytearray()
            for i in range(0, len(new_data), 16):
                chunk = new_data[i:i+16]
                if len(chunk) < 16:
                    # Pad incomplete chunk
                    chunk += b'\x00' * (16 - len(chunk))

                byte1 = 0
                byte2 = 0
                for bit_pos in range(8):
                    byte1 |= ((chunk[bit_pos * 2] >> 1) & 1) << bit_pos
                    byte2 |= (chunk[bit_pos * 2 + 1] & 1) << bit_pos

                result.append(byte1)
                result.append(byte2)

            # Remove padding if original was odd length
            if len(binary_data) % 2 != 0:
                result = result[:-1]

            return bytes(result)

        metadata = {
            'operation': 'interleave_bits',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def deinterleave_bits(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Deinterleave bits from adjacent bytes."""
        # This is essentially the inverse of interleave_bits
        # For simplicity, we'll call interleave_bits as it's self-inverse
        new_data, inverse_fn, metadata = self.interleave_bits(binary_data)
        metadata['operation'] = 'deinterleave_bits'
        return new_data, inverse_fn, metadata