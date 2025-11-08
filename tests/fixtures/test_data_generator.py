"""
Test Data Management System for BSEE
Provides standardized test data generation and management
"""

import os
import random
import struct
import hashlib
import gzip
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, BinaryIO
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import shutil


class DataType(Enum):
    """Test data types"""
    RANDOM = "random"
    STRUCTURED = "structured"
    PATTERNED = "patterned"
    COMPRESSED = "compressed"
    ENCRYPTED = "encrypted"
    MALFORMED = "malformed"


class FileSize(Enum):
    """Standard test file sizes"""
    TINY = 64           # 64 bytes
    SMALL = 1024        # 1 KB
    MEDIUM = 65536      # 64 KB
    LARGE = 1048576     # 1 MB
    HUGE = 10485760     # 10 MB


@dataclass
class TestDataMetadata:
    """Metadata for test data"""
    filename: str
    data_type: DataType
    size: int
    seed: Optional[int]
    description: str
    created_at: str
    checksum: str
    properties: Dict[str, Any]


@dataclass
class ExpectedResult:
    """Expected analysis result for test data"""
    filename: str
    expected_patterns: List[str]
    expected_entropy_range: Tuple[float, float]
    expected_structure_hints: List[str]
    analysis_difficulty: str  # easy, medium, hard
    strategy_rankings: Dict[str, int]


class TestDataGenerator:
    """Generates standardized test data for BSEE testing"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.test_files_dir = self.base_dir / "test_files"
        self.metadata_file = self.base_dir / "metadata.json"
        self.expected_results_file = self.base_dir / "expected_results.json"

        # Ensure directories exist
        self.test_files_dir.mkdir(exist_ok=True, parents=True)

        # Load existing metadata
        self.metadata = self._load_metadata()
        self.expected_results = self._load_expected_results()

    def _load_metadata(self) -> Dict[str, TestDataMetadata]:
        """Load test data metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                return {
                    filename: TestDataMetadata(**metadata)
                    for filename, metadata in data.items()
                }
            except Exception as e:
                print(f"Warning: Failed to load metadata: {e}")
        return {}

    def _load_expected_results(self) -> Dict[str, ExpectedResult]:
        """Load expected analysis results"""
        if self.expected_results_file.exists():
            try:
                with open(self.expected_results_file, 'r') as f:
                    data = json.load(f)
                return {
                    filename: ExpectedResult(**result)
                    for filename, result in data.items()
                }
            except Exception as e:
                print(f"Warning: Failed to load expected results: {e}")
        return {}

    def _save_metadata(self):
        """Save test data metadata"""
        try:
            def metadata_to_dict(metadata):
                """Convert metadata to JSON-serializable dict"""
                data = asdict(metadata)
                data['data_type'] = metadata.data_type.value
                return data

            data = {
                filename: metadata_to_dict(metadata)
                for filename, metadata in self.metadata.items()
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _save_expected_results(self):
        """Save expected analysis results"""
        try:
            data = {
                filename: asdict(result)
                for filename, result in self.expected_results.items()
            }
            with open(self.expected_results_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving expected results: {e}")

    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data).hexdigest()

    def generate_random_data(self, size: int, seed: Optional[int] = None) -> bytes:
        """Generate random binary data"""
        if seed is not None:
            random.seed(seed)

        # Use os.urandom for better randomness if no seed
        if seed is None:
            return os.urandom(size)
        else:
            # Use seeded random for reproducible data
            return bytes(random.randint(0, 255) for _ in range(size))

    def generate_structured_data(self, size: int, structure_type: str = "binary") -> bytes:
        """Generate structured binary data"""
        if structure_type == "pe_header":
            return self._generate_pe_header_structure(size)
        elif structure_type == "elf_header":
            return self._generate_elf_header_structure(size)
        elif structure_type == "archive":
            return self._generate_archive_structure(size)
        elif structure_type == "custom":
            return self._generate_custom_structure(size)
        else:
            return self._generate_binary_structure(size)

    def _generate_pe_header_structure(self, size: int) -> bytes:
        """Generate PE header-like structure"""
        data = bytearray()

        # DOS header
        data.extend(b'MZ')  # Magic number
        data.extend(b'\x90\x00\x03\x00\x00\x00\x04\x00')
        data.extend(b'\x00\x00\xff\xff\x00\x00\xb8\x00')
        data.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00')

        # Add some DOS stub code
        data.extend([0x0E] * 32)  # Some instructions

        # PE signature
        pe_offset = len(data)
        data.extend(b'PE\x00\x00')

        # COFF header
        data.extend(b'\x4c\x01')  # Machine (i386)
        data.extend(b'\x03\x00')  # Number of sections
        data.extend(b'\x00\x00\x00\x00')  # Timestamp
        data.extend(b'\x1e\x00\x00\x00')  # Pointer to symbol table
        data.extend(b'\x00\x00\x00\x00')  # Number of symbols
        data.extend(b'\xf0\x00')  # Optional header size
        data.extend(b'\x03\x03')  # Characteristics

        # Fill with padding to reach desired size
        while len(data) < size:
            data.extend(os.urandom(min(64, size - len(data))))

        return bytes(data[:size])

    def _generate_elf_header_structure(self, size: int) -> bytes:
        """Generate ELF header-like structure"""
        data = bytearray()

        # ELF header
        data.extend(b'\x7fELF')  # Magic number
        data.extend(b'\x01')     # 32-bit
        data.extend(b'\x01')     # Little endian
        data.extend(b'\x01')     # ELF version
        data.extend(b'\x00')     # OS ABI
        data.extend(b'\x00')     # ABI version
        data.extend(b'\x00' * 7)  # Padding

        # ELF type, machine, version
        data.extend(b'\x02\x00')  # Executable
        data.extend(b'\x03\x00')  # 386
        data.extend(b'\x01\x00\x00\x00')  # Version

        # Add program header and section header placeholders
        data.extend(b'\x00' * 16)  # Entry point
        data.extend(b'\x00' * 16)  # Program header offset
        data.extend(b'\x00' * 16)  # Section header offset

        # Fill with padding
        while len(data) < size:
            data.extend(os.urandom(min(64, size - len(data))))

        return bytes(data[:size])

    def _generate_archive_structure(self, size: int) -> bytes:
        """Generate archive-like structure"""
        data = bytearray()

        # Archive magic
        data.extend(b'!<arch>\n')

        # Add some file headers
        file_names = ["file1.txt", "file2.dat", "file3.bin"]
        for filename in file_names:
            # File header (60 bytes)
            header = f"{filename[:16]:<16}"
            header += f"{int(time.time()):<12}"  # Timestamp
            header += f"{0:<6}"  # Owner ID
            header += f"{0:<6}"  # Group ID
            header += f"{644:<8}"  # Mode
            header += f"{len(filename):<10}"  # File size
            header += f"`\n"  # End marker
            data.extend(header.encode('ascii'))

            # File content
            data.extend(filename.encode('ascii'))

            # Pad to even length
            if len(data) % 2 != 0:
                data.append(0x0A)

        # Fill with padding
        while len(data) < size:
            data.extend(os.urandom(min(64, size - len(data))))

        return bytes(data[:size])

    def _generate_custom_structure(self, size: int) -> bytes:
        """Generate custom binary structure"""
        data = bytearray()

        # Custom header
        data.extend(b'CUST\x01\x00')  # Magic and version
        data.extend(struct.pack('<I', size))  # Total size

        # Data sections
        section_types = [0x01, 0x02, 0x03, 0x04]
        for i, section_type in enumerate(section_types):
            # Section header
            data.extend(struct.pack('<H', section_type))  # Section type
            section_size = (size - len(data) - 16) // len(section_types)
            data.extend(struct.pack('<I', section_size))  # Section size
            data.extend(struct.pack('<I', i))  # Section ID

            # Section data
            if section_type == 0x01:
                # Repeating pattern
                pattern = [0xAA, 0x55, 0xFF, 0x00] * (section_size // 4)
                data.extend(pattern[:section_size])
            elif section_type == 0x02:
                # Sequential values
                data.extend(bytes(i % 256 for i in range(section_size)))
            elif section_type == 0x03:
                # Random-like but structured
                for j in range(section_size):
                    data.append((i * 17 + j * 13) % 256)
            else:
                # Mixed data
                for j in range(section_size):
                    if j % 3 == 0:
                        data.append(0x00)
                    elif j % 3 == 1:
                        data.append(0xFF)
                    else:
                        data.append((i + j) % 256)

        # Footer
        data.extend(b'END\xFF\xFF')

        return bytes(data[:size])

    def _generate_binary_structure(self, size: int) -> bytes:
        """Generate generic binary structure"""
        data = bytearray()

        # Header
        data.extend(b'BIN\x01')

        # Mixed data sections
        sections = [
            (0x20, b'\x00' * 0x20),  # Null bytes
            (0x40, bytes(range(0x40))),  # Sequential
            (0x30, b'\xFF' * 0x30),  # High bytes
            (0x50, os.urandom(0x50)),  # Random
        ]

        for section_size, section_data in sections:
            if len(data) + section_size > size - 4:
                section_size = size - len(data) - 4
                section_data = section_data[:section_size]
            data.extend(section_data)

        # Footer
        data.extend(b'END')

        # Fill to exact size
        while len(data) < size:
            data.append(0x00)

        return bytes(data[:size])

    def generate_patterned_data(self, size: int, pattern: str = "repeating") -> bytes:
        """Generate patterned binary data"""
        if pattern == "repeating":
            # Repeating 4-byte pattern
            pattern_bytes = b'\xDE\xAD\xBE\xEF'
            return (pattern_bytes * ((size // 4) + 1))[:size]

        elif pattern == "alternating":
            # Alternating high/low bytes
            return bytes([0xFF if i % 2 == 0 else 0x00 for i in range(size)])

        elif pattern == "incremental":
            # Incrementing bytes
            return bytes(i % 256 for i in range(size))

        elif pattern == "decremental":
            # Decrementing bytes
            return bytes((255 - i) % 256 for i in range(size))

        elif pattern == "checkerboard":
            # 8x8 checkerboard pattern
            pattern = []
            for row in range(8):
                row_pattern = []
                for col in range(8):
                    if (row + col) % 2 == 0:
                        row_pattern.extend([0xFF] * 8)
                    else:
                        row_pattern.extend([0x00] * 8)
                pattern.extend(row_pattern)
            return bytes((pattern * ((size // 64) + 1))[:size])

        else:
            return self.generate_random_data(size)

    def generate_compressed_data(self, uncompressed_size: int,
                                compression_ratio: float = 0.3) -> bytes:
        """Generate compressed test data"""
        # Create uncompressed data with low entropy (easier to compress)
        uncompressed_data = bytearray()

        # Use repeating patterns for better compression
        patterns = [
            b'A' * 100,
            b'B' * 50,
            b'\x00' * 200,
            b'\xFF' * 75,
            bytes(range(128))
        ]

        while len(uncompressed_data) < uncompressed_size:
            pattern = random.choice(patterns)
            uncompressed_data.extend(pattern)

        uncompressed_data = bytes(uncompressed_data[:uncompressed_size])

        # Compress the data
        compressed_data = gzip.compress(uncompressed_data)

        # If compression ratio is not met, try to adjust
        actual_ratio = len(compressed_data) / len(uncompressed_data)
        if actual_ratio > compression_ratio:
            # Data doesn't compress well enough, use more compressible patterns
            uncompressed_data = b'A' * uncompressed_size
            compressed_data = gzip.compress(uncompressed_data)

        return compressed_data

    def generate_malformed_data(self, size: int,
                               malformation_type: str = "truncated") -> bytes:
        """Generate malformed test data"""
        if malformation_type == "truncated":
            # Create a structure and then truncate it
            full_structure = self.generate_structured_data(size * 2, "custom")
            return full_structure[:size]

        elif malformation_type == "invalid_magic":
            # Start with valid structure but change magic bytes
            data = self.generate_structured_data(size, "custom")
            return b'XXXX' + data[4:]

        elif malformation_type == "corrupted":
            # Start with valid data and corrupt random bytes
            data = bytearray(self.generate_structured_data(size, "custom"))
            # Corrupt about 10% of bytes
            corruption_count = int(size * 0.1)
            for _ in range(corruption_count):
                pos = random.randint(0, size - 1)
                data[pos] = random.randint(0, 255)
            return bytes(data)

        elif malformation_type == "overflow":
            # Create data with intentional overflow indicators
            data = bytearray()
            data.extend(b'OVER')
            data.extend(b'\xFF' * 100)  # Potential buffer overflow
            data.extend(os.urandom(size - 104))
            return bytes(data)

        else:
            return self.generate_random_data(size)

    def create_test_file(self, filename: str, data_type: DataType,
                        size: int, **kwargs) -> Tuple[Path, TestDataMetadata]:
        """Create a test file with specified parameters"""
        file_path = self.test_files_dir / filename

        # Generate data based on type
        if data_type == DataType.RANDOM:
            seed = kwargs.get('seed')
            data = self.generate_random_data(size, seed)

        elif data_type == DataType.STRUCTURED:
            structure_type = kwargs.get('structure_type', 'binary')
            data = self.generate_structured_data(size, structure_type)

        elif data_type == DataType.PATTERNED:
            pattern = kwargs.get('pattern', 'repeating')
            data = self.generate_patterned_data(size, pattern)

        elif data_type == DataType.COMPRESSED:
            uncompressed_size = kwargs.get('uncompressed_size', size * 3)
            compression_ratio = kwargs.get('compression_ratio', 0.3)
            data = self.generate_compressed_data(uncompressed_size, compression_ratio)

        elif data_type == DataType.MALFORMED:
            malformation_type = kwargs.get('malformation_type', 'truncated')
            data = self.generate_malformed_data(size, malformation_type)

        else:
            data = self.generate_random_data(size)

        # Write file
        with open(file_path, 'wb') as f:
            f.write(data)

        # Create metadata
        from datetime import datetime
        metadata = TestDataMetadata(
            filename=filename,
            data_type=data_type,
            size=len(data),
            seed=kwargs.get('seed'),
            description=kwargs.get('description', f'{data_type.value} test data'),
            created_at=datetime.now().isoformat(),
            checksum=self._calculate_checksum(data),
            properties=kwargs
        )

        # Store metadata
        self.metadata[filename] = metadata
        self._save_metadata()

        return file_path, metadata

    def create_expected_result(self, filename: str, expected_result: ExpectedResult):
        """Create expected analysis result for test file"""
        self.expected_results[filename] = expected_result
        self._save_expected_results()

    def generate_test_suite(self) -> Dict[str, List[str]]:
        """Generate comprehensive test suite"""
        generated_files = {
            'unit_tests': [],
            'integration_tests': [],
            'performance_tests': [],
            'regression_tests': []
        }

        # Unit test files (small, varied types)
        unit_test_configs = [
            ('random_small.bin', DataType.RANDOM, FileSize.SMALL.value,
             {'seed': 42, 'description': 'Small random data for unit tests'}),
            ('structured_small.bin', DataType.STRUCTURED, FileSize.SMALL.value,
             {'structure_type': 'custom', 'description': 'Small structured data'}),
            ('patterned_small.bin', DataType.PATTERNED, FileSize.SMALL.value,
             {'pattern': 'repeating', 'description': 'Small patterned data'}),
        ]

        for filename, data_type, size, props in unit_test_configs:
            path, _ = self.create_test_file(filename, data_type, size, **props)
            generated_files['unit_tests'].append(str(path))

        # Integration test files (medium, complex structures)
        integration_test_configs = [
            ('pe_header_medium.bin', DataType.STRUCTURED, FileSize.MEDIUM.value,
             {'structure_type': 'pe_header', 'description': 'PE header structure'}),
            ('elf_header_medium.bin', DataType.STRUCTURED, FileSize.MEDIUM.value,
             {'structure_type': 'elf_header', 'description': 'ELF header structure'}),
            ('archive_medium.bin', DataType.STRUCTURED, FileSize.MEDIUM.value,
             {'structure_type': 'archive', 'description': 'Archive structure'}),
            ('compressed_medium.bin', DataType.COMPRESSED, FileSize.MEDIUM.value,
             {'uncompressed_size': FileSize.LARGE.value, 'description': 'Compressed data'}),
        ]

        for filename, data_type, size, props in integration_test_configs:
            path, _ = self.create_test_file(filename, data_type, size, **props)
            generated_files['integration_tests'].append(str(path))

        # Performance test files (large, for benchmarking)
        performance_test_configs = [
            ('random_large.bin', DataType.RANDOM, FileSize.LARGE.value,
             {'seed': 123, 'description': 'Large random data for performance tests'}),
            ('structured_large.bin', DataType.STRUCTURED, FileSize.LARGE.value,
             {'structure_type': 'custom', 'description': 'Large structured data'}),
            ('patterned_large.bin', DataType.PATTERNED, FileSize.LARGE.value,
             {'pattern': 'incremental', 'description': 'Large patterned data'}),
        ]

        for filename, data_type, size, props in performance_test_configs:
            path, _ = self.create_test_file(filename, data_type, size, **props)
            generated_files['performance_tests'].append(str(path))

        # Regression test files (known problematic cases)
        regression_test_configs = [
            ('truncated_malformed.bin', DataType.MALFORMED, FileSize.SMALL.value,
             {'malformation_type': 'truncated', 'description': 'Truncated structure'}),
            ('invalid_magic.bin', DataType.MALFORMED, FileSize.SMALL.value,
             {'malformation_type': 'invalid_magic', 'description': 'Invalid magic bytes'}),
            ('corrupted_data.bin', DataType.MALFORMED, FileSize.MEDIUM.value,
             {'malformation_type': 'corrupted', 'description': 'Corrupted structure'}),
        ]

        for filename, data_type, size, props in regression_test_configs:
            path, _ = self.create_test_file(filename, data_type, size, **props)
            generated_files['regression_tests'].append(str(path))

        # Create expected results for some files
        self._create_default_expected_results()

        return generated_files

    def _create_default_expected_results(self):
        """Create default expected results for key test files"""
        # Expected results for structured data
        self.create_expected_result('structured_small.bin', ExpectedResult(
            filename='structured_small.bin',
            expected_patterns=['custom_header', 'data_sections', 'footer'],
            expected_entropy_range=(3.0, 7.0),
            expected_structure_hints=['binary_structure', 'sectioned_format'],
            analysis_difficulty='easy',
            strategy_rankings={
                'MCTS Strategy': 1,
                'Genetic Algorithm': 2,
                'Beam Search': 3,
                'Simulated Annealing': 4,
                'Heuristic Analysis': 5
            }
        ))

        # Expected results for PE header
        self.create_expected_result('pe_header_medium.bin', ExpectedResult(
            filename='pe_header_medium.bin',
            expected_patterns=['pe_header', 'dos_stub', 'coff_header'],
            expected_entropy_range=(2.0, 5.0),
            expected_structure_hints=['pe_executable', 'windows_format'],
            analysis_difficulty='medium',
            strategy_rankings={
                'Heuristic Analysis': 1,
                'MCTS Strategy': 2,
                'Genetic Algorithm': 3,
                'Beam Search': 4,
                'Simulated Annealing': 5
            }
        ))

    def get_test_file(self, filename: str) -> Optional[Path]:
        """Get test file path by filename"""
        file_path = self.test_files_dir / filename
        return file_path if file_path.exists() else None

    def get_test_files_by_type(self, data_type: DataType) -> List[Path]:
        """Get all test files of specified type"""
        return [
            self.test_files_dir / filename
            for filename, metadata in self.metadata.items()
            if metadata.data_type == data_type
        ]

    def get_test_files_by_size(self, min_size: int, max_size: int) -> List[Path]:
        """Get test files within size range"""
        return [
            self.test_files_dir / filename
            for filename, metadata in self.metadata.items()
            if min_size <= metadata.size <= max_size
        ]

    def verify_file_integrity(self, filename: str) -> bool:
        """Verify test file integrity using checksum"""
        if filename not in self.metadata:
            return False

        file_path = self.test_files_dir / filename
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            current_checksum = self._calculate_checksum(data)
            expected_checksum = self.metadata[filename].checksum

            return current_checksum == expected_checksum
        except Exception:
            return False

    def cleanup_test_files(self):
        """Remove all generated test files"""
        if self.test_files_dir.exists():
            shutil.rmtree(self.test_files_dir)

        # Clear metadata
        self.metadata.clear()
        self.expected_results.clear()

        # Remove metadata files
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        if self.expected_results_file.exists():
            self.expected_results_file.unlink()

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of generated test data"""
        summary = {
            'total_files': len(self.metadata),
            'total_size': sum(meta.size for meta in self.metadata.values()),
            'files_by_type': {},
            'files_by_size': {
                'tiny': 0, 'small': 0, 'medium': 0, 'large': 0, 'huge': 0
            },
            'files_with_expected_results': len(self.expected_results)
        }

        # Count by type
        for metadata in self.metadata.values():
            data_type = metadata.data_type.value
            summary['files_by_type'][data_type] = summary['files_by_type'].get(data_type, 0) + 1

            # Count by size category
            size = metadata.size
            if size <= FileSize.TINY.value:
                summary['files_by_size']['tiny'] += 1
            elif size <= FileSize.SMALL.value:
                summary['files_by_size']['small'] += 1
            elif size <= FileSize.MEDIUM.value:
                summary['files_by_size']['medium'] += 1
            elif size <= FileSize.LARGE.value:
                summary['files_by_size']['large'] += 1
            else:
                summary['files_by_size']['huge'] += 1

        return summary


# Convenience function for quick test data generation
def generate_test_dataset(output_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Generate complete test dataset"""
    generator = TestDataGenerator(output_dir)
    return generator.generate_test_suite()


if __name__ == "__main__":
    # Generate test suite when run directly
    print("Generating BSEE test dataset...")
    generator = TestDataGenerator()

    # Generate test suite
    test_files = generator.generate_test_suite()

    # Print summary
    summary = generator.get_test_summary()
    print(f"\nTest Dataset Summary:")
    print(f"Total files: {summary['total_files']}")
    print(f"Total size: {summary['total_size']:,} bytes")
    print(f"Files with expected results: {summary['files_with_expected_results']}")

    print("\nFiles by type:")
    for data_type, count in summary['files_by_type'].items():
        print(f"  {data_type}: {count}")

    print("\nFiles by size:")
    for size_category, count in summary['files_by_size'].items():
        print(f"  {size_category}: {count}")

    print(f"\nTest files generated in: {generator.test_files_dir}")
    print("Metadata and expected results saved.")