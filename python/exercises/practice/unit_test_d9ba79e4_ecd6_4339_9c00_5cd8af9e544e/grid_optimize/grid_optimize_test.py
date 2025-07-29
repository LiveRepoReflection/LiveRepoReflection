import unittest
from grid_optimize import optimize_grid

class TestGridOptimize(unittest.TestCase):
    def test_simple_direct_flow(self):
        # Two substations with a direct connection.
        n = 2
        connections = [(0, 1, 5, 2)]
        demand = [-3, 3]
        max_latency = 1
        # Expected cost: 3 units * cost 2 = 6
        self.assertEqual(optimize_grid(n, connections, demand, max_latency), 6)

    def test_impossible_due_to_latency(self):
        # Three substations in a line: 0 -> 1 -> 2.
        # Latency constraint is 1 while the only possible flow from 0 to 2 needs latency 2.
        n = 3
        connections = [(0, 1, 10, 1), (1, 2, 10, 1)]
        demand = [-5, 0, 5]
        max_latency = 1
        # Flow cannot be routed due to latency constraint.
        self.assertEqual(optimize_grid(n, connections, demand, max_latency), -1)

    def test_multiple_paths_min_cost(self):
        # Three substations with two alternative paths from 0 to 2.
        n = 3
        connections = [
            (0, 1, 10, 4),
            (1, 2, 10, 4),
            (0, 2, 10, 10)
        ]
        demand = [-6, 0, 6]
        max_latency = 2
        # Optimal flow uses 0->1->2 with cost = 6*(4+4) = 48.
        self.assertEqual(optimize_grid(n, connections, demand, max_latency), 48)

    def test_complex_network(self):
        # A more advanced grid with five substations.
        n = 5
        connections = [
            (0, 1, 10, 2),
            (1, 2, 8, 3),
            (2, 3, 5, 5),
            (3, 4, 10, 1),
            (0, 2, 6, 4),
            (1, 3, 10, 2),
            (2, 4, 6, 3)
        ]
        # Supply at node 0: 5, supply at node 1: 3, demand at node 3: 4, demand at node 4: 4.
        demand = [-5, -3, 0, 4, 4]
        max_latency = 3
        # One possible optimal routing:
        #   4 units from node 0 to node 3 via (0,1) and (1,3): cost = 4*(2+2) = 16.
        #   1 unit from node 0 to node 4 via (0,1,3,4): cost = 1*(2+2+1) = 5.
        #   3 units from node 1 to node 4 via (1,3,4): cost = 3*(2+1) = 9.
        # Total expected cost = 16 + 5 + 9 = 30.
        expected = 30
        self.assertEqual(optimize_grid(n, connections, demand, max_latency), expected)

    def test_zero_demand(self):
        # All substations have zero demand, no transfer is needed.
        n = 3
        connections = [(0, 1, 5, 1), (1, 2, 5, 1)]
        demand = [0, 0, 0]
        max_latency = 2
        # Expected cost is 0.
        self.assertEqual(optimize_grid(n, connections, demand, max_latency), 0)

if __name__ == '__main__':
    unittest.main()