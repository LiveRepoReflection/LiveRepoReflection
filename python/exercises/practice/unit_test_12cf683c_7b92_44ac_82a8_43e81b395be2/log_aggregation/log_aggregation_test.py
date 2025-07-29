import unittest
from time import time
from log_aggregator import LogAggregator
import threading
import time
import random

class LogAggregatorTest(unittest.TestCase):
    def setUp(self):
        # Create a fresh LogAggregator for each test
        self.aggregator = LogAggregator()
        
        # Create some test data
        self.now = int(time.time() * 1000)  # Current time in milliseconds
        
        # Sample server and region mappings
        self.server_region_map = {
            "server1": "us-east",
            "server2": "us-east",
            "server3": "us-west",
            "server4": "eu-central",
            "server5": "asia-east"
        }
        
        # Register servers with their regions
        for server_id, region in self.server_region_map.items():
            self.aggregator.register_server(server_id, region)
            
        # Sample logs spanning different time periods
        self.sample_logs = [
            (self.now - 5000, "server1", "Error in module A"),
            (self.now - 4500, "server2", "Warning: CPU high"),
            (self.now - 4000, "server1", "Error persists in module A"),
            (self.now - 3500, "server3", "Starting backup process"),
            (self.now - 3000, "server1", "Module A restored"),
            (self.now - 2500, "server4", "Connection timeout"),
            (self.now - 2000, "server2", "Memory usage normal"),
            (self.now - 1500, "server5", "New user registered"),
            (self.now - 1000, "server3", "Backup completed"),
            (self.now - 500, "server4", "Connection reestablished")
        ]
        
        # Ingest sample logs
        for log in self.sample_logs:
            self.aggregator.ingest_log(*log)
    
    def test_server_query(self):
        # Query logs for server1
        results = self.aggregator.query("server", "server1", self.now - 6000, self.now)
        
        # Expected logs from server1
        expected = [
            "Error in module A",
            "Error persists in module A",
            "Module A restored"
        ]
        
        self.assertEqual(results, expected)
        
        # Query with narrower time range
        results = self.aggregator.query("server", "server1", self.now - 4200, self.now - 3200)
        expected = ["Error persists in module A"]
        self.assertEqual(results, expected)
        
        # Query with no results expected
        results = self.aggregator.query("server", "server1", self.now - 2000, self.now - 1000)
        self.assertEqual(results, [])
    
    def test_region_query(self):
        # Query logs for us-east region
        results = self.aggregator.query("region", "us-east", self.now - 6000, self.now)
        
        # Expected logs from us-east (server1 and server2)
        expected = [
            "Error in module A",
            "Warning: CPU high",
            "Error persists in module A",
            "Module A restored",
            "Memory usage normal"
        ]
        
        # Verify all expected logs are in results (order may vary due to sorting)
        self.assertEqual(sorted(results), sorted(expected))
    
    def test_global_query(self):
        # Query all logs
        results = self.aggregator.query("global", None, self.now - 6000, self.now)
        
        # All logs should be returned
        expected = [log[2] for log in self.sample_logs]
        
        # Verify all expected logs are in results (order may vary due to sorting)
        self.assertEqual(sorted(results), sorted(expected))
    
    def test_concurrent_ingestion(self):
        # Test concurrent log ingestion
        num_threads = 10
        logs_per_thread = 100
        
        def generate_logs(thread_id):
            base_time = int(time.time() * 1000)
            for i in range(logs_per_thread):
                server_id = f"server{random.randint(1, 5)}"
                timestamp = base_time + i
                log_message = f"Thread {thread_id} log {i}"
                self.aggregator.ingest_log(timestamp, server_id, log_message)
        
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=generate_logs, args=(i,))
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify total number of logs
        total_logs = num_threads * logs_per_thread + len(self.sample_logs)
        global_results = self.aggregator.query("global", None, 0, int(time.time() * 1000) + 10000)
        self.assertEqual(len(global_results), total_logs)
    
    def test_fault_tolerance(self):
        # Test fault tolerance by simulating server failure
        self.aggregator.mark_server_failed("server1")
        
        # Ingesting logs for failed server should still work
        self.aggregator.ingest_log(self.now, "server1", "Log after failure")
        
        # Server should be recovered automatically
        results = self.aggregator.query("server", "server1", self.now - 1000, self.now + 1000)
        self.assertIn("Log after failure", results)
    
    def test_large_scale(self):
        # Test with a larger number of logs
        large_aggregator = LogAggregator()
        
        # Register 100 servers across 10 regions
        for i in range(100):
            server_id = f"server{i+1}"
            region = f"region{i % 10 + 1}"
            large_aggregator.register_server(server_id, region)
        
        # Ingest 10,000 logs
        base_time = int(time.time() * 1000)
        for i in range(10000):
            server_id = f"server{i % 100 + 1}"
            timestamp = base_time + i
            log_message = f"Log message {i}"
            large_aggregator.ingest_log(timestamp, server_id, log_message)
        
        # Query performance test
        start_time = time.time()
        results = large_aggregator.query("region", "region1", base_time, base_time + 10000)
        end_time = time.time()
        
        # Query should return quickly (< 100ms)
        self.assertLess(end_time - start_time, 0.1)
        
        # Should have approximately 1000 logs for region1
        self.assertGreaterEqual(len(results), 900)
        self.assertLessEqual(len(results), 1100)

    def test_invalid_query_parameters(self):
        # Test invalid query type
        with self.assertRaises(ValueError):
            self.aggregator.query("invalid_type", "server1", self.now - 1000, self.now)
        
        # Test invalid server ID
        results = self.aggregator.query("server", "non_existent_server", self.now - 1000, self.now)
        self.assertEqual(results, [])
        
        # Test invalid region
        results = self.aggregator.query("region", "non_existent_region", self.now - 1000, self.now)
        self.assertEqual(results, [])
        
        # Test invalid time range (end before start)
        with self.assertRaises(ValueError):
            self.aggregator.query("global", None, self.now, self.now - 1000)

    def test_empty_results(self):
        # Test query with no results
        future_time = self.now + 10000
        results = self.aggregator.query("global", None, future_time, future_time + 1000)
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()