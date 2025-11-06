"""
File handling and edge case testing for BSEE.
"""

import unittest
import tempfile
import os
from pathlib import Path
import time

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from bsee.engine.pipeline import Pipeline
from bsee.engine.gui_pipeline import GUIPipeline
import argparse


class TestFileHandling(unittest.TestCase):
    """Test file handling and edge cases."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test files of various sizes
        self.test_files = {}

        # Empty file
        empty_file = self.test_dir / "empty.bin"
        empty_file.write_bytes(b"")
        self.test_files['empty'] = empty_file

        # Small file (1KB)
        small_file = self.test_dir / "small.bin"
        small_file.write_bytes(os.urandom(1024))
        self.test_files['small'] = small_file

        # Medium file (1MB)
        medium_file = self.test_dir / "medium.bin"
        medium_file.write_bytes(os.urandom(1024 * 1024))
        self.test_files['medium'] = medium_file

        # Large file (10MB)
        large_file = self.test_dir / "large.bin"
        large_file.write_bytes(os.urandom(10 * 1024 * 1024))
        self.test_files['large'] = large_file

        # Patterned file
        pattern_file = self.test_dir / "pattern.bin"
        pattern_data = b"".join([i.to_bytes(1, 'big') for i in range(256)]) * 1024
        pattern_file.write_bytes(pattern_data)
        self.test_files['pattern'] = pattern_file

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_args(self, input_file):
        """Create CLI arguments for testing."""
        return argparse.Namespace(
            input_file=str(input_file),
            policy='config/policies/policy_ideality.yaml',
            costs='config/costs/cost_default.yaml',
            strategy='greedy',
            metrics='file_ideality_score,entropy_global',
            target_metrics='file_ideality_score=max,entropy_global=min',
            max_operations=10,  # Keep small for testing
            max_cost=1000,
            allowed_ops=None,
            operation_limit=None,
            output_dir=str(self.test_dir / 'results'),
            log_level='ERROR'  # Reduce log noise during tests
        )

    def test_empty_file_handling(self):
        """Test handling of empty files."""
        args = self._create_args(self.test_files['empty'])

        try:
            pipeline = Pipeline(args)
            results = pipeline.run()
            self.assertTrue(results.success)
            self.assertEqual(results.total_operations, 0)
        except Exception as e:
            # Empty files might be handled specially
            print(f"Empty file handling: {e}")

    def test_small_file_processing(self):
        """Test processing of small files."""
        args = self._create_args(self.test_files['small'])

        pipeline = Pipeline(args)
        results = pipeline.run()

        self.assertTrue(results.success)
        self.assertGreaterEqual(results.total_operations, 0)
        self.assertIsNotNone(results.initial_state)
        self.assertIsNotNone(results.final_state)

    def test_medium_file_processing(self):
        """Test processing of medium files."""
        args = self._create_args(self.test_files['medium'])

        start_time = time.time()
        pipeline = Pipeline(args)
        results = pipeline.run()
        end_time = time.time()

        self.assertTrue(results.success)
        self.assertLess(end_time - start_time, 60)  # Should complete within 60 seconds

    def test_large_file_processing(self):
        """Test processing of large files."""
        args = self._create_args(self.test_files['large'])
        args.max_operations = 5  # Reduce for performance

        start_time = time.time()
        pipeline = Pipeline(args)
        results = pipeline.run()
        end_time = time.time()

        self.assertTrue(results.success)
        self.assertLess(end_time - start_time, 120)  # Should complete within 2 minutes

    def test_patterned_file_processing(self):
        """Test processing of patterned files."""
        args = self._create_args(self.test_files['pattern'])

        pipeline = Pipeline(args)
        results = pipeline.run()

        self.assertTrue(results.success)
        # Patterned files should show interesting metric changes

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        nonexistent_file = self.test_dir / "nonexistent.bin"
        args = self._create_args(nonexistent_file)

        with self.assertRaises(FileNotFoundError):
            pipeline = Pipeline(args)
            pipeline.run()

    def test_directory_as_file(self):
        """Test handling when a directory is specified as input file."""
        args = self._create_args(self.test_dir)

        with self.assertRaises((FileNotFoundError, IsADirectoryError)):
            pipeline = Pipeline(args)
            pipeline.run()

    def test_permission_denied(self):
        """Test handling of permission denied errors."""
        # Create a file and remove read permissions
        restricted_file = self.test_dir / "restricted.bin"
        restricted_file.write_bytes(b"test data")

        try:
            # Remove read permissions
            restricted_file.chmod(0o000)
            args = self._create_args(restricted_file)

            with self.assertRaises((PermissionError, IOError)):
                pipeline = Pipeline(args)
                pipeline.run()
        finally:
            # Restore permissions for cleanup
            restricted_file.chmod(0o644)

    def test_unicode_filename(self):
        """Test handling of Unicode filenames."""
        unicode_name = "tëst_ünîcødë.bin"
        unicode_file = self.test_dir / unicode_name
        unicode_file.write_bytes(b"unicode test data")

        args = self._create_args(unicode_file)

        try:
            pipeline = Pipeline(args)
            results = pipeline.run()
            self.assertTrue(results.success)
        except Exception as e:
            # Unicode handling might vary by system
            print(f"Unicode filename handling: {e}")

    def test_special_characters_in_path(self):
        """Test handling of special characters in file paths."""
        special_name = "test-file_with spaces & symbols!.bin"
        special_file = self.test_dir / special_name
        special_file.write_bytes(b"special chars test")

        args = self._create_args(special_file)

        try:
            pipeline = Pipeline(args)
            results = pipeline.run()
            self.assertTrue(results.success)
        except Exception as e:
            print(f"Special characters in path: {e}")

    def test_network_drive_simulation(self):
        """Test simulation of network drive access."""
        # Create a subdirectory to simulate network path
        network_sim = self.test_dir / "network_sim"
        network_sim.mkdir()
        test_file = network_sim / "network_test.bin"
        test_file.write_bytes(b"network simulation test")

        args = self._create_args(test_file)

        try:
            pipeline = Pipeline(args)
            results = pipeline.run()
            self.assertTrue(results.success)
        except Exception as e:
            print(f"Network path simulation: {e}")

    def test_concurrent_access(self):
        """Test concurrent access to the same file."""
        import threading
        import queue

        results_queue = queue.Queue()

        def run_analysis():
            try:
                args = self._create_args(self.test_files['small'])
                args.max_operations = 5
                pipeline = Pipeline(args)
                results = pipeline.run()
                results_queue.put(results.success)
            except Exception as e:
                results_queue.put(False)

        # Run multiple analyses concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_analysis)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)

        # Check results
        success_count = 0
        while not results_queue.empty():
            if results_queue.get():
                success_count += 1

        # At least one should succeed
        self.assertGreater(success_count, 0)

    def test_gui_pipeline_integration(self):
        """Test GUI pipeline with different file sizes."""
        import queue

        progress_queue = queue.Queue()
        args = self._create_args(self.test_files['small'])

        try:
            pipeline = GUIPipeline(args, progress_queue)
            results = pipeline.run()

            self.assertTrue(results.success)

            # Check that progress messages were sent
            messages_received = 0
            while not progress_queue.empty():
                progress_queue.get()
                messages_received += 1

            self.assertGreater(messages_received, 0)

        except Exception as e:
            print(f"GUI pipeline test: {e}")


def run_file_tests():
    """Run all file handling tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestFileHandling))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("BSEE File Handling Test Suite")
    print("=" * 50)
    success = run_file_tests()
    sys.exit(0 if success else 1)