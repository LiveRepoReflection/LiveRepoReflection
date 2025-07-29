import unittest
from network_domination.network_domination import find_dominating_set

class TestNetworkDomination(unittest.TestCase):
    def test_small_network(self):
        n = 4
        edges = [(1, 2), (2, 3), (3, 4)]
        result = find_dominating_set(n, edges)
        self.assertTrue(self._is_dominating_set(n, edges, result))
        self.assertLessEqual(len(result), 2)  # Optimal solution is 2 nodes

    def test_star_network(self):
        n = 5
        edges = [(1, 2), (1, 3), (1, 4), (1, 5)]
        result = find_dominating_set(n, edges)
        self.assertTrue(self._is_dominating_set(n, edges, result))
        self.assertEqual(len(result), 1)  # Center node alone is sufficient

    def test_cycle_network(self):
        n = 6
        edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)]
        result = find_dominating_set(n, edges)
        self.assertTrue(self._is_dominating_set(n, edges, result))
        self.assertLessEqual(len(result), 2)  # Optimal solution is 2 nodes

    def test_complete_graph(self):
        n = 5
        edges = [(1, 2), (1, 3), (1, 4), (1, 5),
                 (2, 3), (2, 4), (2, 5),
                 (3, 4), (3, 5),
                 (4, 5)]
        result = find_dominating_set(n, edges)
        self.assertTrue(self._is_dominating_set(n, edges, result))
        self.assertEqual(len(result), 1)  # Any single node is sufficient

    def test_disconnected_graph(self):
        n = 6
        edges = [(1, 2), (2, 3), (4, 5), (5, 6)]
        result = find_dominating_set(n, edges)
        self.assertTrue(self._is_dominating_set(n, edges, result))
        self.assertLessEqual(len(result), 4)  # Need at least 2 nodes per component

    def test_large_network(self):
        n = 1000
        edges = [(i, i+1) for i in range(1, 1000)]
        result = find_dominating_set(n, edges)
        self.assertTrue(self._is_dominating_set(n, edges, result))
        self.assertLessEqual(len(result), 334)  # Linear graph needs ~n/3 nodes

    def test_empty_graph(self):
        n = 5
        edges = []
        result = find_dominating_set(n, edges)
        self.assertEqual(len(result), n)  # Need all nodes when no edges

    def test_single_node(self):
        n = 1
        edges = []
        result = find_dominating_set(n, edges)
        self.assertEqual(result, [1])

    def _is_dominating_set(self, n, edges, dominating_set):
        dominated = set(dominating_set)
        for u, v in edges:
            if u in dominating_set:
                dominated.add(v)
            if v in dominating_set:
                dominated.add(u)
        return len(dominated) == n

if __name__ == '__main__':
    unittest.main()