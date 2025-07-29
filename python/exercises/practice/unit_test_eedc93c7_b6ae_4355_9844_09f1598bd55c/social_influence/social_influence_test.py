import unittest
from social_influence import select_seed_users

class TestSocialInfluence(unittest.TestCase):

    def test_basic_graph(self):
        # A simple graph where nodes: 0, 1, 2 are connected in a line.
        # Edges: 0 -> 1 with weight 0.5, 1 -> 2 with weight 0.5.
        edges = [
            (0, 1, 0.5),
            (1, 2, 0.5)
        ]
        k = 1
        iterations = 1000
        seeds = select_seed_users(edges, k, iterations)
        # Check that exactly one seed is returned.
        self.assertEqual(len(seeds), k)
        # The seed should be one of the nodes in the graph.
        valid_nodes = {0, 1, 2}
        for seed in seeds:
            self.assertIn(seed, valid_nodes)

    def test_disconnected_graph(self):
        # Graph with two disconnected components.
        # Component 1: nodes 0, 1; Component 2: nodes 2, 3.
        edges = [
            (0, 1, 0.7),
            (2, 3, 0.8)
        ]
        k = 2
        iterations = 500
        seeds = select_seed_users(edges, k, iterations)
        # Check that exactly k seeds are returned.
        self.assertEqual(len(seeds), k)
        # All seeds must be among the nodes mentioned in the graph.
        valid_nodes = {0, 1, 2, 3}
        for seed in seeds:
            self.assertIn(seed, valid_nodes)

    def test_cycle_graph(self):
        # Graph is a cycle: 0->1->2->0
        edges = [
            (0, 1, 0.4),
            (1, 2, 0.4),
            (2, 0, 0.4)
        ]
        k = 2
        iterations = 800
        seeds = select_seed_users(edges, k, iterations)
        self.assertEqual(len(seeds), k)
        valid_nodes = {0, 1, 2}
        for seed in seeds:
            self.assertIn(seed, valid_nodes)

    def test_k_greater_than_nodes(self):
        # When k is greater than the number of nodes available in the graph.
        edges = [
            (0, 1, 0.6),
            (1, 2, 0.6)
        ]
        k = 5  # More seeds than nodes; expect returned seeds equal to all available nodes.
        iterations = 400
        seeds = select_seed_users(edges, k, iterations)
        # Extract unique nodes from the graph.
        valid_nodes = {0, 1, 2}
        # The seed list should contain every node in the graph (order does not matter)
        self.assertEqual(set(seeds), valid_nodes)

    def test_isolated_nodes(self):
        # Graph with isolated nodes (nodes appear without any edge connections).
        # Represent isolated nodes by simply providing no edges for them.
        # To simulate isolated nodes, we include edges with self-loops with very low weight.
        edges = [
            (0, 0, 0.0),  # self-loop acting as isolated node
            (1, 1, 0.0),
            (2, 2, 0.0)
        ]
        k = 2
        iterations = 300
        seeds = select_seed_users(edges, k, iterations)
        self.assertEqual(len(seeds), k)
        valid_nodes = {0, 1, 2}
        for seed in seeds:
            self.assertIn(seed, valid_nodes)

if __name__ == "__main__":
    unittest.main()