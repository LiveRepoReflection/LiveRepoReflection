import unittest
from network_anomaly import detect_anomalies

class NetworkAnomalyTest(unittest.TestCase):
    def test_basic_anomaly_detection(self):
        # Basic test case with obvious anomalies
        traffic_data = [
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1100, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 1200, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 5000, "protocol": "TCP", "flags": 1}, # Anomaly
            {"timestamp": 1678886404, "source_node": "C", "destination_node": "D", "packet_size": 500, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886405, "source_node": "C", "destination_node": "D", "packet_size": 600, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886406, "source_node": "C", "destination_node": "D", "packet_size": 700, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886407, "source_node": "C", "destination_node": "D", "packet_size": 100, "protocol": "UDP", "flags": 0}, # Anomaly
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Should detect 2 anomalies
        self.assertEqual(len(anomalies), 2)
        
        # First anomaly should be the 4th record
        self.assertEqual(anomalies[0]["timestamp"], 1678886403)
        self.assertEqual(anomalies[0]["source_node"], "A")
        self.assertEqual(anomalies[0]["destination_node"], "B")
        self.assertEqual(anomalies[0]["protocol"], "TCP")
        
        # Second anomaly should be the 8th record
        self.assertEqual(anomalies[1]["timestamp"], 1678886407)
        self.assertEqual(anomalies[1]["source_node"], "C")
        self.assertEqual(anomalies[1]["destination_node"], "D")
        self.assertEqual(anomalies[1]["protocol"], "UDP")
        
        # Each anomaly should have an anomaly score
        self.assertIn("anomaly_score", anomalies[0])
        self.assertIn("anomaly_score", anomalies[1])
        
        # Anomaly scores should be reasonable (greater than threshold)
        self.assertGreater(anomalies[0]["anomaly_score"], 3.0)
        self.assertGreater(anomalies[1]["anomaly_score"], 3.0)

    def test_no_anomalies(self):
        # Test case with consistent traffic, no anomalies
        traffic_data = [
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1050, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 950, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 1020, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886404, "source_node": "A", "destination_node": "B", "packet_size": 980, "protocol": "TCP", "flags": 1},
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Should detect 0 anomalies
        self.assertEqual(len(anomalies), 0)

    def test_insufficient_data(self):
        # Test case with single data point for each connection (insufficient for baseline)
        traffic_data = [
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "C", "destination_node": "D", "packet_size": 500, "protocol": "UDP", "flags": 0},
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Should not detect any anomalies due to insufficient data
        self.assertEqual(len(anomalies), 0)

    def test_gradual_shift(self):
        # Test case with gradual shift in packet size (shouldn't be flagged as anomalies)
        traffic_data = [
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1050, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 1100, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 1150, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886404, "source_node": "A", "destination_node": "B", "packet_size": 1200, "protocol": "TCP", "flags": 1},
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Gradual shifts should not be flagged as anomalies
        self.assertEqual(len(anomalies), 0)

    def test_multiple_connections(self):
        # Test multiple connections with different baselines
        traffic_data = [
            # Connection 1: Baseline ~1000
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 950, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 1050, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 4000, "protocol": "TCP", "flags": 1}, # Anomaly
            
            # Connection 2: Baseline ~500
            {"timestamp": 1678886404, "source_node": "C", "destination_node": "D", "packet_size": 480, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886405, "source_node": "C", "destination_node": "D", "packet_size": 500, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886406, "source_node": "C", "destination_node": "D", "packet_size": 520, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886407, "source_node": "C", "destination_node": "D", "packet_size": 1500, "protocol": "UDP", "flags": 0}, # Anomaly
            
            # Connection 3: Small baseline ~100
            {"timestamp": 1678886408, "source_node": "E", "destination_node": "F", "packet_size": 90, "protocol": "HTTP", "flags": 2},
            {"timestamp": 1678886409, "source_node": "E", "destination_node": "F", "packet_size": 100, "protocol": "HTTP", "flags": 2},
            {"timestamp": 1678886410, "source_node": "E", "destination_node": "F", "packet_size": 110, "protocol": "HTTP", "flags": 2},
            {"timestamp": 1678886411, "source_node": "E", "destination_node": "F", "packet_size": 400, "protocol": "HTTP", "flags": 2}, # Anomaly
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Should detect 3 anomalies (one for each connection)
        self.assertEqual(len(anomalies), 3)
        
        # Verify the anomalies are from different connections
        connection_keys = set()
        for anomaly in anomalies:
            key = (anomaly["source_node"], anomaly["destination_node"], anomaly["protocol"])
            connection_keys.add(key)
        
        self.assertEqual(len(connection_keys), 3)
        self.assertIn(("A", "B", "TCP"), connection_keys)
        self.assertIn(("C", "D", "UDP"), connection_keys)
        self.assertIn(("E", "F", "HTTP"), connection_keys)

    def test_zero_standard_deviation(self):
        # Test handling of zero standard deviation (all packets same size)
        traffic_data = [
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 2000, "protocol": "TCP", "flags": 1}, # Should be anomaly
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Should detect 1 anomaly despite zero standard deviation in first three packets
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["timestamp"], 1678886403)

    def test_large_dataset(self):
        # Test with larger dataset to ensure performance
        import random
        
        # Generate consistent baseline traffic with occasional anomalies
        traffic_data = []
        random.seed(42)  # For reproducibility
        
        # Generate 10 connections with 100 records each (total 1000 records)
        for i in range(10):
            source = f"Node{i}"
            dest = f"Node{i+1}"
            protocol = random.choice(["TCP", "UDP", "HTTP"])
            baseline = random.randint(500, 2000)
            
            # Generate mostly normal traffic
            for j in range(100):
                timestamp = 1678886400 + (i * 100) + j
                
                # Every 20th packet is an anomaly (5% anomaly rate)
                if j % 20 == 19:
                    # Anomaly: 3-5x baseline
                    packet_size = baseline * random.randint(3, 5)
                else:
                    # Normal: baseline ± 10%
                    packet_size = int(baseline * (1 + random.uniform(-0.1, 0.1)))
                
                traffic_data.append({
                    "timestamp": timestamp,
                    "source_node": source,
                    "destination_node": dest,
                    "packet_size": packet_size,
                    "protocol": protocol,
                    "flags": random.randint(0, 3)
                })
        
        anomalies = detect_anomalies(traffic_data)
        
        # There should be approximately 50 anomalies (10 connections × 5 anomalies per connection)
        # Allow some flexibility due to random initialization
        self.assertGreaterEqual(len(anomalies), 40)
        self.assertLessEqual(len(anomalies), 60)

    def test_mixed_protocols(self):
        # Test case with same source-destination but different protocols
        traffic_data = [
            # A->B with TCP protocol
            {"timestamp": 1678886400, "source_node": "A", "destination_node": "B", "packet_size": 1000, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886401, "source_node": "A", "destination_node": "B", "packet_size": 1100, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886402, "source_node": "A", "destination_node": "B", "packet_size": 1200, "protocol": "TCP", "flags": 1},
            {"timestamp": 1678886403, "source_node": "A", "destination_node": "B", "packet_size": 5000, "protocol": "TCP", "flags": 1}, # Anomaly
            
            # A->B with UDP protocol (different baseline)
            {"timestamp": 1678886404, "source_node": "A", "destination_node": "B", "packet_size": 200, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886405, "source_node": "A", "destination_node": "B", "packet_size": 250, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886406, "source_node": "A", "destination_node": "B", "packet_size": 300, "protocol": "UDP", "flags": 0},
            {"timestamp": 1678886407, "source_node": "A", "destination_node": "B", "packet_size": 1200, "protocol": "UDP", "flags": 0}, # Anomaly
        ]
        
        anomalies = detect_anomalies(traffic_data)
        
        # Should detect 2 anomalies
        self.assertEqual(len(anomalies), 2)
        
        # Verify that both protocol types are represented
        protocols = [a["protocol"] for a in anomalies]
        self.assertIn("TCP", protocols)
        self.assertIn("UDP", protocols)

if __name__ == '__main__':
    unittest.main()