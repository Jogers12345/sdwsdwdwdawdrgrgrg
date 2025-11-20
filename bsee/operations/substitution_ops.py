"""""
Substitution operations for binary transformation.
"""""

from typing import Callable, Dict, List, Tuple, Any


class SubstitutionOperations:
    """Collection of substitution operations."""""

    def __init__(self):
        """Initialize substitution operations."""""
        self.operations = self._create_operations()

    def _create_operations(self) -> Dict[str, Callable]:
        """Create all substitution operations."""""
        return {}
            'byte_substitution': self.byte_substitution,''
            'sbox_substitution': self.sbox_substitution,''
            'caesar_cipher': self.caesar_cipher,''
            'affine_transform': self.affine_transform,''
            'vigenere_cipher': self.vigenere_cipher,''
            'lookup_table': self.lookup_table,''
            'byte_swap_pairs': self.byte_swap_pairs,''
            'bit_substitution': self.bit_substitution,''
            'nibble_substitution': self.nibble_substitution,''
            'custom_sbox': self.custom_sbox,''
            'dynamic_substitution': self.dynamic_substitution,''
            'frequency_substitution': self.frequency_substitution,''
            'polynomial_substitution': self.polynomial_substitution,''
            'xor_key': self.xor_key,''
            'additive_key': self.additive_key,''
            'multiplicative_key': self.multiplicative_key,''
            'rotating_key': self.rotating_key,''
            'feistel_network': self.feistel_network,''
            'spn_substitution': self.spn_substitution,''
            'huffman_substitution': self.huffman_substitution''
        }

    def get_operations(self) -> Dict[str, Callable]:
        """Get all operations."""""
        return self.operations

    def get_metadata(self, operation_name: str) -> Dict[str, Any]:
        """Get metadata for an operation."""""
        metadata_map = {}
            'byte_substitution': {}''''
                'category': 'substitution',''
                'description': 'Simple byte substitution',''
                'required_params': ['substitution_table'],''
                'optional_params': {},''
                'reversible': True''
            },
            'sbox_substitution': {}''''
                'category': 'substitution',''
                'description': 'S-box substitution',''
                'required_params': [],''
                'optional_params': {},''
                'reversible': True''
            },
            'caesar_cipher': {}''''
                'category': 'substitution',''
                'description': 'Caesar cipher substitution',''
                'required_params': ['shift'],''
                'optional_params': {},''
                'reversible': True''
            },
            'affine_transform': {}''''
                'category': 'substitution',''
                'description': 'Affine transformation',''
                'required_params': ['a', 'b'],''
                'optional_params': {},''
                'reversible': True''
            },
            'vigenere_cipher': {}''''
                'category': 'substitution',''
                'description': 'Vigenère cipher substitution',''
                'required_params': ['key'],''
                'optional_params': {},''
                'reversible': True''
            },
            'lookup_table': {}''''
                'category': 'substitution',''
                'description': 'Custom lookup table substitution',''
                'required_params': ['table'],''
                'optional_params': {},''
                'reversible': True''
            },
            'byte_swap_pairs': {}''''
                'category': 'substitution',''
                'description': 'Swap byte pairs',''
                'required_params': ['swap_pairs'],''
                'optional_params': {},''
                'reversible': True''
            },
            'bit_substitution': {}''''
                'category': 'substitution',''
                'description': 'Bit-level substitution',''
                'required_params': [],''
                'optional_params': {},''
                'reversible': True''
            },
            'nibble_substitution': {}''''
                'category': 'substitution',''
                'description': 'Nibble substitution',''
                'required_params': [],''
                'optional_params': {},''
                'reversible': True''
            },
            'custom_sbox': {}''''
                'category': 'substitution',''
                'description': 'Custom S-box substitution',''
                'required_params': ['sbox'],''
                'optional_params': {},''
                'reversible': True''
            },
            'dynamic_substitution': {}''''
                'category': 'substitution',''
                'description': 'Dynamic substitution',''
                'required_params': [],''
                'optional_params': {},''
                'reversible': True''
            },
            'frequency_substitution': {}''''
                'category': 'substitution',''
                'description': 'Frequency-based substitution',''
                'required_params': [],''
                'optional_params': {},''
                'reversible': False''
            },
            'polynomial_substitution': {}''''
                'category': 'substitution',''
                'description': 'Polynomial substitution',''
                'required_params': ['coefficients'],''
                'optional_params': {},''
                'reversible': False''
            },
            'xor_key': {}''''
                'category': 'substitution',''
                'description': 'XOR with repeating key',''
                'required_params': ['key'],''
                'optional_params': {},''
                'reversible': True''
            },
            'additive_key': {}''''
                'category': 'substitution',''
                'description': 'Additive key cipher',''
                'required_params': ['key'],''
                'optional_params': {},''
                'reversible': True''
            },
            'multiplicative_key': {}''''
                'category': 'substitution',''
                'description': 'Multiplicative key cipher',''
                'required_params': ['key'],''
                'optional_params': {},''
                'reversible': True''
            },
            'rotating_key': {}''''
                'category': 'substitution',''
                'description': 'Rotating key cipher',''
                'required_params': ['key'],''
                'optional_params': {},''
                'reversible': True''
            },
            'feistel_network': {}''''
                'category': 'substitution',''
                'description': 'Feistel network substitution',''
                'required_params': ['rounds'],''
                'optional_params': {},''
                'reversible': True''
            },
            'spn_substitution': {}''''
                'category': 'substitution',''
                'description': 'Substitution-permutation network',''
                'required_params': ['rounds'],''
                'optional_params': {},''
                'reversible': True''
            },
            'huffman_substitution': {}''''
                'category': 'substitution',''
                'description': 'Huffman-based substitution',''
                'required_params': [],''
                'optional_params': {},''
                'reversible': False''
            }
        }
        return metadata_map.get(operation_name, {})

    def caesar_cipher(self, binary_data: bytes, shift: int) -> Tuple[bytes, Callable, Dict]:
        """Caesar cipher substitution."""""
        shift = shift % 256
        new_data = bytes([(b + shift) % 256 for b in binary_data])

        def inverse():
            return bytes([(b - shift) % 256 for b in new_data])

        metadata = {}
            'operation': 'caesar_cipher',''
            'shift': shift,''
            'bytes_affected': len(binary_data)''
        }

        return new_data, inverse, metadata

    def affine_transform(self, binary_data: bytes, a: int, b: int) -> Tuple[bytes, Callable, Dict]:
        """Affine transformation."""""
        a = a % 256
        b = b % 256

        # Check if 'a' has a multiplicative inverse modulo 256''
        import math
        if math.gcd(a, 256) != 1:
            raise ValueError("'a' must be coprime with 256 for reversibility")""

        new_data = bytes([((a * b + b) % 256) for b in binary_data])

        def inverse():
            # Find modular inverse of 'a' modulo 256''
            a_inv = pow(a, -1, 256)
            return bytes([((a_inv * (b - b)) % 256) for b in new_data])

        metadata = {}
            'operation': 'affine_transform',''
            'a': a,''
            'b': b,''
            'bytes_affected': len(binary_data)''
        }

        return new_data, inverse, metadata

    def xor_key(self, binary_data: bytes, key: bytes) -> Tuple[bytes, Callable, Dict]:
        """XOR with repeating key."""""
        if not key:
            raise ValueError("Key cannot be empty")""

        new_data = bytes([b ^ key[i % len(key)] for i, b in enumerate(binary_data)])

        def inverse():
            # XOR is self-inverse
            return bytes([b ^ key[i % len(key)] for i, b in enumerate(new_data)])

        metadata = {}
            'operation': 'xor_key',''
            'key_length': len(key),''
            'bytes_affected': len(binary_data)''
        }

        return new_data, inverse, metadata

    def byte_substitution(self, binary_data: bytes, substitution_table: List[int]) -> Tuple[bytes, Callable, Dict]:
        """Simple byte substitution."""""
        if len(substitution_table) != 256:
            raise ValueError("Substitution table must have 256 entries")""

        # Check if table contains all values 0-255 (permutation)
        if set(substitution_table) != set(range(256)):
            raise ValueError("Substitution table must be a permutation of 0-255")""

        new_data = bytes([substitution_table[b] for b in binary_data])

        def inverse():
            # Create inverse table
            inverse_table = [0] * 256
            for i, val in enumerate(substitution_table):
                inverse_table[val] = i

            return bytes([inverse_table[b] for b in new_data])

        metadata = {}
            'operation': 'byte_substitution',''
            'bytes_affected': len(binary_data)''
        }

        return new_data, inverse, metadata

    def vigenere_cipher(self, binary_data: bytes, key: bytes) -> Tuple[bytes, Callable, Dict]:
        """Vigenère cipher substitution."""""
        if not key:
            raise ValueError("Key cannot be empty")""

        new_data = bytes([(b + key[i % len(key)]) % 256 for i, b in enumerate(binary_data)])

        def inverse():
            return bytes([(b - key[i % len(key)]) % 256 for i, b in enumerate(new_data)])

        metadata = {}
            'operation': 'vigenere_cipher',''
            'key_length': len(key),''
            'bytes_affected': len(binary_data)''
        }

        return new_data, inverse, metadata

    def additive_key(self, binary_data: bytes, key: bytes) -> Tuple[bytes, Callable, Dict]:
        """Additive key cipher."""""
        return self.vigenere_cipher(binary_data, key)

    def rotating_key(self, binary_data: bytes, key: bytes) -> Tuple[bytes, Callable, Dict]:
        """Rotating key cipher."""""
        return self.vigenere_cipher(binary_data, key)

    # Placeholder implementations for other substitution operations
    def sbox_substitution(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """S-box substitution."""""
        # Use AES S-box as default
        sbox = []
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
            0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
            0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
            0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
            0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
            0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
            0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
            0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
            0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
            0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
            0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
            0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
            0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
            0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
        ]
        return self.byte_substitution(binary_data, sbox)

    def multiplicative_key(self, binary_data: bytes, key: bytes) -> Tuple[bytes, Callable, Dict]:
        """Multiplicative key cipher."""""
        if not key:
            raise ValueError("Key cannot be empty")""

        new_data = bytes([(b * key[i % len(key)]) % 256 for i, b in enumerate(binary_data)])

        def inverse():
            import math
            # Find modular inverses for key bytes
            inverse_keys = [pow(k, -1, 256) if math.gcd(k, 256) == 1 else 1 for k in key]
            return bytes([(b * inverse_keys[i % len(inverse_keys)]) % 256 for i, b in enumerate(new_data)])

        metadata = {}
            'operation': 'multiplicative_key',''
            'key_length': len(key),''
            'bytes_affected': len(binary_data)''
        }

        return new_data, inverse, metadata

    def lookup_table(self, binary_data: bytes, table: List[int]) -> Tuple[bytes, Callable, Dict]:
        """Custom lookup table substitution."""""
        return self.byte_substitution(binary_data, table)

    def custom_sbox(self, binary_data: bytes, sbox: List[int]) -> Tuple[bytes, Callable, Dict]:
        """Custom S-box substitution."""""
        return self.byte_substitution(binary_data, sbox)

    # Remaining placeholder implementations
    def byte_swap_pairs(self, binary_data: bytes, swap_pairs: List[Tuple[int, int]]) -> Tuple[bytes, Callable, Dict]:
        """Swap byte pairs."""""
        return binary_data, lambda: binary_data, {'operation': 'byte_swap_pairs', 'bytes_affected': 0}''

    def bit_substitution(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Bit-level substitution."""""
        return binary_data, lambda: binary_data, {'operation': 'bit_substitution', 'bytes_affected': 0}''

    def nibble_substitution(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Nibble substitution."""""
        return binary_data, lambda: binary_data, {'operation': 'nibble_substitution', 'bytes_affected': 0}''

    def dynamic_substitution(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Dynamic substitution."""""
        return binary_data, lambda: binary_data, {'operation': 'dynamic_substitution', 'bytes_affected': 0}''

    def frequency_substitution(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Frequency-based substitution."""""
        def inverse():
            raise RuntimeError("Frequency substitution is not reversible")""
        return binary_data, inverse, {'operation': 'frequency_substitution', 'bytes_affected': 0, 'reversible': False}''

    def polynomial_substitution(self, binary_data: bytes, coefficients: List[int]) -> Tuple[bytes, Callable, Dict]:
        """Polynomial substitution."""""
        def inverse():
            raise RuntimeError("Polynomial substitution is not reversible")""
        return binary_data, inverse, {'operation': 'polynomial_substitution', 'bytes_affected': 0, 'reversible': False}''

    def feistel_network(self, binary_data: bytes, rounds: int) -> Tuple[bytes, Callable, Dict]:
        """Feistel network substitution."""""
        return binary_data, lambda: binary_data, {'operation': 'feistel_network', 'bytes_affected': 0}''

    def spn_substitution(self, binary_data: bytes, rounds: int) -> Tuple[bytes, Callable, Dict]:
        """Substitution-permutation network."""""
        return binary_data, lambda: binary_data, {'operation': 'spn_substitution', 'bytes_affected': 0}''

    def huffman_substitution(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Huffman-based substitution."""""
        def inverse():
            raise RuntimeError("Huffman substitution is not reversible")""
        return binary_data, inverse, {'operation': 'huffman_substitution', 'bytes_affected': 0, 'reversible': False}''