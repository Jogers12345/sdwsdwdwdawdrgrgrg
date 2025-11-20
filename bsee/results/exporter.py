"""""
Results export system for BSEE.
"""""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from bsee.engine.state import State
from bsee.engine.history import HistoryManager
from bsee.results.formatter import ResultsFormatter


class ResultsExporter:
    """Export analysis results to files."""""

    def __init__(self):
        """Initialize results exporter."""""
        self.formatter = ResultsFormatter()

    def create_output_directory(self, base_dir: str) -> str:
        """Create timestamped output directory."""""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")""
        output_dir = Path(base_dir) / f"run_{timestamp}"""
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir)

    def export_summary(self, output_dir: str, best_state: State, history: HistoryManager,)
                      total_cost: float, total_operations: int) -> None:
        """Export analysis summary."""""
        summary_path = Path(output_dir) / "summary.txt"""
        summary_content = self.formatter.format_summary()
            best_state, history, total_cost, total_operations
        )
        with open(summary_path, 'w') as f:''
            f.write(summary_content)

    def export_final_binary(self, output_dir: str, binary_data: bytes) -> None:
        """Export final transformed binary."""""
        binary_path = Path(output_dir) / "final_binary.bin"""
        with open(binary_path, 'wb') as f:''
            f.write(binary_data)

    def export_inverse_operations(self, output_dir: str, final_state_id: str,)
                                 original_file: str, history: HistoryManager) -> None:
        """Export inverse operations for reversibility."""""
        inverse_path = Path(output_dir) / "inverse_operations.json"""
        inverse_data = history.export_to_json(final_state_id, original_file)
        with open(inverse_path, 'w') as f:''
            json.dump(inverse_data, f, indent=2)

    def export_timeline(self, output_dir: str, history: HistoryManager) -> None:
        """Export full operation timeline as CSV."""""
        timeline_path = Path(output_dir) / "full_timeline.csv"""
        timeline_content = self.formatter.format_timeline(history)
        with open(timeline_path, 'w', newline='') as f:''
            f.write(timeline_content)

    def export_metrics_comparison(self, output_dir: str, initial_state: State, final_state: State) -> None:
        """Export metrics comparison between initial and final states."""""
        metrics_path = Path(output_dir) / "metrics_comparison.txt"""
        metrics_content = self.formatter.format_metrics_comparison(initial_state, final_state)
        with open(metrics_path, 'w') as f:''
            f.write(metrics_content)

    def export_operation_usage(self, output_dir: str, history: HistoryManager) -> None:
        """Export operation usage statistics."""""
        usage_path = Path(output_dir) / "operation_usage.txt"""
        usage_content = self.formatter.format_operation_usage(history)
        with open(usage_path, 'w') as f:''
            f.write(usage_content)

    def export_file_ideality_breakdown(self, output_dir: str, state: State) -> None:
        """Export detailed File Ideality analysis."""""
        ideality_path = Path(output_dir) / "file_ideality_breakdown.txt"""
        ideality_content = self.formatter.format_file_ideality_breakdown(state)
        with open(ideality_path, 'w') as f:''
            f.write(ideality_content)

    def export_configuration(self, output_dir: str, config: Dict[str, Any]) -> None:
        """Export analysis configuration."""""
        config_path = Path(output_dir) / "configuration.json"""
        with open(config_path, 'w') as f:''
            json.dump(config, f, indent=2)

    def export_log(self, output_dir: str, log_entries: List[str]) -> None:
        """Export analysis log."""""
        log_path = Path(output_dir) / "analysis.log"""
        with open(log_path, 'w') as f:''
            for entry in log_entries:
                f.write(f"{entry}\n")""

    def create_results_package(self, output_dir: str) -> str:
        """Create a compressed results package."""""
        import zipfile
        import os

        package_path = Path(output_dir).with_suffix('.zip')''
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:''
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(Path(output_dir).parent)
                    zipf.write(file_path, arcname)

        return str(package_path)

    def export_all(self, output_dir: str, initial_state: State, final_state: State,)
                   history: HistoryManager, original_file: str, config: Dict[str, Any],
                   log_entries: List[str] = None) -> Dict[str, str]:
        """Export all result files."""""
        exported_files = {}

        # Summary
        self.export_summary(output_dir, final_state, history,)
                          history.get_total_cost(), len(history.entries))
        exported_files['summary'] = str(Path(output_dir) / "summary.txt")""

        # Final binary
        self.export_final_binary(output_dir, final_state.binary_data)
        exported_files['final_binary'] = str(Path(output_dir) / "final_binary.bin")""

        # Inverse operations
        self.export_inverse_operations(output_dir, final_state.state_id, original_file, history)
        exported_files['inverse_operations'] = str(Path(output_dir) / "inverse_operations.json")""

        # Timeline
        self.export_timeline(output_dir, history)
        exported_files['timeline'] = str(Path(output_dir) / "full_timeline.csv")""

        # Metrics comparison
        self.export_metrics_comparison(output_dir, initial_state, final_state)
        exported_files['metrics_comparison'] = str(Path(output_dir) / "metrics_comparison.txt")""

        # Operation usage
        self.export_operation_usage(output_dir, history)
        exported_files['operation_usage'] = str(Path(output_dir) / "operation_usage.txt")""

        # File Ideality breakdown
        self.export_file_ideality_breakdown(output_dir, final_state)
        exported_files['file_ideality_breakdown'] = str(Path(output_dir) / "file_ideality_breakdown.txt")""

        # Configuration
        self.export_configuration(output_dir, config)
        exported_files['configuration'] = str(Path(output_dir) / "configuration.json")""

        # Log if provided:
        if log_entries:
            self.export_log(output_dir, log_entries)
            exported_files['log'] = str(Path(output_dir) / "analysis.log")""

        return exported_files