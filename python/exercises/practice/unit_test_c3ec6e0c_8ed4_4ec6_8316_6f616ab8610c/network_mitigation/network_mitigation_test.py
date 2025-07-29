import unittest
from network_mitigation import mitigate_congestion

class TestNetworkMitigation(unittest.TestCase):
    def test_already_below_capacity(self):
        N = 3
        edges = [(0, 1, 10), (1, 2, 15)]
        capacity = 30
        self.assertEqual(mitigate_congestion(N, edges, capacity), [])

    def test_single_edge_reduction(self):
        N = 2
        edges = [(0, 1, 50)]
        capacity = 40
        expected = [(0, 1, 10)]
        self.assertEqual(sorted(mitigate_congestion(N, edges, capacity)), sorted(expected))

    def test_multiple_edges_reduction(self):
        N = 4
        edges = [(0, 1, 20), (1, 2, 30), (2, 3, 40)]
        capacity = 70
        result = mitigate_congestion(N, edges, capacity)
        total_reduction = sum(r[2] for r in result)
        self.assertEqual(total_reduction, 20)
        self.assertLessEqual(sum(w for _, _, w in edges) - total_reduction, capacity)

    def test_tie_breaking(self):
        N = 3
        edges = [(0, 1, 25), (1, 2, 25), (0, 2, 10)]
        capacity = 50
        result = mitigate_congestion(N, edges, capacity)
        total_reduction = sum(r[2] for r in result)
        self.assertEqual(total_reduction, 10)
        self.assertTrue(any(r[2] > 0 for r in result))

    def test_large_network(self):
        N = 1000
        edges = [(i, i+1, 10) for i in range(N-1)]
        capacity = 5000
        result = mitigate_congestion(N, edges, capacity)
        total_reduction = sum(r[2] for r in result)
        expected_reduction = max(0, sum(w for _, _, w in edges) - capacity)
        self.assertEqual(total_reduction, expected_reduction)

    def test_empty_edges(self):
        N = 5
        edges = []
        capacity = 100
        self.assertEqual(mitigate_congestion(N, edges, capacity), [])

    def test_multiple_edges_same_nodes(self):
        N = 2
        edges = [(0, 1, 15), (0, 1, 25), (0, 1, 10)]
        capacity = 40
        result = mitigate_congestion(N, edges, capacity)
        total_reduction = sum(r[2] for r in result)
        self.assertEqual(total_reduction, 10)

    def test_exact_capacity(self):
        N = 3
        edges = [(0, 1, 20), (1, 2, 30)]
        capacity = 50
        self.assertEqual(mitigate_congestion(N, edges, capacity), [])

    def test_insufficient_capacity(self):
        N = 2
        edges = [(0, 1, 100)]
        capacity = 10
        result = mitigate_congestion(N, edges, capacity)
        self.assertEqual(result[0][2], 90)

if __name__ == '__main__':
    unittest.main()