import unittest
from network_paths import find_k_edge_disjoint_paths

class TestNetworkPaths(unittest.TestCase):
    def test_simple_graph(self):
        N = 4
        edges = [
            (0, 1, 10, 2),
            (0, 2, 5, 1),
            (1, 3, 8, 3),
            (2, 3, 7, 2)
        ]
        result = find_k_edge_disjoint_paths(N, edges, 0, 3, 2)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(path[0][0] == 0 and path[0][-1] == 3 for path in result))
        self.assertTrue(all(path[1] > 0 for path in result))
        self.assertTrue(all(path[2] > 0 for path in result))

    def test_no_path_exists(self):
        N = 3
        edges = [
            (0, 1, 5, 1),
            (1, 2, 5, 1)
        ]
        result = find_k_edge_disjoint_paths(N, edges, 0, 2, 2)
        self.assertEqual(result, [])

    def test_insufficient_paths(self):
        N = 4
        edges = [
            (0, 1, 10, 1),
            (0, 2, 10, 1),
            (1, 3, 10, 1),
            (2, 3, 10, 1)
        ]
        result = find_k_edge_disjoint_paths(N, edges, 0, 3, 3)
        self.assertEqual(result, [])

    def test_complex_graph(self):
        N = 6
        edges = [
            (0, 1, 10, 1),
            (0, 2, 5, 2),
            (1, 3, 7, 3),
            (2, 3, 8, 1),
            (3, 4, 12, 2),
            (3, 5, 3, 4),
            (1, 5, 5, 2),
            (2, 4, 2, 3),
            (4, 5, 9, 1)
        ]
        result = find_k_edge_disjoint_paths(N, edges, 0, 5, 2)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(path[0][0] == 0 and path[0][-1] == 5 for path in result))
        self.assertTrue(all(path[1] > 0 for path in result))
        self.assertTrue(all(path[2] > 0 for path in result))
        # Verify edge disjointness
        all_edges = set()
        for path in result:
            edges_in_path = list(zip(path[0][:-1], path[0][1:]))
            for edge in edges_in_path:
                self.assertNotIn(edge, all_edges)
                all_edges.add(edge)

    def test_cyclic_graph(self):
        N = 4
        edges = [
            (0, 1, 10, 1),
            (1, 2, 10, 1),
            (2, 3, 10, 1),
            (3, 1, 10, 1),
            (0, 3, 15, 2)
        ]
        result = find_k_edge_disjoint_paths(N, edges, 0, 3, 2)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(path[0][0] == 0 and path[0][-1] == 3 for path in result))
        self.assertTrue(all(path[1] > 0 for path in result))
        self.assertTrue(all(path[2] > 0 for path in result))

    def test_single_node(self):
        N = 1
        edges = []
        result = find_k_edge_disjoint_paths(N, edges, 0, 0, 1)
        self.assertEqual(result, [([0], 0, float('inf'))])

    def test_empty_graph(self):
        N = 3
        edges = []
        result = find_k_edge_disjoint_paths(N, edges, 0, 2, 1)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()