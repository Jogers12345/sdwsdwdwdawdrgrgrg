"""
Enhanced Binary Operation Player for BSEE GUI
Provides playback and visualization of binary transformations.
"""

import tkinter as tk
from tkinter import ttk, Canvas, Frame, Label, Button, Scale
import time
import threading
import queue
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class EnhancedOperationPlayer:
    """Enhanced binary operation player with playback capabilities."""

    def __init__(self, parent, callback=None):
        """Initialize enhanced operation player."""
        self.parent = parent
        self.callback = callback
        self.operation_history = []
        self.current_index = 0
        self.is_playing = False
        self.playback_speed = 1.0  # 1.0 = normal speed
        self.auto_loop = False

        self._setup_ui()
        self._setup_controls()

    def _setup_ui(self):
        """Setup the player UI."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Player controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Operation Player")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        # Playback controls
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Control buttons with modern styling
        self.btn_prev = ttk.Button(button_frame, text="◀◀ Previous", width=15,
                                    command=self._prev_operation)
        self.btn_prev.pack(side=tk.LEFT, padx=2)

        self.btn_play = ttk.Button(button_frame, text="▶ Play", width=10,
                                    command=self._toggle_playback)
        self.btn_play.pack(side=tk.LEFT, padx=2)

        self.btn_stop = ttk.Button(button_frame, text="■ Stop", width=10,
                                    command=self._stop_playback)
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        self.btn_next = ttk.Button(button_frame, text="Next ▶▶", width=15,
                                    command=self._next_operation)
        self.btn_next.pack(side=tk.LEFT, padx=2)

        # Loop control
        self.loop_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(button_frame, text="🔁 Loop", variable=self.loop_var,
                     command=self._toggle_loop).pack(side=tk.LEFT, padx=10)

        # Speed control
        speed_frame = ttk.Frame(controls_frame)
        speed_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.speed_var,
                                  orient=tk.HORIZONTAL, length=200)
        self.speed_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.LEFT, padx=5)

        # Bind speed change
        self.speed_var.trace("w", self._on_speed_change)

        # Progress frame
        progress_frame = ttk.Frame(controls_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                         maximum=100, length=200)
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Position label
        self.position_label = ttk.Label(progress_frame, text="0 / 0")
        self.position_label.pack(side=tk.LEFT, padx=5)

        # Visualization canvas
        viz_frame = ttk.LabelFrame(main_frame, text="Operation Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = Canvas(viz_frame, bg="black", fg="green",
                          font=("Courier New", 9))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind canvas events
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _setup_controls(self):
        """Setup additional controls."""
        # Keyboard shortcuts
        self.parent.bind("<space>", self._toggle_playback)
        self.parent.bind("<Left>", self._prev_operation)
        self.parent.bind("<Right>", self._next_operation)
        self.parent.bind("<Home>", self._first_operation)
        self.parent.bind("<End>", self._last_operation)
        self.parent.bind("<Control-l>", self._toggle_loop)

    def load_operation_history(self, operations: List[Dict[str, Any]]):
        """Load operation history for playback."""
        self.operation_history = operations
        self.current_index = 0
        self.progress_var.set(0)
        self._update_position_label()
        self._visualize_operation()

    def _toggle_playback(self):
        """Toggle playback state."""
        if self.is_playing:
            self._stop_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        """Start operation playback."""
        if not self.operation_history:
            return

        self.is_playing = True
        self.btn_play.config(text="⏸ Pause")
        self._playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self._playback_thread.start()

    def _stop_playback(self):
        """Stop operation playback."""
        self.is_playing = False
        self.btn_play.config(text="▶ Play")

    def _toggle_loop(self):
        """Toggle loop mode."""
        self.auto_loop = self.loop_var.get()

    def _prev_operation(self):
        """Go to previous operation."""
        if self.operation_history and self.current_index > 0:
            self.current_index -= 1
            self._update_position()
            self._visualize_operation()

    def _next_operation(self):
        """Go to next operation."""
        if self.operation_history and self.current_index < len(self.operation_history) - 1:
            self.current_index += 1
            self._update_position()
            self._visualize_operation()

    def _first_operation(self):
        """Go to first operation."""
        if self.operation_history:
            self.current_index = 0
            self._update_position()
            self._visualize_operation()

    def _last_operation(self):
        """Go to last operation."""
        if self.operation_history:
            self.current_index = len(self.operation_history) - 1
            self._update_position()
            self._visualize_operation()

    def _update_position(self):
        """Update position display and progress."""
        self.progress_var.set(int((self.current_index + 1) / len(self.operation_history) * 100))
        self._update_position_label()

    def _update_position_label(self):
        """Update position label."""
        current = self.current_index + 1
        total = len(self.operation_history)
        self.position_label.config(text=f"{current} / {total}")

    def _on_speed_change(self, *args):
        """Handle speed change."""
        self.playback_speed = self.speed_var.get()
        self.speed_label.config(text=f"{self.playback_speed:.1f}x")

    def _playback_loop(self):
        """Main playback loop."""
        while self.is_playing:
            if self.current_index >= len(self.operation_history) - 1:
                if self.auto_loop:
                    self.current_index = 0
                else:
                    self._stop_playback()
                    self.parent.after(0, lambda: self.position_label.config(text="Playback completed"))
                    break
            else:
                self.current_index += 1

            # Update UI from main thread
            self.parent.after(0, self._update_position)
            self.parent.after(0, self._visualize_operation)

            # Wait based on speed (1000ms = normal speed)
            delay = 1.0 / self.playback_speed
            time.sleep(delay)

    def _visualize_operation(self):
        """Visualize current operation on canvas."""
        if not self.operation_history or self.current_index >= len(self.operation_history):
            self.canvas.delete("all")
            return

        operation = self.operation_history[self.current_index]
        self.canvas.delete("all")

        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Draw operation visualization
        self._draw_operation_summary(operation, width, height)

    def _draw_operation_summary(self, operation: Dict[str, Any], width: int, height: int):
        """Draw a summary of the operation."""
        # Clear canvas
        self.canvas.delete("all")

        # Title
        operation_name = operation.get('operation', 'Unknown')
        self.canvas.create_text(width // 2, 30,
                               text=f"Operation: {operation_name}",
                               font=("Arial", 12, "bold"),
                               fill="white", anchor=tk.CENTER)

        # Parameters
        params = operation.get('params', {})
        if params:
            param_text = f"Parameters: {params}"
            # Wrap text if too long
            lines = self._wrap_text(param_text, width - 40)
            y_offset = 60
            for line in lines:
                self.canvas.create_text(20, y_offset,
                                       text=line,
                                       font=("Courier New", 10),
                                       fill="lightgreen", anchor=tk.W)
                y_offset += 20

        # Cost and timestamp
        cost = operation.get('cost', 0)
        timestamp = operation.get('timestamp', 'Unknown')

        info_y = height - 100
        self.canvas.create_text(20, info_y,
                               text=f"Cost: {cost:.3f}",
                               font=("Arial", 10),
                               fill="yellow", anchor=tk.W)

        self.canvas.create_text(20, info_y + 20,
                               text=f"Time: {timestamp}",
                               font=("Arial", 9),
                               fill="lightblue", anchor=tk.W)

        # Score improvement if available
        if 'score_improvement' in operation:
            improvement = operation['score_improvement']
            if isinstance(improvement, dict) and 'file_ideality_score' in improvement:
                score_change = improvement['file_ideality_score']
                color = "lightgreen" if score_change > 0 else "lightred" if score_change < 0 else "white"
                self.canvas.create_text(width - 20, info_y + 40,
                                       text=f"Score Change: {score_change:+.3f}",
                                       font=("Arial", 10, "bold"),
                                       fill=color, anchor=tk.E)

        # Visual effect border
        self.canvas.create_rectangle(10, 50, width - 10, height - 50,
                                 outline="green", width=2)

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            # Approximate width (assuming monospace font, 8 pixels per character)
            if len(test_line) * 8 > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        else:
            current_line = test_line

        if current_line:
            lines.append(current_line)

        return lines

    def _on_canvas_resize(self, event):
        """Handle canvas resize."""
        self._visualize_operation()

    def get_current_operation(self) -> Optional[Dict[str, Any]]:
        """Get current operation."""
        if self.operation_history and 0 <= self.current_index < len(self.operation_history):
            return self.operation_history[self.current_index]
        return None