import unittest
import time
import random
from packet_anomaly import AnomalyDetector

class PacketAnomalyTest(unittest.TestCase):
    def setUp(self):
        self.detector = AnomalyDetector()

    def create_packet(self, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, packet_size):
        return {
            "timestamp": timestamp,
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "source_port": src_port,
            "destination_port": dst_port,
            "protocol": protocol,
            "packet_size": packet_size
        }

    def test_anomaly_score_range(self):
        packets = [
            self.create_packet(1000, "192.168.1.1", "10.0.0.1", 1234, 80, "TCP", 500),
            self.create_packet(1010, "192.168.1.2", "10.0.0.2", 1235, 80, "TCP", 450),
            self.create_packet(1020, "192.168.1.3", "10.0.0.3", 1236, 443, "TCP", 600)
        ]
        for packet in packets:
            score = self.detector.process(packet)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_consistent_output(self):
        packets = [
            self.create_packet(1000, "192.168.1.1", "10.0.0.1", 1234, 80, "TCP", 500),
            self.create_packet(1010, "192.168.1.2", "10.0.0.2", 1235, 80, "TCP", 450),
            self.create_packet(1020, "192.168.1.3", "10.0.0.3", 1236, 443, "TCP", 600)
        ]
        scores1 = [self.detector.process(packet) for packet in packets]
        # Reset the detector to test reproducibility with a fresh state
        self.detector = AnomalyDetector()
        scores2 = [self.detector.process(packet) for packet in packets]
        self.assertEqual(scores1, scores2)

    def test_edge_case_spike(self):
        normal_packets = [self.create_packet(1000 + i * 10, "192.168.1.1", "10.0.0.1", 1234, 80, "TCP", 500) for i in range(10)]
        spike_packet = self.create_packet(1100, "192.168.1.1", "10.0.0.1", 1234, 80, "TCP", 10000)
        for packet in normal_packets:
            self.detector.process(packet)
        spike_score = self.detector.process(spike_packet)
        self.assertIsInstance(spike_score, float)
        self.assertGreater(spike_score, 0.5)

    def test_adaptive_learning(self):
        base_packets = [self.create_packet(1000 + i * 5, "10.0.0.1", "192.168.1.1", 1000 + i, 80, "TCP", 600) for i in range(20)]
        for packet in base_packets:
            self.detector.process(packet)
        divergent_packet = self.create_packet(1100, "10.0.0.2", "192.168.1.2", 2000, 80, "TCP", 50)
        score = self.detector.process(divergent_packet)
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.5)

    def test_high_volume_performance(self):
        num_packets = 1000
        start_time = time.perf_counter()
        for i in range(num_packets):
            packet = self.create_packet(
                1000 + i,
                f"192.168.1.{i % 255}",
                f"10.0.0.{(i + 1) % 255}",
                1000 + i % 1000,
                80,
                "UDP" if i % 2 == 0 else "TCP",
                random.randint(100, 1000)
            )
            self.detector.process(packet)
        end_time = time.perf_counter()
        average_time = (end_time - start_time) / num_packets
        self.assertLess(average_time, 0.001, msg=f"Average processing time {average_time*1000:.3f}ms exceeds 1ms per packet.")

if __name__ == '__main__':
    unittest.main()