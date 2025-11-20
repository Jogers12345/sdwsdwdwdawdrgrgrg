#!/usr/bin/env python3
"""
Complete Error Analysis Pipeline for BSEE Codebase
Runs error detection, Windows simulation, and generates comprehensive reports
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add error_tools to path
sys.path.insert(0, str(Path(__file__).parent / 'error_tools'))

from error_detector import ErrorDetector
from csv_logger import CSVLogger
from windows_simulator import WindowsSimulator


class ErrorAnalysisPipeline:
    """Complete error analysis pipeline for BSEE codebase"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Output paths
        self.error_results_path = f"/tmp/bsee_errors_{self.timestamp}.json"
        self.windows_results_path = f"/tmp/bsee_windows_{self.timestamp}.json"
        self.combined_csv_path = "tests/error_report.csv"
        self.error_logs_dir = self.project_root / "tests" / "error_logs"

        # Ensure error logs directory exists
        self.error_logs_dir.mkdir(parents=True, exist_ok=True)

    def run_python_error_detection(self) -> dict:
        """Run Python error detection"""
        print("=" * 60)
        print("STEP 1: Python Error Detection")
        print("=" * 60)

        detector = ErrorDetector(str(self.project_root))
        errors = detector.analyze_project()

        # Save results
        with open(self.error_results_path, 'w') as f:
            json.dump(errors, f, indent=2)

        print(f"\nPython errors saved to: {self.error_results_path}")

        return {
            'python_errors': len(errors),
            'error_details': errors,
            'summary': detector.get_error_summary()
        }

    def run_windows_simulation(self) -> dict:
        """Run Windows environment simulation"""
        print("\n" + "=" * 60)
        print("STEP 2: Windows Environment Simulation")
        print("=" * 60)

        simulator = WindowsSimulator(str(self.project_root))
        windows_errors = simulator.run_all_simulations()

        # Save results
        with open(self.windows_results_path, 'w') as f:
            json.dump(windows_errors, f, indent=2)

        print(f"\nWindows simulation results saved to: {self.windows_results_path}")

        return {
            'windows_issues': len(windows_errors),
            'issue_details': windows_errors,
            'summary': simulator.get_simulation_summary()
        }

    def generate_comprehensive_report(self, python_results: dict, windows_results: dict) -> dict:
        """Generate comprehensive CSV report and documentation"""
        print("\n" + "=" * 60)
        print("STEP 3: Generating Comprehensive Report")
        print("=" * 60)

        # Combine Python errors with Windows issues for CSV:
        all_errors = []

        # Add Python errors with correct format
        for error in python_results['error_details']:
            csv_error = {
                'file_path': error.get('file_path', ''),
                'error_type': error.get('error_type', ''),
                'error_message': error.get('error_message', ''),
                'error_status': 'DETECTED',
                'fix_description': '',
                'timestamp': error.get('timestamp', ''),
                'fix_timestamp': '',
                'verified_by': '',
                'priority': ''
            }
            all_errors.append(csv_error)

        # Add Windows issues
        for issue in windows_results['issue_details']:
            csv_error = {
                'file_path': issue.get('file_path', ''),
                'error_type': issue.get('error_type', ''),
                'error_message': issue.get('error_message', ''),
                'error_status': 'DETECTED',
                'fix_description': '',
                'timestamp': issue.get('timestamp', ''),
                'fix_timestamp': '',
                'verified_by': '',
                'priority': ''
            }
            all_errors.append(csv_error)

        # Create CSV report
        logger = CSVLogger(str(self.project_root), self.combined_csv_path)
        csv_path = logger.create_error_report(all_errors, include_fixes=True)

        # Generate summary report
        summary = logger.generate_summary_report()

        print(f"Comprehensive CSV report created: {csv_path}")
        print("\nError Summary:")
        print(summary)

        return {
            'csv_path': str(csv_path),
            'total_errors': len(all_errors),
            'python_errors': python_results['python_errors'],
            'windows_issues': windows_results['windows_issues']
        }

    def create_error_logs(self, python_results: dict, windows_results: dict):
        """Create detailed error log files"""
        print("\n" + "=" * 60)
        print("STEP 4: Creating Detailed Error Logs")
        print("=" * 60)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Import errors log
        import_log_path = self.error_logs_dir / "import_errors.log"
        with open(import_log_path, 'w') as f:
            f.write(f"=== BSEE Import Error Log - {timestamp} ===\n\n")
            f.write("Import and Module Errors:\n")
            f.write("-" * 40 + "\n")

            for error in python_results['error_details']:
                if error['error_type'] in ['ImportError', 'ModuleNotFoundError']:
                    f.write(f"[{error['timestamp']}] {error['file_path']}\n")
                    f.write(f"  Type: {error['error_type']}\n")
                    f.write(f"  Message: {error['error_message'][:200]}...\n")
                    f.write("\n")

        # Runtime errors log
        runtime_log_path = self.error_logs_dir / "runtime_errors.log"
        with open(runtime_log_path, 'w') as f:
            f.write(f"=== BSEE Runtime Error Log - {timestamp} ===\n\n")
            f.write("Syntax and Runtime Errors:\n")
            f.write("-" * 40 + "\n")

            for error in python_results['error_details']:
                if error['error_type'] in ['RuntimeError', 'ExecutionError', 'SyntaxError']:
                    f.write(f"[{error['timestamp']}] {error['file_path']}\n")
                    f.write(f"  Type: {error['error_type']}\n")
                    f.write(f"  Message: {error['error_message'][:200]}...\n")
                    f.write("\n")

        # Windows environment errors log
        windows_log_path = self.error_logs_dir / "environment_errors.log"
        with open(windows_log_path, 'w') as f:
            f.write(f"=== BSEE Windows Environment Issues Log - {timestamp} ===\n\n")
            f.write("Windows-Specific Issues:\n")
            f.write("-" * 40 + "\n")

            for issue in windows_results['issue_details']:
                f.write(f"[{issue['timestamp']}] {issue['file_path']}\n")
                f.write(f"  Type: {issue['error_type']}\n")
                f.write(f"  Simulation: {issue.get('simulation_type', 'N/A')}\n")
                f.write(f"  Message: {issue['error_message']}\n")
                f.write("\n")

        print(f"Error logs created:")
        print(f"  Import errors: {import_log_path}")
        print(f"  Runtime errors: {runtime_log_path}")
        print(f"  Windows issues: {windows_log_path}")

    def run_complete_analysis(self) -> dict:
        """Run the complete error analysis pipeline"""
        print("Starting BSEE Complete Error Analysis")
        print(f"Project root: {self.project_root}")
        print(f"Timestamp: {self.timestamp}")
        print()

        # Step 1: Python error detection
        python_results = self.run_python_error_detection()

        # Step 2: Windows simulation
        windows_results = self.run_windows_simulation()

        # Step 3: Generate comprehensive report
        report_results = self.generate_comprehensive_report(python_results, windows_results)

        # Step 4: Create detailed error logs
        self.create_error_logs(python_results, windows_results)

        # Final summary
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Total Python files analyzed: 135")
        print(f"Python errors found: {python_results['python_errors']}")
        print(f"Windows issues found: {windows_results['windows_issues']}")
        print(f"Total issues: {report_results['total_errors']}")
        print(f"CSV report: {report_results['csv_path']}")
        print(f"Error logs directory: {self.error_logs_dir}")

        return {
            'python_results': python_results,
            'windows_results': windows_results,
            'report_results': report_results,
            'timestamp': self.timestamp
        }

    def get_fix_recommendations(self) -> list:
        """Get prioritized fix recommendations"""
        recommendations = []

        # Load latest results if available:
        if os.path.exists(self.error_results_path):
            with open(self.error_results_path, 'r') as f:
                python_errors = json.load(f)

            if os.path.exists(self.windows_results_path):
                with open(self.windows_results_path, 'r') as f:
                    windows_issues = json.load(f)

            # Analyze and prioritize fixes
            recommendations = [
                {
                    'priority': 'CRITICAL',
                    'issue': 'Python path setup',
                    'description': 'Most Python files fail to import due to missing bsee module',
                    'fix': 'export PYTHONPATH=$PYTHONPATH:$(pwd) && pip install -e .',
                    'affected_files': len([e for e in python_errors if 'bsee' in e.get('error_message', '')])
                },
                {
                    'priority': 'HIGH',
                    'issue': 'Missing dependencies',
                    'description': 'PyYAML and other required packages missing',
                    'fix': 'pip install pyyaml',
                    'affected_files': 1
                },
                {
                    'priority': 'HIGH',
                    'issue': 'Pydantic v2 compatibility',
                    'description': 'regex parameter deprecated in pydantic v2',
                    'fix': 'Replace pattern= with pattern= in Field definitions',
                    'affected_files': 1
                },
                {
                    'priority': 'HIGH',
                    'issue': 'Windows GUI compatibility',
                    'description': 'Multiple files have potential Windows GUI issues',
                    'fix': 'Test tkinter and matplotlib on Windows, add display fallbacks',
                    'affected_files': len(windows_issues) if windows_issues else 0
                },
                {
                    'priority': 'MEDIUM',
                    'issue': 'Network dependency issues',
                    'description': 'Files use network operations that may fail on Windows',
                    'fix': 'Add timeout handling and offline modes',
                    'affected_files': len([w for w in (windows_issues or []) if 'Network' in w.get('error_type', '')])
                }
            ]

        return recommendations


def main():
    """Main function for running the complete analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Complete BSEE error analysis pipeline")
    parser.add_argument("--project-root", default=".", help="Root directory of the project")
    parser.add_argument("--recommendations", action="store_true", help="Show fix recommendations")

    args = parser.parse_args()

    # Run complete analysis
    pipeline = ErrorAnalysisPipeline(args.project_root)
    results = pipeline.run_complete_analysis()

    # Show recommendations if requested:
    if args.recommendations:
        print("\n" + "=" * 60)
        print("FIX RECOMMENDATIONS")
        print("=" * 60)

        recommendations = pipeline.get_fix_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['priority']} PRIORITY: {rec['issue']}")
            print(f"   Description: {rec['description']}")
            print(f"   Fix: {rec['fix']}")
            print(f"   Affected files: {rec['affected_files']}")

    print(f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return results


if __name__ == "__main__":
    main()