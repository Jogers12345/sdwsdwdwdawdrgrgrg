"""
Performance Profiler
Built-in profiling for performance optimization and bottleneck identification
"""

import time
import cProfile
import pstats
import io
import threading
import traceback
import inspect
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import functools
import gc
import sys
import os

try:
    import memory_profiler
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False

try:
    import line_profiler
    LINE_PROFILER_AVAILABLE = True
except ImportError:
    LINE_PROFILER_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class FunctionProfile:
    """Profile data for a single function"""
    function_name: str
    module_name: str
    call_count: int = 0
    total_time: float = 0.0
    cumulative_time: float = 0.0
    average_time: float = 0.0
    per_call_time: float = 0.0
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0
    line_profile_data: Optional[Dict[int, float]] = None
    source_code: Optional[str] = None
    is_hot: bool = False
    is_bottleneck: bool = False


@dataclass
class StrategyProfile:
    """Profile data for a strategy"""
    strategy_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    convergence_rate: float = 0.0
    memory_usage_mb: float = 0.0
    operations_per_second: float = 0.0
    function_profiles: Dict[str, FunctionProfile] = field(default_factory=dict)


@dataclass
class ProfileSession:
    """A complete profiling session"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    duration: float = 0.0
    function_profiles: Dict[str, FunctionProfile] = field(default_factory=dict)
    strategy_profiles: Dict[str, StrategyProfile] = field(default_factory=dict)
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    memory_profile_data: Optional[List[Dict[str, Any]]] = None
    call_graph_data: Optional[Dict[str, Any]] = None


class FunctionProfiler:
    """Function-level performance profiler"""

    def __init__(self):
        self.function_times = defaultdict(list)
        self.function_calls = defaultdict(int)
        self.function_memory = defaultdict(list)
        self._lock = threading.RLock()
        self._enabled = False

    def start_profiling(self):
        """Start function profiling"""
        self._enabled = True

    def stop_profiling(self):
        """Stop function profiling"""
        self._enabled = False

    def profile_function(self, func_name: str = None):
        """Decorator for profiling functions"""
        def decorator(func):
            nonlocal func_name
            if func_name is None:
                func_name = f"{func.__module__}.{func.__qualname__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)

                # Start timing
                start_time = time.time()
                start_memory = self._get_memory_usage()

                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    result = e
                    success = False
                    raise
                finally:
                    # End timing
                    end_time = time.time()
                    end_memory = self._get_memory_usage()

                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory

                    # Record profiling data
                    with self._lock:
                        self.function_times[func_name].append(execution_time)
                        self.function_calls[func_name] += 1
                        self.function_memory[func_name].append(memory_delta)

                return result

            return wrapper
        return decorator

    def record_function_call(self, func_name: str, execution_time: float, memory_delta: float = 0.0):
        """Record a function call manually"""
        if self._enabled:
            with self._lock:
                self.function_times[func_name].append(execution_time)
                self.function_calls[func_name] += 1
                self.function_memory[func_name].append(memory_delta)

    def get_function_profiles(self) -> Dict[str, FunctionProfile]:
        """Get profile data for all functions"""
        profiles = {}

        with self._lock:
            for func_name, times in self.function_times.items():
                if not times:
                    continue

                call_count = self.function_calls[func_name]
                total_time = sum(times)
                average_time = total_time / len(times)
                per_call_time = total_time / call_count

                # Memory statistics
                memory_samples = self.function_memory.get(func_name, [])
                memory_usage = sum(memory_samples) / len(memory_samples) if memory_samples else 0.0
                peak_memory = max(memory_samples) if memory_samples else 0.0

                # Get source code
                try:
                    module_name, function_name = func_name.rsplit('.', 1)
                    module = sys.modules.get(module_name)
                    source_code = inspect.getsource(getattr(module, function_name, None)) if module else None
                except:
                    source_code = None

                profiles[func_name] = FunctionProfile(
                    function_name=function_name,
                    module_name=module_name if 'module_name' in locals() else 'unknown',
                    call_count=call_count,
                    total_time=total_time,
                    cumulative_time=total_time,
                    average_time=average_time,
                    per_call_time=per_call_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    source_code=source_code,
                    is_hot=call_count > 100,
                    is_bottleneck=average_time > 0.1  # More than 100ms
                )

        return profiles

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / (1024 * 1024)
            except:
                pass
        return 0.0

    def reset(self):
        """Reset all profiling data"""
        with self._lock:
            self.function_times.clear()
            self.function_calls.clear()
            self.function_memory.clear()


class StrategyProfiler:
    """Strategy-specific performance profiler"""

    def __init__(self):
        self.strategy_profiles = {}
        self._lock = threading.RLock()
        self._enabled = False

    def start_profiling(self):
        """Start strategy profiling"""
        self._enabled = True

    def stop_profiling(self):
        """Stop strategy profiling"""
        self._enabled = False

    def start_strategy_execution(self, strategy_name: str, strategy_config: Dict[str, Any]):
        """Start profiling a strategy execution"""
        if not self._enabled:
            return None

        execution_id = f"{strategy_name}_{int(time.time() * 1000000)}"

        with self._lock:
            if strategy_name not in self.strategy_profiles:
                self.strategy_profiles[strategy_name] = StrategyProfile(strategy_name=strategy_name)

        return {
            'execution_id': execution_id,
            'strategy_name': strategy_name,
            'start_time': time.time(),
            'start_memory': self._get_memory_usage()
        }

    def end_strategy_execution(self, execution_context: Dict[str, Any], success: bool = True,
                             convergence_info: Optional[Dict[str, Any]] = None):
        """End profiling a strategy execution"""
        if not self._enabled or execution_context is None:
            return

        end_time = time.time()
        end_memory = self._get_memory_usage()

        execution_time = end_time - execution_context['start_time']
        memory_delta = end_memory - execution_context['start_memory']
        strategy_name = execution_context['strategy_name']

        with self._lock:
            profile = self.strategy_profiles[strategy_name]
            profile.total_executions += 1

            if success:
                profile.successful_executions += 1
            else:
                profile.failed_executions += 1

            profile.total_time += execution_time
            profile.average_time = profile.total_time / profile.total_executions
            profile.min_time = min(profile.min_time, execution_time)
            profile.max_time = max(profile.max_time, execution_time)
            profile.memory_usage_mb += memory_delta

            # Calculate convergence rate if provided
            if convergence_info:
                convergence_rate = convergence_info.get('convergence_rate', 0.0)
                profile.convergence_rate = (
                    (profile.convergence_rate * (profile.successful_executions - 1) + convergence_rate) /
                    profile.successful_executions
                )

            # Calculate operations per second
            if execution_time > 0:
                ops_per_sec = convergence_info.get('operations_count', 0) / execution_time if convergence_info else 0
                profile.operations_per_second = (
                    (profile.operations_per_second * (profile.successful_executions - 1) + ops_per_sec) /
                    profile.successful_executions
                )

    def get_strategy_profiles(self) -> Dict[str, StrategyProfile]:
        """Get profile data for all strategies"""
        with self._lock:
            return dict(self.strategy_profiles)

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / (1024 * 1024)
            except:
                pass
        return 0.0

    def reset(self):
        """Reset all strategy profiling data"""
        with self._lock:
            self.strategy_profiles.clear()


class PerformanceProfiler:
    """Main performance profiling system"""

    def __init__(self, enable_system_profiling: bool = True):
        self.function_profiler = FunctionProfiler()
        self.strategy_profiler = StrategyProfiler()
        self.enable_system_profiling = enable_system_profiling

        # Profile sessions
        self.sessions = OrderedDict()
        self.current_session = None
        self._session_lock = threading.RLock()

        # cProfile integration
        self.cprofile_enabled = False
        self.cprofiler = None

        # Memory profiling
        self.memory_profile_enabled = False
        self.memory_samples = []

        # System monitoring
        self.system_monitoring_enabled = False
        self.system_metrics = []

        # Analysis results
        self.analysis_results = {}

    def start_profiling_session(self, session_id: Optional[str] = None) -> str:
        """Start a new profiling session"""
        if session_id is None:
            session_id = f"session_{int(time.time() * 1000)}"

        with self._session_lock:
            # End current session if active
            if self.current_session:
                self.end_profiling_session()

            # Create new session
            session = ProfileSession(
                session_id=session_id,
                start_time=time.time()
            )

            self.sessions[session_id] = session
            self.current_session = session

            # Start component profilers
            self.function_profiler.start_profiling()
            self.strategy_profiler.start_profiling()

            # Start system profiling if enabled
            if self.enable_system_profiling:
                self.start_system_profiling()

            # Start cProfile if enabled
            if self.cprofile_enabled:
                self.cprofiler = cProfile.Profile()
                self.cprofiler.enable()

            print(f"Started profiling session: {session_id}")
            return session_id

    def end_profiling_session(self) -> Optional[ProfileSession]:
        """End the current profiling session"""
        with self._session_lock:
            if not self.current_session:
                return None

            # End time
            end_time = time.time()
            self.current_session.end_time = end_time
            self.current_session.duration = end_time - self.current_session.start_time

            # Collect profiling data
            self.current_session.function_profiles = self.function_profiler.get_function_profiles()
            self.current_session.strategy_profiles = self.strategy_profiler.get_strategy_profiles()

            if self.system_monitoring_enabled:
                self.current_session.system_metrics = dict(self.system_metrics)

            if self.memory_profile_enabled:
                self.current_session.memory_profile_data = list(self.memory_samples)

            # Stop cProfile
            if self.cprofiler:
                self.cprofiler.disable()
                self.current_session.call_graph_data = self._process_cprofile_data()

            # Stop component profilers
            self.function_profiler.stop_profiling()
            self.strategy_profiler.stop_profiling()

            # Stop system profiling
            self.stop_system_profiling()

            session = self.current_session
            self.current_session = None

            # Analyze the session
            self._analyze_session(session)

            print(f"Ended profiling session: {session.session_id}")
            return session

    def start_system_profiling(self):
        """Start system resource monitoring"""
        self.system_monitoring_enabled = True
        self.system_metrics.clear()
        self._system_monitor_thread = threading.Thread(target=self._system_monitoring_loop, daemon=True)
        self._system_monitor_thread.start()

    def stop_system_profiling(self):
        """Stop system resource monitoring"""
        self.system_monitoring_enabled = False
        if hasattr(self, '_system_monitor_thread'):
            self._system_monitor_thread.join(timeout=2.0)

    def _system_monitoring_loop(self):
        """Background system monitoring loop"""
        while self.system_monitoring_enabled:
            try:
                if PSUTIL_AVAILABLE:
                    # CPU and memory metrics
                    cpu_percent = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    process = psutil.Process()

                    metrics = {
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available_mb': memory.available / (1024 * 1024),
                        'process_memory_mb': process.memory_info().rss / (1024 * 1024),
                        'process_cpu_percent': process.cpu_percent(),
                        'thread_count': process.num_threads()
                    }

                    self.system_metrics.append(metrics)

                    # Keep only last 1000 samples
                    if len(self.system_metrics) > 1000:
                        self.system_metrics.pop(0)

                time.sleep(1.0)  # Sample every second

            except Exception as e:
                print(f"Error in system monitoring: {e}")
                time.sleep(1.0)

    def start_memory_profiling(self):
        """Start memory profiling"""
        self.memory_profile_enabled = True
        self.memory_samples.clear()

        if MEMORY_PROFILER_AVAILABLE:
            # This would require more complex integration with memory_profiler
            pass

        self._memory_monitor_thread = threading.Thread(target=self._memory_monitoring_loop, daemon=True)
        self._memory_monitor_thread.start()

    def stop_memory_profiling(self):
        """Stop memory profiling"""
        self.memory_profile_enabled = False
        if hasattr(self, '_memory_monitor_thread'):
            self._memory_monitor_thread.join(timeout=2.0)

    def _memory_monitoring_loop(self):
        """Background memory monitoring loop"""
        while self.memory_profile_enabled:
            try:
                if PSUTIL_AVAILABLE:
                    process = psutil.Process()
                    memory_info = process.memory_info()

                    sample = {
                        'timestamp': time.time(),
                        'rss_mb': memory_info.rss / (1024 * 1024),
                        'vms_mb': memory_info.vms / (1024 * 1024),
                        'percent': process.memory_percent()
                    }

                    self.memory_samples.append(sample)

                    # Keep only last 1000 samples
                    if len(self.memory_samples) > 1000:
                        self.memory_samples.pop(0)

                time.sleep(0.5)  # Sample every 500ms

            except Exception as e:
                print(f"Error in memory monitoring: {e}")
                time.sleep(0.5)

    def _process_cprofile_data(self) -> Dict[str, Any]:
        """Process cProfile data for call graph analysis"""
        if not self.cprofiler:
            return {}

        try:
            # Create stats object
            s = io.StringIO()
            ps = pstats.Stats(self.cprofiler, stream=s)

            # Get stats data
            ps.sort_stats('cumulative')
            stats_data = ps.stats

            # Process into call graph format
            call_graph = {}
            for func_info, (cc, nc, tt, ct, callers) in stats_data.items():
                func_name = f"{func_info[0]}.{func_info[2]}"
                call_graph[func_name] = {
                    'call_count': cc,
                    'total_time': tt,
                    'cumulative_time': ct,
                    'callers': dict(callers)
                }

            return call_graph

        except Exception as e:
            print(f"Error processing cProfile data: {e}")
            return {}

    def _analyze_session(self, session: ProfileSession):
        """Analyze profiling session and identify bottlenecks"""
        analysis = {
            'hot_functions': [],
            'bottlenecks': [],
            'memory_issues': [],
            'strategy_performance': {},
            'recommendations': []
        }

        # Analyze function profiles
        for func_name, profile in session.function_profiles.items():
            # Identify hot functions (high call count)
            if profile.call_count > 1000:
                analysis['hot_functions'].append({
                    'function': func_name,
                    'call_count': profile.call_count,
                    'total_time': profile.total_time,
                    'recommendation': 'Consider optimizing or caching this frequently called function'
                })

            # Identify bottlenecks (slow functions)
            if profile.average_time > 0.1:  # More than 100ms
                analysis['bottlenecks'].append({
                    'function': func_name,
                    'average_time': profile.average_time,
                    'total_time': profile.total_time,
                    'recommendation': 'This function is a performance bottleneck, consider optimization'
                })

            # Memory issues
            if profile.peak_memory_mb > 100:  # More than 100MB
                analysis['memory_issues'].append({
                    'function': func_name,
                    'peak_memory_mb': profile.peak_memory_mb,
                    'recommendation': 'High memory usage, consider memory optimization'
                })

        # Analyze strategy performance
        for strategy_name, profile in session.strategy_profiles.items():
            success_rate = (profile.successful_executions / profile.total_executions * 100) if profile.total_executions > 0 else 0

            analysis['strategy_performance'][strategy_name] = {
                'executions': profile.total_executions,
                'success_rate': success_rate,
                'average_time': profile.average_time,
                'convergence_rate': profile.convergence_rate,
                'operations_per_second': profile.operations_per_second
            }

            # Strategy-specific recommendations
            if success_rate < 90:
                analysis['recommendations'].append(
                    f"Strategy {strategy_name} has low success rate ({success_rate:.1f}%), consider parameter tuning"
                )

            if profile.average_time > 5.0:
                analysis['recommendations'].append(
                    f"Strategy {strategy_name} is slow ({profile.average_time:.2f}s), consider optimization"
                )

        # Store analysis results
        self.analysis_results[session.session_id] = analysis

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a profiling session"""
        session = self.sessions.get(session_id)
        if not session:
            return {}

        analysis = self.analysis_results.get(session_id, {})

        return {
            'session_info': {
                'session_id': session.session_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'duration': session.duration
            },
            'functions_profiled': len(session.function_profiles),
            'strategies_profiled': len(session.strategy_profiles),
            'hot_functions_count': len(analysis.get('hot_functions', [])),
            'bottlenecks_count': len(analysis.get('bottlenecks', [])),
            'memory_issues_count': len(analysis.get('memory_issues', [])),
            'recommendations_count': len(analysis.get('recommendations', [])),
            'system_metrics_available': len(session.system_metrics) > 0,
            'memory_profile_available': len(session.memory_profile_data) if session.memory_profile_data else 0
        }

    def generate_report(self, session_id: str, format: str = 'html') -> str:
        """Generate performance report for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return f"Session {session_id} not found"

        analysis = self.analysis_results.get(session_id, {})

        if format.lower() == 'html':
            return self._generate_html_report(session, analysis)
        elif format.lower() == 'text':
            return self._generate_text_report(session, analysis)
        elif format.lower() == 'json':
            return self._generate_json_report(session, analysis)
        else:
            raise ValueError(f"Unsupported report format: {format}")

    def _generate_html_report(self, session: ProfileSession, analysis: Dict[str, Any]) -> str:
        """Generate HTML performance report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>BSEE Performance Report - {session.session_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .table {{ border-collapse: collapse; width: 100%; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
                .warning {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; }}
                .error {{ background-color: #f8d7da; padding: 10px; border-radius: 5px; }}
                .success {{ background-color: #d4edda; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BSEE Performance Report</h1>
                <p><strong>Session ID:</strong> {session.session_id}</p>
                <p><strong>Duration:</strong> {session.duration:.2f} seconds</p>
                <p><strong>Generated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="section">
                <h2>Summary</h2>
                <ul>
                    <li>Functions Profiled: {len(session.function_profiles)}</li>
                    <li>Strategies Profiled: {len(session.strategy_profiles)}</li>
                    <li>Hot Functions: {len(analysis.get('hot_functions', []))}</li>
                    <li>Bottlenecks: {len(analysis.get('bottlenecks', []))}</li>
                    <li>Memory Issues: {len(analysis.get('memory_issues', []))}</li>
                </ul>
            </div>
        """

        # Hot functions section
        if analysis.get('hot_functions'):
            html += """
            <div class="section">
                <h2>Hot Functions</h2>
                <table class="table">
                    <tr><th>Function</th><th>Call Count</th><th>Total Time</th><th>Recommendation</th></tr>
            """
            for hot_func in analysis['hot_functions']:
                html += f"""
                    <tr>
                        <td>{hot_func['function']}</td>
                        <td>{hot_func['call_count']}</td>
                        <td>{hot_func['total_time']:.4f}s</td>
                        <td>{hot_func['recommendation']}</td>
                    </tr>
                """
            html += "</table></div>"

        # Bottlenecks section
        if analysis.get('bottlenecks'):
            html += """
            <div class="section">
                <h2>Performance Bottlenecks</h2>
                <div class="error">
                    <p>The following functions are causing performance issues:</p>
            """
            for bottleneck in analysis['bottlenecks']:
                html += f"""
                    <p><strong>{bottleneck['function']}</strong>: {bottleneck['average_time']:.4f}s average time<br>
                    {bottleneck['recommendation']}</p>
                """
            html += "</div></div>"

        # Recommendations section
        if analysis.get('recommendations'):
            html += """
            <div class="section">
                <h2>Recommendations</h2>
                <div class="warning">
            """
            for rec in analysis['recommendations']:
                html += f"<p>• {rec}</p>"
            html += "</div></div>"

        html += """
        </body>
        </html>
        """

        return html

    def _generate_text_report(self, session: ProfileSession, analysis: Dict[str, Any]) -> str:
        """Generate text performance report"""
        report = f"""
BSEE Performance Report - {session.session_id}
{'=' * 50}

Session Information:
- Session ID: {session.session_id}
- Duration: {session.duration:.2f} seconds
- Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.start_time))}
- End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.end_time))}

Summary:
- Functions Profiled: {len(session.function_profiles)}
- Strategies Profiled: {len(session.strategy_profiles)}
- Hot Functions: {len(analysis.get('hot_functions', []))}
- Bottlenecks: {len(analysis.get('bottlenecks', []))}
- Memory Issues: {len(analysis.get('memory_issues', []))}
"""

        if analysis.get('hot_functions'):
            report += "\nHot Functions:\n"
            for hot_func in analysis['hot_functions']:
                report += f"  - {hot_func['function']}: {hot_func['call_count']} calls, {hot_func['total_time']:.4f}s total\n"

        if analysis.get('bottlenecks'):
            report += "\nPerformance Bottlenecks:\n"
            for bottleneck in analysis['bottlenecks']:
                report += f"  - {bottleneck['function']}: {bottleneck['average_time']:.4f}s average\n"

        if analysis.get('recommendations'):
            report += "\nRecommendations:\n"
            for rec in analysis['recommendations']:
                report += f"  • {rec}\n"

        return report

    def _generate_json_report(self, session: ProfileSession, analysis: Dict[str, Any]) -> str:
        """Generate JSON performance report"""
        import json

        report_data = {
            'session': {
                'session_id': session.session_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'duration': session.duration
            },
            'analysis': analysis,
            'function_profiles': {
                name: {
                    'call_count': fp.call_count,
                    'total_time': fp.total_time,
                    'average_time': fp.average_time,
                    'memory_usage_mb': fp.memory_usage_mb,
                    'is_hot': fp.is_hot,
                    'is_bottleneck': fp.is_bottleneck
                }
                for name, fp in session.function_profiles.items()
            },
            'strategy_profiles': {
                name: {
                    'total_executions': sp.total_executions,
                    'successful_executions': sp.successful_executions,
                    'average_time': sp.average_time,
                    'convergence_rate': sp.convergence_rate,
                    'operations_per_second': sp.operations_per_second
                }
                for name, sp in session.strategy_profiles.items()
            }
        }

        return json.dumps(report_data, indent=2, default=str)

    def enable_cprofile(self):
        """Enable cProfile integration"""
        self.cprofile_enabled = True

    def disable_cprofile(self):
        """Disable cProfile integration"""
        self.cprofile_enabled = False

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all profiling sessions"""
        sessions = []
        for session_id, session in self.sessions.items():
            sessions.append(self.get_session_summary(session_id))
        return sessions

    def cleanup_session(self, session_id: str):
        """Clean up a profiling session"""
        with self._session_lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.analysis_results:
                del self.analysis_results[session_id]

    def cleanup_all_sessions(self):
        """Clean up all profiling sessions"""
        with self._session_lock:
            self.sessions.clear()
            self.analysis_results.clear()
        self.function_profiler.reset()
        self.strategy_profiler.reset()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.current_session:
            self.end_profiling_session()
        self.cleanup_all_sessions()