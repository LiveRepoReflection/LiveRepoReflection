import unittest
from network_restructure import optimal_network_restructure

class TestNetworkRestructure(unittest.TestCase):
    def test_small_network(self):
        N = 4
        M = 5
        edges = [(1, 2, 10), (1, 3, 15), (1, 4, 20), (2, 3, 5), (3, 4, 8)]
        B = 40
        K = 2
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 2)

    def test_minimum_edges_required(self):
        N = 3
        M = 3
        edges = [(1, 2, 5), (2, 3, 5), (1, 3, 10)]
        B = 15
        K = 2
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 2)

    def test_no_solution(self):
        N = 4
        M = 5
        edges = [(1, 2, 50), (1, 3, 50), (1, 4, 50), (2, 3, 50), (3, 4, 50)]
        B = 10
        K = 2
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), -1)

    def test_large_budget(self):
        N = 5
        M = 7
        edges = [(1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 5, 1),
                 (2, 3, 1), (3, 4, 1), (4, 5, 1)]
        B = 100
        K = 3
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 2)

    def test_star_topology(self):
        N = 5
        M = 4
        edges = [(1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 5, 1)]
        B = 4
        K = 1
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 4)

    def test_ring_topology(self):
        N = 5
        M = 5
        edges = [(1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (5, 1, 1)]
        B = 5
        K = 3
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 2)

    def test_complete_graph(self):
        N = 4
        M = 6
        edges = [(1, 2, 1), (1, 3, 1), (1, 4, 1),
                 (2, 3, 1), (2, 4, 1), (3, 4, 1)]
        B = 3
        K = 2
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 2)

    def test_single_node(self):
        N = 1
        M = 0
        edges = []
        B = 0
        K = 0
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 0)

    def test_two_nodes(self):
        N = 2
        M = 1
        edges = [(1, 2, 5)]
        B = 5
        K = 1
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 1)

    def test_edge_case_large_k(self):
        N = 3
        M = 2
        edges = [(1, 2, 1), (2, 3, 1)]
        B = 2
        K = 2
        self.assertEqual(optimal_network_restructure(N, M, edges, B, K), 2)

if __name__ == '__main__':
    unittest.main()