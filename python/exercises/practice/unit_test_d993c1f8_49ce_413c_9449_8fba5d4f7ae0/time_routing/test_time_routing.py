import unittest
from time_routing import min_cost_path

class TestTimeRouting(unittest.TestCase):
    def test_single_node(self):
        N = 1
        M = 0
        edges = []
        start_node = 0
        end_node = 0
        start_time = 0
        self.assertEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), 0)

    def test_two_nodes_direct_connection(self):
        N = 2
        M = 1
        edges = [(0, 1, [(0, 1.0), (10, 2.0)])]
        start_node = 0
        end_node = 1
        start_time = 5
        expected_cost = 1.0 + (5-0)/(10-0)*(2.0-1.0)  # Interpolated cost at time=5
        self.assertAlmostEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), expected_cost)

    def test_unreachable_node(self):
        N = 3
        M = 1
        edges = [(0, 1, [(0, 1.0)])]
        start_node = 0
        end_node = 2
        start_time = 0
        self.assertEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), -1)

    def test_multiple_paths(self):
        N = 4
        M = 5
        edges = [
            (0, 1, [(0, 1.0), (10, 2.0)]),
            (0, 2, [(0, 3.0), (5, 1.0), (15, 4.0)]),
            (1, 2, [(0, 2.0), (7, 5.0)]),
            (1, 3, [(0, 1.0)]),
            (2, 3, [(0, 4.0), (12, 2.0)])
        ]
        start_node = 0
        end_node = 3
        start_time = 2
        # Expected to take path 0->1->3 with total cost = 1.2 + 1.0 = 2.2
        self.assertAlmostEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), 2.2)

    def test_large_time_value(self):
        N = 2
        M = 1
        edges = [(0, 1, [(0, 1.0), (10, 2.0)])]
        start_node = 0
        end_node = 1
        start_time = 20  # Should use last cost value (2.0)
        self.assertEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), 2.0)

    def test_small_time_value(self):
        N = 2
        M = 1
        edges = [(0, 1, [(5, 1.0), (10, 2.0)])]
        start_node = 0
        end_node = 1
        start_time = 0  # Should use first cost value (1.0)
        self.assertEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), 1.0)

    def test_complex_network(self):
        N = 5
        M = 8
        edges = [
            (0, 1, [(0, 2.0), (5, 4.0)]),
            (0, 2, [(0, 1.0), (10, 3.0)]),
            (1, 2, [(0, 1.5), (8, 2.5)]),
            (1, 3, [(0, 3.0), (6, 1.0)]),
            (2, 3, [(0, 2.0), (7, 5.0)]),
            (2, 4, [(0, 4.0)]),
            (3, 4, [(0, 1.0), (5, 2.0)]),
            (4, 0, [(0, 3.0)])
        ]
        start_node = 0
        end_node = 4
        start_time = 3
        # Expected path: 0->2->4 with total cost = 1.6 + 4.0 = 5.6
        self.assertAlmostEqual(min_cost_path(N, M, edges, start_node, end_node, start_time), 5.6)

if __name__ == '__main__':
    unittest.main()