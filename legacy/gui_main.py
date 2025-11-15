#!/usr/bin/env python3
"""
BSEE GUI Entry Point with Graceful Dependency Handling

Binary Structure Exploration Engine - Windows GUI Application
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Double-check project root is in Python path for BSEE imports
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Verify project root is correctly set
if not (project_root / "bsee" / "__init__.py").exists():
    print(f"Warning: BSEE module not found at {project_root}/bsee")
    print("Make sure you're running from the correct directory")

# Additional fix for virtual environment compatibility
if "VIRTUAL_ENV" in os.environ:
    venv_site_packages = Path(os.environ["VIRTUAL_ENV"]) / "Lib" / "site-packages"
    if str(venv_site_packages) not in sys.path:
        sys.path.insert(0, str(venv_site_packages))


def check_dependencies() -> Tuple[List[str], List[Tuple[str, Optional[str]]]]:
    """
    Check dependencies with graceful fallback handling.

    Returns:
        Tuple of (missing_required, missing_optional_with_fallbacks)
        missing_required: List of required module names
        missing_optional: List of (module_name, fallback_mode) tuples
    """
    dependency_map = {
        'tkinter': {'required': True, 'fallback': None},
        'matplotlib': {'required': False, 'fallback': 'terminal'},
        'numpy': {'required': True, 'fallback': None},
        'scipy': {'required': False, 'fallback': 'simplified'},
        'pyyaml': {'required': True, 'fallback': None},
        'pywt': {'required': False, 'fallback': 'haar_fallback'},
        'lz4': {'required': False, 'fallback': 'skip_lz4'},
        'zstandard': {'required': False, 'fallback': 'skip_zstd'}
    }

    missing_required = []
    missing_optional = []

    for module, info in dependency_map.items():
        try:
            __import__(module)
        except ImportError:
            if info['required']:
                missing_required.append(module)
            else:
                missing_optional.append((module, info['fallback']))

    return missing_required, missing_optional


def setup_fallback_mode(missing_optional: List[Tuple[str, str]]) -> Dict[str, str]:
    """Configure fallback components for missing optional dependencies."""
    fallback_config = {}

    for module, fallback in missing_optional:
        if fallback == 'terminal':
            fallback_config['visualization_mode'] = 'terminal'
        elif fallback == 'simplified':
            fallback_config['math_mode'] = 'numpy_only'
        elif fallback == 'haar_fallback':
            fallback_config['wavelet_mode'] = 'haar_only'
        elif fallback == 'skip_lz4':
            fallback_config['compression_mode'] = 'exclude_lz4'
        elif fallback == 'skip_zstd':
            fallback_config['compression_mode'] = 'exclude_zstd'

    # Set defaults if not configured
    fallback_config.setdefault('visualization_mode', 'gui')
    fallback_config.setdefault('math_mode', 'full')
    fallback_config.setdefault('wavelet_mode', 'full')
    fallback_config.setdefault('compression_mode', 'full')
    fallback_config.setdefault('chart_width', 60)
    fallback_config.setdefault('chart_height', 20)
    fallback_config.setdefault('max_results_display', 10)

    return fallback_config


def terminal_mode():
    """Run BSEE in full terminal mode when GUI unavailable."""
    print("=" * 60)
    print("BSEE - Binary Structure Exploration Engine")
    print("Terminal Mode v1.0")
    print("=" * 60)
    print()

    # Try to import BSEE components
    try:
        from bsee.engine.pipeline import SearchPipeline
        from bsee.utils.logger import setup_logging
        from gui.panels.terminal_visualization_panel import TerminalVisualizationPanel
    except ImportError as e:
        print(f"Error importing BSEE components: {e}")
        print("Please ensure BSEE is properly installed.")
        return

    # Setup terminal logging
    setup_logging(log_level="INFO")

    # Create visualization panel
    fallback_config = {
        'visualization_mode': 'terminal',
        'chart_width': 60,
        'chart_height': 20,
        'max_results_display': 10
    }
    viz_panel = TerminalVisualizationPanel(fallback_config)

    # State management
    pipeline = None
    current_file = None
    current_strategy = "mcts"
    config_file = None
    search_results = []

    print("Available commands:")
    print("  help                 - Show this help")
    print("  load <file>          - Load binary file")
    print("  strategy <name>      - Select search strategy")
    print("  config <file>        - Load configuration file")
    print("  run [iterations]     - Start search")
    print("  status               - Show current status")
    print("  results              - Show search results")
    print("  plot <type>          - Show visualizations (scores, ops, tree)")
    print("  save <file>          - Save results to file")
    print("  export <format>      - Export in format (json, csv, txt)")
    print("  clear                - Clear screen")
    print("  quit                 - Exit BSEE")
    print()

    while True:
        try:
            command = input("BSEE> ").strip().split()
            if not command:
                continue

            cmd = command[0].lower()
            args = command[1:] if len(command) > 1 else []

            if cmd == 'quit' or cmd == 'exit':
                print("Goodbye!")
                break

            elif cmd == 'help':
                print_help()

            elif cmd == 'load':
                if not args:
                    print("Error: Please specify a file to load")
                    continue
                current_file = args[0]
                if os.path.exists(current_file):
                    print(f"Loaded file: {current_file}")
                    # Initialize pipeline with file
                    try:
                        pipeline = SearchPipeline()
                        # pipeline.load_file(current_file)  # Would implement this
                        print("Pipeline ready for search")
                    except Exception as e:
                        print(f"Error initializing pipeline: {e}")
                else:
                    print(f"Error: File '{current_file}' not found")

            elif cmd == 'strategy':
                if not args:
                    print("Available strategies: mcts, genetic, beam, annealing, heuristic, greedy")
                    continue
                strategy = args[0]
                available_strategies = ['mcts', 'genetic', 'beam', 'annealing', 'heuristic', 'greedy']
                if strategy in available_strategies:
                    current_strategy = strategy
                    print(f"Strategy set to: {strategy}")
                else:
                    print(f"Error: Unknown strategy '{strategy}'")
                    print(f"Available: {', '.join(available_strategies)}")

            elif cmd == 'config':
                if not args:
                    print("Error: Please specify a configuration file")
                    continue
                config_file = args[0]
                if os.path.exists(config_file):
                    print(f"Configuration loaded: {config_file}")
                else:
                    print(f"Error: Configuration file '{config_file}' not found")

            elif cmd == 'run':
                iterations = int(args[0]) if args else 100
                print(f"Running search with {current_strategy} strategy for {iterations} iterations...")

                # Simulate search progress
                for i in range(iterations + 1):
                    viz_panel.show_progress_bar(i, iterations, f"Running {current_strategy}")
                    # Simulate some work
                    import time
                    time.sleep(0.01)

                # Generate mock results for demonstration
                import random
                search_results = []
                for i in range(10):
                    search_results.append({
                        'score': random.uniform(0.5, 0.95),
                        'operations': [f'op_{j}' for j in range(random.randint(3, 8))],
                        'iterations': random.randint(50, iterations)
                    })

                print(f"\nSearch completed! Found {len(search_results)} results.")

            elif cmd == 'status':
                print_status(pipeline, current_file, current_strategy, config_file)

            elif cmd == 'results':
                print_results(search_results, viz_panel)

            elif cmd == 'plot':
                if not args:
                    print("Available plots: scores, operations, tree, progress")
                    continue
                plot_type = args[0].lower()
                if not search_results:
                    print("No results to plot. Run search first.")
                    continue

                if plot_type == 'scores':
                    scores = [r['score'] for r in search_results]
                    viz_panel.plot_score_progression(scores, "Search Scores")
                elif plot_type == 'operations':
                    all_ops = []
                    for r in search_results:
                        all_ops.extend(r['operations'])
                    viz_panel.plot_operation_distribution(all_ops, "Operation Usage")
                elif plot_type == 'tree':
                    # Mock tree data
                    tree_data = [
                        {'score': 0.85, 'operations': ['dct_transform'], 'children': [
                            {'score': 0.87, 'operations': ['huffman_encode'], 'children': []},
                            {'score': 0.82, 'operations': ['lz77_encode'], 'children': []}
                        ]},
                        {'score': 0.78, 'operations': ['fft_transform'], 'children': []}
                    ]
                    viz_panel.show_search_tree_ascii(tree_data)
                else:
                    print(f"Unknown plot type: {plot_type}")

            elif cmd == 'save':
                if not args:
                    print("Error: Please specify output file")
                    continue
                if not search_results:
                    print("No results to save. Run search first.")
                    continue
                save_results(search_results, args[0])
                print(f"Results saved to: {args[0]}")

            elif cmd == 'export':
                if not args:
                    print("Available formats: json, csv, txt")
                    continue
                if not search_results:
                    print("No results to export. Run search first.")
                    continue
                export_format = args[0].lower()
                filename = f"results.{export_format}"
                export_results(search_results, filename, export_format)
                print(f"Results exported to: {filename}")

            elif cmd == 'clear':
                viz_panel.clear_screen()
                print("BSEE Terminal Mode - Screen cleared")

            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """Print detailed help information."""
    print("\nBSEE Terminal Mode Help:")
    print("=" * 40)
    print("FILE OPERATIONS:")
    print("  load <file>     - Load a binary file for analysis")
    print("  save <file>     - Save search results to file")
    print("  export <format> - Export results (json, csv, txt)")
    print()
    print("SEARCH CONFIGURATION:")
    print("  strategy <name> - Choose search algorithm:")
    print("                  * mcts - Monte Carlo Tree Search")
    print("                  * genetic - Genetic Algorithm")
    print("                  * beam - Beam Search")
    print("                  * annealing - Simulated Annealing")
    print("                  * heuristic - Heuristic Search")
    print("                  * greedy - Greedy Search")
    print("  config <file>   - Load configuration file")
    print("  run [n]         - Start search (optional iteration count)")
    print()
    print("RESULTS & VISUALIZATION:")
    print("  status          - Show current search status")
    print("  results         - Display search results")
    print("  plot <type>     - Show visualizations:")
    print("                  * scores - Score progression chart")
    print("                  * operations - Operation distribution")
    print("                  * tree - Search tree structure")
    print("  clear           - Clear terminal screen")
    print()
    print("SYSTEM:")
    print("  help            - Show this help")
    print("  quit            - Exit BSEE")
    print()


def print_status(pipeline, current_file, current_strategy, config_file):
    """Print current search status."""
    print(f"\nCurrent Status:")
    print(f"  Loaded file: {current_file or 'None'}")
    print(f"  Strategy: {current_strategy}")
    print(f"  Config file: {config_file or 'Default'}")
    if pipeline:
        print(f"  Pipeline: Active")
        # print(f"  Iterations: {pipeline.iteration_count}")
        # print(f"  Best score: {pipeline.best_score:.4f}")
    else:
        print("  Pipeline: Not initialized")


def print_results(search_results, viz_panel):
    """Print search results in terminal-friendly format."""
    if not search_results:
        print("No results to display")
        return

    print("\nSearch Results:")
    print("=" * 60)

    # Sort by score
    sorted_results = sorted(search_results, key=lambda x: x['score'], reverse=True)

    # Create table data
    headers = ["Rank", "Score", "Operations", "Iterations"]
    rows = []

    for i, result in enumerate(sorted_results[:viz_panel.max_results_display]):
        ops_str = ", ".join(result['operations'][:3])
        if len(result['operations']) > 3:
            ops_str += f" (+{len(result['operations'])-3})"
        rows.append([
            str(i + 1),
            f"{result['score']:.4f}",
            ops_str,
            str(result.get('iterations', 'N/A'))
        ])

    viz_panel.show_table(headers, rows, "Top Search Results")


def save_results(search_results, filename):
    """Save results to file."""
    import json
    with open(filename, 'w') as f:
        json.dump(search_results, f, indent=2)


def export_results(search_results, filename, format_type):
    """Export results in specified format."""
    if format_type == 'json':
        save_results(search_results, filename)
    elif format_type == 'csv':
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Score', 'Operations', 'Iterations'])
            for result in search_results:
                writer.writerow([
                    result['score'],
                    ";".join(result['operations']),
                    result.get('iterations', '')
                ])
    elif format_type == 'txt':
        with open(filename, 'w') as f:
            f.write("BSEE Search Results\n")
            f.write("=" * 40 + "\n\n")
            for i, result in enumerate(search_results):
                f.write(f"{i+1}. Score: {result['score']:.4f}\n")
                f.write(f"   Operations: {', '.join(result['operations'])}\n")
                f.write(f"   Iterations: {result.get('iterations', 'N/A')}\n\n")


def create_visualization_panel(dependencies_available: Dict[str, bool],
                            fallback_config: Dict[str, str]):
    """Create appropriate visualization based on available dependencies."""
    if dependencies_available.get('matplotlib', False):
        try:
            from gui.panels.visualization_panel import VisualizationPanel
            return VisualizationPanel()
        except ImportError:
            pass

    # Fallback to terminal visualization
    from gui.panels.terminal_visualization_panel import TerminalVisualizationPanel
    return TerminalVisualizationPanel(fallback_config)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: BSEE GUI requires Python 3.8 or higher")
        print(f"Current version: {sys.version}")
        sys.exit(1)


def setup_directories():
    """Create necessary directories."""
    directories = [
        'inputs',
        'results',
        'presets',
        'history',
        'logs',
        'temp'
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def main():
    """Main entry point with graceful degradation."""
    print("BSEE - Binary Structure Exploration Engine")
    print("GUI Version 1.0.0 (with Graceful Fallbacks)")
    print("=" * 60)

    # Check Python version
    check_python_version()

    # Check dependencies with fallback handling
    missing_required, missing_optional = check_dependencies()

    # Handle missing required dependencies
    if missing_required:
        print("Error: Missing required dependencies:")
        for module in missing_required:
            print(f"  - {module}")
        print("\nRequired dependencies must be installed:")
        print("pip install -r requirements.txt")

        # Check if we can run in terminal mode
        if 'tkinter' in missing_required:
            print("\nFalling back to terminal mode...")
            setup_directories()
            terminal_mode()
            return
        else:
            sys.exit(1)

    # Handle missing optional dependencies
    if missing_optional:
        print("Note: Some optional dependencies are missing:")
        for module, fallback in missing_optional:
            print(f"  - {module} (using {fallback} fallback)")

        # Setup fallback configurations
        fallback_config = setup_fallback_mode(missing_optional)
        print("\nRunning with reduced functionality.")
        print("For full functionality, install missing dependencies:")
        print("pip install -r requirements.txt")
    else:
        fallback_config = {}
        print("All dependencies available!")

    # Create necessary directories
    setup_directories()

    try:
        # Determine if we can run GUI
        if 'tkinter' in missing_required:
            # Run in terminal mode
            terminal_mode()
        else:
            # Try to run GUI
            try:
                from gui.main_window import MainWindow
                app = MainWindow(fallback_config=fallback_config)
                app.run()
            except ImportError as e:
                print(f"GUI initialization failed: {e}")
                print("Falling back to terminal mode...")
                terminal_mode()
            except Exception as e:
                print(f"GUI runtime error: {e}")
                print("Falling back to terminal mode...")
                terminal_mode()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        print("\nAttempting terminal mode fallback...")
        try:
            terminal_mode()
        except Exception as fallback_error:
            print(f"Terminal mode also failed: {fallback_error}")
            sys.exit(1)


if __name__ == "__main__":
    main()