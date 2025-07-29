import unittest
from consensus_graph import consensus_graph

def normalize_edges(edges):
    return set((min(a, b), max(a, b)) for a, b in edges)

class ConsensusGraphTest(unittest.TestCase):
    def test_empty_node_views(self):
        # With no nodes, expected consensus is empty set.
        node_views = []
        result = consensus_graph(node_views, max_iterations=10)
        self.assertEqual(result, set())

    def test_empty_node_views_with_empty_set(self):
        # Nodes exist but each has an empty view.
        node_views = [set(), set(), set()]
        result = consensus_graph(node_views, max_iterations=10)
        self.assertEqual(result, set())

    def test_single_node(self):
        # Single node with some edges.
        node_views = [{(1, 2), (2, 3)}]
        result = consensus_graph(node_views, max_iterations=10)
        expected = {(1, 2), (2, 3)}
        # Normalize not really needed since they are already sorted.
        self.assertEqual(normalize_edges(result), normalize_edges(expected))

    def test_already_consensus(self):
        # All nodes already have the same view.
        common_view = {(1, 2), (2, 3), (3, 4)}
        node_views = [set(common_view), set(common_view), set(common_view)]
        result = consensus_graph(node_views, max_iterations=5)
        self.assertEqual(normalize_edges(result), normalize_edges(common_view))

    def test_convergence_with_diff_views(self):
        # Nodes start with different sets that when unioned yield the full graph.
        node_views = [
            {(1, 2), (3, 4)},
            {(2, 3)},
            {(4, 5)}
        ]
        result = consensus_graph(node_views, max_iterations=10)
        expected_union = {(1, 2), (3, 4), (2, 3), (4, 5)}
        self.assertEqual(normalize_edges(result), normalize_edges(expected_union))

    def test_convergence_with_reversed_edges(self):
        # Test that reversed edges are considered equivalent.
        node_views = [
            {(1, 2), (3, 4)},
            {(2, 1), (4, 3)},
            {(1, 2), (4, 3), (5, 6)}
        ]
        result = consensus_graph(node_views, max_iterations=10)
        expected_union = {(1, 2), (3, 4), (5, 6)}
        self.assertEqual(normalize_edges(result), normalize_edges(expected_union))

    def test_max_iterations_zero(self):
        # When max_iterations is 0, no iterations should occur.
        # Depending on implementation, the consensus might reflect the first node's view.
        node_views = [
            {(1, 2), (2, 3)},
            {(2, 3), (3, 4)}
        ]
        result = consensus_graph(node_views, max_iterations=0)
        # As no iterations occur, we expect the result to be exactly the state of the first node.
        expected = {(1, 2), (2, 3)}
        self.assertEqual(normalize_edges(result), normalize_edges(expected))

if __name__ == '__main__':
    unittest.main()