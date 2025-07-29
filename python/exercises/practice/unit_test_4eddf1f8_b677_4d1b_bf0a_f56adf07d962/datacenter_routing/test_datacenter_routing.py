import unittest
import numpy as np
from datacenter_routing import optimize_routing

class TestDatacenterRouting(unittest.TestCase):
    def test_small_network(self):
        N = 3
        servers = [100, 200, 300]
        latency = [
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ]
        traffic = [
            [0, 50, 30],
            [40, 0, 60],
            [25, 45, 0]
        ]
        
        routing = optimize_routing(N, servers, latency, traffic)
        
        # Check dimensions
        self.assertEqual(routing.shape, (N, N, N))
        
        # Check constraints
        for i in range(N):
            for j in range(N):
                # Check if routing sum doesn't exceed traffic
                self.assertLessEqual(np.sum(routing[i][j]), traffic[i][j])
                
                # Check non-negative values
                for k in range(N):
                    self.assertGreaterEqual(routing[i][j][k], 0)

    def test_medium_network(self):
        N = 5
        servers = [100, 200, 300, 400, 500]
        latency = [
            [0, 10, 20, 30, 40],
            [10, 0, 15, 25, 35],
            [20, 15, 0, 18, 28],
            [30, 25, 18, 0, 22],
            [40, 35, 28, 22, 0]
        ]
        traffic = [
            [0, 50, 30, 20, 40],
            [40, 0, 60, 35, 25],
            [25, 45, 0, 50, 30],
            [35, 20, 40, 0, 55],
            [30, 40, 25, 45, 0]
        ]
        
        routing = optimize_routing(N, servers, latency, traffic)
        
        # Check dimensions
        self.assertEqual(routing.shape, (N, N, N))
        
        # Verify routing constraints
        for i in range(N):
            for j in range(N):
                self.assertLessEqual(np.sum(routing[i][j]), traffic[i][j])
                for k in range(N):
                    self.assertGreaterEqual(routing[i][j][k], 0)

    def test_edge_cases(self):
        # Test single datacenter
        N = 1
        servers = [100]
        latency = [[0]]
        traffic = [[0]]
        
        routing = optimize_routing(N, servers, latency, traffic)
        self.assertEqual(routing.shape, (1, 1, 1))
        self.assertEqual(routing[0][0][0], 0)

        # Test no traffic
        N = 3
        servers = [100, 200, 300]
        latency = [
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ]
        traffic = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        routing = optimize_routing(N, servers, latency, traffic)
        self.assertTrue(np.all(routing == 0))

    def test_cost_improvement(self):
        N = 4
        servers = [100, 200, 300, 400]
        latency = [
            [0, 100, 20, 30],
            [100, 0, 10, 40],
            [20, 10, 0, 50],
            [30, 40, 50, 0]
        ]
        traffic = [
            [0, 50, 30, 20],
            [40, 0, 60, 35],
            [25, 45, 0, 50],
            [35, 20, 40, 0]
        ]
        
        routing = optimize_routing(N, servers, latency, traffic)
        
        # Calculate direct routing cost
        direct_cost = sum(traffic[i][j] * latency[i][j] 
                         for i in range(N) 
                         for j in range(N) if i != j)
        
        # Calculate optimized routing cost
        optimized_cost = 0
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                # Direct routing cost
                direct_amount = traffic[i][j] - np.sum(routing[i][j])
                optimized_cost += direct_amount * latency[i][j]
                # Indirect routing cost through intermediate datacenters
                for k in range(N):
                    if k != i and k != j:
                        optimized_cost += routing[i][j][k] * (latency[i][k] + latency[k][j])
        
        # Optimized cost should be less than or equal to direct routing cost
        self.assertLessEqual(optimized_cost, direct_cost)

    def test_input_validation(self):
        # Test invalid dimensions
        with self.assertRaises(ValueError):
            optimize_routing(0, [], [], [])
        
        # Test mismatched dimensions
        N = 3
        servers = [100, 200]  # Wrong length
        latency = [[0, 1], [1, 0]]  # Wrong size
        traffic = [[0, 1, 2], [1, 0, 3], [2, 3, 0]]
        
        with self.assertRaises(ValueError):
            optimize_routing(N, servers, latency, traffic)

        # Test negative values
        N = 2
        servers = [100, 200]
        latency = [[0, -1], [1, 0]]  # Negative latency
        traffic = [[0, 1], [1, 0]]
        
        with self.assertRaises(ValueError):
            optimize_routing(N, servers, latency, traffic)

if __name__ == '__main__':
    unittest.main()