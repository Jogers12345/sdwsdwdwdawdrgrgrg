"""
Enhanced Console Panel Component for BSEE GUI
Provides better console experience with logging, filtering, and export.
"""

import tkinter as tk
from tkinter import ttk, Canvas, Scrollbar, Frame, Label, Button, Text
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from datetime import datetime
import queue
import threading
from typing import Dict, List, Any, Optional
import re


class EnhancedConsolePanel:
    """Enhanced console panel with improved UX and functionality."""

    def __init__(self, parent):
        """Initialize enhanced console panel."""
        self.parent = parent
        self.message_queue = queue.Queue()
        self.log_history = []
        self.filter_level = "ALL"  # ALL, INFO, WARNING, ERROR, DEBUG
        self.max_history = 1000
        self.auto_scroll = True
        self.show_timestamps = True
        self.word_wrap = True

        self._setup_ui()
        self._setup_shortcuts()
        self._start_message_monitor()

    def _setup_ui(self):
        """Setup enhanced console UI."""
        # Main container with title
        main_frame = ttk.LabelFrame(self.parent, text="Enhanced Console", padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        # Filter controls
        filter_frame = ttk.LabelFrame(toolbar_frame, text="Console Filter")
        filter_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Level:").pack(side=tk.LEFT, padx=2)
        self.filter_var = tk.StringVar(value="ALL")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["ALL", "INFO", "WARNING", "ERROR", "DEBUG"],
                                   state="readonly", width=10)
        filter_combo.pack(side=tk.LEFT, padx=2)
        filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Options
        options_frame = ttk.Frame(filter_frame)
        options_frame.pack(side=tk.LEFT, padx=10)

        self.timestamp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Timestamp",
                     variable=self.timestamp_var,
                     command=self._update_display).pack(side=tk.LEFT, padx=2)

        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-scroll",
                     variable=self.auto_scroll_var,
                     command=self._toggle_auto_scroll).pack(side=tk.LEFT, padx=2)

        self.word_wrap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Word Wrap",
                     variable=self.word_wrap_var,
                     command=self._toggle_word_wrap).pack(side=tk.LEFT, padx=2)

        # Search controls
        search_frame = ttk.LabelFrame(toolbar_frame, text="Search")
        search_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        ttk.Button(search_frame, text="🔍", width=5,
                  command=self._search_next).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="🔁", width=5,
                  command=self._search_previous).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="⏭", width=5,
                  command=self._clear_search).pack(side=tk.LEFT, padx=2)

        # Export controls
        export_frame = ttk.Frame(toolbar_frame)
        export_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Button(export_frame, text="📋 Copy", width=8,
                  command=self._copy_console).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="💾 Save", width=8,
                  command=self._save_console).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="🗑️ Clear", width=8,
                  command=self._clear_console).pack(side=tk.LEFT, padx=2)

        # Console text area with enhanced features
        console_frame = ttk.Frame(main_frame)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create enhanced text widget
        self.console_text = ScrolledText(console_frame, wrap=tk.WORD,
                                         font=("Consolas", 10),
                                         bg="black", fg="lightgreen",
                                         insertbackground="black",
                                         selectbackground="darkblue",
                                         height=15, width=80)

        # Configure text tags for color coding
        self.console_text.tag_configure("INFO", foreground="lightgreen", font=("Consolas", 10, "normal"))
        self.console_text.tag_configure("WARNING", foreground="yellow", font=("Consolas", 10, "bold"))
        self.console_text.tag_configure("ERROR", foreground="red", font=("Consolas", 10, "bold"))
        self.console_text.tag_configure("DEBUG", foreground="cyan", font=("Consolas", 10, "normal"))
        self.console_text.tag_configure("TIMESTAMP", foreground="gray", font=("Consolas", 9, "normal"))
        self.console_text.tag_configure("SEARCH_HIGHLIGHT", background="darkblue", foreground="white")

        # Add line numbers for better reference
        self.line_numbers_var = tk.BooleanVar(value=False)
        self.setup_line_numbers()

        self.console_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

        self.status_label = ttk.Label(self.status_frame, text="Console Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.count_label = ttk.Label(self.status_frame, text="0 messages", relief=tk.SUNKEN)
        self.count_label.pack(side=tk.RIGHT, padx=10)

        # Initialize search state
        self.search_results = []
        self.current_search_index = 0

    def setup_line_numbers(self):
        """Setup line numbers in console."""
        if self.line_numbers_var.get():
            # Enable line numbers (implementation would be more complex)
            self.console_text.config(insertunfocuses="1")
        else:
            self.console_text.config(insertunfocuses="0")

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for enhanced console."""
        self.parent.bind("<Control-l>", lambda e: self.filter_var.set("ALL"))
        self.parent.bind("<Control-i>", lambda e: self.filter_var.set("INFO"))
        self.parent.bind("<Control-w>", lambda e: self.filter_var.set("WARNING"))
        self.parent.bind("<Control-e>", lambda e: self.filter_var.set("ERROR"))
        self.parent.bind("<Control-d>", lambda e: self.filter_var.set("DEBUG"))
        self.parent.bind("<Control-f>", lambda e: self.search_var.focus_set())
        self.parent.bind("<F3>", lambda e: self._search_next())
        self.parent.bind("<Control-c>", lambda e: self._copy_console())
        self.parent.bind("<Control-s>", lambda e: self._save_console())

    def _start_message_monitor(self):
        """Start background message monitor."""
        def monitor_messages():
            while True:
                try:
                    message = self.message_queue.get(timeout=0.1)
                    self._display_message(message)
                except queue.Empty:
                    pass
                except:
                    break

        monitor_thread = threading.Thread(target=monitor_messages, daemon=True)
        monitor_thread.start()

    def add_message(self, level: str, text: str, timestamp: Optional[str] = None):
        """Add message to console queue."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        message = {
            'level': level,
            'text': text,
            'timestamp': timestamp
        }
        self.message_queue.put(message)

    def _display_message(self, message: Dict[str, Any]):
        """Display message in console."""
        level = message.get('level', 'INFO')
        text = message.get('text', '')
        timestamp = message.get('timestamp', '')

        # Check filter
        if self.filter_level != "ALL" and level != self.filter_level:
            return

        # Format message
        if self.show_timestamps:
            formatted_text = f"[{timestamp}] [{level}] {text}"
            timestamp_part = f"[{timestamp}] [{level}] "
            message_part = f"{text}"
        else:
            formatted_text = f"[{level}] {text}"
            timestamp_part = f"[{level}] "
            message_part = f"{text}"

        # Add to history
        self.log_history.append(message)
        if len(self.log_history) > self.max_history:
            self.log_history.pop(0)

        # Insert into console with proper formatting
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, formatted_text, level)

        # Add timestamp tag separately for styling
        if self.show_timestamps:
            start_index = self.console_text.index(tk.END) + f" -{len(timestamp_part)}c"
            end_index = self.console_text.index(tk.END)
            self.console_text.tag_add("TIMESTAMP", start_index, end_index)

        # Update status
        self._update_status()

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            self.console_text.see(tk.END)

        # Limit buffer size for performance
        line_count = int(self.console_text.index('end-1c').split('.')[0])
        if line_count > 1000:  # Keep last 1000 lines
            self.console_text.delete('1.0', f'{line_count - 500}.0')

    def _on_filter_change(self, event):
        """Handle filter level change."""
        self.filter_level = self.filter_var.get()
        self._refresh_display()

    def _on_search_change(self, *args):
        """Handle search text change."""
        search_text = self.search_var.get().lower()
        if not search_text:
            self._clear_search_highlight()
            return

        # Find all matches
        self.search_results = []
        content = self.console_text.get('1.0', tk.END)
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if search_text in line.lower():
                self.search_results.append(i)

        self._highlight_search_results()
        self.current_search_index = 0
        self._jump_to_search_result()

    def _search_next(self):
        """Jump to next search result."""
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self._jump_to_search_result()

    def _search_previous(self):
        """Jump to previous search result."""
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self._jump_to_search_result()

    def _jump_to_search_result(self):
        """Jump to current search result."""
        if not self.search_results:
            return

        line_num = self.search_results[self.current_search_index] + 1
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"

        self.console_text.see(line_start)
        self.console_text.tag_remove("SEARCH_HIGHLIGHT", '1.0', tk.END)
        self.console_text.tag_add("SEARCH_HIGHLIGHT", line_start, line_end)

    def _highlight_search_results(self):
        """Highlight all search results."""
        content = self.console_text.get('1.0', tk.END)
        lines = content.split('\n')

        for line_num in self.search_results:
            line_start = f"{line_num + 1}.0"
            line_end = f"{line_num + 1}.end"
            self.console_text.tag_add("SEARCH_HIGHLIGHT", line_start, line_end)

    def _clear_search_highlight(self):
        """Clear search highlighting."""
        self.console_text.tag_remove("SEARCH_HIGHLIGHT", '1.0', tk.END)

    def _clear_search(self):
        """Clear search."""
        self.search_var.set("")
        self.search_results = []
        self.current_search_index = 0
        self._clear_search_highlight()

    def _refresh_display(self):
        """Refresh console display based on filter."""
        # This would need to re-render all messages
        # For now, just update status
        self._update_status()

    def _update_status(self):
        """Update status bar."""
        # Count messages by filter level
        total_messages = len(self.log_history)
        filtered_messages = len([msg for msg in self.log_history
                              if self.filter_level == "ALL" or msg['level'] == self.filter_level])

        self.status_label.config(text=f"Console ({self.filter_level}): {filtered_messages}/{total_messages} messages")
        self.count_label.config(text=f"Total: {total_messages} | Filtered: {filtered_messages}")

    def _toggle_auto_scroll(self):
        """Toggle auto-scroll."""
        self.auto_scroll = self.auto_scroll_var.get()

    def _toggle_word_wrap(self):
        """Toggle word wrap."""
        self.word_wrap = self.word_wrap_var.get()
        if self.word_wrap:
            self.console_text.config(wrap=tk.WORD)
        else:
            self.console_text.config(wrap=tk.NONE)

    def _copy_console(self):
        """Copy console content to clipboard."""
        try:
            # Get selected text or all text
            selected_text = self.console_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not selected_text:
                selected_text = self.console_text.get('1.0', tk.END)

            self.parent.clipboard_clear()
            self.parent.clipboard_append(selected_text)
            self.add_message("INFO", f"Copied {len(selected_text)} characters to clipboard")
        except Exception as e:
            self.add_message("ERROR", f"Failed to copy: {str(e)}")

    def _save_console(self):
        """Save console content to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bsee_console_{timestamp}.log"

            # Get all content or filtered content
            if self.filter_level == "ALL":
                content = self.console_text.get('1.0', tk.END)
            else:
                # Filter content by level
                lines = self.console_text.get('1.0', tk.END).split('\n')
                filtered_lines = []
                for line in lines:
                    if self._line_contains_level(line, self.filter_level):
                        filtered_lines.append(line)
                content = '\n'.join(filtered_lines)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            self.add_message("INFO", f"Console saved to {filename}")
        except Exception as e:
            self.add_message("ERROR", f"Failed to save: {str(e)}")

    def _clear_console(self):
        """Clear console."""
        self.console_text.delete('1.0', tk.END)
        self.log_history.clear()
        self._update_status()

    def _line_contains_level(self, line: str, level: str) -> bool:
        """Check if line contains specified log level."""
        level_pattern = rf'\[{level}\]'
        return re.search(level_pattern, line) is not None

    def set_filter_level(self, level: str):
        """Set filter level programmatically."""
        self.filter_var.set(level)
        self.filter_level = level
        self._refresh_display()