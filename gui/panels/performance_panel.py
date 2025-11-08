"""
Performance Panel GUI
Real-time performance visualization dashboard for BSEE
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from typing import Dict, List, Any, Optional
import queue

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from bsee.monitoring.performance_monitor import PerformanceMonitor, PerformanceSnapshot
from bsee.monitoring.performance_alerts import PerformanceAlerts, PerformanceAlert, AlertSeverity


class MetricCard(ttk.Frame):
    """Widget for displaying a single metric with label and value"""

    def __init__(self, parent, title: str, unit: str = "", format_spec: str = ".2f"):
        super().__init__(parent, relief=tk.RAISED, borderwidth=1)

        self.title = title
        self.unit = unit
        self.format_spec = format_spec

        # Title label
        self.title_label = ttk.Label(self, text=title, font=('Arial', 9, 'bold'))
        self.title_label.pack(pady=2)

        # Value label
        self.value_label = ttk.Label(self, text="--", font=('Arial', 14, 'bold'))
        self.value_label.pack(pady=2)

        # Unit label
        if unit:
            self.unit_label = ttk.Label(self, text=unit, font=('Arial', 8))
            self.unit_label.pack()

        # Status indicator
        self.status_label = ttk.Label(self, text="●", font=('Arial', 10))
        self.status_label.pack(pady=1)

        self.current_value = 0.0
        self.status = "normal"

    def update_value(self, value: float, status: str = "normal"):
        """Update the displayed value and status"""
        self.current_value = value
        self.status = status

        # Format and display value
        if value is not None:
            formatted_value = f"{value:{self.format_spec}}"
            self.value_label.config(text=formatted_value)
        else:
            self.value_label.config(text="--")

        # Update status color
        if status == "good":
            color = "#00aa00"  # Green
        elif status == "warning":
            color = "#ff9900"  # Orange
        elif status == "error":
            color = "#ff0000"  # Red
        elif status == "critical":
            color = "#cc0000"  # Dark red
        else:
            color = "#000000"  # Black

        self.status_label.config(text="●", foreground=color)


class PerformanceChart:
    """Base class for performance charts"""

    def __init__(self, title: str, max_points: int = 60):
        self.title = title
        self.max_points = max_points
        self.timestamps = []
        self.values = []

    def add_data_point(self, timestamp: float, value: float):
        """Add a new data point"""
        self.timestamps.append(timestamp)
        self.values.append(value)

        # Keep only the most recent points
        if len(self.timestamps) > self.max_points:
            self.timestamps.pop(0)
            self.values.pop(0)

    def clear_data(self):
        """Clear all data points"""
        self.timestamps.clear()
        self.values.clear()


class MatplotlibChart(PerformanceChart):
    """Matplotlib-based chart for performance metrics"""

    def __init__(self, parent, title: str, ylabel: str, color: str = 'blue', max_points: int = 60):
        super().__init__(title, max_points)

        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib not available")

        self.fig = Figure(figsize=(6, 3), dpi=80)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_title(title, fontsize=10)
        self.ax.set_ylabel(ylabel, fontsize=8)
        self.ax.set_xlabel('Time (seconds ago)', fontsize=8)
        self.ax.grid(True, alpha=0.3)

        self.line, = self.ax.plot([], [], color=color, linewidth=1.5)
        self.ax.set_xlim(max_points, 0)  # Reverse x-axis for time ago
        self.ax.tick_params(axis='both', labelsize=8)

        # Adjust layout
        self.fig.tight_layout()

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_chart(self):
        """Update the chart with current data"""
        if len(self.timestamps) > 1:
            # Convert timestamps to relative time (seconds ago)
            current_time = time.time()
            time_ago = [current_time - t for t in self.timestamps]

            self.line.set_data(time_ago, self.values)

            # Adjust y-axis limits
            if self.values:
                y_min, y_max = min(self.values), max(self.values)
                y_range = y_max - y_min
                if y_range > 0:
                    self.ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)
                else:
                    self.ax.set_ylim(y_min - 1, y_max + 1)

            self.canvas.draw()


class FallbackChart(ttk.Frame, PerformanceChart):
    """Fallback chart using Canvas when matplotlib is not available"""

    def __init__(self, parent, title: str, ylabel: str, color: str = 'blue', max_points: int = 60):
        ttk.Frame.__init__(self, parent)
        PerformanceChart.__init__(self, title, max_points)

        self.ylabel = ylabel
        self.color = color

        # Title label
        self.title_label = ttk.Label(self, text=title, font=('Arial', 10, 'bold'))
        self.title_label.pack()

        # Canvas for drawing
        self.canvas = tk.Canvas(self, height=150, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Value label
        self.value_label = ttk.Label(self, text="--", font=('Arial', 9))
        self.value_label.pack()

    def update_chart(self):
        """Update the chart with current data"""
        if not self.values:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Draw chart
        margin = 20
        chart_width = width - 2 * margin
        chart_height = height - 2 * margin

        if chart_width <= 0 or chart_height <= 0:
            return

        # Calculate scale
        if self.values:
            y_min = min(self.values)
            y_max = max(self.values)
            y_range = y_max - y_min

            if y_range == 0:
                y_range = 1

            # Draw axes
            self.canvas.create_line(margin, height - margin, width - margin, height - margin, fill='black')
            self.canvas.create_line(margin, margin, margin, height - margin, fill='black')

            # Draw data points
            if len(self.values) > 1:
                points = []
                for i, value in enumerate(self.values):
                    x = margin + (i / (len(self.values) - 1)) * chart_width
                    y = height - margin - ((value - y_min) / y_range) * chart_height
                    points.extend([x, y])

                if len(points) >= 4:
                    self.canvas.create_line(points, fill=self.color, width=2)

            # Update current value label
            current_value = self.values[-1] if self.values else 0
            self.value_label.config(text=f"{self.ylabel}: {current_value:.2f}")


class PerformancePanel(ttk.Frame):
    """Real-time performance monitoring dashboard"""

    def __init__(self, parent, performance_monitor: Optional[PerformanceMonitor] = None):
        super().__init__(parent)

        self.performance_monitor = performance_monitor or PerformanceMonitor()
        self.alerts_system = PerformanceAlerts()

        # Data storage
        self.update_queue = queue.Queue()
        self.updating = False

        # Chart objects
        self.cpu_chart = None
        self.memory_chart = None
        self.ops_chart = None

        # Setup UI
        self.setup_ui()
        self.setup_charts()

        # Start monitoring
        self.start_monitoring()

    def setup_ui(self):
        """Setup the main UI layout"""
        # Title
        title_label = ttk.Label(self, text="Performance Dashboard", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Metric cards section
        metrics_frame = ttk.LabelFrame(self, text="Real-Time Metrics", padding=10)
        metrics_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # Create metric cards
        self.ops_card = MetricCard(metrics_frame, "Operations/Sec", "ops/sec", ".1f")
        self.ops_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.cpu_card = MetricCard(metrics_frame, "CPU Usage", "%", ".1f")
        self.cpu_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.memory_card = MetricCard(metrics_frame, "Memory Usage", "%", ".1f")
        self.memory_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.cache_card = MetricCard(metrics_frame, "Cache Hit Rate", "%", ".1f")
        self.cache_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Configure grid weights
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)

        # Charts section
        charts_frame = ttk.LabelFrame(self, text="Performance Charts", padding=10)
        charts_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Strategy performance section
        strategy_frame = ttk.LabelFrame(self, text="Strategy Performance", padding=10)
        strategy_frame.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)

        # Strategy performance tree
        columns = ('Ops/Sec', 'Avg Time', 'Success Rate', 'Status')
        self.strategy_tree = ttk.Treeview(strategy_frame, columns=columns, height=8, show='tree headings')
        self.strategy_tree.heading('#0', text='Strategy')
        self.strategy_tree.heading('Ops/Sec', text='Ops/Sec')
        self.strategy_tree.heading('Avg Time', text='Avg Time')
        self.strategy_tree.heading('Success Rate', text='Success %')
        self.strategy_tree.heading('Status', text='Status')

        # Configure column widths
        self.strategy_tree.column('#0', width=100)
        self.strategy_tree.column('Ops/Sec', width=70)
        self.strategy_tree.column('Avg Time', width=70)
        self.strategy_tree.column('Success Rate', width=80)
        self.strategy_tree.column('Status', width=60)

        self.strategy_tree.pack(fill=tk.BOTH, expand=True)

        # Strategy scrollbar
        strategy_scrollbar = ttk.Scrollbar(strategy_frame, orient=tk.VERTICAL, command=self.strategy_tree.yview)
        strategy_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.strategy_tree.configure(yscrollcommand=strategy_scrollbar.set)

        # Alerts section
        alerts_frame = ttk.LabelFrame(self, text="Active Alerts", padding=10)
        alerts_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # Alerts list
        self.alerts_text = scrolledtext.ScrolledText(alerts_frame, height=4, wrap=tk.WORD)
        self.alerts_text.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=4, column=0, columnspan=3, pady=10)

        self.start_button = ttk.Button(controls_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(controls_frame, text="Stop Monitoring", command=self.stop_monitoring)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(controls_frame, text="Clear Alerts", command=self.clear_alerts)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ttk.Button(controls_frame, text="Export Data", command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=2)

    def setup_charts(self):
        """Setup performance charts"""
        charts_frame = self.grid_slaves(row=2, column=0)[0] if self.grid_slaves(row=2, column=0) else None
        if not charts_frame:
            return

        # CPU usage chart
        if MATPLOTLIB_AVAILABLE:
            self.cpu_chart = MatplotlibChart(charts_frame, "CPU Usage (%)", "CPU %", 'red')
            self.cpu_chart.canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            # Memory usage chart
            self.memory_chart = MatplotlibChart(charts_frame, "Memory Usage (%)", "Memory %", 'blue')
            self.memory_chart.canvas.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky="ew")

            # Operations per second chart
            self.ops_chart = MatplotlibChart(charts_frame, "Operations per Second", "Ops/Sec", 'green')
            self.ops_chart.canvas.get_tk_widget().grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        else:
            # Fallback charts
            self.cpu_chart = FallbackChart(charts_frame, "CPU Usage (%)", "CPU %", 'red')
            self.cpu_chart.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            self.memory_chart = FallbackChart(charts_frame, "Memory Usage (%)", "Memory %", 'blue')
            self.memory_chart.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

            self.ops_chart = FallbackChart(charts_frame, "Operations per Second", "Ops/Sec", 'green')
            self.ops_chart.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Configure chart frame grid
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)

    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.performance_monitor._monitoring:
            self.performance_monitor.start_monitoring()
            self.alerts_system.start_monitoring()

            # Set up callbacks
            self.performance_monitor.add_callback('metrics_collected', self.on_metrics_collected)
            self.alerts_system.add_action(AlertSeverity.WARNING, self.AlertCallback(self))

            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            # Start UI update loop
            self.start_ui_updates()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.performance_monitor.stop_monitoring()
        self.alerts_system.stop_monitoring()

        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

        self.stop_ui_updates()

    def start_ui_updates(self):
        """Start the UI update loop"""
        self.updating = True
        self.update_ui()

    def stop_ui_updates(self):
        """Stop the UI update loop"""
        self.updating = False

    def update_ui(self):
        """Update UI elements with latest data"""
        if not self.updating:
            return

        try:
            # Process queued updates
            while not self.update_queue.empty():
                try:
                    snapshot = self.update_queue.get_nowait()
                    self.update_dashboard(snapshot)
                except queue.Empty:
                    break

        except Exception as e:
            print(f"Error updating UI: {e}")

        # Schedule next update
        self.after(1000, self.update_ui)  # Update every second

    def on_metrics_collected(self, snapshot: PerformanceSnapshot):
        """Callback when new metrics are collected"""
        try:
            self.update_queue.put_nowait(snapshot)
        except queue.Full:
            pass  # Skip update if queue is full

    def update_dashboard(self, snapshot: PerformanceSnapshot):
        """Update dashboard with new performance data"""
        try:
            # Update metric cards
            self.ops_card.update_value(
                snapshot.operations.operations_per_second,
                self.get_metric_status(snapshot.operations.operations_per_second, 1.0, 5.0)
            )

            self.cpu_card.update_value(
                snapshot.system.cpu_percent,
                self.get_metric_status(snapshot.system.cpu_percent, 60.0, 85.0, reverse=True)
            )

            self.memory_card.update_value(
                snapshot.system.memory_percent,
                self.get_metric_status(snapshot.system.memory_percent, 70.0, 90.0, reverse=True)
            )

            self.cache_card.update_value(
                snapshot.operations.cache_hit_rate,
                self.get_metric_status(snapshot.operations.cache_hit_rate, 60.0, 30.0)
            )

            # Update charts
            if self.cpu_chart:
                self.cpu_chart.add_data_point(snapshot.timestamp, snapshot.system.cpu_percent)
                self.cpu_chart.update_chart()

            if self.memory_chart:
                self.memory_chart.add_data_point(snapshot.timestamp, snapshot.system.memory_percent)
                self.memory_chart.update_chart()

            if self.ops_chart:
                self.ops_chart.add_data_point(snapshot.timestamp, snapshot.operations.operations_per_second)
                self.ops_chart.update_chart()

            # Update strategy performance
            self.update_strategy_performance(snapshot.strategies)

            # Check for alerts
            self.alerts_system.check_performance_snapshot(snapshot)

        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def update_strategy_performance(self, strategies: Dict[str, Any]):
        """Update strategy performance tree"""
        # Clear existing items
        for item in self.strategy_tree.get_children():
            self.strategy_tree.delete(item)

        # Add strategy data
        for strategy_name, strategy_metrics in strategies.items():
            ops_per_sec = strategy_metrics.operations_count / max(strategy_metrics.average_execution_time, 0.001)
            avg_time = strategy_metrics.average_execution_time
            success_rate = strategy_metrics.success_rate

            # Determine status
            if success_rate >= 90 and avg_time <= 2.0:
                status = "Good"
                status_tag = "good"
            elif success_rate >= 70 and avg_time <= 5.0:
                status = "Slow"
                status_tag = "warning"
            else:
                status = "Error"
                status_tag = "error"

            self.strategy_tree.insert('', 'end', text=strategy_name,
                                     values=(f"{ops_per_sec:.1f}",
                                            f"{avg_time:.2f}s",
                                            f"{success_rate:.1f}%",
                                            status),
                                     tags=(status_tag,))

        # Configure tags
        self.strategy_tree.tag_configure('good', foreground='green')
        self.strategy_tree.tag_configure('warning', foreground='orange')
        self.strategy_tree.tag_configure('error', foreground='red')

    def get_metric_status(self, value: float, good_threshold: float, bad_threshold: float, reverse: bool = False) -> str:
        """Determine metric status based on value"""
        if reverse:
            # For metrics where lower is better (CPU, memory)
            if value <= good_threshold:
                return "good"
            elif value <= bad_threshold:
                return "warning"
            else:
                return "error"
        else:
            # For metrics where higher is better (cache hit rate, ops/sec)
            if value >= good_threshold:
                return "good"
            elif value >= bad_threshold:
                return "warning"
            else:
                return "error"

    def clear_alerts(self):
        """Clear all active alerts"""
        self.alerts_system.active_alerts.clear()
        self.update_alerts_display()

    def update_alerts_display(self):
        """Update the alerts display"""
        self.alerts_text.delete(1.0, tk.END)

        active_alerts = self.alerts_system.get_active_alerts()
        if not active_alerts:
            self.alerts_text.insert(tk.END, "No active alerts\n")
        else:
            for alert in active_alerts:
                alert_text = f"[{alert.severity.value.upper()}] {alert.alert_type.value}: {alert.message}\n"
                self.alerts_text.insert(tk.END, alert_text)

                # Color code by severity
                if alert.severity == AlertSeverity.ERROR:
                    self.alerts_text.tag_add("error", f"end-2l", f"end-1l")
                elif alert.severity == AlertSeverity.WARNING:
                    self.alerts_text.tag_add("warning", f"end-2l", f"end-1l")

        # Configure tags
        self.alerts_text.tag_configure("error", foreground="red")
        self.alerts_text.tag_configure("warning", foreground="orange")

    def export_data(self):
        """Export performance data"""
        try:
            # Get export format from user
            export_window = tk.Toplevel(self)
            export_window.title("Export Performance Data")
            export_window.geometry("300x150")

            ttk.Label(export_window, text="Select export format:").pack(pady=10)

            format_var = tk.StringVar(value="json")
            formats = [("JSON", "json"), ("CSV", "csv")]

            for text, value in formats:
                ttk.Radiobutton(export_window, text=text, variable=format_var, value=value).pack()

            def do_export():
                try:
                    data = self.performance_monitor.export_metrics(format_var.get())
                    filename = f"performance_export_{int(time.time())}.{format_var.get()}"

                    with open(filename, 'w') as f:
                        f.write(data)

                    ttk.Label(export_window, text=f"Exported to {filename}").pack(pady=10)
                    export_window.after(2000, export_window.destroy)

                except Exception as e:
                    ttk.Label(export_window, text=f"Export failed: {e}").pack(pady=10)

            ttk.Button(export_window, text="Export", command=do_export).pack(pady=10)

        except Exception as e:
            print(f"Error opening export dialog: {e}")

    class AlertCallback:
        """Callback for handling alerts"""

        def __init__(self, panel):
            self.panel = panel

        def __call__(self, alert: PerformanceAlert):
            """Handle alert notification"""
            # Update alerts display
            self.panel.update_alerts_display()

            # Could add additional alert handling here
            # like showing notifications, logging, etc.

    def on_closing(self):
        """Handle panel closing"""
        self.stop_monitoring()
        if hasattr(self, 'master') and self.master:
            self.master.destroy()