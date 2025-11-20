#!/usr/bin/env python3
"""
Error Detection Tool for BSEE Codebase
Dry-runs each Python file to detect import, syntax, and runtime errors
"""

import os
import sys
import ast
import importlib.util
import traceback
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class ErrorDetector:
    """Detects errors in Python files through dry-run analysis"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.errors = []
        self.python_files = []

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        self.python_files = python_files
        return python_files

    def check_syntax_error(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check for syntax errors by parsing AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse the AST
            ast.parse(content)
            return None

        except SyntaxError as e:
            return {
                'file_path': str(file_path.relative_to(self.project_root)),
                'error_type': 'SyntaxError',
                'error_message': f"Line {e.lineno}: {e.msg}",
                'full_traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
        except UnicodeDecodeError as e:
            return {
                'file_path': str(file_path.relative_to(self.project_root)),
                'error_type': 'UnicodeError',
                'error_message': f"Encoding error: {str(e)}",
                'full_traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }

    def check_import_error(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check for import errors by attempting to import the module"""
        try:
            # Create a temporary spec for the module
            spec = importlib.util.spec_from_file_location(
                file_path.stem, file_path
            )

            if spec is None:
                return {
                    'file_path': str(file_path.relative_to(self.project_root)),
                    'error_type': 'ImportError',
                    'error_message': 'Could not create module spec',
                    'full_traceback': '',
                    'timestamp': datetime.now().isoformat()
                }

            # Try to load the module without executing
            module = importlib.util.module_from_spec(spec)

            # Don't execute the module yet, just check if spec can be created
            return None

        except Exception as e:
            error_type = type(e).__name__
            return {
                'file_path': str(file_path.relative_to(self.project_root)),
                'error_type': error_type,
                'error_message': str(e),
                'full_traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }

    def check_runtime_errors(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check for runtime errors by attempting to execute the file in isolation"""
        runtime_errors = []

        try:
            # Create a temporary test script that imports the target file
            test_script = f'''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath("{file_path}")))

try:
    # Try to import the module
    import importlib.util
    spec = importlib.util.spec_from_file_location("test_module", "{file_path}")
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # If it has a main function, try to call it with basic args
        if hasattr(module, 'main') and callable(getattr(module, 'main')):
            # Test with help flag first to avoid actual execution
            import sys
            original_argv = sys.argv
            try:
                sys.argv = ['test', '--help']
                module.main()
            except SystemExit:
                # Expected for --help
                pass
            except Exception as e:
                raise type(e)(f"Main function error: {{e}}")
            finally:
                sys.argv = original_argv

except ImportError as e:
    raise ImportError(f"Import error: {{e}}")
except Exception as e:
    raise Exception(f"Runtime error: {{e}}")
'''

            # Write test script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(test_script)
                temp_file_path = temp_file.name

            try:
                # Run the test script
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=str(self.project_root)
                )

                if result.returncode != 0:
                    # Parse the error output
                    error_output = result.stderr

                    # Categorize the error
                    if 'ImportError' in error_output or 'ModuleNotFoundError' in error_output:
                        error_type = 'ImportError'
                    elif 'SyntaxError' in error_output:
                        error_type = 'SyntaxError'
                    elif 'RuntimeError' in error_output:
                        error_type = 'RuntimeError'
                    elif 'AttributeError' in error_output:
                        error_type = 'AttributeError'
                    elif 'TypeError' in error_output:
                        error_type = 'TypeError'
                    else:
                        error_type = 'ExecutionError'

                    runtime_errors.append({
                        'file_path': str(file_path.relative_to(self.project_root)),
                        'error_type': error_type,
                        'error_message': error_output.strip(),
                        'full_traceback': error_output,
                        'timestamp': datetime.now().isoformat()
                    })

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except subprocess.TimeoutExpired:
            runtime_errors.append({
                'file_path': str(file_path.relative_to(self.project_root)),
                'error_type': 'TimeoutError',
                'error_message': 'Script execution timed out after 30 seconds',
                'full_traceback': 'Execution timeout',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            runtime_errors.append({
                'file_path': str(file_path.relative_to(self.project_root)),
                'error_type': 'TestError',
                'error_message': f"Error testing file: {str(e)}",
                'full_traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })

        return runtime_errors

    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single file for all types of errors"""
        file_errors = []

        # Check syntax errors first
        syntax_error = self.check_syntax_error(file_path)
        if syntax_error:
            file_errors.append(syntax_error)
            return file_errors  # Don't check other errors if syntax is broken

        # Check import errors
        import_error = self.check_import_error(file_path)
        if import_error:
            file_errors.append(import_error)

        # Check runtime errors
        runtime_errors = self.check_runtime_errors(file_path)
        file_errors.extend(runtime_errors)

        return file_errors

    def analyze_project(self) -> List[Dict[str, Any]]:
        """Analyze all Python files in the project"""
        print(f"Analyzing project at: {self.project_root}")

        # Find all Python files
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files")

        all_errors = []
        analyzed_count = 0

        for file_path in python_files:
            analyzed_count += 1
            print(f"Analyzing {analyzed_count}/{len(python_files)}: {file_path.relative_to(self.project_root)}")

            try:
                file_errors = self.analyze_file(file_path)
                if file_errors:
                    all_errors.extend(file_errors)
                    print(f"  ❌ Found {len(file_errors)} error(s)")
                else:
                    print(f"  ✅ No errors found")
            except Exception as e:
                # Error in the analysis itself
                all_errors.append({
                    'file_path': str(file_path.relative_to(self.project_root)),
                    'error_type': 'AnalysisError',
                    'error_message': f"Error during analysis: {str(e)}",
                    'full_traceback': traceback.format_exc(),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"  ❌ Analysis error: {str(e)}")

        self.errors = all_errors
        print(f"\nAnalysis complete. Found {len(all_errors)} total errors across {len(python_files)} files.")

        return all_errors

    def get_error_summary(self) -> Dict[str, int]:
        """Get a summary of error types"""
        summary = {}
        for error in self.errors:
            error_type = error.get('error_type', 'Unknown')
            summary[error_type] = summary.get(error_type, 0) + 1
        return summary

    def export_errors(self) -> List[Dict[str, Any]]:
        """Export all detected errors"""
        return self.errors.copy()


def main():
    """Main function for standalone testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Detect errors in Python files")
    parser.add_argument("--project-root", default=".", help="Root directory of the project")
    parser.add_argument("--output", help="Output file for error results (JSON)")

    args = parser.parse_args()

    detector = ErrorDetector(args.project_root)
    errors = detector.analyze_project()

    # Print summary
    summary = detector.get_error_summary()
    print("\nError Summary:")
    for error_type, count in sorted(summary.items()):
        print(f"  {error_type}: {count}")

    # Save results if output file specified
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    return errors


if __name__ == "__main__":
    main()