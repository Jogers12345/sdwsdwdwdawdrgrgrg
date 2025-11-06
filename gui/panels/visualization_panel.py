"""
Real-time visualization panel for bit-level operations.
"""

import tkinter as tk
from tkinter import ttk, Canvas
from typing import Dict, Any, Optional, List
import colorsys


class VisualizationPanel:
    """Panel for displaying binary data and operation effects."""

    def __init__(self, parent):
        """Initialize visualization panel."""
        self.frame = ttk.LabelFrame(parent, text="Binary Visualization", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.current_data: Optional[bytes] = None
        self.operation_data: Optional[Dict[str, Any]] = None
        self.offset = 0
        self.bytes_per_row = 16
        self.max_rows = 20  # Maximum rows to display
        self.highlighted_bytes: List[int] = []

        self._create_widgets()

    def _create_widgets(self):
        """Create visualization widgets."""
        # Control toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # Navigation controls
        ttk.Label(toolbar, text="Offset:").pack(side=tk.LEFT, padx=(0, 5))
        self.offset_var = tk.StringVar(value="0")
        self.offset_spin = ttk.Spinbox(toolbar, from_=0, to=999999, textvariable=self.offset_var,
                                       width=10, command=self._on_offset_change)
        self.offset_spin.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="←", command=self._scroll_up, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="→", command=self._scroll_down, width=3).pack(side=tk.LEFT, padx=1)

        # Zoom controls
        ttk.Label(toolbar, text="Bytes/Row:").pack(side=tk.LEFT, padx=(10, 5))
        self.bytes_per_row_var = tk.StringVar(value="16")
        bytes_options = ["8", "16", "32", "64"]
        self.bytes_combo = ttk.Combobox(toolbar, textvariable=self.bytes_per_row_var,
                                       values=bytes_options, width=5, state="readonly")
        self.bytes_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.bytes_combo.bind('<<ComboboxSelected>>', self._on_bytes_per_row_change)

        # Display mode
        ttk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=(10, 5))
        self.display_mode_var = tk.StringVar(value="hex")
        display_modes = ["hex", "binary", "decimal", "ascii"]
        self.display_mode_combo = ttk.Combobox(toolbar, textvariable=self.display_mode_var,
                                              values=display_modes, width=8, state="readonly")
        self.display_mode_combo.pack(side=tk.LEFT)

        # Main visualization canvas with scrollbars
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = Canvas(canvas_frame, bg="black")
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Bind mouse events
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-1>", self._on_click)

        # Info panel
        info_frame = ttk.LabelFrame(self.frame, text="Operation Info", padding=5)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.operation_label = ttk.Label(info_frame, text="No operation in progress",
                                       font=("TkDefaultFont", 9))
        self.operation_label.pack(anchor=tk.W)

        self.details_label = ttk.Label(info_frame, text="", font=("TkDefaultFont", 8),
                                      foreground="gray")
        self.details_label.pack(anchor=tk.W)

    def update_display(self, message: Dict[str, Any]):
        """Update visualization with new data."""
        if 'binary_data' in message:
            self.current_data = message['binary_data']
            self._redraw_display()

        if 'operation' in message:
            self.operation_data = message['operation']
            self._update_operation_info()

        if 'changes' in message:
            self.highlighted_bytes = message['changes']
            self._redraw_display()

        if 'offset' in message:
            self.offset = message['offset']
            self.offset_var.set(str(self.offset))

    def _redraw_display(self):
        """Redraw the binary display."""
        self.canvas.delete("all")

        if not self.current_data:
            self._draw_no_data()
            return

        display_mode = self.display_mode_var.get()
        bytes_per_row = int(self.bytes_per_row_var.get())

        # Calculate display range
        start_byte = self.offset
        end_byte = min(len(self.current_data), start_byte + (bytes_per_row * self.max_rows))

        if start_byte >= len(self.current_data):
            start_byte = max(0, len(self.current_data) - bytes_per_row)
            end_byte = len(self.current_data)
            self.offset_var.set(str(start_byte))

        # Draw header
        self._draw_header(bytes_per_row)

        # Draw data rows
        for row in range((end_byte - start_byte + bytes_per_row - 1) // bytes_per_row):
            row_start = start_byte + row * bytes_per_row
            row_end = min(row_start + bytes_per_row, end_byte)

            if row_start >= len(self.current_data):
                break

            self._draw_row(row, row_start, row_end, display_mode, bytes_per_row)

        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _draw_no_data(self):
        """Draw placeholder when no data available."""
        self.canvas.create_text(
            10, 10,
            text="No binary data to display. Start an analysis to see visualization.",
            fill="white",
            anchor=tk.NW,
            font=("TkDefaultFont", 10)
        )

    def _draw_header(self, bytes_per_row: int):
        """Draw column header."""
        y_offset = 5

        # Offset header
        self.canvas.create_text(
            10, y_offset,
            text="Offset",
            fill="cyan",
            anchor=tk.W,
            font=("Courier New", 9, "bold")
        )

        # Byte position headers
        x_offset = 80
        for i in range(bytes_per_row):
            self.canvas.create_text(
                x_offset + i * 40, y_offset,
                text=f"{i:02X}",
                fill="yellow",
                font=("Courier New", 8)
            )

        # ASCII header
        ascii_x = x_offset + bytes_per_row * 40 + 20
        self.canvas.create_text(
            ascii_x, y_offset,
            text="ASCII",
            fill="cyan",
            anchor=tk.W,
            font=("Courier New", 9, "bold")
        )

    def _draw_row(self, row: int, start_byte: int, end_byte: int, display_mode: str, bytes_per_row: int):
        """Draw a single row of binary data."""
        y_offset = 25 + row * 20

        # Offset label
        self.canvas.create_text(
            10, y_offset,
            text=f"{start_byte:08X}",
            fill="cyan",
            anchor=tk.W,
            font=("Courier New", 9)
        )

        # Byte values
        x_offset = 80
        ascii_chars = ""

        for byte_pos in range(start_byte, end_byte):
            byte_val = self.current_data[byte_pos]
            col = byte_pos - start_byte
            x = x_offset + col * 40

            # Determine color based on highlighting
            if byte_pos in self.highlighted_bytes:
                color = "red"
                bg_color = "darkred"
            else:
                color = self._get_byte_color(byte_val)
                bg_color = None

            # Draw background if highlighted
            if bg_color:
                self.canvas.create_rectangle(
                    x - 15, y_offset - 8,
                    x + 15, y_offset + 8,
                    fill=bg_color, outline=""
                )

            # Draw byte value based on display mode
            if display_mode == "hex":
                byte_text = f"{byte_val:02X}"
            elif display_mode == "binary":
                byte_text = f"{byte_val:08b}"
            elif display_mode == "decimal":
                byte_text = f"{byte_val:3d}"
            else:  # ascii
                byte_text = chr(byte_val) if 32 <= byte_val <= 126 else "."

            self.canvas.create_text(
                x, y_offset,
                text=byte_text,
                fill=color,
                font=("Courier New", 9)
            )

            # ASCII representation
            if 32 <= byte_val <= 126:
                ascii_chars += chr(byte_val)
            else:
                ascii_chars += "."

        # Draw ASCII representation
        ascii_x = x_offset + bytes_per_row * 40 + 20
        self.canvas.create_text(
            ascii_x, y_offset,
            text=ascii_chars,
            fill="lightgreen",
            anchor=tk.W,
            font=("Courier New", 9)
        )

    def _get_byte_color(self, byte_val: int) -> str:
        """Get color for byte value based on entropy."""
        # Use HSV color space for smooth gradients
        # Map byte value (0-255) to hue (0-240 degrees, red to blue)
        hue = (240 * (255 - byte_val)) / 255
        rgb = colorsys.hsv_to_rgb(hue / 360, 0.8, 1.0)
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

    def _update_operation_info(self):
        """Update operation information display."""
        if not self.operation_data:
            self.operation_label.config(text="No operation in progress")
            self.details_label.config(text="")
            return

        op_name = self.operation_data.get('name', 'Unknown')
        op_params = self.operation_data.get('params', {})
        op_cost = self.operation_data.get('cost', 0)

        # Update main operation label
        self.operation_label.config(text=f"Current: {op_name}")

        # Update details
        details = []
        if op_params:
            param_str = ", ".join(f"{k}={v}" for k, v in op_params.items())
            details.append(f"Parameters: {param_str}")

        if op_cost > 0:
            details.append(f"Cost: {op_cost:.2f}")

        if self.operation_data.get('bytes_affected'):
            details.append(f"Bytes affected: {self.operation_data['bytes_affected']}")

        self.details_label.config(text=" | ".join(details))

    def _on_offset_change(self):
        """Handle offset change."""
        try:
            self.offset = int(self.offset_var.get())
            self._redraw_display()
        except ValueError:
            self.offset_var.set(str(self.offset))

    def _on_bytes_per_row_change(self, event=None):
        """Handle bytes per row change."""
        try:
            self.bytes_per_row = int(self.bytes_per_row_var.get())
            self._redraw_display()
        except ValueError:
            self.bytes_per_row_var.set(str(self.bytes_per_row))

    def _scroll_up(self):
        """Scroll up one page."""
        page_size = self.bytes_per_row * self.max_rows
        self.offset = max(0, self.offset - page_size)
        self.offset_var.set(str(self.offset))
        self._redraw_display()

    def _scroll_down(self):
        """Scroll down one page."""
        if not self.current_data:
            return

        page_size = self.bytes_per_row * self.max_rows
        self.offset = min(len(self.current_data) - self.bytes_per_row,
                         self.offset + page_size)
        self.offset_var.set(str(self.offset))
        self._redraw_display()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.delta > 0:
            self.offset = max(0, self.offset - self.bytes_per_row)
        else:
            if self.current_data:
                self.offset = min(len(self.current_data) - self.bytes_per_row,
                                 self.offset + self.bytes_per_row)

        self.offset_var.set(str(self.offset))
        self._redraw_display()

    def _on_click(self, event):
        """Handle mouse click on canvas."""
        # Could implement byte selection or detailed inspection here
        pass

    def clear(self):
        """Clear visualization."""
        self.current_data = None
        self.operation_data = None
        self.highlighted_bytes = []
        self.offset = 0
        self.offset_var.set("0")
        self._redraw_display()
        self.operation_label.config(text="No operation in progress")
        self.details_label.config(text="")

    def set_data(self, data: bytes):
        """Set binary data for display."""
        self.current_data = data
        self.offset = 0
        self.offset_var.set("0")
        self._redraw_display()