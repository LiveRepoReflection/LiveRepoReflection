import unittest
from flow_scheduler import min_cost_flow

class FlowSchedulerTest(unittest.TestCase):
    def test_example_case(self):
        # This test is based on the given example in the problem description.
        num_warehouses = 4
        edges = [
            (0, 1, 10, 1.0),  # Warehouse 0 to 1
            (0, 2, 5, 2.0),   # Warehouse 0 to 2
            (1, 3, 7, 1.5),   # Warehouse 1 to 3
            (2, 3, 8, 0.5)    # Warehouse 2 to 3
        ]
        commodities = [
            (0, 3, 6),       # Commodity from 0 to 3, demand 6
            (0, 3, 2)        # Commodity from 0 to 3, demand 2
        ]
        expected_cost = 20.0
        cost = min_cost_flow(num_warehouses, edges, commodities)
        self.assertAlmostEqual(cost, expected_cost, places=4)

    def test_insufficient_capacity(self):
        # Test the scenario where network capacities are insufficient to meet demand.
        num_warehouses = 3
        edges = [
            (0, 1, 3, 1.0),
            (1, 2, 3, 1.0)
        ]
        # Demand is greater than available capacity
        commodities = [
            (0, 2, 5)
        ]
        expected_cost = -1.0
        cost = min_cost_flow(num_warehouses, edges, commodities)
        self.assertEqual(cost, expected_cost)

    def test_parallel_edges(self):
        # Test the scenario where parallel edges exist between nodes.
        num_warehouses = 3
        edges = [
            (0, 1, 5, 2.0),
            (0, 1, 5, 1.0),  # Parallel edge with lower cost
            (1, 2, 10, 1.5)
        ]
        commodities = [
            (0, 2, 8)
        ]
        # Optimal strategy is to use as much as possible of the lower cost edge.
        # Expected cost calculation: Use 5 units from the cheaper edge (0,1) and 3 from the expensive edge.
        # Cost from 0 to 1: (5*1.0) + (3*2.0) = 5 + 6 = 11, then 8*1.5 = 12, total = 23.
        expected_cost = 23.0
        cost = min_cost_flow(num_warehouses, edges, commodities)
        self.assertAlmostEqual(cost, expected_cost, places=4)

    def test_multiple_commodities(self):
        # Test with multiple commodities sharing part of the network.
        num_warehouses = 5
        edges = [
            (0, 1, 10, 1.0),
            (1, 2, 8, 2.0),
            (2, 4, 10, 1.0),
            (0, 3, 5, 2.0),
            (3, 4, 5, 2.5),
            (1, 3, 7, 1.0),
            (3, 2, 7, 1.5)
        ]
        commodities = [
            (0, 4, 7),
            (0, 4, 3)
        ]
        # There may be multiple valid routing options; we verify that a valid minimum cost is computed.
        cost = min_cost_flow(num_warehouses, edges, commodities)
        # Assert that the function returns a float and not the failure flag.
        self.assertIsInstance(cost, float)
        self.assertGreaterEqual(cost, 0.0)

    def test_complex_network(self):
        # Test with a more complex network where multiple paths and cycles might exist.
        num_warehouses = 6
        edges = [
            (0, 1, 5, 1.0),
            (0, 2, 10, 2.0),
            (1, 3, 5, 1.5),
            (2, 3, 5, 0.5),
            (3, 4, 10, 1.0),
            (2, 5, 5, 2.5),
            (5, 4, 5, 1.0),
            (1, 5, 3, 2.0),
            (3, 5, 2, 0.5)
        ]
        commodities = [
            (0, 4, 8),
            (0, 4, 2)
        ]
        cost = min_cost_flow(num_warehouses, edges, commodities)
        self.assertIsInstance(cost, float)
        # The expected optimal cost is not trivial; we only verify the solution is computed and feasible.
        self.assertGreaterEqual(cost, 0.0)

    def test_minimal_demand(self):
        # Test with the smallest possible demand and network.
        num_warehouses = 2
        edges = [
            (0, 1, 1, 0.1)
        ]
        commodities = [
            (0, 1, 1)
        ]
        expected_cost = 0.1
        cost = min_cost_flow(num_warehouses, edges, commodities)
        self.assertAlmostEqual(cost, expected_cost, places=4)

if __name__ == '__main__':
    unittest.main()