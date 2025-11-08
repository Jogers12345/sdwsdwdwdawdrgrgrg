"""
Memory-Optimized Processing
Optimize memory usage for large file processing and streaming operations
"""

import os
import mmap
import gc
import time
import threading
from typing import Dict, List, Any, Optional, Iterator, Tuple, Callable, Union
from dataclasses import dataclass
from enum import Enum
import psutil
import tempfile
import shutil

from ..engine.state import BinaryState
from ..engine.operations import Operation


class MemoryPressureLevel(Enum):
    """Memory pressure levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemoryStatus:
    """Current memory status information"""
    total_memory_mb: float
    available_memory_mb: float
    used_memory_mb: float
    usage_percent: float
    pressure_level: MemoryPressureLevel
    process_memory_mb: float
    process_memory_percent: float
    swap_usage_mb: float
    swap_usage_percent: float


@dataclass
class ChunkConfig:
    """Configuration for chunked processing"""
    chunk_size: int = 1024 * 1024  # 1MB default
    overlap_size: int = 0  # Overlap between chunks
    max_memory_usage_mb: float = 512.0  # Maximum memory usage target
    enable_streaming: bool = True
    temp_dir: Optional[str] = None


@dataclass
class ProcessingStats:
    """Statistics for memory-optimized processing"""
    total_bytes_processed: int = 0
    chunks_processed: int = 0
    peak_memory_usage_mb: float = 0.0
    average_memory_usage_mb: float = 0.0
    processing_time_seconds: float = 0.0
    bytes_per_second: float = 0.0
    gc_runs: int = 0
    temporary_files_created: int = 0
    temporary_files_cleaned: int = 0


class MemoryMappedFile:
    """Memory-mapped file handler for efficient large file access"""

    def __init__(self, file_path: str, mode: str = 'r'):
        self.file_path = file_path
        self.mode = mode
        self.file_obj = None
        self.mmap_obj = None
        self.size = 0
        self.is_open = False

    def open(self):
        """Open the memory-mapped file"""
        try:
            self.file_obj = open(self.file_path, self.mode + 'b')
            self.size = os.path.getsize(self.file_path)

            if self.size > 0:
                if self.mode == 'r':
                    self.mmap_obj = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_READ)
                else:
                    self.mmap_obj = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_WRITE)

            self.is_open = True
            return True

        except Exception as e:
            print(f"Error opening memory-mapped file {self.file_path}: {e}")
            if self.file_obj:
                self.file_obj.close()
            return False

    def read(self, offset: int, size: int) -> bytes:
        """Read data from memory-mapped file"""
        if not self.is_open or not self.mmap_obj:
            raise RuntimeError("File not open")

        end_offset = min(offset + size, self.size)
        return self.mmap_obj[offset:end_offset]

    def write(self, offset: int, data: bytes) -> int:
        """Write data to memory-mapped file"""
        if not self.is_open or not self.mmap_obj:
            raise RuntimeError("File not open")

        end_offset = min(offset + len(data), self.size)
        self.mmap_obj[offset:end_offset] = data[:end_offset - offset]
        return end_offset - offset

    def get_slice(self, start: int, end: int) -> bytes:
        """Get a slice of the file data"""
        if not self.is_open or not self.mmap_obj:
            raise RuntimeError("File not open")

        start = max(0, min(start, self.size))
        end = max(start, min(end, self.size))
        return self.mmap_obj[start:end]

    def close(self):
        """Close the memory-mapped file"""
        try:
            if self.mmap_obj:
                self.mmap_obj.close()
                self.mmap_obj = None

            if self.file_obj:
                self.file_obj.close()
                self.file_obj = None

            self.is_open = False

        except Exception as e:
            print(f"Error closing memory-mapped file: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __len__(self):
        """Get file size"""
        return self.size


class ChunkedProcessor:
    """Process large files in configurable chunks"""

    def __init__(self, config: ChunkConfig):
        self.config = config
        self.temp_files = []
        self.lock = threading.Lock()

    def process_file_chunks(self, file_path: str, operation: Operation,
                          progress_callback: Optional[Callable[[float], None]] = None) -> ProcessingStats:
        """Process a file in chunks using the specified operation"""
        stats = ProcessingStats()
        start_time = time.time()

        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return stats

            # Determine optimal chunk size
            chunk_size = self._calculate_optimal_chunk_size(file_size)
            overlap = min(self.config.overlap_size, chunk_size // 2)

            # Process chunks
            with MemoryMappedFile(file_path, 'r') as mm_file:
                offset = 0
                chunk_index = 0

                while offset < file_size:
                    # Check memory pressure
                    self._check_memory_pressure()

                    # Calculate chunk boundaries
                    chunk_start = max(0, offset - overlap)
                    chunk_end = min(offset + chunk_size + overlap, file_size)
                    actual_chunk_size = chunk_end - chunk_start

                    # Read chunk
                    chunk_data = mm_file.read(chunk_start, actual_chunk_size)

                    # Create temporary file for chunk processing if needed
                    if self.config.enable_streaming:
                        chunk_file = self._create_temp_file(chunk_data)
                        chunk_path = chunk_file.name
                    else:
                        chunk_path = None

                    try:
                        # Process chunk
                        if chunk_path:
                            # Process from temporary file
                            chunk_result = self._process_chunk_file(chunk_path, operation)
                        else:
                            # Process in memory
                            chunk_result = self._process_chunk_data(chunk_data, operation)

                        # Handle result (could be written to output file)
                        self._handle_chunk_result(chunk_result, chunk_index, chunk_start)

                        # Update statistics
                        stats.total_bytes_processed += actual_chunk_size
                        stats.chunks_processed += 1
                        stats.peak_memory_usage_mb = max(stats.peak_memory_usage_mb,
                                                        self._get_current_memory_usage())

                        # Update progress
                        if progress_callback:
                            progress = min(1.0, (offset + chunk_size) / file_size)
                            progress_callback(progress)

                    finally:
                        # Clean up temporary file
                        if chunk_path and os.path.exists(chunk_path):
                            os.unlink(chunk_path)
                            with self.lock:
                                stats.temporary_files_cleaned += 1

                    # Move to next chunk
                    offset += chunk_size
                    chunk_index += 1

                    # Periodic garbage collection
                    if chunk_index % 10 == 0:
                        gc.collect()
                        stats.gc_runs += 1

            # Calculate final statistics
            end_time = time.time()
            stats.processing_time_seconds = end_time - start_time
            stats.bytes_per_second = stats.total_bytes_processed / stats.processing_time_seconds if stats.processing_time_seconds > 0 else 0

            return stats

        except Exception as e:
            print(f"Error processing file chunks: {e}")
            return stats

    def _calculate_optimal_chunk_size(self, file_size: int) -> int:
        """Calculate optimal chunk size based on file size and memory constraints"""
        target_memory_mb = self.config.max_memory_usage_mb * 0.5  # Use 50% of target for chunk
        target_chunk_size = int(target_memory_mb * 1024 * 1024)

        # Consider file size
        if file_size < target_chunk_size:
            return file_size

        # Consider system memory
        available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
        max_chunk_size = int(available_memory_mb * 0.1)  # Use 10% of available memory

        # Use minimum of calculated sizes, but at least 64KB
        chunk_size = min(target_chunk_size, max_chunk_size, self.config.chunk_size)
        return max(chunk_size, 64 * 1024)

    def _create_temp_file(self, data: bytes) -> tempfile.NamedTemporaryFile:
        """Create a temporary file with chunk data"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=self.config.temp_dir)
        temp_file.write(data)
        temp_file.flush()
        temp_file.close()

        with self.lock:
            self.temp_files.append(temp_file.name)

        return temp_file

    def _process_chunk_data(self, chunk_data: bytes, operation: Operation) -> Any:
        """Process chunk data in memory"""
        try:
            state = BinaryState(chunk_data)
            result_state = operation.apply(state)
            return result_state.data
        except Exception as e:
            print(f"Error processing chunk data: {e}")
            return chunk_data  # Return original data on error

    def _process_chunk_file(self, chunk_path: str, operation: Operation) -> Any:
        """Process chunk from temporary file"""
        try:
            with open(chunk_path, 'rb') as f:
                chunk_data = f.read()
            return self._process_chunk_data(chunk_data, operation)
        except Exception as e:
            print(f"Error processing chunk file: {e}")
            with open(chunk_path, 'rb') as f:
                return f.read()  # Return original data on error

    def _handle_chunk_result(self, result: Any, chunk_index: int, offset: int):
        """Handle the result of chunk processing"""
        # This would typically write to an output file or queue
        # For now, we just track that it was processed
        pass

    def _check_memory_pressure(self):
        """Check current memory pressure and take action if needed"""
        memory_status = get_memory_status()

        if memory_status.pressure_level == MemoryPressureLevel.CRITICAL:
            # Aggressive cleanup
            gc.collect()
            self._cleanup_temp_files()

            # Raise error if still critical
            if get_memory_status().pressure_level == MemoryPressureLevel.CRITICAL:
                raise MemoryError("Critical memory pressure, cannot continue processing")

        elif memory_status.pressure_level == MemoryPressureLevel.HIGH:
            # Moderate cleanup
            gc.collect()

    def _get_current_memory_usage(self) -> float:
        """Get current process memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        with self.lock:
            for temp_file in self.temp_files[:]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                    self.temp_files.remove(temp_file)
                except Exception as e:
                    print(f"Error cleaning up temp file {temp_file}: {e}")

    def cleanup(self):
        """Clean up resources"""
        self._cleanup_temp_files()


class StreamingProcessor:
    """Streaming processor for very large files"""

    def __init__(self, buffer_size: int = 64 * 1024):  # 64KB default
        self.buffer_size = buffer_size
        self.temp_dir = tempfile.mkdtemp(prefix="bsee_streaming_")

    def stream_process_file(self, input_path: str, output_path: str,
                           operation: Operation, buffer_size: Optional[int] = None,
                           progress_callback: Optional[Callable[[float], None]] = None) -> ProcessingStats:
        """Process a file using streaming approach"""
        stats = ProcessingStats()
        start_time = time.time()

        if buffer_size is None:
            buffer_size = self.buffer_size

        try:
            # Get file size
            file_size = os.path.getsize(input_path)
            if file_size == 0:
                return stats

            # Open input and output files
            with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
                bytes_processed = 0
                chunk_index = 0

                while True:
                    # Read buffer
                    buffer = input_file.read(buffer_size)
                    if not buffer:
                        break

                    # Check memory pressure periodically
                    if chunk_index % 100 == 0:
                        self._check_memory_pressure()

                    # Process buffer
                    processed_buffer = self._process_buffer(buffer, operation)

                    # Write processed buffer
                    output_file.write(processed_buffer)

                    # Update statistics
                    bytes_processed += len(buffer)
                    stats.total_bytes_processed += len(buffer)
                    stats.chunks_processed += 1

                    # Update peak memory usage
                    current_memory = self._get_current_memory_usage()
                    stats.peak_memory_usage_mb = max(stats.peak_memory_usage_mb, current_memory)

                    # Update progress
                    if progress_callback and chunk_index % 10 == 0:
                        progress = bytes_processed / file_size
                        progress_callback(progress)

                    chunk_index += 1

                    # Periodic garbage collection
                    if chunk_index % 1000 == 0:
                        gc.collect()
                        stats.gc_runs += 1

            # Calculate final statistics
            end_time = time.time()
            stats.processing_time_seconds = end_time - start_time
            stats.bytes_per_second = stats.total_bytes_processed / stats.processing_time_seconds if stats.processing_time_seconds > 0 else 0

            return stats

        except Exception as e:
            print(f"Error in streaming processing: {e}")
            return stats

    def _process_buffer(self, buffer: bytes, operation: Operation) -> bytes:
        """Process a single buffer"""
        try:
            state = BinaryState(buffer)
            result_state = operation.apply(state)
            return result_state.data
        except Exception as e:
            print(f"Error processing buffer: {e}")
            return buffer  # Return original buffer on error

    def _check_memory_pressure(self):
        """Check memory pressure and take action"""
        memory_status = get_memory_status()

        if memory_status.pressure_level == MemoryPressureLevel.CRITICAL:
            gc.collect()
            if get_memory_status().pressure_level == MemoryPressureLevel.CRITICAL:
                raise MemoryError("Critical memory pressure in streaming processor")

        elif memory_status.pressure_level == MemoryPressureLevel.HIGH:
            gc.collect()

    def _get_current_memory_usage(self) -> float:
        """Get current process memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def cleanup(self):
        """Clean up streaming processor resources"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up streaming processor: {e}")


def get_memory_status() -> MemoryStatus:
    """Get current memory status"""
    try:
        # System memory
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Process memory
        process = psutil.Process()
        process_memory = process.memory_info()

        # Determine pressure level
        if memory.percent < 50:
            pressure_level = MemoryPressureLevel.LOW
        elif memory.percent < 75:
            pressure_level = MemoryPressureLevel.MEDIUM
        elif memory.percent < 90:
            pressure_level = MemoryPressureLevel.HIGH
        else:
            pressure_level = MemoryPressureLevel.CRITICAL

        return MemoryStatus(
            total_memory_mb=memory.total / (1024 * 1024),
            available_memory_mb=memory.available / (1024 * 1024),
            used_memory_mb=memory.used / (1024 * 1024),
            usage_percent=memory.percent,
            pressure_level=pressure_level,
            process_memory_mb=process_memory.rss / (1024 * 1024),
            process_memory_percent=process.memory_percent(),
            swap_usage_mb=swap.used / (1024 * 1024),
            swap_usage_percent=swap.percent
        )

    except Exception as e:
        print(f"Error getting memory status: {e}")
        return MemoryStatus(
            total_memory_mb=0, available_memory_mb=0, used_memory_mb=0,
            usage_percent=0, pressure_level=MemoryPressureLevel.LOW,
            process_memory_mb=0, process_memory_percent=0,
            swap_usage_mb=0, swap_usage_percent=0
        )


class MemoryOptimizer:
    """Main memory optimization system"""

    def __init__(self, default_chunk_config: Optional[ChunkConfig] = None):
        self.default_chunk_config = default_chunk_config or ChunkConfig()
        self.processing_stats = []
        self.lock = threading.Lock()

        # Memory monitoring
        self.monitoring_enabled = False
        self.monitor_thread = None
        self.memory_history = []

    def optimize_for_file(self, file_path: str, file_size_hint: Optional[int] = None) -> ChunkConfig:
        """Create optimal chunk configuration for a specific file"""
        try:
            # Get file size
            if file_size_hint is None:
                file_size = os.path.getsize(file_path)
            else:
                file_size = file_size_hint

            if file_size == 0:
                return self.default_chunk_config

            # Get memory status
            memory_status = get_memory_status()

            # Calculate optimal configuration
            config = ChunkConfig()

            # Adjust chunk size based on file size
            if file_size < 1024 * 1024:  # < 1MB
                config.chunk_size = file_size
                config.enable_streaming = False
            elif file_size < 100 * 1024 * 1024:  # < 100MB
                config.chunk_size = min(1024 * 1024, file_size // 10)
                config.enable_streaming = False
            else:  # >= 100MB
                config.chunk_size = min(10 * 1024 * 1024, file_size // 100)
                config.enable_streaming = True

            # Adjust for memory availability
            if memory_status.pressure_level == MemoryPressureLevel.HIGH:
                config.chunk_size = min(config.chunk_size, 512 * 1024)  # Max 512KB chunks
                config.max_memory_usage_mb = min(config.max_memory_usage_mb, 128.0)
            elif memory_status.pressure_level == MemoryPressureLevel.CRITICAL:
                config.chunk_size = min(config.chunk_size, 256 * 1024)  # Max 256KB chunks
                config.max_memory_usage_mb = min(config.max_memory_usage_mb, 64.0)

            # Set temporary directory
            config.temp_dir = tempfile.mkdtemp(prefix="bsee_optimized_")

            return config

        except Exception as e:
            print(f"Error optimizing for file: {e}")
            return self.default_chunk_config

    def process_large_file(self, file_path: str, operation: Operation,
                          chunk_config: Optional[ChunkConfig] = None,
                          progress_callback: Optional[Callable[[float], None]] = None) -> ProcessingStats:
        """Process a large file with memory optimization"""
        if chunk_config is None:
            chunk_config = self.optimize_for_file(file_path)

        try:
            # Choose processing method based on file size and configuration
            file_size = os.path.getsize(file_path)

            if chunk_config.enable_streaming or file_size > 500 * 1024 * 1024:  # 500MB threshold
                # Use streaming processor for very large files
                processor = StreamingProcessor(buffer_size=chunk_config.chunk_size)

                # Create output file path
                output_path = file_path + "_processed"

                try:
                    stats = processor.stream_process_file(
                        file_path, output_path, operation,
                        chunk_config.chunk_size, progress_callback
                    )

                    # Store statistics
                    with self.lock:
                        self.processing_stats.append(stats)

                    return stats

                finally:
                    processor.cleanup()

            else:
                # Use chunked processor for medium files
                processor = ChunkedProcessor(chunk_config)

                try:
                    stats = processor.process_file_chunks(file_path, operation, progress_callback)

                    # Store statistics
                    with self.lock:
                        self.processing_stats.append(stats)

                    return stats

                finally:
                    processor.cleanup()

        except Exception as e:
            print(f"Error processing large file: {e}")
            return ProcessingStats()

    def start_memory_monitoring(self, interval_seconds: float = 5.0):
        """Start background memory monitoring"""
        if self.monitoring_enabled:
            return

        self.monitoring_enabled = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        print("Memory monitoring started")

    def stop_memory_monitoring(self):
        """Stop background memory monitoring"""
        self.monitoring_enabled = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        print("Memory monitoring stopped")

    def _monitoring_loop(self, interval_seconds: float):
        """Background memory monitoring loop"""
        while self.monitoring_enabled:
            try:
                memory_status = get_memory_status()

                # Store in history (keep last 1000 entries)
                self.memory_history.append({
                    'timestamp': time.time(),
                    'status': memory_status
                })

                if len(self.memory_history) > 1000:
                    self.memory_history.pop(0)

                # Check for critical memory pressure
                if memory_status.pressure_level == MemoryPressureLevel.CRITICAL:
                    print(f"CRITICAL: Memory usage at {memory_status.usage_percent:.1f}%")
                    gc.collect()

                time.sleep(interval_seconds)

            except Exception as e:
                print(f"Error in memory monitoring: {e}")
                time.sleep(interval_seconds)

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get statistics about memory optimization"""
        with self.lock:
            if not self.processing_stats:
                return {}

            total_files = len(self.processing_stats)
            total_bytes = sum(stats.total_bytes_processed for stats in self.processing_stats)
            total_time = sum(stats.processing_time_seconds for stats in self.processing_stats)
            peak_memory = max(stats.peak_memory_usage_mb for stats in self.processing_stats)
            total_gc_runs = sum(stats.gc_runs for stats in self.processing_stats)

            return {
                'files_processed': total_files,
                'total_bytes_processed': total_bytes,
                'total_processing_time_seconds': total_time,
                'average_bytes_per_second': total_bytes / total_time if total_time > 0 else 0,
                'peak_memory_usage_mb': peak_memory,
                'total_gc_runs': total_gc_runs,
                'average_gc_runs_per_file': total_gc_runs / total_files if total_files > 0 else 0,
                'memory_monitoring_enabled': self.monitoring_enabled,
                'memory_history_entries': len(self.memory_history)
            }

    def export_optimization_data(self, format: str = 'json') -> str:
        """Export optimization statistics"""
        try:
            data = {
                'statistics': self.get_optimization_statistics(),
                'recent_memory_history': [
                    {
                        'timestamp': entry['timestamp'],
                        'usage_percent': entry['status'].usage_percent,
                        'pressure_level': entry['status'].pressure_level.value
                    }
                    for entry in self.memory_history[-100:]  # Last 100 entries
                ],
                'configuration': {
                    'default_chunk_size': self.default_chunk_config.chunk_size,
                    'default_max_memory_mb': self.default_chunk_config.max_memory_usage_mb,
                    'default_streaming': self.default_chunk_config.enable_streaming
                },
                'export_timestamp': time.time()
            }

            if format.lower() == 'json':
                import json
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            return f"Error exporting optimization data: {e}"

    def cleanup(self):
        """Clean up memory optimizer resources"""
        self.stop_memory_monitoring()

        # Clean up any remaining temporary files
        try:
            temp_dirs = [self.default_chunk_config.temp_dir] if self.default_chunk_config.temp_dir else []
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up memory optimizer: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()