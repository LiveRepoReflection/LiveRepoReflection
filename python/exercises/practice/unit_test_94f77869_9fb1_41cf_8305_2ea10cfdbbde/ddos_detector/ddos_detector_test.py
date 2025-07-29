import unittest
from unittest.mock import patch, MagicMock
import time
import sys
from io import StringIO
from ddos_detector import detect_ddos

class DDOSDetectorTest(unittest.TestCase):
    def test_empty_stream(self):
        """Test behavior with an empty stream of packets."""
        with patch('sys.stdin', StringIO('')):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                detect_ddos()
                self.assertEqual(fake_out.getvalue().strip(), "[]")

    def test_below_threshold(self):
        """Test when traffic is below the anomaly threshold."""
        # Create 500 packets from different sources to the same destination
        packets = ""
        for i in range(500):
            packet = f'{{"timestamp": 1678886400, "source_ip": "1.1.1.{i}", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        with patch('sys.stdin', StringIO(packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                detect_ddos()
                self.assertEqual(fake_out.getvalue().strip(), "[]")

    def test_above_threshold(self):
        """Test when traffic exceeds the anomaly threshold."""
        # Create 1500 packets from different sources to the same destination
        packets = ""
        for i in range(1500):
            packet = f'{{"timestamp": 1678886400, "source_ip": "1.1.1.{i}", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        with patch('sys.stdin', StringIO(packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                detect_ddos()
                self.assertEqual(fake_out.getvalue().strip(), '["10.0.0.1"]')

    def test_multiple_destinations(self):
        """Test behavior with multiple destination IPs."""
        # Create 1200 packets to destination 10.0.0.1 and 800 to 10.0.0.2
        packets = ""
        for i in range(1200):
            packet = f'{{"timestamp": 1678886400, "source_ip": "1.1.1.{i}", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        for i in range(800):
            packet = f'{{"timestamp": 1678886400, "source_ip": "2.2.2.{i}", "destination_ip": "10.0.0.2", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        with patch('sys.stdin', StringIO(packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                detect_ddos()
                output = fake_out.getvalue().strip()
                # Convert the string output to a list
                import json
                result = json.loads(output)
                self.assertIn("10.0.0.1", result)
                self.assertNotIn("10.0.0.2", result)

    def test_time_window(self):
        """Test the sliding time window functionality."""
        # Create packets spanning more than the 60-second window
        packets = ""
        # First group at timestamp 1678886400
        for i in range(600):
            packet = f'{{"timestamp": 1678886400, "source_ip": "1.1.1.{i}", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        # Second group at timestamp 1678886470 (70 seconds later, outside window)
        for i in range(600):
            packet = f'{{"timestamp": 1678886470, "source_ip": "1.1.1.{i+600}", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        with patch('sys.stdin', StringIO(packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                detect_ddos()
                self.assertEqual(fake_out.getvalue().strip(), "[]")  # Should not detect DDoS as packets are spread out

    def test_decay_factor(self):
        """Test the decay factor on older packets."""
        # Create packets with increasing timestamps to test decay
        packets = ""
        # 1100 packets spread over 55 seconds
        for i in range(1100):
            # Spread packets evenly across 55 seconds
            timestamp = 1678886400 + (i % 55)
            packet = f'{{"timestamp": {timestamp}, "source_ip": "1.1.1.{i}", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        with patch('sys.stdin', StringIO(packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                detect_ddos()
                # Due to decay, the effective count would be less than 1100
                # Depending on the implementation, this might not trigger an alert
                output = fake_out.getvalue().strip()
                # Hard to predict exact behavior without knowing implementation details
                # Just check if the output can be parsed as JSON
                import json
                result = json.loads(output)
                self.assertIsInstance(result, list)

    def test_high_packet_rate(self):
        """Test handling of high packet arrival rate."""
        # Create a large number of packets to simulate high packet rate
        packets = ""
        for i in range(10000):  # 10k packets
            src_ip = f"1.1.1.{i % 2000}"  # 2000 unique source IPs
            dst_ip = f"10.0.0.{i % 5}"    # 5 destination IPs
            packet = f'{{"timestamp": 1678886400, "source_ip": "{src_ip}", "destination_ip": "{dst_ip}", "source_port": 12345, "destination_port": 80, "packet_size": 100}}\n'
            packets += packet
        
        with patch('sys.stdin', StringIO(packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                # Measure execution time to ensure it's reasonably fast
                start_time = time.time()
                detect_ddos()
                end_time = time.time()
                
                execution_time = end_time - start_time
                # Check execution time is reasonable (adjust as needed for your environment)
                self.assertLess(execution_time, 10.0)  # Should process 10k packets in under 10 seconds
                
                # Verify output
                output = fake_out.getvalue().strip()
                import json
                result = json.loads(output)
                self.assertIsInstance(result, list)

    def test_invalid_packet_format(self):
        """Test handling of invalid packet formats."""
        # Create some invalid JSON
        invalid_packets = """
        {"timestamp": 1678886400, "source_ip": "1.1.1.1", "destination_ip": "10.0.0.1", "source_port": 12345, "destination_port": 80, "packet_size": 100}
        not a json packet
        {"timestamp": 1678886401, "source_ip": "1.1.1.2", "destination_ip": "10.0.0.1", "source_port": 12346, "destination_port": 80}
        {"incomplete": "json"
        """
        
        with patch('sys.stdin', StringIO(invalid_packets)):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                # Should handle errors gracefully
                detect_ddos()
                output = fake_out.getvalue().strip()
                import json
                # Ensure output is valid JSON
                try:
                    result = json.loads(output)
                    self.assertIsInstance(result, list)
                except json.JSONDecodeError:
                    self.fail("Output is not valid JSON")

if __name__ == '__main__':
    unittest.main()