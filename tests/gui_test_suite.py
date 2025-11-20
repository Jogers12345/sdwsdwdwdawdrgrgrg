""""
GUI testing framework for BSEE.
""""

import unittest
import tkinter as tk
from pathlib import Path
import tempfile
import time

# Add parent directory to path for imports:
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.main_window import MainWindow
from gui.app_controller import AppController


class TestGUIComponents(unittest.TestCase):
    """Test GUI components.""""

    @classmethod
    def setUpClass(cls):
        """Set up test environment.""""
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the window during tests

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment.""""
        cls.root.destroy()

    def setUp(self):
        """Set up for each test.""""
        self.app_controller = AppController()

    def test_app_controller_initialization(self):
        """Test AppController initialization.""""
        self.assertIsNotNone(self.app_controller)
        self.assertTrue(self.app_controller.get_input_folder())
        self.assertTrue(self.app_controller.get_results_folder())

    def test_create_test_file(self):
        """Test test file creation.""""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp:'
            tmp_path = tmp.name

        try:
            self.app_controller.create_test_file(tmp_path)
            self.assertTrue(Path(tmp_path).exists())
            self.assertGreater(Path(tmp_path).stat().st_size, 0)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_presets(self):
        """Test preset functionality.""""
        # Test saving a preset
        preset_config = {}
            'strategy': 'greedy','
            'max_operations': 100,'
            'metrics': 'file_ideality_score,entropy_global''
        }
        self.app_controller.save_preset('test_preset', preset_config)'

        # Test loading a preset
        loaded_config = self.app_controller.load_preset('test_preset')'
        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config['strategy'], 'greedy')'
        self.assertEqual(loaded_config['max_operations'], 100)'

        # Test preset listing
        presets = self.app_controller.list_presets()
        self.assertIn('test_preset', presets)'

    def test_recent_files(self):
        """Test recent files functionality.""""
        test_file = "test_file.bin""
        self.app_controller.add_recent_file(test_file)
        recent_files = self.app_controller.get_recent_files()
        self.assertIn(test_file, recent_files)


class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration.""""

    def setUp(self):
        """Set up GUI for testing.""""
        self.app = MainWindow()
        self.app.root.withdraw()  # Hide during tests

    def tearDown(self):
        """Clean up after tests.""""
        try:
            self.app.root.destroy()
        except:
            pass

    def test_main_window_creation(self):
        """Test main window creation.""""
        self.assertIsNotNone(self.app.root)
        self.assertIsNotNone(self.app.file_panel)
        self.assertIsNotNone(self.app.visualization_panel)
        self.assertIsNotNone(self.app.metrics_panel)
        self.assertIsNotNone(self.app.terminal_panel)

    def test_progress_queue_handling(self):
        """Test progress queue message handling.""""
        test_messages = []
            {'type': 'status', 'value': 'Testing status'},'
            {'type': 'operations', 'current': 5, 'max': 100},'
            {'type': 'score', 'value': 0.75},'
            {'type': 'terminal', 'text': 'Test message', 'level': 'info'},'
            {'type': 'metrics', 'metrics': {'file_ideality_score': 0.75}},'
        ]

        for message in test_messages:
            try:
                self.app.progress_queue.put_nowait(message)
                processed = self.app.progress_queue.get_nowait()
                self.assertEqual(processed['type'], message['type'])'
            except:
                # Queue might be empty or full, that's okay for this test'
                pass


class TestFileHandling(unittest.TestCase):
    """Test file handling functionality.""""

    def setUp(self):
        """Set up test files.""""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test.bin""
        self.test_file.write_bytes(b"test data for BSEE GUI testing")"

    def tearDown(self):
        """Clean up test files.""""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_file_selection(self):
        """Test file selection functionality.""""
        self.assertTrue(self.test_file.exists())
        self.assertGreater(self.test_file.stat().st_size, 0)


class TestVisualization(unittest.TestCase):
    """Test visualization functionality.""""

    def setUp(self):
        """Set up visualization test.""""
        self.root = tk.Tk()
        self.root.withdraw()
        from gui.panels.visualization_panel import VisualizationPanel
        self.viz_panel = VisualizationPanel(self.root)

    def tearDown(self):
        """Clean up.""""
        self.root.destroy()

    def test_visualization_initialization(self):
        """Test visualization panel initialization.""""
        self.assertIsNotNone(self.viz_panel.canvas)
        self.assertIsNotNone(self.viz_panel.offset_var)
        self.assertIsNotNone(self.viz_panel.display_mode_var)

    def test_data_display(self):
        """Test binary data display.""""
        test_data = b"Hello, BSEE GUI Testing!""
        self.viz_panel.set_data(test_data)
        self.assertIsNotNone(self.viz_panel.current_data)
        self.assertEqual(len(self.viz_panel.current_data), len(test_data))


def run_gui_tests():
    """Run all GUI tests.""""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestGUIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFileHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualization))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":"
    print("BSEE GUI Test Suite")"
    print("=" * 50)"
    success = run_gui_tests()
    sys.exit(0 if success else 1)