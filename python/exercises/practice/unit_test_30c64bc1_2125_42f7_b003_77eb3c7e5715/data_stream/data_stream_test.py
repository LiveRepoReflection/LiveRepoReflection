import unittest
from data_stream import DataStreamAnalyzer

class DataStreamAnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.analyzer = DataStreamAnalyzer()

    def test_top_k_basic(self):
        # Add some basic traffic
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(1001, "192.168.1.1", "10.0.0.1", "TCP", 200)
        self.analyzer.process_packet(1002, "192.168.1.2", "10.0.0.2", "TCP", 150)
        
        result = self.analyzer.top_k("TCP", 1000, 1002, 2)
        self.assertEqual(result, [("10.0.0.1", 2), ("10.0.0.2", 1)])

    def test_top_k_with_protocol_filter(self):
        # Add mixed protocol traffic
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(1001, "192.168.1.1", "10.0.0.1", "UDP", 200)
        self.analyzer.process_packet(1002, "192.168.1.2", "10.0.0.2", "TCP", 150)
        
        result = self.analyzer.top_k("TCP", 1000, 1002, 2)
        self.assertEqual(result, [("10.0.0.1", 1), ("10.0.0.2", 1)])

    def test_top_k_time_range(self):
        # Add traffic with different timestamps
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(2000, "192.168.1.1", "10.0.0.1", "TCP", 200)
        self.analyzer.process_packet(3000, "192.168.1.2", "10.0.0.2", "TCP", 150)
        
        result = self.analyzer.top_k("TCP", 1000, 2000, 1)
        self.assertEqual(result, [("10.0.0.1", 2)])

    def test_aggregate_basic(self):
        # Test basic aggregation
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(1001, "192.168.1.1", "10.0.0.2", "TCP", 200)
        
        result = self.analyzer.aggregate("192.168.1.1", 1000, 1001)
        self.assertEqual(result, 300)

    def test_aggregate_time_range(self):
        # Test aggregation with specific time range
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(2000, "192.168.1.1", "10.0.0.1", "TCP", 200)
        self.analyzer.process_packet(3000, "192.168.1.1", "10.0.0.1", "TCP", 300)
        
        result = self.analyzer.aggregate("192.168.1.1", 1000, 2000)
        self.assertEqual(result, 300)

    def test_detect_malicious_basic(self):
        # Test basic malicious detection
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 1000)
        self.analyzer.process_packet(1001, "192.168.1.1", "10.0.0.2", "TCP", 1000)
        
        result = self.analyzer.detect_malicious(900.0, 2)
        self.assertEqual(result, ["192.168.1.1"])

    def test_detect_malicious_window(self):
        # Test malicious detection with time window
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 2000)
        self.analyzer.process_packet(1010, "192.168.1.1", "10.0.0.2", "TCP", 2000)
        self.analyzer.process_packet(1020, "192.168.1.2", "10.0.0.3", "TCP", 100)
        
        result = self.analyzer.detect_malicious(300.0, 15)
        self.assertEqual(set(result), {"192.168.1.1"})

    def test_out_of_order_packets(self):
        # Test handling out of order packets
        self.analyzer.process_packet(2000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 200)
        self.analyzer.process_packet(1500, "192.168.1.1", "10.0.0.1", "TCP", 300)
        
        result = self.analyzer.aggregate("192.168.1.1", 1000, 2000)
        self.assertEqual(result, 600)

    def test_duplicate_packets(self):
        # Test handling duplicate packets
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        self.analyzer.process_packet(1000, "192.168.1.1", "10.0.0.1", "TCP", 100)
        
        result = self.analyzer.top_k("TCP", 1000, 1000, 1)
        self.assertEqual(result, [("10.0.0.1", 2)])

    def test_empty_results(self):
        # Test queries with no matching results
        result = self.analyzer.top_k("TCP", 1000, 2000, 1)
        self.assertEqual(result, [])
        
        result = self.analyzer.aggregate("192.168.1.1", 1000, 2000)
        self.assertEqual(result, 0)
        
        result = self.analyzer.detect_malicious(100.0, 10)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()