import unittest
from multi_source_path import solve

class MultiSourcePathTest(unittest.TestCase):
    def test_single_node_with_source(self):
        n = 1
        edges = []
        sources = [0]
        # Only one node, and it's a source so distance is 0.
        expected = [0]
        self.assertEqual(solve(n, edges, sources), expected)

    def test_single_node_without_source(self):
        n = 1
        edges = []
        sources = []
        # No source provided, so the only node is unreachable.
        expected = [-1]
        self.assertEqual(solve(n, edges, sources), expected)

    def test_simple_directed_graph(self):
        # Graph:
        # 0 -> 1 (2), 0 -> 2 (5), 1 -> 2 (1), 2 -> 3 (2)
        n = 4
        edges = [
            (0, 1, 2),
            (0, 2, 5),
            (1, 2, 1),
            (2, 3, 2)
        ]
        sources = [0]
        # Distances: 0:0, 1:2, 2:3, 3:5
        expected = [0, 2, 3, 5]
        self.assertEqual(solve(n, edges, sources), expected)

    def test_multiple_sources(self):
        # Graph:
        # 0 -> 1 (4)
        # 1 -> 4 (1)
        # 2 -> 3 (2)
        # 3 -> 4 (3)
        n = 5
        edges = [
            (0, 1, 4),
            (1, 4, 1),
            (2, 3, 2),
            (3, 4, 3)
        ]
        sources = [0, 2]
        # Expected distances:
        # Node 0: 0 (from source 0)
        # Node 1: 4 (from source 0)
        # Node 2: 0 (source 2)
        # Node 3: 2 (from source 2)
        # Node 4: 5 (min(0->1->4, 2->3->4))
        expected = [0, 4, 0, 2, 5]
        self.assertEqual(solve(n, edges, sources), expected)

    def test_disconnected_graph(self):
        # Graph with unreachable node
        # 0 -> 1 (10)
        n = 3
        edges = [
            (0, 1, 10)
        ]
        sources = [0]
        # Node 2 is unreachable.
        expected = [0, 10, -1]
        self.assertEqual(solve(n, edges, sources), expected)

    def test_self_loop(self):
        # Graph with self-loop:
        # 0 -> 0 (3), 0 -> 1 (1), 1 -> 2 (2)
        n = 3
        edges = [
            (0, 0, 3),
            (0, 1, 1),
            (1, 2, 2)
        ]
        sources = [0]
        # Self-loop at 0 should not affect optimal paths.
        expected = [0, 1, 3]
        self.assertEqual(solve(n, edges, sources), expected)

    def test_cycle_in_graph(self):
        # Graph with cycle:
        # 0 -> 1 (1), 1 -> 2 (1), 2 -> 0 (1), 1 -> 3 (5)
        n = 4
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 0, 1),
            (1, 3, 5)
        ]
        sources = [0]
        # Optimal paths:
        # Node 0: 0, Node 1: 1, Node 2: 2, Node 3: 6
        expected = [0, 1, 2, 6]
        self.assertEqual(solve(n, edges, sources), expected)

if __name__ == '__main__':
    unittest.main()