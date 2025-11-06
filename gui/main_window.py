"""
Main window for BSEE GUI application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .panels.file_panel import FilePanel
from .panels.visualization_panel import VisualizationPanel
from .panels.metrics_panel import MetricsPanel
from .panels.terminal_panel import TerminalPanel
from .app_controller import AppController


class MainWindow:
    """Main application window for BSEE GUI."""

    def __init__(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("BSEE - Binary Structure Exploration Engine")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Set Windows-style theme
        self.root.style = ttk.Style()
        if 'winnative' in self.root.style.theme_names():
            self.root.style.theme_use('winnative')

        # Initialize app controller
        self.controller = AppController()

        # Progress update queue
        self.progress_queue = queue.Queue()

        # Analysis state
        self.is_analyzing = False
        self.analysis_thread: Optional[threading.Thread] = None

        # Setup GUI components
        self._setup_menu()
        self._setup_layout()
        self._setup_status_bar()

        # Start progress monitoring
        self._monitor_progress()

    def _setup_menu(self):
        """Setup menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Binary File...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences...", command=self._show_preferences)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Clear Terminal", command=self._clear_terminal)
        view_menu.add_separator()
        view_menu.add_command(label="Show Input Folder", command=self._show_input_folder)
        view_menu.add_command(label="Show Results Folder", command=self._show_results_folder)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Create Test File...", command=self._create_test_file)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About BSEE", command=self._show_about)

    def _setup_layout(self):
        """Setup main layout panels."""
        # Main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel (File and Controls)
        left_frame = ttk.Frame(main_paned, width=350)
        main_paned.add(left_frame, weight=1)

        # File panel
        self.file_panel = FilePanel(left_frame, self.controller, self._on_start_analysis)
        self.file_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Middle panel (Visualization)
        middle_frame = ttk.Frame(main_paned)
        main_paned.add(middle_frame, weight=2)

        self.visualization_panel = VisualizationPanel(middle_frame)
        self.visualization_panel.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


        # Right panel (Metrics)
        right_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(right_frame, weight=1)

        self.metrics_panel = MetricsPanel(right_frame)
        self.metrics_panel.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


        # Bottom panel (Terminal)
        terminal_frame = ttk.Frame(self.root, height=200)
        terminal_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        terminal_frame.pack_propagate(False)

        self.terminal_panel = TerminalPanel(terminal_frame)
        self.terminal_panel.frame.pack(fill=tk.BOTH, expand=True)


        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-q>', lambda e: self._on_closing())

    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Status sections
        self.status_text = tk.StringVar(value="Ready")
        ttk.Label(self.status_frame, textvariable=self.status_text).pack(side=tk.LEFT, padx=5)

        ttk.Separator(self.status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.operations_text = tk.StringVar(value="Ops: 0/0")
        ttk.Label(self.status_frame, textvariable=self.operations_text).pack(side=tk.LEFT, padx=5)

        self.score_text = tk.StringVar(value="Score: 0.000")
        ttk.Label(self.status_frame, textvariable=self.score_text).pack(side=tk.LEFT, padx=5)

        self.memory_text = tk.StringVar(value="Memory: 0MB")
        ttk.Label(self.status_frame, textvariable=self.memory_text).pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)

    def _monitor_progress(self):
        """Monitor progress queue and update GUI."""
        try:
            while True:
                message = self.progress_queue.get_nowait()
                self._handle_progress_message(message)
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.root.after(100, self._monitor_progress)

    def _handle_progress_message(self, message: Dict[str, Any]):
        """Handle progress messages from analysis thread."""
        msg_type = message.get('type', 'unknown')

        if msg_type == 'status':
            self.status_text.set(message['text'])
        elif msg_type == 'operations':
            self.operations_text.set(f"Ops: {message['current']}/{message['max']}")
        elif msg_type == 'score':
            self.score_text.set(f"Score: {message['value']:.3f}")
        elif msg_type == 'memory':
            self.memory_text.set(f"Memory: {message['value']}MB")
        elif msg_type == 'progress':
            self.progress_var.set(message['value'])
        elif msg_type == 'terminal':
            self.terminal_panel.add_message(message['text'], message.get('level', 'info'))
        elif msg_type == 'visualization':
            self.visualization_panel.update_display(message)
        elif msg_type == 'metrics':
            self.metrics_panel.update_metrics(message['metrics'])
        elif msg_type == 'finished':
            self._on_analysis_finished(message['success'], message.get('error'))

    def _on_start_analysis(self, config: Dict[str, Any]):
        """Start analysis with given configuration."""
        if self.is_analyzing:
            messagebox.showwarning("Analysis in Progress", "An analysis is already running. Please wait for it to complete.")
            return

        # Validate configuration
        if not config.get('input_file'):
            messagebox.showerror("Error", "Please select an input file.")
            return

        input_path = Path(config['input_file'])
        if not input_path.exists():
            messagebox.showerror("Error", f"Input file '{input_path}' does not exist.")
            return

        # Start analysis in separate thread
        self.is_analyzing = True
        self.file_panel.set_analyzing(True)
        self.status_text.set("Starting analysis...")
        self.progress_var.set(0)

        self.analysis_thread = threading.Thread(
            target=self._run_analysis,
            args=(config,),
            daemon=True
        )
        self.analysis_thread.start()

    def _run_analysis(self, config: Dict[str, Any]):
        """Run analysis in background thread."""
        try:
            self.progress_queue.put({'type': 'terminal', 'text': 'Starting BSEE analysis...', 'level': 'info'})

            # Create CLI arguments from GUI config
            import sys
            from argparse import Namespace

            args = Namespace(
                input_file=config['input_file'],
                policy=config.get('policy', 'config/policies/policy_ideality.yaml'),
                costs=config.get('costs', 'config/costs/cost_default.yaml'),
                strategy=config.get('strategy', 'greedy'),
                metrics=config.get('metrics', 'file_ideality_score,entropy_global,lz77_ratio'),
                target_metrics=config.get('target_metrics', 'file_ideality_score=max,entropy_global=min'),
                max_operations=config.get('max_operations', 1000),
                max_cost=config.get('max_cost', 10000),
                allowed_ops=config.get('allowed_ops'),
                operation_limit=config.get('operation_limit'),
                output_dir=config.get('output_dir', 'results'),
                log_level=config.get('log_level', 'INFO')
            )

            # Create custom pipeline with GUI callbacks
            from bsee.engine.gui_pipeline import GUIPipeline
            pipeline = GUIPipeline(args, self.progress_queue)

            # Run analysis
            results = pipeline.run()

            if results.success:
                self.progress_queue.put({
                    'type': 'terminal',
                    'text': f'Analysis completed successfully!',
                    'level': 'success'
                })
                self.progress_queue.put({
                    'type': 'terminal',
                    'text': f'Results saved to: {results.output_directory}',
                    'level': 'info'
                })
                self.progress_queue.put({
                    'type': 'terminal',
                    'text': f'Final score: {results.final_score:.3f}',
                    'level': 'info'
                })
                self.progress_queue.put({'type': 'finished', 'success': True})
            else:
                self.progress_queue.put({
                    'type': 'terminal',
                    'text': 'Analysis failed',
                    'level': 'error'
                })
                self.progress_queue.put({'type': 'finished', 'success': False, 'error': 'Unknown error'})

        except Exception as e:
            import traceback
            error_msg = f"Analysis error: {str(e)}\n{traceback.format_exc()}"
            self.progress_queue.put({'type': 'terminal', 'text': error_msg, 'level': 'error'})
            self.progress_queue.put({'type': 'finished', 'success': False, 'error': str(e)})

    def _on_analysis_finished(self, success: bool, error: Optional[str] = None):
        """Handle analysis completion."""
        self.is_analyzing = False
        self.file_panel.set_analyzing(False)
        self.progress_var.set(100)

        if success:
            self.status_text.set("Analysis completed successfully")
            messagebox.showinfo("Success", "Analysis completed successfully!")
        else:
            self.status_text.set("Analysis failed")
            if error:
                messagebox.showerror("Error", f"Analysis failed: {error}")

    def _open_file(self):
        """Open file dialog for binary file selection."""
        filename = filedialog.askopenfilename(
            title="Select Binary File",
            filetypes=[
                ("Binary Files", "*.bin *.exe *.dll *.so"),
                ("All Files", "*.*")
            ],
            initialdir=str(Path.cwd())
        )
        if filename:
            self.file_panel.set_input_file(filename)

    def _clear_terminal(self):
        """Clear terminal output."""
        self.terminal_panel.clear()

    def _show_input_folder(self):
        """Show input folder in explorer."""
        input_folder = self.controller.get_input_folder()
        if input_folder and Path(input_folder).exists():
            import subprocess
            subprocess.run(['explorer', input_folder])

    def _show_results_folder(self):
        """Show results folder in explorer."""
        results_folder = self.controller.get_results_folder()
        if results_folder and Path(results_folder).exists():
            import subprocess
            subprocess.run(['explorer', results_folder])

    def _create_test_file(self):
        """Create a test binary file."""
        filename = filedialog.asksaveasfilename(
            title="Create Test File",
            defaultextension=".bin",
            filetypes=[("Binary Files", "*.bin")],
            initialdir=str(Path.cwd())
        )
        if filename:
            self.controller.create_test_file(filename)
            messagebox.showinfo("Success", f"Test file created: {filename}")

    def _show_preferences(self):
        """Show preferences dialog."""
        messagebox.showinfo("Preferences", "Preferences dialog coming soon!")

    def _show_about(self):
        """Show about dialog."""
        about_text = """BSEE - Binary Structure Exploration Engine

Version: 1.0.0
Author: BSEE Team

A comprehensive tool for analyzing binary files through reversible transformations.

Features:
• 100+ binary operations across 6 categories
• 114+ metrics across 9 measurement categories
• Real-time visualization and monitoring
• Professional Windows GUI interface
• Bit-level operation tracking
• Performance and complexity analysis"""

        messagebox.showinfo("About BSEE", about_text)

    def _on_closing(self):
        """Handle window closing."""
        if self.is_analyzing:
            if messagebox.askokcancel("Quit", "Analysis is still running. Do you want to quit?"):
                self.is_analyzing = False
                self.root.quit()
        else:
            self.root.quit()

    def run(self):
        """Start the GUI main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()