import unittest
from adaptive_load_balancing import distribute_requests

class TestAdaptiveLoadBalancing(unittest.TestCase):
    def test_basic_case(self):
        N = 2
        M = 1
        server_capacities = [100, 150]
        initial_loads = [20, 30]
        latency_matrix = [[0.5, 1.0]]
        requests = 200
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(result, [80, 120])

    def test_insufficient_capacity(self):
        N = 2
        M = 1
        server_capacities = [100, 150]
        initial_loads = [90, 140]
        latency_matrix = [[0.5, 1.0]]
        requests = 100
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(sum(result), 20)  # Only 20 can be assigned (10+10)

    def test_multiple_load_balancers(self):
        N = 3
        M = 2
        server_capacities = [100, 200, 150]
        initial_loads = [50, 100, 75]
        latency_matrix = [
            [0.5, 1.0, 0.8],
            [0.7, 0.9, 0.6]
        ]
        requests = 300
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(sum(result), 225)  # Total capacity available

    def test_equal_latency(self):
        N = 2
        M = 1
        server_capacities = [100, 100]
        initial_loads = [0, 0]
        latency_matrix = [[1.0, 1.0]]
        requests = 150
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(result, [75, 75])  # Should split evenly

    def test_large_scale(self):
        N = 1000
        M = 10
        server_capacities = [100] * N
        initial_loads = [0] * N
        latency_matrix = [[0.5] * N for _ in range(M)]
        requests = 50000
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(sum(result), 50000)
        self.assertTrue(all(0 <= x <= 100 for x in result))

    def test_zero_requests(self):
        N = 2
        M = 1
        server_capacities = [100, 150]
        initial_loads = [20, 30]
        latency_matrix = [[0.5, 1.0]]
        requests = 0
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(result, [0, 0])

    def test_server_at_capacity(self):
        N = 3
        M = 1
        server_capacities = [100, 100, 100]
        initial_loads = [100, 50, 0]
        latency_matrix = [[0.5, 1.0, 2.0]]
        requests = 100
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(result[0], 0)  # Server 0 is at capacity
        self.assertEqual(sum(result), 100)

    def test_complex_latency(self):
        N = 4
        M = 3
        server_capacities = [200, 200, 200, 200]
        initial_loads = [50, 100, 150, 0]
        latency_matrix = [
            [1.0, 2.0, 3.0, 0.5],
            [2.0, 1.0, 0.5, 3.0],
            [3.0, 0.5, 1.0, 2.0]
        ]
        requests = 300
        result = distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests)
        self.assertEqual(sum(result), 300)
        # Should prefer servers with lower latency from any LB
        self.assertTrue(result[3] > result[0])  # Server 3 has lowest latency from LB0

if __name__ == '__main__':
    unittest.main()