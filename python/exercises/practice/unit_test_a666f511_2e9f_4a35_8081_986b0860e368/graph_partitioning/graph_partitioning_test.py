import unittest
import random
from graph_partitioning import partition_graph

class TestGraphPartitioning(unittest.TestCase):
    def check_valid_output(self, n, k, assignment):
        # Check that the assignment list is of length n
        self.assertEqual(len(assignment), n, f"Expected assignment length {n}, got {len(assignment)}")
        # Check each community index is in range [0, k-1]
        for community in assignment:
            self.assertTrue(0 <= community < k, f"Community index {community} is out of bounds for k={k}")

    def test_single_node(self):
        # Test with a single node and no edges, only one community.
        n = 1
        edges = []
        k = 1
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

    def test_no_edges(self):
        # Test with multiple nodes but no edges.
        n = 5
        edges = []
        k = 3
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

    def test_complete_graph(self):
        # Test with a complete graph.
        n = 4
        edges = [(i, j) for i in range(n) for j in range(i+1, n)]
        k = 2
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

    def test_disconnected_graph(self):
        # Test with a graph that has two disconnected components.
        # Component 1: nodes [0, 1, 2] fully connected.
        # Component 2: nodes [3, 4] connected by one edge.
        n = 5
        edges = [(0, 1), (0, 2), (1, 2), (3, 4)]
        k = 2
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

    def test_sparse_graph(self):
        # Test with a sparse graph (line graph).
        n = 10
        edges = [(i, i + 1) for i in range(n - 1)]
        k = 3
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

    def test_complex_graph(self):
        # Test with a graph combining cycles, trees, and chains.
        # Cycle: 0-1-2-3-0; Tree: 3->4, 3->5; Chain: 5-6-7.
        n = 8
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (3, 5), (5, 6), (6, 7)]
        k = 3
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

    def test_large_random_graph(self):
        # Test with a larger random sparse graph.
        n = 100
        k = 4
        num_edges = 200
        edges_set = set()
        while len(edges_set) < num_edges:
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)
            if u != v:
                edge = (min(u, v), max(u, v))
                edges_set.add(edge)
        edges = list(edges_set)
        result = partition_graph(n, edges, k)
        self.check_valid_output(n, k, result)

if __name__ == '__main__':
    unittest.main()