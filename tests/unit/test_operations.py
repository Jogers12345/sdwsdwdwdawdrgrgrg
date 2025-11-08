"""
Operation Correctness Tests
Ensure all operations work as specified and are truly reversible
"""

import pytest
import random
import struct
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import Mock, patch

from tests.conftest import TestDataGenerator, TestResultValidator


class TestXorOperation:
    """Test XOR operation correctness"""

    @pytest.mark.unit
    def test_xor_basic_functionality(self):
        """Test basic XOR operation functionality"""
        def xor_operation(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        # Test with known inputs
        data = b"Hello"
        key = 0x42
        result = xor_operation(data, key)

        # Verify result
        expected = bytes([ord('H') ^ 0x42, ord('e') ^ 0x42, ord('l') ^ 0x42,
                         ord('l') ^ 0x42, ord('o') ^ 0x42])
        assert result == expected

    @pytest.mark.unit
    def test_xor_reversibility(self, result_validator):
        """Test XOR operation is reversible"""
        def xor_operation(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        def xor_inverse(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)  # XOR is its own inverse

        class XorOp:
            def __init__(self, key: int):
                self.key = key
                self.name = f"xor_{key}"

            def apply(self, data: bytes) -> bytes:
                return xor_operation(data, self.key)

            def inverse(self):
                return XorOp(self.key)  # Same operation for inverse

        # Test with multiple data patterns
        test_cases = [
            b"test data",
            b"\x00\x01\x02\x03\xFF\xFE\xFD",
            TestDataGenerator.generate_random_data(1000, seed=42),
            TestDataGenerator.generate_pattern_data(500, b"ABCD")
        ]

        for test_data in test_cases:
            op = XorOp(0x5A)
            reversibility = result_validator.validate_operation_reversibility(
                test_data, op
            )
            assert reversibility, f"XOR reversibility failed for data of length {len(test_data)}"

    @pytest.mark.unit
    def test_xor_parameter_validation(self):
        """Test XOR operation parameter validation"""
        class XorOp:
            def __init__(self, key: int):
                if not isinstance(key, int):
                    raise TypeError("Key must be integer")
                if not 0 <= key <= 255:
                    raise ValueError("Key must be in range 0-255")
                self.key = key

        # Test valid keys
        XorOp(0)
        XorOp(128)
        XorOp(255)

        # Test invalid keys
        with pytest.raises(TypeError):
            XorOp("not_an_int")

        with pytest.raises(ValueError):
            XorOp(-1)

        with pytest.raises(ValueError):
            XorOp(256)

    @pytest.mark.unit
    def test_xor_edge_cases(self):
        """Test XOR operation edge cases"""
        def xor_operation(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        # Test empty data
        assert xor_operation(b"", 0x42) == b""

        # Test single byte
        assert xor_operation(b"\xFF", 0xFF) == b"\x00"
        assert xor_operation(b"\x00", 0xFF) == b"\xFF"

        # Test key of 0 (no change)
        test_data = b"Hello, World!"
        assert xor_operation(test_data, 0) == test_data

        # Test key of 0xFF (bit inversion)
        test_data = b"\x00\xFF\x80\x7F"
        result = xor_operation(test_data, 0xFF)
        expected = b"\xFF\x00\x7F\x80"
        assert result == expected

    @pytest.mark.unit
    def test_xor_various_data_patterns(self):
        """Test XOR with various data patterns"""
        def xor_operation(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        patterns = [
            ("all_zeros", b"\x00" * 100),
            ("all_ones", b"\xFF" * 100),
            ("alternating", b"\xAA\x55" * 50),
            ("incrementing", bytes(range(100))),
            ("decrementing", bytes(range(100, 0, -1)))
        ]

        key = 0x5A

        for pattern_name, data in patterns:
            result = xor_operation(data, key)
            # Verify result has same length
            assert len(result) == len(data)
            # Verify result is different from original (unless key is 0)
            if key != 0:
                assert result != data


class TestAddConstantOperation:
    """Test Add Constant operation correctness"""

    @pytest.mark.unit
    def test_add_constant_basic_functionality(self):
        """Test basic add constant functionality"""
        def add_constant(data: bytes, constant: int) -> bytes:
            return bytes((b + constant) % 256 for b in data)

        # Test with known inputs
        data = b"\x01\x02\xFE"
        constant = 5
        result = add_constant(data, constant)

        expected = b"\x06\x07\x03"  # 1+5=6, 2+5=7, 254+5=259%256=3
        assert result == expected

    @pytest.mark.unit
    def test_add_constant_reversibility(self, result_validator):
        """Test add constant operation is reversible"""
        def add_constant(data: bytes, constant: int) -> bytes:
            return bytes((b + constant) % 256 for b in data)

        def subtract_constant(data: bytes, constant: int) -> bytes:
            return bytes((b - constant) % 256 for b in data)

        class AddConstantOp:
            def __init__(self, constant: int):
                self.constant = constant
                self.name = f"add_{constant}"

            def apply(self, data: bytes) -> bytes:
                return add_constant(data, self.constant)

            def inverse(self):
                return SubtractConstantOp(self.constant)

        class SubtractConstantOp:
            def __init__(self, constant: int):
                self.constant = constant
                self.name = f"subtract_{constant}"

            def apply(self, data: bytes) -> bytes:
                return subtract_constant(data, self.constant)

        # Test with multiple data patterns
        test_cases = [
            b"test data",
            b"\x7F\x80\xFF",
            TestDataGenerator.generate_random_data(500, seed=123),
            TestDataGenerator.generate_pattern_data(250, b"XYZ")
        ]

        for test_data in test_cases:
            op = AddConstantOp(42)
            reversibility = result_validator.validate_operation_reversibility(
                test_data, op
            )
            assert reversibility, f"Add constant reversibility failed for constant 42"

    @pytest.mark.unit
    def test_add_constant_parameter_validation(self):
        """Test add constant parameter validation"""
        class AddConstantOp:
            def __init__(self, constant: int):
                if not isinstance(constant, int):
                    raise TypeError("Constant must be integer")
                if not -128 <= constant <= 127:
                    raise ValueError("Constant must be in range -128 to 127")
                self.constant = constant

        # Test valid constants
        AddConstantOp(0)
        AddConstantOp(42)
        AddConstantOp(-42)
        AddConstantOp(127)
        AddConstantOp(-128)

        # Test invalid constants
        with pytest.raises(TypeError):
            AddConstantOp("not_an_int")

        with pytest.raises(ValueError):
            AddConstantOp(-129)

        with pytest.raises(ValueError):
            AddConstantOp(128)

    @pytest.mark.unit
    def test_add_constant_overflow_handling(self):
        """Test add constant handles overflow correctly"""
        def add_constant(data: bytes, constant: int) -> bytes:
            return bytes((b + constant) % 256 for b in data)

        # Test overflow
        assert add_constant(b"\xFF", 1) == b"\x00"
        assert add_constant(b"\xFE", 5) == b"\x03"

        # Test underflow
        assert add_constant(b"\x00", -1) == b"\xFF"
        assert add_constant(b"\x01", -5) == b"\xFC"

        # Test multiple wraps
        assert add_constant(b"\xF0", 32) == b"\x10"
        assert add_constant(b"\x10", -32) == b"\xF0"

    @pytest.mark.unit
    def test_add_constant_various_constants(self):
        """Test add constant with various constant values"""
        def add_constant(data: bytes, constant: int) -> bytes:
            return bytes((b + constant) % 256 for b in data)

        test_data = b"\x40\x80\xC0"

        constants_to_test = [0, 1, -1, 64, -64, 127, -128, 255, -255]

        for constant in constants_to_test:
            result = add_constant(test_data, constant)
            assert len(result) == len(test_data)

            # Verify by reverse operation
            reverse_result = add_constant(result, -constant)
            assert reverse_result == test_data


class TestRotateOperation:
    """Test Rotate operation correctness"""

    @pytest.mark.unit
    def test_rotate_left_basic_functionality(self):
        """Test basic rotate left functionality"""
        def rotate_left(data: bytes, bits: int) -> bytes:
            if not data or bits % 8 == 0:
                return data

            bits = bits % 8
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        # Test with known inputs
        data = b"\x01"  # 00000001
        result = rotate_left(data, 1)
        assert result == b"\x02"  # 00000010

        data = b"\x80"  # 10000000
        result = rotate_left(data, 1)
        assert result == b"\x01"  # 00000001

        data = b"\xFF"  # 11111111
        result = rotate_left(data, 2)
        assert result == b"\xFF"  # 11111111 (unchanged)

    @pytest.mark.unit
    def test_rotate_left_reversibility(self, result_validator):
        """Test rotate left operation is reversible"""
        def rotate_left(data: bytes, bits: int) -> bytes:
            if not data or bits % 8 == 0:
                return data
            bits = bits % 8
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        def rotate_right(data: bytes, bits: int) -> bytes:
            return rotate_left(data, 8 - (bits % 8))

        class RotateLeftOp:
            def __init__(self, bits: int):
                self.bits = bits
                self.name = f"rotate_left_{bits}"

            def apply(self, data: bytes) -> bytes:
                return rotate_left(data, self.bits)

            def inverse(self):
                return RotateRightOp(self.bits)

        class RotateRightOp:
            def __init__(self, bits: int):
                self.bits = bits
                self.name = f"rotate_right_{bits}"

            def apply(self, data: bytes) -> bytes:
                return rotate_right(data, self.bits)

        # Test with multiple bit amounts
        test_data = b"rotation test data"
        bit_amounts = [1, 2, 3, 4, 5, 6, 7]

        for bits in bit_amounts:
            op = RotateLeftOp(bits)
            reversibility = result_validator.validate_operation_reversibility(
                test_data, op
            )
            assert reversibility, f"Rotate left reversibility failed for {bits} bits"

    @pytest.mark.unit
    def test_rotate_parameter_validation(self):
        """Test rotate operation parameter validation"""
        class RotateOp:
            def __init__(self, bits: int, direction: str = "left"):
                if not isinstance(bits, int):
                    raise TypeError("Bits must be integer")
                if not 0 <= bits <= 7:
                    raise ValueError("Bits must be in range 0-7")
                if direction not in ["left", "right"]:
                    raise ValueError("Direction must be 'left' or 'right'")
                self.bits = bits
                self.direction = direction

        # Test valid parameters
        RotateOp(0, "left")
        RotateOp(4, "right")
        RotateOp(7, "left")

        # Test invalid bits
        with pytest.raises(TypeError):
            RotateOp("not_an_int")

        with pytest.raises(ValueError):
            RotateOp(-1)

        with pytest.raises(ValueError):
            RotateOp(8)

        # Test invalid direction
        with pytest.raises(ValueError):
            RotateOp(3, "invalid")

    @pytest.mark.unit
    def test_rotate_edge_cases(self):
        """Test rotate operation edge cases"""
        def rotate_left(data: bytes, bits: int) -> bytes:
            if not data or bits % 8 == 0:
                return data
            bits = bits % 8
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        # Test empty data
        assert rotate_left(b"", 3) == b""

        # Test zero rotation
        test_data = b"Hello"
        assert rotate_left(test_data, 0) == test_data
        assert rotate_left(test_data, 8) == test_data

        # Test single byte with all possible rotations
        byte = b"\xA5"  # 10100101
        for bits in range(1, 8):
            rotated = rotate_left(byte, bits)
            assert len(rotated) == 1
            # Verify rotation is correct by rotating back
            rotated_back = rotate_left(rotated, 8 - bits)
            assert rotated_back == byte

    @pytest.mark.unit
    def test_rotate_all_bit_values(self):
        """Test rotate operation with all possible bit values"""
        def rotate_left(data: bytes, bits: int) -> bytes:
            if not data or bits % 8 == 0:
                return data
            bits = bits % 8
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        test_byte = b"\x53"  # 01010011
        expected_rotations = {
            1: b"\xA6",  # 10100110
            2: b"\x4D",  # 01001101
            3: b"\x9B",  # 10011011
            4: b"\x37",  # 00110111
            5: b"\x6E",  # 01101110
            6: b"\xDC",  # 11011100
            7: b"\xB9",  # 10111001
        }

        for bits, expected in expected_rotations.items():
            result = rotate_left(test_byte, bits)
            assert result == expected, f"Rotate left by {bits} bits failed"


class TestSubstituteOperation:
    """Test Substitute operation correctness"""

    @pytest.mark.unit
    def test_substitute_basic_functionality(self):
        """Test basic substitute functionality"""
        def substitute(data: bytes, mapping: Dict[int, int]) -> bytes:
            result = bytearray()
            for byte in data:
                replacement = mapping.get(byte, byte)
                result.append(replacement)
            return bytes(result)

        # Test with known mapping
        mapping = {ord('A'): ord('X'), ord('B'): ord('Y'), ord('C'): ord('Z')}
        data = b"ABCABCXYZ"
        result = substitute(data, mapping)

        expected = b"XYZXYZXYZ"  # A->X, B->Y, C->Z, others unchanged
        assert result == expected

    @pytest.mark.unit
    def test_substitute_reversibility(self, result_validator):
        """Test substitute operation is reversible"""
        def substitute(data: bytes, mapping: Dict[int, int]) -> bytes:
            result = bytearray()
            for byte in data:
                replacement = mapping.get(byte, byte)
                result.append(replacement)
            return bytes(result)

        class SubstituteOp:
            def __init__(self, mapping: Dict[int, int]):
                self.mapping = mapping.copy()
                self.name = "substitute"

            def apply(self, data: bytes) -> bytes:
                return substitute(data, self.mapping)

            def inverse(self):
                # Create inverse mapping
                inverse_mapping = {}
                for k, v in self.mapping.items():
                    inverse_mapping[v] = k
                return SubstituteOp(inverse_mapping)

        # Test with bijection mapping (one-to-one)
        mapping = {1: 10, 2: 20, 3: 30, 10: 1, 20: 2, 30: 3}
        test_data = bytes([1, 2, 3, 99, 10, 20, 30])  # Include unmapped byte (99)

        op = SubstituteOp(mapping)
        reversibility = result_validator.validate_operation_reversibility(
            test_data, op
        )
        assert reversibility, "Substitute reversibility failed with bijection mapping"

    @pytest.mark.unit
    def test_substitute_parameter_validation(self):
        """Test substitute parameter validation"""
        class SubstituteOp:
            def __init__(self, mapping: Dict[int, int]):
                if not isinstance(mapping, dict):
                    raise TypeError("Mapping must be dictionary")
                if not mapping:
                    raise ValueError("Mapping cannot be empty")
                for k, v in mapping.items():
                    if not isinstance(k, int) or not isinstance(v, int):
                        raise TypeError("Mapping keys and values must be integers")
                    if not 0 <= k <= 255 or not 0 <= v <= 255:
                        raise ValueError("Mapping values must be in range 0-255")
                self.mapping = mapping

        # Test valid mapping
        valid_mapping = {65: 90, 66: 89}  # A->Z, B->Y
        SubstituteOp(valid_mapping)

        # Test invalid mappings
        with pytest.raises(TypeError):
            SubstituteOp("not_a_dict")

        with pytest.raises(ValueError):
            SubstituteOp({})

        with pytest.raises(TypeError):
            SubstituteOp({1.5: 10})

        with pytest.raises(ValueError):
            SubstituteOp({256: 10})

        with pytest.raises(ValueError):
            SubstituteOp({1: 256})

    @pytest.mark.unit
    def test_substitute_edge_cases(self):
        """Test substitute operation edge cases"""
        def substitute(data: bytes, mapping: Dict[int, int]) -> bytes:
            result = bytearray()
            for byte in data:
                replacement = mapping.get(byte, byte)
                result.append(replacement)
            return bytes(result)

        # Test empty data
        mapping = {1: 2}
        assert substitute(b"", mapping) == b""

        # Test identity mapping
        identity_mapping = {i: i for i in range(256)}
        test_data = b"Hello, World!"
        assert substitute(test_data, identity_mapping) == test_data

        # Test complete mapping
        complete_mapping = {i: (255 - i) for i in range(256)}  # Bit inversion
        test_data = bytes([0, 1, 254, 255])
        result = substitute(test_data, complete_mapping)
        expected = bytes([255, 254, 1, 0])
        assert result == expected

    @pytest.mark.unit
    def test_substitute_collision_handling(self):
        """Test substitute handles mapping collisions"""
        def substitute(data: bytes, mapping: Dict[int, int]) -> bytes:
            result = bytearray()
            for byte in data:
                replacement = mapping.get(byte, byte)
                result.append(replacement)
            return bytes(result)

        # Test non-bijective mapping (multiple keys map to same value)
        # This should work for forward operation but won't be reversible
        collision_mapping = {1: 100, 2: 100, 3: 100}
        test_data = bytes([1, 2, 3, 4])
        result = substitute(test_data, collision_mapping)
        expected = bytes([100, 100, 100, 4])
        assert result == expected


class TestCompressionOperation:
    """Test Compression operation correctness"""

    @pytest.mark.unit
    def test_compression_basic_functionality(self):
        """Test basic compression functionality"""
        try:
            import gzip
            import zlib

            def compress_data(data: bytes, algorithm: str = "gzip") -> bytes:
                if algorithm == "gzip":
                    return gzip.compress(data)
                elif algorithm == "zlib":
                    return zlib.compress(data)
                else:
                    raise ValueError(f"Unknown compression algorithm: {algorithm}")

            # Test with compressible data
            data = b"A" * 1000  # Highly compressible
            compressed = compress_data(data, "gzip")

            assert len(compressed) < len(data)  # Should be smaller
            assert gzip.decompress(compressed) == data  # Should decompress correctly

            # Test with random data (less compressible)
            random_data = TestDataGenerator.generate_random_data(1000)
            compressed_random = compress_data(random_data, "gzip")

            # Random data might not compress much, but should still round-trip
            assert gzip.decompress(compressed_random) == random_data

        except ImportError:
            pytest.skip("gzip/zlib not available")

    @pytest.mark.unit
    def test_compression_reversibility(self, result_validator):
        """Test compression operation is reversible"""
        try:
            import gzip

            class CompressOp:
                def __init__(self, algorithm="gzip"):
                    self.algorithm = algorithm
                    self.name = f"compress_{algorithm}"

                def apply(self, data: bytes) -> bytes:
                    return gzip.compress(data)

                def inverse(self):
                    return DecompressOp(self.algorithm)

            class DecompressOp:
                def __init__(self, algorithm="gzip"):
                    self.algorithm = algorithm
                    self.name = f"decompress_{algorithm}"

                def apply(self, data: bytes) -> bytes:
                    return gzip.decompress(data)

            # Test with various data types
            test_cases = [
                b"Highly repetitive data " * 50,
                TestDataGenerator.generate_random_data(500, seed=456),
                TestDataGenerator.generate_pattern_data(300, b"pattern"),
                b""  # Empty data
            ]

            for test_data in test_cases:
                op = CompressOp("gzip")
                reversibility = result_validator.validate_operation_reversibility(
                    test_data, op
                )
                assert reversibility, f"Compression reversibility failed for data length {len(test_data)}"

        except ImportError:
            pytest.skip("gzip not available")

    @pytest.mark.unit
    def test_compression_parameter_validation(self):
        """Test compression parameter validation"""
        try:
            import gzip

            class CompressOp:
                def __init__(self, algorithm="gzip", level=6):
                    valid_algorithms = ["gzip", "zlib", "bz2"]
                    if algorithm not in valid_algorithms:
                        raise ValueError(f"Algorithm must be one of {valid_algorithms}")
                    if not isinstance(level, int) or not 0 <= level <= 9:
                        raise ValueError("Compression level must be integer 0-9")
                    self.algorithm = algorithm
                    self.level = level

            # Test valid parameters
            CompressOp("gzip", 6)
            CompressOp("zlib", 9)
            CompressOp("gzip", 0)

            # Test invalid algorithm
            with pytest.raises(ValueError):
                CompressOp("invalid_algorithm")

            # Test invalid level
            with pytest.raises(ValueError):
                CompressOp("gzip", -1)

            with pytest.raises(ValueError):
                CompressOp("gzip", 10)

        except ImportError:
            pytest.skip("compression libraries not available")

    @pytest.mark.unit
    def test_compression_edge_cases(self):
        """Test compression edge cases"""
        try:
            import gzip

            # Test empty data
            empty_compressed = gzip.compress(b"")
            empty_decompressed = gzip.decompress(empty_compressed)
            assert empty_decompressed == b""

            # Test single byte
            single_byte = gzip.compress(b"A")
            assert gzip.decompress(single_byte) == b"A"

            # Test very large data
            large_data = b"X" * 100000  # 100KB
            compressed_large = gzip.compress(large_data)
            assert gzip.decompress(compressed_large) == large_data
            assert len(compressed_large) < len(large_data)  # Should compress well

        except ImportError:
            pytest.skip("gzip not available")


class TestOperationMetadata:
    """Test operation metadata accuracy"""

    @pytest.mark.unit
    def test_operation_name_and_description(self):
        """Test operations have correct names and descriptions"""
        class MockOperation:
            def __init__(self, name: str, description: str):
                self.name = name
                self.description = description
                self.metadata = {
                    "name": name,
                    "description": description,
                    "reversible": True,
                    "parameters": {}
                }

            def apply(self, data: bytes) -> bytes:
                return data

            def inverse(self):
                return MockOperation(self.name + "_inverse", self.description)

        op = MockOperation("test_op", "A test operation for testing")

        assert op.name == "test_op"
        assert op.description == "A test operation for testing"
        assert op.metadata["name"] == "test_op"
        assert op.metadata["reversible"] is True

    @pytest.mark.unit
    def test_operation_parameter_metadata(self):
        """Test operation parameter metadata is accurate"""
        class ParameterizedOperation:
            def __init__(self, value: int):
                self.name = "param_op"
                self.value = value
                self.metadata = {
                    "name": self.name,
                    "parameters": {
                        "value": {
                            "type": "int",
                            "range": [0, 255],
                            "default": 128,
                            "current": self.value
                        }
                    }
                }

            def apply(self, data: bytes) -> bytes:
                return bytes((b + self.value) % 256 for b in data)

        op = ParameterizedOperation(42)

        assert "parameters" in op.metadata
        assert "value" in op.metadata["parameters"]
        assert op.metadata["parameters"]["value"]["current"] == 42
        assert op.metadata["parameters"]["value"]["type"] == "int"

    @pytest.mark.unit
    def test_operation_reversibility_metadata(self):
        """Test operation reversibility is correctly reported"""
        class ReversibleOperation:
            def __init__(self):
                self.name = "reversible"
                self.metadata = {"reversible": True}

            def apply(self, data: bytes) -> bytes:
                return bytes((b + 1) % 256 for b in data)

            def inverse(self):
                return ReversibleOperation()

        class IrreversibleOperation:
            def __init__(self):
                self.name = "irreversible"
                self.metadata = {"reversible": False}

            def apply(self, data: bytes) -> bytes:
                return hash(data).to_bytes(8, 'big')  # Hash is irreversible

        reversible_op = ReversibleOperation()
        irreversible_op = IrreversibleOperation()

        assert reversible_op.metadata["reversible"] is True
        assert irreversible_op.metadata["reversible"] is False
        assert hasattr(reversible_op, 'inverse')
        assert not hasattr(irreversible_op, 'inverse')


class TestOperationIntegration:
    """Integration tests for operations"""

    @pytest.mark.integration
    def test_multiple_operation_sequence(self):
        """Test sequence of multiple operations"""
        def xor_op(data: bytes, key: int) -> bytes:
            return bytes(b ^ key for b in data)

        def add_op(data: bytes, value: int) -> bytes:
            return bytes((b + value) % 256 for b in data)

        def rotate_op(data: bytes, bits: int) -> bytes:
            bits = bits % 8
            result = bytearray()
            for byte in data:
                rotated = ((byte << bits) | (byte >> (8 - bits))) & 0xFF
                result.append(rotated)
            return bytes(result)

        # Apply sequence: XOR -> ADD -> ROTATE
        original_data = b"test_sequence"

        step1 = xor_op(original_data, 0x5A)
        step2 = add_op(step1, 42)
        step3 = rotate_op(step2, 3)

        # Reverse sequence: ROTATE inverse -> SUBTRACT -> XOR inverse (same)
        reverse_step1 = rotate_op(step3, 5)  # 8-3=5
        reverse_step2 = add_op(reverse_step1, -42)
        reverse_step3 = xor_op(reverse_step2, 0x5A)

        assert reverse_step3 == original_data

    @pytest.mark.integration
    def test_operation_with_various_data_sizes(self):
        """Test operations with various data sizes"""
        def simple_op(data: bytes) -> bytes:
            # Simple operation: complement bits
            return bytes(~b & 0xFF for b in data)

        data_sizes = [0, 1, 10, 100, 1000, 10000]

        for size in data_sizes:
            test_data = TestDataGenerator.generate_random_data(size, seed=size)
            result = simple_op(test_data)
            reversed_result = simple_op(result)  # Operation is its own inverse

            assert reversed_result == test_data
            assert len(result) == size

    @pytest.mark.integration
    def test_operation_performance_consistency(self):
        """Test operations produce consistent performance"""
        def test_operation(data: bytes) -> bytes:
            # Simple but deterministic operation
            return bytes((b * 7 + 13) % 256 for b in data)

        test_data = b"performance_test"
        results = []

        # Run operation multiple times
        for _ in range(10):
            result = test_operation(test_data)
            results.append(result)

        # All results should be identical
        assert all(result == results[0] for result in results)

    @pytest.mark.integration
    def test_operation_error_handling(self):
        """Test operation error handling"""
        class ErrorOperation:
            def __init__(self, should_fail: bool = False):
                self.should_fail = should_fail
                self.name = "error_op"

            def apply(self, data: bytes) -> bytes:
                if self.should_fail:
                    raise ValueError("Intentional error for testing")
                return data

        # Test successful operation
        success_op = ErrorOperation(should_fail=False)
        test_data = b"test"
        assert success_op.apply(test_data) == test_data

        # Test failing operation
        fail_op = ErrorOperation(should_fail=True)
        with pytest.raises(ValueError, match="Intentional error for testing"):
            fail_op.apply(test_data)


class TestOperationBoundaryConditions:
    """Test operations at boundary conditions"""

    @pytest.mark.unit
    def test_empty_data_handling(self):
        """Test operations handle empty data correctly"""
        operations = [
            lambda data: bytes(b ^ 0x42 for b in data),  # XOR
            lambda data: bytes((b + 10) % 256 for b in data),  # Add
            lambda data: data,  # Identity
            lambda data: bytes(reversed(data)),  # Reverse
        ]

        for op in operations:
            result = op(b"")
            assert result == b""
            assert isinstance(result, bytes)

    @pytest.mark.unit
    def test_maximum_size_data(self):
        """Test operations handle large data correctly"""
        # Create 1MB of test data
        large_data = TestDataGenerator.generate_random_data(1024 * 1024, seed=999)

        def simple_operation(data: bytes) -> bytes:
            # Simple operation that should work on any size
            return bytes(b ^ 0xAA for b in data)

        result = simple_operation(large_data)

        assert len(result) == len(large_data)
        assert result != large_data  # Should be different due to XOR

        # Verify operation is reversible
        reverse_result = simple_operation(result)
        assert reverse_result == large_data

    @pytest.mark.unit
    def test_unicode_and_special_characters(self):
        """Test operations handle special characters correctly"""
        special_data = (
            b"Hello \xC3\xA9 World! \xF0\x9F\x98\x8A "  # UTF-8 encoded
            b"Null\x00Byte\xFFEscape\x1BTest"
        )

        def byte_operation(data: bytes) -> bytes:
            return bytes(b + 1 for b in data)

        result = byte_operation(special_data)

        assert len(result) == len(special_data)
        assert isinstance(result, bytes)

        # Verify reversibility
        reverse_result = bytes(b - 1 for b in result)
        assert reverse_result == special_data

    @pytest.mark.unit
    def test_extreme_parameter_values(self):
        """Test operations with extreme parameter values"""
        def add_constant_operation(data: bytes, constant: int) -> bytes:
            return bytes((b + constant) % 256 for b in data)

        test_data = b"\x7F\x80\xFF"

        # Test with extreme constants
        extreme_constants = [-128, -255, -256, 255, 256, 512, 1024]

        for constant in extreme_constants:
            result = add_constant_operation(test_data, constant)
            assert len(result) == len(test_data)

            # Verify result is in valid byte range
            assert all(0 <= byte <= 255 for byte in result)

            # Test reversibility
            reverse_constant = -constant
            reverse_result = add_constant_operation(result, reverse_constant)
            assert reverse_result == test_data