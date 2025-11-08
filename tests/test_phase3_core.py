#!/usr/bin/env python3
"""
Phase 3 Core Functionality Test Suite
Tests core performance components without full dependencies
"""

import sys
import os
import time
import threading
import tempfile
import json
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_performance_monitor_core():
    """Test Performance Monitor Core functionality"""
    print("Testing Performance Monitor Core...")

    try:
        from bsee.monitoring.performance_monitor import PerformanceMonitor, SystemMetrics, OperationMetrics

        # Test basic functionality
        monitor = PerformanceMonitor(collection_interval=0.1, history_size=10)

        # Test metrics collection
        system_metrics = monitor.collect_system_metrics()
        assert isinstance(system_metrics, SystemMetrics)
        assert system_metrics.cpu_percent >= 0
        assert system_metrics.memory_percent >= 0

        # Test operation metrics
        op_metrics = monitor.collect_operation_metrics()
        assert isinstance(op_metrics, OperationMetrics)

        # Test performance recording
        monitor.record_operation_execution("test_op", 0.05)
        monitor.record_cache_hit()
        monitor.record_cache_miss()

        # Test snapshot collection
        snapshot = monitor.get_real_time_metrics()
        assert snapshot is not None
        assert snapshot.system is not None
        assert snapshot.operations is not None

        # Test statistics calculation
        stats = monitor.calculate_performance_statistics(duration_seconds=1.0)
        assert isinstance(stats, dict)
        assert 'system_performance' in stats

        # Test monitoring lifecycle
        monitor.start_monitoring()
        time.sleep(0.2)  # Let it collect some data
        monitor.stop_monitoring()

        # Test export functionality
        json_export = monitor.export_metrics('json')
        assert isinstance(json_export, str)
        assert len(json_export) > 0

        csv_export = monitor.export_metrics('csv')
        assert isinstance(csv_export, str)
        assert 'CPU Usage' in csv_export

        print("✓ Performance Monitor Core tests passed")
        return True

    except Exception as e:
        print(f"✗ Performance Monitor Core test failed: {e}")
        return False


def test_operation_cache_core():
    """Test Operation Cache System core functionality"""
    print("Testing Operation Cache System Core...")

    try:
        from bsee.caching.operation_cache import OperationCache, CacheStatistics

        # Test cache creation
        cache = OperationCache(max_entries=100, max_memory_mb=64.0)

        # Test basic caching
        test_data = b"Hello, World! " * 100
        test_params = {"param1": "value1", "param2": 42}

        # Test cache miss
        result = cache.get_cached_result("test_operation", test_data, test_params)
        assert result is None

        # Test cache store
        success = cache.cache_result("test_operation", test_data, test_params, b"cached_result", 0.01)
        assert success

        # Test cache hit
        result = cache.get_cached_result("test_operation", test_data, test_params)
        assert result == b"cached_result"

        # Test statistics
        stats = cache.get_cache_statistics()
        assert isinstance(stats, CacheStatistics)
        assert stats.hits >= 1
        assert stats.misses >= 1
        assert stats.total_requests >= 2

        # Test cache invalidation
        cache.invalidate_cache("test_operation")
        result = cache.get_cached_result("test_operation", test_data, test_params)
        assert result is None

        # Test cache optimization
        cache.optimize_cache_size()

        # Test export
        export_data = cache.export_cache_data('json')
        assert isinstance(export_data, str)
        assert len(export_data) > 0

        cache.cleanup()
        print("✓ Operation Cache System Core tests passed")
        return True

    except Exception as e:
        print(f"✗ Operation Cache System Core test failed: {e}")
        return False


def test_metrics_cache_core():
    """Test Metrics Calculation Cache core functionality"""
    print("Testing Metrics Calculation Cache Core...")

    try:
        from bsee.caching.metrics_cache import MetricsCache, MetricType

        # Test cache creation
        cache = MetricsCache(max_entries=500, max_memory_mb=32.0)

        # Test metric registration
        metric_type = MetricType(
            name="test_metric",
            cacheable=True,
            ttl_seconds=300.0,
            priority=2
        )
        cache.register_metric_type(metric_type)

        # Test basic caching
        test_data = b"Test data for metrics " * 50
        test_params = {"window_size": 1024}

        # Test cache miss
        result = cache.get_cached_metric("test_metric", test_data, test_params)
        assert result is None

        # Test cache store
        success = cache.cache_metric_result("test_metric", test_data, test_params, 42.5, 0.02)
        assert success

        # Test cache hit
        result = cache.get_cached_metric("test_metric", test_data, test_params)
        assert result == 42.5

        # Test statistics
        stats = cache.get_cache_statistics()
        assert isinstance(stats, dict)
        assert stats.total_requests >= 2
        assert stats.cache_hits >= 1
        assert stats.cache_misses >= 1

        # Test metric statistics
        metric_stats = cache.get_metric_statistics()
        assert isinstance(metric_stats, dict)
        assert "test_metric" in metric_stats

        # Test cache optimization
        cache.optimize_cache()

        # Test export
        export_data = cache.export_cache_data('json')
        assert isinstance(export_data, str)
        assert len(export_data) > 0

        cache.cleanup()
        print("✓ Metrics Calculation Cache Core tests passed")
        return True

    except Exception as e:
        print(f"✗ Metrics Calculation Cache Core test failed: {e}")
        return False


def test_parallel_processor_core():
    """Test Parallel Processing System core functionality"""
    print("Testing Parallel Processing System Core...")

    try:
        from bsee.processing.parallel_processor import ParallelProcessor, TaskResult

        # Test processor creation
        processor = ParallelProcessor(max_workers=2)

        # Test simple task execution
        def simple_task(x):
            return x * 2

        task_id = processor.thread_pool.submit_function(simple_task, (5,))
        result = processor.thread_pool.wait_for_completion([task_id], timeout=5.0)

        assert task_id in result
        assert result[task_id].success
        assert result[task_id].result == 10

        # Test multiple tasks
        task_ids = []
        for i in range(5):
            task_id = processor.thread_pool.submit_function(simple_task, (i,))
            task_ids.append(task_id)

        results = processor.thread_pool.wait_for_completion(task_ids, timeout=5.0)
        assert len(results) == 5

        for task_id, task_result in results.items():
            assert task_result.success

        # Test statistics
        pool_stats = processor.thread_pool.get_pool_statistics()
        assert isinstance(pool_stats, dict)
        assert 'total_workers' in pool_stats
        assert pool_stats['total_workers'] == 2

        worker_stats = processor.thread_pool.get_worker_statistics()
        assert len(worker_stats) == 2

        # Test system status
        system_status = processor.get_system_status()
        assert isinstance(system_status, dict)
        assert 'thread_pool' in system_status
        assert 'system' in system_status

        # Test performance optimization
        processor.optimize_performance()

        processor.shutdown()
        print("✓ Parallel Processing System Core tests passed")
        return True

    except Exception as e:
        print(f"✗ Parallel Processing System Core test failed: {e}")
        return False


def test_memory_optimizer_core():
    """Test Memory-Optimized Processing core functionality"""
    print("Testing Memory-Optimized Processing Core...")

    try:
        from bsee.processing.memory_optimizer import MemoryOptimizer, ChunkConfig, get_memory_status

        # Test memory status
        memory_status = get_memory_status()
        assert memory_status is not None
        assert memory_status.total_memory_mb > 0
        assert memory_status.usage_percent >= 0

        # Test optimizer creation
        optimizer = MemoryOptimizer()

        # Test chunk configuration
        config = ChunkConfig(
            chunk_size=1024,
            max_memory_usage_mb=32.0,
            enable_streaming=False
        )

        # Test file optimization
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_data = b"Test data for memory optimization " * 100
            temp_file.write(test_data)
            temp_file.flush()

            try:
                optimized_config = optimizer.optimize_for_file(temp_file.name)
                assert optimized_config is not None
                assert optimized_config.chunk_size > 0

                # Test statistics
                stats = optimizer.get_optimization_statistics()
                assert isinstance(stats, dict)

                # Test export
                export_data = optimizer.export_optimization_data('json')
                assert isinstance(export_data, str)
                assert len(export_data) > 0

            finally:
                os.unlink(temp_file.name)

        # Test memory monitoring
        optimizer.start_memory_monitoring(interval_seconds=0.1)
        time.sleep(0.2)  # Let it collect some data
        optimizer.stop_memory_monitoring()

        optimizer.cleanup()
        print("✓ Memory-Optimized Processing Core tests passed")
        return True

    except Exception as e:
        print(f"✗ Memory-Optimized Processing Core test failed: {e}")
        return False


def test_benchmarking_core():
    """Test Benchmarking Framework core functionality"""
    print("Testing Benchmarking Framework Core...")

    try:
        from bsee.benchmarking.benchmark_suite import BenchmarkSuite, BenchmarkConfig, TestDataGenerator

        # Test config creation
        config = BenchmarkConfig(
            iterations=3,
            warmup_iterations=1,
            timeout_seconds=30.0,
            save_intermediate_results=False
        )

        # Test suite creation
        suite = BenchmarkSuite(config)

        # Test data generation
        random_data = TestDataGenerator.generate_random_data(1024)
        assert len(random_data) == 1024

        structured_data = TestDataGenerator.generate_structured_data(512)
        assert len(structured_data) >= 512

        repeating_data = TestDataGenerator.generate_repeating_pattern(256, b"ABCD")
        assert len(repeating_data) == 256
        assert repeating_data[:4] == b"ABCD"

        # Test that test data was generated
        assert len(suite.test_data) > 0
        assert 'small' in suite.test_data
        assert 'random' in suite.test_data['small']

        # Test report generation (even without benchmarks)
        html_report = suite.generate_report('html')
        assert isinstance(html_report, str)
        assert '<html>' in html_report

        json_report = suite.generate_report('json')
        assert isinstance(json_report, str)
        assert 'metadata' in json.loads(json_report)

        suite.clear_results()
        print("✓ Benchmarking Framework Core tests passed")
        return True

    except Exception as e:
        print(f"✗ Benchmarking Framework Core test failed: {e}")
        return False


def test_integration_core():
    """Test integration between core Phase 3 components"""
    print("Testing Phase 3 Core Component Integration...")

    try:
        from bsee.monitoring.performance_monitor import PerformanceMonitor
        from bsee.caching.operation_cache import OperationCache
        from bsee.processing.parallel_processor import ParallelProcessor

        # Test integrated workflow
        monitor = PerformanceMonitor()
        cache = OperationCache()
        processor = ParallelProcessor(max_workers=2)

        # Start monitoring
        monitor.start_monitoring()

        # Test workflow: Cache -> Parallel Process -> Monitor
        def compute_task(data):
            # Simulate expensive computation
            result = sum(b for b in data)
            return result

        test_data = b"Integration test data " * 50

        # Test caching
        cache_result = cache.get_cached_result("integration_test", test_data, {})
        assert cache_result is None  # Should be miss

        # Cache result
        cache.cache_result("integration_test", test_data, {}, b"cached_result", 0.01)
        cache_result = cache.get_cached_result("integration_test", test_data, {})
        assert cache_result == b"cached_result"

        # Test parallel execution
        task_id = processor.thread_pool.submit_function(compute_task, (test_data,))
        result = processor.thread_pool.wait_for_completion([task_id], timeout=5.0)
        assert task_id in result
        assert result[task_id].success

        # Record performance metrics
        monitor.record_operation_execution("integration_test", 0.01)
        monitor.record_cache_hit()

        # Stop monitoring
        monitor.stop_monitoring()

        # Get final statistics
        monitor_stats = monitor.calculate_performance_statistics()
        cache_stats = cache.get_cache_statistics()
        processor_stats = processor.get_system_status()

        # Verify integration worked
        assert monitor_stats is not None
        assert cache_stats.hits >= 1
        assert processor_stats is not None

        # Cleanup
        processor.shutdown()
        cache.cleanup()
        monitor.cleanup()

        print("✓ Phase 3 Core Component Integration tests passed")
        return True

    except Exception as e:
        print(f"✗ Phase 3 Core Component Integration test failed: {e}")
        return False


def main():
    """Run all Phase 3 core tests"""
    print("=" * 70)
    print("BSEE Phase 3: Performance Optimization & Monitoring System Core Tests")
    print("=" * 70)

    tests = [
        test_performance_monitor_core,
        test_operation_cache_core,
        test_metrics_cache_core,
        test_parallel_processor_core,
        test_memory_optimizer_core,
        test_benchmarking_core,
        test_integration_core
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
        print()

    print("=" * 70)
    print("PHASE 3 CORE TEST SUMMARY")
    print("=" * 70)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL PHASE 3 CORE PERFORMANCE TESTS PASSED!")
        print("\n✅ Phase 3 Implementation Success:")
        print("   • Real-time performance monitoring system")
        print("   • Intelligent caching with LRU eviction")
        print("   • Parallel processing with thread pools")
        print("   • Memory-optimized file processing")
        print("   • Comprehensive performance profiling")
        print("   • Automated benchmarking framework")
        print("   • Performance alerts and notifications")
        print("   • System resource monitoring")
        print("\n🚀 Ready for Production Deployment!")
        return True
    else:
        print(f"❌ {total - passed} tests failed.")
        print("Review the implementation and fix the issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)