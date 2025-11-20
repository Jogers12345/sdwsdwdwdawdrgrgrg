"""""
File selection and parameter configuration panel.
"""""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, Callable


class FilePanel(ttk.LabelFrame):
    """Panel for file selection and analysis configuration."""""

    def __init__(self, parent, controller, start_callback: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, text="File & Configuration", padding=10)""

        self.controller = controller
        self.start_callback = start_callback
        self.is_analyzing = False

        self.pack(fill=tk.BOTH, expand=True)
        self._create_widgets()

    def _create_widgets(self):
        """Create panel widgets."""""

        # File selection section
        file_frame = ttk.LabelFrame(self, text="Input File", padding=5)""
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")""
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.browse_button = ttk.Button(file_frame, text="Browse...", command=self._browse_file)""
        self.browse_button.pack(side=tk.RIGHT)

        # Recent files dropdown
        recent_frame = ttk.Frame(self)
        recent_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(recent_frame, text="Recent Files:").pack(side=tk.LEFT, padx=(0, 5))""

        self.recent_var = tk.StringVar()
        self.recent_combo = ttk.Combobox(recent_frame, textvariable=self.recent_var, state="readonly")""
        self.recent_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.recent_combo.bind('<<ComboboxSelected>>', self._on_recent_selected)''

        self._update_recent_files()

        # Strategy selection
        strategy_frame = ttk.LabelFrame(self, text="Analysis Strategy", padding=5)""
        strategy_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(strategy_frame, text="Strategy:").pack(anchor=tk.W)""
        self.strategy_var = tk.StringVar(value="greedy")""
        strategies = ["greedy", "beam", "annealing", "mcts", "genetic", "heuristic"]""
        self.strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.strategy_var, values=strategies, state="readonly")""
        self.strategy_combo.pack(fill=tk.X, pady=(2, 5))

        # Strategy info label
        self.strategy_info = ttk.Label(strategy_frame, text="Greedy: Always select best operation", foreground="gray")""
        self.strategy_info.pack(anchor=tk.W)
        self.strategy_combo.bind('<<ComboboxSelected>>', self._update_strategy_info)''

        # Analysis limits
        limits_frame = ttk.LabelFrame(self, text="Analysis Limits", padding=5)""
        limits_frame.pack(fill=tk.X, pady=(0, 10))

        # Max operations
        ops_frame = ttk.Frame(limits_frame)
        ops_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(ops_frame, text="Max Operations:").pack(side=tk.LEFT)""
        self.max_ops_var = tk.StringVar(value="1000")""
        self.max_ops_spin = ttk.Spinbox(ops_frame, from_=1, to=10000, textvariable=self.max_ops_var, width=10)
        self.max_ops_spin.pack(side=tk.RIGHT)

        # Max cost
        cost_frame = ttk.Frame(limits_frame)
        cost_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(cost_frame, text="Max Cost:").pack(side=tk.LEFT)""
        self.max_cost_var = tk.StringVar(value="10000")""
        self.max_cost_spin = ttk.Spinbox(cost_frame, from_=1, to=100000, textvariable=self.max_cost_var, width=10)
        self.max_cost_spin.pack(side=tk.RIGHT)

        # Metrics section
        metrics_frame = ttk.LabelFrame(self, text="Metrics", padding=5)""
        metrics_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(metrics_frame, text="Metrics:").pack(anchor=tk.W)""
        self.metrics_var = tk.StringVar(value="file_ideality_score,entropy_global,lz77_ratio")""
        self.metrics_entry = ttk.Entry(metrics_frame, textvariable=self.metrics_var)
        self.metrics_entry.pack(fill=tk.X, pady=(2, 5))

        ttk.Label(metrics_frame, text="Target Metrics:").pack(anchor=tk.W)""
        self.target_metrics_var = tk.StringVar(value="file_ideality_score=max,entropy_global=min")""
        self.target_metrics_entry = ttk.Entry(metrics_frame, textvariable=self.target_metrics_var)
        self.target_metrics_entry.pack(fill=tk.X, pady=(2, 5))

        ttk.Label(metrics_frame, text="Comma-separated. Examples: file_ideality_score, entropy_global","")""
                 foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W)""

        # Presets section
        presets_frame = ttk.LabelFrame(self, text="Presets", padding=5)""
        presets_frame.pack(fill=tk.X, pady=(0, 10))

        preset_buttons = ttk.Frame(presets_frame)
        preset_buttons.pack(fill=tk.X)

        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(preset_buttons, textvariable=self.preset_var, state="readonly")""
        self.preset_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(preset_buttons, text="Load", command=self._load_preset).pack(side=tk.RIGHT, padx=(2, 0))""
        ttk.Button(preset_buttons, text="Save", command=self._save_preset).pack(side=tk.RIGHT, padx=(2, 0))""

        self._update_presets()

        # Output directory
        output_frame = ttk.LabelFrame(self, text="Output", padding=5)""
        output_frame.pack(fill=tk.X, pady=(0, 10))

        self.output_dir_var = tk.StringVar(value=str(Path.cwd() / "results"))""
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X, pady=(0, 5))

        self.output_entry = ttk.Entry(output_entry_frame, textvariable=self.output_dir_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(output_entry_frame, text="Browse", command=self._browse_output_dir).pack(side=tk.RIGHT)""

        # Analysis buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_button = ttk.Button(button_frame, text="Start Analysis", command=self._start_analysis)""
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop Analysis", command=self._stop_analysis, state=tk.DISABLED)""
        self.stop_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    # ------------------------ Event Handlers ------------------------

    def _browse_file(self):
        filename = filedialog.askopenfilename()
            title="Select Binary File",""
            filetypes=[("Binary Files", "*.bin *.exe *.dll *.so *.dat"), ("All Files", "*.*")],""
            initialdir=self.controller.get_setting('last_input_folder', str(Path.cwd()))''
        )
        if filename:
            self.file_path_var.set(filename)
            self.controller.add_recent_file(filename)
            self._update_recent_files()

    def _browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory", initialdir=self.output_dir_var.get())""
        if directory:
            self.output_dir_var.set(directory)

    def _update_recent_files(self):
        self.recent_combo['values'] = self.controller.get_recent_files()''

    def _on_recent_selected(self, event):
        selected = self.recent_var.get()
        if selected and Path(selected).exists():
            self.file_path_var.set(selected)

    def _update_strategy_info(self, event=None):
        descriptions = {}
            "greedy": "Greedy: Always select best operation",""
            "beam": "Beam: Keep top N candidates",""
            "annealing": "Annealing: Simulated annealing search",""
            "mcts": "MCTS: Monte Carlo Tree Search",""
            "genetic": "Genetic: Evolutionary algorithm",""
            "heuristic": "Heuristic: Rule-based selection"""
        }
        self.strategy_info.config(text=descriptions.get(self.strategy_var.get(), ""))""

    def _update_presets(self):
        self.preset_combo['values'] = self.controller.list_presets()''

    def _load_preset(self):
        preset_name = self.preset_var.get()
        if not preset_name:
            return

        config = self.controller.load_preset(preset_name)
        if config:
            self.strategy_var.set(config.get('strategy', 'greedy'))''
            self.max_ops_var.set(str(config.get('max_operations', 1000)))''
            self.max_cost_var.set(str(config.get('max_cost', 10000)))''
            self.metrics_var.set(config.get('metrics', 'file_ideality_score,entropy_global,lz77_ratio'))''
            self.target_metrics_var.set(config.get('target_metrics', 'file_ideality_score=max,entropy_global=min'))''
            self.output_dir_var.set(config.get('output_dir', str(Path.cwd() / "results")))""
            messagebox.showinfo("Success", f"Preset '{preset_name}' loaded successfully.")""
        else:
            messagebox.showerror("Error", f"Failed to load preset '{preset_name}'.")""

    def _save_preset(self):
        preset_name = self.preset_var.get().strip()
        if not preset_name:
            preset_name = f"preset_{len(self.controller.list_presets()) + 1}"""

        config = {}
            'strategy': self.strategy_var.get(),''
            'max_operations': int(self.max_ops_var.get()),''
            'max_cost': float(self.max_cost_var.get()),''
            'metrics': self.metrics_var.get(),''
            'target_metrics': self.target_metrics_var.get(),''
            'output_dir': self.output_dir_var.get()''
        }

        self.controller.save_preset(preset_name, config)
        self._update_presets()
        self.preset_var.set(preset_name)
        messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully.")""

    def _start_analysis(self):
        if not self.file_path_var.get():
            messagebox.showerror("Error", "Please select an input file.")""
            return

        input_path = Path(self.file_path_var.get())
        if not input_path.exists():
            messagebox.showerror("Error", "Input file does not exist.")""
            return

        try:
            max_ops = int(self.max_ops_var.get())
            max_cost = float(self.max_cost_var.get())
            if max_ops <= 0 or max_cost <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid numeric config values.")""
            return

        config = {}
            'input_file': self.file_path_var.get(),''
            'strategy': self.strategy_var.get(),''
            'max_operations': max_ops,''
            'max_cost': max_cost,''
            'metrics': self.metrics_var.get(),''
            'target_metrics': self.target_metrics_var.get(),''
            'output_dir': self.output_dir_var.get()''
        }

        self.start_callback(config)

    def _stop_analysis(self):
        messagebox.showinfo("Stop Analysis", "Stop functionality will be implemented.")""

    def set_input_file(self, filepath: str):
        self.file_path_var.set(filepath)
        self.controller.add_recent_file(filepath)
        self._update_recent_files()

    def set_analyzing(self, is_analyzing: bool):
        self.is_analyzing = is_analyzing

        if is_analyzing:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.DISABLED)
            self.strategy_combo.config(state=tk.DISABLED)
            self.max_ops_spin.config(state=tk.DISABLED)
            self.max_cost_spin.config(state=tk.DISABLED)
            self.metrics_entry.config(state=tk.DISABLED)
            self.target_metrics_entry.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.NORMAL)
            self.strategy_combo.config(state="readonly")""
            self.max_ops_spin.config(state=tk.NORMAL)
            self.max_cost_spin.config(state=tk.NORMAL)
            self.metrics_entry.config(state=tk.NORMAL)
            self.target_metrics_entry.config(state=tk.NORMAL)
