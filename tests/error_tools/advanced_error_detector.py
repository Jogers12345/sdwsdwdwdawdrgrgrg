#!/usr/bin/env python3
"""
Advanced Multi-Phase Error Detection System for BSEE Codebase
Progressive testing with increasing context, logical error detection, and smart fixes
"""

import os
import sys
import ast
import subprocess
import tempfile
import importlib.util
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "CRITICAL"  # Prevents execution
    HIGH = "HIGH"         # Major functionality issues
    MEDIUM = "MEDIUM"     # Annoying but workable
    LOW = "LOW"          # Code quality/style issues


class ErrorCategory(Enum):
    """Error categories for better classification"""
    SYNTAX = "SYNTAX"
    IMPORT = "IMPORT"
    RUNTIME = "RUNTIME"
    LOGICAL = "LOGICAL"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    MAINTAINABILITY = "MAINTAINABILITY"
    COMPATIBILITY = "COMPATIBILITY"


@dataclass
class ErrorInfo:
    """Enhanced error information structure"""
    file_path: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    context_snippet: Optional[str] = None
    suggested_fix: Optional[str] = None
    dependencies: List[str] = None
    test_context: Optional[str] = None
    fix_applied: bool = False
    verification_status: str = "PENDING"
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = []


class TestingPhase(Enum):
    """Testing phases for progressive context building"""
    ISOLATED = "isolated"          # File alone, no context
    BASIC_CONTEXT = "basic"        # With bsee/ directory context
    MODULE_CONTEXT = "module"      # With full module path
    PACKAGE_CONTEXT = "package"    # With complete package context
    RUNTIME_CONTEXT = "runtime"    # With simulated execution


class AdvancedErrorDetector:
    """Advanced multi-phase error detection system"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.errors = []
        self.fixes_applied = []
        self.testing_phases = [
            TestingPhase.ISOLATED,
            TestingPhase.BASIC_CONTEXT,
            TestingPhase.MODULE_CONTEXT,
            TestingPhase.PACKAGE_CONTEXT,
            TestingPhase.RUNTIME_CONTEXT
        ]

    def detect_all_errors(self) -> List[ErrorInfo]:
        """Run complete multi-phase error detection"""
        print("🚀 Starting Advanced Multi-Phase Error Detection")
        print(f"Project: {self.project_root}")
        print("=" * 60)

        # Phase 1: Find all Python files
        python_files = self._find_python_files()
        print(f"📁 Found {len(python_files)} Python files to analyze")

        all_errors = []

        for file_path in python_files:
            print(f"\n🔍 Analyzing: {file_path.relative_to(self.project_root)}")
            file_errors = self._analyze_file_with_progressive_context(file_path)
            all_errors.extend(file_errors)

            # Apply smart fixes if possible
            fixed_count = self._apply_smart_fixes(file_path, file_errors)
            if fixed_count > 0:
                print(f"  ✅ Applied {fixed_count} smart fixes")

        # Phase 2: Cross-file logical analysis
        logical_errors = self._detect_logical_errors(all_errors)
        all_errors.extend(logical_errors)

        # Phase 3: Performance and security analysis
        perf_security_errors = self._detect_performance_and_security_issues(all_errors)
        all_errors.extend(perf_security_errors)

        # Sort errors by severity and phase
        all_errors.sort(key=lambda x: (
            self._severity_order(x.severity),
            self._category_order(x.category),
            x.file_path
        ))

        self.errors = all_errors
        self._print_error_summary()

        return all_errors

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip cache and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                '__pycache__', 'node_modules', '.git', '.pytest_cache'
            ]]

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        return sorted(python_files)

    def _analyze_file_with_progressive_context(self, file_path: Path) -> List[ErrorInfo]:
        """Analyze a file with progressively increasing context"""
        file_errors = []

        # Phase 1: Isolated syntax checking
        syntax_errors = self._check_syntax_errors(file_path)
        file_errors.extend(syntax_errors)

        # If syntax errors, don't continue with other phases
        if syntax_errors:
            return file_errors

        # Phase 2: Progressive import testing
        import_errors = self._test_imports_progressively(file_path)
        file_errors.extend(import_errors)

        # Phase 3: Runtime testing with different contexts
        runtime_errors = self._test_runtime_progressively(file_path)
        file_errors.extend(runtime_errors)

        # Phase 4: Code quality analysis
        quality_errors = self._analyze_code_quality(file_path)
        file_errors.extend(quality_errors)

        return file_errors

    def _check_syntax_errors(self, file_path: Path) -> List[ErrorInfo]:
        """Check for syntax errors using AST parsing"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST to find syntax errors
            ast.parse(content)

            # Additional syntax checks
            syntax_issues = self._detect_advanced_syntax_issues(content, file_path)
            errors.extend(syntax_issues)

        except SyntaxError as e:
            error_info = ErrorInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                error_type="SyntaxError",
                error_message=f"Syntax error at line {e.lineno}: {e.msg}",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SYNTAX,
                line_number=e.lineno,
                column_number=e.offset,
                context_snippet=self._get_context_line(file_path, e.lineno),
                suggested_fix=self._suggest_syntax_fix(e, file_path)
            )
            errors.append(error_info)

        except UnicodeDecodeError as e:
            error_info = ErrorInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                error_type="EncodingError",
                error_message=f"File encoding error: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SYNTAX,
                suggested_fix="Check file encoding and special characters"
            )
            errors.append(error_info)

        return errors

    def _detect_advanced_syntax_issues(self, content: str, file_path: Path) -> List[ErrorInfo]:
        """Detect advanced syntax and code quality issues"""
        errors = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()

            # Check for common syntax issues
            if self._has_unclosed_brackets(line):
                errors.append(ErrorInfo(
                    file_path=str(file_path.relative_to(self.project_root)),
                    error_type="UnclosedBrackets",
                    error_message=f"Potential unclosed brackets in line {line_num}",
                    severity=ErrorSeverity.MEDIUM,
                    category=ErrorCategory.SYNTAX,
                    line_number=line_num,
                    context_snippet=line,
                    suggested_fix="Check for missing closing brackets or quotes"
                ))

            # Check for potential logic issues
            if self._has_logic_anti_patterns(line):
                errors.append(ErrorInfo(
                    file_path=str(file_path.relative_to(self.project_root)),
                    error_type="LogicAntiPattern",
                    error_message=f"Potential logical anti-pattern at line {line_num}: {line[:50]}...",
                    severity=ErrorSeverity.MEDIUM,
                    category=ErrorCategory.LOGICAL,
                    line_number=line_num,
                    context_snippet=line,
                    suggested_fix="Review code for logical correctness"
                ))

            # Check for security issues
            security_issues = self._detect_security_issues(line, line_num, file_path)
            errors.extend(security_issues)

        return errors

    def _test_imports_progressively(self, file_path: Path) -> List[ErrorInfo]:
        """Test imports with progressively increasing context"""
        errors = []
        file_content = file_path.read_text(encoding='utf-8')

        # Extract imports from the file
        imports = self._extract_imports(file_content)

        if not imports:
            return errors

        # Phase 1: Test with no bsee context
        isolated_errors = self._test_imports_with_context(file_path, imports, "isolated")
        errors.extend(isolated_errors)

        # Phase 2: Test with bsee directory in Python path
        if any('bsee' in imp for imp in imports):
            bsee_errors = self._test_imports_with_context(file_path, imports, "bsee_context")
            # Only add new errors that weren't found in isolated testing
            new_errors = [e for e in bsee_errors if not self._error_exists(e, errors)]
            for error in new_errors:
                error.test_context = "bsee_context"
            errors.extend(new_errors)

        # Phase 3: Test with full package context
        package_errors = self._test_imports_with_context(file_path, imports, "package_context")
        new_errors = [e for e in package_errors if not self._error_exists(e, errors)]
        for error in new_errors:
            error.test_context = "package_context"
        errors.extend(new_errors)

        return errors

    def _test_imports_with_context(self, file_path: Path, imports: List[str], context: str) -> List[ErrorInfo]:
        """Test imports with specific context setup"""
        errors = []

        # Create test script with appropriate context
        test_script = self._create_context_test_script(file_path, imports, context)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(test_script)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root)
            )

            if result.returncode != 0:
                # Analyze the error output
                error_info = self._analyze_import_error(result.stderr, file_path, context)
                if error_info:
                    errors.append(error_info)

        except subprocess.TimeoutExpired:
            errors.append(ErrorInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                error_type="ImportTimeout",
                error_message=f"Import testing timed out in {context} context",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.IMPORT,
                test_context=context,
                suggested_fix="Review import logic and potential circular dependencies"
            ))
        except Exception as e:
            errors.append(ErrorInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                error_type="ImportTestError",
                error_message=f"Error testing imports: {str(e)}",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.IMPORT,
                test_context=context
            ))
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

        return errors

    def _create_context_test_script(self, file_path: Path, imports: List[str], context: str) -> str:
        """Create test script with appropriate context setup"""
        rel_path = file_path.relative_to(self.project_root)

        script_lines = [
            "import sys",
            "import os",
            "import importlib.util"
        ]

        # Add context-specific Python path setup
        if context == "bsee_context":
            script_lines.extend([
                "sys.path.insert(0, os.path.join(os.getcwd(), 'bsee'))"
            ])
        elif context == "package_context":
            script_lines.extend([
                "sys.path.insert(0, os.getcwd())"
            ])

        script_lines.extend([
            "",
            "try:",
            f"    # Test importing target file: {rel_path}",
            "    spec = importlib.util.spec_from_file_location('test_module', '" + str(file_path) + "')",
            "    if spec and spec.loader:",
            "        module = importlib.util.module_from_spec(spec)",
            "        spec.loader.exec_module(module)",
            "        print('SUCCESS: File imported successfully')",
            "except ImportError as e:",
            "    print(f'IMPORT_ERROR: {e}')",
            "except Exception as e:",
            "    print(f'OTHER_ERROR: {e}')",
            "",
            "print('TEST_COMPLETE')"
        ])

        return '\n'.join(script_lines)

    def _test_runtime_progressively(self, file_path: Path) -> List[ErrorInfo]:
        """Test file runtime with progressive context"""
        errors = []
        rel_path = file_path.relative_to(self.project_root)

        # Create a runtime test script
        test_script = f"""
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # Import the file
    import importlib.util
    spec = importlib.util.spec_from_file_location('test_module', '{file_path}')
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test if it has a main function
        if hasattr(module, 'main') and callable(getattr(module, 'main')):
            print('HAS_MAIN_FUNCTION')
        else:
            print('NO_MAIN_FUNCTION')

except Exception as e:
    print(f'RUNTIME_ERROR: {{e}}')
    import traceback
    traceback.print_exc()
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(test_script)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root)
            )

            if "RUNTIME_ERROR" in result.stdout or result.returncode != 0:
                error_info = ErrorInfo(
                    file_path=str(rel_path),
                    error_type="RuntimeError",
                    error_message=f"Runtime error: {result.stdout.split('RUNTIME_ERROR:')[1] if 'RUNTIME_ERROR:' in result.stdout else 'Unknown runtime error'}",
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.RUNTIME,
                    test_context="runtime_context",
                    suggested_fix="Debug runtime logic and check dependencies"
                )
                errors.append(error_info)

        except subprocess.TimeoutExpired:
            errors.append(ErrorInfo(
                file_path=str(rel_path),
                error_type="RuntimeTimeout",
                error_message="Runtime testing timed out",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.RUNTIME,
                suggested_fix="Review code for infinite loops or blocking operations"
            ))
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

        return errors

    def _analyze_code_quality(self, file_path: Path) -> List[ErrorInfo]:
        """Analyze code quality issues"""
        errors = []
        content = file_path.read_text(encoding='utf-8')

        # Parse AST for structural analysis
        try:
            tree = ast.parse(content)

            # Check for various code quality issues
            quality_issues = self._detect_code_quality_issues(tree, content, file_path)
            errors.extend(quality_issues)

        except Exception as e:
            # If AST parsing fails, we already caught it as syntax error
            pass

        return errors

    def _detect_code_quality_issues(self, tree: ast.AST, content: str, file_path: Path) -> List[ErrorInfo]:
        """Detect code quality issues using AST analysis"""
        errors = []

        # Check for overly complex functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    errors.append(ErrorInfo(
                        file_path=str(file_path.relative_to(self.project_root)),
                        error_type="HighComplexity",
                        error_message=f"Function '{node.name}' has high cyclomatic complexity: {complexity}",
                        severity=ErrorSeverity.MEDIUM,
                        category=ErrorCategory.MAINTAINABILITY,
                        line_number=node.lineno,
                        suggested_fix=f"Consider breaking down function '{node.name}' into smaller functions"
                    ))

            # Check for overly long functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines_count = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 50
                if lines_count > 50:
                    errors.append(ErrorInfo(
                        file_path=str(file_path.relative_to(self.project_root)),
                        error_type="LongFunction",
                        error_message=f"Function '{node.name}' is too long: {lines_count} lines",
                        severity=ErrorSeverity.MEDIUM,
                        category=ErrorCategory.MAINTAINABILITY,
                        line_number=node.lineno,
                        suggested_fix=f"Consider refactoring function '{node.name}' to be more concise"
                    ))

        return errors

    def _detect_logical_errors(self, all_errors: List[ErrorInfo]) -> List[ErrorInfo]:
        """Detect logical errors by analyzing relationships between errors"""
        logical_errors = []

        # Check for potential circular imports
        import_errors = [e for e in all_errors if e.category == ErrorCategory.IMPORT]
        circular_imports = self._detect_circular_imports(import_errors)
        logical_errors.extend(circular_imports)

        # Check for missing dependencies
        missing_deps = self._detect_missing_dependencies(all_errors)
        logical_errors.extend(missing_deps)

        return logical_errors

    def _detect_circular_imports(self, import_errors: List[ErrorInfo]) -> List[ErrorInfo]:
        """Detect potential circular import issues"""
        # This is a simplified version - a real implementation would build a dependency graph
        circular_imports = []

        # Group by directory to find potential circular dependencies
        directories = {}
        for error in import_errors:
            path_parts = error.file_path.split('/')
            if len(path_parts) > 1:
                directory = '/'.join(path_parts[:-1])
                if directory not in directories:
                    directories[directory] = []
                directories[directory].append(error)

        # Check for suspicious patterns
        for dir_name, errors in directories.items():
            if len(errors) > 5:  # Many import errors in same directory
                circular_imports.append(ErrorInfo(
                    file_path=dir_name,
                    error_type="PotentialCircularImport",
                    error_message=f"Directory '{dir_name}' has multiple import issues, check for circular dependencies",
                    severity=ErrorSeverity.MEDIUM,
                    category=ErrorCategory.LOGICAL,
                    suggested_fix="Review imports in this directory for circular dependencies"
                ))

        return circular_imports

    def _detect_missing_dependencies(self, all_errors: List[ErrorInfo]) -> List[ErrorInfo]:
        """Detect missing dependencies that appear in multiple files"""
        dependency_counts = {}

        for error in all_errors:
            if error.category == ErrorCategory.IMPORT:
                # Extract module name from error message
                if "No module named" in error.error_message:
                    match = re.search(r"No module named '([^']+)'", error.error_message)
                    if match:
                        module_name = match.group(1)
                        dependency_counts[module_name] = dependency_counts.get(module_name, 0) + 1

        missing_deps = []
        for module, count in dependency_counts.items():
            if count > 3:  # Module missing in multiple files
                missing_deps.append(ErrorInfo(
                    file_path="multiple_files",
                    error_type="MissingDependency",
                    error_message=f"Module '{module}' is missing in {count} files",
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.LOGICAL,
                    suggested_fix=f"Install missing dependency: pip install {module}"
                ))

        return missing_deps

    def _detect_performance_and_security_issues(self, all_errors: List[ErrorInfo]) -> List[ErrorInfo]:
        """Detect performance and security issues"""
        perf_security_errors = []

        # Analyze files for security issues
        python_files = self._find_python_files()
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                security_issues = self._detect_security_content_issues(content, file_path)
                perf_security_errors.extend(security_issues)
            except Exception:
                continue

        return perf_security_errors

    def _detect_security_content_issues(self, content: str, file_path: Path) -> List[ErrorInfo]:
        """Detect security issues in file content"""
        errors = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # Security anti-patterns
            security_issues = [
                ("eval(", "Use of eval() function"),
                ("exec(", "Use of exec() function"),
                ("subprocess.call", "Unsanitized subprocess call"),
                ("pickle.load", "Unsafe pickle deserialization"),
                ("input()", "Unvalidated input"),
                ("os.system", "Unsafe os.system call"),
                ("shell=True", "Shell injection risk"),
                ("password=", "Password in code"),
                ("secret=", "Secret in code"),
                ("token=", "Token in code"),
                ("api_key=", "API key in code"),
            ]

            for pattern, description in security_issues:
                if pattern in line_lower and not line.strip().startswith('#'):
                    severity = ErrorSeverity.HIGH if "eval" in pattern or "exec" in pattern else ErrorSeverity.MEDIUM

                    errors.append(ErrorInfo(
                        file_path=str(file_path.relative_to(self.project_root)),
                        error_type="SecurityIssue",
                        error_message=f"{description} at line {line_num}: {line[:80]}...",
                        severity=severity,
                        category=ErrorCategory.SECURITY,
                        line_number=line_num,
                        context_snippet=line.strip(),
                        suggested_fix=f"Review and secure {description}"
                    ))

            # Performance issues
            performance_issues = [
                ("time.sleep", "Potential blocking sleep"),
                ("while True:", "Potential infinite loop"),
                ("for i in range(", "Check loop efficiency"),
                ("global ", "Use of global variables"),
            ]

            for pattern, description in performance_issues:
                if pattern in line and not line.strip().startswith('#'):
                    errors.append(ErrorInfo(
                        file_path=str(file_path.relative_to(self.project_root)),
                        error_type="PerformanceIssue",
                        error_message=f"{description} at line {line_num}: {line[:80]}...",
                        severity=ErrorSeverity.LOW,
                        category=ErrorCategory.PERFORMANCE,
                        line_number=line_num,
                        context_snippet=line.strip(),
                        suggested_fix=f"Review {description} for optimization"
                    ))

        return errors

    def _apply_smart_fixes(self, file_path: Path, file_errors: List[ErrorInfo]) -> int:
        """Apply smart fixes to common issues"""
        fixes_applied = 0

        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content

            # Apply fixes for common issues
            for error in file_errors:
                if error.fix_applied:
                    continue

                if "regex" in error.error_message and "pattern" not in content:
                    # Fix Pydantic regex -> pattern
                    content = content.replace('regex=', 'pattern=')
                    error.fix_applied = True
                    fixes_applied += 1
                    error.verification_status = "FIXED"

                elif "validator" in error.error_message and "field_validator" not in content:
                    # Fix validator -> field_validator
                    content = content.replace('@validator', '@field_validator')
                    error.fix_applied = True
                    fixes_applied += 1
                    error.verification_status = "FIXED"

            # Write back if changes were made
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"  🔧 Applied {fixes_applied} automated fixes")

        except Exception as e:
            print(f"  ⚠️  Error applying fixes: {e}")

        return fixes_applied

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from file content"""
        imports = []

        # Extract import statements
        for match in re.finditer(r'^import ([\w\.]+)', content, re.MULTILINE):
            imports.append(match.group(1))

        for match in re.finditer(r'^from ([\w\.]+) import', content, re.MULTILINE):
            imports.append(match.group(1))

        return imports

    def _get_context_line(self, file_path: Path, line_num: int, context_lines: int = 3) -> str:
        """Get context lines around an error"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)

            context = []
            for i in range(start, end):
                marker = ">>> " if i == line_num - 1 else "    "
                context.append(f"{marker}{lines[i].rstrip()}")

            return '\n'.join(context)
        except Exception:
            return "Context not available"

    def _suggest_syntax_fix(self, error: SyntaxError, file_path: Path) -> str:
        """Suggest fix for syntax error"""
        msg = error.msg.lower()

        if "invalid syntax" in msg:
            return "Check for missing brackets, colons, or quotes"
        elif "unexpected eof" in msg:
            return "Check for unclosed brackets or quotes"
        elif "indentation" in msg:
            return "Fix indentation to match surrounding code"
        elif "invalid character" in msg:
            return "Remove invalid characters or check file encoding"
        else:
            return "Review syntax at indicated location"

    def _analyze_import_error(self, error_output: str, file_path: Path, context: str) -> Optional[ErrorInfo]:
        """Analyze import error output and create ErrorInfo"""
        if "IMPORT_ERROR:" in error_output:
            error_msg = error_output.split('IMPORT_ERROR:')[1].strip()

            # Determine severity based on context
            if context == "isolated":
                severity = ErrorSeverity.MEDIUM
                category = ErrorCategory.IMPORT
            elif context == "bsee_context":
                severity = ErrorSeverity.HIGH
                category = ErrorCategory.IMPORT
            else:
                severity = ErrorSeverity.HIGH
                category = ErrorCategory.IMPORT

            return ErrorInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                error_type="ImportError",
                error_message=error_msg,
                severity=severity,
                category=category,
                test_context=context,
                suggested_fix=self._suggest_import_fix(error_msg, context)
            )

        return None

    def _suggest_import_fix(self, error_msg: str, context: str) -> str:
        """Suggest fix for import error"""
        if "No module named" in error_msg:
            module_match = re.search(r"No module named '([^']+)'", error_msg)
            if module_match:
                module = module_match.group(1)
                if module == 'yaml':
                    return "Install PyYAML: pip install pyyaml"
                elif module.startswith('bsee'):
                    return "Add bsee to Python path: export PYTHONPATH=$PYTHONPATH:$(pwd)"
                else:
                    return f"Install missing module: pip install {module}"

        elif "attempted relative import" in error_msg:
            return "Run file as part of package: python -m package.module"

        elif "cannot import" in error_msg:
            return "Check if the imported name exists in the target module"

        return "Review import statement and module structure"

    def _has_unclosed_brackets(self, line: str) -> bool:
        """Check if line has unclosed brackets"""
        brackets = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        stack = []
        in_string = False
        string_char = None

        for char in line:
            if in_string:
                if char == string_char and (line.count(char) % 2 == 1 or char not in brackets):
                    in_string = False
                    string_char = None
            else:
                if char in brackets.values():
                    if stack and stack[-1] == char:
                        stack.pop()
                elif char in brackets.keys():
                    if char in ['"', "'"]:
                        in_string = True
                        string_char = char
                    stack.append(brackets[char])

        return len(stack) > 0 or in_string

    def _has_logic_anti_patterns(self, line: str) -> bool:
        """Check for common logical anti-patterns"""
        anti_patterns = [
            "if True:",
            "if False:",
            "while True:",  # Could be intentional, worth checking
            "except:",
            "except Exception:",
            "pass  # TODO",
            "return None",  # Often indicates missing error handling
        ]

        line_stripped = line.strip()
        for pattern in anti_patterns:
            if line_stripped.startswith(pattern):
                return True

        return False

    def _detect_security_issues(self, line: str, line_num: int, file_path: Path) -> List[ErrorInfo]:
        """Detect security issues in a line of code"""
        return []  # Implemented in _detect_security_content_issues

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith,
                               ast.Try, ast.ExceptHandler, ast.ListComp, ast.SetComp, ast.DictComp,
                               ast.GeneratorExp)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _error_exists(self, error: ErrorInfo, existing_errors: List[ErrorInfo]) -> bool:
        """Check if error already exists in list"""
        for existing in existing_errors:
            if (existing.file_path == error.file_path and
                existing.error_type == error.error_type and
                existing.test_context == error.test_context):
                return True
        return False

    def _severity_order(self, severity: ErrorSeverity) -> int:
        """Get order for sorting by severity"""
        order = {
            ErrorSeverity.CRITICAL: 0,
            ErrorSeverity.HIGH: 1,
            ErrorSeverity.MEDIUM: 2,
            ErrorSeverity.LOW: 3
        }
        return order.get(severity, 4)

    def _category_order(self, category: ErrorCategory) -> int:
        """Get order for sorting by category"""
        order = {
            ErrorCategory.SYNTAX: 0,
            ErrorCategory.IMPORT: 1,
            ErrorCategory.RUNTIME: 2,
            ErrorCategory.LOGICAL: 3,
            ErrorCategory.SECURITY: 4,
            ErrorCategory.PERFORMANCE: 5,
            ErrorCategory.MAINTAINABILITY: 6,
            ErrorCategory.COMPATIBILITY: 7
        }
        return order.get(category, 8)

    def _print_error_summary(self):
        """Print comprehensive error summary"""
        print("\n" + "=" * 60)
        print("📊 ADVANCED ERROR DETECTION SUMMARY")
        print("=" * 60)

        if not self.errors:
            print("🎉 NO ERRORS FOUND! Code is clean.")
            return

        # Count by severity
        severity_counts = {}
        category_counts = {}

        for error in self.errors:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1

        print(f"📈 Total Errors Found: {len(self.errors)}")
        print()

        print("🚨 BY SEVERITY:")
        severity_order = [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH, ErrorSeverity.MEDIUM, ErrorSeverity.LOW]
        for severity in severity_order:
            count = severity_counts.get(severity.value, 0)
            if count > 0:
                icon = "🔴" if severity == ErrorSeverity.CRITICAL else "🟠" if severity == ErrorSeverity.HIGH else "🟡" if severity == ErrorSeverity.MEDIUM else "🟢"
                print(f"  {icon} {severity.value:12}: {count:4} ({count/len(self.errors)*100:5.1f}%)")

        print()
        print("📂 BY CATEGORY:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:15}: {count:4} ({count/len(self.errors)*100:5.1f}%)")

        print()
        print("🎯 TOP ISSUES REQUIRING ATTENTION:")

        # Show top 10 most critical errors
        critical_errors = sorted(self.errors, key=lambda x: (self._severity_order(x.severity), x.file_path))[:10]
        for i, error in enumerate(critical_errors, 1):
            icon = "🔴" if error.severity == ErrorSeverity.CRITICAL else "🟠" if error.severity == ErrorSeverity.HIGH else "🟡"
            print(f"  {i}. {icon} {error.file_path}")
            print(f"     {error.error_type}: {error.error_message[:100]}...")
            if error.suggested_fix:
                print(f"     💡 Fix: {error.suggested_fix}")
            print()

        print("💡 Use the provided fixes and suggestions to resolve these issues.")

    def export_results(self, output_path: str = None) -> str:
        """Export results to JSON"""
        if output_path is None:
            output_path = f"/tmp/advanced_error_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'total_errors': len(self.errors),
            'errors': []
        }

        for error in self.errors:
            error_dict = {
                'file_path': error.file_path,
                'error_type': error.error_type,
                'error_message': error.error_message,
                'severity': error.severity.value,
                'category': error.category.value,
                'line_number': error.line_number,
                'column_number': error.column_number,
                'context_snippet': error.context_snippet,
                'suggested_fix': error.suggested_fix,
                'dependencies': error.dependencies,
                'test_context': error.test_context,
                'fix_applied': error.fix_applied,
                'verification_status': error.verification_status,
                'timestamp': error.timestamp
            }
            results['errors'].append(error_dict)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results exported to: {output_path}")
        return output_path


def main():
    """Main function for advanced error detection"""
    import argparse

    parser = argparse.ArgumentParser(description="Advanced multi-phase error detection")
    parser.add_argument("--project-root", default=".", help="Root directory of the project")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--fix-automatically", action="store_true", help="Apply automatic fixes where possible")

    args = parser.parse_args()

    detector = AdvancedErrorDetector(args.project_root)
    errors = detector.detect_all_errors()

    # Export results
    output_path = detector.export_results(args.output)

    return errors


if __name__ == "__main__":
    main()