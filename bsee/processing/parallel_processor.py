"""
Parallel Processing System
Parallel execution of operations and strategy evaluations for improved performance
"""

import time
import threading
import concurrent.futures
import queue
import multiprocessing
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import traceback
import gc
import psutil

from ..engine.operations import Operation
from ..engine.strategies import Strategy
from ..engine.state import BinaryState


class WorkerStatus(Enum):
    """Worker thread status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class TaskResult:
    """Result from a parallel task"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    worker_id: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class WorkerStatistics:
    """Statistics for a worker thread"""
    worker_id: str
    status: WorkerStatus
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_task_time: float = 0.0
    current_task: Optional[str] = None
    last_activity: float = 0.0
    error_count: int = 0
    memory_usage_mb: float = 0.0


class ParallelTask:
    """A task that can be executed in parallel"""

    def __init__(self, task_id: str, func: Callable, args: tuple = (), kwargs: dict = None,
                 timeout: Optional[float] = None, priority: int = 0):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.timeout = timeout
        self.priority = priority
        self.created_time = time.time()
        self.started_time = None
        self.completed_time = None

    def execute(self) -> TaskResult:
        """Execute the task and return result"""
        start_time = time.time()
        self.started_time = start_time

        try:
            # Execute the function
            if self.timeout:
                # Note: Actual timeout implementation would require more complex logic
                result = self.func(*self.args, **self.kwargs)
            else:
                result = self.func(*self.args, **self.kwargs)

            end_time = time.time()
            self.completed_time = end_time

            return TaskResult(
                task_id=self.task_id,
                success=True,
                result=result,
                execution_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time
            )

        except Exception as e:
            end_time = time.time()
            self.completed_time = end_time

            return TaskResult(
                task_id=self.task_id,
                success=False,
                error=e,
                execution_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time
            )


class WorkerThread:
    """Worker thread for executing parallel tasks"""

    def __init__(self, worker_id: str, task_queue: queue.Queue, result_queue: queue.Queue):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.statistics = WorkerStatistics(worker_id=worker_id, status=WorkerStatus.IDLE)
        self._running = False
        self._thread = None
        self._process = psutil.Process()

    def start(self):
        """Start the worker thread"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Stop the worker thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self.statistics.status = WorkerStatus.STOPPED

    def _worker_loop(self):
        """Main worker loop"""
        self.statistics.status = WorkerStatus.IDLE
        self.statistics.last_activity = time.time()

        while self._running:
            try:
                # Get task from queue (with timeout to allow checking _running)
                try:
                    task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Update statistics
                self.statistics.status = WorkerStatus.BUSY
                self.statistics.current_task = task.task_id
                self.statistics.last_activity = time.time()

                # Execute task
                result = task.execute()
                result.worker_id = self.worker_id

                # Update statistics
                if result.success:
                    self.statistics.tasks_completed += 1
                else:
                    self.statistics.tasks_failed += 1
                    self.statistics.error_count += 1

                self.statistics.total_execution_time += result.execution_time
                if self.statistics.tasks_completed > 0:
                    self.statistics.average_task_time = (
                        self.statistics.total_execution_time / self.statistics.tasks_completed
                    )

                # Update memory usage
                try:
                    memory_info = self._process.memory_info()
                    self.statistics.memory_usage_mb = memory_info.rss / 1024 / 1024
                except:
                    pass

                # Put result in result queue
                self.result_queue.put(result)

                # Reset status
                self.statistics.status = WorkerStatus.IDLE
                self.statistics.current_task = None
                self.statistics.last_activity = time.time()

                # Mark task as done
                self.task_queue.task_done()

            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")
                self.statistics.status = WorkerStatus.ERROR
                self.statistics.error_count += 1

        self.statistics.status = WorkerStatus.STOPPED


class ThreadPool:
    """Custom thread pool with enhanced monitoring and control"""

    def __init__(self, max_workers: Optional[int] = None):
        if max_workers is None:
            max_workers = min(32, (multiprocessing.cpu_count() or 1) + 4)

        self.max_workers = max_workers
        self.task_queue = queue.PriorityQueue()  # Priority queue for tasks
        self.result_queue = queue.Queue()
        self.workers = []

        # Statistics
        self.total_tasks_submitted = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0

        # Start workers
        self._start_workers()

    def _start_workers(self):
        """Start worker threads"""
        for i in range(self.max_workers):
            worker = WorkerThread(f"worker-{i}", self.task_queue, self.result_queue)
            worker.start()
            self.workers.append(worker)

    def submit_task(self, task: ParallelTask) -> str:
        """Submit a task for execution"""
        # Use negative priority for max-heap behavior (higher priority first)
        priority_key = (-task.priority, task.created_time)
        self.task_queue.put((priority_key, task))
        self.total_tasks_submitted += 1
        return task.task_id

    def submit_function(self, func: Callable, args: tuple = (), kwargs: dict = None,
                       task_id: Optional[str] = None, timeout: Optional[float] = None,
                       priority: int = 0) -> str:
        """Submit a function for execution"""
        if task_id is None:
            task_id = f"task-{int(time.time() * 1000000)}-{id(func)}"

        task = ParallelTask(task_id, func, args, kwargs, timeout, priority)
        return self.submit_task(task)

    def get_result(self, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """Get a result from the result queue"""
        try:
            result = self.result_queue.get(timeout=timeout)
            if result.success:
                self.total_tasks_completed += 1
            else:
                self.total_tasks_failed += 1
            return result
        except queue.Empty:
            return None

    def get_all_results(self, timeout: Optional[float] = None) -> List[TaskResult]:
        """Get all available results"""
        results = []
        while True:
            result = self.get_result(timeout=0.1)  # Short timeout
            if result is None:
                break
            results.append(result)
        return results

    def wait_for_completion(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, TaskResult]:
        """Wait for specific tasks to complete"""
        results = {}
        start_time = time.time()
        remaining_tasks = set(task_ids)

        while remaining_tasks and (timeout is None or time.time() - start_time < timeout):
            result = self.get_result(timeout=0.5)
            if result and result.task_id in remaining_tasks:
                results[result.task_id] = result
                remaining_tasks.remove(result.task_id)

        return results

    def get_worker_statistics(self) -> List[WorkerStatistics]:
        """Get statistics for all workers"""
        return [worker.statistics for worker in self.workers]

    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get thread pool statistics"""
        worker_stats = self.get_worker_statistics()
        busy_workers = sum(1 for w in worker_stats if w.status == WorkerStatus.BUSY)
        idle_workers = sum(1 for w in worker_stats if w.status == WorkerStatus.IDLE)
        error_workers = sum(1 for w in worker_stats if w.status == WorkerStatus.ERROR)

        return {
            'total_workers': len(self.workers),
            'busy_workers': busy_workers,
            'idle_workers': idle_workers,
            'error_workers': error_workers,
            'total_tasks_submitted': self.total_tasks_submitted,
            'total_tasks_completed': self.total_tasks_completed,
            'total_tasks_failed': self.total_tasks_failed,
            'success_rate': (self.total_tasks_completed / max(self.total_tasks_submitted, 1)) * 100,
            'queue_size': self.task_queue.qsize(),
            'average_task_time': sum(w.average_task_time for w in worker_stats) / len(worker_stats) if worker_stats else 0,
            'total_memory_usage_mb': sum(w.memory_usage_mb for w in worker_stats)
        }

    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool"""
        # Stop workers
        for worker in self.workers:
            worker.stop()

        # Wait for workers to finish if requested
        if wait:
            for worker in self.workers:
                if worker._thread:
                    worker._thread.join(timeout=5.0)


class ParallelProcessor:
    """Main parallel processing system for BSEE"""

    def __init__(self, max_workers: Optional[int] = None, enable_load_balancing: bool = True):
        self.thread_pool = ThreadPool(max_workers)
        self.enable_load_balancing = enable_load_balancing

        # Load balancing
        self.worker_loads = {worker.worker_id: 0 for worker in self.thread_pool.workers}

        # Deadlock detection
        self._deadlock_check_interval = 30.0  # seconds
        self._last_deadlock_check = time.time()
        self._running_tasks = {}

    def evaluate_operations_parallel(self, state: BinaryState, operations: List[Operation],
                                   max_workers: Optional[int] = None) -> Dict[str, TaskResult]:
        """Evaluate multiple operations in parallel"""
        task_ids = []

        # Submit all operations for evaluation
        for operation in operations:
            def eval_op(op=operation):
                # Create a copy of the state for this operation
                state_copy = state.copy()
                try:
                    result_state = op.apply(state_copy)
                    score = self._calculate_score(result_state)
                    return {
                        'operation': op,
                        'result_state': result_state,
                        'score': score,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'operation': op,
                        'error': e,
                        'success': False
                    }

            task_id = self.thread_pool.submit_function(
                eval_op,
                task_id=f"eval_op_{operation.name}_{int(time.time() * 1000)}",
                priority=1
            )
            task_ids.append(task_id)

        # Wait for all operations to complete
        results = self.thread_pool.wait_for_completion(task_ids, timeout=60.0)

        return results

    def calculate_metrics_parallel(self, states: List[BinaryState], metric_names: List[str],
                                  max_workers: Optional[int] = None) -> Dict[str, Dict[str, TaskResult]]:
        """Calculate metrics for multiple states in parallel"""
        results = {state.get_id(): {} for state in states}

        # Submit metric calculations for each state
        task_mapping = {}

        for state in states:
            state_id = state.get_id()
            for metric_name in metric_names:
                def calc_metric(st=state, metric=metric_name):
                    try:
                        # This would call the actual metric calculation
                        from ..metrics.metrics import calculate_metric
                        value = calculate_metric(st.data, metric)
                        return {
                            'metric_name': metric,
                            'value': value,
                            'state_id': state_id,
                            'success': True
                        }
                    except Exception as e:
                        return {
                            'metric_name': metric,
                            'error': e,
                            'state_id': state_id,
                            'success': False
                        }

                task_id = self.thread_pool.submit_function(
                    calc_metric,
                    task_id=f"calc_metric_{state_id}_{metric_name}_{int(time.time() * 1000)}",
                    priority=0
                )
                task_mapping[task_id] = (state_id, metric_name)

        # Wait for all calculations to complete
        task_results = self.thread_pool.wait_for_completion(list(task_mapping.keys()), timeout=120.0)

        # Organize results
        for task_id, result in task_results.items():
            state_id, metric_name = task_mapping[task_id]
            results[state_id][metric_name] = result

        return results

    def run_strategy_parallel(self, strategy: Strategy, initial_states: List[BinaryState],
                            max_iterations: int = 100) -> Dict[str, TaskResult]:
        """Run strategy on multiple initial states in parallel"""
        task_ids = []

        for i, state in enumerate(initial_states):
            def run_strategy_single(s=state, strategy=strategy):
                try:
                    # Create a fresh copy of the strategy
                    strategy_copy = strategy.__class__(strategy.config)
                    result = strategy_copy.analyze(s, max_iterations)
                    return {
                        'initial_state_id': s.get_id(),
                        'result': result,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'initial_state_id': s.get_id(),
                        'error': e,
                        'success': False
                    }

            task_id = self.thread_pool.submit_function(
                run_strategy_single,
                task_id=f"strategy_{strategy.name}_{state.get_id()}_{int(time.time() * 1000)}",
                priority=2
            )
            task_ids.append(task_id)

        # Wait for all strategies to complete
        results = self.thread_pool.wait_for_completion(task_ids, timeout=300.0)

        return results

    def benchmark_operations_parallel(self, operations: List[Operation], test_data: List[bytes],
                                    iterations: int = 10) -> Dict[str, Dict[str, float]]:
        """Benchmark operations in parallel"""
        benchmark_results = {}

        for operation in operations:
            def benchmark_op(op=operation):
                times = []
                success_count = 0

                for data in test_data:
                    for _ in range(iterations):
                        start_time = time.time()
                        try:
                            state = BinaryState(data)
                            result_state = op.apply(state)
                            end_time = time.time()
                            times.append(end_time - start_time)
                            success_count += 1
                        except Exception:
                            times.append(float('inf'))

                return {
                    'operation_name': op.name,
                    'average_time': sum(t for t in times if t != float('inf')) / max(success_count, 1),
                    'min_time': min(t for t in times if t != float('inf')) if success_count > 0 else float('inf'),
                    'max_time': max(t for t in times if t != float('inf')) if success_count > 0 else float('inf'),
                    'success_rate': success_count / (len(test_data) * iterations) * 100,
                    'total_operations': len(test_data) * iterations
                }

            # Run benchmark for this operation
            task_id = self.thread_pool.submit_function(
                benchmark_op,
                task_id=f"benchmark_{operation.name}_{int(time.time() * 1000)}",
                priority=3
            )

            # Get result (blocking for benchmarks)
            result = self.thread_pool.wait_for_completion([task_id], timeout=600.0)
            if task_id in result:
                benchmark_results[operation.name] = result[task_id].result

        return benchmark_results

    def _calculate_score(self, state: BinaryState) -> float:
        """Calculate score for a state (placeholder)"""
        # This would integrate with the actual scoring system
        # For now, return a simple metric
        try:
            entropy = self._calculate_entropy(state.data)
            return entropy
        except:
            return 0.0

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate entropy of data"""
        if not data:
            return 0.0

        # Count byte frequencies
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1

        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for count in freq:
            if count > 0:
                p = count / data_len
                entropy -= p * (p.bit_length() - 1)  # Approximation of log2(p)

        return entropy

    def _detect_deadlocks(self):
        """Check for potential deadlocks"""
        current_time = time.time()
        if current_time - self._last_deadlock_check < self._deadlock_check_interval:
            return

        self._last_deadlock_check = current_time

        # Check for long-running tasks
        for task_id, start_time in list(self._running_tasks.items()):
            if current_time - start_time > 300:  # 5 minutes
                print(f"Warning: Long-running task detected: {task_id}")

        # Check for worker threads that are stuck
        worker_stats = self.thread_pool.get_worker_statistics()
        for worker in worker_stats:
            if (worker.status == WorkerStatus.BUSY and
                current_time - worker.last_activity > 600):  # 10 minutes
                print(f"Warning: Worker {worker.worker_id} may be stuck")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        pool_stats = self.thread_pool.get_pool_statistics()
        worker_stats = self.thread_pool.get_worker_statistics()

        # System information
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        return {
            'thread_pool': pool_stats,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3)
            },
            'workers': [
                {
                    'id': w.worker_id,
                    'status': w.status.value,
                    'tasks_completed': w.tasks_completed,
                    'tasks_failed': w.tasks_failed,
                    'average_task_time': w.average_task_time,
                    'memory_usage_mb': w.memory_usage_mb,
                    'current_task': w.current_task
                }
                for w in worker_stats
            ],
            'deadlock_check': {
                'last_check': self._last_deadlock_check,
                'running_tasks': len(self._running_tasks)
            }
        }

    def optimize_performance(self):
        """Optimize thread pool performance based on current load"""
        try:
            pool_stats = self.thread_pool.get_pool_statistics()
            system_status = self.get_system_status()

            # Adjust worker count based on load
            if (pool_stats['idle_workers'] / pool_stats['total_workers'] > 0.7 and
                system_status['system']['cpu_percent'] < 50):
                # Low utilization, could reduce workers
                print("Consider reducing worker count due to low utilization")

            elif (pool_stats['busy_workers'] / pool_stats['total_workers'] > 0.9 and
                  pool_stats['queue_size'] > 10):
                # High utilization and queue buildup, could increase workers
                print("Consider increasing worker count due to high utilization")

            # Check for memory usage
            total_memory_mb = sum(w.memory_usage_mb for w in self.thread_pool.get_worker_statistics())
            if total_memory_mb > 1024:  # 1GB
                print("High memory usage detected, consider reducing concurrent tasks")

            # Trigger garbage collection
            gc.collect()

        except Exception as e:
            print(f"Error optimizing performance: {e}")

    def shutdown(self):
        """Shutdown the parallel processor"""
        self.thread_pool.shutdown(wait=True)
        print("Parallel processor shutdown completed")