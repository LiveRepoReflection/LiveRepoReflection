import unittest
from unittest.mock import patch
import threading
import time
from event_kth import DistributedAggregator

class TestDistributedAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = DistributedAggregator(k=3, window_size=60)

    def test_initialization(self):
        self.assertEqual(self.aggregator.k, 3)
        self.assertEqual(self.aggregator.window_size, 60)

    def test_basic_aggregation(self):
        # Add events for a single metric
        events = [
            {"timestamp": 1678886400, "worker_id": "worker1", "metric_name": "CPU_Usage", "metric_value": 25.5},
            {"timestamp": 1678886410, "worker_id": "worker2", "metric_name": "CPU_Usage", "metric_value": 30.2},
            {"timestamp": 1678886420, "worker_id": "worker1", "metric_name": "CPU_Usage", "metric_value": 28.1},
            {"timestamp": 1678886430, "worker_id": "worker3", "metric_name": "CPU_Usage", "metric_value": 32.8},
            {"timestamp": 1678886440, "worker_id": "worker2", "metric_name": "CPU_Usage", "metric_value": 27.9}
        ]
        
        for event in events:
            self.aggregator.process_event(event)
        
        # 3rd smallest of [25.5, 27.9, 28.1, 30.2, 32.8] is 28.1
        self.assertEqual(self.aggregator.get_kth_smallest("CPU_Usage"), 28.1)
        
        # Add one more event
        self.aggregator.process_event({
            "timestamp": 1678886450, 
            "worker_id": "worker4", 
            "metric_name": "CPU_Usage", 
            "metric_value": 26.7
        })
        
        # 3rd smallest of [25.5, 26.7, 27.9, 28.1, 30.2, 32.8] is 27.9
        self.assertEqual(self.aggregator.get_kth_smallest("CPU_Usage"), 27.9)

    def test_multiple_metrics(self):
        # Add events for multiple metrics
        events = [
            {"timestamp": 1678886400, "worker_id": "worker1", "metric_name": "CPU_Usage", "metric_value": 25.5},
            {"timestamp": 1678886410, "worker_id": "worker2", "metric_name": "Memory_Usage", "metric_value": 75.2},
            {"timestamp": 1678886420, "worker_id": "worker1", "metric_name": "CPU_Usage", "metric_value": 28.1},
            {"timestamp": 1678886430, "worker_id": "worker3", "metric_name": "Memory_Usage", "metric_value": 80.5},
            {"timestamp": 1678886440, "worker_id": "worker2", "metric_name": "Memory_Usage", "metric_value": 78.3}
        ]
        
        for event in events:
            self.aggregator.process_event(event)
        
        # Only 2 CPU_Usage metrics, need 3 for k=3
        self.assertEqual(self.aggregator.get_kth_smallest("CPU_Usage"), -1)
        
        # 3 Memory_Usage metrics, 3rd smallest (largest) is 80.5
        self.assertEqual(self.aggregator.get_kth_smallest("Memory_Usage"), 80.5)
        
        # Add one more CPU_Usage event
        self.aggregator.process_event({
            "timestamp": 1678886450, 
            "worker_id": "worker4", 
            "metric_name": "CPU_Usage", 
            "metric_value": 30.2
        })
        
        # Now we have 3 CPU_Usage metrics, 3rd smallest (largest) is 30.2
        self.assertEqual(self.aggregator.get_kth_smallest("CPU_Usage"), 30.2)

    def test_window_sliding(self):
        # Use a smaller window size for this test
        aggregator = DistributedAggregator(k=2, window_size=30)
        
        # Add events with timestamps within the window
        aggregator.process_event({
            "timestamp": 1678886400, 
            "worker_id": "worker1", 
            "metric_name": "CPU_Usage", 
            "metric_value": 25.5
        })
        
        aggregator.process_event({
            "timestamp": 1678886410, 
            "worker_id": "worker2", 
            "metric_name": "CPU_Usage", 
            "metric_value": 30.2
        })
        
        aggregator.process_event({
            "timestamp": 1678886420, 
            "worker_id": "worker3", 
            "metric_name": "CPU_Usage", 
            "metric_value": 28.1
        })
        
        # 2nd smallest of [25.5, 28.1, 30.2] is 28.1
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), 28.1)
        
        # Add event with timestamp that causes the first event to fall outside the window
        # Current time becomes 1678886440, window is [1678886410, 1678886440]
        aggregator.process_event({
            "timestamp": 1678886440, 
            "worker_id": "worker4", 
            "metric_name": "CPU_Usage", 
            "metric_value": 27.0
        })
        
        # 2nd smallest of [27.0, 28.1, 30.2] is 28.1 (25.5 is outside the window)
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), 28.1)
        
        # Add another event that pushes more events out of the window
        # Current time becomes 1678886450, window is [1678886420, 1678886450]
        aggregator.process_event({
            "timestamp": 1678886450, 
            "worker_id": "worker5", 
            "metric_name": "CPU_Usage", 
            "metric_value": 26.0
        })
        
        # 2nd smallest of [26.0, 27.0, 28.1] is 27.0 (25.5 and 30.2 are outside the window)
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), 27.0)

    def test_nonexistent_metric(self):
        # Should return -1 for a metric that doesn't exist
        self.assertEqual(self.aggregator.get_kth_smallest("NonExistentMetric"), -1)

    def test_fewer_than_k_values(self):
        # Add only 2 events when k=3
        events = [
            {"timestamp": 1678886400, "worker_id": "worker1", "metric_name": "CPU_Usage", "metric_value": 25.5},
            {"timestamp": 1678886410, "worker_id": "worker2", "metric_name": "CPU_Usage", "metric_value": 30.2}
        ]
        
        for event in events:
            self.aggregator.process_event(event)
        
        # Should return -1 when fewer than k values are available
        self.assertEqual(self.aggregator.get_kth_smallest("CPU_Usage"), -1)

    def test_same_timestamp_different_workers(self):
        # Events with the same timestamp from different workers
        events = [
            {"timestamp": 1678886400, "worker_id": "worker1", "metric_name": "CPU_Usage", "metric_value": 25.5},
            {"timestamp": 1678886400, "worker_id": "worker2", "metric_name": "CPU_Usage", "metric_value": 30.2},
            {"timestamp": 1678886400, "worker_id": "worker3", "metric_name": "CPU_Usage", "metric_value": 28.1}
        ]
        
        for event in events:
            self.aggregator.process_event(event)
        
        # 3rd smallest of [25.5, 28.1, 30.2] is 30.2
        self.assertEqual(self.aggregator.get_kth_smallest("CPU_Usage"), 30.2)

    def test_thread_safety(self):
        # Test concurrent event processing from multiple threads
        aggregator = DistributedAggregator(k=3, window_size=60)
        num_threads = 5
        events_per_thread = 200
        
        def worker(worker_id):
            base_time = 1678886400
            for i in range(events_per_thread):
                event = {
                    "timestamp": base_time + i,
                    "worker_id": f"worker{worker_id}",
                    "metric_name": "CPU_Usage",
                    "metric_value": 20.0 + (worker_id * 10) + (i % 10)
                }
                aggregator.process_event(event)
                # Small sleep to simulate real-world conditions
                time.sleep(0.001)
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # At this point, each thread has added events_per_thread events
        # We should have num_threads * events_per_thread events in total
        # The k-th smallest value should be deterministic regardless of thread execution order
        kth_smallest = aggregator.get_kth_smallest("CPU_Usage")
        self.assertIsInstance(kth_smallest, float)
        self.assertNotEqual(kth_smallest, -1)  # We should have enough values

    def test_large_k_value(self):
        # Test with a large k value
        aggregator = DistributedAggregator(k=10, window_size=60)
        
        # Add only 5 events
        for i in range(5):
            event = {
                "timestamp": 1678886400 + i,
                "worker_id": f"worker{i}",
                "metric_name": "CPU_Usage",
                "metric_value": 20.0 + i
            }
            aggregator.process_event(event)
        
        # Should return -1 when fewer than k values are available
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), -1)
        
        # Add 5 more events to reach k
        for i in range(5, 10):
            event = {
                "timestamp": 1678886400 + i,
                "worker_id": f"worker{i}",
                "metric_name": "CPU_Usage",
                "metric_value": 20.0 + i
            }
            aggregator.process_event(event)
        
        # Now we have exactly k values
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), 29.0)  # 10th smallest is 29.0
        
        # Add one more event
        aggregator.process_event({
            "timestamp": 1678886410,
            "worker_id": "worker10",
            "metric_name": "CPU_Usage",
            "metric_value": 15.0  # Smaller than all existing values
        })
        
        # Now the 10th smallest should be different
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), 28.0)  # 10th smallest is now 28.0

    def test_edge_cases(self):
        # Test with k=1 (minimum value)
        aggregator = DistributedAggregator(k=1, window_size=60)
        
        aggregator.process_event({
            "timestamp": 1678886400,
            "worker_id": "worker1",
            "metric_name": "CPU_Usage",
            "metric_value": 25.5
        })
        
        # 1st smallest of [25.5] is 25.5
        self.assertEqual(aggregator.get_kth_smallest("CPU_Usage"), 25.5)
        
        # Test with the same value from different workers
        events = [
            {"timestamp": 1678886400, "worker_id": "worker1", "metric_name": "Memory_Usage", "metric_value": 50.0},
            {"timestamp": 1678886410, "worker_id": "worker2", "metric_name": "Memory_Usage", "metric_value": 50.0},
            {"timestamp": 1678886420, "worker_id": "worker3", "metric_name": "Memory_Usage", "metric_value": 50.0}
        ]
        
        for event in events:
            aggregator.process_event(event)
        
        # 1st smallest of [50.0, 50.0, 50.0] is 50.0
        self.assertEqual(aggregator.get_kth_smallest("Memory_Usage"), 50.0)

if __name__ == '__main__':
    unittest.main()