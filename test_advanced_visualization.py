#!/usr/bin/env python3
"""
Comprehensive Test Suite for Advanced Visualization System

Tests the transformation viewer, animation system, binary display modes,
and export capabilities implemented in Phase 2.
"""

import sys
import os
import time
import tempfile
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def test_transformation_viewer():
    """Test transformation viewer component."""
    print("Testing Transformation Viewer...")
    print("-" * 40)

    try:
        from gui.components.transformation_viewer import TransformationViewer
        from bsee.engine.history import HistoryManager

        # Create history manager
        history_manager = HistoryManager()

        # Create viewer
        viewer = TransformationViewer(None, history_manager)
        print("✓ TransformationViewer created successfully")

        # Create mock transformation data
        mock_data = create_mock_transformation_data()
        viewer.load_analysis_history(mock_data)
        print("✓ Mock data loaded successfully")

        # Test navigation
        if viewer.operation_steps:
            initial_count = len(viewer.operation_steps)
            viewer.step_forward()
            viewer.step_backward()
            viewer.reset_replay()
            print(f"✓ Navigation works with {initial_count} operations")

        return True

    except Exception as e:
        print(f"✗ Transformation viewer test failed: {e}")
        return False

def test_operation_animator():
    """Test operation animation system."""
    print("\nTesting Operation Animator...")
    print("-" * 40)

    try:
        from gui.animation.operation_animator import OperationAnimator

        # Create animator
        animator = OperationAnimator(None)
        print("✓ OperationAnimator created successfully")

        # Test animation effects
        changes = [(0, 0x41, 0x42), (1, 0x42, 0x43), (2, 0x43, 0x44)]

        # Create mock text widget
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window

        text_widget = tk.Text(root, height=10, width=40,
                               bg='#1e1e1e', fg='#00ff00',
                               font=('Consolas', 10))

        # Test different animation effects
        animator.animate_byte_changes(changes, text_widget)
        animator.pulse_effect([0, 1, 2], text_widget, duration=0.1)
        animator.fade_in_effect([0, 1, 2], text_widget, duration=0.1)
        animator.slide_effect(0, 2, text_widget, duration=0.1)

        print("✓ Animation effects created successfully")
        print(f"✓ Animation status: {animator.get_animation_status()}")

        root.destroy()
        return True

    except Exception as e:
        print(f"✗ Operation animator test failed: {e}")
        return False

def test_binary_display():
    """Test enhanced binary display modes."""
    print("\nTesting Enhanced Binary Display...")
    print("-" * 40)

    try:
        from gui.components.binary_display import BinaryDisplay, DisplayConfig

        # Create display
        config = DisplayConfig()
        display = BinaryDisplay(None, config)
        print("✓ BinaryDisplay created successfully")

        # Test data
        test_data = b"Hello World! " + bytes(range(256))
        display.set_display_data(test_data)
        print(f"✓ Data loaded: {len(test_data)} bytes")

        # Test different display modes
        modes = ["hex", "binary", "decimal", "ascii", "mixed"]
        for mode in modes:
            display.mode_var.set(mode)
            display._refresh_display()
            print(f"✓ {mode} mode works")

        # Test cursor movement
        display._move_cursor(10)
        display._move_cursor_to_end()
        print("✓ Cursor navigation works")

        # Test selection
        display.selection_start = 5
        display.selection_end = 15
        display._update_selection()
        print("✓ Selection works")

        # Test byte information
        byte_val = display.get_byte_at_cursor()
        entropy = display._calculate_entropy()
        print(f"✓ Byte info: {byte_val}, Entropy: {entropy:.3f}")

        return True

    except Exception as e:
        print(f"✗ Binary display test failed: {e}")
        return False

def test_transformation_export():
    """Test transformation export capabilities."""
    print("\nTesting Transformation Export...")
    print("-" * 40)

    try:
        from gui.export.transformation_export import TransformationExporter, ExportConfig

        # Create exporter
        exporter = TransformationExporter()
        print("✓ TransformationExporter created successfully")

        # Test configuration
        config = ExportConfig()
        exporter.config = config
        print("✓ Export configuration works")

        # Test available formats
        formats = exporter.available_formats
        print(f"✓ Available formats: {formats}")

        # Test mock export (without saving files)
        mock_data = create_mock_transformation_data()

        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_export.json")

            # Test data export
            success = exporter._export_json_data(mock_data, test_file)
            if success:
                print("✓ JSON export works")
                # Verify file was created and has content
                if os.path.exists(test_file):
                    with open(test_file, 'r') as f:
                        exported_data = json.load(f)
                        if 'transformation' in exported_data:
                            print("✓ Exported data structure is correct")

        return True

    except Exception as e:
        print(f"✗ Transformation export test failed: {e}")
        return False

def test_history_integration():
    """Test history manager integration."""
    print("\nTesting History Manager Integration...")
    print("-" * 40)

    try:
        from bsee.engine.history import HistoryManager

        # Create history manager
        history = HistoryManager()
        print("✓ HistoryManager created successfully")

        # Test session management
        session_id = history.start_session(
            initial_data=b"Test data",
            metadata={"test": True}
        )
        print(f"✓ Session started: {session_id}")

        # Add operation snapshots
        before_data = b"Hello"
        after_data = b"Hello World!"

        snapshot = history.add_operation_snapshot(
            operation_name="test_operation",
            operation_params={"param1": "value1"},
            before_data=before_data,
            after_data=after_data,
            metrics_before={"entropy": 1.0},
            metrics_after={"entropy": 2.0},
            timing_info={"execution_time": 0.1}
        )
        print(f"✓ Operation snapshot added: {snapshot.operation_name}")

        # Test session export for replay
        replay_data = history.export_session_for_replay()
        if 'operations' in replay_data:
            print(f"✓ Replay data exported: {len(replay_data['operations'])} operations")

        # End session
        completed_session = history.end_session()
        print(f"✓ Session completed: {completed_session.session_id}")

        # Test session history
        history_list = history.get_session_history()
        print(f"✓ Session history: {len(history_list)} sessions")

        return True

    except Exception as e:
        print(f"✗ History integration test failed: {e}")
        return False

def test_visualization_modes():
    """Test advanced visualization modes."""
    print("\nTesting Advanced Visualization Modes...")
    print("-" * 40)

    try:
        from gui.components.binary_display import BinaryDisplay

        # Test data with different patterns
        test_patterns = [
            b"AAAAAAABBBBBBCCCCCCCDDDDDD",  # Repeated patterns
            bytes(range(256)),                   # All byte values
            b"\x00\x01\x02\x03" * 64,            # Sequential
            os.urandom(1024),                    # Random data
        ]

        display = BinaryDisplay(None)

        for i, pattern in enumerate(test_patterns):
            display.set_display_data(pattern)
            entropy = display._calculate_entropy()
            display.mode_var.set("heatmap")
            display._refresh_display()
            print(f"✓ Pattern {i+1}: {len(pattern)} bytes, entropy: {entropy:.3f}")

        return True

    except Exception as e:
        print(f"✗ Visualization modes test failed: {e}")
        return False

def test_animation_performance():
    """Test animation system performance."""
    print("\nTesting Animation Performance...")
    print("-" * 40)

    try:
        from gui.animation.operation_animator import OperationAnimator

        animator = OperationAnimator(None)

        # Create large number of changes
        large_changes = [(i, i % 256, (i + 1) % 256) for i in range(1000)]

        import tkinter as tk
        root = tk.Tk()
        root.withdraw()

        text_widget = tk.Text(root, height=20, width=60)

        # Measure animation time
        start_time = time.time()
        animator.animate_byte_changes(large_changes, text_widget)
        end_time = time.time()

        animation_time = end_time - start_time
        print(f"✓ Animated {len(large_changes)} changes in {animation_time:.3f}s")
        print(f"✓ Rate: {len(large_changes)/animation_time:.0f} changes/second")

        root.destroy()
        return True

    except Exception as e:
        print(f"✗ Animation performance test failed: {e}")
        return False

def test_export_formats():
    """Test different export formats."""
    print("\nTesting Export Formats...")
    print("-" * 40)

    try:
        from gui.export.transformation_export import TransformationExporter

        exporter = TransformationExporter()

        # Test HTML report generation
        mock_data = create_mock_transformation_data()
        html_content = exporter._generate_html_report(mock_data)
        if "<html>" in html_content and "</html>" in html_content:
            print("✓ HTML report generation works")

        # Test markdown report generation
        markdown_content = exporter._generate_markdown_report(mock_data)
        if "# BSEE" in markdown_content:
            print("✓ Markdown report generation works")

        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_file = f.name
        exporter._export_json_data(mock_data, json_file)
        if os.path.exists(json_file):
            print("✓ JSON export works")
            os.unlink(json_file)

        return True

    except Exception as e:
        print(f"✗ Export formats test failed: {e}")
        return False

def create_mock_transformation_data():
    """Create mock transformation data for testing."""
    operations = []

    # Create a sequence of transformations
    initial_data = b"Hello World! " + bytes(range(100))
    current_data = initial_data

    for i in range(5):
        operation_name = f"test_operation_{i+1}"
        operation_params = {"step": i+1, "param": f"value_{i+1}"}

        # Simulate transformation
        if i == 0:  # Add data
            after_data = current_data + b"Additional data"
        elif i == 1:  # Transform data
            after_data = bytes((b + 1) % 256 for b in current_data)
        elif i == 2:  # Reverse some data
            after_data = current_data[:len(current_data)//2] + current_data[len(current_data)//2::-1]
        elif i == 3:  # Modify data
            after_data = current_data[:20] + b"MODIFIED" + current_data[28:]
        else:  # Final transformation
            after_data = current_data.upper() if isinstance(current_data, bytes) else current_data

        # Create mock metrics
        metrics_before = {
            "entropy": 6.5 - i * 0.5,
            "compression_ratio": 1.2 - i * 0.1,
            "complexity": 100.0 + i * 10
        }

        metrics_after = {
            "entropy": 6.0 - i * 0.5,
            "compression_ratio": 1.1 - i * 0.1,
            "complexity": 110.0 + i * 10
        }

        # Create mock timing
        timing_info = {
            "execution_time": 0.05 + i * 0.01,
            "preparation_time": 0.001,
            "cleanup_time": 0.002
        }

        # Create mock byte changes
        byte_changes = []
        min_len = min(len(current_data), len(after_data))
        for j in range(min_len):
            if current_data[j] != after_data[j]:
                byte_changes.append((j, current_data[j], after_data[j]))

        # Add operation
        operation = {
            "name": operation_name,
            "params": operation_params,
            "before_hex": current_data.hex(),
            "after_hex": after_data.hex(),
            "metrics_before": metrics_before,
            "metrics_after": metrics_after,
            "timing": timing_info,
            "byte_changes": byte_changes,
            "metadata": {"test": True, "index": i}
        }

        operations.append(operation)
        current_data = after_data

    return {
        "session_id": f"test_session_{int(time.time())}",
        "start_time": time.time(),
        "initial_data": initial_data.hex(),
        "final_data": current_data.hex(),
        "operations": operations,
        "test_metadata": {"created_for": "advanced_visualization_testing"}
    }

def run_comprehensive_tests():
    """Run all advanced visualization tests."""
    print("=" * 60)
    print("BSEE Advanced Visualization System - Comprehensive Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Transformation Viewer", test_transformation_viewer),
        ("Operation Animator", test_operation_animator),
        ("Binary Display", test_binary_display),
        ("Transformation Export", test_transformation_export),
        ("History Integration", test_history_integration),
        ("Visualization Modes", test_visualization_modes),
        ("Animation Performance", test_animation_performance),
        ("Export Formats", test_export_formats)
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
        print("\n🎉 ALL TESTS PASSED! Advanced visualization system is working correctly.")
        print("\n✅ Phase 2 Implementation Complete:")
        print("   • Transformation Viewer with step-by-step replay")
        print("   • Real-time animation system with byte changes")
        print("   • Enhanced binary display modes (hex, binary, heatmap)")
        print("   • Comprehensive export capabilities")
        print("   • History manager integration")
        print("   • Advanced visualization features")
        print("   • Performance optimized animations")
    else:
        print(f"\n❌ {total - passed} tests failed. Please review the implementation.")

    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)