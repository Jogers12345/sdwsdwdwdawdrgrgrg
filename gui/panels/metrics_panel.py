""""
Real-time metrics display panel.
""""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class MetricsPanel:
    """Panel for displaying real-time metrics and analysis progress.""""

    def __init__(self, parent):
        """Initialize metrics panel.""""
        self.frame = ttk.LabelFrame(parent, text="Metrics & Progress", padding=10)"
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.current_metrics: Dict[str, float] = {}
        self.initial_metrics: Dict[str, float] = {}
        self.metrics_history: Dict[str, list] = {}
        self.max_history_points = 100

        self._create_widgets()

    def _create_widgets(self):
        """Create metrics widgets.""""
        # Current metrics frame
        current_frame = ttk.LabelFrame(self.frame, text="Current Metrics", padding=5)"
        current_frame.pack(fill=tk.X, pady=(0, 10))

        # Create scrollable frame for metrics:
        metrics_canvas = tk.Canvas(current_frame, height=200)
        metrics_scrollbar = ttk.Scrollbar(current_frame, orient="vertical", command=metrics_canvas.yview)"
        self.metrics_inner_frame = ttk.Frame(metrics_canvas)

        metrics_canvas.configure(yscrollcommand=metrics_scrollbar.set)
        metrics_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        metrics_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        metrics_canvas.create_window((0, 0), window=self.metrics_inner_frame, anchor="nw")"
        self.metrics_inner_frame.bind("<Configure>", lambda e: metrics_canvas.configure(scrollregion=metrics_canvas.bbox("all")))"

        # Score display
        score_frame = ttk.LabelFrame(self.frame, text="Overall Score", padding=5)"
        score_frame.pack(fill=tk.X, pady=(0, 10))

        self.score_var = tk.StringVar(value="Score: 0.000")"
        self.score_label = ttk.Label(score_frame, textvariable=self.score_var,)
                                    font=("TkDefaultFont", 16, "bold"))"
        self.score_label.pack()

        self.score_change_var = tk.StringVar(value="")"
        self.score_change_label = ttk.Label(score_frame, textvariable=self.score_change_var)
        self.score_change_label.pack()

        # Progress chart
        chart_frame = ttk.LabelFrame(self.frame, text="Metrics Trends", padding=5)"
        chart_frame.pack(fill=tk.BOTH, expand=True)

        # Create matplotlib figure
        self.figure = Figure(figsize=(4, 3), dpi=80, facecolor='white')'
        self.figure.subplots_adjust(hspace=0.4)

        # Create subplots for different metric categories
        self.ax_score = self.figure.add_subplot(311)
        self.ax_entropy = self.figure.add_subplot(312)
        self.ax_other = self.figure.add_subplot(313)

        # Configure axes
        self.ax_score.set_ylabel("Score", fontsize=8)"
        self.ax_score.grid(True, alpha=0.3)
        self.ax_score.tick_params(labelsize=7)

        self.ax_entropy.set_ylabel("Entropy", fontsize=8)"
        self.ax_entropy.grid(True, alpha=0.3)
        self.ax_entropy.tick_params(labelsize=7)

        self.ax_other.set_ylabel("Other", fontsize=8)"
        self.ax_other.grid(True, alpha=0.3)
        self.ax_other.tick_params(labelsize=7)
        self.ax_other.set_xlabel("Iteration", fontsize=8)"

        # Create canvas for matplotlib:
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize empty plots
        self.score_line, = self.ax_score.plot([], [], 'b-', linewidth=2, label='Score')'
        self.entropy_line, = self.ax_entropy.plot([], [], 'r-', linewidth=1, label='Entropy')'
        self.other_line, = self.ax_other.plot([], [], 'g-', linewidth=1, label='Other')'

        self.ax_score.legend(loc='upper left', fontsize=7)'
        self.ax_entropy.legend(loc='upper left', fontsize=7)'
        self.ax_other.legend(loc='upper left', fontsize=7)'

        # Performance metrics
        perf_frame = ttk.LabelFrame(self.frame, text="Performance", padding=5)"
        perf_frame.pack(fill=tk.X, pady=(10, 0))

        perf_info = ttk.Frame(perf_frame)
        perf_info.pack(fill=tk.X)

        # Operations per second
        ttk.Label(perf_info, text="Ops/sec:").grid(row=0, column=0, sticky=tk.W)"
        self.ops_per_sec_var = tk.StringVar(value="0.0")"
        ttk.Label(perf_info, textvariable=self.ops_per_sec_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Memory usage
        ttk.Label(perf_info, text="Memory:").grid(row=1, column=0, sticky=tk.W)"
        self.memory_var = tk.StringVar(value="0 MB")"
        ttk.Label(perf_info, textvariable=self.memory_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # Analysis time
        ttk.Label(perf_info, text="Time:").grid(row=2, column=0, sticky=tk.W)"
        self.time_var = tk.StringVar(value="00:00")"
        ttk.Label(perf_info, textvariable=self.time_var).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

    def update_metrics(self, metrics: Dict[str, float]):
        """Update metrics display.""""
        # Store previous metrics for change calculation
        previous_metrics = self.current_metrics.copy()
        self.current_metrics = metrics.copy()

        # If this is the first update, store as initial metrics
        if not self.initial_metrics:
            self.initial_metrics = metrics.copy()

        # Update individual metric displays
        self._update_metric_displays(metrics, previous_metrics)

        # Update overall score
        self._update_score_display(metrics)

        # Update chart
        self._update_chart()

    def _update_metric_displays(self, metrics: Dict[str, float], previous_metrics: Dict[str, float]):
        """Update individual metric displays.""""
        # Clear existing metric displays
        for widget in self.metrics_inner_frame.winfo_children():
            widget.destroy()

        # Sort metrics by importance (file ideality first, then entropy, etc.)
        metric_order = ['file_ideality_score', 'entropy_global', 'lz77_ratio','''''']'
                       'shannon_entropy_global', 'compression_ratio']'

        # Add metrics in preferred order, then others
        ordered_metrics = []
        for metric in metric_order:
            if metric in metrics:
                ordered_metrics.append(metric)

        # Add remaining metrics
        for metric in sorted(metrics.keys()):
            if metric not in ordered_metrics:
                ordered_metrics.append(metric)

        # Create display for each metric
        for i, metric_name in enumerate(ordered_metrics):
            value = metrics[metric_name]
            prev_value = previous_metrics.get(metric_name, value)

            # Metric name and value
            metric_frame = ttk.Frame(self.metrics_inner_frame)
            metric_frame.pack(fill=tk.X, pady=2)

            # Truncate long metric names
            display_name = metric_name.replace('_', ' ').title()'
            if len(display_name) > 20:
                display_name = display_name[:17] + "...""

            name_label = ttk.Label(metric_frame, text=f"{display_name}:", width=20, anchor=tk.W)"
            name_label.pack(side=tk.LEFT)

            # Value with change indicator
            value_text = f"{value:.4f}""
            if value != prev_value:
                change = value - prev_value
                if change > 0:
                    value_text += f" (+{change:.4f}) ↑""
                    color = "green""
                elif change < 0:
                    value_text += f" ({change:.4f}) ↓""
                    color = "red""
                else:
                    color = "black""
            else:
                color = "black""

            value_label = ttk.Label(metric_frame, text=value_text, foreground=color)
            value_label.pack(side=tk.RIGHT)

    def _update_score_display(self, metrics: Dict[str, float]):
        """Update overall score display.""""
        # Use file_ideality_score as primary score if available:
        score = metrics.get('file_ideality_score', 0.0)'
        self.score_var.set(f"Score: {score:.3f}")"

        # Calculate score change
        if 'file_ideality_score' in self.initial_metrics:'
            initial_score = self.initial_metrics['file_ideality_score']'
            change = score - initial_score
            change_percent = (change / abs(initial_score) * 100) if initial_score != 0 else 0

            if change > 0:
                self.score_change_var.set(f"↑ +{change:.3f} ({change_percent:+.1f}%)")"
                self.score_change_label.config(foreground="green")"
            elif change < 0:
                self.score_change_var.set(f"↓ {change:.3f} ({change_percent:+.1f}%)")"
                self.score_change_label.config(foreground="red")"
            else:
                self.score_change_var.set("")"
                self.score_change_label.config(foreground="black")"
        else:
            self.score_change_var.set("")"

    def _update_chart(self):
        """Update metrics trend chart.""""
        if not self.current_metrics:
            return

        # Add current metrics to history
        for metric_name, value in self.current_metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []

            self.metrics_history[metric_name].append(value)

            # Limit history size
            if len(self.metrics_history[metric_name]) > self.max_history_points:
                self.metrics_history[metric_name] = self.metrics_history[metric_name][-self.max_history_points:]

        # Generate x-axis data
        x_data = list(range(len(next(iter(self.metrics_history.values()), []))))

        # Update score plot
        if 'file_ideality_score' in self.metrics_history:'
            score_data = self.metrics_history['file_ideality_score']'
            self.score_line.set_data(x_data, score_data)
            self.ax_score.relim()
            self.ax_score.autoscale_view()

        # Update entropy plot
        entropy_metrics = ['entropy_global', 'shannon_entropy_global']'
        for metric in entropy_metrics:
            if metric in self.metrics_history:
                entropy_data = self.metrics_history[metric]
                self.entropy_line.set_data(x_data, entropy_data)
                self.ax_entropy.relim()
                self.ax_entropy.autoscale_view()
                break

        # Update other metrics plot (use compression ratio if available)
        if 'lz77_ratio' in self.metrics_history:'
            other_data = self.metrics_history['lz77_ratio']'
            self.other_line.set_data(x_data, other_data)
            self.ax_other.relim()
            self.ax_other.autoscale_view()

        # Refresh canvas
        self.chart_canvas.draw()

    def update_performance(self, ops_per_sec: float, memory_mb: float, elapsed_seconds: float):
        """Update performance metrics.""""
        self.ops_per_sec_var.set(f"{ops_per_sec:.1f}")"
        self.memory_var.set(f"{memory_mb:.1f} MB")"

        # Format time
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        self.time_var.set(f"{minutes:02d}:{seconds:02d}")"

    def clear(self):
        """Clear all metrics and reset display.""""
        self.current_metrics = {}
        self.initial_metrics = {}
        self.metrics_history = {}

        # Clear displays
        for widget in self.metrics_inner_frame.winfo_children():
            widget.destroy()

        self.score_var.set("Score: 0.000")"
        self.score_change_var.set("")"

        # Clear charts
        self.score_line.set_data([], [])
        self.entropy_line.set_data([], [])
        self.other_line.set_data([], [])

        self.ax_score.relim()
        self.ax_score.autoscale_view()
        self.ax_entropy.relim()
        self.ax_entropy.autoscale_view()
        self.ax_other.relim()
        self.ax_other.autoscale_view()

        self.chart_canvas.draw()

        # Reset performance metrics
        self.ops_per_sec_var.set("0.0")"
        self.memory_var.set("0 MB")"
        self.time_var.set("00:00")"