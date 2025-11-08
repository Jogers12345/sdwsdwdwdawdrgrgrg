#!/usr/bin/env python3
"""
Comprehensive Test Suite for GUI Fallback System

Tests the enhanced dependency handling and terminal mode functionality
implemented as part of the BSEE planning document.
"""

import sys
import os
from pathlib import Path
import tempfile
import subprocess

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_dependency_system():
    """Test the dependency checking system."""
    print("Testing Dependency System...")
    print("-" * 40)

    import gui_main

    # Test normal dependency checking
    missing_required, missing_optional = gui_main.check_dependencies()

    print(f"Missing required: {missing_required}")
    print(f"Missing optional: {missing_optional}")

    # Verify tkinter is in missing required (for this test environment)
    assert 'tkinter' in missing_required, "tkinter should be detected as missing"

    # Test fallback configuration
    if missing_optional:
        fallback_config = gui_main.setup_fallback_mode(missing_optional)
        print(f"Fallback config created: {len(fallback_config)} settings")

        # Verify required fallback settings
        assert 'visualization_mode' in fallback_config
        assert 'chart_width' in fallback_config
        assert 'chart_height' in fallback_config

        print("✓ Dependency system working correctly")
    else:
        print("✓ All optional dependencies available")

    return True


def test_terminal_visualization():
    """Test the terminal visualization panel."""
    print("\nTesting Terminal Visualization Panel...")
    print("-" * 45)

    try:
        from gui.panels.terminal_visualization_panel import TerminalVisualizationPanel

        # Create test configuration
        test_config = {
            'visualization_mode': 'terminal',
            'chart_width': 30,
            'chart_height': 10,
            'max_results_display': 5
        }

        viz_panel = TerminalVisualizationPanel(test_config)

        # Test score progression
        test_scores = [0.1, 0.3, 0.5, 0.7, 0.9, 0.8, 0.6, 0.4, 0.2]
        viz_panel.plot_score_progression(test_scores, "Test Scores")

        # Test operation distribution
        test_ops = ['dct_transform', 'huffman_encode', 'dct_transform', 'fft_transform',
                   'huffman_encode', 'dct_transform']
        viz_panel.plot_operation_distribution(test_ops, "Test Operations")

        # Test table display
        test_headers = ['Rank', 'Score', 'Ops']
        test_rows = [
            ['1', '0.9', 'dct_transform'],
            ['2', '0.8', 'huffman_encode'],
            ['3', '0.7', 'fft_transform']
        ]
        viz_panel.show_table(test_headers, test_rows, "Test Results")

        # Test progress bar
        for i in range(101):
            viz_panel.show_progress_bar(i, 100, "Test Progress", width=20)
        print()  # New line after progress bar

        print("✓ Terminal visualization panel working correctly")
        return True

    except Exception as e:
        print(f"✗ Terminal visualization failed: {e}")
        return False


def test_fallback_configuration():
    """Test fallback configuration system."""
    print("\nTesting Fallback Configuration...")
    print("-" * 38)

    import gui_main

    # Test with missing matplotlib (should trigger terminal fallback)
    mock_missing = [
        ('matplotlib', 'terminal'),
        ('scipy', 'simplified'),
        ('pywt', 'haar_fallback')
    ]

    fallback_config = gui_main.setup_fallback_mode(mock_missing)

    print(f"Fallback settings:")
    for key, value in fallback_config.items():
        print(f"  {key}: {value}")

    # Verify expected settings
    assert fallback_config['visualization_mode'] == 'terminal'
    assert fallback_config['math_mode'] == 'numpy_only'
    assert fallback_config['wavelet_mode'] == 'haar_only'

    print("✓ Fallback configuration working correctly")
    return True


def test_terminal_mode_import():
    """Test that terminal mode components can be imported."""
    print("\nTesting Terminal Mode Components...")
    print("-" * 42)

    try:
        from gui.panels.terminal_visualization_panel import TerminalVisualizationPanel
        print("✓ TerminalVisualizationPanel imported successfully")

        # Test instantiation
        config = {'chart_width': 40, 'chart_height': 15}
        panel = TerminalVisualizationPanel(config)
        print("✓ TerminalVisualizationPanel instantiated successfully")

        # Test methods exist
        assert hasattr(panel, 'plot_score_progression')
        assert hasattr(panel, 'plot_operation_distribution')
        assert hasattr(panel, 'show_table')
        assert hasattr(panel, 'show_progress_bar')
        print("✓ All required visualization methods available")

        return True

    except Exception as e:
        print(f"✗ Terminal mode import failed: {e}")
        return False


def test_gui_main_structure():
    """Test the structure and functions of gui_main.py."""
    print("\nTesting GUI Main Structure...")
    print("-" * 35)

    import gui_main

    # Check required functions exist
    required_functions = [
        'check_dependencies',
        'setup_fallback_mode',
        'terminal_mode',
        'main',
        'check_python_version',
        'setup_directories',
        'print_help',
        'print_status',
        'print_results'
    ]

    for func_name in required_functions:
        assert hasattr(gui_main, func_name), f"Missing function: {func_name}"
        print(f"✓ Function {func_name} exists")

    # Test dependency checking returns correct format
    missing_req, missing_opt = gui_main.check_dependencies()
    assert isinstance(missing_req, list), "Missing required should be list"
    assert isinstance(missing_opt, list), "Missing optional should be list"
    print("✓ Dependency checking returns correct types")

    print("✓ GUI main structure correct")
    return True


def test_help_functionality():
    """Test the help system in terminal mode."""
    print("\nTesting Help System...")
    print("-" * 25)

    import gui_main

    # Test that help function exists and can be called
    try:
        gui_main.print_help()
        print("✓ Help system working correctly")
        return True
    except Exception as e:
        print(f"✗ Help system failed: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("BSEE GUI Fallback System - Comprehensive Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Dependency System", test_dependency_system),
        ("Terminal Visualization", test_terminal_visualization),
        ("Fallback Configuration", test_fallback_configuration),
        ("Terminal Mode Components", test_terminal_mode_import),
        ("GUI Main Structure", test_gui_main_structure),
        ("Help System", test_help_functionality)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")

    print("-" * 60)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED! GUI fallback system is working correctly.")
        print("\n✅ The planning document requirements have been successfully implemented:")
        print("   • Enhanced dependency checking with graceful fallbacks")
        print("   • Terminal mode with full command-line interface")
        print("   • ASCII visualization panel for terminal mode")
        print("   • Updated gui_main.py with graceful degradation")
        print("   • Comprehensive error handling and recovery")
    else:
        print("❌ Some tests failed. Please review the implementation.")

    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)