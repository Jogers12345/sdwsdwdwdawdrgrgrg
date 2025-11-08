"""
Performance Alerts System
Automated performance issue detection and alerts for BSEE
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from collections import deque
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of performance alerts"""
    MEMORY_HIGH = "memory_high"
    CPU_HIGH = "cpu_high"
    LOW_OPS_RATE = "low_ops_rate"
    STRATEGY_SLOW = "strategy_slow"
    ERROR_RATE_HIGH = "error_rate_high"
    DISK_IO_HIGH = "disk_io_high"
    THREAD_COUNT_HIGH = "thread_count_high"
    CACHE_HIT_RATE_LOW = "cache_hit_rate_low"


@dataclass
class AlertThreshold:
    """Configuration for alert thresholds"""
    alert_type: AlertType
    threshold_value: float
    severity: AlertSeverity
    duration_seconds: float = 10.0  # How long condition must persist
    enabled: bool = True
    message_template: str = ""


@dataclass
class PerformanceAlert:
    """Performance alert instance"""
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    start_time: float
    duration: float = 0.0
    resolved: bool = False
    resolution_time: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AlertAction:
    """Base class for alert actions"""

    def execute(self, alert: PerformanceAlert) -> bool:
        """Execute the alert action. Returns True if successful."""
        raise NotImplementedError


class LogAction(AlertAction):
    """Log alert to console or file"""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file

    def execute(self, alert: PerformanceAlert) -> bool:
        message = f"[{alert.severity.value.upper()}] {alert.alert_type.value}: {alert.message}"

        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
            except Exception as e:
                print(f"Failed to write to log file: {e}")
                return False
        else:
            print(message)

        return True


class EmailAction(AlertAction):
    """Send email notification for alerts"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str,
                 password: str, from_email: str, to_emails: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails

    def execute(self, alert: PerformanceAlert) -> bool:
        try:
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"BSEE Performance Alert: {alert.alert_type.value}"

            body = f"""
            Performance Alert Detected

            Type: {alert.alert_type.value}
            Severity: {alert.severity.value}
            Message: {alert.message}
            Current Value: {alert.current_value}
            Threshold: {alert.threshold_value}
            Duration: {alert.duration:.1f} seconds
            Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.start_time))}

            This is an automated alert from the BSEE Performance Monitoring System.
            """

            msg.attach(MimeText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, self.to_emails, text)
            server.quit()

            return True

        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False


class CallbackAction(AlertAction):
    """Execute custom callback function for alerts"""

    def __init__(self, callback: Callable[[PerformanceAlert], None]):
        self.callback = callback

    def execute(self, alert: PerformanceAlert) -> bool:
        try:
            self.callback(alert)
            return True
        except Exception as e:
            print(f"Error in alert callback: {e}")
            return False


class AutoFixAction(AlertAction):
    """Attempt automatic remediation for certain alert types"""

    def __init__(self):
        self.fix_functions = {
            AlertType.CACHE_HIT_RATE_LOW: self._clear_cache,
            AlertType.MEMORY_HIGH: self._trigger_gc,
            AlertType.THREAD_COUNT_HIGH: self._monitor_threads,
        }

    def execute(self, alert: PerformanceAlert) -> bool:
        fix_func = self.fix_functions.get(alert.alert_type)
        if fix_func:
            return fix_func(alert)
        return False

    def _clear_cache(self, alert: PerformanceAlert) -> bool:
        """Clear application caches to improve performance"""
        try:
            # This would need to be connected to the actual cache system
            print("Auto-fix: Attempting to clear caches")
            # Implementation would clear operation cache, metrics cache, etc.
            return True
        except Exception as e:
            print(f"Auto-fix failed: {e}")
            return False

    def _trigger_gc(self, alert: PerformanceAlert) -> bool:
        """Trigger garbage collection to free memory"""
        try:
            import gc
            collected = gc.collect()
            print(f"Auto-fix: Triggered garbage collection, collected {collected} objects")
            return True
        except Exception as e:
            print(f"Auto-fix failed: {e}")
            return False

    def _monitor_threads(self, alert: PerformanceAlert) -> bool:
        """Monitor and potentially manage thread count"""
        try:
            print("Auto-fix: Monitoring thread usage")
            # Implementation would analyze thread usage and potentially take action
            return True
        except Exception as e:
            print(f"Auto-fix failed: {e}")
            return False


class PerformanceAlerts:
    """Performance alerts monitoring and management system"""

    def __init__(self):
        self.thresholds = self._create_default_thresholds()
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history = deque(maxlen=1000)
        self.actions: Dict[AlertSeverity, List[AlertAction]] = {
            AlertSeverity.INFO: [LogAction()],
            AlertSeverity.WARNING: [LogAction()],
            AlertSeverity.ERROR: [LogAction(), AutoFixAction()],
            AlertSeverity.CRITICAL: [LogAction(), AutoFixAction()]
        }

        # Monitoring state
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.RLock()

        # Alert conditions tracking
        self._condition_tracking = {}
        self._last_check_time = time.time()

    def _create_default_thresholds(self) -> List[AlertThreshold]:
        """Create default alert thresholds"""
        return [
            AlertThreshold(
                alert_type=AlertType.MEMORY_HIGH,
                threshold_value=80.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=30.0,
                message_template="High memory usage: {current_value:.1f}% (threshold: {threshold_value:.1f}%)"
            ),
            AlertThreshold(
                alert_type=AlertType.MEMORY_HIGH,
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL,
                duration_seconds=10.0,
                message_template="Critical memory usage: {current_value:.1f}% (threshold: {threshold_value:.1f}%)"
            ),
            AlertThreshold(
                alert_type=AlertType.CPU_HIGH,
                threshold_value=80.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=60.0,
                message_template="High CPU usage: {current_value:.1f}% (threshold: {threshold_value:.1f}%)"
            ),
            AlertThreshold(
                alert_type=AlertType.CPU_HIGH,
                threshold_value=95.0,
                severity=AlertSeverity.ERROR,
                duration_seconds=30.0,
                message_template="Very high CPU usage: {current_value:.1f}% (threshold: {threshold_value:.1f}%)"
            ),
            AlertThreshold(
                alert_type=AlertType.LOW_OPS_RATE,
                threshold_value=1.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=30.0,
                message_template="Low operations rate: {current_value:.2f} ops/sec (threshold: {threshold_value:.2f})"
            ),
            AlertThreshold(
                alert_type=AlertType.LOW_OPS_RATE,
                threshold_value=0.1,
                severity=AlertSeverity.ERROR,
                duration_seconds=60.0,
                message_template="Very low operations rate: {current_value:.2f} ops/sec (threshold: {threshold_value:.2f})"
            ),
            AlertThreshold(
                alert_type=AlertType.CACHE_HIT_RATE_LOW,
                threshold_value=50.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=120.0,
                message_template="Low cache hit rate: {current_value:.1f}% (threshold: {threshold_value:.1f}%)"
            ),
            AlertThreshold(
                alert_type=AlertType.THREAD_COUNT_HIGH,
                threshold_value=50,
                severity=AlertSeverity.WARNING,
                duration_seconds=30.0,
                message_template="High thread count: {current_value:.0f} (threshold: {threshold_value:.0f})"
            ),
            AlertThreshold(
                alert_type=AlertType.STRATEGY_SLOW,
                threshold_value=5.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=60.0,
                message_template="Slow strategy execution: {current_value:.2f}s (threshold: {threshold_value:.2f}s)"
            ),
            AlertThreshold(
                alert_type=AlertType.ERROR_RATE_HIGH,
                threshold_value=5.0,
                severity=AlertSeverity.ERROR,
                duration_seconds=30.0,
                message_template="High error rate: {current_value:.1f}% (threshold: {threshold_value:.1f}%)"
            ),
        ]

    def add_threshold(self, threshold: AlertThreshold):
        """Add or update an alert threshold"""
        self.thresholds = [t for t in self.thresholds if t.alert_type != threshold.alert_type
                          or t.threshold_value != threshold.threshold_value]
        self.thresholds.append(threshold)

    def add_action(self, severity: AlertSeverity, action: AlertAction):
        """Add action for specific alert severity"""
        if severity not in self.actions:
            self.actions[severity] = []
        self.actions[severity].append(action)

    def remove_action(self, severity: AlertSeverity, action_type: type):
        """Remove action of specific type for severity"""
        if severity in self.actions:
            self.actions[severity] = [a for a in self.actions[severity]
                                     if not isinstance(a, action_type)]

    def start_monitoring(self):
        """Start alert monitoring"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        print("Performance alerts monitoring started")

    def stop_monitoring(self):
        """Stop alert monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        print("Performance alerts monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                self._check_alerts()
                time.sleep(5.0)  # Check every 5 seconds
            except Exception as e:
                print(f"Error in alerts monitoring loop: {e}")
                time.sleep(5.0)

    def check_performance_snapshot(self, snapshot):
        """Check a performance snapshot for alert conditions"""
        self._evaluate_thresholds(snapshot)
        self._update_alert_durations()

    def _check_alerts(self):
        """Check alerts from current performance state"""
        # This would typically get the current performance snapshot
        # For now, we'll just update durations
        self._update_alert_durations()

    def _evaluate_thresholds(self, snapshot):
        """Evaluate all thresholds against current performance snapshot"""
        current_time = time.time()

        for threshold in self.thresholds:
            if not threshold.enabled:
                continue

            current_value = self._get_metric_value(threshold.alert_type, snapshot)
            if current_value is None:
                continue

            condition_met = self._evaluate_condition(threshold.alert_type, current_value, threshold.threshold_value)
            condition_key = f"{threshold.alert_type.value}_{threshold.threshold_value}"

            if condition_met:
                # Track condition start time
                if condition_key not in self._condition_tracking:
                    self._condition_tracking[condition_key] = current_time

                # Check if condition has persisted long enough
                condition_duration = current_time - self._condition_tracking[condition_key]

                if condition_duration >= threshold.duration_seconds:
                    self._trigger_alert(threshold, current_value, snapshot, condition_duration)

            else:
                # Condition not met, remove tracking
                if condition_key in self._condition_tracking:
                    del self._condition_tracking[condition_key]

                # Resolve any active alerts for this condition
                self._resolve_alerts(threshold.alert_type, current_time)

    def _get_metric_value(self, alert_type: AlertType, snapshot) -> Optional[float]:
        """Extract metric value from snapshot based on alert type"""
        try:
            if alert_type == AlertType.MEMORY_HIGH:
                return snapshot.system.memory_percent
            elif alert_type == AlertType.CPU_HIGH:
                return snapshot.system.cpu_percent
            elif alert_type == AlertType.LOW_OPS_RATE:
                return snapshot.operations.operations_per_second
            elif alert_type == AlertType.CACHE_HIT_RATE_LOW:
                return snapshot.operations.cache_hit_rate
            elif alert_type == AlertType.THREAD_COUNT_HIGH:
                return float(snapshot.system.thread_count)
            elif alert_type == AlertType.DISK_IO_HIGH:
                return snapshot.system.disk_io_read_mb + snapshot.system.disk_io_write_mb
            elif alert_type == AlertType.STRATEGY_SLOW:
                # Use average execution time from strategies
                if snapshot.strategies:
                    return max(s.average_execution_time for s in snapshot.strategies.values())
                return None
            else:
                return None
        except Exception:
            return None

    def _evaluate_condition(self, alert_type: AlertType, current_value: float, threshold_value: float) -> bool:
        """Evaluate if alert condition is met"""
        if alert_type in [AlertType.MEMORY_HIGH, AlertType.CPU_HIGH, AlertType.THREAD_COUNT_HIGH,
                         AlertType.STRATEGY_SLOW, AlertType.DISK_IO_HIGH, AlertType.ERROR_RATE_HIGH]:
            return current_value >= threshold_value
        else:
            # Low conditions (ops rate, cache hit rate)
            return current_value <= threshold_value

    def _trigger_alert(self, threshold: AlertThreshold, current_value: float, snapshot, duration: float):
        """Trigger a new alert"""
        alert_id = f"{threshold.alert_type.value}_{threshold.threshold_value}_{int(time.time())}"

        # Check if similar alert already exists
        for existing_alert in self.active_alerts.values():
            if (existing_alert.alert_type == threshold.alert_type and
                not existing_alert.resolved):
                return  # Alert already active

        # Format message
        if threshold.message_template:
            message = threshold.message_template.format(
                current_value=current_value,
                threshold_value=threshold.threshold_value
            )
        else:
            message = f"{threshold.alert_type.value}: {current_value} (threshold: {threshold_value})"

        alert = PerformanceAlert(
            id=alert_id,
            alert_type=threshold.alert_type,
            severity=threshold.severity,
            message=message,
            current_value=current_value,
            threshold_value=threshold.threshold_value,
            start_time=time.time(),
            duration=duration,
            metadata={
                'snapshot_timestamp': snapshot.timestamp,
                'condition_duration': duration
            }
        )

        with self._lock:
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

        # Execute alert actions
        self._execute_actions(alert)

    def _resolve_alerts(self, alert_type: AlertType, resolution_time: float):
        """Resolve active alerts of specific type"""
        with self._lock:
            for alert in self.active_alerts.values():
                if alert.alert_type == alert_type and not alert.resolved:
                    alert.resolved = True
                    alert.resolution_time = resolution_time
                    alert.duration = resolution_time - alert.start_time

                    # Remove from active alerts
                    self.active_alerts = {
                        k: v for k, v in self.active_alerts.items()
                        if v.id != alert.id
                    }

                    # Log resolution
                    print(f"Alert resolved: {alert.alert_type.value} - {alert.message}")

    def _update_alert_durations(self):
        """Update durations for active alerts"""
        current_time = time.time()

        with self._lock:
            for alert in self.active_alerts.values():
                if not alert.resolved:
                    alert.duration = current_time - alert.start_time

    def _execute_actions(self, alert: PerformanceAlert):
        """Execute actions for an alert"""
        actions = self.actions.get(alert.severity, [])

        for action in actions:
            try:
                success = action.execute(alert)
                if not success:
                    print(f"Alert action failed for {alert.alert_type.value}: {type(action).__name__}")
            except Exception as e:
                print(f"Error executing alert action: {e}")

    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get list of currently active alerts"""
        with self._lock:
            return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[PerformanceAlert]:
        """Get recent alert history"""
        with self._lock:
            return list(self.alert_history)[-limit:]

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        with self._lock:
            total_alerts = len(self.alert_history)
            active_alerts = len(self.active_alerts)

            # Count by severity
            severity_counts = {}
            for alert in self.alert_history:
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Count by type
            type_counts = {}
            for alert in self.alert_history:
                alert_type = alert.alert_type.value
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1

            # Average resolution time
            resolved_alerts = [a for a in self.alert_history if a.resolved]
            avg_resolution_time = 0.0
            if resolved_alerts:
                avg_resolution_time = sum(a.duration for a in resolved_alerts) / len(resolved_alerts)

            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'severity_distribution': severity_counts,
                'type_distribution': type_counts,
                'average_resolution_time': avg_resolution_time,
                'last_check_time': self._last_check_time
            }

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert (mark as acknowledged)"""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.metadata['acknowledged'] = True
                alert.metadata['acknowledged_time'] = time.time()
                return True
            return False

    def clear_alert(self, alert_id: str) -> bool:
        """Clear an alert (remove from active alerts)"""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolution_time = time.time()
                alert.metadata['manually_cleared'] = True
                del self.active_alerts[alert_id]
                return True
            return False

    def configure_email_alerts(self, smtp_config: Dict[str, Any], recipients: List[str]):
        """Configure email alert notifications"""
        email_action = EmailAction(
            smtp_server=smtp_config['server'],
            smtp_port=smtp_config['port'],
            username=smtp_config['username'],
            password=smtp_config['password'],
            from_email=smtp_config['from_email'],
            to_emails=recipients
        )

        # Add email action for error and critical alerts
        self.add_action(AlertSeverity.ERROR, email_action)
        self.add_action(AlertSeverity.CRITICAL, email_action)

    def export_alerts(self, format: str = 'json') -> str:
        """Export alerts data"""
        with self._lock:
            data = {
                'active_alerts': [alert.__dict__ for alert in self.active_alerts.values()],
                'alert_history': [alert.__dict__ for alert in self.alert_history],
                'statistics': self.get_alert_statistics(),
                'export_timestamp': time.time()
            }

        if format.lower() == 'json':
            import json
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def __enter__(self):
        """Context manager entry"""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()