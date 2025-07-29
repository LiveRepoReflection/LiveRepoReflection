import unittest
from robust_routing import find_reliable_paths

class RobustRoutingTest(unittest.TestCase):
    def test_basic_network(self):
        N = 5
        edges = [
            (0, 1, 10, 0.05),
            (0, 2, 15, 0.1),
            (1, 2, 5, 0.02),
            (1, 3, 12, 0.08),
            (2, 4, 8, 0.03),
            (3, 4, 7, 0.01)
        ]
        result = find_reliable_paths(N, edges, 0, 4, 2, 40)
        self.assertEqual(len(result), 2)
        # Verify paths exist and are valid
        self.assertTrue(all(isinstance(path, list) for path in result))
        self.assertTrue(all(all(isinstance(node, int) for node in path) for path in result))

    def test_same_source_destination(self):
        N = 3
        edges = [
            (0, 1, 5, 0.1),
            (1, 2, 5, 0.1)
        ]
        result = find_reliable_paths(N, edges, 1, 1, 1, 10)
        self.assertEqual(result, [[1]])

    def test_no_path_exists(self):
        N = 4
        edges = [
            (0, 1, 5, 0.1),
            (2, 3, 5, 0.1)
        ]
        result = find_reliable_paths(N, edges, 0, 3, 1, 20)
        self.assertEqual(result, [])

    def test_latency_constraint(self):
        N = 3
        edges = [
            (0, 1, 15, 0.1),
            (1, 2, 15, 0.1)
        ]
        result = find_reliable_paths(N, edges, 0, 2, 1, 20)
        self.assertEqual(result, [])

    def test_large_k_value(self):
        N = 3
        edges = [
            (0, 1, 5, 0.1),
            (1, 2, 5, 0.1)
        ]
        result = find_reliable_paths(N, edges, 0, 2, 10, 20)
        self.assertEqual(len(result), 1)  # Should only return one path even though K=10

    def test_multiple_paths_same_reliability(self):
        N = 4
        edges = [
            (0, 1, 5, 0.1),
            (1, 3, 5, 0.1),
            (0, 2, 5, 0.1),
            (2, 3, 5, 0.1)
        ]
        result = find_reliable_paths(N, edges, 0, 3, 2, 20)
        self.assertEqual(len(result), 2)
        # Verify paths have same length (same reliability in this case)
        self.assertEqual(len(result[0]), len(result[1]))

    def test_disconnected_graph(self):
        N = 6
        edges = [
            (0, 1, 5, 0.1),
            (1, 2, 5, 0.1),
            (3, 4, 5, 0.1),
            (4, 5, 5, 0.1)
        ]
        result = find_reliable_paths(N, edges, 0, 5, 1, 20)
        self.assertEqual(result, [])

    def test_cyclic_graph(self):
        N = 4
        edges = [
            (0, 1, 5, 0.1),
            (1, 2, 5, 0.1),
            (2, 3, 5, 0.1),
            (1, 3, 5, 0.1),
            (2, 0, 5, 0.1)
        ]
        result = find_reliable_paths(N, edges, 0, 3, 2, 20)
        self.assertTrue(len(result) <= 2)
        # Verify no cycles in returned paths
        for path in result:
            self.assertEqual(len(set(path)), len(path))

    def test_numerical_stability(self):
        N = 10
        edges = [(i, i+1, 1, 0.001) for i in range(9)]
        result = find_reliable_paths(N, edges, 0, 9, 1, 20)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 0)
        self.assertEqual(result[0][-1], 9)

    def test_empty_edges(self):
        N = 5
        edges = []
        result = find_reliable_paths(N, edges, 0, 4, 2, 40)
        self.assertEqual(result, [])

    def test_invalid_input_validation(self):
        # Test negative latency
        with self.assertRaises((ValueError, AssertionError)):
            find_reliable_paths(5, [(0, 1, -5, 0.1)], 0, 4, 2, 40)
        
        # Test invalid probability
        with self.assertRaises((ValueError, AssertionError)):
            find_reliable_paths(5, [(0, 1, 5, 1.5)], 0, 4, 2, 40)
        
        # Test invalid node IDs
        with self.assertRaises((ValueError, AssertionError)):
            find_reliable_paths(5, [(0, 5, 5, 0.1)], 0, 4, 2, 40)

if __name__ == '__main__':
    unittest.main()