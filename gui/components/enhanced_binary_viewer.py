"""
Enhanced Binary Viewer Component for BSEE GUI
Provides binary data visualization with multiple viewing modes.
"""

import tkinter as tk
from tkinter import ttk, Canvas, Scrollbar, Frame, Label, Button
import struct
import binascii
from typing import Optional, Dict, List, Tuple
from pathlib import Path


class EnhancedBinaryViewer:
    """Enhanced binary data viewer with multiple visualization modes."""

    def __init__(self, parent, callback=None):
        """Initialize enhanced binary viewer."""
        self.parent = parent
        self.callback = callback
        self.binary_data = b""
        self.current_offset = 0
        self.view_mode = "hex"  # hex, binary, text, structure
        self.bytes_per_line = 16
        self.show_ascii = True
        self.highlight_changes = True
        self.bookmarks = []

        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self):
        """Setup the enhanced viewer UI."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Viewer Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # View mode selection
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(mode_frame, text="View Mode:").pack(side=tk.LEFT, padx=5)
        self.view_mode_var = tk.StringVar(value="hex")
        view_modes = ttk.Combobox(mode_frame, textvariable=self.view_mode_var,
                                   values=["hex", "binary", "text", "structure", "mixed"],
                                   state="readonly", width=12)
        view_modes.pack(side=tk.LEFT, padx=5)
        view_modes.bind("<<ComboboxSelected>>", self._on_view_mode_change)

        # Bytes per line control
        ttk.Label(mode_frame, text="Bytes/Line:").pack(side=tk.LEFT, padx=20)
        self.bytes_per_line_var = tk.IntVar(value=16)
        bytes_spin = ttk.Spinbox(mode_frame, from_=8, to=32, textvariable=self.bytes_per_line_var,
                                   width=8, increment=4)
        bytes_spin.pack(side=tk.LEFT, padx=5)

        # Options
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        self.show_ascii_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show ASCII",
                     variable=self.show_ascii_var,
                     command=self._refresh_display).pack(side=tk.LEFT, padx=5)

        self.highlight_changes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Highlight Changes",
                     variable=self.highlight_changes_var,
                     command=self._refresh_display).pack(side=tk.LEFT, padx=5)

        # Navigation frame
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        # Offset navigation
        offset_frame = ttk.Frame(nav_frame)
        offset_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(offset_frame, text="Offset:").pack(side=tk.LEFT)
        self.offset_var = tk.StringVar(value="0x00000000")
        offset_entry = ttk.Entry(offset_frame, textvariable=self.offset_var, width=12)
        offset_entry.pack(side=tk.LEFT, padx=5)
        offset_entry.bind("<Return>", self._jump_to_offset)

        # Navigation buttons
        nav_btn_frame = ttk.Frame(nav_frame)
        nav_btn_frame.pack(side=tk.LEFT, padx=20)

        ttk.Button(nav_btn_frame, text="◀◀", width=5,
                  command=lambda: self._navigate_offset(-self.bytes_per_line)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_btn_frame, text="◀", width=5,
                  command=lambda: self._navigate_offset(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_btn_frame, text="▶", width=5,
                  command=lambda: self._navigate_offset(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_btn_frame, text="▶▶", width=5,
                  command=lambda: self._navigate_offset(self.bytes_per_line)).pack(side=tk.LEFT, padx=2)

        # Bookmark buttons
        bookmark_frame = ttk.Frame(nav_frame)
        bookmark_frame.pack(side=tk.LEFT, padx=20)

        ttk.Button(bookmark_frame, text="🔖", width=5,
                  command=self._add_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(bookmark_frame, text="📋", width=5,
                  command=self._show_bookmarks).pack(side=tk.LEFT, padx=2)

        # Search frame
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind("<Return>", self._search_bytes)

        ttk.Button(search_frame, text="🔍", width=5,
                  command=self._search_bytes).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="⏭", width=5,
                  command=self._clear_search).pack(side=tk.LEFT, padx=2)

        # Binary display canvas with scrollbars
        display_frame = ttk.LabelFrame(main_frame, text="Binary Data")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create scrollable canvas
        canvas_frame = Frame(display_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = Canvas(canvas_frame, bg="black", fg="green",
                          font=("Courier New", 10))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Canvas events
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)

        # Status bar
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Initialize display
        self.lines = []
        self.search_results = []

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for enhanced navigation."""
        self.parent.bind("<Control-g>", lambda e: self._search_next())
        self.parent.bind("<Control-f>", lambda e: self.search_var.focus_set())
        self.parent.bind("<Control-b>", lambda e: self._add_bookmark())
        self.parent.bind("<Home>", lambda e: self._jump_to_offset("0x00000000"))
        self.parent.bind("<End>", lambda e: self._jump_to_end())
        self.parent.bind("<Control-Home>", lambda e: self._jump_to_start())

    def load_binary_data(self, binary_data: bytes, filename: str = "unknown"):
        """Load binary data for viewing."""
        self.binary_data = binary_data
        self.current_offset = 0
        self.bookmarks = []

        # Update status
        data_size = len(binary_data)
        self.status_label.config(text=f"Loaded: {filename} ({data_size:,} bytes)")

        # Refresh display
        self._refresh_display()

    def _refresh_display(self):
        """Refresh the binary data display."""
        if not self.binary_data:
            return

        self.canvas.delete("all")
        self.lines = []

        view_mode = self.view_mode_var.get()
        bytes_per_line = self.bytes_per_line_var.get()
        show_ascii = self.show_ascii_var.get()

        # Calculate display area
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        char_width = 8  # Approximate width of monospace character
        char_height = 16  # Approximate height of monospace character line

        lines_per_screen = canvas_height // char_height - 2
        start_line = max(0, self.current_offset // bytes_per_line)

        # Generate display lines
        for i in range(start_line, min(start_line + lines_per_screen, len(self.binary_data) // bytes_per_line)):
            offset = i * bytes_per_line
            if offset >= len(self.binary_data):
                break

            line_data = self.binary_data[offset:offset + bytes_per_line]

            if view_mode == "hex":
                display_line = self._format_hex_line(line_data, offset, show_ascii)
            elif view_mode == "binary":
                display_line = self._format_binary_line(line_data, offset)
            elif view_mode == "text":
                display_line = self._format_text_line(line_data, offset)
            elif view_mode == "structure":
                display_line = self._format_structure_line(line_data, offset)
            else:  # mixed mode
                display_line = self._format_mixed_line(line_data, offset, show_ascii)

            self.lines.append(display_line)

        # Render lines to canvas
        y_pos = 20
        for line_num, line in enumerate(self.lines):
            self.canvas.create_text(10, y_pos + line_num * char_height,
                                   line, anchor=tk.NW,
                                   font=("Courier New", 10),
                                   fill="white")

    def _format_hex_line(self, data: bytes, offset: int, show_ascii: bool) -> str:
        """Format line as hexadecimal with optional ASCII."""
        hex_part = " ".join(f"{byte:02X}" for byte in data)
        ascii_part = ""

        if show_ascii:
            try:
                ascii_part = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in data)
            except:
                ascii_part = "." * len(data)

        offset_str = f"{offset:08X}"

        if ascii_part:
            return f"{offset_str}  {hex_part:<{len(data) * 3}}  {ascii_part}"
        else:
            return f"{offset_str}  {hex_part}"

    def _format_binary_line(self, data: bytes, offset: int) -> str:
        """Format line as binary representation."""
        binary_part = " ".join(f"{byte:08b}" for byte in data)
        offset_str = f"{offset:08X}"
        return f"{offset_str}  {binary_part}"

    def _format_text_line(self, data: bytes, offset: int) -> str:
        """Format line as text representation."""
        try:
            text_part = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in data)
        except:
            text_part = "." * len(data)
        offset_str = f"{offset:08X}"
        return f"{offset_str}  {text_part}"

    def _format_structure_line(self, data: bytes, offset: int) -> str:
        """Format line with structure analysis."""
        # Basic structure detection
        if len(data) >= 4:
            first_four = data[:4]
            if first_four == b'MZ\x90':
                struct_type = "PE Header"
            elif first_four[:2] == b'\x7fELF':
                struct_type = "ELF Header"
            elif first_four[:2] == b'MZ':
                struct_type = "DOS Header"
            else:
                struct_type = "Data"
        else:
            struct_type = "Data"

        offset_str = f"{offset:08X}"
        hex_part = " ".join(f"{byte:02X}" for byte in data[:8])
        return f"{offset_str}  {hex_part:<24}  {struct_type}"

    def _format_mixed_line(self, data: bytes, offset: int, show_ascii: bool) -> str:
        """Format line with mixed hex/binary and ASCII."""
        hex_part = " ".join(f"{byte:02X}" for byte in data[:8])
        binary_data = data[8:16] if len(data) > 8 else data[:8]
        binary_part = " ".join(f"{byte:08b}" for byte in binary_data)

        ascii_part = ""
        if show_ascii:
            try:
                ascii_part = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in data)
            except:
                ascii_part = "." * len(data)

        offset_str = f"{offset:08X}"
        return f"{offset_str}  {hex_part:<24}  {binary_part:<128}  {ascii_part}"

    def _navigate_offset(self, delta: int):
        """Navigate by specified offset delta."""
        new_offset = max(0, self.current_offset + delta)
        if new_offset < len(self.binary_data):
            self.current_offset = new_offset
            self.offset_var.set(f"{new_offset:08X}")
            self._refresh_display()

    def _jump_to_offset(self):
        """Jump to offset from entry field."""
        try:
            offset_str = self.offset_var.get()
            if offset_str.startswith("0x") or offset_str.startswith("0X"):
                offset = int(offset_str, 16)
            else:
                offset = int(offset_str)
            self.current_offset = max(0, min(offset, len(self.binary_data) - 1))
            self.offset_var.set(f"{self.current_offset:08X}")
            self._refresh_display()
        except ValueError:
            self.status_label.config(text="Invalid offset format")

    def _jump_to_start(self):
        """Jump to start of binary data."""
        self.current_offset = 0
        self.offset_var.set("0x00000000")
        self._refresh_display()

    def _jump_to_end(self):
        """Jump to end of visible binary data."""
        bytes_per_line = self.bytes_per_line_var.get()
        self.current_offset = max(0, len(self.binary_data) - bytes_per_line)
        self.offset_var.set(f"{self.current_offset:08X}")
        self._refresh_display()

    def _add_bookmark(self):
        """Add bookmark at current offset."""
        if self.current_offset not in self.bookmarks:
            self.bookmarks.append(self.current_offset)
            self.status_label.config(text=f"Bookmark added at 0x{self.current_offset:08X}")

    def _show_bookmarks(self):
        """Show bookmark dialog."""
        if not self.bookmarks:
            self.status_label.config(text="No bookmarks set")
            return

        bookmark_text = "\n".join(f"0x{offset:08X}" for offset in sorted(self.bookmarks))
        self.status_label.config(text=f"Bookmarks: {len(self.bookmarks)} locations")

    def _search_bytes(self):
        """Search for byte pattern in binary data."""
        search_pattern = self.search_var.get().strip()
        if not search_pattern:
            return

        try:
            # Parse hex pattern like "4A 6F 72" or "4A6F72"
            if " " in search_pattern:
                pattern_bytes = bytes.fromhex(search_pattern.replace(" ", ""))
            else:
                pattern_bytes = bytes.fromhex(search_pattern)

            # Search in binary data
            self.search_results = []
            current_offset = self.current_offset

            while current_offset < len(self.binary_data):
                # Look for pattern
                found_pos = self.binary_data.find(pattern_bytes, current_offset)
                if found_pos == -1:
                    break

                self.search_results.append(found_pos)
                current_offset = found_pos + len(pattern_bytes)

            if self.search_results:
                self.status_label.config(text=f"Found {len(self.search_results)} matches")
                if self.search_results:
                    self.current_offset = self.search_results[0]
                    self.offset_var.set(f"{self.current_offset:08X}")
                    self._refresh_display()
            else:
                self.status_label.config(text="Pattern not found")

        except ValueError:
            self.status_label.config(text="Invalid hex pattern format")

    def _search_next(self):
        """Jump to next search result."""
        if self.search_results:
            current_idx = 0
            try:
                current_idx = self.search_results.index(self.current_offset)
            except ValueError:
                pass

            next_idx = (current_idx + 1) % len(self.search_results)
            self.current_offset = self.search_results[next_idx]
            self.offset_var.set(f"{self.current_offset:08X}")
            self._refresh_display()
            self.status_label.config(text=f"Jumping to match {next_idx + 1}/{len(self.search_results)}")

    def _clear_search(self):
        """Clear search results."""
        self.search_results = []
        self.search_var.set("")
        self.status_label.config(text="Search cleared")

    def _on_view_mode_change(self, event):
        """Handle view mode change."""
        self._refresh_display()

    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        self._refresh_display()

    def _on_canvas_click(self, event):
        """Handle canvas click for offset selection."""
        # Calculate clicked offset based on y position
        char_height = 16
        line_height = char_height
        clicked_line = event.y // line_height

        bytes_per_line = self.bytes_per_line_var.get()
        clicked_offset = clicked_line * bytes_per_line

        if clicked_offset < len(self.binary_data):
            self.current_offset = clicked_offset
            self.offset_var.set(f"{self.current_offset:08X}")
            self._refresh_display()

    def _on_canvas_drag(self, event):
        """Handle canvas drag for scrolling."""
        # Could implement drag scrolling here
        pass

    def _on_mouse_wheel(self, event):
        """Handle mouse wheel for scrolling."""
        # Scroll up/down by lines
        if event.delta > 0:
            self._navigate_offset(-self.bytes_per_line_var.get())
        else:
            self._navigate_offset(self.bytes_per_line_var.get())