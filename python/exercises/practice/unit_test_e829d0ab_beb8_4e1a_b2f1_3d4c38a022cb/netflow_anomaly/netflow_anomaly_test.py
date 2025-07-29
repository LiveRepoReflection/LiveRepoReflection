import unittest
import time
from netflow_anomaly import AnomalyDetector

class TestAnomalyDetector(unittest.TestCase):
    def setUp(self):
        self.detector = AnomalyDetector()

    def test_single_normal_flow(self):
        flow = {
            "timestamp": int(time.time()),
            "source_ip": "192.168.1.100",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        score = self.detector.process_flow(flow)
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 1)
        self.assertLess(score, 0.5)  # Normal traffic should have low anomaly score

    def test_repeated_normal_flows(self):
        flow = {
            "timestamp": int(time.time()),
            "source_ip": "192.168.1.100",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        scores = []
        for _ in range(10):
            scores.append(self.detector.process_flow(flow))
        
        self.assertTrue(all(0 <= score <= 1 for score in scores))
        self.assertTrue(all(score < 0.5 for score in scores))

    def test_sudden_anomaly(self):
        # First establish normal traffic pattern
        normal_flow = {
            "timestamp": int(time.time()),
            "source_ip": "192.168.1.100",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        for _ in range(10):
            self.detector.process_flow(normal_flow)

        # Then introduce anomalous traffic
        anomalous_flow = {
            "timestamp": int(time.time()),
            "source_ip": "10.0.0.1",
            "destination_ip": "172.217.160.142",
            "source_port": 44444,
            "destination_port": 80,
            "protocol": "TCP",
            "packet_size": 15000,
            "packet_count": 1000
        }
        score = self.detector.process_flow(anomalous_flow)
        self.assertGreater(score, 0.5)  # Anomalous traffic should have high anomaly score

    def test_gradual_pattern_change(self):
        initial_flow = {
            "timestamp": int(time.time()),
            "source_ip": "192.168.1.100",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        
        # Establish initial pattern
        for _ in range(10):
            self.detector.process_flow(initial_flow)

        # Gradually increase packet size and count
        scores = []
        for i in range(10):
            modified_flow = dict(initial_flow)
            modified_flow["packet_size"] = 512 + (i * 100)
            modified_flow["packet_count"] = 1 + i
            scores.append(self.detector.process_flow(modified_flow))

        # Gradual changes should result in lower anomaly scores than sudden changes
        self.assertTrue(all(score < 0.7 for score in scores))

    def test_invalid_input(self):
        invalid_flow = {
            "timestamp": "invalid",
            "source_ip": "192.168.1.100",
            "destination_ip": "8.8.8.8",
            "source_port": "invalid",
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        with self.assertRaises(ValueError):
            self.detector.process_flow(invalid_flow)

    def test_missing_fields(self):
        incomplete_flow = {
            "timestamp": int(time.time()),
            "source_ip": "192.168.1.100",
            # missing destination_ip
            "source_port": 50000,
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        with self.assertRaises(KeyError):
            self.detector.process_flow(incomplete_flow)

    def test_high_volume_processing(self):
        flow = {
            "timestamp": int(time.time()),
            "source_ip": "192.168.1.100",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 53,
            "protocol": "UDP",
            "packet_size": 512,
            "packet_count": 1
        }
        
        start_time = time.time()
        for _ in range(1000):  # Process 1000 flows
            score = self.detector.process_flow(flow)
            self.assertTrue(0 <= score <= 1)
        
        processing_time = time.time() - start_time
        self.assertLess(processing_time, 1.0)  # Should process 1000 flows in less than 1 second

    def test_memory_usage(self):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process 10000 flows
        for _ in range(10000):
            flow = {
                "timestamp": int(time.time()),
                "source_ip": "192.168.1.100",
                "destination_ip": "8.8.8.8",
                "source_port": 50000,
                "destination_port": 53,
                "protocol": "UDP",
                "packet_size": 512,
                "packet_count": 1
            }
            self.detector.process_flow(flow)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # Convert to MB
        
        self.assertLess(memory_increase, 100)  # Memory increase should be less than 100MB

if __name__ == '__main__':
    unittest.main()