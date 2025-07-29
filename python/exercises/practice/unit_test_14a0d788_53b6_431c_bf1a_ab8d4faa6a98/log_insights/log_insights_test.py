import unittest
from log_insights import LogSystem

class TestLogSystem(unittest.TestCase):
    def setUp(self):
        self.log_system = LogSystem()

    def test_ingest_and_query_time_range(self):
        # Ingest some log entries
        self.log_system.ingest(1000, "server1", 2, "Started process")
        self.log_system.ingest(1001, "server2", 3, "Warning issued")
        self.log_system.ingest(1002, "server1", 4, "Error occurred")
        
        # Query logs within a time range
        result = self.log_system.query_time_range(1000, 1001)
        expected = [
            (1000, "server1", 2, "Started process"),
            (1001, "server2", 3, "Warning issued")
        ]
        self.assertEqual(result, expected)

    def test_query_server_log_level(self):
        # Ingest multiple logs from different servers and log levels
        logs = [
            (1000, "server1", 2, "Info message"),
            (1001, "server1", 1, "Debug message"),
            (1002, "server1", 3, "Warning message"),
            (1003, "server2", 4, "Error message"),
            (1004, "server1", 4, "Critical error")
        ]
        for log in logs:
            self.log_system.ingest(*log)
        
        # Query for server1 logs with log_level >= 2
        result = self.log_system.query_server_log_level("server1", 2)
        expected = [
            (1000, "server1", 2, "Info message"),
            (1002, "server1", 3, "Warning message"),
            (1004, "server1", 4, "Critical error")
        ]
        self.assertEqual(result, expected)
        
    def test_top_k_frequent_messages(self):
        # Ingest logs with some messages repeating
        logs = [
            (1000, "server1", 2, "A"),
            (1001, "server2", 3, "B"),
            (1002, "server1", 4, "A"),
            (1003, "server2", 4, "C"),
            (1004, "server2", 4, "A"),
            (1005, "server2", 4, "B"),
            (1006, "server1", 4, "C"),
            (1007, "server1", 4, "D"),
            (1008, "server1", 4, "B")
        ]
        for log in logs:
            self.log_system.ingest(*log)
        
        # Frequencies: A: 3, B: 3, C: 2, D: 1
        # For equal frequency, messages should be sorted lexicographically ascending.
        result = self.log_system.top_k_frequent_messages(1000, 1008, 2)
        expected = [("A", 3), ("B", 3)]
        self.assertEqual(result, expected)

    def test_top_k_with_ties_and_sorting(self):
        # Ingest logs where multiple messages have the same frequency
        logs = [
            (1000, "server1", 2, "cat"),
            (1001, "server2", 3, "dog"),
            (1002, "server1", 4, "cat"),
            (1003, "server2", 4, "bird"),
            (1004, "server1", 4, "dog"),
            (1005, "server2", 4, "bird")
        ]
        for log in logs:
            self.log_system.ingest(*log)
        
        # Frequencies: bird:2, cat:2, dog:2
        # Lexicographical order for tie: bird, cat, dog
        result = self.log_system.top_k_frequent_messages(1000, 1005, 2)
        expected = [("bird", 2), ("cat", 2)]
        self.assertEqual(result, expected)

    def test_query_no_logs(self):
        # Query time range where no logs exist
        result = self.log_system.query_time_range(0, 999)
        self.assertEqual(result, [])
        
        # Query server and log level where no logs exist
        result = self.log_system.query_server_log_level("non_existing", 1)
        self.assertEqual(result, [])
        
        # Query Top K Frequent messages in an empty range
        result = self.log_system.top_k_frequent_messages(0, 999, 3)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()