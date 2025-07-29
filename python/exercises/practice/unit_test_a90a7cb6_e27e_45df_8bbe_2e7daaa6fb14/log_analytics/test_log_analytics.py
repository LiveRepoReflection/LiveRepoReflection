import unittest
import time
import random
from collections import defaultdict
from log_analytics import LogAggregator

class TestLogAnalytics(unittest.TestCase):
    def setUp(self):
        self.aggregator = LogAggregator()
        self.sample_logs = [
            {"timestamp": int(time.time()), "service_id": "auth_service", "log_level": "INFO", "message": "User login successful"},
            {"timestamp": int(time.time()), "service_id": "payment_service", "log_level": "ERROR", "message": "Transaction failed"},
            {"timestamp": int(time.time()), "service_id": "auth_service", "log_level": "WARNING", "message": "Multiple failed login attempts"},
            {"timestamp": int(time.time()), "service_id": "inventory_service", "log_level": "INFO", "message": "Stock updated"},
            {"timestamp": int(time.time()), "service_id": "payment_service", "log_level": "INFO", "message": "Transaction processed"}
        ]
        
        # Generate high volume test data
        self.high_volume_logs = []
        services = ["service_" + str(i) for i in range(100)]
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        for _ in range(10000):
            self.high_volume_logs.append({
                "timestamp": int(time.time()) - random.randint(0, 3600),
                "service_id": random.choice(services),
                "log_level": random.choice(levels),
                "message": random.choice(["Operation succeeded", "Operation failed", "Timeout occurred", "Resource not found"])
            })

    def test_log_ingestion(self):
        for log in self.sample_logs:
            self.aggregator.ingest_log(log)
        self.assertEqual(len(self.aggregator.logs), len(self.sample_logs))

    def test_high_volume_ingestion(self):
        for log in self.high_volume_logs:
            self.aggregator.ingest_log(log)
        self.assertEqual(len(self.aggregator.logs), len(self.high_volume_logs))

    def test_query_by_service(self):
        for log in self.sample_logs:
            self.aggregator.ingest_log(log)
        
        auth_logs = self.aggregator.query_logs(service_id="auth_service")
        self.assertEqual(len(auth_logs), 2)
        for log in auth_logs:
            self.assertEqual(log["service_id"], "auth_service")

    def test_query_by_level(self):
        for log in self.sample_logs:
            self.aggregator.ingest_log(log)
        
        error_logs = self.aggregator.query_logs(log_level="ERROR")
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(error_logs[0]["log_level"], "ERROR")

    def test_query_by_time_range(self):
        now = int(time.time())
        time_test_logs = [
            {"timestamp": now - 300, "service_id": "test_service", "log_level": "INFO", "message": "Old log"},
            {"timestamp": now - 60, "service_id": "test_service", "log_level": "INFO", "message": "Recent log"},
            {"timestamp": now, "service_id": "test_service", "log_level": "INFO", "message": "Current log"}
        ]
        
        for log in time_test_logs:
            self.aggregator.ingest_log(log)
            
        recent_logs = self.aggregator.query_logs(start_time=now-120, end_time=now+10)
        self.assertEqual(len(recent_logs), 2)

    def test_anomaly_detection(self):
        # Create a pattern that should trigger anomaly detection
        for _ in range(20):
            self.aggregator.ingest_log({
                "timestamp": int(time.time()),
                "service_id": "critical_service",
                "log_level": "ERROR",
                "message": "System failure"
            })
        
        anomalies = self.aggregator.detect_anomalies()
        self.assertGreater(len(anomalies), 0)
        self.assertTrue(any("critical_service" in a["service_id"] for a in anomalies))

    def test_top_messages(self):
        for log in self.sample_logs * 3:  # Create some repetition
            self.aggregator.ingest_log(log)
            
        top_messages = self.aggregator.get_top_messages(service_id="auth_service", n=1)
        self.assertEqual(len(top_messages), 1)
        self.assertEqual(top_messages[0]["message"], "User login successful")

    def test_fault_tolerance(self):
        # Test with malformed logs
        malformed_logs = [
            {"service_id": "test_service", "log_level": "INFO"},  # Missing timestamp and message
            {"timestamp": "invalid", "service_id": "test_service", "log_level": "INFO", "message": "test"},  # Invalid timestamp
            {"timestamp": int(time.time()), "log_level": "INFO", "message": "test"}  # Missing service_id
        ]
        
        for log in malformed_logs:
            with self.assertRaises(ValueError):
                self.aggregator.ingest_log(log)

    def test_concurrent_ingestion(self):
        import threading
        
        def ingest_concurrently(logs):
            for log in logs:
                self.aggregator.ingest_log(log)
        
        threads = []
        chunk_size = len(self.high_volume_logs) // 4
        for i in range(4):
            chunk = self.high_volume_logs[i*chunk_size : (i+1)*chunk_size]
            thread = threading.Thread(target=ingest_concurrently, args=(chunk,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        self.assertEqual(len(self.aggregator.logs), len(self.high_volume_logs))

if __name__ == '__main__':
    unittest.main()