#!/usr/bin/env python3
"""
Error Fix Progress Tracker for BSEE Codebase
Tracks fixes applied and updates CSV with resolution status
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add error_tools to path
sys.path.insert(0, str(Path(__file__).parent / 'error_tools'))

from csv_logger import CSVLogger


class FixProgressTracker:
    """Tracks and manages error fix progress"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.csv_path = self.project_root / "tests" / "error_report.csv"
        self.progress_log = self.project_root / "tests" / "error_logs" / "fix_progress.log"

        # Ensure error logs directory exists
        self.progress_log.parent.mkdir(parents=True, exist_ok=True)

        self.logger = CSVLogger(str(self.project_root), str(self.csv_path))
        self.fix_history = []

    def log_fix_attempt(self, file_path: str, error_type: str,
                       action: str, result: str, details: str = ""):
        """Log a fix attempt to the progress log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"[{timestamp}] {file_path}:{error_type}\n"
        log_entry += f"  Action: {action}\n"
        log_entry += f"  Result: {result}\n"
        log_entry += f"  Details: {details}\n"
        log_entry += "-" * 60 + "\n"

        with open(self.progress_log, 'a') as f:
            f.write(log_entry)

        # Store in fix history
        self.fix_history.append({
            'timestamp': timestamp,
            'file_path': file_path,
            'error_type': error_type,
            'action': action,
            'result': result,
            'details': details
        })

    def mark_error_fixed(self, file_path: str, error_type: str,
                       fix_description: str, verified_by: str = "auto") -> bool:
        """Mark an error as fixed in the CSV"""
        success = self.logger.update_error_status(
            file_path=file_path,
            error_type=error_type,
            new_status="FIXED",
            fix_description=fix_description,
            verified_by=verified_by
        )

        if success:
            self.log_fix_attempt(file_path, error_type,
                               "Marked as FIXED", "Success", fix_description)

        return success

    def mark_error_verified(self, file_path: str, error_type: str) -> bool:
        """Mark an error as verified/fixed"""
        return self.logger.update_error_status(
            file_path=file_path,
            error_type=error_type,
            new_status="VERIFIED",
            verified_by="verification_test"
        )

    def get_fix_statistics(self) -> Dict[str, Any]:
        """Get current fix statistics"""
        stats = self.logger.get_error_statistics()

        if 'error' in stats:
            return stats

        return {
            'total_errors': stats.get('total_errors', 0),
            'fixed': stats.get('by_status', {}).get('FIXED', 0),
            'detected': stats.get('by_status', {}).get('DETECTED', 0),
            'verified': stats.get('by_status', {}).get('VERIFIED', 0),
            'fix_percentage': 0
        }

    def generate_fix_report(self) -> str:
        """Generate a comprehensive fix progress report"""
        stats = self.get_fix_statistics()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = []
        report.append("=" * 60)
        report.append("BSEE Error Fix Progress Report")
        report.append("=" * 60)
        report.append(f"Generated: {timestamp}")
        report.append("")

        if stats.get('total_errors', 0) > 0:
            total = stats['total_errors']
            fixed = stats.get('fixed', 0)
            verified = stats.get('verified', 0)
            detected = stats.get('detected', 0)

            fix_percentage = ((fixed + verified) / total) * 100 if total > 0 else 0

            report.append("Fix Status Summary:")
            report.append(f"  Total Errors:     {total:4}")
            report.append(f"  Fixed:           {fixed:4} ({(fixed/total)*100:5.1f}%)")
            report.append(f"  Verified:        {verified:4} ({(verified/total)*100:5.1f}%)")
            report.append(f"  Still Detected:  {detected:4} ({(detected/total)*100:5.1f}%)")
            report.append(f"  Overall Progress: {fix_percentage:5.1f}%")
            report.append("")

        # Show recent fix history
        if self.fix_history:
            report.append("Recent Fix History:")
            report.append("-" * 40)
            for fix in self.fix_history[-10:]:  # Last 10 fixes
                report.append(f"{fix['timestamp']} - {fix['file_path']}")
                report.append(f"  {fix['action']}: {fix['result']}")
            report.append("")

        # Priority breakdown
        if 'by_priority' in stats:
            report.append("Priority Breakdown:")
            report.append("-" * 20)
            for priority, count in sorted(stats['by_priority'].items()):
                report.append(f"  {priority}: {count}")
            report.append("")

        return "\n".join(report)

    def create_checklist(self) -> List[Dict[str, Any]]:
        """Create a checklist of errors to fix"""
        if not self.csv_path.exists():
            return []

        checklist = []
        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row['error_status'] in ['DETECTED']:
                    checklist.append({
                        'file_path': row['file_path'],
                        'error_type': row['error_type'],
                        'error_message': row['error_message'][:100] + "...",
                        'priority': row['priority'],
                        'fix_description': row['fix_description']
                    })

        # Sort by priority (HIGH first)
        priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        checklist.sort(key=lambda x: priority_order.get(x['priority'], 4))

        return checklist

    def print_checklist(self):
        """Print the current fix checklist"""
        checklist = self.create_checklist()

        print("\n" + "=" * 60)
        print("ERROR FIX CHECKLIST")
        print("=" * 60)

        if not checklist:
            print("✅ No errors detected! All issues have been resolved.")
            return

        priority_counts = {}
        for item in checklist:
            priority = item['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        print(f"Total errors to fix: {len(checklist)}")
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            count = priority_counts.get(priority, 0)
            if count > 0:
                print(f"  {priority} priority: {count}")
        print()

        for i, item in enumerate(checklist, 1):
            status_icon = "🔴" if item['priority'] == 'HIGH' else "🟡" if item['priority'] == 'MEDIUM' else "🟢"
            print(f"{i:3}. {status_icon} {item['file_path']}")
            print(f"     Type: {item['error_type']}")
            print(f"     Priority: {item['priority']}")
            print(f"     Suggested Fix: {item['fix_description']}")
            print()


def main():
    """Main function for tracking fix progress"""
    import argparse

    parser = argparse.ArgumentParser(description="Track error fix progress")
    parser.add_argument("--project-root", default=".", help="Root directory of the project")
    parser.add_argument("--checklist", action="store_true", help="Show fix checklist")
    parser.add_argument("--report", action="store_true", help="Show progress report")
    parser.add_argument("--mark-fixed", nargs=3, metavar=("FILE", "TYPE", "DESCRIPTION"),
                       help="Mark an error as fixed")
    parser.add_argument("--mark-verified", nargs=2, metavar=("FILE", "TYPE"),
                       help="Mark an error as verified")

    args = parser.parse_args()

    tracker = FixProgressTracker(args.project_root)

    if args.checklist:
        tracker.print_checklist()

    if args.report:
        print(tracker.generate_fix_report())

    if args.mark_fixed:
        file_path, error_type, description = args.mark_fixed
        success = tracker.mark_error_fixed(file_path, error_type, description)
        if success:
            print(f"✅ Marked as FIXED: {file_path}:{error_type}")
        else:
            print(f"❌ Failed to mark as FIXED: {file_path}:{error_type}")

    if args.mark_verified:
        file_path, error_type = args.mark_verified
        success = tracker.mark_error_verified(file_path, error_type)
        if success:
            print(f"✅ Marked as VERIFIED: {file_path}:{error_type}")
        else:
            print(f"❌ Failed to mark as VERIFIED: {file_path}:{error_type}")

    # Show current stats if no specific action
    if not any([args.checklist, args.report, args.mark_fixed, args.mark_verified]):
        stats = tracker.get_fix_statistics()
        print("Current Fix Status:")
        print(f"  Total: {stats.get('total_errors', 0)}")
        print(f"  Fixed: {stats.get('fixed', 0)}")
        print(f"  Detected: {stats.get('detected', 0)}")
        print(f"  Use --checklist to see remaining issues")


if __name__ == "__main__":
    main()