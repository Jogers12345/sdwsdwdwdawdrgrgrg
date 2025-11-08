"""
Metrics Calculation Cache
Cache expensive metric calculations for improved performance
"""

import time
import threading
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from collections import OrderedDict
import pickle
import math

from .operation_cache import LRUCache, CacheStatistics


@dataclass
class MetricType:
    """Definition of a metric type with caching parameters"""
    name: str
    cacheable: bool = True
    ttl_seconds: float = float('inf')  # Time to live
    max_age_seconds: float = 3600.0    # Maximum age before recalculation
    priority: int = 1                  # Priority for eviction (higher = less likely to evict)
    size_weight: float = 1.0          # Relative size weight for memory management
    recomputation_cost: float = 1.0    # Relative cost of recomputation


@dataclass
class MetricCacheEntry:
    """Cache entry for metric calculation result"""
    metric_name: str
    data_hash: str
    parameters_hash: str
    result: Any
    result_size: int
    creation_time: float
    last_access_time: float
    access_count: int
    calculation_time: float
    ttl: float
    metric_type: MetricType
    is_valid: bool = True
    validation_data: Optional[Dict[str, Any]] = None


@dataclass
class MetricCacheStatistics:
    """Statistics for metrics cache"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    expired_entries: int = 0
    invalidated_entries: int = 0
    total_calculation_time_saved: float = 0.0
    cache_size_bytes: int = 0
    memory_usage_mb: float = 0.0
    hit_rate: float = 0.0
    entries_by_metric: Dict[str, int] = field(default_factory=dict)
    average_calculation_time: float = 0.0


class MetricsCache:
    """Specialized cache for expensive metric calculations"""

    def __init__(self, max_entries: int = 5000, max_memory_mb: float = 256.0):
        self.max_entries = max_entries
        self.max_memory_bytes = max_memory_mb * 1024 * 1024

        # Cache storage
        self._cache: OrderedDict[str, MetricCacheEntry] = OrderedDict()
        self._lock = threading.RLock()

        # Metric type definitions
        self.metric_types = self._initialize_metric_types()

        # Statistics
        self.stats = MetricCacheStatistics()

        # Background cleanup thread
        self._cleanup_running = False
        self._cleanup_thread = None

        # Validation callbacks
        self._validation_callbacks: Dict[str, Callable] = {}

        # Start background cleanup
        self.start_background_cleanup()

    def _initialize_metric_types(self) -> Dict[str, MetricType]:
        """Initialize predefined metric types"""
        return {
            # File-level metrics
            'entropy': MetricType('entropy', ttl_seconds=float('inf'), priority=3, size_weight=1.0),
            'ideality': MetricType('ideality', ttl_seconds=float('inf'), priority=3, size_weight=1.2),
            'compression_ratio': MetricType('compression_ratio', ttl_seconds=300.0, priority=2, size_weight=0.8),
            'file_size': MetricType('file_size', cacheable=False),  # Very cheap to calculate

            # Window-based metrics
            'window_entropy': MetricType('window_entropy', ttl_seconds=1800.0, priority=2, size_weight=2.0),
            'window_ideality': MetricType('window_ideality', ttl_seconds=1800.0, priority=2, size_weight=2.2),
            'local_variance': MetricType('local_variance', ttl_seconds=600.0, priority=1, size_weight=1.5),

            # Pattern analysis metrics
            'pattern_frequency': MetricType('pattern_frequency', ttl_seconds=3600.0, priority=2, size_weight=3.0),
            'byte_distribution': MetricType('byte_distribution', ttl_seconds=3600.0, priority=2, size_weight=2.0),
            'repeating_patterns': MetricType('repeating_patterns', ttl_seconds=7200.0, priority=3, size_weight=2.5),

            # Advanced metrics
            'lz77_complexity': MetricType('lz77_complexity', ttl_seconds=1800.0, priority=3, size_weight=1.8),
            'dct_coefficients': MetricType('dct_coefficients', ttl_seconds=2400.0, priority=3, size_weight=2.0),
            'fourier_spectrum': MetricType('fourier_spectrum', ttl_seconds=2400.0, priority=2, size_weight=2.5),

            # Statistical metrics
            'correlation_matrix': MetricType('correlation_matrix', ttl_seconds=1800.0, priority=2, size_weight=1.5),
            'autocorrelation': MetricType('autocorrelation', ttl_seconds=1200.0, priority=2, size_weight=1.8),
            'runs_test': MetricType('runs_test', ttl_seconds=900.0, priority=1, size_weight=1.2),

            # Custom metrics (user-defined)
            'custom': MetricType('custom', ttl_seconds=600.0, priority=1, size_weight=1.0),
        }

    def register_metric_type(self, metric_type: MetricType):
        """Register a new metric type"""
        self.metric_types[metric_type.name] = metric_type

    def register_validation_callback(self, metric_name: str, callback: Callable[[Any, Any], bool]):
        """Register validation callback for a metric"""
        self._validation_callbacks[metric_name] = callback

    def _generate_data_hash(self, data: bytes) -> str:
        """Generate hash for input data"""
        return hashlib.sha256(data).hexdigest()

    def _generate_parameters_hash(self, parameters: Dict[str, Any]) -> str:
        """Generate hash for calculation parameters"""
        # Sort parameters to ensure consistent hashing
        sorted_params = sorted(parameters.items())
        param_str = str(sorted_params)
        return hashlib.md5(param_str.encode()).hexdigest()

    def _generate_cache_key(self, metric_name: str, data_hash: str, parameters_hash: str) -> str:
        """Generate cache key for metric"""
        return f"{metric_name}:{data_hash}:{parameters_hash}"

    def _is_entry_expired(self, entry: MetricCacheEntry) -> bool:
        """Check if cache entry has expired"""
        current_time = time.time()

        # Check TTL
        if entry.ttl != float('inf') and (current_time - entry.creation_time) > entry.ttl:
            return True

        # Check maximum age
        if (current_time - entry.creation_time) > entry.metric_type.max_age_seconds:
            return True

        return False

    def _is_entry_valid(self, entry: MetricCacheEntry, data: bytes, parameters: Dict[str, Any]) -> bool:
        """Check if cached entry is still valid for current data"""
        # Check if entry is marked invalid
        if not entry.is_valid:
            return False

        # Check expiration
        if self._is_entry_expired(entry):
            return False

        # Run custom validation if available
        metric_name = entry.metric_name
        if metric_name in self._validation_callbacks:
            try:
                validation_result = self._validation_callbacks[metric_name](entry.result, data)
                if not validation_result:
                    entry.is_valid = False
                    return False
            except Exception as e:
                print(f"Error in validation callback for {metric_name}: {e}")
                return False

        return True

    def _estimate_entry_size(self, entry: MetricCacheEntry) -> int:
        """Estimate memory usage of cache entry"""
        base_size = 200  # Base overhead
        result_size = len(pickle.dumps(entry.result))
        return base_size + result_size

    def _evict_entries(self, target_memory: Optional[float] = None) -> int:
        """Evict entries based on priority and usage"""
        evicted_count = 0

        if target_memory is None:
            target_memory = self.max_memory_bytes * 0.8

        # Get entries sorted by eviction priority
        entries = list(self._cache.items())
        entries.sort(key=lambda x: self._calculate_eviction_score(x[1]), reverse=True)

        current_memory = self._estimate_memory_usage()

        for key, entry in entries:
            if current_memory <= target_memory:
                break

            # Don't evict high-priority entries unless necessary
            if entry.metric_type.priority >= 3 and current_memory < self.max_memory_bytes:
                continue

            del self._cache[key]
            current_memory -= self._estimate_entry_size(entry)
            evicted_count += 1
            self.stats.invalidated_entries += 1

        return evicted_count

    def _calculate_eviction_score(self, entry: MetricCacheEntry) -> float:
        """Calculate eviction score (higher = more likely to evict)"""
        current_time = time.time()
        age = current_time - entry.creation_time
        time_since_access = current_time - entry.last_access_time

        # Factors that increase eviction score (more likely to evict):
        # - Low priority
        # - Old age
        # - Haven't been accessed recently
        # - Low access count
        # - Large size

        priority_factor = 4.0 - entry.metric_type.priority  # Invert priority
        age_factor = min(age / 3600.0, 2.0)  # Age in hours, max 2.0
        access_factor = 1.0 / (1.0 + entry.access_count)  # Inverse of access count
        recent_access_factor = min(time_since_access / 1800.0, 2.0)  # 30 minutes max
        size_factor = entry.result_size / (1024 * 1024)  # Size in MB

        return (priority_factor * 0.3 +
                age_factor * 0.2 +
                access_factor * 0.2 +
                recent_access_factor * 0.2 +
                size_factor * 0.1)

    def _estimate_memory_usage(self) -> int:
        """Estimate total memory usage of cache"""
        total_size = 0
        for entry in self._cache.values():
            total_size += self._estimate_entry_size(entry)
        return total_size

    def _cleanup_expired_entries(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if self._is_entry_expired(entry):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
            self.stats.expired_entries += 1

        if expired_keys:
            print(f"Cleaned up {len(expired_keys)} expired metric cache entries")

    def _background_cleanup_loop(self):
        """Background thread for cache cleanup"""
        while self._cleanup_running:
            try:
                self._cleanup_expired_entries()

                # Check memory usage and evict if necessary
                current_memory = self._estimate_memory_usage()
                if current_memory > self.max_memory_bytes:
                    self._evict_entries()

                # Sleep for 60 seconds
                time.sleep(60)

            except Exception as e:
                print(f"Error in background cleanup: {e}")
                time.sleep(60)

    def start_background_cleanup(self):
        """Start background cleanup thread"""
        if not self._cleanup_running:
            self._cleanup_running = True
            self._cleanup_thread = threading.Thread(target=self._background_cleanup_loop, daemon=True)
            self._cleanup_thread.start()

    def stop_background_cleanup(self):
        """Stop background cleanup thread"""
        self._cleanup_running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)

    def get_cached_metric(self, metric_name: str, data: bytes, parameters: Dict[str, Any]) -> Optional[Any]:
        """Retrieve cached metric calculation result"""
        start_time = time.time()

        try:
            with self._lock:
                self.stats.total_requests += 1

                # Check if metric type is cacheable
                if metric_name not in self.metric_types or not self.metric_types[metric_name].cacheable:
                    self.stats.cache_misses += 1
                    return None

                # Generate cache key
                data_hash = self._generate_data_hash(data)
                params_hash = self._generate_parameters_hash(parameters)
                cache_key = self._generate_cache_key(metric_name, data_hash, params_hash)

                # Check cache
                if cache_key in self._cache:
                    entry = self._cache[cache_key]

                    # Validate entry
                    if self._is_entry_valid(entry, data, parameters):
                        # Update access statistics
                        entry.last_access_time = time.time()
                        entry.access_count += 1

                        # Move to end (most recently used)
                        self._cache.move_to_end(cache_key)

                        # Update statistics
                        self.stats.cache_hits += 1
                        self.stats.hit_rate = self.stats.cache_hits / self.stats.total_requests
                        self.stats.total_calculation_time_saved += entry.calculation_time

                        # Update metric statistics
                        if metric_name not in self.stats.entries_by_metric:
                            self.stats.entries_by_metric[metric_name] = 0
                        self.stats.entries_by_metric[metric_name] += 1

                        return entry.result
                    else:
                        # Remove invalid entry
                        del self._cache[cache_key]
                        self.stats.invalidated_entries += 1

                self.stats.cache_misses += 1
                self.stats.hit_rate = self.stats.cache_hits / self.stats.total_requests
                return None

        except Exception as e:
            print(f"Error retrieving cached metric: {e}")
            self.stats.cache_misses += 1
            return None

    def cache_metric_result(self, metric_name: str, data: bytes, parameters: Dict[str, Any],
                           result: Any, calculation_time: float) -> bool:
        """Cache metric calculation result"""
        try:
            with self._lock:
                # Check if metric type is cacheable
                if metric_name not in self.metric_types or not self.metric_types[metric_name].cacheable:
                    return False

                # Generate cache key
                data_hash = self._generate_data_hash(data)
                params_hash = self._generate_parameters_hash(parameters)
                cache_key = self._generate_cache_key(metric_name, data_hash, params_hash)

                # Estimate result size
                result_size = len(pickle.dumps(result))

                # Check memory usage and evict if necessary
                current_memory = self._estimate_memory_usage()
                if current_memory + result_size > self.max_memory_bytes:
                    self._evict_entries()

                # Get metric type
                metric_type = self.metric_types[metric_name]

                # Create cache entry
                entry = MetricCacheEntry(
                    metric_name=metric_name,
                    data_hash=data_hash,
                    parameters_hash=params_hash,
                    result=result,
                    result_size=result_size,
                    creation_time=time.time(),
                    last_access_time=time.time(),
                    access_count=1,
                    calculation_time=calculation_time,
                    ttl=metric_type.ttl_seconds,
                    metric_type=metric_type,
                    is_valid=True
                )

                # Add to cache
                self._cache[cache_key] = entry

                # Update statistics
                if metric_name not in self.stats.entries_by_metric:
                    self.stats.entries_by_metric[metric_name] = 0
                self.stats.entries_by_metric[metric_name] += 1

                return True

        except Exception as e:
            print(f"Error caching metric result: {e}")
            return False

    def invalidate_metric(self, metric_name: str, pattern: Optional[str] = None):
        """Invalidate cached metric entries"""
        try:
            with self._lock:
                if pattern is None:
                    # Invalidate all entries for this metric
                    keys_to_remove = [key for key in self._cache.keys()
                                     if key.startswith(f"{metric_name}:")]

                    for key in keys_to_remove:
                        del self._cache[key]
                        self.stats.invalidated_entries += 1

                else:
                    # Invalidate entries matching pattern
                    keys_to_remove = []
                    for key, entry in self._cache.items():
                        if (key.startswith(f"{metric_name}:") and
                            pattern.lower() in str(entry.result).lower()):
                            keys_to_remove.append(key)

                    for key in keys_to_remove:
                        del self._cache[key]
                        self.stats.invalidated_entries += 1

                print(f"Invalidated {len(keys_to_remove) if 'keys_to_remove' in locals() else 0} entries for metric: {metric_name}")

        except Exception as e:
            print(f"Error invalidating metric: {e}")

    def invalidate_all_metrics(self):
        """Clear all cached metrics"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self.stats.invalidated_entries += count
            print(f"Cleared {count} cached metric entries")

    def get_cache_statistics(self) -> MetricCacheStatistics:
        """Get current cache statistics"""
        with self._lock:
            # Update memory usage
            self.stats.cache_size_bytes = self._estimate_memory_usage()
            self.stats.memory_usage_mb = self.stats.cache_size_bytes / (1024 * 1024)

            # Calculate average calculation time
            total_calc_time = sum(entry.calculation_time for entry in self._cache.values())
            if self._cache:
                self.stats.average_calculation_time = total_calc_time / len(self._cache)

            return self.stats

    def get_metric_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed statistics for each metric type"""
        with self._lock:
            metric_stats = {}

            for metric_name, metric_type in self.metric_types.items():
                entries = [entry for entry in self._cache.values()
                          if entry.metric_name == metric_name]

                if entries:
                    total_accesses = sum(entry.access_count for entry in entries)
                    avg_calc_time = sum(entry.calculation_time for entry in entries) / len(entries)
                    total_size = sum(entry.result_size for entry in entries)
                    avg_age = sum(time.time() - entry.creation_time for entry in entries) / len(entries)

                    metric_stats[metric_name] = {
                        'entry_count': len(entries),
                        'total_accesses': total_accesses,
                        'average_accesses': total_accesses / len(entries),
                        'average_calculation_time': avg_calc_time,
                        'total_size_bytes': total_size,
                        'average_age_seconds': avg_age,
                        'priority': metric_type.priority,
                        'cacheable': metric_type.cacheable,
                        'ttl_seconds': metric_type.ttl_seconds
                    }
                else:
                    metric_stats[metric_name] = {
                        'entry_count': 0,
                        'total_accesses': 0,
                        'average_accesses': 0,
                        'average_calculation_time': 0,
                        'total_size_bytes': 0,
                        'average_age_seconds': 0,
                        'priority': metric_type.priority,
                        'cacheable': metric_type.cacheable,
                        'ttl_seconds': metric_type.ttl_seconds
                    }

            return metric_stats

    def optimize_cache(self):
        """Optimize cache based on usage patterns"""
        try:
            with self._lock:
                # Analyze metric usage patterns
                metric_stats = self.get_metric_statistics()

                # Identify underutilized metrics
                underutilized = []
                for metric_name, stats in metric_stats.items():
                    if stats['entry_count'] > 0:
                        access_ratio = stats['average_accesses']
                        if access_ratio < 0.5:  # Less than 0.5 accesses per entry
                            underutilized.append((metric_name, access_ratio))

                # Suggest configuration changes
                if underutilized:
                    print("Underutilized metrics (consider reducing TTL or disabling cache):")
                    for metric_name, access_ratio in sorted(underutilized, key=lambda x: x[1]):
                        print(f"  {metric_name}: {access_ratio:.2f} avg accesses")

                # Perform cleanup
                self._cleanup_expired_entries()

                # Evict old entries if memory pressure
                current_memory = self._estimate_memory_usage()
                if current_memory > self.max_memory_bytes * 0.9:
                    evicted = self._evict_entries()
                    print(f"Evicted {evicted} entries to reduce memory usage")

                print(f"Cache optimization completed: {len(self._cache)} entries, {self.stats.memory_usage_mb:.2f} MB")

        except Exception as e:
            print(f"Error optimizing cache: {e}")

    def export_cache_data(self, format: str = 'json') -> str:
        """Export cache statistics and configuration"""
        try:
            data = {
                'statistics': self.stats.__dict__,
                'metric_statistics': self.get_metric_statistics(),
                'configuration': {
                    'max_entries': self.max_entries,
                    'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                    'metric_types': {name: {
                        'cacheable': mt.cacheable,
                        'ttl_seconds': mt.ttl_seconds,
                        'priority': mt.priority,
                        'size_weight': mt.size_weight
                    } for name, mt in self.metric_types.items()}
                },
                'cache_entries': len(self._cache),
                'export_timestamp': time.time()
            }

            if format.lower() == 'json':
                import json
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            return f"Error exporting cache data: {e}"

    def cleanup(self):
        """Cleanup cache resources"""
        try:
            self.stop_background_cleanup()
            self.invalidate_all_metrics()
            self._cache.clear()
            print("Metrics cache cleanup completed")

        except Exception as e:
            print(f"Error during metrics cache cleanup: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()