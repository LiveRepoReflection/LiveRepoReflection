import unittest
from path_optim import find_optimal_path

class TestPathOptim(unittest.TestCase):
    def setUp(self):
        # Define a constant MAX_TRAFFIC used in tests
        self.MAX_TRAFFIC = 100

    def test_same_node(self):
        # When source and target are the same, the optimal path is just the single node.
        graph = {0: []}
        result = find_optimal_path(graph, 0, 0, 0.5, 0.5, 10, self.MAX_TRAFFIC)
        self.assertEqual(result, [0])

    def test_simple_path(self):
        # A simple one-edge path from 0 to 1
        graph = {
            0: [{
                'to': 1,
                'length': 100,
                'speed_limit': 10,
                'traffic_density': 0,
                'toll_cost': 5,
                'fuel_consumption_rate': 0.1
            }],
            1: []
        }
        # Fuel consumption = 100 * 0.1 = 10, max_fuel is exactly 10.
        result = find_optimal_path(graph, 0, 1, 1, 0, 10, self.MAX_TRAFFIC)
        self.assertEqual(result, [0, 1])

    def test_no_valid_path_due_to_fuel(self):
        # Available fuel is too low for the only edge (requires 10 fuel, available 5).
        graph = {
            0: [{
                'to': 1,
                'length': 100,
                'speed_limit': 10,
                'traffic_density': 0,
                'toll_cost': 5,
                'fuel_consumption_rate': 0.1
            }],
            1: []
        }
        result = find_optimal_path(graph, 0, 1, 1, 0, 5, self.MAX_TRAFFIC)
        self.assertEqual(result, [])

    def test_impossible_due_to_traffic(self):
        # The road is impassable because traffic_density >= MAX_TRAFFIC.
        graph = {
            0: [{
                'to': 1,
                'length': 100,
                'speed_limit': 10,
                'traffic_density': self.MAX_TRAFFIC,
                'toll_cost': 5,
                'fuel_consumption_rate': 0.1
            }],
            1: []
        }
        result = find_optimal_path(graph, 0, 1, 1, 0, 20, self.MAX_TRAFFIC)
        self.assertEqual(result, [])

    def test_with_cycles(self):
        # Graph has a cycle: 0 -> 1 -> 2 -> 0 and an exit path 1 -> 3.
        graph = {
            0: [{
                'to': 1,
                'length': 50,
                'speed_limit': 10,
                'traffic_density': 10,
                'toll_cost': 2,
                'fuel_consumption_rate': 0.1
            }],
            1: [
                {
                    'to': 2,
                    'length': 50,
                    'speed_limit': 10,
                    'traffic_density': 10,
                    'toll_cost': 2,
                    'fuel_consumption_rate': 0.1
                },
                {
                    'to': 3,
                    'length': 100,
                    'speed_limit': 10,
                    'traffic_density': 5,
                    'toll_cost': 5,
                    'fuel_consumption_rate': 0.1
                }
            ],
            2: [{
                'to': 0,
                'length': 50,
                'speed_limit': 10,
                'traffic_density': 10,
                'toll_cost': 2,
                'fuel_consumption_rate': 0.1
            }],
            3: []
        }
        result = find_optimal_path(graph, 0, 3, 0.7, 0.3, 20, self.MAX_TRAFFIC)
        # Expect the optimal path to be: 0 -> 1 -> 3
        self.assertEqual(result, [0, 1, 3])

    def test_invalid_nodes(self):
        # Test case when target node is not present in the graph.
        graph = {0: []}
        result = find_optimal_path(graph, 0, 1, 0.5, 0.5, 10, self.MAX_TRAFFIC)
        self.assertEqual(result, [])

    def test_multiple_paths_trade_off(self):
        # Two potential routes with different trade-offs:
        # Route 1 (0 -> 1 -> 3): fast but high toll cost.
        # Route 2 (0 -> 2 -> 3): slower but lower toll cost.
        graph = {
            0: [
                {
                    'to': 1,
                    'length': 50,
                    'speed_limit': 20,
                    'traffic_density': 0,
                    'toll_cost': 10,
                    'fuel_consumption_rate': 0.05
                },
                {
                    'to': 2,
                    'length': 100,
                    'speed_limit': 10,
                    'traffic_density': 0,
                    'toll_cost': 2,
                    'fuel_consumption_rate': 0.05
                }
            ],
            1: [{
                'to': 3,
                'length': 50,
                'speed_limit': 20,
                'traffic_density': 0,
                'toll_cost': 10,
                'fuel_consumption_rate': 0.05
            }],
            2: [{
                'to': 3,
                'length': 100,
                'speed_limit': 10,
                'traffic_density': 0,
                'toll_cost': 2,
                'fuel_consumption_rate': 0.05
            }],
            3: []
        }
        # Case 1: Emphasize travel time (time_weight=1, cost_weight=0)
        result1 = find_optimal_path(graph, 0, 3, 1, 0, 20, self.MAX_TRAFFIC)
        self.assertEqual(result1, [0, 1, 3])
        
        # Case 2: Emphasize toll cost (time_weight=0, cost_weight=1)
        result2 = find_optimal_path(graph, 0, 3, 0, 1, 20, self.MAX_TRAFFIC)
        self.assertEqual(result2, [0, 2, 3])

    def test_self_loop(self):
        # Test graph with a self-loop on node 0.
        graph = {
            0: [
                {
                    'to': 0,
                    'length': 10,
                    'speed_limit': 10,
                    'traffic_density': 0,
                    'toll_cost': 1,
                    'fuel_consumption_rate': 0.1
                },
                {
                    'to': 1,
                    'length': 100,
                    'speed_limit': 10,
                    'traffic_density': 0,
                    'toll_cost': 5,
                    'fuel_consumption_rate': 0.1
                }
            ],
            1: []
        }
        result = find_optimal_path(graph, 0, 1, 0.5, 0.5, 15, self.MAX_TRAFFIC)
        # Optimal path should be the direct route 0 -> 1 rather than looping.
        self.assertEqual(result, [0, 1])

if __name__ == '__main__':
    unittest.main()