import unittest
import tempfile
import os
import time
from datetime import datetime, timedelta
from log_aggregate import LogAggregator

class TestLogAggregator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.aggregator = LogAggregator(storage_path=self.temp_dir.name)
        
        # Sample log entries
        self.logs = [
            "2024-01-01T10:00:00Z|INFO|192.168.1.1|System started",
            "2024-01-01T10:00:01Z|ERROR|192.168.1.2|Connection failed",
            "2024-01-01T10:00:02Z|WARNING|192.168.1.1|High memory usage",
            "2024-01-01T10:00:03Z|ERROR|192.168.1.2|Database timeout",
            "2024-01-02T10:00:00Z|INFO|192.168.1.3|Backup completed"
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ingestion(self):
        for log in self.logs:
            self.aggregator.ingest(log)
        self.assertEqual(len(self.aggregator), 5)

    def test_query_simple(self):
        for log in self.logs:
            self.aggregator.ingest(log)
        
        # Test single field query
        results = self.aggregator.query("level:ERROR")
        self.assertEqual(len(results), 2)
        self.assertTrue(all("ERROR" in log for log in results))

    def test_query_complex(self):
        for log in self.logs:
            self.aggregator.ingest(log)
        
        # Test AND query
        results = self.aggregator.query("level:ERROR AND ip:192.168.1.2")
        self.assertEqual(len(results), 2)
        
        # Test OR query
        results = self.aggregator.query("level:INFO OR level:WARNING")
        self.assertEqual(len(results), 3)

    def test_retention_policy(self):
        old_log = "2023-12-25T00:00:00Z|INFO|192.168.1.1|Old system message"
        self.aggregator.ingest(old_log)
        
        # Set retention to 7 days
        self.aggregator.apply_retention_policy(timedelta(days=7))
        
        # Old log should be purged
        self.assertEqual(len(self.aggregator), 0)

    def test_real_time_aggregation(self):
        for log in self.logs:
            self.aggregator.ingest(log)
        
        # Test error count by IP
        agg_results = self.aggregator.aggregate(
            field="ip",
            filter="level:ERROR",
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2)
        )
        self.assertEqual(agg_results["192.168.1.2"], 2)

    def test_malformed_log(self):
        with self.assertRaises(ValueError):
            self.aggregator.ingest("BAD_LOG_FORMAT")
        
        with self.assertRaises(ValueError):
            self.aggregator.ingest("2024-01-01T10:00:00Z|INFO|MISSING_MESSAGE")

    def test_concurrent_access(self):
        import threading
        
        def ingest_logs():
            for _ in range(100):
                self.aggregator.ingest("2024-01-01T10:00:00Z|INFO|192.168.1.1|Concurrent message")
        
        threads = [threading.Thread(target=ingest_logs) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        self.assertEqual(len(self.aggregator), 1000)

if __name__ == '__main__':
    unittest.main()