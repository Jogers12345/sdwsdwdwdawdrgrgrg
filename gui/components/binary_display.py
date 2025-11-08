"""
Enhanced Binary Display Component for BSEE

Provides multiple visualization modes for binary data with
heatmap visualization, frequency analysis, and interactive exploration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

try:
    import matplotlib.pyplot as plt
    import matplotlib.figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.colors import LinearSegmentedColormap
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


@dataclass
class DisplayConfig:
    """Configuration for binary display modes."""
    mode: str = "hex"  # hex, binary, decimal, ascii, mixed, heatmap, frequency
    font_size: int = 10
    font_family: str = "Consolas"
    line_height: int = 16
    bytes_per_line: int = 16
    show_addresses: bool = True
    show_ascii: bool = True
    heatmap_update_frequency: float = 0.5  # seconds between updates
    color_scheme: str = "default"  # default, dark, bright, thermal


class BinaryDisplay(tk.Frame):
    """Enhanced binary display with multiple visualization modes."""

    def __init__(self, parent, config: Optional[DisplayConfig] = None):
        """
        Initialize binary display component.

        Args:
            parent: Parent widget
            config: Display configuration
        """
        super().__init__(parent)

        self.config = config or DisplayConfig()
        self.display_data = b""
        self.cursor_pos = 0
        self.selection_start = None
        self.selection_end = None

        # Analysis data for visualizations
        self.byte_frequency = np.zeros(256, dtype=np.int32)
        self.heatmap_colors = None
        self.color_map = None

        # UI components
        self.text_widget = None
        self.mode_var = tk.StringVar(value=self.config.mode)
        self.font_var = tk.StringVar(value=self.config.font_family)
        self.font_size_var = tk.IntVar(value=self.config.font_size)

        # External components (matplotlib dependent)
        self.figure = None
        self.canvas = None
        self.frequency_fig = None
        self.heatmap_fig = None

        self._create_widgets()
        self._setup_bindings()
        self._setup_color_maps()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Control panel
        control_frame = ttk.LabelFrame(self, text="Display Controls", padding=5)
        control_frame.pack(fill=tk.X, pady=(0, 5))

        self._create_control_panel(control_frame)

        # Display area
        self.display_frame = ttk.Frame(self)
        self.display_frame.pack(fill=tk.BOTH, expand=True)

        # Create display based on mode
        self._create_current_display()

        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        self._create_status_bar(status_frame)

    def _create_control_panel(self, parent):
        """Create display control panel."""
        # Mode selection
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill=tk.X, pady=2)

        ttk.Label(mode_frame, text="Display Mode:").pack(side=tk.LEFT)
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var,
                                 values=["hex", "binary", "decimal", "ascii", "mixed",
                                        "heatmap", "frequency"],
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=(5, 10))
        mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

        # Font controls
        font_frame = ttk.Frame(parent)
        font_frame.pack(fill=tk.X, pady=2)

        ttk.Label(font_frame, text="Font:").pack(side=tk.LEFT)
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var,
                                   values=["Consolas", "Courier New", "Lucida Console",
                                          "Menlo", "Monaco", "Inconsolata"],
                                   state="readonly", width=12)
        font_combo.pack(side=tk.LEFT, padx=(5, 5))

        ttk.Label(font_frame, text="Size:").pack(side=tk.LEFT, padx=(10, 0))
        size_spin = ttk.Spinbox(font_frame, from_=8, to=16, textvariable=self.font_size_var,
                             width=5, command=self._on_font_change)
        size_spin.pack(side=tk.LEFT, padx=(5, 10))

        # Options
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X, pady=2)

        self.show_addresses_var = tk.BooleanVar(value=self.config.show_addresses)
        ttk.Checkbutton(options_frame, text="Show Addresses", variable=self.show_addresses_var,
                       command=self._on_option_change).pack(side=tk.LEFT, padx=(0, 15))

        self.show_ascii_var = tk.BooleanVar(value=self.config.show_ascii)
        ttk.Checkbutton(options_frame, text="Show ASCII", variable=self.show_ascii_var,
                       command=self._on_option_change).pack(side=tk.LEFT, padx=(0, 15))

        # Color scheme (for heatmap mode)
        if MATPLOTLIB_AVAILABLE:
            color_frame = ttk.Frame(parent)
            color_frame.pack(fill=tk.X, pady=2)

            ttk.Label(color_frame, text="Color Scheme:").pack(side=tk.LEFT)
            color_var = tk.StringVar(value=self.config.color_scheme)
            color_combo = ttk.Combobox(color_frame, textvariable=color_var,
                                      values=["default", "dark", "bright", "thermal",
                                             "viridis", "plasma", "inferno"],
                                      state="readonly", width=12)
            color_combo.pack(side=tk.LEFT, padx=(5, 10))
            color_combo.bind("<<ComboboxSelected>>",
                             lambda e: self._on_color_scheme_change(color_var.get()))

    def _create_current_display(self):
        """Create display widget for current mode."""
        # Clear existing display
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()

        if mode == "hex":
            self._create_hex_display()
        elif mode == "binary":
            self._create_binary_display()
        elif mode == "decimal":
            self._create_decimal_display()
        elif mode == "ascii":
            self._create_ascii_display()
        elif mode == "mixed":
            self._create_mixed_display()
        elif mode == "heatmap" and MATPLOTLIB_AVAILABLE:
            self._create_heatmap_display()
        elif mode == "frequency" and MATPLOTLIB_AVAILABLE:
            self._create_frequency_display()
        else:
            # Fallback to hex display if matplotlib not available
            self.mode_var.set("hex")
            self._create_hex_display()

    def _create_hex_display(self):
        """Create standard hex display with addresses."""
        # Create scrolled text widget
        self.text_widget = tk.Text(self.display_frame, wrap=tk.NONE,
                                    font=(self.config.font_family, self.config.font_size),
                                    bg='#1e1e1e', fg='#00ff00',
                                    insertbackground='#00ff00',
                                    selectbackground='#444444')
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure text tags
        self._configure_text_tags()
        self.text_widget.bind("<Configure>", self._on_text_resize)

        # Update display
        self._update_hex_display()

    def _create_binary_display(self):
        """Create binary display showing individual bits."""
        self.text_widget = tk.Text(self.display_frame, wrap=tk.NONE,
                                    font=(self.config.font_family, self.config.font_size - 2),
                                    bg='#1e1e1e', fg='#00ff00',
                                    insertbackground='#00ff00',
                                    selectbackground='#444444')
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self._configure_text_tags()
        self._update_binary_display()

    def _create_decimal_display(self):
        """Create decimal display of byte values."""
        self.text_widget = tk.Text(self.display_frame, wrap=tk.NONE,
                                    font=(self.config.font_family, self.config.font_size),
                                    bg='#1e1e1e', fg='#00ff00',
                                    insertbackground='#00ff00',
                                    selectbackground='#444444')
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self._configure_text_tags()
        self._update_decimal_display()

    def _create_ascii_display(self):
        """Create ASCII character display."""
        self.text_widget = tk.Text(self.display_frame, wrap=tk.NONE,
                                    font=(self.config.font_family, self.config.font_size),
                                    bg='#1e1e1e', fg='#00ff00',
                                    insertbackground='#00ff00',
                                    selectbackground='#444444')
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self._configure_text_tags()
        self._update_ascii_display()

    def _create_mixed_display(self):
        """Create mixed hex + ASCII display (like hex editors)."""
        # Use hex display with enhanced ASCII representation
        self._create_hex_display()
        # Configure for mixed display
        self.config.show_ascii = True
        self.show_ascii_var.set(True)

    def _create_heatmap_display(self):
        """Create heatmap visualization using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            self._create_hex_display()
            return

        # Create matplotlib figure
        self.figure = matplotlib.figure.Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create heatmap
        ax = self.figure.add_subplot(111)
        self.heatmap_ax = ax

        # Initial display
        self._update_heatmap_display()

    def _create_frequency_display(self):
        """Create frequency distribution chart using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            self._create_hex_display()
            return

        # Create matplotlib figure
        self.figure = matplotlib.figure.Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create frequency chart
        ax = self.figure.add_subplot(111)
        self.frequency_ax = ax

        # Initial display
        self._update_frequency_display()

    def _create_status_bar(self, parent):
        """Create status information bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)

        # Cursor position
        self.cursor_label = ttk.Label(status_frame, text="Cursor: 0x0000")
        self.cursor_label.pack(side=tk.LEFT, padx=(0, 10))

        # Selection information
        self.selection_label = ttk.Label(status_frame, text="Selection: None")
        self.selection_label.pack(side=tk.LEFT, padx=(0, 10))

        # Data size
        self.size_label = ttk.Label(status_frame, text="Size: 0 bytes")
        self.size_label.pack(side=tk.LEFT, padx=(0, 10))

        # Entropy
        self.entropy_label = ttk.Label(status_frame, text="Entropy: 0.000")
        self.entropy_label.pack(side=tk.LEFT, padx=(0, 10))

    def _setup_bindings(self):
        """Setup keyboard and mouse bindings."""
        # Keyboard navigation
        self.bind('<Left>', lambda e: self._move_cursor(-1))
        self.bind('<Right>', lambda e: self._move_cursor(1))
        self.bind('<Up>', lambda e: self._move_cursor(-16))
        self.bind('<Down>', lambda e: self._move_cursor(16))
        self.bind('<Home>', lambda e: self._move_cursor_to_start())
        self.bind('<End>', lambda e: self._move_cursor_to_end())
        self.bind('<Page_Up>', lambda e: self._move_cursor(-256))
        self.bind('<Page_Down>', lambda e: self._move_cursor(256))

        # Mouse bindings for selection
        if hasattr(self, 'text_widget') and self.text_widget:
            self.text_widget.bind('<Button-1>', self._on_mouse_down)
            self.text_widget.bind('<B1-Motion>', self._on_mouse_drag)
            self.text_widget.bind('<ButtonRelease-1>', self._on_mouse_up)

        # Data binding
        self.bind('<Control-a>', lambda e: self._select_all())

    def _configure_text_tags(self):
        """Configure text tags for different display purposes."""
        if not hasattr(self, 'text_widget') or not self.text_widget:
            return

        # Basic colors
        self.text_widget.tag_configure('address', foreground='#808080')
        self.text_widget.tag_configure('ascii', foreground='#808080')
        self.text_widget.tag_configure('non_printable', foreground='#404040')
        self.text_widget.tag_configure('selected', background='#666666', foreground='#ffffff')
        self.text_widget.tag_configure('cursor', background='#ffffff', foreground='#000000')

        # Byte value colors (for future enhancements)
        self.text_widget.tag_configure('byte_null', foreground='#666666')
        self.text_widget.tag_configure('byte_printable', foreground='#00ff00')
        self.text_widget.tag_configure('byte_control', foreground='#ff0000')
        self.text_widget.tag_configure('byte_extended', foreground='#0000ff')

    def _setup_color_maps(self):
        """Setup color schemes for different visualization modes."""
        self.color_maps = {
            'default': {
                'rare': '#ff0000',      # Bright red for rare bytes
                'uncommon': '#ff8800',   # Orange for uncommon
                'common': '#888800',      # Dark yellow for common
                'frequent': '#008888',     # Dark cyan for frequent
                'background': '#1a1a1a'    # Dark background
            },
            'dark': {
                'rare': '#ff4444',
                'uncommon': '#ff9944',
                'common': '#aaaa44',
                'frequent': '#44aaaa',
                'background': '#0d1117'
            },
            'bright': {
                'rare': '#ff6666',
                'uncommon': '#ffaa66',
                'common': '#ffff66',
                'frequent': '#66ffff',
                'background': '#ffffff'
            },
            'thermal': {
                'rare': '#0066ff',      # Blue (cold)
                'uncommon': '#0099ff',
                'common': '#ffcc00',      # Yellow (warm)
                'frequent': '#ff6600',    # Red (hot)
                'background': '#000000'
            }
        }

        # Matplotlib colormaps if available
        if MATPLOTLIB_AVAILABLE:
            self.matplotlib_colormaps = {
                'viridis': plt.cm.viridis,
                'plasma': plt.cm.plasma,
                'inferno': plt.cm.inferno
            }

    def _on_mode_change(self, event=None):
        """Handle display mode change."""
        mode = self.mode_var.get()
        self.config.mode = mode
        self._create_current_display()

    def _on_font_change(self, event=None):
        """Handle font change."""
        self.config.font_family = self.font_var.get()
        self.config.font_size = self.font_size_var.get()
        if self.text_widget:
            self.text_widget.config(font=(self.config.font_family, self.config.font_size))
            self._refresh_display()

    def _on_option_change(self):
        """Handle display option changes."""
        self.config.show_addresses = self.show_addresses_var.get()
        self.config.show_ascii = self.show_ascii_var.get()
        self._refresh_display()

    def _on_color_scheme_change(self, scheme: str):
        """Handle color scheme change."""
        self.config.color_scheme = scheme
        if self.mode_var.get() in ["heatmap", "frequency"]:
            self._refresh_display()

    def _on_text_resize(self, event):
        """Handle text widget resize."""
        self._refresh_display()

    def _refresh_display(self):
        """Refresh current display."""
        mode = self.mode_var.get()
        if mode == "hex":
            self._update_hex_display()
        elif mode == "binary":
            self._update_binary_display()
        elif mode == "decimal":
            self._update_decimal_display()
        elif mode == "ascii":
            self._update_ascii_display()
        elif mode == "heatmap":
            self._update_heatmap_display()
        elif mode == "frequency":
            self._update_frequency_display()

    def _update_hex_display(self):
        """Update hex display with current data."""
        if not self.text_widget:
            return

        self.text_widget.delete(1.0, tk.END)

        # Calculate byte frequency for tooltips
        self._calculate_byte_frequency()

        for i in range(0, len(self.display_data), self.config.bytes_per_line):
            # Address
            if self.config.show_addresses:
                addr_text = f"{i:08x}: "
                self.text_widget.insert(tk.END, addr_text, 'address')

            # Hex bytes
            hex_bytes = []
            tags = []

            for j in range(self.config.bytes_per_line):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    hex_bytes.append(f"{byte_val:02x}")

                    # Add space for readability
                    if j == self.config.bytes_per_line // 2 - 1:
                        hex_bytes.append(" ")
                    else:
                        hex_bytes.append(" ")

                    # Color coding based on byte value
                    tag = self._get_byte_tag(byte_val, j)
                    tags.append((f"byte_{i+j}", tag))
                else:
                    hex_bytes.append("   ")

            hex_text = " ".join(hex_bytes)
            self.text_widget.insert(tk.END, hex_text, ' '.join(tag[1] for tag in tags))

            # ASCII representation
            if self.config.show_ascii:
                self.text_widget.insert(tk.END, "  ", 'address')
                ascii_text = ""
                ascii_tags = []

                for j in range(self.config.bytes_per_line):
                    if i + j < len(self.display_data):
                        byte_val = self.display_data[i + j]
                        if 32 <= byte_val <= 126:
                            ascii_text += chr(byte_val)
                            ascii_tags.append(f"ascii_{i+j}")
                        else:
                            ascii_text += "."
                            ascii_tags.append("non_printable")
                    else:
                        ascii_text += " "

                self.text_widget.insert(tk.END, ascii_text, ' '.join(ascii_tags))

            self.text_widget.insert(tk.END, "\n")

        # Update status bar
        self._update_status_bar()

    def _update_binary_display(self):
        """Update binary display showing individual bits."""
        if not self.text_widget:
            return

        self.text_widget.delete(1.0, tk.END)

        for i in range(0, len(self.display_data), 8):  # 8 bytes per line for binary
            if self.config.show_addresses:
                addr_text = f"{i:08x}: "
                self.text_widget.insert(tk.END, addr_text, 'address')

            for j in range(8):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    binary_text = f"{byte_val:08b} "
                    tag = self._get_byte_tag(byte_val, j)
                    self.text_widget.insert(tk.END, binary_text, tag)
                else:
                    self.text_widget.insert(tk.END, "         ", 'normal')

            self.text_widget.insert(tk.END, "\n")

        self._update_status_bar()

    def _update_decimal_display(self):
        """Update decimal display of byte values."""
        if not self.text_widget:
            return

        self.text_widget.delete(1.0, tk.END)

        for i in range(0, len(self.display_data), self.config.bytes_per_line):
            if self.config.show_addresses:
                addr_text = f"{i:08x}: "
                self.text_widget.insert(tk.END, addr_text, 'address')

            for j in range(self.config.bytes_per_line):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    decimal_text = f"{byte_val:3d} "
                    tag = self._get_byte_tag(byte_val, j)
                    self.text_widget.insert(tk.END, decimal_text, tag)
                else:
                    self.text_widget.insert(tk.END, "    ", 'normal')

            self.text_widget.insert(tk.END, "\n")

        self._update_status_bar()

    def _update_ascii_display(self):
        """Update ASCII character display."""
        if not self.text_widget:
            return

        self.text_widget.delete(1.0, tk.END)

        for i in range(0, len(self.display_data), self.config.bytes_per_line):
            if self.config.show_addresses:
                addr_text = f"{i:08x}: "
                self.text_widget.insert(tk.END, addr_text, 'address')

            ascii_text = ""
            ascii_tags = []

            for j in range(self.config.bytes_per_line):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    if 32 <= byte_val <= 126:
                        ascii_text += chr(byte_val)
                        ascii_tags.append(f"ascii_{i+j}")
                    else:
                        ascii_text += "."
                        ascii_tags.append("non_printable")
                else:
                    ascii_text += " "

            self.text_widget.insert(tk.END, ascii_text, ' '.join(ascii_tags))
            self.text_widget.insert(tk.END, "\n")

        self._update_status_bar()

    def _update_heatmap_display(self):
        """Update heatmap visualization."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'heatmap_ax'):
            return

        # Calculate frequency if needed
        self._calculate_byte_frequency()

        # Clear axis
        self.heatmap_ax.clear()

        # Create 32x32 grid for first 1024 bytes
        grid_data = np.zeros((32, 32), dtype=int)
        data_len = min(len(self.display_data), 1024)

        for idx in range(data_len):
            byte_val = self.display_data[idx]
            row = idx // 32
            col = idx % 32
            grid_data[row, col] = byte_val

        # Get color scheme
        colors = self.color_maps.get(self.config.color_scheme, self.color_maps['default'])

        # Apply color mapping
        if self.config.color_scheme in self.matplotlib_colormaps:
            # Use matplotlib colormap
            norm = plt.Normalize(vmin=0, vmax=255)
            im = self.heatmap_ax.imshow(grid_data, cmap=self.matplotlib_colormaps[self.config.color_scheme], norm=norm)
        else:
            # Use custom color mapping
            max_freq = np.max(self.byte_frequency) if np.max(self.byte_frequency) > 0 else 1
            colored_grid = np.zeros((32, 32, 3), dtype=np.uint8)

            for i in range(32):
                for j in range(32):
                    if i * 32 + j < len(self.display_data):
                        byte_val = grid_data[i, j]
                        freq = self.byte_frequency[byte_val]
                        normalized_freq = freq / max_freq

                        # Map frequency to color
                        if normalized_freq > 0.7:
                            color = colors['frequent']
                        elif normalized_freq < 0.3:
                            color = colors['rare']
                        elif normalized_freq < 0.5:
                            color = colors['uncommon']
                        else:
                            color = colors['common']

                        # Convert hex to RGB
                        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                        colored_grid[i, j] = rgb
                    else:
                        colored_grid[i, j] = [0x1a, 0x1a, 0x1a]  # Background color

            im = self.heatmap_ax.imshow(colored_grid)

        # Set title and labels
        self.heatmap_ax.set_title("Byte Frequency Heatmap")
        self.heatmap_ax.set_xlabel("Column")
        self.heatmap_ax.set_ylabel("Row")

        # Add colorbar
        if self.config.color_scheme in self.matplotlib_colormaps:
            cbar = self.figure.colorbar(im, ax=self.heatmap_ax, shrink=0.8)
            cbar.set_label("Byte Value")

        # Enable interaction
        self.canvas.mpl_connect('button_press_event', self._on_heatmap_click)

        self.figure.tight_layout()
        self.canvas.draw()

        # Update status bar
        self._update_status_bar()

    def _update_frequency_display(self):
        """Update frequency distribution chart."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'frequency_ax'):
            return

        # Calculate frequency
        self._calculate_byte_frequency()

        # Clear axis
        self.frequency_ax.clear()

        # Create bar chart
        x = np.arange(256)
        y = self.byte_frequency

        bars = self.frequency_ax.bar(x, y, width=1, alpha=0.7)

        # Color bars based on frequency
        max_freq = np.max(y) if np.max(y) > 0 else 1
        colors = []
        for freq in y:
            normalized_freq = freq / max_freq
            if normalized_freq > 0.7:
                colors.append('#0066cc')  # Blue for frequent
            elif normalized_freq < 0.1:
                colors.append('#cc0066')  # Red for rare
            else:
                colors.append('#66cc00')  # Green for medium

        # Apply colors to bars
        for i, bar in enumerate(bars):
            if i < len(colors):
                bar.set_color(colors[i])

        # Set labels and title
        self.frequency_ax.set_xlabel("Byte Value (0-255)")
        self.frequency_ax.set_ylabel("Frequency")
        self.frequency_ax.set_title("Byte Value Distribution")
        self.frequency_ax.set_xlim(-1, 256)
        self.frequency_ax.set_ylim(0, max_freq * 1.1 if max_freq > 0 else 1)

        # Add grid
        self.frequency_ax.grid(True, alpha=0.3)

        # Enable click events
        self.canvas.mpl_connect('button_press_event', self._on_frequency_click)

        self.figure.tight_layout()
        self.canvas.draw()

        # Update status bar
        self._update_status_bar()

    def _get_byte_tag(self, byte_val: int, position: int) -> str:
        """Get appropriate text tag for byte value."""
        if byte_val == 0:
            return 'byte_null'
        elif 32 <= byte_val <= 126:
            return 'byte_printable'
        elif 128 <= byte_val <= 159:
            return 'byte_extended'
        else:
            return f"byte_{byte_val % 16}"

    def _calculate_byte_frequency(self):
        """Calculate byte frequency distribution."""
        # Reset frequency array
        self.byte_frequency = np.zeros(256, dtype=np.int32)

        # Count occurrences
        for byte_val in self.display_data:
            self.byte_frequency[byte_val] += 1

    def _update_status_bar(self):
        """Update status bar information."""
        # Cursor position
        if self.cursor_pos < len(self.display_data):
            cursor_addr = f"0x{self.cursor_pos:04x}"
            self.cursor_label.config(text=f"Cursor: {cursor_addr}")
        else:
            self.cursor_label.config(text="Cursor: End")

        # Selection
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.selection_label.config(text=f"Selection: {start} - {end} ({end-start+1} bytes)")
        else:
            self.selection_label.config(text="Selection: None")

        # Data size
        self.size_label.config(text=f"Size: {len(self.display_data)} bytes")

        # Entropy
        entropy = self._calculate_entropy()
        self.entropy_label.config(text=f"Entropy: {entropy:.3f}")

    def _calculate_entropy(self) -> float:
        """Calculate Shannon entropy of current data."""
        if not self.display_data:
            return 0.0

        # Calculate byte frequencies
        freq = np.zeros(256, dtype=np.float64)
        for byte_val in self.display_data:
            freq[byte_val] += 1

        # Convert to probabilities
        total = len(self.display_data)
        if total == 0:
            return 0.0

        probs = freq / total

        # Calculate Shannon entropy
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * np.log2(p)

        return entropy

    def _move_cursor(self, delta: int):
        """Move cursor position by delta."""
        new_pos = self.cursor_pos + delta
        new_pos = max(0, min(new_pos, len(self.display_data) - 1))
        self.cursor_pos = new_pos

        if self.text_widget:
            self._highlight_cursor()

    def _move_cursor_to_start(self):
        """Move cursor to beginning of data."""
        self.cursor_pos = 0
        if self.text_widget:
            self._highlight_cursor()

    def _move_cursor_to_end(self):
        """Move cursor to end of data."""
        self.cursor_pos = max(0, len(self.display_data) - 1)
        if self.text_widget:
            self._highlight_cursor()

    def _highlight_cursor(self):
        """Highlight current cursor position in hex display."""
        # Remove existing cursor highlight
        self.text_widget.tag_remove('cursor', '1.0', tk.END)

        # Calculate line and position for current cursor
        line = self.cursor_pos // self.config.bytes_per_line
        byte_in_line = self.cursor_pos % self.config.bytes_per_line

        # Calculate character position in line
        char_pos = 0
        if self.config.show_addresses:
            char_pos = 10  # Address length

        char_pos += byte_in_line * 3  # 2 hex chars + space

        # Add extra space after 8th byte in line
        if self.config.bytes_per_line == 16 and byte_in_line >= 8:
            char_pos += 1

        # Calculate start and end positions
        start_pos = f"{line + 1}.{char_pos}"
        end_pos = f"{line + 1}.{char_pos + 2}"

        try:
            self.text_widget.tag_add('cursor', start_pos, end_pos)
        except:
            pass  # Ignore positioning errors

        # Ensure cursor is visible
        self.text_widget.see(start_pos)

    def _on_mouse_down(self, event):
        """Handle mouse button down event."""
        self.selection_start = self._get_position_from_coords(event.x, event.y)
        self.selection_end = self.selection_start

    def _on_mouse_drag(self, event):
        """Handle mouse drag event."""
        self.selection_end = self._get_position_from_coords(event.x, event.y)
        self._update_selection()

    def _on_mouse_up(self, event):
        """Handle mouse button up event."""
        self.selection_end = self._get_position_from_coords(event.x, event.y)
        self._update_selection()

    def _update_selection(self):
        """Update visual selection in text widget."""
        if not self.text_widget or self.selection_start is None or self.selection_end is None:
            return

        # Remove existing selection
        self.text_widget.tag_remove('selected', '1.0', tk.END)

        # Calculate positions
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)

        # Convert to text widget positions
        start_pos = self._get_text_position(start)
        end_pos = self._get_text_position(end + 1)  # Include end byte

        try:
            self.text_widget.tag_add('selected', start_pos, end_pos)
        except:
            pass  # Ignore positioning errors

    def _get_position_from_coords(self, x: int, y: int) -> int:
        """Convert widget coordinates to data position."""
        # This is a simplified implementation
        # A full implementation would need to account for font metrics and line heights
        line = y // self.config.font_size  # Approximate
        offset_in_line = x // (self.config.font_size * 3)  # Approximate (3 chars per byte)

        position = line * self.config.bytes_per_line + offset_in_line
        return max(0, min(position, len(self.display_data) - 1))

    def _get_text_position(self, data_pos: int) -> str:
        """Convert data position to text widget position."""
        line = data_pos // self.config.bytes_per_line
        byte_in_line = data_pos % self.config.bytes_per_line

        char_pos = 0
        if self.config.show_addresses:
            char_pos = 10  # Address length

        char_pos += byte_in_line * 3  # 2 hex chars + space

        # Add extra space after 8th byte
        if self.config.bytes_per_line == 16 and byte_in_line >= 8:
            char_pos += 1

        return f"{line + 1}.{char_pos}"

    def _select_all(self):
        """Select all data."""
        self.selection_start = 0
        self.selection_end = len(self.display_data) - 1
        self._update_selection()

    def _on_heatmap_click(self, event):
        """Handle click on heatmap."""
        if event.inaxes != self.heatmap_ax:
            return

        # Get clicked position
        x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)

        # Convert to data position
        data_pos = y * 32 + x
        if data_pos < len(self.display_data):
            byte_val = self.display_data[data_pos]
            frequency = self.byte_frequency[byte_val]

            info = f"Position: 0x{data_pos:04x}\n"
            info += f"Byte Value: 0x{byte_val:02x} ({byte_val})\n"
            info += f"Frequency: {frequency} occurrences\n"
            info += f"Row: {y}, Column: {x}"

            messagebox.showinfo("Byte Information", info)

    def _on_frequency_click(self, event):
        """Handle click on frequency chart."""
        if event.inaxes != self.frequency_ax:
            return

        # Get clicked bar
        if hasattr(event, 'bar') and event.bar is not None:
            byte_val = event.bar
            frequency = self.byte_frequency[byte_val]

            info = f"Byte Value: 0x{byte_val:02x} ({byte_val})\n"
            info += f"Frequency: {frequency} occurrences\n"
            info += f"Percentage: {(frequency/len(self.display_data)*100):.2f}%"

            messagebox.showinfo("Byte Frequency", info)

    def set_display_data(self, data: bytes):
        """Set binary data to display."""
        self.display_data = data
        self.cursor_pos = 0
        self.selection_start = None
        self.selection_end = None
        self._refresh_display()

    def get_display_config(self) -> DisplayConfig:
        """Get current display configuration."""
        return self.config

    def get_byte_at_cursor(self) -> Optional[int]:
        """Get byte value at current cursor position."""
        if 0 <= self.cursor_pos < len(self.display_data):
            return self.display_data[self.cursor_pos]
        return None

    def get_selected_bytes(self) -> bytes:
        """Get currently selected bytes."""
        if self.selection_start is None or self.selection_end is None:
            return b""

        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)

        return self.display_data[start:end + 1]

    def get_display_mode(self) -> str:
        """Get current display mode."""
        return self.mode_var.get()

    def show_byte_info(self, position: int):
        """Show detailed information about specific byte."""
        if 0 <= position < len(self.display_data):
            byte_val = self.display_data[position]
            frequency = self.byte_frequency[byte_val]

            info = f"Position: 0x{position:04x}\n"
            info += f"Byte Value: 0x{byte_val:02x} ({byte_val})\n"
            info += f"Decimal: {byte_val}\n"

            if 32 <= byte_val <= 126:
                info += f"ASCII: '{chr(byte_val)}' ({chr(byte_val)})\n"
            else:
                info += f"ASCII: Non-printable (0x{byte_val:02x})\n"

            info += f"Binary: {byte_val:08b}\n"
            info += f"Frequency: {frequency} occurrences"

            messagebox.showinfo("Byte Information", info)

    def highlight_byte(self, position: int):
        """Highlight specific byte in display."""
        if not self.text_widget or position < 0 or position >= len(self.display_data):
            return

        # Calculate text position
        text_pos = self._get_text_position(position)

        try:
            # Remove existing highlights
            self.text_widget.tag_remove('highlight', '1.0', tk.END)
            # Add new highlight
            end_pos = self._get_text_position(position + 1)
            self.text_widget.tag_add('highlight', text_pos, end_pos)
            # Scroll to position
            self.text_widget.see(text_pos)
        except:
            pass  # Ignore positioning errors

    def export_display(self, filename: str, format_type: str):
        """Export current display to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if format_type == 'text':
                    f.write("BSEE Binary Display Export\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Display Mode: {self.get_display_mode()}\n")
                    f.write(f"Data Size: {len(self.display_data)} bytes\n")
                    f.write(f"Entropy: {self._calculate_entropy():.6f}\n\n")

                    if self.get_display_mode() == 'hex':
                        self._export_hex_text(f)
                    elif self.get_display_mode() == 'binary':
                        self._export_binary_text(f)
                    elif self.get_display_mode() == 'ascii':
                        self._export_ascii_text(f)

                elif format_type == 'json':
                    import json
                    export_data = {
                        'display_mode': self.get_display_mode(),
                        'data_size': len(self.display_data),
                        'entropy': self._calculate_entropy(),
                        'byte_frequency': self.byte_frequency.tolist(),
                        'data': self.display_data.hex()
                    }
                    json.dump(export_data, f, indent=2)

            messagebox.showinfo("Export Complete", f"Display exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export display: {e}")

    def _export_hex_text(self, file_handle):
        """Export hex formatted text to file."""
        for i in range(0, len(self.display_data), 16):
            if self.config.show_addresses:
                file_handle.write(f"{i:08x}: ")

            hex_bytes = []
            for j in range(16):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    hex_bytes.append(f"{byte_val:02x}")
                else:
                    hex_bytes.append("  ")

            hex_text = " ".join(hex_bytes)
            file_handle.write(hex_text)

            if self.config.show_ascii:
                file_handle.write("  ")
                ascii_text = ""
                for j in range(16):
                    if i + j < len(self.display_data):
                        byte_val = self.display_data[i + j]
                        if 32 <= byte_val <= 126:
                            ascii_text += chr(byte_val)
                        else:
                            ascii_text += "."
                    else:
                        ascii_text += " "
                file_handle.write(ascii_text)

            file_handle.write("\n")

    def _export_binary_text(self, file_handle):
        """Export binary formatted text to file."""
        for i in range(0, len(self.display_data), 8):
            if self.config.show_addresses:
                file_handle.write(f"{i:08x}: ")

            for j in range(8):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    binary_text = f"{byte_val:08b} "
                    file_handle.write(binary_text)
                else:
                    file_handle.write("         ")

            file_handle.write("\n")

    def _export_ascii_text(self, file_handle):
        """Export ASCII formatted text to file."""
        for i in range(0, len(self.display_data), 16):
            if self.config.show_addresses:
                file_handle.write(f"{i:08x}: ")

            ascii_text = ""
            for j in range(16):
                if i + j < len(self.display_data):
                    byte_val = self.display_data[i + j]
                    if 32 <= byte_val <= 126:
                        ascii_text += chr(byte_val)
                    else:
                        ascii_text += "."
                else:
                    ascii_text += " "

            file_handle.write(ascii_text + "\n")