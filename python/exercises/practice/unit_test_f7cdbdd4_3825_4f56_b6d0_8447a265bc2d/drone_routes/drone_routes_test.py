import unittest
from drone_routes import find_optimal_route

class DroneRoutesTest(unittest.TestCase):
    def test_simple_path(self):
        graph = {
            0: {1: 10, 2: 5},
            1: {2: 2, 3: 8},
            2: {3: 15},
            3: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 3, 3), [0, 1, 3])

    def test_direct_path_is_optimal(self):
        graph = {
            0: {1: 10, 2: 5, 3: 4},
            1: {2: 2, 3: 8},
            2: {3: 15},
            3: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 3, 1), [0, 3])

    def test_longer_path_but_lower_bottleneck(self):
        graph = {
            0: {1: 20, 4: 10},
            1: {2: 5},
            2: {3: 8},
            3: {},
            4: {3: 9}
        }
        self.assertEqual(find_optimal_route(graph, 0, 3, 4), [0, 4, 3])

    def test_max_hops_constraint(self):
        graph = {
            0: {1: 5},
            1: {2: 5},
            2: {3: 5},
            3: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 3, 3), [0, 1, 2, 3])
        self.assertIsNone(find_optimal_route(graph, 0, 3, 2))

    def test_no_path_exists(self):
        graph = {
            0: {1: 10},
            1: {2: 5},
            3: {}
        }
        self.assertIsNone(find_optimal_route(graph, 0, 3, 5))

    def test_disconnected_graph(self):
        graph = {
            0: {1: 10},
            1: {},
            2: {3: 5},
            3: {}
        }
        self.assertIsNone(find_optimal_route(graph, 0, 2, 5))

    def test_path_with_cycle(self):
        graph = {
            0: {1: 10},
            1: {2: 5, 0: 3},
            2: {3: 2},
            3: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 3, 4), [0, 1, 2, 3])

    def test_multiple_paths_same_bottleneck(self):
        # When multiple paths have the same bottleneck cost,
        # we expect any of them to be returned
        graph = {
            0: {1: 10, 2: 10},
            1: {3: 10},
            2: {3: 10},
            3: {}
        }
        result = find_optimal_route(graph, 0, 3, 2)
        self.assertTrue(result == [0, 1, 3] or result == [0, 2, 3])

    def test_zero_hops_same_node(self):
        graph = {
            0: {1: 10},
            1: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 0, 0), [0])
        self.assertIsNone(find_optimal_route(graph, 0, 1, 0))

    def test_complex_graph(self):
        graph = {
            0: {1: 7, 2: 9, 5: 14},
            1: {2: 10, 3: 15},
            2: {3: 11, 5: 2},
            3: {4: 6},
            4: {5: 9},
            5: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 5, 3), [0, 2, 5])

    def test_large_graph(self):
        # Create a linear graph with 100 nodes where each edge has cost i+1
        graph = {}
        for i in range(99):
            graph[i] = {i+1: i+1}
        graph[99] = {}
        
        # Test finding a path with varying max_hops
        self.assertEqual(find_optimal_route(graph, 0, 5, 5), [0, 1, 2, 3, 4, 5])
        self.assertIsNone(find_optimal_route(graph, 0, 5, 4))
        
        # Test finding a path with exactly enough hops
        self.assertEqual(find_optimal_route(graph, 0, 10, 10), 
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_empty_graph(self):
        graph = {}
        self.assertIsNone(find_optimal_route(graph, 0, 3, 5))

    def test_negative_costs(self):
        # Edge costs should be positive, but let's test handling invalid inputs
        graph = {
            0: {1: -10},
            1: {2: 5},
            2: {}
        }
        with self.assertRaises(ValueError):
            find_optimal_route(graph, 0, 2, 2)

    def test_graph_with_self_loops(self):
        graph = {
            0: {0: 1, 1: 10},
            1: {2: 5},
            2: {2: 3, 3: 2},
            3: {}
        }
        self.assertEqual(find_optimal_route(graph, 0, 3, 5), [0, 1, 2, 3])

if __name__ == '__main__':
    unittest.main()