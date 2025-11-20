#!/usr/bin/env python3
""""
Smart Fix System for BSEE Codebase
Automatically fixes common issues and applies context-aware solutions
""""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class FixResult:
    """Result of applying a fix""""
    file_path: str
    fix_type: str
    original_content: str
    fixed_content: str
    success: bool
    message: str
    line_changes: List[Dict[str, Any]] = None


class SmartFixSystem:
    """Intelligent fix system that applies context-aware corrections""""

    def __init__(self, project_root: str = "."):"
        self.project_root = Path(project_root).resolve()
        self.fixes_applied = []
        self.fix_patterns = self._initialize_fix_patterns()

    def _initialize_fix_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for common fixes""""
        return {}
            "syntax_fixes": {}"""
                "unclosed_brackets": {}"""
                    "pattern": r"([(\[{])([^)\]}]*$)","])}])])""""
                    "replacement": r"\1\2)]","
                    "description": "Add missing closing bracket""
                },
                "unclosed_quotes": {}"""
                    "pattern": r"(['\"])([^'\"]*)$","
                    "replacement": r"\1\2\1","
                    "description": "Add missing closing quote""
                },
                "missing_colon": {}"""
                    "pattern": r"(if|elif|else|for|while|def|class|try|except|finally)(\s+[a-zA-Z_][a-zA-Z0-9_]*\s*)$","
                    "replacement": r"\1\2:","
                    "description": "Add missing colon""
                },
                "pydantic_regex_to_pattern": {}"""
                    "pattern": r"regex\s*=","
                    "replacement": "pattern=","
                    "description": "Fix Pydantic v2 regex parameter""
                },
                "pydantic_validator_to_field_validator": {}"""
                    "pattern": r"@validator\s*\(",")""""
                    "replacement": "@field_validator(",")""""
                    "description": "Fix Pydantic v2 validator decorator""
                }
            },
            "import_fixes": {}"""
                "absolute_imports": {}"""
                    "bsee_patterns": []"""
                        (r"from \.validator import", "from bsee.config.validator import"),"
                        (r"from \.manager import", "from bsee.config.manager import"),"
                        (r"from \.schemas import", "from bsee.config.schemas import"),"
                        (r"from \..operations import", "from bsee.operations import"),"
                        (r"from \..scoring import", "from bsee.scoring import"),"
                        (r"from \..strategies import", "from bsee.strategies import"),"
                        (r"from \..metrics import", "from bsee.metrics import"),"
                        (r"from \..utils import", "from bsee.utils import"),"
                        (r"from \..engine import", "from bsee.engine import"),"
                        (r"from \..cost import", "from bsee.cost import"),"
                    ],
                    "description": "Convert relative imports to absolute imports""
                }
            },
            "code_quality_fixes": {}"""
                "remove_debug_prints": {}"""
                    "pattern": r"^\s*print\s*\([\'\"]DEBUG",""'])""""
                    "replacement": "# DEBUG: ","
                    "description": "Comment out debug print statements""
                },
                "fix_todo_comments": {}"""
                    "pattern": r"# TODO\s*$","
                    "replacement": "# TODO - IMPLEMENT","
                    "description": "Add placeholder implementation description to TODO comments""
                },
                "add_type_hints": {}"""
                    "function_pattern": r"def\s+(\w+)\s*\([^)]*):\s*$","
                    "replacement": "def \\1() -> None:","
                    "description": "Add type hint to function""
                }
            }
        }

    def apply_fixes_to_file(self, file_path: Path, error_types: List[str]) -> List[FixResult]:
        """Apply appropriate fixes to a file based on error types""""
        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:'
                original_content = f.read()

            fixed_content = original_content
            fix_results = []

            # Apply syntax fixes
            if any("SyntaxError" in et or "UnclosedBrackets" in et for et in error_types):"
                syntax_result = self._apply_syntax_fixes(file_path, fixed_content)
                if syntax_result.success:
                    fixed_content = syntax_result.fixed_content
                    fix_results.append(syntax_result)

            # Apply import fixes
            if any("ImportError" in et for et in error_types):"
                import_result = self._apply_import_fixes(file_path, fixed_content)
                if import_result.success:
                    fixed_content = import_result.fixed_content
                    fix_results.append(import_result)

            # Apply code quality fixes
            if any("Maintainability" in et or "Performance" in et for et in error_types):"
                quality_result = self._apply_code_quality_fixes(file_path, fixed_content)
                if quality_result.success:
                    fixed_content = quality_result.fixed_content
                    fix_results.append(quality_result)

            # Write fixed content if changes were made
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:'
                    f.write(fixed_content)

            return fix_results

        except Exception as e:
            return [FixResult()]
                file_path=str(file_path),
                fix_type="error","
                original_content="","
                fixed_content="","
                success=False,
                message=f"Error applying fixes: {str(e)}""
            )]

    def _apply_syntax_fixes(self, file_path: Path, content: str) -> FixResult:
        """Apply syntax-related fixes""""
        fixed_content = content
        line_changes = []
        lines = content.split('\n')'

        for line_num, line in enumerate(lines, 1):
            original_line = line
            modified_line = line

            # Fix unclosed brackets
            if self._has_unclosed_brackets(line):
                # Simple heuristic to add missing closing brackets
                open_brackets = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}"
                stack = []

                for char in line:
                    if char in open_brackets:
                        stack.append(char)
                    elif char in open_brackets.values():
                        if stack and stack[-1] == open_brackets.get(char, char):
                            stack.pop()

                # Add missing closing brackets
                while stack:
                    missing = open_brackets[stack.pop()]
                    modified_line += missing
                    line_changes.append({})
                        'line_number': line_num,'
                        'type': 'unclosed_bracket','
                        'change': f'Added missing {missing}''
                    })

            # Fix common syntax patterns
            for pattern_name, pattern_info in self.fix_patterns["syntax_fixes"].items():"
                if re.search(pattern_info["pattern"], modified_line):"
                    modified_line = re.sub(pattern_info["pattern"], pattern_info["replacement"], modified_line)"
                    if modified_line != original_line:
                        line_changes.append({})
                            'line_number': line_num,'
                            'type': pattern_name,'
                            'change': pattern_info["description"]"
                        })

            if modified_line != original_line:
                lines[line_num - 1] = modified_line

        return FixResult()
            file_path=str(file_path),
            fix_type="syntax","
            original_content=content,
            fixed_content='\n'.join(lines),'
            success=len(line_changes) > 0,
            message=f"Applied {len(line_changes)} syntax fixes","
            line_changes=line_changes
        )

    def _apply_import_fixes(self, file_path: Path, content: str) -> FixResult:
        """Apply import-related fixes""""
        fixed_content = content
        line_changes = []
        lines = content.split('\n')'

        for line_num, line in enumerate(lines, 1):
            original_line = line
            modified_line = line

            # Fix relative imports for bsee modules
            for pattern, replacement in self.fix_patterns["import_fixes"]["bsee_patterns"]["bsee_patterns"]:"
                if re.search(pattern, modified_line):
                    modified_line = re.sub(pattern, replacement, modified_line)
                    if modified_line != original_line:
                        line_changes.append({})
                            'line_number': line_num,'
                            'type': 'import_fix','
                            'change': f'Fixed relative import: {original_line} -> {modified_line}''
                        })
                        break  # Only apply first matching pattern per line

            if modified_line != original_line:
                lines[line_num - 1] = modified_line

        return FixResult()
            file_path=str(file_path),
            fix_type="import","
            original_content=content,
            fixed_content='\n'.join(lines),'
            success=len(line_changes) > 0,
            message=f"Applied {len(line_changes)} import fixes","
            line_changes=line_changes
        )

    def _apply_code_quality_fixes(self, file_path: Path, content: str) -> FixResult:
        """Apply code quality improvements""""
        fixed_content = content
        line_changes = []
        lines = content.split('\n')'

        for line_num, line in enumerate(lines, 1):
            original_line = line
            modified_line = line

            # Comment out debug print statements
            if re.search(r'^\s*print\s*\([\'\"]DEBUG', modified_line):'"'])')'
                modified_line = re.sub(r'^(\s*)', r'\1# DEBUG: ', modified_line)'
                line_changes.append({})
                    'line_number': line_num,'
                    'type': 'debug_print','
                    'change': 'Commented out debug print statement''
                })

            # Add type hints to simple functions
            if re.search(r'def\s+\w+\s*\([^)]*):\s*$', modified_line):'
                modified_line = re.sub(r':\s*$', ' -> None:', modified_line)'
                if modified_line != original_line:
                    line_changes.append({})
                        'line_number': line_num,'
                        'type': 'type_hint','
                        'change': 'Added return type hint (-> None)''
                    })

            if modified_line != original_line:
                lines[line_num - 1] = modified_line

        return FixResult()
            file_path=str(file_path),
            fix_type="code_quality","
            original_content=content,
            fixed_content='\n'.join(lines),'
            success=len(line_changes) > 0,
            message=f"Applied {len(line_changes)} code quality fixes","
            line_changes=line_changes
        )

    def _has_unclosed_brackets(self, line: str) -> bool:
        """Check if line has unclosed brackets""""
        brackets = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}"
        stack = []
        in_string = False
        string_char = None

        for char in line:
            if in_string:
                if char == string_char and line.count(char) % 2 == 1:
                    in_string = False
                    string_char = None
            else:
                if char in brackets.values():
                    if stack and stack[-1] == char:
                        stack.pop()
                elif char in brackets.keys():
                    if char in ['"', "'"]:"
                        in_string = True
                        string_char = char
                    stack.append(brackets[char])

        return len(stack) > 0 or in_string

    def fix_all_issues(self, error_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fixes to all detected issues""""
        print("🔧 Applying Smart Fixes to Detected Issues")"
        print("=" * 50)"

        errors_by_file = {}
        for error in error_results.get('errors', []):'
            file_path = error['file_path']'
            if file_path not in errors_by_file:
                errors_by_file[file_path] = []
            errors_by_file[file_path].append(error)

        total_fixes_applied = 0
        files_fixed = 0

        for file_path, file_errors in errors_by_file.items():
            print(f"\n🔧 Fixing: {file_path}")"

            # Extract error types
            error_types = list(set(error['error_type'] for error in file_errors))'

            # Apply fixes
            full_path = self.project_root / file_path
            fix_results = self.apply_fixes_to_file(full_path, error_types)

            for fix_result in fix_results:
                if fix_result.success:
                    total_fixes_applied += len(fix_result.line_changes or [])
                    print(f"  ✅ {fix_result.message}")"
                    for change in fix_result.line_changes or []:
                        print(f"    Line {change['line_number']}: {change['change']}")"
                    files_fixed += 1
                else:
                    print(f"  ⚠️  Fix failed: {fix_result.message}")"

        # Create fix summary
        summary = {}
            'timestamp': datetime.now().isoformat(),'
            'total_fixes_applied': total_fixes_applied,'
            'files_fixed': files_fixed,'
            'fix_results': self.fixes_applied'
        }

        print(f"\n📊 Fix Summary:")"
        print(f"  Total fixes applied: {total_fixes_applied}")"
        print(f"  Files fixed: {files_fixed}")"

        return summary

    def create_fix_report(self, fix_results: Dict[str, Any]) -> str:
        """Create a comprehensive fix report""""
        report = []
        report.append("# BSEE Smart Fix System Report")"
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")"
        report.append("")"
        report.append("## Fix Summary")"
        report.append("")"
        report.append(f"- **Total Fixes Applied**: {fix_results.get('total_fixes_applied', 0)}")"
        report.append(f"- **Files Fixed**: {fix_results.get('files_fixed', 0)}")"
        report.append("")"
        report.append("## Applied Fixes by Type")"
        report.append("")"

        # Group fixes by type
        fix_types = {}
        for result in self.fixes_applied:
            if result.success:
                fix_type = result.fix_type
                if fix_type not in fix_types:
                    fix_types[fix_type] = 0
                fix_types[fix_type] += len(result.line_changes or [])

        for fix_type, count in sorted(fix_types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{fix_type.title()} Fixes**: {count}")"

        report.append("")"
        report.append("## Recommendations")"
        report.append("")"
        report.append("1. **Review Applied Changes**: Verify that all fixes are correct")"
        report.append("2. **Run Tests Again**: Run error detection to verify improvements")"
        report.append("3. **Manual Review**: Some issues may require manual attention")"
        report.append("4. **Continuous Monitoring**: Regularly run error detection to catch new issues")"

        return '\n'.join(report)'


def main():
    """Main function for smart fix system""""
    import argparse

    parser = argparse.ArgumentParser(description="Smart fix system for BSEE codebase")"
    parser.add_argument("--project-root", default=".", help="Root directory of the project")"
    parser.add_argument("--input-json", required=True, help="JSON file with error detection results")"
    parser.add_argument("--output", help="Output file for fix report")"

    args = parser.parse_args()

    # Load error results
    try:
        with open(args.input_json, 'r') as f:'
            error_results = json.load(f)
    except Exception as e:
        print(f"Error loading error results: {e}")"
        return

    # Apply fixes
    fix_system = SmartFixSystem(args.project_root)
    fix_summary = fix_system.fix_all_issues(error_results)

    # Generate report
    report = fix_system.create_fix_report(fix_summary)

    if args.output:
        with open(args.output, 'w') as f:'
            f.write(report)
        print(f"\n📄 Fix report saved to: {args.output}")"
    else:
        print(report)

    return fix_summary


if __name__ == "__main__":"
    main()