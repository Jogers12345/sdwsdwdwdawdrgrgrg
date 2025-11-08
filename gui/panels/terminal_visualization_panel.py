"""
Terminal-based Visualization Panel for BSEE

Provides ASCII-based visualizations when matplotlib is unavailable.
Implements charts and graphs using terminal characters.
"""

from typing import List, Dict, Any
from collections import Counter
import math


class TerminalVisualizationPanel:
    """Terminal-based visualization panel using ASCII art."""

    def __init__(self, fallback_config: Dict[str, str]):
        """
        Initialize terminal visualization panel.

        Args:
            fallback_config: Configuration dict with fallback settings
        """
        self.fallback_config = fallback_config
        self.chart_width = int(fallback_config.get('chart_width', 60))
        self.chart_height = int(fallback_config.get('chart_height', 20))
        self.max_results_display = int(fallback_config.get('max_results_display', 10))

    def plot_score_progression(self, scores: List[float], title: str = "Score Progression"):
        """
        Create ASCII line chart of score progression.

        Args:
            scores: List of score values over time
            title: Chart title
        """
        if not scores:
            print("No data to plot")
            return

        # Simple ASCII line chart
        min_score = min(scores)
        max_score = max(scores)
        range_score = max_score - min_score if max_score != min_score else 1

        print(f"\n{title}")
        print("=" * len(title))

        height = min(self.chart_height, 20)
        width = min(self.chart_width, len(scores))

        # Scale scores to chart height
        scaled_scores = [int((s - min_score) / range_score * (height - 1)) for s in scores]

        # Create chart grid
        chart = [[' ' for _ in range(width)] for _ in range(height)]

        # Plot points
        for col in range(width):
            idx = int(col * len(scores) / width)
            row = scaled_scores[idx]
            if 0 <= row < height:
                chart[height - 1 - row][col] = '●'

        # Print chart with axes
        for row in range(height):
            y_value = min_score + (height - 1 - row) * range_score / (height - 1)
            line = f"{y_value:6.2f} │" + "".join(chart[row])
            print(line)

        # Print x-axis
        print("       └" + "─" * width)

        # Print x-axis labels
        step = max(1, len(scores) // 10)
        for i in range(0, len(scores), step):
            pos = int(i * width / len(scores))
            print(f"{i:>7}", end="")
        print()

    def plot_operation_distribution(self, operations: List[str], title: str = "Operation Usage"):
        """
        Create ASCII bar chart of operation usage.

        Args:
            operations: List of operation names
            title: Chart title
        """
        op_counts = Counter(operations)
        if not op_counts:
            print("No operations to plot")
            return

        print(f"\n{title}")
        print("=" * len(title))

        max_count = max(op_counts.values())
        max_name_len = max(len(name) for name in op_counts.keys())

        # Sort by count (descending)
        sorted_ops = sorted(op_counts.items(), key=lambda x: x[1], reverse=True)

        for op_name, count in sorted_ops[:self.max_results_display]:
            bar_length = int(count / max_count * min(30, self.chart_width - max_name_len - 10))
            bar = "█" * bar_length
            percentage = (count / sum(op_counts.values())) * 100
            print(f"{op_name:<{max_name_len}} │ {bar:<30} {count:>4d} ({percentage:5.1f}%)")

    def plot_compression_ratios(self, ratios: List[float], labels: List[str] = None,
                               title: str = "Compression Ratios"):
        """
        Create ASCII bar chart of compression ratios.

        Args:
            ratios: List of compression ratio values
            labels: Optional labels for each ratio
            title: Chart title
        """
        if not ratios:
            print("No compression ratios to plot")
            return

        print(f"\n{title}")
        print("=" * len(title))

        max_ratio = max(ratios) if ratios else 1
        max_label_len = max(len(str(label)) for label in labels) if labels else 10

        for i, ratio in enumerate(ratios[:self.max_results_display]):
            bar_length = int(ratio / max_ratio * min(30, self.chart_width - max_label_len - 15))
            bar = "█" * bar_length
            label = str(labels[i]) if labels and i < len(labels) else f"Item {i+1}"
            print(f"{label:<{max_label_len}} │ {bar:<30} {ratio:>6.3f}x")

    def plot_entropy_heatmap(self, entropy_values: List[float],
                            title: str = "Entropy Heatmap"):
        """
        Create ASCII heatmap of entropy values.

        Args:
            entropy_values: List of entropy values
            title: Chart title
        """
        if not entropy_values:
            print("No entropy data to plot")
            return

        print(f"\n{title}")
        print("=" * len(title))

        max_entropy = max(entropy_values) if entropy_values else 1

        # ASCII gradient characters for heatmap
        gradient = [' ', '░', '▒', '▓', '█']

        # Determine grid size (roughly square)
        grid_size = int(math.sqrt(len(entropy_values))) + 1

        for i in range(0, len(entropy_values), grid_size):
            row_values = entropy_values[i:i+grid_size]
            row_chars = []
            for value in row_values:
                if max_entropy > 0:
                    normalized = value / max_entropy
                    char_index = min(int(normalized * len(gradient)), len(gradient) - 1)
                    row_chars.append(gradient[char_index])
                else:
                    row_chars.append(' ')
            print("".join(row_chars))

    def show_search_tree_ascii(self, nodes: List[Dict], max_depth: int = 5):
        """
        Display search tree structure in ASCII.

        Args:
            nodes: List of tree nodes with structure
            max_depth: Maximum depth to display
        """
        print("\nSearch Tree Structure")
        print("=" * 20)

        def print_node(node, depth=0, prefix="", is_last=True):
            if depth > max_depth:
                return

            indent = "    " * depth
            score = node.get('score', 0)
            ops = node.get('operations', [])

            op_str = ops[0] if ops else "root"
            connector = "└─" if is_last else "├─"

            print(f"{prefix}{indent}{connector} {op_str} (score: {score:.3f})")

            children = node.get('children', [])
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                child_prefix = prefix + indent + ("    " if is_last_child else "│   ")
                print_node(child, depth + 1, child_prefix, is_last_child)

        # Start with root nodes
        for i, node in enumerate(nodes[:3]):  # Show first 3 root branches
            is_last = (i == min(len(nodes), 3) - 1)
            print_node(node, 0, "", is_last)

    def show_progress_bar(self, current: int, total: int, width: int = 50,
                         label: str = "Progress"):
        """
        Show ASCII progress bar.

        Args:
            current: Current progress value
            total: Total target value
            width: Width of progress bar
            label: Progress label
        """
        if total == 0:
            percentage = 100
        else:
            percentage = (current / total) * 100

        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)

        print(f"\r{label}: [{bar}] {percentage:5.1f}% ({current}/{total})", end="", flush=True)

        if current >= total:
            print()  # New line when complete

    def show_table(self, headers: List[str], rows: List[List[str]],
                  title: str = "Data Table"):
        """
        Display ASCII table.

        Args:
            headers: List of column headers
            rows: List of row data
            title: Table title
        """
        if not headers or not rows:
            print("No data to display in table")
            return

        print(f"\n{title}")
        print("=" * len(title))

        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Create header separator
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        # Print table
        print(separator)
        header_row = "|" + "|".join(f" {header:<{col_widths[i]}} "
                                   for i, header in enumerate(headers)) + "|"
        print(header_row)
        print(separator)

        # Print data rows
        for row in rows[:self.max_results_display]:
            row_str = "|" + "|".join(f" {str(cell):<{col_widths[i]}} "
                                    for i, cell in enumerate(row[:len(col_widths)])) + "|"
            print(row_str)

        print(separator)

        if len(rows) > self.max_results_display:
            print(f"... and {len(rows) - self.max_results_display} more rows")

    def show_statistics_box(self, stats: Dict[str, Any], title: str = "Statistics"):
        """
        Display statistics in a formatted box.

        Args:
            stats: Dictionary of statistics
            title: Box title
        """
        print(f"\n┌─ {title}")
        print("│" + "─" * (len(title) + 4))

        for key, value in stats.items():
            if isinstance(value, float):
                print(f"│ {key}: {value:.4f}")
            else:
                print(f"│ {key}: {value}")

        print("└" + "─" * (len(title) + 8))

    def clear_screen(self):
        """Clear terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_help(self):
        """Display help information for terminal visualizations."""
        help_text = """
BSEE Terminal Visualization Help
================================

Available Commands:
  plot_scores <data>     - Plot score progression chart
  plot_operations <data> - Plot operation distribution
  plot_ratios <data>     - Plot compression ratios
  plot_entropy <data>    - Plot entropy heatmap
  show_tree <data>       - Show search tree structure
  progress <current> <total> - Show progress bar
  table <headers> <rows> - Display data table
  stats <data>           - Show statistics box
  clear                  - Clear screen
  help                   - Show this help

Data Formats:
  - Numbers: space-separated values (e.g., "1.2 3.4 5.6")
  - Labels: comma-separated values (e.g., "op1,op2,op3")
  - Tables: headers|row1,cell2|row2,cell1
        """
        print(help_text)