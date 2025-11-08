"""
Performance Monitor Core
Real-time collection and analysis of performance metrics for BSEE
"""

import time
import threading
import psutil
import queue
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import gc
import os


@dataclass
class SystemMetrics:
    """System-level performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_rss_mb: float
    memory_vms_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    thread_count: int
    process_count: int
    load_average: Optional[List[float]] = None


@dataclass
class OperationMetrics:
    """Application-specific operation metrics"""
    timestamp: float
    operations_per_second: float
    strategy_execution_time: float
    metric_calculation_time: float
    cache_hit_rate: float
    cache_miss_rate: float
    memory_allocated_mb: float
    active_operations: int
    queued_operations: int


@dataclass
class StrategyMetrics:
    """Strategy-specific performance metrics"""
    strategy_name: str
    timestamp: float
    operations_count: int
    average_execution_time: float
    success_rate: float
    best_score: float
    convergence_rate: float
    memory_usage_mb: float


@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot at a point in time"""
    timestamp: float
    system: SystemMetrics
    operations: OperationMetrics
    strategies: Dict[str, StrategyMetrics]
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Real-time performance monitoring system"""

    def __init__(self, collection_interval: float = 1.0, history_size: int = 60):
        self.collection_interval = collection_interval
        self.history_size = history_size

        # Data storage
        self.metrics_history = deque(maxlen=history_size)
        self.operation_times = deque(maxlen=1000)
        self.strategy_performance = {}
        self.custom_metrics = {}

        # Threading and synchronization
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.RLock()
        self._metrics_queue = queue.Queue()

        # Performance counters
        self._operation_count = 0
        self._total_operation_time = 0.0
        self._cache_hits = 0
        self._cache_misses = 0
        self._last_collection_time = time.time()

        # Process handle
        self.process = psutil.Process()
        self.initial_process = psutil.Process()

        # Callbacks
        self.callbacks = {
            'metrics_collected': [],
            'alert_triggered': [],
            'performance_threshold_exceeded': []
        }

        # Performance baselines
        self.baseline_metrics = None
        self.performance_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'operations_per_second': 1.0,
            'strategy_execution_time': 5.0
        }

    def start_monitoring(self):
        """Begin background performance collection"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        print("Performance monitoring started")

    def stop_monitoring(self):
        """Stop background performance collection"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        print("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop running in background thread"""
        while self._monitoring:
            try:
                # Collect all metrics
                snapshot = self.collect_metrics_snapshot()

                # Store in history
                with self._lock:
                    self.metrics_history.append(snapshot)

                # Trigger callbacks
                self._trigger_callbacks('metrics_collected', snapshot)

                # Check for performance alerts
                self._check_performance_alerts(snapshot)

                # Sleep until next collection
                time.sleep(self.collection_interval)

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory metrics
            memory_info = self.process.memory_info()
            memory_rss_mb = memory_info.rss / 1024 / 1024
            memory_vms_mb = memory_info.vms / 1024 / 1024
            memory_percent = self.process.memory_percent()

            # Disk I/O metrics
            io_counters = self.process.io_counters()
            disk_io_read_mb = io_counters.read_bytes / 1024 / 1024
            disk_io_write_mb = io_counters.write_bytes / 1024 / 1024

            # Thread and process counts
            thread_count = self.process.num_threads()
            process_count = len(psutil.pids())

            # Load average (Unix systems)
            load_average = None
            try:
                load_average = list(os.getloadavg())
            except AttributeError:
                # Windows doesn't have load average
                pass

            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_rss_mb=memory_rss_mb,
                memory_vms_mb=memory_vms_mb,
                memory_percent=memory_percent,
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb,
                thread_count=thread_count,
                process_count=process_count,
                load_average=load_average
            )

        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            # Return empty metrics on error
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0, memory_rss_mb=0.0, memory_vms_mb=0.0,
                memory_percent=0.0, disk_io_read_mb=0.0, disk_io_write_mb=0.0,
                thread_count=0, process_count=0
            )

    def collect_operation_metrics(self) -> OperationMetrics:
        """Collect application-specific operation metrics"""
        try:
            current_time = time.time()
            time_delta = current_time - self._last_collection_time

            # Calculate operations per second
            if time_delta > 0:
                operations_per_second = self._operation_count / time_delta
            else:
                operations_per_second = 0.0

            # Reset counters
            self._operation_count = 0
            self._last_collection_time = current_time

            # Calculate average strategy execution time
            if len(self.operation_times) > 0:
                avg_execution_time = sum(self.operation_times) / len(self.operation_times)
            else:
                avg_execution_time = 0.0

            # Calculate cache hit/miss rates
            total_cache_requests = self._cache_hits + self._cache_misses
            if total_cache_requests > 0:
                cache_hit_rate = (self._cache_hits / total_cache_requests) * 100
                cache_miss_rate = (self._cache_misses / total_cache_requests) * 100
            else:
                cache_hit_rate = 0.0
                cache_miss_rate = 0.0

            # Memory allocation estimation
            memory_allocated_mb = gc.get_stats()[0].get('collections', 0) * 0.1  # Rough estimate

            return OperationMetrics(
                timestamp=current_time,
                operations_per_second=operations_per_second,
                strategy_execution_time=avg_execution_time,
                metric_calculation_time=0.0,  # Would be populated by actual metric calculations
                cache_hit_rate=cache_hit_rate,
                cache_miss_rate=cache_miss_rate,
                memory_allocated_mb=memory_allocated_mb,
                active_operations=0,  # Would be populated by operation tracking
                queued_operations=0
            )

        except Exception as e:
            print(f"Error collecting operation metrics: {e}")
            return OperationMetrics(
                timestamp=time.time(),
                operations_per_second=0.0, strategy_execution_time=0.0,
                metric_calculation_time=0.0, cache_hit_rate=0.0,
                cache_miss_rate=0.0, memory_allocated_mb=0.0,
                active_operations=0, queued_operations=0
            )

    def collect_strategy_metrics(self) -> Dict[str, StrategyMetrics]:
        """Collect strategy-specific performance metrics"""
        with self._lock:
            # Return copy of current strategy metrics
            return dict(self.strategy_performance)

    def collect_metrics_snapshot(self) -> PerformanceSnapshot:
        """Collect complete performance snapshot"""
        return PerformanceSnapshot(
            timestamp=time.time(),
            system=self.collect_system_metrics(),
            operations=self.collect_operation_metrics(),
            strategies=self.collect_strategy_metrics(),
            custom_metrics=dict(self.custom_metrics)
        )

    def record_operation_execution(self, operation_name: str, execution_time: float):
        """Record operation execution for performance tracking"""
        with self._lock:
            self._operation_count += 1
            self.operation_times.append(execution_time)
            self._total_operation_time += execution_time

    def record_cache_hit(self):
        """Record a cache hit for performance tracking"""
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self):
        """Record a cache miss for performance tracking"""
        with self._lock:
            self._cache_misses += 1

    def record_strategy_performance(self, strategy_name: str, metrics: Dict[str, Any]):
        """Record strategy-specific performance metrics"""
        with self._lock:
            self.strategy_performance[strategy_name] = StrategyMetrics(
                strategy_name=strategy_name,
                timestamp=time.time(),
                operations_count=metrics.get('operations_count', 0),
                average_execution_time=metrics.get('average_execution_time', 0.0),
                success_rate=metrics.get('success_rate', 0.0),
                best_score=metrics.get('best_score', 0.0),
                convergence_rate=metrics.get('convergence_rate', 0.0),
                memory_usage_mb=metrics.get('memory_usage_mb', 0.0)
            )

    def add_custom_metric(self, name: str, value: Any):
        """Add a custom metric for tracking"""
        with self._lock:
            self.custom_metrics[name] = value

    def get_real_time_metrics(self) -> Optional[PerformanceSnapshot]:
        """Return current metrics snapshot"""
        return self.collect_metrics_snapshot()

    def get_metrics_history(self, duration_seconds: float = None) -> List[PerformanceSnapshot]:
        """Get historical metrics within specified duration"""
        with self._lock:
            if duration_seconds is None:
                return list(self.metrics_history)

            cutoff_time = time.time() - duration_seconds
            return [snapshot for snapshot in self.metrics_history
                   if snapshot.timestamp >= cutoff_time]

    def calculate_performance_statistics(self, duration_seconds: float = 60.0) -> Dict[str, Any]:
        """Generate performance summary statistics"""
        history = self.get_metrics_history(duration_seconds)

        if not history:
            return {}

        # System statistics
        cpu_values = [snapshot.system.cpu_percent for snapshot in history]
        memory_values = [snapshot.system.memory_percent for snapshot in history]
        ops_values = [snapshot.operations.operations_per_second for snapshot in history]

        system_stats = {
            'cpu_average': sum(cpu_values) / len(cpu_values),
            'cpu_max': max(cpu_values),
            'memory_average': sum(memory_values) / len(memory_values),
            'memory_max': max(memory_values),
            'operations_per_second_average': sum(ops_values) / len(ops_values),
            'operations_per_second_max': max(ops_values),
            'data_points': len(history)
        }

        # Strategy statistics
        strategy_stats = {}
        for snapshot in history:
            for strategy_name, strategy_metrics in snapshot.strategies.items():
                if strategy_name not in strategy_stats:
                    strategy_stats[strategy_name] = {
                        'execution_times': [],
                        'success_rates': [],
                        'scores': []
                    }

                strategy_stats[strategy_name]['execution_times'].append(
                    strategy_metrics.average_execution_time
                )
                strategy_stats[strategy_name]['success_rates'].append(
                    strategy_metrics.success_rate
                )
                strategy_stats[strategy_name]['scores'].append(
                    strategy_metrics.best_score
                )

        # Calculate strategy averages
        for strategy_name, stats in strategy_stats.items():
            stats['average_execution_time'] = (
                sum(stats['execution_times']) / len(stats['execution_times'])
                if stats['execution_times'] else 0.0
            )
            stats['average_success_rate'] = (
                sum(stats['success_rates']) / len(stats['success_rates'])
                if stats['success_rates'] else 0.0
            )
            stats['average_score'] = (
                sum(stats['scores']) / len(stats['scores'])
                if stats['scores'] else 0.0
            )

        return {
            'system_performance': system_stats,
            'strategy_performance': strategy_stats,
            'collection_duration': duration_seconds,
            'analysis_timestamp': time.time()
        }

    def set_performance_thresholds(self, **thresholds):
        """Set performance thresholds for alerting"""
        self.performance_thresholds.update(thresholds)

    def _check_performance_alerts(self, snapshot: PerformanceSnapshot):
        """Check for performance threshold violations"""
        alerts = []

        # CPU alert
        if snapshot.system.cpu_percent > self.performance_thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"High CPU usage: {snapshot.system.cpu_percent:.1f}%",
                'value': snapshot.system.cpu_percent,
                'threshold': self.performance_thresholds['cpu_percent']
            })

        # Memory alert
        if snapshot.system.memory_percent > self.performance_thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f"High memory usage: {snapshot.system.memory_percent:.1f}%",
                'value': snapshot.system.memory_percent,
                'threshold': self.performance_thresholds['memory_percent']
            })

        # Operations per second alert
        if (snapshot.operations.operations_per_second <
            self.performance_thresholds['operations_per_second']):
            alerts.append({
                'type': 'low_ops_rate',
                'severity': 'warning',
                'message': f"Low operations rate: {snapshot.operations.operations_per_second:.2f} ops/sec",
                'value': snapshot.operations.operations_per_second,
                'threshold': self.performance_thresholds['operations_per_second']
            })

        # Trigger alert callbacks
        for alert in alerts:
            self._trigger_callbacks('alert_triggered', alert)
            self._trigger_callbacks('performance_threshold_exceeded', alert)

    def add_callback(self, event_type: str, callback: Callable):
        """Add callback function for monitoring events"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger all callbacks for a specific event type"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Error in performance monitor callback: {e}")

    def reset_metrics(self):
        """Reset all performance counters"""
        with self._lock:
            self._operation_count = 0
            self._total_operation_time = 0.0
            self._cache_hits = 0
            self._cache_misses = 0
            self.operation_times.clear()
            self.strategy_performance.clear()
            self.custom_metrics.clear()
            self.metrics_history.clear()

    def get_current_process_info(self) -> Dict[str, Any]:
        """Get detailed current process information"""
        try:
            return {
                'pid': self.process.pid,
                'name': self.process.name(),
                'cpu_percent': self.process.cpu_percent(),
                'memory_info': self.process.memory_info()._asdict(),
                'memory_percent': self.process.memory_percent(),
                'num_threads': self.process.num_threads(),
                'create_time': self.process.create_time(),
                'status': self.process.status(),
                'connections': len(self.process.connections()),
                'open_files': len(self.process.open_files())
            }
        except Exception as e:
            return {'error': str(e)}

    def export_metrics(self, format: str = 'json') -> str:
        """Export current metrics in specified format"""
        snapshot = self.get_real_time_metrics()
        stats = self.calculate_performance_statistics()

        if format.lower() == 'json':
            import json
            return json.dumps({
                'current_snapshot': snapshot.__dict__ if snapshot else None,
                'statistics': stats,
                'export_timestamp': time.time()
            }, indent=2, default=str)

        elif format.lower() == 'csv':
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(['Metric', 'Value', 'Unit'])

            if snapshot:
                # System metrics
                writer.writerow(['CPU Usage', snapshot.system.cpu_percent, '%'])
                writer.writerow(['Memory Usage', snapshot.system.memory_percent, '%'])
                writer.writerow(['Memory RSS', snapshot.system.memory_rss_mb, 'MB'])
                writer.writerow(['Operations/Sec', snapshot.operations.operations_per_second, 'ops/sec'])
                writer.writerow(['Cache Hit Rate', snapshot.operations.cache_hit_rate, '%'])

            return output.getvalue()

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def __enter__(self):
        """Context manager entry"""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()