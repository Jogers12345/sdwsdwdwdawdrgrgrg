"""
Custom operations for binary transformation.
"""

from typing import Callable, Dict, List, Tuple, Any


class CustomOperations:
    """Collection of custom operations."""

    def __init__(self):
        """Initialize custom operations."""
        self.operations = self._create_operations()

    def _create_operations(self) -> Dict[str, Callable]:
        """Create all custom operations."""
        return {
            'custom_filter': self.custom_filter,
            'pattern_replace': self.pattern_replace,
            'data_embedding': self.data_embedding,
            'data_extraction': self.data_extraction,
            'checksum_add': self.checksum_add,
            'checksum_verify': self.checksum_verify,
            'compression_custom': self.compression_custom,
            'encryption_custom': self.encryption_custom,
            'hash_transform': self.hash_transform,
            'error_correction': self.error_correction,
            'steganography_embed': self.steganography_embed,
            'steganography_extract': self.steganography_extract,
            'dna_encoding': self.dna_encoding,
            'dna_decoding': self.dna_decoding,
            'base64_encode': self.base64_encode,
            'base64_decode': self.base64_decode
        }

    def get_operations(self) -> Dict[str, Callable]:
        """Get all operations."""
        return self.operations

    def get_metadata(self, operation_name: str) -> Dict[str, Any]:
        """Get metadata for an operation."""
        metadata_map = {
            'custom_filter': {
                'category': 'custom',
                'description': 'Apply custom filter function',
                'required_params': ['filter_function'],
                'optional_params': {},
                'reversible': False
            },
            'pattern_replace': {
                'category': 'custom',
                'description': 'Replace pattern in binary data',
                'required_params': ['pattern', 'replacement'],
                'optional_params': {},
                'reversible': False
            },
            'data_embedding': {
                'category': 'custom',
                'description': 'Embed data into binary',
                'required_params': ['embedded_data'],
                'optional_params': {},
                'reversible': True
            },
            'data_extraction': {
                'category': 'custom',
                'description': 'Extract embedded data',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'checksum_add': {
                'category': 'custom',
                'description': 'Add checksum to binary',
                'required_params': ['checksum_type'],
                'optional_params': {},
                'reversible': False
            },
            'checksum_verify': {
                'category': 'custom',
                'description': 'Verify checksum in binary',
                'required_params': ['checksum_type'],
                'optional_params': {},
                'reversible': False
            },
            'compression_custom': {
                'category': 'custom',
                'description': 'Custom compression algorithm',
                'required_params': ['algorithm'],
                'optional_params': {},
                'reversible': False
            },
            'encryption_custom': {
                'category': 'custom',
                'description': 'Custom encryption algorithm',
                'required_params': ['algorithm', 'key'],
                'optional_params': {},
                'reversible': True
            },
            'hash_transform': {
                'category': 'custom',
                'description': 'Transform using hash function',
                'required_params': ['hash_function'],
                'optional_params': {},
                'reversible': False
            },
            'error_correction': {
                'category': 'custom',
                'description': 'Add error correction codes',
                'required_params': ['ecc_type'],
                'optional_params': {},
                'reversible': True
            },
            'steganography_embed': {
                'category': 'custom',
                'description': 'Embed data using steganography',
                'required_params': ['hidden_data'],
                'optional_params': {},
                'reversible': True
            },
            'steganography_extract': {
                'category': 'custom',
                'description': 'Extract steganographic data',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'dna_encoding': {
                'category': 'custom',
                'description': 'Encode binary data as DNA sequence',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'dna_decoding': {
                'category': 'custom',
                'description': 'Decode DNA sequence to binary',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'base64_encode': {
                'category': 'custom',
                'description': 'Base64 encode binary data',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'base64_decode': {
                'category': 'custom',
                'description': 'Base64 decode to binary',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            }
        }
        return metadata_map.get(operation_name, {})

    def base64_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Base64 encode binary data."""
        import base64

        encoded_data = base64.b64encode(binary_data)

        def inverse():
            return base64.b64decode(encoded_data)

        metadata = {
            'operation': 'base64_encode',
            'bytes_affected': len(binary_data)
        }

        return encoded_data, inverse, metadata

    def base64_decode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Base64 decode to binary."""
        import base64

        decoded_data = base64.b64decode(binary_data)

        def inverse():
            return base64.b64encode(decoded_data)

        metadata = {
            'operation': 'base64_decode',
            'bytes_affected': len(binary_data)
        }

        return decoded_data, inverse, metadata

    def data_embedding(self, binary_data: bytes, embedded_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Embed data into binary."""
        # Simple LSB steganography - embed data in least significant bits
        if len(embedded_data) * 8 > len(binary_data):
            raise ValueError("Not enough space to embed data")

        data_list = list(binary_data)
        bit_index = 0

        # Embed data length first (4 bytes)
        length_bytes = len(embedded_data).to_bytes(4, 'big')
        for length_byte in length_bytes:
            for bit_pos in range(8):
                if bit_index < len(data_list):
                    bit = (length_byte >> bit_pos) & 1
                    data_list[bit_index] = (data_list[bit_index] & 0xFE) | bit
                    bit_index += 1

        # Embed actual data
        for embed_byte in embedded_data:
            for bit_pos in range(8):
                if bit_index < len(data_list):
                    bit = (embed_byte >> bit_pos) & 1
                    data_list[bit_index] = (data_list[bit_index] & 0xFE) | bit
                    bit_index += 1

        new_data = bytes(data_list)

        def inverse():
            # Extract embedded data
            bit_index = 0

            # Extract length
            length_bytes = bytearray(4)
            for i in range(4):
                length_byte = 0
                for bit_pos in range(8):
                    if bit_index < len(new_data):
                        bit = new_data[bit_index] & 1
                        length_byte |= (bit << bit_pos)
                        bit_index += 1
                length_bytes[i] = length_byte

            embedded_length = int.from_bytes(length_bytes, 'big')

            # Extract embedded data
            extracted_data = bytearray(embedded_length)
            for i in range(embedded_length):
                extracted_byte = 0
                for bit_pos in range(8):
                    if bit_index < len(new_data):
                        bit = new_data[bit_index] & 1
                        extracted_byte |= (bit << bit_pos)
                        bit_index += 1
                extracted_data[i] = extracted_byte

            # Restore original data by clearing LSBs
            original_list = list(new_data)
            for i in range(min(len(original_list), bit_index)):
                original_list[i] = original_list[i] & 0xFE

            return bytes(original_list), bytes(extracted_data)

        def inverse_only():
            original_data, _ = inverse()
            return original_data

        metadata = {
            'operation': 'data_embedding',
            'embedded_length': len(embedded_data),
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse_only, metadata

    def dna_encoding(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Encode binary data as DNA sequence."""
        # Map 2 bits to DNA nucleotides: 00->A, 01->C, 10->G, 11->T
        nucleotides = {0: b'A', 1: b'C', 2: b'G', 3: b'T'}

        dna_sequence = bytearray()
        for i in range(0, len(binary_data), 2):
            if i + 1 < len(binary_data):
                # Two bytes = 16 bits = 8 nucleotides
                combined = (binary_data[i] << 8) | binary_data[i + 1]
                for j in range(8):
                    two_bits = (combined >> (14 - j * 2)) & 3
                    dna_sequence.extend(nucleotides[two_bits])
            else:
                # Single byte = 8 bits = 4 nucleotides
                byte_val = binary_data[i]
                for j in range(4):
                    two_bits = (byte_val >> (6 - j * 2)) & 3
                    dna_sequence.extend(nucleotides[two_bits])

        new_data = bytes(dna_sequence)

        def inverse():
            # Map nucleotides back to bits
            nucleotide_to_bits = {ord('A'): 0, ord('C'): 1, ord('G'): 2, ord('T'): 3}

            binary_result = bytearray()
            i = 0
            while i < len(new_data):
                if i + 7 < len(new_data):
                    # 8 nucleotides = 2 bytes
                    combined = 0
                    for j in range(8):
                        nucleotide = new_data[i + j]
                        if nucleotide in nucleotide_to_bits:
                            combined = (combined << 2) | nucleotide_to_bits[nucleotide]
                        else:
                            # Invalid nucleotide, use A as default
                            combined = (combined << 2) | 0

                    binary_result.append((combined >> 8) & 0xFF)
                    binary_result.append(combined & 0xFF)
                    i += 8
                else:
                    # Handle partial sequence (shouldn't happen with proper encoding)
                    break

            return bytes(binary_result)

        metadata = {
            'operation': 'dna_encoding',
            'dna_length': len(new_data),
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def dna_decoding(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Decode DNA sequence to binary."""
        new_data, inverse_fn, metadata = self.dna_encoding(binary_data)
        metadata['operation'] = 'dna_decoding'
        return new_data, inverse_fn, metadata

    # Placeholder implementations for other custom operations
    def custom_filter(self, binary_data: bytes, filter_function: str) -> Tuple[bytes, Callable, Dict]:
        """Apply custom filter function."""
        def inverse():
            raise RuntimeError("Custom filter is not reversible")
        return binary_data, inverse, {'operation': 'custom_filter', 'bytes_affected': 0, 'reversible': False}

    def pattern_replace(self, binary_data: bytes, pattern: bytes, replacement: bytes) -> Tuple[bytes, Callable, Dict]:
        """Replace pattern in binary data."""
        new_data = binary_data.replace(pattern, replacement)
        def inverse():
            # Pattern replacement is generally not reversible
            raise RuntimeError("Pattern replacement is not reversible")
        return new_data, inverse, {'operation': 'pattern_replace', 'bytes_affected': len(binary_data), 'reversible': False}

    def data_extraction(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Extract embedded data."""
        def inverse():
            raise RuntimeError("Data extraction is not reversible")
        return binary_data, inverse, {'operation': 'data_extraction', 'bytes_affected': 0, 'reversible': False}

    def checksum_add(self, binary_data: bytes, checksum_type: str) -> Tuple[bytes, Callable, Dict]:
        """Add checksum to binary."""
        import hashlib

        if checksum_type == 'md5':
            checksum = hashlib.md5(binary_data).digest()
        elif checksum_type == 'sha1':
            checksum = hashlib.sha1(binary_data).digest()
        elif checksum_type == 'sha256':
            checksum = hashlib.sha256(binary_data).digest()
        else:
            checksum = b''

        new_data = binary_data + checksum

        def inverse():
            return new_data[:len(binary_data)]

        metadata = {
            'operation': 'checksum_add',
            'checksum_type': checksum_type,
            'checksum_length': len(checksum),
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def checksum_verify(self, binary_data: bytes, checksum_type: str) -> Tuple[bytes, Callable, Dict]:
        """Verify checksum in binary."""
        import hashlib

        # Assume checksum is at the end
        if checksum_type == 'md5':
            checksum_length = 16
        elif checksum_type == 'sha1':
            checksum_length = 20
        elif checksum_type == 'sha256':
            checksum_length = 32
        else:
            return binary_data, lambda: binary_data, {'operation': 'checksum_verify', 'bytes_affected': 0}

        if len(binary_data) < checksum_length:
            return binary_data, lambda: binary_data, {'operation': 'checksum_verify', 'bytes_affected': 0}

        data_part = binary_data[:-checksum_length]
        stored_checksum = binary_data[-checksum_length:]

        if checksum_type == 'md5':
            calculated_checksum = hashlib.md5(data_part).digest()
        elif checksum_type == 'sha1':
            calculated_checksum = hashlib.sha1(data_part).digest()
        elif checksum_type == 'sha256':
            calculated_checksum = hashlib.sha256(data_part).digest()
        else:
            calculated_checksum = b''

        is_valid = calculated_checksum == stored_checksum

        def inverse():
            return binary_data

        metadata = {
            'operation': 'checksum_verify',
            'checksum_type': checksum_type,
            'checksum_valid': is_valid,
            'bytes_affected': len(binary_data)
        }

        return binary_data, inverse, metadata

    def compression_custom(self, binary_data: bytes, algorithm: str) -> Tuple[bytes, Callable, Dict]:
        """Custom compression algorithm."""
        def inverse():
            raise RuntimeError("Custom compression is not reversible")
        return binary_data, inverse, {'operation': 'compression_custom', 'bytes_affected': 0, 'reversible': False}

    def encryption_custom(self, binary_data: bytes, algorithm: str, key: bytes) -> Tuple[bytes, Callable, Dict]:
        """Custom encryption algorithm."""
        # Simple XOR encryption as placeholder
        new_data = bytes([b ^ key[i % len(key)] for i, b in enumerate(binary_data)])

        def inverse():
            return bytes([b ^ key[i % len(key)] for i, b in enumerate(new_data)])

        metadata = {
            'operation': 'encryption_custom',
            'algorithm': algorithm,
            'key_length': len(key),
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def hash_transform(self, binary_data: bytes, hash_function: str) -> Tuple[bytes, Callable, Dict]:
        """Transform using hash function."""
        import hashlib

        if hash_function == 'md5':
            hash_result = hashlib.md5(binary_data).digest()
        elif hash_function == 'sha1':
            hash_result = hashlib.sha1(binary_data).digest()
        elif hash_function == 'sha256':
            hash_result = hashlib.sha256(binary_data).digest()
        else:
            hash_result = b''

        def inverse():
            raise RuntimeError("Hash transform is not reversible")
        return hash_result, inverse, {'operation': 'hash_transform', 'bytes_affected': 0, 'reversible': False}

    def error_correction(self, binary_data: bytes, ecc_type: str) -> Tuple[bytes, Callable, Dict]:
        """Add error correction codes."""
        # Placeholder - just append some parity bits
        parity = sum(binary_data) % 256
        new_data = binary_data + bytes([parity])

        def inverse():
            return new_data[:-1]

        metadata = {
            'operation': 'error_correction',
            'ecc_type': ecc_type,
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def steganography_embed(self, binary_data: bytes, hidden_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Embed data using steganography."""
        # Use data_embedding as placeholder
        return self.data_embedding(binary_data, hidden_data)

    def steganography_extract(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Extract steganographic data."""
        def inverse():
            raise RuntimeError("Steganography extraction is not reversible")
        return binary_data, inverse, {'operation': 'steganography_extract', 'bytes_affected': 0, 'reversible': False}