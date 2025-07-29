import unittest
import time
from datetime import datetime, timedelta
from ddos_detect import detect_ddos

class DdosDetectTest(unittest.TestCase):
    def test_empty_flow_records(self):
        flow_records = []
        result = detect_ddos(flow_records, 60, 2.0, 10, 300)
        self.assertEqual(result, [])

    def test_zero_parameters(self):
        # When parameters like time_window, threshold_factor, min_source_ips or attack_duration are zero,
        # expect the function to return an empty list (or handle gracefully).
        flow_records = [{
            "start_time": 1000,
            "source_ip": "192.168.0.1",
            "destination_ip": "10.0.0.1",
            "bytes_sent": 100,
            "bytes_received": 50
        }]
        result = detect_ddos(flow_records, 0, 0, 0, 0)
        self.assertEqual(result, [])

    def test_single_record(self):
        flow_records = [{
            "start_time": 1000,
            "source_ip": "192.168.0.1",
            "destination_ip": "10.0.0.1",
            "bytes_sent": 200,
            "bytes_received": 100
        }]
        result = detect_ddos(flow_records, 60, 2.0, 3, 120)
        self.assertEqual(result, [])

    def test_ddos_detection_single_target(self):
        # Create baseline traffic for destination IP "192.168.1.1"
        flow_records = []
        base_time = 1000
        # Baseline: low volume behavior from t=1000 to t=1100
        for t in range(base_time, base_time + 100, 10):
            flow_records.append({
                "start_time": t,
                "source_ip": "192.168.0.1",
                "destination_ip": "192.168.1.1",
                "bytes_sent": 100,
                "bytes_received": 50
            })
        # Attack period: heavy traffic with sufficient unique source IPs from t=1200 to t=1320 (duration 120 sec)
        for t in range(1200, 1321):
            # Create 6 records per second to satisfy min_source_ips and overload threshold
            for i in range(6):
                flow_records.append({
                    "start_time": t,
                    "source_ip": f"10.0.0.{i+1}",
                    "destination_ip": "192.168.1.1",
                    "bytes_sent": 500,
                    "bytes_received": 250
                })
        # Additional normal traffic after attack
        for t in range(1400, 1420):
            flow_records.append({
                "start_time": t,
                "source_ip": "192.168.0.2",
                "destination_ip": "192.168.1.1",
                "bytes_sent": 100,
                "bytes_received": 50
            })
        # Parameters: time_window=30 sec, threshold_factor=2.0, min_source_ips=5, attack_duration=60 sec.
        result = detect_ddos(flow_records, 30, 2.0, 5, 60)
        self.assertIn("192.168.1.1", result)
        self.assertEqual(len(result), 1)

    def test_multiple_ddos_targets(self):
        flow_records = []
        base_time = 2000
        # For destination 192.168.1.1 - DDoS attack
        for t in range(base_time, base_time + 50, 5):  # baseline low traffic
            flow_records.append({
                "start_time": t,
                "source_ip": "10.1.1.1",
                "destination_ip": "192.168.1.1",
                "bytes_sent": 120,
                "bytes_received": 60
            })
        # Sustained anomalous traffic for 192.168.1.1 from t=2100 to t=2180 (80 sec)
        for t in range(2100, 2181):
            for i in range(7):
                flow_records.append({
                    "start_time": t,
                    "source_ip": f"10.1.1.{i+2}",
                    "destination_ip": "192.168.1.1",
                    "bytes_sent": 400,
                    "bytes_received": 200
                })
        
        # For destination 192.168.1.2 - Traffic spike not satisfying unique source IP requirement
        for t in range(base_time, base_time + 50, 5):
            flow_records.append({
                "start_time": t,
                "source_ip": "10.1.2.1",
                "destination_ip": "192.168.1.2",
                "bytes_sent": 100,
                "bytes_received": 50
            })
        # Spike period for 192.168.1.2 with only one unique source (should not trigger)
        for t in range(2100, 2150):
            flow_records.append({
                "start_time": t,
                "source_ip": "10.1.2.1",
                "destination_ip": "192.168.1.2",
                "bytes_sent": 500,
                "bytes_received": 250
            })
        
        # Parameters: time_window=20 sec, threshold_factor=2.0, min_source_ips=5, attack_duration=60 sec.
        result = detect_ddos(flow_records, 20, 2.0, 5, 60)
        # Only "192.168.1.1" should be detected as under DDoS.
        self.assertIn("192.168.1.1", result)
        self.assertNotIn("192.168.1.2", result)
        self.assertEqual(len(result), 1)

    def test_no_ddos_due_to_short_duration(self):
        flow_records = []
        base_time = 3000
        # Base traffic for destination "192.168.1.3"
        for t in range(base_time, base_time + 100, 10):
            flow_records.append({
                "start_time": t,
                "source_ip": "172.16.0.1",
                "destination_ip": "192.168.1.3",
                "bytes_sent": 150,
                "bytes_received": 75
            })
        # Create a short burst (duration less than attack_duration)
        for t in range(3100, 3120):
            for i in range(6):
                flow_records.append({
                    "start_time": t,
                    "source_ip": f"172.16.0.{i+2}",
                    "destination_ip": "192.168.1.3",
                    "bytes_sent": 600,
                    "bytes_received": 300
                })
        # Parameters: time_window=30, threshold_factor=1.5, min_source_ips=5, attack_duration=60 sec.
        result = detect_ddos(flow_records, 30, 1.5, 5, 60)
        # Even though there is a burst, its duration is not enough for confirmed DDoS.
        self.assertNotIn("192.168.1.3", result)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()