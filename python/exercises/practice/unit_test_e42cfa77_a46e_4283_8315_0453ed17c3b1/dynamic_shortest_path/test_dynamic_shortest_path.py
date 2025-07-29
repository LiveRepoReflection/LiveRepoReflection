import unittest
from dynamic_shortest_path import dynamic_shortest_path

class TestDynamicShortestPath(unittest.TestCase):
    def test_small_graph(self):
        N = 4
        edges = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (0, 3, 10)]
        sources = [0]
        updates = []
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 1, 3, 6])

    def test_multiple_sources(self):
        N = 5
        edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (2, 3, 2), (3, 4, 4)]
        sources = [0, 4]
        updates = [(0, 1, 2), (2, 3, 1)]
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 2, 3, 4, 0])

    def test_disconnected_graph(self):
        N = 3
        edges = [(0, 1, 1)]
        sources = [0, 2]
        updates = []
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 1, 0])

    def test_large_graph_with_updates(self):
        N = 6
        edges = [(0, 1, 2), (1, 2, 3), (2, 3, 1), (3, 4, 4), (4, 5, 2)]
        sources = [0]
        updates = [(0, 1, 1), (2, 3, 5), (4, 5, 1)]
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 1, 4, 9, 13, 14])

    def test_negative_case_unreachable_nodes(self):
        N = 4
        edges = [(0, 1, 1), (2, 3, 2)]
        sources = [0]
        updates = []
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 1, float('inf'), float('inf')])

    def test_new_edge_addition(self):
        N = 3
        edges = [(0, 1, 2)]
        sources = [0]
        updates = [(1, 2, 3), (0, 2, 10)]
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 2, 5])

    def test_empty_graph(self):
        N = 0
        edges = []
        sources = []
        updates = []
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [])

    def test_single_node_graph(self):
        N = 1
        edges = []
        sources = [0]
        updates = []
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0])

    def test_cyclic_graph(self):
        N = 3
        edges = [(0, 1, 1), (1, 2, 1), (2, 0, 1)]
        sources = [0]
        updates = [(1, 2, 3)]
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 1, 4])

    def test_multiple_updates_same_edge(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        sources = [0]
        updates = [(0, 1, 2), (0, 1, 1), (1, 2, 3)]
        result = dynamic_shortest_path(N, edges, sources, updates)
        self.assertEqual(result, [0, 1, 4])

if __name__ == '__main__':
    unittest.main()