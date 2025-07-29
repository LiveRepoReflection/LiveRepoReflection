import unittest
from log_analyzer import LogAnalysisSystem

class TestLogAnalysisSystem(unittest.TestCase):
    def setUp(self):
        self.system = LogAnalysisSystem()

    def test_empty_query(self):
        """Test querying an empty system returns empty list"""
        result = self.system.query_logs(0, 100, {"machine1"})
        self.assertEqual(result, [])

    def test_single_log_entry(self):
        """Test processing and querying a single log entry"""
        self.system.process_log_entry(10, "machine1", "INFO", "test message")
        result = self.system.query_logs(0, 100, {"machine1"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (10, "machine1", "INFO", "test message"))

    def test_time_range_filtering(self):
        """Test filtering by time range"""
        self.system.process_log_entry(10, "machine1", "INFO", "message1")
        self.system.process_log_entry(20, "machine1", "INFO", "message2")
        self.system.process_log_entry(30, "machine1", "INFO", "message3")
        
        result = self.system.query_logs(15, 25, {"machine1"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (20, "machine1", "INFO", "message2"))

    def test_machine_id_filtering(self):
        """Test filtering by machine ID"""
        self.system.process_log_entry(10, "machine1", "INFO", "message1")
        self.system.process_log_entry(20, "machine2", "INFO", "message2")
        self.system.process_log_entry(30, "machine3", "INFO", "message3")
        
        result = self.system.query_logs(0, 100, {"machine1", "machine2"})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (10, "machine1", "INFO", "message1"))
        self.assertEqual(result[1], (20, "machine2", "INFO", "message2"))

    def test_timestamp_sorting(self):
        """Test results are sorted by timestamp"""
        self.system.process_log_entry(30, "machine1", "INFO", "message3")
        self.system.process_log_entry(10, "machine1", "INFO", "message1")
        self.system.process_log_entry(20, "machine1", "INFO", "message2")
        
        result = self.system.query_logs(0, 100, {"machine1"})
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], 10)
        self.assertEqual(result[1][0], 20)
        self.assertEqual(result[2][0], 30)

    def test_boundary_conditions(self):
        """Test boundary conditions of time range"""
        self.system.process_log_entry(10, "machine1", "INFO", "message1")
        
        # Exact boundaries
        result = self.system.query_logs(10, 10, {"machine1"})
        self.assertEqual(len(result), 1)
        
        # Just outside boundaries
        result = self.system.query_logs(11, 20, {"machine1"})
        self.assertEqual(len(result), 0)
        result = self.system.query_logs(0, 9, {"machine1"})
        self.assertEqual(len(result), 0)

    def test_multiple_log_levels(self):
        """Test handling of different log levels"""
        self.system.process_log_entry(10, "machine1", "INFO", "info message")
        self.system.process_log_entry(20, "machine1", "ERROR", "error message")
        self.system.process_log_entry(30, "machine1", "WARN", "warning message")
        
        result = self.system.query_logs(0, 100, {"machine1"})
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][2], "INFO")
        self.assertEqual(result[1][2], "ERROR")
        self.assertEqual(result[2][2], "WARN")

    def test_large_dataset(self):
        """Test handling of a larger dataset"""
        # Insert 1000 log entries
        for i in range(1000):
            self.system.process_log_entry(
                i, 
                f"machine{i % 10}", 
                "INFO", 
                f"message{i}"
            )
        
        # Query for specific time range and machines
        result = self.system.query_logs(100, 200, {"machine1", "machine2"})
        
        # Verify results
        self.assertTrue(all(100 <= entry[0] <= 200 for entry in result))
        self.assertTrue(all(entry[1] in {"machine1", "machine2"} for entry in result))
        self.assertTrue(all(entry[0] <= entry2[0] for entry, entry2 in zip(result, result[1:])))

    def test_empty_machine_ids(self):
        """Test querying with empty machine IDs set"""
        self.system.process_log_entry(10, "machine1", "INFO", "message")
        result = self.system.query_logs(0, 100, set())
        self.assertEqual(len(result), 0)

    def test_non_existent_machine_ids(self):
        """Test querying for non-existent machine IDs"""
        self.system.process_log_entry(10, "machine1", "INFO", "message")
        result = self.system.query_logs(0, 100, {"machine2"})
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()