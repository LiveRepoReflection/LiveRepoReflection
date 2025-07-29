import unittest
from resource_flow.resource_flow import optimize_resource_allocation

class TestResourceFlow(unittest.TestCase):
    def test_simple_feasible_case(self):
        nodes = [
            {'id': 1, 'capacity': 100, 'demand': 50},
            {'id': 2, 'capacity': 100, 'demand': -30},
            {'id': 3, 'capacity': 100, 'demand': -20}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 40, 'cost': 1.0},
            {'source': 1, 'destination': 3, 'capacity': 60, 'cost': 2.0}
        ]
        total_resources = 100
        result = optimize_resource_allocation(nodes, edges, total_resources)
        expected = {
            (1, 2): 30.0,
            (1, 3): 20.0
        }
        self.assertEqual(result, expected)

    def test_infeasible_case(self):
        nodes = [
            {'id': 1, 'capacity': 50, 'demand': 100},
            {'id': 2, 'capacity': 50, 'demand': -150}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 200, 'cost': 1.0}
        ]
        total_resources = 200
        self.assertIsNone(optimize_resource_allocation(nodes, edges, total_resources))

    def test_multiple_paths_optimal_choice(self):
        nodes = [
            {'id': 1, 'capacity': 100, 'demand': 50},
            {'id': 2, 'capacity': 100, 'demand': -50},
            {'id': 3, 'capacity': 100, 'demand': 0}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 30, 'cost': 5.0},
            {'source': 1, 'destination': 3, 'capacity': 40, 'cost': 1.0},
            {'source': 3, 'destination': 2, 'capacity': 40, 'cost': 1.0}
        ]
        total_resources = 100
        result = optimize_resource_allocation(nodes, edges, total_resources)
        expected = {
            (1, 3): 40.0,
            (3, 2): 40.0,
            (1, 2): 10.0
        }
        self.assertEqual(result, expected)

    def test_node_capacity_constraints(self):
        nodes = [
            {'id': 1, 'capacity': 30, 'demand': 50},
            {'id': 2, 'capacity': 100, 'demand': -50}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 100, 'cost': 1.0}
        ]
        total_resources = 100
        self.assertIsNone(optimize_resource_allocation(nodes, edges, total_resources))

    def test_edge_capacity_constraints(self):
        nodes = [
            {'id': 1, 'capacity': 100, 'demand': 50},
            {'id': 2, 'capacity': 100, 'demand': -50}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 30, 'cost': 1.0}
        ]
        total_resources = 100
        self.assertIsNone(optimize_resource_allocation(nodes, edges, total_resources))

    def test_complex_network(self):
        nodes = [
            {'id': 1, 'capacity': 200, 'demand': 100},
            {'id': 2, 'capacity': 100, 'demand': -40},
            {'id': 3, 'capacity': 100, 'demand': -60},
            {'id': 4, 'capacity': 50, 'demand': 0}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 50, 'cost': 3.0},
            {'source': 1, 'destination': 3, 'capacity': 80, 'cost': 5.0},
            {'source': 1, 'destination': 4, 'capacity': 100, 'cost': 1.0},
            {'source': 4, 'destination': 2, 'capacity': 60, 'cost': 2.0},
            {'source': 4, 'destination': 3, 'capacity': 40, 'cost': 4.0}
        ]
        total_resources = 200
        result = optimize_resource_allocation(nodes, edges, total_resources)
        self.assertTrue(isinstance(result, dict))
        self.assertAlmostEqual(sum(result.values()), 100, places=2)

    def test_zero_demand_nodes(self):
        nodes = [
            {'id': 1, 'capacity': 100, 'demand': 50},
            {'id': 2, 'capacity': 100, 'demand': 0},
            {'id': 3, 'capacity': 100, 'demand': -50}
        ]
        edges = [
            {'source': 1, 'destination': 2, 'capacity': 60, 'cost': 1.0},
            {'source': 2, 'destination': 3, 'capacity': 60, 'cost': 1.0}
        ]
        total_resources = 100
        result = optimize_resource_allocation(nodes, edges, total_resources)
        expected = {
            (1, 2): 50.0,
            (2, 3): 50.0
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()