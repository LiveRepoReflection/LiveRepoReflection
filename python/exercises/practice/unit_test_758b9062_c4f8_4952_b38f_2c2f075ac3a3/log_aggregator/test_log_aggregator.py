import unittest
from datetime import datetime, timedelta
import time

class TestLogAggregator(unittest.TestCase):
    def setUp(self):
        self.start_time = datetime.now()
        self.keywords = ["error", "warning", "critical"]
        self.window_seconds = 60
        self.num_services = 100

    def test_basic_log_ingestion(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        # Test single log entry
        timestamp = datetime.now()
        aggregator.ingest_log(1, "Error: System failure", timestamp)
        
        logs = aggregator.get_logs(1, timestamp - timedelta(seconds=1), 
                                 timestamp + timedelta(seconds=1))
        self.assertEqual(len(logs), 1)
        self.assertEqual(aggregator.get_keyword_count("error"), 1)

    def test_multiple_services(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        timestamp = datetime.now()
        aggregator.ingest_log(1, "Error in service 1", timestamp)
        aggregator.ingest_log(2, "Warning in service 2", timestamp)
        
        logs_svc1 = aggregator.get_logs(1, timestamp - timedelta(seconds=1),
                                      timestamp + timedelta(seconds=1))
        logs_svc2 = aggregator.get_logs(2, timestamp - timedelta(seconds=1),
                                      timestamp + timedelta(seconds=1))
        
        self.assertEqual(len(logs_svc1), 1)
        self.assertEqual(len(logs_svc2), 1)

    def test_sliding_window(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, 2)  # 2-second window
        
        # Add log outside window
        old_timestamp = datetime.now() - timedelta(seconds=3)
        aggregator.ingest_log(1, "Error: Old message", old_timestamp)
        
        # Add log inside window
        current_timestamp = datetime.now()
        aggregator.ingest_log(1, "Error: New message", current_timestamp)
        
        # Wait for 1 second to ensure proper window sliding
        time.sleep(1)
        
        self.assertEqual(aggregator.get_keyword_count("error"), 1)

    def test_keyword_case_insensitivity(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        timestamp = datetime.now()
        aggregator.ingest_log(1, "ERROR: uppercase", timestamp)
        aggregator.ingest_log(1, "error: lowercase", timestamp)
        aggregator.ingest_log(1, "Error: mixed case", timestamp)
        
        self.assertEqual(aggregator.get_keyword_count("error"), 3)

    def test_concurrent_logs(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        timestamp = datetime.now()
        # Simulate concurrent log entries
        for i in range(1000):
            service_id = i % 10
            aggregator.ingest_log(service_id, f"Error: Message {i}", timestamp)
        
        total_error_count = aggregator.get_keyword_count("error")
        self.assertEqual(total_error_count, 1000)

    def test_time_range_query(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        start_time = datetime.now()
        mid_time = start_time + timedelta(seconds=1)
        end_time = start_time + timedelta(seconds=2)
        
        aggregator.ingest_log(1, "Error: First message", start_time)
        aggregator.ingest_log(1, "Error: Second message", mid_time)
        aggregator.ingest_log(1, "Error: Third message", end_time)
        
        logs = aggregator.get_logs(1, start_time, mid_time)
        self.assertEqual(len(logs), 2)

    def test_invalid_service_id(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        with self.assertRaises(ValueError):
            aggregator.ingest_log(self.num_services + 1, "Invalid service", datetime.now())

    def test_invalid_time_range(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        end_time = datetime.now()
        start_time = end_time + timedelta(seconds=10)
        
        with self.assertRaises(ValueError):
            aggregator.get_logs(1, start_time, end_time)

    def test_high_load(self):
        from log_aggregator import LogAggregator
        aggregator = LogAggregator(self.num_services, self.keywords, self.window_seconds)
        
        # Generate 100,000 log entries
        timestamp = datetime.now()
        for i in range(100000):
            service_id = i % self.num_services
            message = f"Error: Message {i}"
            aggregator.ingest_log(service_id, message, timestamp)
        
        # Verify counts
        self.assertEqual(aggregator.get_keyword_count("error"), 100000)
        
        # Verify retrieval speed (should be fast)
        start_time = time.time()
        logs = aggregator.get_logs(0, timestamp - timedelta(seconds=1),
                                 timestamp + timedelta(seconds=1))
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second

if __name__ == '__main__':
    unittest.main()