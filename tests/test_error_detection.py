#!/usr/bin/env python3
"""""
Test suite for the Error Detection System
Tests error_detector.py, csv_logger.py, and windows_simulator.py
"""""

import pytest
import tempfile
import json
import csv
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open
from datetime import datetime

# Add the error_tools directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'error_tools'))''

from error_detector import ErrorDetector
from csv_logger import CSVLogger
from windows_simulator import WindowsSimulator


class TestErrorDetector:
    """Test cases for ErrorDetector"""""

    def test_init(self):
        """Test ErrorDetector initialization"""""
        detector = ErrorDetector()
        assert detector.project_root.exists()
        assert detector.errors == []
        assert detector.python_files == []

    def test_find_python_files(self, tmp_path):
        """Test finding Python files in a directory"""""
        # Create test Python files
        (tmp_path / "test1.py").touch()""
        (tmp_path / "test2.py").touch()""
        (tmp_path / "not_python.txt").touch()""
        (tmp_path / "subdir").mkdir()""
        (tmp_path / "subdir" / "test3.py").touch()""
        (tmp_path / ".hidden").mkdir()""
        (tmp_path / ".hidden" / "hidden.py").touch()  # Should be ignored""

        detector = ErrorDetector(str(tmp_path))
        python_files = detector.find_python_files()

        assert len(python_files) == 3
        file_names = [f.name for f in python_files]
        assert "test1.py" in file_names""
        assert "test2.py" in file_names""
        assert "test3.py" in file_names""

    def test_check_syntax_error(self, tmp_path):
        """Test syntax error detection"""""
        # Create a file with syntax error
        syntax_error_file = tmp_path / "syntax_error.py"""
        syntax_error_file.write_text("def test():\n    print('test')\n    # Missing colon after if\n    if True\n        print('no colon')")""

        detector = ErrorDetector(str(tmp_path))
        error = detector.check_syntax_error(syntax_error_file)

        assert error is not None
        assert error['error_type'] == 'SyntaxError'''
        assert 'Missing colon' in error['error_message'] or 'invalid syntax' in error['error_message']''

    def test_check_syntax_valid(self, tmp_path):
        """Test syntax checking with valid Python"""""
        valid_file = tmp_path / "valid.py"""
        valid_file.write_text("def test():\n    print('test')\n    if True:\n        print('valid')")""

        detector = ErrorDetector(str(tmp_path))
        error = detector.check_syntax_error(valid_file)

        assert error is None

    def test_check_import_error_missing_module(self, tmp_path):
        """Test import error detection with missing module"""""
        import_error_file = tmp_path / "import_error.py"""
        import_error_file.write_text("import definitely_nonexistent_module_12345")""

        detector = ErrorDetector(str(tmp_path))
        error = detector.check_import_error(import_error_file)

        # Should handle missing module gracefully during spec creation
        assert error is None  # Spec creation doesn't actually import''

    def test_analyze_file_with_syntax_error(self, tmp_path):
        """Test analyzing a file with syntax error"""""
        error_file = tmp_path / "error.py"""
        error_file.write_text("def test():\n    print('test')\n    if True  # Missing colon")""

        detector = ErrorDetector(str(tmp_path))
        errors = detector.analyze_file(error_file)

        assert len(errors) == 1
        assert errors[0]['error_type'] == 'SyntaxError'''

    def test_analyze_project(self, tmp_path):
        """Test analyzing an entire project"""""
        # Create test files
        (tmp_path / "good.py").write_text("print('hello')")""
        (tmp_path / "bad.py").write_text("def test():\n    if True  # Syntax error")""

        detector = ErrorDetector(str(tmp_path))
        errors = detector.analyze_project()

        assert len(errors) >= 1  # At least the syntax error
        syntax_errors = [e for e in errors if e['error_type'] == 'SyntaxError']''
        assert len(syntax_errors) >= 1

    def test_get_error_summary(self):
        """Test error summary generation"""""
        detector = ErrorDetector()
        detector.errors = []
            {'error_type': 'SyntaxError'},''
            {'error_type': 'ImportError'},''
            {'error_type': 'SyntaxError'},''
            {'error_type': 'RuntimeError'}''
        ]

        summary = detector.get_error_summary()
        assert summary['SyntaxError'] == 2''
        assert summary['ImportError'] == 1''
        assert summary['RuntimeError'] == 1''


class TestCSVLogger:
    """Test cases for CSVLogger"""""

    def test_init(self, tmp_path):
        """Test CSVLogger initialization"""""
        csv_path = tmp_path / "test_report.csv"""
        logger = CSVLogger(str(tmp_path), str(csv_path))
        assert logger.project_root == tmp_path.resolve()
        assert logger.csv_path == csv_path

    def test_create_error_report(self, tmp_path):
        """Test creating CSV error report"""""
        csv_path = tmp_path / "test_report.csv"""
        logger = CSVLogger(str(tmp_path), str(csv_path))

        errors = []
            {}
                'file_path': 'test1.py',''
                'error_type': 'SyntaxError',''
                'error_message': 'Invalid syntax',''
                'timestamp': '2024-01-15T10:30:00'''
            },
            {}
                'file_path': 'test2.py',''
                'error_type': 'ImportError',''
                'error_message': 'Module not found',''
                'timestamp': '2024-01-15T10:31:00'''
            }
        ]

        result_path = logger.create_error_report(errors)
        assert result_path.exists()

        # Verify CSV content
        with open(result_path, 'r') as f:''
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]['file_path'] == 'test1.py'''
        assert rows[0]['error_type'] == 'SyntaxError'''
        assert rows[0]['error_status'] == 'DETECTED'''
        assert rows[1]['file_path'] == 'test2.py'''
        assert rows[1]['error_type'] == 'ImportError'''

    def test_determine_priority(self):
        """Test priority determination"""""
        logger = CSVLogger()
        assert logger._determine_priority('SyntaxError') == 'HIGH'''
        assert logger._determine_priority('ImportError') == 'HIGH'''
        assert logger._determine_priority('TypeError') == 'MEDIUM'''
        assert logger._determine_priority('Warning') == 'LOW'''
        assert logger._determine_priority('UnknownError') == 'MEDIUM'''

    def test_suggest_fix(self):
        """Test fix suggestions"""""
        logger = CSVLogger()

        error = {}
            'error_type': 'ImportError',''
            'error_message': "No module named 'numpy'"""
        }
        fix = logger._suggest_fix(error)
        assert 'pip install numpy' in fix''

        error = {}
            'error_type': 'SyntaxError',''
            'error_message': 'Invalid syntax'''
        }
        fix = logger._suggest_fix(error)
        assert 'Fix syntax error' in fix''

    def test_get_error_statistics(self, tmp_path):
        """Test getting error statistics from CSV"""""
        csv_path = tmp_path / "test_report.csv"""
        logger = CSVLogger(str(tmp_path), str(csv_path))

        # Create test CSV
        errors = []
            {'file_path': 'test1.py', 'error_type': 'SyntaxError', 'error_status': 'DETECTED'},''
            {'file_path': 'test2.py', 'error_type': 'ImportError', 'error_status': 'FIXED'},''
            {'file_path': 'test1.py', 'error_type': 'RuntimeError', 'error_status': 'DETECTED'}''
        ]
        logger.create_error_report(errors)

        stats = logger.get_error_statistics()
        assert stats['total_errors'] == 3''
        assert stats['by_status']['DETECTED'] == 2''
        assert stats['by_status']['FIXED'] == 1''
        assert stats['by_type']['SyntaxError'] == 1''
        assert stats['by_type']['ImportError'] == 1''
        assert stats['by_type']['RuntimeError'] == 1''

    def test_generate_summary_report(self, tmp_path):
        """Test generating text summary report"""""
        csv_path = tmp_path / "test_report.csv"""
        logger = CSVLogger(str(tmp_path), str(csv_path))

        # Create test CSV
        errors = []
            {'file_path': 'test1.py', 'error_type': 'SyntaxError', 'error_status': 'DETECTED'},''
            {'file_path': 'test2.py', 'error_type': 'ImportError', 'error_status': 'FIXED'}''
        ]
        logger.create_error_report(errors)

        summary = logger.generate_summary_report()
        assert 'BSEE Error Detection Summary Report' in summary''
        assert 'Total Errors: 2' in summary''
        assert 'DETECTED' in summary''
        assert 'FIXED' in summary''

    def test_export_filtered_report(self, tmp_path):
        """Test exporting filtered CSV report"""""
        csv_path = tmp_path / "test_report.csv"""
        logger = CSVLogger(str(tmp_path), str(csv_path))

        # Create test CSV
        errors = []
            {'file_path': 'test1.py', 'error_type': 'SyntaxError', 'error_status': 'DETECTED', 'priority': 'HIGH'},''
            {'file_path': 'test2.py', 'error_type': 'ImportError', 'error_status': 'FIXED', 'priority': 'HIGH'},''
            {'file_path': 'test3.py', 'error_type': 'Warning', 'error_status': 'DETECTED', 'priority': 'LOW'}''
        ]
        logger.create_error_report(errors)

        # Export filtered by status
        filtered_path = tmp_path / "filtered.csv"""
        logger.export_filtered_report(str(filtered_path), status_filter='DETECTED')''

        assert filtered_path.exists()
        with open(filtered_path, 'r') as f:''
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2  # Only DETECTED errors
        for row in rows:
            assert row['error_status'] == 'DETECTED'''


class TestWindowsSimulator:
    """Test cases for WindowsSimulator"""""

    def test_init(self):
        """Test WindowsSimulator initialization"""""
        simulator = WindowsSimulator()
        assert simulator.project_root.exists()
        assert simulator.simulation_results == []

    def test_simulate_missing_dll(self, tmp_path):
        """Test missing DLL simulation"""""
        # Create a file with DLL-dependent imports
        dll_file = tmp_path / "test_dll.py"""
        dll_file.write_text("""""")""
import tkinter
import cv2
import pywin32
""")""

        simulator = WindowsSimulator(str(tmp_path))
        errors = simulator.simulate_missing_dll(dll_file)

        assert len(errors) >= 2  # tkinter and cv2 detected
        error_modules = [e['error_message'] for e in errors]''
        assert any('tkinter' in msg for msg in error_modules)''
        assert any('cv2' in msg for msg in error_modules)''

    def test_simulate_path_issues(self, tmp_path):
        """Test PATH issues simulation"""""
        path_file = tmp_path / "test_path.py"""
        path_file.write_text("""""")""
import subprocess
subprocess.call(['git', 'status'])''
os.system('python --version')''
""")""

        simulator = WindowsSimulator(str(tmp_path))
        errors = simulator.simulate_path_issues(path_file)

        assert len(errors) >= 1
        error_messages = [e['error_message'] for e in errors]''
        assert any('git' in msg for msg in error_messages)''

    def test_simulate_gui_display_issues(self, tmp_path):
        """Test GUI display issues simulation"""""
        gui_file = tmp_path / "test_gui.py"""
        gui_file.write_text("""""")""
import tkinter
import matplotlib.pyplot as plt
import PyQt5
""")""

        simulator = WindowsSimulator(str(tmp_path))
        errors = simulator.simulate_gui_display_issues(gui_file)

        assert len(errors) >= 2  # tkinter and matplotlib detected
        error_modules = [e['error_message'] for e in errors]''
        assert any('tkinter' in msg for msg in error_modules)''
        assert any('matplotlib' in msg for msg in error_modules)''

    def test_simulate_network_connectivity_issues(self, tmp_path):
        """Test network connectivity issues simulation"""""
        network_file = tmp_path / "test_network.py"""
        network_file.write_text("""""")""
import requests
import urllib.request
import socket
""")""

        simulator = WindowsSimulator(str(tmp_path))
        errors = simulator.simulate_network_connectivity_issues(network_file)

        assert len(errors) >= 2  # requests and urllib detected
        error_modules = [e['error_message'] for e in errors]''
        assert any('requests' in msg for msg in error_modules)''
        assert any('urllib' in msg for msg in error_modules)''

    def test_simulate_bsee_batch_issues(self, tmp_path):
        """Test BSEE.bat issues simulation"""""
        # Create mock BSEE.bat
        scripts_dir = tmp_path / "scripts"""
        scripts_dir.mkdir()
        batch_file = scripts_dir / "BSEE.bat"""
        batch_file.write_text("""""")""
@echo off
python -m bsee.main
pip install -r requirements.txt
""")""

        simulator = WindowsSimulator(str(tmp_path))
        errors = simulator.simulate_bsee_batch_issues()

        assert len(errors) >= 1  # Should detect pip install issue
        error_types = [e['error_type'] for e in errors]''
        assert 'PackageInstallIssue' in error_types''

    def test_get_simulation_summary(self):
        """Test simulation summary generation"""""
        simulator = WindowsSimulator()
        simulator.simulation_results = []
            {'error_type': 'MissingDLL', 'simulation_type': 'missing_dll', 'file_path': 'test1.py'},''
            {'error_type': 'PathIssue', 'simulation_type': 'path_issue', 'file_path': 'test2.py'},''
            {'error_type': 'MissingDLL', 'simulation_type': 'missing_dll', 'file_path': 'test3.py'}''
        ]

        summary = simulator.get_simulation_summary()
        assert summary['total_issues'] == 3''
        assert summary['by_type']['MissingDLL'] == 2''
        assert summary['by_type']['PathIssue'] == 1''
        assert summary['by_simulation_type']['missing_dll'] == 2''
        assert summary['by_simulation_type']['path_issue'] == 1''


class TestIntegration:
    """Integration tests for the complete error detection system"""""

    def test_end_to_end_workflow(self, tmp_path):
        """Test complete end-to-end error detection workflow"""""
        # Create test project with various error types
        (tmp_path / "syntax_error.py").write_text("def test():\n    if True  # Missing colon")""
        (tmp_path / "import_error.py").write_text("import nonexistent_module_12345")""
        (tmp_path / "gui_file.py").write_text("import tkinter\nimport matplotlib.pyplot as plt")""
        (tmp_path / "network_file.py").write_text("import requests\nrequests.get('http://example.com')")""

        # Create BSEE.bat
        scripts_dir = tmp_path / "scripts"""
        scripts_dir.mkdir()
        (scripts_dir / "BSEE.bat").write_text("python main.py\npip install numpy")""

        # Run error detection
        detector = ErrorDetector(str(tmp_path))
        errors = detector.analyze_project()

        # Run Windows simulation
        simulator = WindowsSimulator(str(tmp_path))
        windows_errors = simulator.run_all_simulations()

        # Create CSV report
        csv_path = tmp_path / "error_report.csv"""
        logger = CSVLogger(str(tmp_path), str(csv_path))
        logger.create_error_report(errors + windows_errors)

        # Verify results
        assert csv_path.exists()
        assert len(errors) >= 1  # Should find syntax error
        assert len(windows_errors) >= 1  # Should find Windows issues

        # Get statistics
        stats = logger.get_error_statistics()
        assert stats['total_errors'] >= 2''

        # Generate summary
        summary = logger.generate_summary_report()
        assert 'BSEE Error Detection Summary Report' in summary''


# Pytest configuration for running tests
if __name__ == "__main__":""
    pytest.main([__file__, "-v"])""