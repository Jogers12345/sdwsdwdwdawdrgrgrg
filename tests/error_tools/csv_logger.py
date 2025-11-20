#!/usr/bin/env python3
"""
CSV Error Reporting Tool for BSEE Codebase
Generates CSV reports with file errors and fix status tracking
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class CSVLogger:
    """CSV logger for error reporting and fix tracking"""

    def __init__(self, project_root: str = ".", csv_path: str = "tests/error_report.csv"):
        self.project_root = Path(project_root).resolve()
        self.csv_path = Path(csv_path)
        self.fieldnames = [
            'file_path',
            'error_type',
            'error_message',
            'error_status',
            'fix_description',
            'timestamp',
            'fix_timestamp',
            'verified_by',
            'priority'
        ]

    def create_error_report(self, errors: List[Dict[str, Any]],
                          include_fixes: bool = True) -> Path:
        """Create a comprehensive CSV error report"""

        # Ensure directory exists
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare CSV rows
        csv_rows = []
        for error in errors:
            # Basic error information
            row = {
                'file_path': error.get('file_path', ''),
                'error_type': error.get('error_type', ''),
                'error_message': error.get('error_message', ''),
                'error_status': 'DETECTED',  # Initial status
                'fix_description': '',
                'timestamp': error.get('timestamp', datetime.now().isoformat()),
                'fix_timestamp': '',
                'verified_by': '',
                'priority': self._determine_priority(error.get('error_type', ''))
            }

            # Add fix suggestions
            if include_fixes:
                fix_suggestion = self._suggest_fix(error)
                row['fix_description'] = fix_suggestion

            csv_rows.append(row)

        # Write CSV file
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"CSV error report created: {self.csv_path}")
        print(f"Report contains {len(csv_rows)} errors")

        return self.csv_path

    def _determine_priority(self, error_type: str) -> str:
        """Determine priority level based on error type"""
        high_priority = ['SyntaxError', 'ImportError', 'ModuleNotFoundError']
        medium_priority = ['AttributeError', 'TypeError', 'RuntimeError']
        low_priority = ['Warning', 'DeprecationWarning']

        if error_type in high_priority:
            return 'HIGH'
        elif error_type in medium_priority:
            return 'MEDIUM'
        elif error_type in low_priority:
            return 'LOW'
        else:
            return 'MEDIUM'

    def _suggest_fix(self, error: Dict[str, Any]) -> str:
        """Suggest fixes for common error types"""
        error_type = error.get('error_type', '')
        error_message = error.get('error_message', '')
        file_path = error.get('file_path', '')

        # Common fix suggestions based on error type
        fix_suggestions = {
            'ImportError': 'Check if required module is installed and accessible in Python path',
            'ModuleNotFoundError': 'Install missing module: pip install <module_name>',
            'SyntaxError': 'Fix syntax error in the code (check brackets, indentation, etc.)',
            'AttributeError': 'Check if attribute/method exists on the object',
            'TypeError': 'Verify data types match expected types',
            'RuntimeError': 'Debug runtime logic and check input data',
            'UnicodeError': 'Check file encoding and special characters',
            'TimeoutError': 'Optimize code or increase timeout limit',
            'ExecutionError': 'Review code logic and dependencies'
        }

        base_suggestion = fix_suggestions.get(error_type, 'Review error details and debug the issue')

        # Specific suggestions based on error message content
        if 'No module named' in error_message:
            module_name = self._extract_module_name(error_message)
            if module_name:
                return f"Install missing module: pip install {module_name}"

        elif 'bsee' in error_message.lower() and 'import' in error_message.lower():
            return "Add bsee module to Python path or check project structure"

        elif 'tkinter' in error_message.lower():
            return "Install tkinter package (usually included with Python, check Python installation)"

        elif 'numpy' in error_message.lower():
            return "Install numpy: pip install numpy"

        elif 'yaml' in error_message.lower() or 'pyyaml' in error_message.lower():
            return "Install PyYAML: pip install pyyaml"

        elif 'matplotlib' in error_message.lower():
            return "Install matplotlib: pip install matplotlib"

        elif 'scipy' in error_message.lower():
            return "Install scipy: pip install scipy"

        elif 'pandas' in error_message.lower():
            return "Install pandas: pip install pandas"

        elif 'torch' in error_message.lower():
            return "Install PyTorch: pip install torch torchvision"

        elif 'tensorflow' in error_message.lower():
            return "Install TensorFlow: pip install tensorflow"

        elif 'git' in error_message.lower():
            return "Install Git and ensure it's in system PATH"

        elif 'python' in error_message.lower() and ('not found' in error_message.lower() or 'command' in error_message.lower()):
            return "Ensure Python is installed and in system PATH"

        return base_suggestion

    def _extract_module_name(self, error_message: str) -> Optional[str]:
        """Extract module name from error message"""
        import re

        # Pattern to match "No module named 'module_name'"
        match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_message)
        if match:
            return match.group(1)

        return None

    def update_error_status(self, file_path: str, error_type: str,
                          new_status: str, fix_description: str = '',
                          verified_by: str = '') -> bool:
        """Update the status of an existing error in the CSV"""
        if not self.csv_path.exists():
            print(f"CSV file not found: {self.csv_path}")
            return False

        # Read existing rows
        rows = []
        updated = False

        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            for row in reader:
                if (row['file_path'] == file_path and
                    row['error_type'] == error_type and
                    row['error_status'] != 'FIXED'):

                    row['error_status'] = new_status
                    row['fix_timestamp'] = datetime.now().isoformat()
                    if fix_description:
                        row['fix_description'] = fix_description
                    if verified_by:
                        row['verified_by'] = verified_by
                    updated = True

                rows.append(row)

        if updated:
            # Write back to CSV
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"Updated error status for {file_path}: {error_type} -> {new_status}")
            return True
        else:
            print(f"No matching error found for {file_path}: {error_type}")
            return False

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics from the CSV report"""
        if not self.csv_path.exists():
            return {"error": "CSV file not found"}

        stats = {
            'total_errors': 0,
            'by_status': {},
            'by_type': {},
            'by_priority': {},
            'by_file': {}
        }

        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                stats['total_errors'] += 1

                # Count by status
                status = row.get('error_status', 'UNKNOWN')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

                # Count by type
                error_type = row.get('error_type', 'UNKNOWN')
                stats['by_type'][error_type] = stats['by_type'].get(error_type, 0) + 1

                # Count by priority
                priority = row.get('priority', 'MEDIUM')
                stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1

                # Count by file
                file_path = row.get('file_path', 'UNKNOWN')
                if file_path not in stats['by_file']:
                    stats['by_file'][file_path] = 0
                stats['by_file'][file_path] += 1

        return stats

    def generate_summary_report(self) -> str:
        """Generate a text summary of the error report"""
        stats = self.get_error_statistics()

        if 'error' in stats:
            return f"Error generating summary: {stats['error']}"

        summary = []
        summary.append("=" * 60)
        summary.append("BSEE Error Detection Summary Report")
        summary.append("=" * 60)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Total Errors: {stats['total_errors']}")
        summary.append("")

        # Status breakdown
        summary.append("Error Status Breakdown:")
        for status, count in sorted(stats['by_status'].items()):
            percentage = (count / stats['total_errors']) * 100
            summary.append(f"  {status:15} : {count:4} ({percentage:5.1f}%)")
        summary.append("")

        # Type breakdown
        summary.append("Error Type Breakdown:")
        for error_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_errors']) * 100
            summary.append(f"  {error_type:20} : {count:4} ({percentage:5.1f}%)")
        summary.append("")

        # Priority breakdown
        summary.append("Priority Breakdown:")
        for priority, count in sorted(stats['by_priority'].items()):
            percentage = (count / stats['total_errors']) * 100
            summary.append(f"  {priority:10} : {count:4} ({percentage:5.1f}%)")
        summary.append("")

        # Files with most errors
        summary.append("Files with Most Errors:")
        sorted_files = sorted(stats['by_file'].items(), key=lambda x: x[1], reverse=True)[:10]
        for file_path, count in sorted_files:
            summary.append(f"  {file_path:40} : {count}")
        summary.append("")

        return "\n".join(summary)

    def export_filtered_report(self, output_path: str,
                             status_filter: Optional[str] = None,
                             type_filter: Optional[str] = None,
                             priority_filter: Optional[str] = None) -> Path:
        """Export a filtered version of the error report"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        filtered_rows = []

        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Apply filters
                if status_filter and row.get('error_status') != status_filter:
                    continue
                if type_filter and row.get('error_type') != type_filter:
                    continue
                if priority_filter and row.get('priority') != priority_filter:
                    continue

                filtered_rows.append(row)

        # Write filtered report
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path_obj, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(filtered_rows)

        print(f"Filtered report exported to: {output_path_obj}")
        print(f"Contains {len(filtered_rows)} errors")

        return output_path_obj


def main():
    """Main function for standalone testing"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate CSV error reports")
    parser.add_argument("--project-root", default=".", help="Root directory of the project")
    parser.add_argument("--csv-path", default="tests/error_report.csv", help="Path for CSV output")
    parser.add_argument("--input-json", help="Input JSON file with errors")
    parser.add_argument("--statistics", action="store_true", help="Show error statistics")
    parser.add_argument("--summary", action="store_true", help="Generate text summary")
    parser.add_argument("--filter-status", help="Filter by status (DETECTED, FIXED, etc.)")
    parser.add_argument("--filter-type", help="Filter by error type")
    parser.add_argument("--filter-priority", help="Filter by priority")
    parser.add_argument("--export-filtered", help="Export filtered report to this path")

    args = parser.parse_args()

    logger = CSVLogger(args.project_root, args.csv_path)

    # Load errors from JSON if provided
    errors = []
    if args.input_json:
        with open(args.input_json, 'r') as f:
            errors = json.load(f)

    if errors:
        logger.create_error_report(errors)

    # Show statistics if requested
    if args.statistics:
        stats = logger.get_error_statistics()
        print("Error Statistics:")
        print(json.dumps(stats, indent=2))

    # Generate summary if requested
    if args.summary:
        summary = logger.generate_summary_report()
        print(summary)

    # Export filtered report if requested
    if args.export_filtered:
        logger.export_filtered_report(
            args.export_filtered,
            status_filter=args.filter_status,
            type_filter=args.filter_type,
            priority_filter=args.filter_priority
        )


if __name__ == "__main__":
    main()