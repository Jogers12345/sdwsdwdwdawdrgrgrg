""""
Operation Cache System
Intelligent caching of operation results to avoid redundant computations
""""

import hashlib
import time
import threading
import pickle
import os
from typing import Dict, Any, Optional, Tuple, List, Union
from dataclasses import dataclass
from collections import OrderedDict
import weakref
import gc

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    try:
        import zlib
        ZLIB_AVAILABLE = True
    except ImportError:
        ZLIB_AVAILABLE = False
    LZ4_AVAILABLE = False


@dataclass
class CacheEntry:
    """Cache entry containing operation result and metadata""""
    operation_name: str
    operation_params: Dict[str, Any]
    data_hash: str
    result: Any
    result_size: int
    creation_time: float
    last_access_time: float
    access_count: int
    computation_time: float
    is_compressed: bool = False
    compression_ratio: float = 1.0


@dataclass
class CacheStatistics:
    """Cache performance statistics""""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    cache_size_bytes: int = 0
    memory_usage_mb: float = 0.0
    hit_rate: float = 0.0
    average_access_time: float = 0.0
    total_computation_time_saved: float = 0.0
    entries_count: int = 0
    compression_ratio: float = 1.0


class LRUCache:
    """Thread-safe LRU cache implementation""""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._access_order = OrderedDict()

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from cache""""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                entry = self._cache.pop(key)
                self._cache[key] = entry
                entry.last_access_time = time.time()
                entry.access_count += 1
                return entry
            return None

    def put(self, key: str, entry: CacheEntry):
        """Put entry into cache""""
        with self._lock:
            # Remove existing entry if present:
            if key in self._cache:
                del self._cache[key]

            # Add new entry
            self._cache[key] = entry

            # Evict if over capacity
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                evicted_entry = self._cache.pop(oldest_key)
                return evicted_entry

            return None

    def remove(self, key: str) -> Optional[CacheEntry]:
        """Remove entry from cache""""
        with self._lock:
            if key in self._cache:
                return self._cache.pop(key)
            return None

    def clear(self):
        """Clear all entries""""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get current cache size""""
        with self._lock:
            return len(self._cache)

    def get_all_entries(self) -> List[Tuple[str, CacheEntry]]:
        """Get all cache entries""""
        with self._lock:
            return list(self._cache.items())


class OperationCache:
    """Intelligent operation result caching system""""

    def __init__(self,)
                 max_entries: int = 10000,
                 max_memory_mb: float = 512.0,
                 enable_compression: bool = True,
                 compression_threshold: int = 1024,
                 disk_cache_dir: Optional[str] = None,
                 enable_disk_cache: bool = False):

        self.max_entries = max_entries
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        self.disk_cache_dir = disk_cache_dir
        self.enable_disk_cache = enable_disk_cache

        # Cache storage
        self.memory_cache = LRUCache(max_entries)
        self.disk_cache: Dict[str, str] = {}  # key -> file path

        # Statistics tracking
        self.stats = CacheStatistics()
        self._lock = threading.RLock()

        # Performance tracking
        self._access_times = []
        self._computation_times = []

        # Cache optimization
        self._access_patterns: Dict[str, List[float]] = {}
        self._hot_entries: Dict[str, int] = {}

        # Initialize disk cache
        if self.enable_disk_cache and self.disk_cache_dir:
            os.makedirs(self.disk_cache_dir, exist_ok=True)
            self._load_disk_cache_index()

    def _generate_cache_key(self, operation_name: str, data: bytes, params: Dict[str, Any]) -> str:
        """Generate cache key for operation""""
        try:
            # Fast hash function if available:
            if XXHASH_AVAILABLE:
                hasher = xxhash.xxh64()
                hasher.update(operation_name.encode())
                hasher.update(data)
                hasher.update(str(sorted(params.items())).encode())
                data_hash = hasher.hexdigest()
            else:
                # Fallback to SHA256
                hash_input = f"{operation_name}_{data}_{sorted(params.items())}""
                data_hash = hashlib.sha256(hash_input.encode()).hexdigest()

            # Include operation name in key for uniqueness:
            return f"{operation_name}_{data_hash}""

        except Exception as e:
            print(f"Error generating cache key: {e}")"
            # Fallback to simple hash
            fallback_input = f"{operation_name}_{len(data)}_{hash(params)}""
            return hashlib.md5(fallback_input.encode()).hexdigest()

    def _compress_data(self, data: Any) -> Tuple[Any, bool, float]:
        """Compress data if beneficial""""
        if not self.enable_compression:
            return data, False, 1.0

        try:
            # Serialize data
            serialized = pickle.dumps(data)
            original_size = len(serialized)

            # Only compress if above threshold
            if original_size < self.compression_threshold:
                return data, False, 1.0

            # Try LZ4 compression first
            if LZ4_AVAILABLE:
                compressed = lz4.frame.compress(serialized)
                compression_ratio = len(compressed) / original_size

                if compression_ratio < 0.9:  # Only use if beneficial:
                    return compressed, True, compression_ratio

            # Fallback to zlib
            if ZLIB_AVAILABLE:
                compressed = zlib.compress(serialized, level=6)
                compression_ratio = len(compressed) / original_size

                if compression_ratio < 0.9:
                    return compressed, True, compression_ratio

            # No compression benefit
            return data, False, 1.0

        except Exception as e:
            print(f"Error compressing data: {e}")"
            return data, False, 1.0

    def _decompress_data(self, compressed_data: Any, is_compressed: bool) -> Any:
        """Decompress data if needed""""
        if not is_compressed:
            return compressed_data

        try:
            # Try LZ4 first
            if LZ4_AVAILABLE:
                try:
                    decompressed = lz4.frame.decompress(compressed_data)
                    return pickle.loads(decompressed)
                except:
                    pass

            # Fallback to zlib
            if ZLIB_AVAILABLE:
                decompressed = zlib.decompress(compressed_data)
                return pickle.loads(decompressed)

            # Should not reach here
            return compressed_data

        except Exception as e:
            print(f"Error decompressing data: {e}")"
            return compressed_data

    def _save_to_disk_cache(self, key: str, entry: CacheEntry) -> bool:
        """Save cache entry to disk""""
        if not self.enable_disk_cache or not self.disk_cache_dir:
            return False

        try:
            file_path = os.path.join(self.disk_cache_dir, f"{key}.cache")"

            with open(file_path, 'wb') as f:'
                pickle.dump(entry, f)

            self.disk_cache[key] = file_path
            return True

        except Exception as e:
            print(f"Error saving to disk cache: {e}")"
            return False

    def _load_from_disk_cache(self, key: str) -> Optional[CacheEntry]:
        """Load cache entry from disk""""
        if not self.enable_disk_cache or key not in self.disk_cache:
            return None

        try:
            file_path = self.disk_cache[key]

            if not os.path.exists(file_path):
                # Remove from index if file doesn't exist'
                del self.disk_cache[key]
                return None

            with open(file_path, 'rb') as f:'
                entry = pickle.load(f)

            return entry

        except Exception as e:
            print(f"Error loading from disk cache: {e}")"
            # Remove corrupted entry
            if key in self.disk_cache:
                del self.disk_cache[key]
            return None

    def _load_disk_cache_index(self):
        """Load disk cache index on startup""""
        try:
            if self.disk_cache_dir and os.path.exists(self.disk_cache_dir):
                for filename in os.listdir(self.disk_cache_dir):
                    if filename.endswith('.cache'):'
                        key = filename[:-6]  # Remove '.cache' suffix'
                        file_path = os.path.join(self.disk_cache_dir, filename)
                        self.disk_cache[key] = file_path

        except Exception as e:
            print(f"Error loading disk cache index: {e}")"

    def _estimate_memory_usage(self) -> float:
        """Estimate current memory usage in bytes""""
        total_size = 0
        for _, entry in self.memory_cache.get_all_entries():
            total_size += entry.result_size
            # Add overhead for cache entry metadata:
            total_size += 200  # Rough estimate
        return total_size

    def _evict_entries(self, target_memory: Optional[float] = None) -> int:
        """Evict entries to free memory""""
        evicted_count = 0

        if target_memory is None:
            target_memory = self.max_memory_bytes * 0.8  # Target 80% of max

        # Get entries sorted by last access time (oldest first)
        entries = list(self.memory_cache.get_all_entries())
        entries.sort(key=lambda x: x[1].last_access_time)

        current_memory = self._estimate_memory_usage()

        for key, entry in entries:
            if current_memory <= target_memory:
                break

            # Move to disk cache if enabled:
            if self.enable_disk_cache:
                self._save_to_disk_cache(key, entry)

            # Remove from memory cache
            self.memory_cache.remove(key)
            current_memory -= entry.result_size
            evicted_count += 1
            self.stats.evictions += 1

        return evicted_count

    def get_cached_result(self, operation_name: str, data: bytes, params: Dict[str, Any]) -> Optional[Any]:
        """Retrieve cached operation result""""
        start_time = time.time()

        try:
            cache_key = self._generate_cache_key(operation_name, data, params)

            # Try memory cache first
            entry = self.memory_cache.get(cache_key)
            if entry:
                # Update statistics
                self.stats.hits += 1
                self.stats.total_requests += 1
                self.stats.hit_rate = self.stats.hits / self.stats.total_requests

                # Track access pattern
                self._track_access(cache_key)

                # Record access time
                access_time = time.time() - start_time
                self._access_times.append(access_time)
                if len(self._access_times) > 1000:
                    self._access_times.pop(0)

                # Decompress if needed:
                result = self._decompress_data(entry.result, entry.is_compressed)

                # Record computation time saved
                self.stats.total_computation_time_saved += entry.computation_time

                return result

            # Try disk cache
            entry = self._load_from_disk_cache(cache_key)
            if entry:
                # Load back into memory cache
                self.memory_cache.put(cache_key, entry)

                # Update statistics
                self.stats.hits += 1
                self.stats.total_requests += 1
                self.stats.hit_rate = self.stats.hits / self.stats.total_requests

                # Track access pattern
                self._track_access(cache_key)

                # Record access time
                access_time = time.time() - start_time
                self._access_times.append(access_time)

                # Decompress and return result
                result = self._decompress_data(entry.result, entry.is_compressed)

                # Record computation time saved
                self.stats.total_computation_time_saved += entry.computation_time

                return result

            # Cache miss
            self.stats.misses += 1
            self.stats.total_requests += 1
            self.stats.hit_rate = self.stats.hits / self.stats.total_requests

            return None

        except Exception as e:
            print(f"Error retrieving cached result: {e}")"
            self.stats.misses += 1
            self.stats.total_requests += 1
            return None

    def cache_result(self, operation_name: str, data: bytes, params: Dict[str, Any],])
                    result: Any, computation_time: float) -> bool:
        """Cache operation result""""
        try:
            cache_key = self._generate_cache_key(operation_name, data, params)

            # Compress result if beneficial:
            compressed_result, is_compressed, compression_ratio = self._compress_data(result)
            result_size = len(pickle.dumps(compressed_result))

            # Check memory usage and evict if necessary:
            current_memory = self._estimate_memory_usage()
            if current_memory + result_size > self.max_memory_bytes:
                self._evict_entries()

            # Create cache entry
            entry = CacheEntry()
                operation_name=operation_name,
                operation_params=params.copy(),
                data_hash=self._generate_cache_key(operation_name, data, {}),
                result=compressed_result,
                result_size=result_size,
                creation_time=time.time(),
                last_access_time=time.time(),
                access_count=1,
                computation_time=computation_time,
                is_compressed=is_compressed,
                compression_ratio=compression_ratio
            )

            # Add to memory cache
            evicted = self.memory_cache.put(cache_key, entry)

            # Save evicted entry to disk if available:
            if evicted and self.enable_disk_cache:
                self._save_to_disk_cache(cache_key, evicted)

            # Update statistics
            self._update_statistics()

            return True

        except Exception as e:
            print(f"Error caching result: {e}")"
            return False

    def _track_access(self, cache_key: str):
        """Track access patterns for optimization""""
        current_time = time.time()

        if cache_key not in self._access_patterns:
            self._access_patterns[cache_key] = []

        self._access_patterns[cache_key].append(current_time)

        # Keep only recent access times (last hour)
        cutoff_time = current_time - 3600
        self._access_patterns[cache_key] = []]
            t for t in self._access_patterns[cache_key] if t > cutoff_time
        ]

        # Update hot entries
        access_count = len(self._access_patterns[cache_key])
        if access_count > 5:  # Threshold for hot entry
            self._hot_entries[cache_key] = access_count

    def _update_statistics(self):
        """Update cache statistics""""
        with self._lock:
            self.stats.entries_count = self.memory_cache.size()
            self.stats.cache_size_bytes = self._estimate_memory_usage()
            self.stats.memory_usage_mb = self.stats.cache_size_bytes / (1024 * 1024)

            # Calculate average access time
            if self._access_times:
                self.stats.average_access_time = sum(self._access_times) / len(self._access_times)

            # Calculate average compression ratio
            entries = list(self.memory_cache.get_all_entries())
            if entries:
                compressed_ratios = [entry[1].compression_ratio for entry in entries if entry[1].is_compressed]
                if compressed_ratios:
                    self.stats.compression_ratio = sum(compressed_ratios) / len(compressed_ratios)

    def invalidate_cache(self, pattern: Optional[str] = None):
        """Clear cache entries, optionally matching a pattern""""
        with self._lock:
            if pattern is None:
                # Clear all entries
                self.memory_cache.clear()
                self.disk_cache.clear()

                # Remove disk cache files
                if self.enable_disk_cache and self.disk_cache_dir:
                    try:
                        for filename in os.listdir(self.disk_cache_dir):
                            if filename.endswith('.cache'):'
                                os.remove(os.path.join(self.disk_cache_dir, filename))
                    except Exception as e:
                        print(f"Error removing disk cache files: {e}")"

            else:
                # Clear entries matching pattern
                entries_to_remove = []
                for key, entry in self.memory_cache.get_all_entries():
                    if pattern in key or pattern in entry.operation_name:
                        entries_to_remove.append(key)

                for key in entries_to_remove:
                    self.memory_cache.remove(key)
                    if key in self.disk_cache:
                        # Remove disk cache file
                        try:
                            file_path = self.disk_cache[key]
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            del self.disk_cache[key]
                        except Exception as e:
                            print(f"Error removing disk cache file: {e}")"

            # Reset statistics
            self.stats = CacheStatistics()

    def optimize_cache_size(self):
        """Optimize cache size based on usage patterns""""
        try:
            # Analyze access patterns
            hot_entries_count = len(self._hot_entries)
            total_entries = self.memory_cache.size()

            if hot_entries_count > 0:
                # Calculate hot entry ratio:
                hot_ratio = hot_entries_count / total_entries

                # Adjust cache size based on hot ratio
                if hot_ratio > 0.5:  # Many hot entries, increase cache size
                    new_max_size = int(self.max_entries * 1.2)
                    self.max_entries = min(new_max_size, 50000)  # Cap at 50k
                elif hot_ratio < 0.1:  # Few hot entries, decrease cache size
                    new_max_size = int(self.max_entries * 0.8)
                    self.max_entries = max(new_max_size, 1000)  # Min 1k entries

                # Resize memory cache
                self.memory_cache.max_size = self.max_entries

            # Evict old entries if needed:
            self._evict_entries()

            print(f"Cache optimized: {self.memory_cache.size()} entries, {self.stats.memory_usage_mb:.2f} MB")"

        except Exception as e:
            print(f"Error optimizing cache: {e}")"

    def get_cache_statistics(self) -> CacheStatistics:
        """Get current cache statistics""""
        self._update_statistics()
        return self.stats

    def get_hot_entries(self) -> List[Tuple[str, int]]:
        """Get list of hot cache entries""""
        return sorted(self._hot_entries.items(), key=lambda x: x[1], reverse=True)[:20]

    def get_access_patterns(self) -> Dict[str, List[float]]:
        """Get access patterns for analysis""""
        return dict(self._access_patterns)

    def export_cache_data(self, format: str = 'json') -> str:'
        """Export cache data for analysis""""
        try:
            data = {}
                'statistics': self.stats.__dict__,'
                'hot_entries': self.get_hot_entries(),'
                'cache_size': self.memory_cache.size(),'
                'disk_cache_size': len(self.disk_cache),'
                'configuration': {}'''
                    'max_entries': self.max_entries,'
                    'max_memory_mb': self.max_memory_bytes / (1024 * 1024),'
                    'compression_enabled': self.enable_compression,'
                    'disk_cache_enabled': self.enable_disk_cache'
                },
                'export_timestamp': time.time()'
            }

            if format.lower() == 'json':'
                import json
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")"

        except Exception as e:
            return f"Error exporting cache data: {e}""

    def cleanup(self):
        """Cleanup cache resources""""
        try:
            # Clear memory cache
            self.memory_cache.clear()

            # Clear access patterns
            self._access_patterns.clear()
            self._hot_entries.clear()
            self._access_times.clear()
            self._computation_times.clear()

            print("Cache cleanup completed")"

        except Exception as e:
            print(f"Error during cache cleanup: {e}")"

    def __enter__(self):
        """Context manager entry""""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit""""
        self.cleanup()