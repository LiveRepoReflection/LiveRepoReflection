import unittest
import threading
import time
import statistics
import math
from stream_analyzer import ConcurrentStreamAnalyzer

class TestConcurrentStreamAnalyzer(unittest.TestCase):
    def setUp(self):
        # Use a small window size for some tests and larger for concurrency.
        self.window_size = 5
        self.num_sources = 3
        self.analyzer = ConcurrentStreamAnalyzer(window_size=self.window_size, num_sources=self.num_sources)

    def test_empty_window_statistics(self):
        stats = self.analyzer.get_statistics()
        self.assertIsNone(stats["mean"])
        self.assertIsNone(stats["median"])
        self.assertIsNone(stats["std_dev"])
        self.assertIsNone(stats["min"])
        self.assertIsNone(stats["max"])

    def test_invalid_source_id(self):
        with self.assertRaises(ValueError):
            self.analyzer.process_data(-1, 1.0)
        with self.assertRaises(ValueError):
            self.analyzer.process_data(self.num_sources, 1.0)

    def test_single_thread_sequential_inputs(self):
        # Insert less than window_size elements.
        values = [1.0, 2.0, 3.0]
        for val in values:
            self.analyzer.process_data(0, val)
        stats = self.analyzer.get_statistics()
        expected_mean = statistics.mean(values)
        expected_median = statistics.median(values)
        # For stdev, if len(values)<2, it should be None. In this case, len(values)==3.
        expected_std_dev = statistics.stdev(values)
        self.assertAlmostEqual(stats["mean"], expected_mean, places=5)
        self.assertAlmostEqual(stats["median"], expected_median, places=5)
        self.assertAlmostEqual(stats["std_dev"], expected_std_dev, places=5)
        self.assertEqual(stats["min"], min(values))
        self.assertEqual(stats["max"], max(values))

    def test_sliding_window_eviction(self):
        # Insert more than window_size elements and ensure eviction of oldest ones.
        data_points = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        for idx, val in enumerate(data_points):
            source_id = idx % self.num_sources
            self.analyzer.process_data(source_id, val)
        # The sliding window should now contain the last 'window_size' data points.
        expected_window = data_points[-self.window_size:]
        stats = self.analyzer.get_statistics()
        expected_mean = statistics.mean(expected_window)
        expected_median = statistics.median(expected_window)
        expected_std_dev = statistics.stdev(expected_window) if len(expected_window) > 1 else None
        self.assertAlmostEqual(stats["mean"], expected_mean, places=5)
        self.assertAlmostEqual(stats["median"], expected_median, places=5)
        if expected_std_dev is None:
            self.assertIsNone(stats["std_dev"])
        else:
            self.assertAlmostEqual(stats["std_dev"], expected_std_dev, places=5)
        self.assertEqual(stats["min"], min(expected_window))
        self.assertEqual(stats["max"], max(expected_window))

    def test_concurrent_processing(self):
        # Use a larger window such that all inserted data remain.
        total_threads = 4
        numbers_per_thread = 25
        window_size = total_threads * numbers_per_thread  # exactly all numbers added will be in the window
        analyzer = ConcurrentStreamAnalyzer(window_size=window_size, num_sources=total_threads)
        
        # Prepare data for each thread:
        def worker(source_id, start, count):
            for i in range(start, start + count):
                analyzer.process_data(source_id, float(i))
                # A tiny sleep to encourage context switching.
                time.sleep(0.001)
        
        threads = []
        # For reproducibility, generate non-overlapping ranges for each thread.
        expected_data = []
        for t in range(total_threads):
            start = t * 100 + 1
            thread_values = list(range(start, start + numbers_per_thread))
            expected_data.extend(thread_values)
            thread = threading.Thread(target=worker, args=(t, start, numbers_per_thread))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Since total inserted equals window size, the window should contain all expected data.
        expected_mean = statistics.mean(expected_data)
        expected_median = statistics.median(expected_data)
        expected_std_dev = statistics.stdev(expected_data) if len(expected_data) > 1 else None
        expected_min = min(expected_data)
        expected_max = max(expected_data)

        stats = analyzer.get_statistics()
        self.assertAlmostEqual(stats["mean"], expected_mean, places=4)
        self.assertAlmostEqual(stats["median"], expected_median, places=4)
        if expected_std_dev is None:
            self.assertIsNone(stats["std_dev"])
        else:
            self.assertAlmostEqual(stats["std_dev"], expected_std_dev, places=4)
        self.assertEqual(stats["min"], expected_min)
        self.assertEqual(stats["max"], expected_max)

if __name__ == '__main__':
    unittest.main()