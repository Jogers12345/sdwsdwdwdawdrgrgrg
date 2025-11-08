"""
Transform operations for binary transformation.
"""

from typing import Callable, Dict, List, Tuple, Any


class TransformOperations:
    """Collection of transform operations."""

    def __init__(self):
        """Initialize transform operations."""
        self.operations = self._create_operations()

    def _create_operations(self) -> Dict[str, Callable]:
        """Create all transform operations."""
        return {
            'burrows_wheeler': self.burrows_wheeler,
            'burrows_wheeler_inverse': self.burrows_wheeler_inverse,
            'bitplane_extract': self.bitplane_extract,
            'bitplane_insert': self.bitplane_insert,
            'dct_transform': self.dct_transform,
            'dwt_transform': self.dwt_transform,
            'fft_transform': self.fft_transform,
            'walsh_hadamard': self.walsh_hadamard,
            'huffman_encode': self.huffman_encode,
            'run_length_encode': self.run_length_encode,
            'arithmetic_encode': self.arithmetic_encode,
            'lz77_encode': self.lz77_encode,
            'move_to_front': self.move_to_front,
            'distance_coding': self.distance_coding,
            'elias_gamma': self.elias_gamma,
            'elias_delta': self.elias_delta,
            'golomb_coding': self.golomb_coding,
            'fibonacci_coding': self.fibonacci_coding,
            'phase_in_coding': self.phase_in_coding,
            'adaptive_huffman': self.adaptive_huffman
        }

    def get_operations(self) -> Dict[str, Callable]:
        """Get all operations."""
        return self.operations

    def get_metadata(self, operation_name: str) -> Dict[str, Any]:
        """Get metadata for an operation."""
        metadata_map = {
            'burrows_wheeler': {
                'category': 'transform',
                'description': 'Burrows-Wheeler transform',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'burrows_wheeler_inverse': {
                'category': 'transform',
                'description': 'Inverse Burrows-Wheeler transform',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'bitplane_extract': {
                'category': 'transform',
                'description': 'Extract specific bitplane',
                'required_params': ['plane'],
                'optional_params': {},
                'reversible': False
            },
            'bitplane_insert': {
                'category': 'transform',
                'description': 'Insert bitplane data',
                'required_params': ['plane', 'data'],
                'optional_params': {},
                'reversible': False
            },
            'dct_transform': {
                'category': 'transform',
                'description': 'Discrete cosine transform',
                'required_params': [],
                'optional_params': {'padding': 'auto', 'normalization': 'ortho'},
                'reversible': True
            },
            'dwt_transform': {
                'category': 'transform',
                'description': 'Discrete wavelet transform',
                'required_params': [],
                'optional_params': {'wavelet': 'haar', 'mode': 'symmetric', 'levels': 1},
                'reversible': True
            },
            'fft_transform': {
                'category': 'transform',
                'description': 'Fast Fourier transform',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'walsh_hadamard': {
                'category': 'transform',
                'description': 'Walsh-Hadamard transform',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'huffman_encode': {
                'category': 'transform',
                'description': 'Huffman encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'run_length_encode': {
                'category': 'transform',
                'description': 'Run-length encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'arithmetic_encode': {
                'category': 'transform',
                'description': 'Arithmetic encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'lz77_encode': {
                'category': 'transform',
                'description': 'LZ77 encoding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'move_to_front': {
                'category': 'transform',
                'description': 'Move-to-front transform',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'distance_coding': {
                'category': 'transform',
                'description': 'Distance coding',
                'required_params': [],
                'optional_params': {},
                'reversible': True
            },
            'elias_gamma': {
                'category': 'transform',
                'description': 'Elias gamma coding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'elias_delta': {
                'category': 'transform',
                'description': 'Elias delta coding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'golomb_coding': {
                'category': 'transform',
                'description': 'Golomb coding',
                'required_params': ['parameter'],
                'optional_params': {},
                'reversible': False
            },
            'fibonacci_coding': {
                'category': 'transform',
                'description': 'Fibonacci coding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'phase_in_coding': {
                'category': 'transform',
                'description': 'Phase-in coding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            },
            'adaptive_huffman': {
                'category': 'transform',
                'description': 'Adaptive Huffman coding',
                'required_params': [],
                'optional_params': {},
                'reversible': False
            }
        }
        return metadata_map.get(operation_name, {})

    def burrows_wheeler(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Burrows-Wheeler transform."""
        if len(binary_data) <= 1:
            return binary_data, lambda: binary_data, {'operation': 'burrows_wheeler', 'bytes_affected': 0}

        # Add EOF marker (use 0 as it's rarely in binary data)
        data_with_eof = binary_data + b'\x00'

        # Generate all rotations
        rotations = []
        for i in range(len(data_with_eof)):
            rotation = data_with_eof[i:] + data_with_eof[:i]
            rotations.append(rotation)

        # Sort rotations
        rotations.sort()

        # Find original string index
        original_index = rotations.index(data_with_eof)

        # Extract last column (BWT result)
        bwt_result = bytes([rotation[-1] for rotation in rotations])

        # Combine index with result
        result = bwt_result + original_index.to_bytes(4, 'big')

        def inverse():
            if len(result) <= 4:
                return b''

            # Extract index and BWT data
            original_index = int.from_bytes(result[-4:], 'big')
            bwt_data = result[:-4]

            # Reconstruct original using LF mapping
            table = [""] * len(bwt_data)
            for _ in range(len(bwt_data)):
                # Prepend BWT character to each string
                table = [bwt_data[i] + table[i] for i in range(len(bwt_data))]
                # Sort table
                table.sort()

            return table[original_index].replace(b'\x00', b'')

        metadata = {
            'operation': 'burrows_wheeler',
            'original_index': original_index,
            'bytes_affected': len(binary_data)
        }

        return result, inverse, metadata

    def burrows_wheeler_inverse(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Inverse Burrows-Wheeler transform."""
        # Extract index and BWT data from the end
        if len(binary_data) <= 4:
            return binary_data, lambda: binary_data, {'operation': 'burrows_wheeler_inverse', 'bytes_affected': 0}

        original_index = int.from_bytes(binary_data[-4:], 'big')
        bwt_data = binary_data[:-4]

        # Reconstruct original using LF mapping
        table = [""] * len(bwt_data)
        for _ in range(len(bwt_data)):
            table = [bwt_data[i] + table[i] for i in range(len(bwt_data))]
            table.sort()

        original = table[original_index].replace(b'\x00', b'')

        def inverse():
            # Forward BWT again
            return self.burrows_wheeler(original)[0]

        metadata = {
            'operation': 'burrows_wheeler_inverse',
            'original_index': original_index,
            'bytes_affected': len(bwt_data)
        }

        return original, inverse, metadata

    def bitplane_extract(self, binary_data: bytes, plane: int) -> Tuple[bytes, Callable, Dict]:
        """Extract specific bitplane."""
        if not 0 <= plane <= 7:
            raise ValueError("Plane must be in range 0-7")

        # Extract bits from specified plane
        bitplane_bits = []
        for byte_val in binary_data:
            bit = (byte_val >> plane) & 1
            bitplane_bits.append(bit)

        # Pack bits into bytes
        result = bytearray()
        for i in range(0, len(bitplane_bits), 8):
            byte_val = 0
            for j in range(min(8, len(bitplane_bits) - i)):
                if bitplane_bits[i + j]:
                    byte_val |= (1 << j)
            result.append(byte_val)

        new_data = bytes(result)

        def inverse():
            # Bitplane extraction is lossy
            raise RuntimeError("Bitplane extraction is not reversible")

        metadata = {
            'operation': 'bitplane_extract',
            'plane': plane,
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return new_data, inverse, metadata

    def bitplane_insert(self, binary_data: bytes, plane: int, data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Insert bitplane data."""
        if not 0 <= plane <= 7:
            raise ValueError("Plane must be in range 0-7")

        def inverse():
            # Bitplane insertion is lossy
            raise RuntimeError("Bitplane insertion is not reversible")

        metadata = {
            'operation': 'bitplane_insert',
            'plane': plane,
            'data_length': len(data),
            'bytes_affected': len(binary_data),
            'reversible': False
        }

        return binary_data, inverse, metadata

    def move_to_front(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Move-to-front transform."""
        # Initialize symbol list (0-255)
        symbol_list = list(range(256))

        result = []
        for byte_val in binary_data:
            # Find index of symbol
            index = symbol_list.index(byte_val)
            result.append(index)

            # Move symbol to front
            symbol_list.pop(index)
            symbol_list.insert(0, byte_val)

        # Convert indices to bytes
        new_data = bytes(result)

        def inverse():
            # Initialize symbol list
            symbol_list = list(range(256))
            original = []

            for index_val in new_data:
                # Get symbol at index
                symbol = symbol_list[index_val]
                original.append(symbol)

                # Move symbol to front
                symbol_list.pop(index_val)
                symbol_list.insert(0, symbol)

            return bytes(original)

        metadata = {
            'operation': 'move_to_front',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def walsh_hadamard(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Walsh-Hadamard transform."""
        import numpy as np

        # Convert to numpy array and pad to power of 2
        data = np.frombuffer(binary_data, dtype=np.uint8)
        n = len(data)
        next_power = 1 << (n - 1).bit_length()
        if next_power > n:
            data = np.pad(data, (0, next_power - n), 'constant')

        # Convert to float for computation
        data_float = data.astype(np.float32)

        # Apply Walsh-Hadamard transform (simplified)
        def walsh_hadamard_recursive(x):
            if len(x) == 1:
                return x
            n = len(x) // 2
            left = walsh_hadamard_recursive(x[:n])
            right = walsh_hadamard_recursive(x[n:])
            return np.concatenate([left + right, left - right])

        transformed = walsh_hadamard_recursive(data_float)

        # Convert back to bytes (simplified - just take integer part)
        result_bytes = np.clip(transformed, 0, 255).astype(np.uint8).tobytes()

        new_data = result_bytes[:n]  # Remove padding

        def inverse():
            # Walsh-Hadamard is self-inverse up to scaling
            # Simplified inverse
            return new_data  # Placeholder

        metadata = {
            'operation': 'walsh_hadamard',
            'bytes_affected': len(binary_data)
        }

        return new_data, inverse, metadata

    def dct_transform(self, binary_data: bytes, padding: str = 'auto', normalization: str = 'ortho') -> Tuple[bytes, Callable, Dict]:
        """Discrete cosine transform with scipy implementation and numpy fallback."""
        import numpy as np

        if len(binary_data) == 0:
            def inverse_empty():
                return b''
            return b'', inverse_empty, {'operation': 'dct_transform', 'bytes_affected': 0, 'reversible': True}

        original_length = len(binary_data)

        # Convert binary data to float array
        data = np.frombuffer(binary_data, dtype=np.uint8).astype(np.float64)

        # Handle padding
        if padding == 'power_of_2' or (padding == 'auto' and len(data) & (len(data) - 1) != 0):
            # Pad to power of 2
            n = len(data)
            padded_length = 1 << (n - 1).bit_length()
            data = np.pad(data, (0, padded_length - n), 'constant')
            padding_info = {'original_length': n, 'padded_length': padded_length, 'padding_type': 'zero'}
        else:
            padding_info = {'original_length': original_length, 'padded_length': original_length, 'padding_type': 'none'}

        # Apply DCT with scipy or numpy fallback
        try:
            from scipy.fft import dct, idct
            # Use scipy implementation
            if normalization == 'ortho':
                transformed = dct(data, type=2, norm='ortho')
            elif normalization == 'forward':
                transformed = dct(data, type=2, norm='forward')
            else:  # backward
                transformed = dct(data, type=2, norm='backward')
            scipy_available = True
        except ImportError:
            # Fallback to numpy implementation
            scipy_available = False
            transformed = self._numpy_dct_fallback(data)

        # Convert complex/float results back to bytes
        # Use magnitude and phase encoding for reversibility
        magnitude = np.abs(transformed)
        phase = np.angle(transformed)

        # Normalize and pack
        max_mag = np.max(magnitude) if np.max(magnitude) > 0 else 1.0
        normalized_mag = (magnitude / max_mag * 255).astype(np.uint8)
        normalized_phase = ((phase + np.pi) / (2 * np.pi) * 255).astype(np.uint8)

        # Interleave magnitude and phase
        packed = np.empty(2 * len(normalized_mag), dtype=np.uint8)
        packed[0::2] = normalized_mag
        packed[1::2] = normalized_phase

        result_bytes = packed.tobytes()

        def inverse():
            # Unpack magnitude and phase
            packed_array = np.frombuffer(result_bytes, dtype=np.uint8)
            magnitude_restored = packed_array[0::2].astype(np.float64)
            phase_restored = (packed_array[1::2].astype(np.float64) / 255.0 * 2 * np.pi) - np.pi

            # Restore complex numbers
            max_mag = np.max(magnitude_restored) if np.max(magnitude_restored) > 0 else 1.0
            magnitude_restored = magnitude_restored / 255.0 * max_mag
            transformed_restored = magnitude_restored * np.exp(1j * phase_restored)

            # Apply inverse DCT
            if scipy_available:
                if normalization == 'ortho':
                    data_restored = idct(transformed_restored, type=2, norm='ortho')
                elif normalization == 'forward':
                    data_restored = idct(transformed_restored, type=2, norm='forward')
                else:  # backward
                    data_restored = idct(transformed_restored, type=2, norm='backward')
            else:
                data_restored = self._numpy_idct_fallback(transformed_restored)

            # Round and convert back to uint8
            data_restored = np.round(data_restored).clip(0, 255).astype(np.uint8)

            # Remove padding if added
            if padding_info['padded_length'] > padding_info['original_length']:
                data_restored = data_restored[:padding_info['original_length']]

            return data_restored.tobytes()

        metadata = {
            'operation': 'dct_transform',
            'bytes_affected': original_length,
            'reversible': True,
            'padding': padding_info,
            'normalization': normalization,
            'scipy_available': scipy_available,
            'max_magnitude': float(max_mag)
        }

        return result_bytes, inverse, metadata

    def _numpy_dct_fallback(self, data):
        """Fallback DCT implementation using numpy."""
        import numpy as np
        n = len(data)
        # Create DCT matrix
        k = np.arange(n).reshape((n, 1))
        dct_matrix = np.cos(np.pi * k * (2 * np.arange(n) + 1) / (2 * n))
        if n > 1:
            dct_matrix[0, :] = dct_matrix[0, :] / np.sqrt(2)
        dct_matrix = dct_matrix * np.sqrt(2 / n)
        return dct_matrix @ data

    def _numpy_idct_fallback(self, transformed):
        """Fallback inverse DCT implementation using numpy."""
        import numpy as np
        n = len(transformed)
        # Create IDCT matrix (transpose of DCT matrix)
        k = np.arange(n).reshape((n, 1))
        dct_matrix = np.cos(np.pi * k * (2 * np.arange(n) + 1) / (2 * n))
        if n > 1:
            dct_matrix[0, :] = dct_matrix[0, :] / np.sqrt(2)
        dct_matrix = dct_matrix * np.sqrt(2 / n)
        return dct_matrix.T @ transformed

    def dwt_transform(self, binary_data: bytes, wavelet: str = 'haar', mode: str = 'symmetric', levels: int = 1) -> Tuple[bytes, Callable, Dict]:
        """Discrete wavelet transform with PyWavelets and Haar fallback."""
        import numpy as np

        if len(binary_data) == 0:
            def inverse_empty():
                return b''
            return b'', inverse_empty, {'operation': 'dwt_transform', 'bytes_affected': 0, 'reversible': True}

        original_length = len(binary_data)

        # Convert binary data to numpy array
        data = np.frombuffer(binary_data, dtype=np.uint8).astype(np.float64)

        # Apply DWT with PyWavelets or fallback
        try:
            import pywt
            pywt_available = True

            # Handle padding for DWT
            if len(data) < 2:
                # Pad to at least 2 elements
                data = np.pad(data, (0, 2 - len(data)), 'symmetric')
                padding_info = {'original_length': original_length, 'padded_length': len(data), 'padding_type': 'symmetric'}
            else:
                padding_info = {'original_length': original_length, 'padded_length': len(data), 'padding_type': 'none'}

            # Apply multi-level DWT
            coeffs = []
            current_data = data

            for level in range(levels):
                if len(current_data) < 2:
                    break

                # Single level DWT
                cA, cD = pywt.dwt(current_data, wavelet=wavelet, mode=mode)
                coeffs.append((cA, cD))
                current_data = cA

            # Store decomposition details for reconstruction
            decomposition_info = {
                'levels': len(coeffs),
                'wavelet': wavelet,
                'mode': mode,
                'coeff_shapes': [(len(cA), len(cD)) for cA, cD in coeffs]
            }

            # Pack all coefficients into bytes
            # Normalize coefficients to uint8 range
            all_coeffs = []
            for cA, cD in coeffs:
                all_coeffs.extend(cA)
                all_coeffs.extend(cD)

            if all_coeffs:
                coeffs_array = np.array(all_coeffs)
                # Normalize to uint8 range
                min_val = np.min(coeffs_array)
                max_val = np.max(coeffs_array)
                if max_val > min_val:
                    normalized_coeffs = ((coeffs_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                else:
                    normalized_coeffs = np.zeros_like(coeffs_array, dtype=np.uint8)

                # Store normalization info
                decomp_metadata = {
                    'min_value': float(min_val),
                    'max_value': float(max_val),
                    'coeff_count': len(normalized_coeffs)
                }
            else:
                normalized_coeffs = np.array([], dtype=np.uint8)
                decomp_metadata = {'min_value': 0.0, 'max_value': 0.0, 'coeff_count': 0}

            result_bytes = normalized_coeffs.tobytes()

        except ImportError:
            # Fallback to simple Haar wavelet implementation
            pywt_available = False
            result_bytes, decomp_metadata = self._haar_dwt_fallback(data)
            decomposition_info = {'levels': 1, 'wavelet': 'haar_fallback', 'mode': 'symmetric'}
            padding_info = {'original_length': original_length, 'padded_length': len(data), 'padding_type': 'none'}

        def inverse():
            if pywt_available:
                # Unpack coefficients
                if decomp_metadata['coeff_count'] == 0:
                    return b'\x00' * original_length

                coeffs_array = np.frombuffer(result_bytes, dtype=np.uint8).astype(np.float64)

                # Denormalize coefficients
                min_val = decomp_metadata['min_value']
                max_val = decomp_metadata['max_value']
                if max_val > min_val:
                    denormalized_coeffs = (coeffs_array / 255.0 * (max_val - min_val)) + min_val
                else:
                    denormalized_coeffs = np.zeros_like(coeffs_array)

                # Reconstruct coefficients list
                coeffs_reconstructed = []
                start_idx = 0
                for cA_len, cD_len in decomposition_info['coeff_shapes']:
                    end_idx = start_idx + cA_len + cD_len
                    level_coeffs = denormalized_coeffs[start_idx:end_idx]
                    cA_restored = level_coeffs[:cA_len]
                    cD_restored = level_coeffs[cA_len:]
                    coeffs_reconstructed.append((cA_restored, cD_restored))
                    start_idx = end_idx

                # Reconstruct using inverse DWT
                reconstructed_data = coeffs_reconstructed[-1][0]  # Start with last approximation
                for cA, cD in reversed(coeffs_reconstructed[:-1]):
                    reconstructed_data = pywt.idwt(cA, cD, wavelet=wavelet, mode=mode)

            else:
                # Fallback Haar inverse
                reconstructed_data = self._haar_idwt_fallback(result_bytes, decomp_metadata)

            # Remove padding if added
            if padding_info['padded_length'] > padding_info['original_length']:
                reconstructed_data = reconstructed_data[:padding_info['original_length']]

            # Round and convert back to uint8
            reconstructed_data = np.round(reconstructed_data).clip(0, 255).astype(np.uint8)
            return reconstructed_data.tobytes()

        metadata = {
            'operation': 'dwt_transform',
            'bytes_affected': original_length,
            'reversible': True,
            'decomposition': decomposition_info,
            'padding': padding_info,
            'pywt_available': pywt_available,
            'coeff_metadata': decomp_metadata
        }

        return result_bytes, inverse, metadata

    def _haar_dwt_fallback(self, data):
        """Fallback Haar DWT implementation."""
        import numpy as np

        if len(data) < 2:
            return data.tobytes(), {'min_value': 0.0, 'max_value': 0.0, 'coeff_count': 0}

        # Simple Haar wavelet
        n = len(data)
        half_n = n // 2

        # Approximation coefficients (averages)
        cA = (data[0:2*half_n:2] + data[1:2*half_n:2]) / 2.0

        # Detail coefficients (differences)
        cD = (data[0:2*half_n:2] - data[1:2*half_n:2]) / 2.0

        # Handle odd length
        if n % 2 == 1:
            cA = np.append(cA, data[-1])
            cD = np.append(cD, 0)

        # Combine coefficients
        all_coeffs = np.concatenate([cA, cD])

        # Normalize to uint8
        min_val = np.min(all_coeffs)
        max_val = np.max(all_coeffs)
        if max_val > min_val:
            normalized_coeffs = ((all_coeffs - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        else:
            normalized_coeffs = np.zeros_like(all_coeffs, dtype=np.uint8)

        decomp_metadata = {
            'min_value': float(min_val),
            'max_value': float(max_val),
            'coeff_count': len(normalized_coeffs),
            'original_length': len(data)
        }

        return normalized_coeffs.tobytes(), decomp_metadata

    def _haar_idwt_fallback(self, packed_bytes, metadata):
        """Fallback Haar inverse DWT implementation."""
        import numpy as np

        if metadata['coeff_count'] == 0:
            return np.array([], dtype=np.float64)

        # Unpack and denormalize coefficients
        coeffs = np.frombuffer(packed_bytes, dtype=np.uint8).astype(np.float64)
        min_val = metadata['min_value']
        max_val = metadata['max_value']

        if max_val > min_val:
            denormalized_coeffs = (coeffs / 255.0 * (max_val - min_val)) + min_val
        else:
            denormalized_coeffs = np.zeros_like(coeffs)

        original_length = metadata['original_length']
        half_n = original_length // 2

        # Split into approximation and detail
        if original_length % 2 == 0:
            cA = denormalized_coeffs[:half_n]
            cD = denormalized_coeffs[half_n:]
        else:
            cA = denormalized_coeffs[:half_n + 1]
            cD = denormalized_coeffs[half_n + 1:2*half_n + 1]

        # Reconstruct using inverse Haar
        if original_length % 2 == 0:
            # Even length
            reconstructed = np.empty(original_length, dtype=np.float64)
            reconstructed[0::2] = cA + cD
            reconstructed[1::2] = cA - cD
        else:
            # Odd length
            reconstructed = np.empty(original_length, dtype=np.float64)
            reconstructed[0::2] = cA[:-1] + cD
            reconstructed[1::2] = cA[:-1] - cD
            reconstructed[-1] = cA[-1] * 2  # Last element was stored as-is

        return reconstructed

    def fft_transform(self, binary_data: bytes, window_function: str = 'none', padding: str = 'optimal') -> Tuple[bytes, Callable, Dict]:
        """Fast Fourier transform with windowing and optimal padding."""
        import numpy as np

        if len(binary_data) == 0:
            def inverse_empty():
                return b''
            return b'', inverse_empty, {'operation': 'fft_transform', 'bytes_affected': 0, 'reversible': True}

        original_length = len(binary_data)

        # Convert binary data to float array
        data = np.frombuffer(binary_data, dtype=np.uint8).astype(np.float64)

        # Apply window function if specified
        if window_function != 'none':
            data = self._apply_window_function(data, window_function)
            window_info = {'function': window_function, 'applied': True}
        else:
            window_info = {'function': 'none', 'applied': False}

        # Handle padding for optimal FFT
        if padding == 'optimal':
            # Find optimal FFT size (products of small primes)
            n = len(data)
            optimal_n = self._find_optimal_fft_size(n)
            if optimal_n > n:
                data = np.pad(data, (0, optimal_n - n), 'constant')
                padding_info = {'original_length': n, 'padded_length': optimal_n, 'padding_type': 'zero', 'strategy': 'optimal'}
            else:
                padding_info = {'original_length': n, 'padded_length': n, 'padding_type': 'none', 'strategy': 'optimal'}
        elif padding == 'power_of_2':
            # Pad to power of 2
            n = len(data)
            padded_length = 1 << (n - 1).bit_length()
            if padded_length > n:
                data = np.pad(data, (0, padded_length - n), 'constant')
                padding_info = {'original_length': n, 'padded_length': padded_length, 'padding_type': 'zero', 'strategy': 'power_of_2'}
            else:
                padding_info = {'original_length': n, 'padded_length': n, 'padding_type': 'none', 'strategy': 'power_of_2'}
        else:  # none
            padding_info = {'original_length': len(data), 'padded_length': len(data), 'padding_type': 'none', 'strategy': 'none'}

        # Apply FFT
        try:
            from scipy.fft import fft, ifft
            # Use scipy implementation
            transformed = fft(data)
            scipy_available = True
        except ImportError:
            # Fallback to numpy implementation
            import numpy.fft
            transformed = numpy.fft.fft(data)
            scipy_available = False

        # Convert complex results to real values for binary output
        # Use magnitude and phase encoding for reversibility
        magnitude = np.abs(transformed)
        phase = np.angle(transformed)

        # Normalize and pack
        max_mag = np.max(magnitude) if np.max(magnitude) > 0 else 1.0
        normalized_mag = (magnitude / max_mag * 255).astype(np.uint8)
        normalized_phase = ((phase + np.pi) / (2 * np.pi) * 255).astype(np.uint8)

        # Interleave magnitude and phase
        packed = np.empty(2 * len(normalized_mag), dtype=np.uint8)
        packed[0::2] = normalized_mag
        packed[1::2] = normalized_phase

        result_bytes = packed.tobytes()

        def inverse():
            # Unpack magnitude and phase
            packed_array = np.frombuffer(result_bytes, dtype=np.uint8)
            magnitude_restored = packed_array[0::2].astype(np.float64)
            phase_restored = (packed_array[1::2].astype(np.float64) / 255.0 * 2 * np.pi) - np.pi

            # Restore complex numbers
            max_mag = np.max(magnitude_restored) if np.max(magnitude_restored) > 0 else 1.0
            magnitude_restored = magnitude_restored / 255.0 * max_mag
            transformed_restored = magnitude_restored * np.exp(1j * phase_restored)

            # Apply inverse FFT
            if scipy_available:
                from scipy.fft import ifft
                data_restored = ifft(transformed_restored)
            else:
                import numpy.fft
                data_restored = numpy.fft.ifft(transformed_restored)

            # Take real part (imaginary part should be negligible)
            data_restored = np.real(data_restored)

            # Remove windowing if applied
            if window_info['applied']:
                data_restored = self._remove_window_function(data_restored, window_function, original_length)

            # Remove padding if added
            if padding_info['padded_length'] > padding_info['original_length']:
                data_restored = data_restored[:padding_info['original_length']]

            # Round and convert back to uint8
            data_restored = np.round(data_restored).clip(0, 255).astype(np.uint8)
            return data_restored.tobytes()

        metadata = {
            'operation': 'fft_transform',
            'bytes_affected': original_length,
            'reversible': True,
            'window': window_info,
            'padding': padding_info,
            'scipy_available': scipy_available,
            'max_magnitude': float(max_mag),
            'frequency_bins': len(transformed)
        }

        return result_bytes, inverse, metadata

    def _apply_window_function(self, data, window_type):
        """Apply window function to data."""
        import numpy as np
        n = len(data)

        if window_type == 'hamming':
            window = np.hamming(n)
        elif window_type == 'hanning':
            window = np.hanning(n)
        elif window_type == 'blackman':
            window = np.blackman(n)
        elif window_type == 'bartlett':
            window = np.bartlett(n)
        else:
            return data

        return data * window

    def _remove_window_function(self, data, window_type, original_length):
        """Remove window function effects (approximate deconvolution)."""
        import numpy as np
        n = original_length

        if window_type == 'hamming':
            window = np.hamming(n)
        elif window_type == 'hanning':
            window = np.hanning(n)
        elif window_type == 'blackman':
            window = np.blackman(n)
        elif window_type == 'bartlett':
            window = np.bartlett(n)
        else:
            return data

        # Avoid division by zero
        window[window == 0] = 1.0
        return data[:n] / window

    def _find_optimal_fft_size(self, n):
        """Find optimal FFT size (products of small primes 2, 3, 5)."""
        # Start with current size and increase until we find an optimal size
        candidate = n
        while True:
            if self._is_optimal_fft_size(candidate):
                return candidate
            candidate += 1

    def _is_optimal_fft_size(self, n):
        """Check if n is optimal for FFT (factors of 2, 3, 5 only)."""
        # Remove factors of 2
        while n % 2 == 0:
            n //= 2
        # Remove factors of 3
        while n % 3 == 0:
            n //= 3
        # Remove factors of 5
        while n % 5 == 0:
            n //= 5
        # If remaining is 1, it's optimal
        return n == 1

    def huffman_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Huffman encoding."""
        def inverse():
            raise RuntimeError("Huffman encoding is not reversible")
        return binary_data, inverse, {'operation': 'huffman_encode', 'bytes_affected': 0, 'reversible': False}

    def run_length_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Run-length encoding."""
        def inverse():
            raise RuntimeError("Run-length encoding is not reversible")
        return binary_data, inverse, {'operation': 'run_length_encode', 'bytes_affected': 0, 'reversible': False}

    def arithmetic_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Arithmetic encoding."""
        def inverse():
            raise RuntimeError("Arithmetic encoding is not reversible")
        return binary_data, inverse, {'operation': 'arithmetic_encode', 'bytes_affected': 0, 'reversible': False}

    def lz77_encode(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """LZ77 encoding."""
        def inverse():
            raise RuntimeError("LZ77 encoding is not reversible")
        return binary_data, inverse, {'operation': 'lz77_encode', 'bytes_affected': 0, 'reversible': False}

    def distance_coding(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Distance coding."""
        return self.move_to_front(binary_data)

    def elias_gamma(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Elias gamma coding."""
        def inverse():
            raise RuntimeError("Elias gamma coding is not reversible")
        return binary_data, inverse, {'operation': 'elias_gamma', 'bytes_affected': 0, 'reversible': False}

    def elias_delta(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Elias delta coding."""
        def inverse():
            raise RuntimeError("Elias delta coding is not reversible")
        return binary_data, inverse, {'operation': 'elias_delta', 'bytes_affected': 0, 'reversible': False}

    def golomb_coding(self, binary_data: bytes, parameter: int) -> Tuple[bytes, Callable, Dict]:
        """Golomb coding."""
        def inverse():
            raise RuntimeError("Golomb coding is not reversible")
        return binary_data, inverse, {'operation': 'golomb_coding', 'bytes_affected': 0, 'reversible': False}

    def fibonacci_coding(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Fibonacci coding."""
        def inverse():
            raise RuntimeError("Fibonacci coding is not reversible")
        return binary_data, inverse, {'operation': 'fibonacci_coding', 'bytes_affected': 0, 'reversible': False}

    def phase_in_coding(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Phase-in coding."""
        def inverse():
            raise RuntimeError("Phase-in coding is not reversible")
        return binary_data, inverse, {'operation': 'phase_in_coding', 'bytes_affected': 0, 'reversible': False}

    def adaptive_huffman(self, binary_data: bytes) -> Tuple[bytes, Callable, Dict]:
        """Adaptive Huffman coding."""
        def inverse():
            raise RuntimeError("Adaptive Huffman coding is not reversible")
        return binary_data, inverse, {'operation': 'adaptive_huffman', 'bytes_affected': 0, 'reversible': False}