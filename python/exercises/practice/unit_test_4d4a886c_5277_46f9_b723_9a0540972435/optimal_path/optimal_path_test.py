import unittest
from optimal_path import find_optimal_path

class TestOptimalPath(unittest.TestCase):
    def test_direct_edge_valid(self):
        # Two nodes directly connected with sufficient bandwidth.
        n = 2
        edges = [
            (0, 1, 10, 5)
        ]
        start, end, min_bandwidth = 0, 1, 5
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), 10)

    def test_direct_edge_insufficient_bandwidth(self):
        # Two nodes directly connected but bandwidth is insufficient.
        n = 2
        edges = [
            (0, 1, 10, 3)
        ]
        start, end, min_bandwidth = 0, 1, 5
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), -1)

    def test_multiple_paths(self):
        # Graph with multiple paths where only one is valid with respect to bandwidth.
        n = 4
        edges = [
            (0, 1, 5, 6),   # meets bandwidth
            (1, 3, 5, 6),   # meets bandwidth => total cost 10
            (0, 2, 2, 10),  # meets bandwidth
            (2, 3, 10, 4),  # fails min bandwidth
            (0, 3, 20, 7)   # meets bandwidth => total cost 20
        ]
        start, end, min_bandwidth = 0, 3, 5
        # Only valid paths are 0->1->3 (cost=10) and 0->3 (cost=20), choose minimum
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), 10)

    def test_no_possible_path(self):
        # Graph where there is no valid path even though a physical connection exists.
        n = 3
        edges = [
            (0, 1, 4, 4),
            (1, 2, 6, 3)
        ]
        start, end, min_bandwidth = 0, 2, 5
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), -1)

    def test_cycle_in_graph(self):
        # Graph with a cycle. Should correctly avoid infinite loops.
        n = 4
        edges = [
            (0, 1, 2, 5),
            (1, 2, 2, 5),
            (2, 0, 1, 5),  # cycle edge
            (2, 3, 3, 5)
        ]
        start, end, min_bandwidth = 0, 3, 5
        # Path: 0->1->2->3, cost=2+2+3=7
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), 7)

    def test_source_equals_destination_with_valid_outgoing(self):
        # Special rule: if start == end and at least one outgoing edge exists with sufficient bandwidth, the cost is 0.
        n = 3
        edges = [
            (0, 1, 10, 5),
            (0, 2, 15, 6)
        ]
        start, end, min_bandwidth = 0, 0, 5
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), 0)

    def test_source_equals_destination_without_valid_outgoing(self):
        # Special rule: if start == end but no outgoing edge from start meets min_bandwidth, return -1.
        n = 2
        edges = [
            (0, 1, 10, 3)
        ]
        start, end, min_bandwidth = 0, 0, 5
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), -1)

    def test_complex_graph_multiple_choices(self):
        # More complex graph with multiple choices and different costs.
        n = 6
        edges = [
            (0, 1, 3, 7),
            (0, 2, 2, 5),
            (1, 3, 4, 7),
            (2, 3, 1, 5),
            (1, 4, 8, 7),
            (3, 4, 2, 7),
            (4, 5, 3, 7),
            (2, 5, 15, 5)
        ]
        start, end, min_bandwidth = 0, 5, 5
        # Valid paths:
        # 0->1->3->4->5 = 3+4+2+3 = 12
        # 0->2->3->4->5 = 2+1+2+3 = 8
        # 0->2->5 = 2+15 = 17
        self.assertEqual(find_optimal_path(n, edges, start, end, min_bandwidth), 8)

if __name__ == '__main__':
    unittest.main()