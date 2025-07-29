import unittest
from time_anomaly import anomaly_detector

class TestTimeAnomalyDetector(unittest.TestCase):
    def test_constant_stream_no_anomaly(self):
        # Provide a constant stream where no point should be flagged as an anomaly.
        data_stream = iter([10] * 50)
        results = list(anomaly_detector(data_stream, N=10, M=5, k=2.0))
        for dp, is_anom, ewma, threshold in results:
            self.assertIsInstance(dp, (int, float))
            self.assertIsInstance(ewma, (int, float))
            self.assertIsInstance(threshold, (int, float))
            # In a constant stream, even if standard deviation is zero,
            # the detector should not flag any data point as an anomaly.
            self.assertFalse(is_anom, f"Data point {dp} incorrectly flagged as anomaly.")

    def test_spike_detection(self):
        # A stream with a sudden spike should detect the spike as an anomaly.
        data = [10] * 20 + [50] + [10] * 10
        data_stream = iter(data)
        results = list(anomaly_detector(data_stream, N=10, M=5, k=2.0))
        spike_detected = False
        for dp, is_anom, ewma, threshold in results:
            if dp == 50:
                spike_detected = is_anom
        self.assertTrue(spike_detected, "Spike data point was not flagged as anomaly.")

    def test_missing_values(self):
        # Test that the detector handles missing values (None) gracefully.
        data = [10, None, 10, 10, None, 10, 10]
        data_stream = iter(data)
        try:
            results = list(anomaly_detector(data_stream, N=10, M=5, k=2.0))
            # Ensure that each yielded tuple is valid and no unexpected exceptions occur.
            for dp, is_anom, ewma, threshold in results:
                self.assertTrue(is_anom in [True, False])
                self.assertIsInstance(ewma, (int, float))
                self.assertIsInstance(threshold, (int, float))
        except Exception as e:
            self.fail(f"anomaly_detector raised an exception with missing values: {e}")

    def test_initial_phase(self):
        # When there are insufficient data points to fill the window,
        # the detector should still produce outputs without flagging anomalies erroneously.
        data = [15, 15, 15]
        data_stream = iter(data)
        results = list(anomaly_detector(data_stream, N=10, M=5, k=2.0))
        for dp, is_anom, ewma, threshold in results:
            self.assertFalse(is_anom, f"Data point {dp} in the initial phase incorrectly flagged as anomaly.")
            self.assertIsInstance(ewma, (int, float))
            self.assertIsInstance(threshold, (int, float))

    def test_alternating_pattern(self):
        # An alternating pattern may have borderline cases. This test confirms that the function runs without error.
        data = [10, 20, 10, 20, 10, 20, 10, 20, 10, 20]
        data_stream = iter(data)
        results = list(anomaly_detector(data_stream, N=10, M=5, k=1.5))
        # Verify that each result tuple has valid types.
        for dp, is_anom, ewma, threshold in results:
            self.assertIsInstance(dp, (int, float))
            self.assertIsInstance(is_anom, bool)
            self.assertIsInstance(ewma, (int, float))
            self.assertIsInstance(threshold, (int, float))

if __name__ == "__main__":
    unittest.main()