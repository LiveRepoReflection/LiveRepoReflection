import unittest
import time
from unittest.mock import MagicMock
from network_analyzer import NetworkAnalyzer

class TestNetworkAnalyzer(unittest.TestCase):
    def setUp(self):
        self.is_anomalous = MagicMock()
        self.analyzer = NetworkAnalyzer(
            is_anomalous=self.is_anomalous,
            K=10,
            T=60,
            inactivity_timeout=300,
            feature_window=60
        )

    def test_single_normal_flow(self):
        self.is_anomalous.return_value = False
        packet = {
            'timestamp': time.time(),
            'src_ip': '192.168.1.1',
            'dst_ip': '10.0.0.1',
            'src_port': 54321,
            'dst_port': 80,
            'protocol': 'TCP',
            'packet_size': 1500,
            'flags': {'SYN': True, 'ACK': False}
        }
        self.analyzer.process_packet(packet)
        self.assertEqual(len(self.analyzer.get_anomalous_flows()), 0)

    def test_single_anomalous_flow(self):
        self.is_anomalous.return_value = True
        packet = {
            'timestamp': time.time(),
            'src_ip': '192.168.1.2',
            'dst_ip': '10.0.0.2',
            'src_port': 12345,
            'dst_port': 443,
            'protocol': 'TCP',
            'packet_size': 5000,
            'flags': {'SYN': True, 'ACK': False}
        }
        self.analyzer.process_packet(packet)
        self.assertEqual(len(self.analyzer.get_anomalous_flows()), 1)

    def test_rate_limiting(self):
        self.is_anomalous.return_value = True
        current_time = time.time()
        
        # Process K+1 packets within T seconds
        for i in range(11):
            packet = {
                'timestamp': current_time + i*0.1,
                'src_ip': f'192.168.1.{i}',
                'dst_ip': f'10.0.0.{i}',
                'src_port': 50000 + i,
                'dst_port': 80 + i,
                'protocol': 'TCP',
                'packet_size': 1000 + i*100,
                'flags': {'SYN': True, 'ACK': False}
            }
            self.analyzer.process_packet(packet)
        
        # Should only report K flows
        self.assertEqual(len(self.analyzer.get_anomalous_flows()), 10)

    def test_flow_inactivity(self):
        self.is_anomalous.return_value = True
        current_time = time.time()
        
        # Process a packet
        packet1 = {
            'timestamp': current_time,
            'src_ip': '192.168.1.100',
            'dst_ip': '10.0.0.100',
            'src_port': 12345,
            'dst_port': 80,
            'protocol': 'TCP',
            'packet_size': 1500,
            'flags': {'SYN': True, 'ACK': False}
        }
        self.analyzer.process_packet(packet1)
        
        # Process another packet after inactivity timeout
        packet2 = {
            'timestamp': current_time + 301,
            'src_ip': '192.168.1.100',
            'dst_ip': '10.0.0.100',
            'src_port': 12345,
            'dst_port': 80,
            'protocol': 'TCP',
            'packet_size': 1500,
            'flags': {'SYN': False, 'ACK': True}
        }
        self.analyzer.process_packet(packet2)
        
        # Should treat as new flow
        self.assertEqual(len(self.analyzer.get_anomalous_flows()), 2)

    def test_feature_extraction(self):
        current_time = time.time()
        packets = [
            {
                'timestamp': current_time,
                'src_ip': '192.168.1.5',
                'dst_ip': '10.0.0.5',
                'src_port': 54321,
                'dst_port': 22,
                'protocol': 'TCP',
                'packet_size': 1000,
                'flags': {'SYN': True, 'ACK': False}
            },
            {
                'timestamp': current_time + 1,
                'src_ip': '192.168.1.5',
                'dst_ip': '10.0.0.5',
                'src_port': 54321,
                'dst_port': 22,
                'protocol': 'TCP',
                'packet_size': 500,
                'flags': {'SYN': False, 'ACK': True}
            },
            {
                'timestamp': current_time + 2,
                'src_ip': '192.168.1.5',
                'dst_ip': '10.0.0.5',
                'src_port': 54321,
                'dst_port': 22,
                'protocol': 'TCP',
                'packet_size': 1500,
                'flags': {'SYN': False, 'ACK': True}
            }
        ]
        
        for packet in packets:
            self.analyzer.process_packet(packet)
        
        # Verify features passed to is_anomalous
        args, _ = self.is_anomalous.call_args
        features = args[0]
        self.assertEqual(features['total_packets'], 3)
        self.assertEqual(features['total_bytes'], 3000)
        self.assertAlmostEqual(features['avg_packet_size'], 1000)
        self.assertAlmostEqual(features['packet_rate'], 3/60)
        self.assertAlmostEqual(features['byte_rate'], 3000/60)
        self.assertEqual(features['unique_dst_ports'], 1)
        self.assertAlmostEqual(features['syn_ratio'], 1/3)

    def test_non_tcp_protocol(self):
        self.is_anomalous.return_value = False
        packet = {
            'timestamp': time.time(),
            'src_ip': '192.168.1.10',
            'dst_ip': '10.0.0.10',
            'src_port': 12345,
            'dst_port': 53,
            'protocol': 'UDP',
            'packet_size': 512,
            'flags': {}
        }
        self.analyzer.process_packet(packet)
        args, _ = self.is_anomalous.call_args
        features = args[0]
        self.assertEqual(features['syn_ratio'], 0)

if __name__ == '__main__':
    unittest.main()