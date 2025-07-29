import unittest
from drone_delivery import find_optimal_route

class DroneDeliveryTest(unittest.TestCase):
    def setUp(self):
        # Basic test graph setup
        self.basic_graph = {
            1: {
                'coordinates': (0.0, 0.0),
                'capacity': 2,
                'edges': [(2, 5.0, 1.0), (3, 3.0, 1.0)]
            },
            2: {
                'coordinates': (5.0, 0.0),
                'capacity': 2,
                'edges': [(4, 4.0, 1.0)]
            },
            3: {
                'coordinates': (0.0, 3.0),
                'capacity': 2,
                'edges': [(4, 6.0, 1.0)]
            },
            4: {
                'coordinates': (5.0, 3.0),
                'capacity': 2,
                'edges': []
            }
        }

        # Complex test graph with more nodes and varying congestion
        self.complex_graph = {
            1: {
                'coordinates': (0.0, 0.0),
                'capacity': 3,
                'edges': [(2, 4.0, 1.5), (3, 3.0, 1.2), (4, 6.0, 1.0)]
            },
            2: {
                'coordinates': (4.0, 0.0),
                'capacity': 2,
                'edges': [(5, 5.0, 1.1), (6, 4.0, 1.3)]
            },
            3: {
                'coordinates': (0.0, 3.0),
                'capacity': 4,
                'edges': [(4, 4.0, 1.4), (5, 7.0, 1.0)]
            },
            4: {
                'coordinates': (6.0, 3.0),
                'capacity': 2,
                'edges': [(6, 3.0, 1.2)]
            },
            5: {
                'coordinates': (4.0, 5.0),
                'capacity': 3,
                'edges': [(6, 2.0, 1.1)]
            },
            6: {
                'coordinates': (6.0, 5.0),
                'capacity': 4,
                'edges': []
            }
        }

    def test_same_source_and_destination(self):
        """Test when source and destination are the same"""
        result = find_optimal_route(
            self.basic_graph, 1, 1, 100.0,
            {1: 0, 2: 0, 3: 0, 4: 0}
        )
        self.assertEqual(result, [])

    def test_direct_path(self):
        """Test finding a direct path between two nodes"""
        result = find_optimal_route(
            self.basic_graph, 1, 2, 10.0,
            {1: 0, 2: 0, 3: 0, 4: 0}
        )
        self.assertEqual(result, [1, 2])

    def test_indirect_path(self):
        """Test finding an indirect path between nodes"""
        result = find_optimal_route(
            self.basic_graph, 1, 4, 15.0,
            {1: 0, 2: 0, 3: 0, 4: 0}
        )
        self.assertIn(result, [[1, 2, 4], [1, 3, 4]])

    def test_insufficient_battery(self):
        """Test when battery capacity is insufficient"""
        result = find_optimal_route(
            self.basic_graph, 1, 4, 3.0,
            {1: 0, 2: 0, 3: 0, 4: 0}
        )
        self.assertIsNone(result)

    def test_hub_at_capacity(self):
        """Test routing with a hub at maximum capacity"""
        result = find_optimal_route(
            self.basic_graph, 1, 4, 15.0,
            {1: 0, 2: 2, 3: 0, 4: 0}  # Hub 2 is at capacity
        )
        self.assertEqual(result, [1, 3, 4])

    def test_no_possible_path(self):
        """Test when no path exists between nodes"""
        result = find_optimal_route(
            self.basic_graph, 4, 1, 100.0,
            {1: 0, 2: 0, 3: 0, 4: 0}
        )
        self.assertIsNone(result)

    def test_complex_routing(self):
        """Test routing in a more complex graph"""
        result = find_optimal_route(
            self.complex_graph, 1, 6, 20.0,
            {1: 0, 2: 1, 3: 2, 4: 0, 5: 1, 6: 0}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[-1], 6)

    def test_high_congestion(self):
        """Test routing with high congestion factors"""
        modified_graph = self.complex_graph.copy()
        modified_graph[1]['edges'] = [(2, 4.0, 3.0), (3, 3.0, 2.5), (4, 6.0, 2.0)]
        result = find_optimal_route(
            modified_graph, 1, 6, 30.0,
            {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        )
        self.assertIsNotNone(result)

    def test_full_network_congestion(self):
        """Test routing when all paths have high congestion"""
        modified_graph = self.basic_graph.copy()
        for hub in modified_graph.values():
            hub['edges'] = [(dest, dist, 5.0) for dest, dist, _ in hub['edges']]
        result = find_optimal_route(
            modified_graph, 1, 4, 50.0,
            {1: 0, 2: 0, 3: 0, 4: 0}
        )
        self.assertIsNotNone(result)

    def test_edge_case_single_node(self):
        """Test with a graph containing only one node"""
        single_node_graph = {
            1: {
                'coordinates': (0.0, 0.0),
                'capacity': 1,
                'edges': []
            }
        }
        result = find_optimal_route(
            single_node_graph, 1, 1, 10.0,
            {1: 0}
        )
        self.assertEqual(result, [])

    def test_maximum_capacity_all_hubs(self):
        """Test when all hubs are at maximum capacity"""
        result = find_optimal_route(
            self.basic_graph, 1, 4, 15.0,
            {1: 2, 2: 2, 3: 2, 4: 2}
        )
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()