"""
Terminal output panel for real-time logging.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List
from datetime import datetime
import threading


class TerminalPanel:
    """Panel for displaying terminal output and logs."""

    def __init__(self, parent):
        """Initialize terminal panel."""
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.max_lines = 1000
        self.messages: List[str] = []
        self.lock = threading.Lock()

        self._create_widgets()

    def _create_widgets(self):
        """Create terminal widgets."""
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        # Clear button
        ttk.Button(toolbar, text="Clear", command=self.clear).pack(side=tk.RIGHT, padx=(5, 0))

        # Save button
        ttk.Button(toolbar, text="Save Log", command=self.save_log).pack(side=tk.RIGHT, padx=(5, 0))

        # Search frame
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, padx=(10, 10))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind('<KeyRelease>', self._on_search_change)

        # Level filter
        ttk.Label(toolbar, text="Level:").pack(side=tk.LEFT, padx=(10, 5))
        self.level_var = tk.StringVar(value="All")
        level_combo = ttk.Combobox(toolbar, textvariable=self.level_var,
                                  values=["All", "Info", "Warning", "Error", "Success"],
                                  width=10, state="readonly")
        level_combo.pack(side=tk.LEFT)
        level_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_display())

        # Terminal text area
        self.text_area = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="black",
            fg="lightgray",
            insertbackground="white",
            selectbackground="darkblue",
            height=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for different message types
        self.text_area.tag_configure("timestamp", foreground="gray")
        self.text_area.tag_configure("info", foreground="lightgray")
        self.text_area.tag_configure("warning", foreground="yellow")
        self.text_area.tag_configure("error", foreground="red")
        self.text_area.tag_configure("success", foreground="lightgreen")
        self.text_area.tag_configure("debug", foreground="darkgray")
        self.text_area.tag_configure("highlight", background="darkblue")

        # Bind double-click for copy functionality
        self.text_area.bind("<Double-Button-1>", self._copy_selected)

    def add_message(self, message: str, level: str = "info"):
        """Add a message to the terminal."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        with self.lock:
            self.messages.append({
                'text': formatted_message,
                'level': level.lower(),
                'timestamp': timestamp,
                'raw_message': message
            })

            # Limit message history
            if len(self.messages) > self.max_lines:
                self.messages = self.messages[-self.max_lines:]

        # Update display in main thread
        self.text_area.after(0, self._refresh_display)

    def _refresh_display(self):
        """Refresh the terminal display."""
        with self.lock:
            # Clear display
            self.text_area.delete(1.0, tk.END)

            # Get filter settings
            level_filter = self.level_var.get().lower()
            search_text = self.search_var.get().lower()

            # Add messages
            for msg_data in self.messages:
                level = msg_data['level']
                raw_message = msg_data['raw_message'].lower()

                # Apply level filter
                if level_filter != "all" and level != level_filter:
                    continue

                # Apply search filter
                if search_text and search_text not in raw_message:
                    continue

                # Insert message with appropriate formatting
                start_pos = self.text_area.index(tk.END)

                # Insert timestamp
                timestamp_end = f"{start_pos}+9c"
                self.text_area.insert(tk.END, f"[{msg_data['timestamp']}] ", "timestamp")

                # Insert message
                message_start = self.text_area.index(tk.END)
                self.text_area.insert(tk.END, f"{msg_data['raw_message']}\n", level)

                message_end = self.text_area.index(tk.END)

                # Highlight search text
                if search_text:
                    self._highlight_search_text(msg_data['raw_message'], search_text, message_start, message_end)

            # Auto-scroll to bottom
            self.text_area.see(tk.END)

    def _highlight_search_text(self, text: str, search_term: str, start_idx: str, end_idx: str):
        """Highlight search term occurrences."""
        if not search_term:
            return

        start = 0
        while True:
            idx = text.lower().find(search_term.lower(), start)
            if idx == -1:
                break

            # Calculate position in text widget
            line_start = start_idx.split('.')[0]
            char_start = str(int(start_idx.split('.')[1]) + idx)
            char_end = str(int(char_start) + len(search_term))

            highlight_start = f"{line_start}.{char_start}"
            highlight_end = f"{line_start}.{char_end}"

            try:
                self.text_area.tag_add("highlight", highlight_start, highlight_end)
            except:
                break  # Invalid index, probably out of bounds

            start = idx + 1

    def _on_search_change(self, event):
        """Handle search text change."""
        self._refresh_display()

    def _copy_selected(self, event):
        """Copy selected text to clipboard."""
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.clipboard_clear()
            self.text_area.clipboard_append(selected_text)
        except:
            pass  # No text selected

    def clear(self):
        """Clear all messages."""
        with self.lock:
            self.messages = []
        self.text_area.delete(1.0, tk.END)

    def save_log(self):
        """Save terminal log to file."""
        from tkinter import filedialog
        from pathlib import Path

        filename = filedialog.asksaveasfilename(
            title="Save Terminal Log",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"bsee_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    with self.lock:
                        for msg_data in self.messages:
                            f.write(f"{msg_data['text']}\n")

                self.add_message(f"Log saved to: {filename}", "success")
            except Exception as e:
                self.add_message(f"Failed to save log: {e}", "error")

    def add_separator(self):
        """Add a visual separator."""
        self.add_message("-" * 50, "info")

    def add_section(self, title: str):
        """Add a section header."""
        self.add_separator()
        self.add_message(f"=== {title} ===", "success")
        self.add_separator()

    def set_max_lines(self, max_lines: int):
        """Set maximum number of lines to keep in history."""
        self.max_lines = max_lines

        with self.lock:
            if len(self.messages) > max_lines:
                self.messages = self.messages[-max_lines:]

        self._refresh_display()