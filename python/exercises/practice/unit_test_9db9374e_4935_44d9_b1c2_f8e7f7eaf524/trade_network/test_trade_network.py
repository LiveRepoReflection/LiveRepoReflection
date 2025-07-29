import unittest
from trade_network import min_cost_flow

class TestTradeNetwork(unittest.TestCase):
    def test_basic_single_path(self):
        """Test a simple network with one direct path."""
        num_nodes = 2
        edges = [(0, 1, 10, 5.0)]
        source = 0
        destination = 1
        amount = 10
        expected = 50.0  # 10 units at cost 5.0 each
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_basic_multiple_paths(self):
        """Test a simple network with multiple direct paths."""
        num_nodes = 2
        edges = [(0, 1, 5, 5.0), (0, 1, 5, 10.0)]
        source = 0
        destination = 1
        amount = 8
        expected = 5 * 5.0 + 3 * 10.0  # 5 units at cost 5.0 each + 3 units at cost 10.0 each
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_impossible_flow(self):
        """Test when it's impossible to route the entire amount."""
        num_nodes = 2
        edges = [(0, 1, 5, 5.0)]
        source = 0
        destination = 1
        amount = 10
        expected = -1.0
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_partial_possible_flow(self):
        """Test when only part of the requested amount can be routed."""
        num_nodes = 3
        edges = [(0, 1, 5, 5.0), (1, 2, 3, 10.0)]
        source = 0
        destination = 2
        amount = 5
        expected = -1.0  # Can only route 3 units, but requested 5
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_multiple_paths_with_intermediate_nodes(self):
        """Test a network with multiple paths through intermediate nodes."""
        num_nodes = 4
        edges = [
            (0, 1, 5, 5.0),
            (0, 2, 10, 10.0),
            (1, 3, 5, 5.0),
            (2, 3, 10, 5.0)
        ]
        source = 0
        destination = 3
        amount = 15
        expected = 5 * (5.0 + 5.0) + 10 * (10.0 + 5.0)  # 5 units through path 0->1->3 and 10 units through path 0->2->3
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_disconnected_graph(self):
        """Test when the source and destination are not connected."""
        num_nodes = 4
        edges = [(0, 1, 10, 5.0), (2, 3, 10, 5.0)]
        source = 0
        destination = 3
        amount = 5
        expected = -1.0
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_same_source_and_destination(self):
        """Test when source and destination are the same."""
        num_nodes = 3
        edges = [(0, 1, 10, 5.0), (1, 2, 10, 5.0)]
        source = 0
        destination = 0
        amount = 5
        expected = 0.0  # No cost as no flow is needed
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_complex_network(self):
        """Test a more complex network with multiple potential paths."""
        num_nodes = 6
        edges = [
            (0, 1, 10, 2.0),
            (0, 2, 5, 1.0),
            (1, 3, 8, 3.0),
            (1, 4, 4, 2.0),
            (2, 3, 5, 1.0),
            (2, 4, 3, 4.0),
            (3, 5, 10, 2.0),
            (4, 5, 7, 3.0)
        ]
        source = 0
        destination = 5
        amount = 12
        # Optimal flow:
        # 5 units: 0 -> 2 -> 3 -> 5 with cost 1.0 + 1.0 + 2.0 = 4.0 per unit
        # 7 units: 0 -> 1 -> [3 (3) and 4 (4)] -> 5 with costs:
        #   3 units: 0 -> 1 -> 3 -> 5 with cost 2.0 + 3.0 + 2.0 = 7.0 per unit
        #   4 units: 0 -> 1 -> 4 -> 5 with cost 2.0 + 2.0 + 3.0 = 7.0 per unit
        expected = 5 * 4.0 + 3 * 7.0 + 4 * 7.0
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_zero_capacity_edges(self):
        """Test a network with some zero capacity edges."""
        num_nodes = 3
        edges = [(0, 1, 0, 5.0), (1, 2, 10, 5.0)]
        source = 0
        destination = 2
        amount = 5
        expected = -1.0  # Cannot route any flow through the first edge
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_large_network(self):
        """Test a larger network to check algorithm efficiency."""
        num_nodes = 100
        edges = []
        for i in range(99):
            edges.append((i, i + 1, 10, 1.0))
        source = 0
        destination = 99
        amount = 10
        expected = 10 * 99.0  # 10 units through a path of 99 edges at cost 1.0 each
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_parallel_edges(self):
        """Test handling of parallel edges between nodes."""
        num_nodes = 3
        edges = [
            (0, 1, 5, 2.0),
            (0, 1, 5, 3.0),
            (1, 2, 10, 1.0)
        ]
        source = 0
        destination = 2
        amount = 8
        expected = 5 * (2.0 + 1.0) + 3 * (3.0 + 1.0)  # 5 units through cheaper path, 3 through more expensive
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

    def test_negative_cost_edges(self):
        """Test handling of edges with negative costs."""
        num_nodes = 3
        edges = [
            (0, 1, 10, -1.0),
            (1, 2, 10, 2.0)
        ]
        source = 0
        destination = 2
        amount = 5
        expected = 5 * (-1.0 + 2.0)  # 5 units at combined cost 1.0 each
        self.assertEqual(min_cost_flow(num_nodes, edges, source, destination, amount), expected)

if __name__ == '__main__':
    unittest.main()