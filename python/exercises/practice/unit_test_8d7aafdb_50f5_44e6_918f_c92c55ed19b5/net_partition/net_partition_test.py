import unittest
from net_partition import net_partition

class TestNetPartition(unittest.TestCase):
    def test_basic_partition(self):
        n = 6
        k = 2
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        dependencies = [(0, 3), (2, 5), (4, 1)]
        min_size = 2
        max_size = 4
        result = net_partition(n, k, edges, dependencies, min_size, max_size)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), k)
        self.assertTrue(all(min_size <= len(cluster) <= max_size for cluster in result))
        self._verify_connectivity(result, edges)

    def test_no_valid_partition(self):
        n = 6
        k = 3
        edges = [(0, 1), (1, 2), (3, 4), (4, 5)]
        dependencies = [(0, 3), (2, 5)]
        min_size = 2
        max_size = 3
        result = net_partition(n, k, edges, dependencies, min_size, max_size)
        self.assertIsNone(result)

    def test_minimal_input(self):
        n = 3
        k = 1
        edges = [(0, 1), (1, 2)]
        dependencies = [(0, 2)]
        min_size = 1
        max_size = 3
        result = net_partition(n, k, edges, dependencies, min_size, max_size)
        self.assertEqual(result, [[0, 1, 2]])

    def test_max_cluster_size(self):
        n = 8
        k = 2
        edges = [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)]
        dependencies = [(0, 4), (3, 7)]
        min_size = 3
        max_size = 4
        result = net_partition(n, k, edges, dependencies, min_size, max_size)
        self.assertIsNotNone(result)
        self.assertTrue(all(len(cluster) == 4 for cluster in result))

    def test_disconnected_graph(self):
        n = 6
        k = 2
        edges = [(0, 1), (1, 2), (3, 4), (4, 5)]
        dependencies = [(0, 3), (2, 5)]
        min_size = 2
        max_size = 4
        result = net_partition(n, k, edges, dependencies, min_size, max_size)
        self.assertIsNotNone(result)
        self._verify_connectivity(result, edges)

    def test_multiple_dependencies(self):
        n = 5
        k = 2
        edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        dependencies = [(0, 2), (0, 3), (1, 4), (2, 4)]
        min_size = 2
        max_size = 3
        result = net_partition(n, k, edges, dependencies, min_size, max_size)
        self.assertIsNotNone(result)
        self._verify_connectivity(result, edges)

    def _verify_connectivity(self, clusters, edges):
        for cluster in clusters:
            visited = set()
            if cluster:
                stack = [cluster[0]]
                visited.add(cluster[0])
                while stack:
                    node = stack.pop()
                    for u, v in edges:
                        if u == node and v in cluster and v not in visited:
                            visited.add(v)
                            stack.append(v)
                        if v == node and u in cluster and u not in visited:
                            visited.add(u)
                            stack.append(u)
                self.assertEqual(visited, set(cluster))

if __name__ == '__main__':
    unittest.main()