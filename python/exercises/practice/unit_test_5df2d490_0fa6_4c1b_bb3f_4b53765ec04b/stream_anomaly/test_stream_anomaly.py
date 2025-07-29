import unittest
import random
import numpy as np
from stream_anomaly import detect_anomalies

class TestStreamAnomaly(unittest.TestCase):
    def setUp(self):
        self.normal_stream = iter(np.random.normal(0, 1, 1000))
        self.seasonal_stream = self._generate_seasonal_data(1000)
        self.spike_stream = self._generate_spike_data(1000)
        self.missing_data_stream = self._generate_missing_data(1000)

    def _generate_seasonal_data(self, length):
        base = np.sin(np.linspace(0, 10*np.pi, length))
        noise = np.random.normal(0, 0.1, length)
        return iter(base + noise)

    def _generate_spike_data(self, length):
        data = np.random.normal(0, 1, length)
        spikes = random.sample(range(length), 10)
        for i in spikes:
            data[i] += 10 * random.random()
        return iter(data)

    def _generate_missing_data(self, length):
        data = np.random.normal(0, 1, length)
        missing = random.sample(range(length), 50)
        for i in missing:
            data[i] = None
        return iter(data)

    def test_normal_stream(self):
        detector = detect_anomalies(self.normal_stream)
        anomalies = sum(1 for _ in range(1000) if next(detector))
        self.assertLess(anomalies, 50, "Too many false positives in normal data")

    def test_seasonal_stream(self):
        detector = detect_anomalies(self.seasonal_stream)
        anomalies = sum(1 for _ in range(1000) if next(detector))
        self.assertLess(anomalies, 50, "Failed to handle seasonality")

    def test_spike_detection(self):
        detector = detect_anomalies(self.spike_stream)
        anomalies = [i for i in range(1000) if next(detector)]
        self.assertGreaterEqual(len(anomalies), 8, "Failed to detect spikes")
        self.assertLessEqual(len(anomalies), 15, "Too many false positives in spike data")

    def test_missing_data(self):
        detector = detect_anomalies(self.missing_data_stream)
        for _ in range(1000):
            try:
                next(detector)
            except Exception as e:
                self.fail(f"Failed to handle missing data: {str(e)}")

    def test_real_time_performance(self):
        import time
        start = time.time()
        detector = detect_anomalies(self.normal_stream)
        for _ in range(1000):
            next(detector)
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.1, "Processing too slow for real-time")

    def test_memory_usage(self):
        import tracemalloc
        tracemalloc.start()
        detector = detect_anomalies(self.normal_stream)
        for _ in range(1000):
            next(detector)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertLess(peak / 1024, 500, "Memory usage too high")

if __name__ == '__main__':
    unittest.main()