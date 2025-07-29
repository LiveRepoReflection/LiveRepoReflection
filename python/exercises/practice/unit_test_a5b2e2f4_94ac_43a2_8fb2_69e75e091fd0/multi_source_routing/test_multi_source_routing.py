import unittest
from multi_source_routing import optimal_multi_source_routing

class TestMultiSourceRouting(unittest.TestCase):
    def test_single_source_direct_path(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 3)]
        S = {0}
        D = 2
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 8)

    def test_multi_source_optimal_path(self):
        N = 5
        edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (2, 3, 2), (3, 4, 4), (0, 4, 15)]
        S = {0, 1}
        D = 4
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 9)

    def test_no_path_exists(self):
        N = 4
        edges = [(0, 1, 2), (2, 3, 4)]
        S = {0, 2}
        D = 1
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 2)
        S = {2}
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), -1)

    def test_source_is_destination(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 3)]
        S = {2}
        D = 2
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 0)

    def test_large_graph_performance(self):
        N = 10**5
        edges = [(i, i+1, 1) for i in range(N-1)]
        S = {0}
        D = N-1
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), N-1)

    def test_multiple_edges_between_nodes(self):
        N = 3
        edges = [(0, 1, 5), (0, 1, 3), (1, 2, 4), (1, 2, 2)]
        S = {0}
        D = 2
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 5)

    def test_disconnected_graph(self):
        N = 4
        edges = [(0, 1, 2), (2, 3, 3)]
        S = {0, 2}
        D = 3
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 3)
        D = 1
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 2)
        D = 0
        self.assertEqual(optimal_multi_source_routing(N, edges, S, D), 0)

if __name__ == '__main__':
    unittest.main()