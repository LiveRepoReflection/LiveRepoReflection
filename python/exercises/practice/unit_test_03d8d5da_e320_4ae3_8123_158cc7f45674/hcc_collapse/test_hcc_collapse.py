import unittest
from hcc_collapse.hcc_collapse import hcc_collapse

class TestHCCCollapse(unittest.TestCase):
    def test_simple_graph(self):
        num_nodes = 3
        edges = [(0, 1), (1, 0), (1, 2)]
        density_threshold = 0.5
        expected_nodes = [0, 2]
        expected_edges = [(0, 2)]
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_multiple_hccs(self):
        num_nodes = 6
        edges = [(0, 1), (1, 0), (1, 2), (2, 1), (3, 4), (4, 3), (0, 3), (3, 5)]
        density_threshold = 0.5
        expected_nodes = [0, 3, 5]
        expected_edges = [(0, 3), (3, 5)]
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_no_hccs(self):
        num_nodes = 4
        edges = [(0, 1), (1, 2), (2, 3)]
        density_threshold = 0.5
        expected_nodes = [0, 1, 2, 3]
        expected_edges = [(0, 1), (1, 2), (2, 3)]
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_complete_graph(self):
        num_nodes = 4
        edges = [(0, 1), (0, 2), (0, 3),
                 (1, 0), (1, 2), (1, 3),
                 (2, 0), (2, 1), (2, 3),
                 (3, 0), (3, 1), (3, 2)]
        density_threshold = 0.9
        expected_nodes = [0]
        expected_edges = []
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_disconnected_graph(self):
        num_nodes = 5
        edges = [(0, 1), (1, 0), (2, 3), (3, 2)]
        density_threshold = 0.5
        expected_nodes = [0, 2, 4]
        expected_edges = []
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_edge_case_empty_graph(self):
        num_nodes = 0
        edges = []
        density_threshold = 0.5
        expected_nodes = []
        expected_edges = []
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_low_density_threshold(self):
        num_nodes = 4
        edges = [(0, 1), (1, 0), (2, 3), (3, 2)]
        density_threshold = 0.1
        expected_nodes = [0, 2]
        expected_edges = []
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

    def test_self_loops_ignored(self):
        num_nodes = 3
        edges = [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]
        density_threshold = 0.5
        expected_nodes = [0, 2]
        expected_edges = [(0, 2)]
        result_nodes, result_edges = hcc_collapse(num_nodes, edges, density_threshold)
        self.assertEqual(sorted(result_nodes), expected_nodes)
        self.assertEqual(sorted(result_edges), expected_edges)

if __name__ == '__main__':
    unittest.main()