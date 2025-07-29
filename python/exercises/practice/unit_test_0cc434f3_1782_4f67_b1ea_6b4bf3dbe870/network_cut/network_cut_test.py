import unittest
from network_cut import min_removal_cost

class NetworkCutTests(unittest.TestCase):
    def test_no_cut_needed(self):
        # When k = 1, no partitioning required.
        n = 4
        edges = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 0, 4)]
        k = 1
        # Total cost of edges = 1+2+3+4 = 10.
        # Maximum spanning tree (keeping highest costs) uses edges with costs 4, 3, and 2: total kept = 9.
        # Removal cost = 10 - 9 = 1.
        self.assertEqual(min_removal_cost(n, edges, k), 1)

    def test_two_components(self):
        # Graph partitioned into 2 subnetworks.
        n = 4
        edges = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 0, 4)]
        k = 2
        # Maximum spanning tree for k = 1 has kept sum = 9.
        # To get 2 components, remove the smallest edge from the MST (edge with cost 2).
        # New kept sum = 9 - 2 = 7, so removal cost = 10 - 7 = 3.
        self.assertEqual(min_removal_cost(n, edges, k), 3)

    def test_fully_disconnected(self):
        # Partitioning the graph into n disconnected nodes.
        n = 4
        edges = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 0, 4)]
        k = 4
        # Partitioning into 4 components means keeping no edges.
        # Removal cost equals the sum of all edges = 10.
        self.assertEqual(min_removal_cost(n, edges, k), 10)

    def test_single_node(self):
        # A graph with a single node and no edges.
        n = 1
        edges = []
        k = 1
        # With one node, there are no edges to remove.
        self.assertEqual(min_removal_cost(n, edges, k), 0)

    def test_duplicate_edges(self):
        # Graph with duplicate edges between the same nodes.
        n = 3
        edges = [(0, 1, 5), (0, 1, 10), (1, 2, 2)]
        k = 1
        # Total edge cost = 5 + 10 + 2 = 17.
        # Maximum spanning tree chooses the duplicate with cost 10 between 0 and 1,
        # and the edge (1,2,2), total kept = 12.
        # Removal cost = 17 - 12 = 5.
        self.assertEqual(min_removal_cost(n, edges, k), 5)

    def test_duplicate_edges_k2(self):
        # Testing duplicate edge scenario with k = 2.
        n = 3
        edges = [(0, 1, 5), (0, 1, 10), (1, 2, 2)]
        k = 2
        # For k = 2, remove one edge from the MST.
        # MST for k = 1 keeps edges with cost 10 and 2 (total 12).
        # Removing the smallest MST edge (2) leaves kept sum = 10.
        # Removal cost = 17 - 10 = 7.
        self.assertEqual(min_removal_cost(n, edges, k), 7)

    def test_complex_graph(self):
        # A more complex graph.
        n = 6
        edges = [
            (0, 1, 4),
            (0, 2, 3),
            (1, 2, 2),
            (1, 3, 6),
            (2, 3, 5),
            (3, 4, 1),
            (4, 5, 7),
            (3, 5, 4)
        ]
        # Total cost = 4 + 3 + 2 + 6 + 5 + 1 + 7 + 4 = 32.
        # For k = 1: Maximum spanning tree (using Kruskal's algorithm in descending order)
        # might include edges with costs: 7, 6, 5, 4, and 4 (total kept = 26).
        # Removal cost = 32 - 26 = 6.
        k = 1
        self.assertEqual(min_removal_cost(n, edges, k), 6)

    def test_complex_graph_k3(self):
        # Same complex graph, but partitioned into 3 subnetworks.
        n = 6
        edges = [
            (0, 1, 4),
            (0, 2, 3),
            (1, 2, 2),
            (1, 3, 6),
            (2, 3, 5),
            (3, 4, 1),
            (4, 5, 7),
            (3, 5, 4)
        ]
        # Total edge cost = 32.
        # For k = 1 the maximum spanning tree has kept sum = 26.
        # To obtain 3 components, remove the two smallest edges from the MST.
        # If the MST edges sorted ascending are [4, 4, 5, 6, 7], removing two smallest 4 and 4:
        # Kept sum becomes 26 - 8 = 18, and removal cost = 32 - 18 = 14.
        k = 3
        self.assertEqual(min_removal_cost(n, edges, k), 14)

if __name__ == '__main__':
    unittest.main()