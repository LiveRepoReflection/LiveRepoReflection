import unittest
import time
from stream_fusion import process_stream

class StreamFusionTest(unittest.TestCase):
    def test_empty_stream(self):
        # Test with an empty stream of events. Expect no anomalies.
        events = []
        anomalies = process_stream(iter(events), window_size=3, k_threshold=2)
        self.assertEqual(anomalies, [])

    def test_no_anomaly(self):
        # Test with a stream that should not produce any anomalies.
        events = [
            (1, 10.0),
            (2, 11.0),
            (3, 9.0),
            (4, 10.5),
            (5, 10.2)
        ]
        anomalies = process_stream(iter(events), window_size=3, k_threshold=2)
        self.assertEqual(anomalies, [])

    def test_single_anomaly(self):
        # Test with a stream where a single event is an outlier.
        # Using a sliding window of size 3 and a k_threshold of 1.
        # For the window containing events (10.0, 10.0, 30.0), the event (30.0) should be flagged.
        events = [
            (1, 10.0),
            (2, 10.0),
            (3, 30.0),
            (4, 11.0),
            (5, 12.0)
        ]
        anomalies = process_stream(iter(events), window_size=3, k_threshold=1)
        expected_anomalies = [(3, 30.0)]
        self.assertEqual(anomalies, expected_anomalies)

    def test_buffer_eviction(self):
        # Test to ensure the buffer and sliding window behave correctly when eviction occurs.
        # Using a small window size to force eviction on every new event.
        events = [
            (1, 5.0),
            (2, 6.0),
            (3, 7.0),
            (4, 8.0)
        ]
        # For window size 2 and a low k_threshold, each new event (after filling the window)
        # is likely to be an anomaly if the deviation is higher than allowed.
        anomalies = process_stream(iter(events), window_size=2, k_threshold=0.5)
        expected_anomalies = [(2, 6.0), (3, 7.0), (4, 8.0)]
        self.assertEqual(anomalies, expected_anomalies)

    def test_high_volume_data(self):
        # Test the performance and correctness on a high-volume data stream.
        events = []
        num_events = 10000
        # Create a steadily increasing value stream.
        for ts in range(1, num_events + 1):
            value = ts * 0.1
            events.append((ts, value))
        # Insert a significant anomaly in the middle of the stream.
        events[4999] = (5000, 1000.0)
        
        start_time = time.time()
        anomalies = process_stream(iter(events), window_size=50, k_threshold=2)
        duration = time.time() - start_time
        
        # Verify the anomaly at timestamp=5000 is detected.
        self.assertIn((5000, 1000.0), anomalies)
        # Verify anomalies are reported in chronological order.
        timestamps = [ts for (ts, val) in anomalies]
        self.assertEqual(timestamps, sorted(timestamps))
        # Ensure processing time per event is within a reasonable limit.
        avg_time_per_event = duration / num_events
        self.assertLess(avg_time_per_event, 0.005)

if __name__ == '__main__':
    unittest.main()