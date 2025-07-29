import unittest
from resilient_partition import min_cost_partition

class ResilientPartitionTest(unittest.TestCase):

    def test_single_node(self):
        n = 1
        edges = []
        k = 1
        node_weights = [5]
        # A single node is trivially resilient.
        expected = 5
        self.assertEqual(min_cost_partition(n, edges, k, node_weights), expected)

    def test_triangle_graph_single_cluster(self):
        # A triangle graph is a cycle, hence resilient.
        n = 3
        edges = [(0, 1), (1, 2), (2, 0)]
        k = 1
        node_weights = [3, 5, 4]
        # Entire triangle is resilient and cost is sum of weights.
        expected = 12
        self.assertEqual(min_cost_partition(n, edges, k, node_weights), expected)

    def test_chain_graph_impossible_as_single_cluster(self):
        # A chain graph of three nodes is not resilient as a whole
        # because the middle node is an articulation point.
        n = 3
        edges = [(0, 1), (1, 2)]
        k = 1
        node_weights = [1, 2, 1]
        expected = -1
        self.assertEqual(min_cost_partition(n, edges, k, node_weights), expected)

    def test_chain_graph_possible_partition(self):
        # Partitioning a chain graph into two clusters.
        # One possible partition: Cluster 1: [0], Cluster 2: [1, 2]
        # Both clusters are resilient (single node or pair).
        n = 3
        edges = [(0, 1), (1, 2)]
        k = 2
        node_weights = [1, 2, 1]
        # Total cost remains sum of all nodes as each node is assigned to one cluster.
        expected = 4
        self.assertEqual(min_cost_partition(n, edges, k, node_weights), expected)

    def test_disconnected_graph(self):
        # A disconnected graph with 4 nodes and one edge connecting nodes 0 and 1.
        # Other nodes are isolated and each isolated node is resilient.
        n = 4
        edges = [(0, 1)]
        k = 2
        node_weights = [2, 2, 3, 3]
        # One possible partition: Cluster 1: [0, 1] and Cluster 2: [2, 3].
        expected = 10
        self.assertEqual(min_cost_partition(n, edges, k, node_weights), expected)

    def test_complex_graph_partition(self):
        # Graph with a cycle and an attached tail forming a bridge.
        n = 6
        edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
        k = 2
        node_weights = [10, 12, 15, 8, 5, 7]
        # One optimal partition may be:
        # Cluster 1: [0, 1, 2] (cycle; resilient)
        # Cluster 2: [3, 4, 5] (cycle; resilient)
        # Total cost is the sum: 10+12+15+8+5+7 = 57.
        expected = 57
        self.assertEqual(min_cost_partition(n, edges, k, node_weights), expected)

if __name__ == '__main__':
    unittest.main()