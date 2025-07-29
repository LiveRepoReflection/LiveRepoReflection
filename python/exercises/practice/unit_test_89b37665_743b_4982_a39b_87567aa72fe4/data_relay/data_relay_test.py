import unittest
from data_relay import compute_max_transfer_rate

class DataRelayTest(unittest.TestCase):
    def test_direct_connection(self):
        # Direct connection from source (0) to destination (1)
        N = 2
        edges = [(0, 1, 100, 20)]
        server_capacities = [150, 150]
        source = 0
        destination = 1
        data_size = 50
        max_latency = 30
        k = 1
        expected = 100  # min(100 from edge, 150 from servers)
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

    def test_two_path_choice(self):
        # Two available paths: 0->1->2 and 0->3->2, choose the one with the maximum achievable rate
        N = 4
        edges = [(0, 1, 50, 10), (1, 2, 60, 15), (0, 3, 40, 20), (3, 2, 70, 25)]
        server_capacities = [100, 80, 90, 75]
        source = 0
        destination = 2
        data_size = 50
        max_latency = 50
        k = 3
        # Path 0->1->2: edge min = 50, servers min = 80, rate = 50
        # Path 0->3->2: edge min = 40, servers min = 75, rate = 40
        expected = 50
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)
        
    def test_latency_constraint(self):
        # Only one path meets the latency constraint.
        N = 4
        edges = [(0, 1, 100, 40), (1, 2, 80, 30), (0, 3, 50, 10), (3, 2, 90, 15)]
        server_capacities = [120, 100, 110, 60]
        source = 0
        destination = 2
        data_size = 20
        max_latency = 50  # Path 0->1->2 latency = 70 (invalid), 0->3->2 latency = 25 (valid)
        k = 2
        # For path 0->3->2: edge min = min(50,90)=50, servers min = min(120,60,110)=60, rate = 50
        expected = 50
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

    def test_hop_constraint(self):
        # Only a path with a higher hop count would provide a higher rate, but hop constraint forces a lower rate.
        N = 5
        edges = [(0, 1, 100, 10), (1, 2, 100, 10), (2, 3, 100, 10), (3, 4, 100, 10), (0, 4, 30, 40)]
        server_capacities = [110, 110, 110, 110, 110]
        source = 0
        destination = 4
        data_size = 100
        max_latency = 50
        k = 2  # The multi-hop path (0->1->2->3->4) is not allowed.
        # Only valid path is direct: 0->4 with rate = min(30, min(110,110)) = 30.
        expected = 30
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

    def test_no_valid_path(self):
        # Graph where the only available path violates the latency constraint.
        N = 3
        edges = [(0, 1, 50, 60), (1, 2, 50, 60)]
        server_capacities = [100, 100, 100]
        source = 0
        destination = 2
        data_size = 10
        max_latency = 100  # Only path 0->1->2 has latency 120, which violates constraint.
        k = 2
        expected = 0
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

    def test_source_equals_destination(self):
        # When source and destination are the same, rate should be the capacity of that single server.
        N = 1
        edges = []
        server_capacities = [200]
        source = 0
        destination = 0
        data_size = 10
        max_latency = 10
        k = 1
        expected = 200
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

    def test_exact_latency_boundary(self):
        # Test a case where the total latency is exactly the maximum allowed.
        N = 3
        edges = [(0, 1, 70, 25), (1, 2, 80, 25)]
        server_capacities = [100, 90, 100]
        source = 0
        destination = 2
        data_size = 100
        max_latency = 50  # Latency exactly equals 25+25.
        k = 2
        # Rate = min(min(70,80), min(100,90,100)) = min(70,90) = 70.
        expected = 70
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)
        
    def test_multiple_paths_tradeoff(self):
        # Multiple valid paths with trade-offs (bandwidth vs latency).
        N = 5
        edges = [
            (0, 1, 100, 15), (1, 4, 40, 20),
            (0, 2, 60, 10), (2, 3, 55, 20), (3, 4, 70, 15),
            (0, 4, 30, 30)
        ]
        server_capacities = [120, 80, 90, 100, 110]
        source = 0
        destination = 4
        data_size = 200
        max_latency = 50
        k = 3
        # Path 0->1->4: latency = 15+20=35, rate = min(100,40, min(120,80,110)=80) = 40.
        # Path 0->2->3->4: latency = 10+20+15=45, rate = min(60,55,70, min(120,90,100,110)=90) = 55.
        # Path 0->4: latency = 30, rate = min(30, min(120,110)=110) = 30.
        # The best achievable rate is 55.
        expected = 55
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

    def test_server_capacity_limit(self):
        # Test where the server capacity is the limiting factor rather than edge bandwidth.
        N = 3
        edges = [(0, 1, 200, 10), (1, 2, 200, 10)]
        server_capacities = [150, 100, 150]
        source = 0
        destination = 2
        data_size = 50
        max_latency = 30
        k = 2
        # Rate = min(min(edge: 200,200)=200, min(150,100,150)=100) = 100.
        expected = 100
        result = compute_max_transfer_rate(N, edges, server_capacities, source, destination, data_size, max_latency, k)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()