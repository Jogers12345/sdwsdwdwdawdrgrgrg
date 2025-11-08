"""
Transformation Viewer Component for BSEE

Interactive component to replay analysis with step-by-step visualization.
Shows side-by-side comparison of binary data before and after each transformation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import colorsys

from gui.animation.operation_animator import OperationAnimator
from bsee.engine.history import HistoryManager


@dataclass
class OperationStep:
    """Represents a single step in the transformation sequence."""
    step_number: int
    operation_name: str
    operation_params: Dict[str, Any]
    before_data: bytes
    after_data: bytes
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    timing_info: Dict[str, float]
    byte_changes: List[Tuple[int, int, int]]  # (index, old_value, new_value)


class TransformationViewer(tk.Frame):
    """Interactive transformation viewer with step-by-step replay."""

    def __init__(self, parent, history_manager: Optional[HistoryManager] = None):
        """
        Initialize transformation viewer.

        Args:
            parent: Parent widget
            history_manager: History manager for loading analysis data
        """
        super().__init__(parent)

        self.history_manager = history_manager
        self.operation_steps: List[OperationStep] = []
        self.current_step_index = -1
        self.is_playing = False
        self.replay_speed = 1.0
        self.animation_thread = None

        # Animation components
        self.animator = OperationAnimator(self)

        # UI state
        self.before_display = None
        self.after_display = None
        self.status_var = tk.StringVar(value="No analysis loaded")
        self.step_var = tk.StringVar(value="Step 0/0")
        self.operation_var = tk.StringVar(value="No operation selected")
        self.progress_var = tk.DoubleVar(value=0)

        self._create_widgets()
        self._setup_bindings()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control Panel
        control_frame = ttk.LabelFrame(main_container, text="Replay Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self._create_control_panel(control_frame)

        # Content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create paned window for before/after comparison
        paned_window = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel - Before Transformation
        left_frame = ttk.LabelFrame(paned_window, text="Before Transformation", padding=5)
        paned_window.add(left_frame, weight=1)
        self._create_display_panel(left_frame, "before")

        # Right panel - After Transformation
        right_frame = ttk.LabelFrame(paned_window, text="After Transformation", padding=5)
        paned_window.add(right_frame, weight=1)
        self._create_display_panel(right_frame, "after")

        # Bottom panel - Operation Details
        details_frame = ttk.LabelFrame(main_container, text="Operation Details", padding=10)
        details_frame.pack(fill=tk.X, pady=(10, 0))

        self._create_details_panel(details_frame)

    def _create_control_panel(self, parent):
        """Create control panel with playback controls."""
        # Playback controls row
        controls_row = ttk.Frame(parent)
        controls_row.pack(fill=tk.X, pady=(0, 10))

        # Play/Pause button
        self.play_button = ttk.Button(controls_row, text="▶ Play", command=self.toggle_playback)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))

        # Step controls
        ttk.Button(controls_row, text="⏮ Step Back", command=self.step_backward).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_row, text="Step Forward ⏭", command=self.step_forward).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_row, text="↺ Reset", command=self.reset_replay).pack(side=tk.LEFT, padx=(10, 2))

        # Speed control
        ttk.Label(controls_row, text="Speed:").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(controls_row, from_=0.1, to=5.0, variable=self.speed_var,
                               orient=tk.HORIZONTAL, length=150, command=self._on_speed_change)
        speed_scale.pack(side=tk.LEFT, padx=2)
        self.speed_label = ttk.Label(controls_row, text="1.0x")
        self.speed_label.pack(side=tk.LEFT, padx=(2, 10))

        # Progress bar
        ttk.Label(controls_row, text="Progress:").pack(side=tk.LEFT, padx=(10, 5))
        self.progress_bar = ttk.Progressbar(controls_row, variable=self.progress_var,
                                          length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=2)

        # Status display
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)

        ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.step_var, font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(status_frame, textvariable=self.operation_var, font=('Arial', 10, 'italic')).pack(side=tk.RIGHT, padx=(10, 0))

    def _create_display_panel(self, parent, panel_type):
        """Create hex display panel."""
        # Display mode selector
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(mode_frame, text="Display Mode:").pack(side=tk.LEFT)
        mode_var = tk.StringVar(value="hex")
        mode_combo = ttk.Combobox(mode_frame, textvariable=mode_var, width=15,
                                 values=["hex", "binary", "decimal", "ascii", "mixed", "heatmap", "frequency"],
                                 state="readonly")
        mode_combo.pack(side=tk.LEFT, padx=(5, 0))
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self._change_display_mode(panel_type, mode_var.get()))

        # Hex display with scrollbar
        display_frame = ttk.Frame(parent)
        display_frame.pack(fill=tk.BOTH, expand=True)

        # Create text widget with custom styling
        text_widget = scrolledtext.ScrolledText(display_frame, wrap=tk.NONE,
                                              font=('Consolas', 10), height=20,
                                              bg='#1e1e1e', fg='#00ff00',
                                              insertbackground='#00ff00',
                                              selectbackground='#444444')
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for highlighting
        self._configure_text_tags(text_widget)

        # Store reference
        if panel_type == "before":
            self.before_display = text_widget
        else:
            self.after_display = text_widget

        # Sync scrolling
        text_widget.bind("<MouseWheel>", lambda e: self._sync_scrolling(panel_type, e))
        text_widget.bind("<Button-4>", lambda e: self._sync_scrolling(panel_type, e))  # Linux
        text_widget.bind("<Button-5>", lambda e: self._sync_scrolling(panel_type, e))  # Linux

    def _create_details_panel(self, parent):
        """Create operation details panel."""
        # Create notebook for different detail views
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Operation info tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Operation Info")

        self._create_operation_info(info_frame)

        # Metrics tab
        metrics_frame = ttk.Frame(notebook)
        notebook.add(metrics_frame, text="Metrics")

        self._create_metrics_display(metrics_frame)

        # Byte changes tab
        changes_frame = ttk.Frame(notebook)
        notebook.add(changes_frame, text="Byte Changes")

        self._create_byte_changes_display(changes_frame)

    def _create_operation_info(self, parent):
        """Create operation information display."""
        info_container = ttk.Frame(parent)
        info_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Operation name and parameters
        ttk.Label(info_container, text="Operation:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.operation_name_label = ttk.Label(info_container, text="None")
        self.operation_name_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(info_container, text="Parameters:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.parameters_text = tk.Text(info_container, height=4, width=50, wrap=tk.WORD)
        self.parameters_text.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(10, 0))

        # Timing information
        ttk.Label(info_container, text="Execution Time:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.timing_label = ttk.Label(info_container, text="N/A")
        self.timing_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # Data size information
        ttk.Label(info_container, text="Data Size:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.size_label = ttk.Label(info_container, text="N/A")
        self.size_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # Bytes changed
        ttk.Label(info_container, text="Bytes Changed:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.bytes_changed_label = ttk.Label(info_container, text="N/A")
        self.bytes_changed_label.grid(row=4, column=1, sticky=tk.W, padx=(10, 0))

    def _create_metrics_display(self, parent):
        """Create metrics comparison display."""
        metrics_container = ttk.Frame(parent)
        metrics_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for metrics comparison
        columns = ('metric', 'before', 'after', 'change')
        self.metrics_tree = ttk.Treeview(metrics_container, columns=columns, show='headings', height=10)

        # Define column headings
        self.metrics_tree.heading('metric', text='Metric')
        self.metrics_tree.heading('before', text='Before')
        self.metrics_tree.heading('after', text='After')
        self.metrics_tree.heading('change', text='Change')

        # Configure column widths
        self.metrics_tree.column('metric', width=150)
        self.metrics_tree.column('before', width=100)
        self.metrics_tree.column('after', width=100)
        self.metrics_tree.column('change', width=100)

        self.metrics_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(metrics_container, orient=tk.VERTICAL, command=self.metrics_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.metrics_tree.configure(yscrollcommand=scrollbar.set)

    def _create_byte_changes_display(self, parent):
        """Create byte changes display."""
        changes_container = ttk.Frame(parent)
        changes_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for byte changes
        columns = ('offset', 'address', 'old_value', 'new_value', 'change_type')
        self.changes_tree = ttk.Treeview(changes_container, columns=columns, show='headings', height=10)

        # Define column headings
        self.changes_tree.heading('offset', text='Offset')
        self.changes_tree.heading('address', text='Address')
        self.changes_tree.heading('old_value', text='Old Value')
        self.changes_tree.heading('new_value', text='New Value')
        self.changes_tree.heading('change_type', text='Type')

        # Configure column widths
        self.changes_tree.column('offset', width=60)
        self.changes_tree.column('address', width=80)
        self.changes_tree.column('old_value', width=80)
        self.changes_tree.column('new_value', width=80)
        self.changes_tree.column('change_type', width=80)

        self.changes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(changes_container, orient=tk.VERTICAL, command=self.changes_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.changes_tree.configure(yscrollcommand=scrollbar.set)

        # Bind double-click to highlight in hex display
        self.changes_tree.bind('<Double-Button-1>', self._on_byte_change_click)

    def _configure_text_tags(self, text_widget):
        """Configure text tags for syntax highlighting and animations."""
        # Color scheme for different byte values
        text_widget.tag_configure('normal', foreground='#00ff00')
        text_widget.tag_configure('changed', foreground='#ff0000', background='#440000')
        text_widget.tag_configure('modified', foreground='#ffff00', background='#444400')
        text_widget.tag_configure('inserted', foreground='#00ffff', background='#004444')
        text_widget.tag_configure('deleted', foreground='#ff00ff', background='#440044')
        text_widget.tag_configure('address', foreground='#808080')
        text_widget.tag_configure('ascii', foreground='#808080')
        text_widget.tag_configure('heatmap_rare', foreground='#ff0000')
        text_widget.tag_configure('heatmap_common', foreground='#0000ff')
        text_widget.tag_configure('highlight', background='#666666')

    def _setup_bindings(self):
        """Setup keyboard shortcuts and event bindings."""
        self.bind('<Control-space>', lambda e: self.toggle_playback())
        self.bind('<Left>', lambda e: self.step_backward())
        self.bind('<Right>', lambda e: self.step_forward())
        self.bind('<Home>', lambda e: self.reset_replay())
        self.bind('<Escape>', lambda e: self.stop_playback())

    def load_analysis_history(self, history_data: Dict[str, Any]):
        """
        Load complete analysis for replay.

        Args:
            history_data: Dictionary containing analysis history and metadata
        """
        try:
            self.operation_steps.clear()
            self.current_step_index = -1

            # Parse history data into OperationStep objects
            operations = history_data.get('operations', [])
            for i, op_data in enumerate(operations):
                step = OperationStep(
                    step_number=i,
                    operation_name=op_data.get('name', 'unknown'),
                    operation_params=op_data.get('params', {}),
                    before_data=bytes.fromhex(op_data.get('before_hex', '')),
                    after_data=bytes.fromhex(op_data.get('after_hex', '')),
                    metrics_before=op_data.get('metrics_before', {}),
                    metrics_after=op_data.get('metrics_after', {}),
                    timing_info=op_data.get('timing', {}),
                    byte_changes=self._analyze_byte_changes(
                        bytes.fromhex(op_data.get('before_hex', '')),
                        bytes.fromhex(op_data.get('after_hex', ''))
                    )
                )
                self.operation_steps.append(step)

            # Update UI state
            self.status_var.set(f"Loaded {len(self.operation_steps)} operations")
            self._update_step_display()
            self.reset_replay()

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load analysis history: {e}")

    def _analyze_byte_changes(self, before: bytes, after: bytes) -> List[Tuple[int, int, int]]:
        """Analyze byte changes between before and after data."""
        changes = []
        min_len = min(len(before), len(after))

        # Find changed bytes
        for i in range(min_len):
            if before[i] != after[i]:
                changes.append((i, before[i], after[i]))

        # Handle insertions/deletions
        if len(before) < len(after):
            # Insertions
            for i in range(len(before), len(after)):
                changes.append((i, -1, after[i]))  # -1 indicates insertion
        elif len(before) > len(after):
            # Deletions
            for i in range(len(after), len(before)):
                changes.append((i, before[i], -1))  # -1 indicates deletion

        return changes

    def toggle_playback(self):
        """Toggle between play and pause states."""
        if self.is_playing:
            self.stop_playback()
        else:
            self.play_replay()

    def play_replay(self):
        """Start automatic replay with speed control."""
        if not self.operation_steps:
            messagebox.showwarning("No Data", "No analysis data loaded for replay")
            return

        self.is_playing = True
        self.play_button.config(text="⏸ Pause")
        self.status_var.set("Playing...")

        # Start animation thread
        self.animation_thread = threading.Thread(target=self._replay_worker, daemon=True)
        self.animation_thread.start()

    def stop_playback(self):
        """Stop automatic replay."""
        self.is_playing = False
        self.play_button.config(text="▶ Play")
        self.status_var.set("Paused")

    def _replay_worker(self):
        """Worker thread for automatic replay."""
        while self.is_playing and self.current_step_index < len(self.operation_steps) - 1:
            self.after(0, self.step_forward)
            time.sleep(1.0 / self.replay_speed)

        if self.is_playing:
            self.after(0, self.stop_playback)

    def step_forward(self):
        """Move to next operation with animation."""
        if not self.operation_steps:
            return

        if self.current_step_index < len(self.operation_steps) - 1:
            self.current_step_index += 1
            self._show_current_step()

    def step_backward(self):
        """Move to previous operation."""
        if not self.operation_steps:
            return

        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._show_current_step()

    def reset_replay(self):
        """Return to initial state."""
        self.current_step_index = -1
        self.stop_playback()

        if self.operation_steps:
            # Show initial state
            initial_data = self.operation_steps[0].before_data
            self._display_data(self.before_display, initial_data, "hex")
            self._display_data(self.after_display, initial_data, "hex")

        self._update_step_display()
        self.status_var.set("Reset to initial state")

    def _show_current_step(self):
        """Display current operation step with animations."""
        if not self.operation_steps or self.current_step_index < 0:
            return

        step = self.operation_steps[self.current_step_index]

        # Update displays
        self._display_data(self.before_display, step.before_data, "hex")
        self._display_data(self.after_display, step.after_data, "hex")

        # Animate changes
        self.animator.animate_byte_changes(step.byte_changes, self.after_display)

        # Update details panels
        self._update_operation_details(step)
        self._update_metrics_display(step)
        self._update_byte_changes_display(step)

        # Update UI state
        self._update_step_display()

        # Update status
        if self.is_playing:
            self.status_var.set(f"Playing: {step.operation_name}")
        else:
            self.status_var.set(f"Step {self.current_step_index + 1}: {step.operation_name}")

    def _display_data(self, text_widget, data: bytes, display_mode: str):
        """Display binary data in specified format."""
        text_widget.delete(1.0, tk.END)

        if display_mode == "hex":
            self._display_hex(text_widget, data)
        elif display_mode == "binary":
            self._display_binary(text_widget, data)
        elif display_mode == "decimal":
            self._display_decimal(text_widget, data)
        elif display_mode == "ascii":
            self._display_ascii(text_widget, data)
        elif display_mode == "mixed":
            self._display_mixed(text_widget, data)
        elif display_mode == "heatmap":
            self._display_heatmap(text_widget, data)
        elif display_mode == "frequency":
            self._display_frequency(text_widget, data)

    def _display_hex(self, text_widget, data: bytes):
        """Display data in hexadecimal format."""
        for i in range(0, len(data), 16):
            # Address
            addr_text = f"{i:08x}: "
            text_widget.insert(tk.END, addr_text, 'address')

            # Hex bytes
            hex_bytes = []
            for j in range(16):
                if i + j < len(data):
                    byte_val = data[i + j]
                    hex_bytes.append(f"{byte_val:02x}")

                    # Insert space every 4 bytes
                    if j == 7:
                        hex_bytes.append(" ")
                else:
                    hex_bytes.append("  ")

            hex_text = " ".join(hex_bytes)
            text_widget.insert(tk.END, hex_text, 'normal')

            # ASCII representation
            text_widget.insert(tk.END, "  ", 'address')
            ascii_text = ""
            for j in range(16):
                if i + j < len(data):
                    byte_val = data[i + j]
                    if 32 <= byte_val <= 126:
                        ascii_text += chr(byte_val)
                    else:
                        ascii_text += "."
                else:
                    ascii_text += " "

            text_widget.insert(tk.END, ascii_text, 'ascii')
            text_widget.insert(tk.END, "\n")

    def _display_binary(self, text_widget, data: bytes):
        """Display data in binary format."""
        for i in range(0, len(data), 8):
            addr_text = f"{i:08x}: "
            text_widget.insert(tk.END, addr_text, 'address')

            for j in range(8):
                if i + j < len(data):
                    byte_val = data[i + j]
                    binary_text = f"{byte_val:08b} "
                    text_widget.insert(tk.END, binary_text, 'normal')
                else:
                    text_widget.insert(tk.END, "         ", 'normal')

            text_widget.insert(tk.END, "\n")

    def _display_decimal(self, text_widget, data: bytes):
        """Display data in decimal format."""
        for i in range(0, len(data), 8):
            addr_text = f"{i:08x}: "
            text_widget.insert(tk.END, addr_text, 'address')

            for j in range(8):
                if i + j < len(data):
                    byte_val = data[i + j]
                    decimal_text = f"{byte_val:3d} "
                    text_widget.insert(tk.END, decimal_text, 'normal')
                else:
                    text_widget.insert(tk.END, "    ", 'normal')

            text_widget.insert(tk.END, "\n")

    def _display_ascii(self, text_widget, data: bytes):
        """Display data as ASCII characters."""
        for i in range(0, len(data), 16):
            addr_text = f"{i:08x}: "
            text_widget.insert(tk.END, addr_text, 'address')

            ascii_line = ""
            for j in range(16):
                if i + j < len(data):
                    byte_val = data[i + j]
                    if 32 <= byte_val <= 126:
                        ascii_line += chr(byte_val)
                    else:
                        ascii_line += "."
                else:
                    ascii_line += " "

            text_widget.insert(tk.END, ascii_line, 'ascii')
            text_widget.insert(tk.END, "\n")

    def _display_mixed(self, text_widget, data: bytes):
        """Display data in mixed hex + ASCII format (like hex editors)."""
        self._display_hex(text_widget, data)  # Use hex display for now

    def _display_heatmap(self, text_widget, data: bytes):
        """Display data as frequency-based heatmap."""
        # Calculate byte frequencies
        freq = [0] * 256
        for byte_val in data:
            freq[byte_val] += 1

        # Normalize frequencies
        max_freq = max(freq) if max(freq) > 0 else 1

        # Create 32x32 grid for first 1024 bytes
        grid_size = 32
        display_data = data[:grid_size * grid_size]

        for row in range(grid_size):
            for col in range(grid_size):
                idx = row * grid_size + col
                if idx < len(display_data):
                    byte_val = display_data[idx]
                    normalized_freq = freq[byte_val] / max_freq

                    # Color based on frequency
                    if normalized_freq > 0.7:
                        tag = 'heatmap_common'
                    elif normalized_freq < 0.3:
                        tag = 'heatmap_rare'
                    else:
                        tag = 'normal'

                    text_widget.insert(tk.END, f"{byte_val:02x} ", tag)
                else:
                    text_widget.insert(tk.END, "   ", 'normal')

            text_widget.insert(tk.END, "\n")

    def _display_frequency(self, text_widget, data: bytes):
        """Display byte frequency distribution."""
        # Calculate frequencies
        freq = [0] * 256
        for byte_val in data:
            freq[byte_val] += 1

        # Create bar chart visualization
        max_freq = max(freq) if max(freq) > 0 else 1

        for byte_val in range(0, 256, 4):  # Show in groups of 4
            group_freq = sum(freq[byte_val:byte_val+4])
            bar_length = int(group_freq / max_freq * 30)

            text_widget.insert(tk.END, f"{byte_val:02x}-{min(byte_val+3,255):02x}: ", 'address')
            text_widget.insert(tk.END, "█" * bar_length, 'normal')
            text_widget.insert(tk.END, f" ({group_freq})\n")

    def _update_operation_details(self, step: OperationStep):
        """Update operation details panel."""
        self.operation_name_label.config(text=step.operation_name)
        self.operation_var.set(f"Step {step.step_number + 1}: {step.operation_name}")

        # Update parameters
        self.parameters_text.delete(1.0, tk.END)
        for param, value in step.operation_params.items():
            self.parameters_text.insert(tk.END, f"{param}: {value}\n")

        # Update timing
        exec_time = step.timing_info.get('execution_time', 0)
        self.timing_label.config(text=f"{exec_time:.4f} seconds")

        # Update size information
        before_size = len(step.before_data)
        after_size = len(step.after_data)
        size_change = after_size - before_size
        size_text = f"{before_size} → {after_size} bytes"
        if size_change != 0:
            size_text += f" ({size_change:+d})"
        self.size_label.config(text=size_text)

        # Update bytes changed
        changed_count = len(step.byte_changes)
        self.bytes_changed_label.config(text=f"{changed_count} bytes")

    def _update_metrics_display(self, step: OperationStep):
        """Update metrics comparison display."""
        # Clear existing items
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        # Add metrics comparison
        all_metrics = set(step.metrics_before.keys()) | set(step.metrics_after.keys())

        for metric in sorted(all_metrics):
            before_val = step.metrics_before.get(metric, 0)
            after_val = step.metrics_after.get(metric, 0)
            change = after_val - before_val

            # Format values
            before_str = f"{before_val:.4f}"
            after_str = f"{after_val:.4f}"
            change_str = f"{change:+.4f}"

            # Color code based on improvement
            tags = ()
            if change > 0:
                tags = ('improvement',)
            elif change < 0:
                tags = ('degradation',)

            self.metrics_tree.insert('', 'end', values=(metric, before_str, after_str, change_str), tags=tags)

    def _update_byte_changes_display(self, step: OperationStep):
        """Update byte changes display."""
        # Clear existing items
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)

        # Add byte changes
        for offset, old_val, new_val in step.byte_changes:
            addr_hex = f"0x{offset:08x}"

            if old_val == -1:  # Insertion
                old_str = "N/A"
                new_str = f"0x{new_val:02x}"
                change_type = "Insertion"
                tags = ('insertion',)
            elif new_val == -1:  # Deletion
                old_str = f"0x{old_val:02x}"
                new_str = "N/A"
                change_type = "Deletion"
                tags = ('deletion',)
            else:  # Modification
                old_str = f"0x{old_val:02x}"
                new_str = f"0x{new_val:02x}"
                change_type = "Modified"
                tags = ('modified',)

            self.changes_tree.insert('', 'end', values=(
                offset, addr_hex, old_str, new_str, change_type
            ), tags=tags)

    def _update_step_display(self):
        """Update step counter and progress bar."""
        if self.operation_steps:
            total_steps = len(self.operation_steps)
            current_step = max(0, self.current_step_index + 1)
            self.step_var.set(f"Step {current_step}/{total_steps}")

            # Update progress bar
            if total_steps > 0:
                progress = (current_step / total_steps) * 100
                self.progress_var.set(progress)
        else:
            self.step_var.set("Step 0/0")
            self.progress_var.set(0)

    def _on_speed_change(self, value):
        """Handle speed slider change."""
        self.replay_speed = float(value)
        self.speed_label.config(text=f"{self.replay_speed:.1f}x")

    def _change_display_mode(self, panel_type: str, mode: str):
        """Change display mode for specified panel."""
        display = self.before_display if panel_type == "before" else self.after_display

        # Get current data
        if self.current_step_index >= 0 and self.operation_steps:
            step = self.operation_steps[self.current_step_index]
            data = step.before_data if panel_type == "before" else step.after_data
        else:
            data = b""

        # Redisplay with new mode
        self._display_data(display, data, mode)

    def _sync_scrolling(self, source_panel: str, event):
        """Synchronize scrolling between before/after panels."""
        # This would implement synchronized scrolling between panels
        # Implementation depends on the specific scrolling event
        pass

    def _on_byte_change_click(self, event):
        """Handle double-click on byte change item."""
        selection = self.changes_tree.selection()
        if selection:
            item = self.changes_tree.item(selection[0])
            values = item['values']
            if values:
                offset = int(values[0])
                self._highlight_byte_in_display(offset)

    def _highlight_byte_in_display(self, offset: int):
        """Highlight specific byte in hex displays."""
        # Calculate line and column for the offset
        line = offset // 16
        col = (offset % 16) * 3  # 2 hex chars + space

        # Highlight in both displays
        for display in [self.before_display, self.after_display]:
            try:
                # Clear previous highlights
                display.tag_remove('highlight', '1.0', tk.END)

                # Add new highlight
                start_pos = f"{line + 1}.{col + 10}"  # +10 for address prefix
                end_pos = f"{line + 1}.{col + 12}"
                display.tag_add('highlight', start_pos, end_pos)

                # Scroll to position
                display.see(start_pos)
            except:
                pass  # Ignore positioning errors

    def show_transformation(self, operation_index: int):
        """Display specific operation changes."""
        if 0 <= operation_index < len(self.operation_steps):
            self.current_step_index = operation_index
            self._show_current_step()

    def highlight_changed_bytes(self, before_data: bytes, after_data: bytes):
        """Animate byte differences between before and after data."""
        changes = self._analyze_byte_changes(before_data, after_data)
        self.animator.animate_byte_changes(changes, self.after_display)

    def get_current_step(self) -> Optional[OperationStep]:
        """Get current operation step."""
        if 0 <= self.current_step_index < len(self.operation_steps):
            return self.operation_steps[self.current_step_index]
        return None

    def set_animation_speed(self, speed: float):
        """Control animation timing."""
        self.replay_speed = max(0.1, min(5.0, speed))
        self.speed_var.set(self.replay_speed)
        self.speed_label.config(text=f"{self.replay_speed:.1f}x")