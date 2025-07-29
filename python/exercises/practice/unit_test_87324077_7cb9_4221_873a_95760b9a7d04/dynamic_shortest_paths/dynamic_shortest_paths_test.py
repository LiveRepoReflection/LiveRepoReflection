import unittest
import math
from dynamic_shortest_paths import dynamic_shortest_paths

class TestDynamicShortestPaths(unittest.TestCase):
    def test_sample_case(self):
        N = 4
        M = 5
        edges = [(0, 1, 2), (0, 2, 5), (1, 2, 1), (2, 3, 4), (1, 3, 7)]
        sources = [0, 1]
        Q = 2
        updates = [(0, 1, 5), (2, 3, 1)]
        # After first update:
        # Graph becomes: (0,1,5), (0,2,5), (1,2,1), (2,3,4), (1,3,7)
        # For sources 0 and 1:
        # From 0: distances = [0, 5, 5, 9]
        # From 1: distances = [inf, 0, 1, 5]
        # Minimum distances: [0, 0, 1, 5]
        #
        # After second update:
        # Graph becomes: (0,1,5), (0,2,5), (1,2,1), (2,3,1), (1,3,7)
        # From 0: distances = [0, 5, 5, 6]
        # From 1: distances = [inf, 0, 1, 2]
        # Minimum distances: [0, 0, 1, 2]
        expected = [
            [0, 0, 1, 5],
            [0, 0, 1, 2]
        ]
        result = dynamic_shortest_paths(N, M, edges, sources, Q, updates)
        self.assertEqual(result, expected)

    def test_single_edge_and_update(self):
        N = 2
        M = 1
        edges = [(0, 1, 10)]
        sources = [0]
        Q = 1
        updates = [(0, 1, 5)]
        # After update, the only edge becomes (0,1,5).
        # Distances from node 0: [0, 5]
        expected = [[0, 5]]
        result = dynamic_shortest_paths(N, M, edges, sources, Q, updates)
        self.assertEqual(result, expected)

    def test_unreachable_node(self):
        N = 3
        M = 1
        edges = [(0, 1, 3)]
        sources = [0]
        Q = 1
        updates = [(0, 1, 2)]
        # After update, graph has edge (0,1,2) and node 2 remains unreachable.
        result = dynamic_shortest_paths(N, M, edges, sources, Q, updates)
        # For node 0: distance 0; node 1: distance 2; node 2: unreachable -> float('inf')
        self.assertEqual(result[0][0], 0)
        self.assertEqual(result[0][1], 2)
        self.assertTrue(math.isinf(result[0][2]))

    def test_cycle_graph(self):
        # Graph with a cycle: 0 -> 1 -> 2 -> 0
        N = 3
        M = 3
        edges = [(0, 1, 4), (1, 2, 6), (2, 0, 8)]
        sources = [1]
        Q = 2
        updates = [(0, 1, 2), (2, 0, 3)]
        # After first update:
        # Edges: (0,1,2), (1,2,6), (2,0,8)
        # From source 1:
        # node1 = 0
        # node2 = 6
        # node0 = 1->2->0: 6+8 = 14
        # So distances: [14, 0, 6]
        #
        # After second update:
        # Edges: (0,1,2), (1,2,6), (2,0,3)
        # From source 1:
        # node1 = 0
        # node2 = 6
        # node0 = 1->2->0: 6+3 = 9
        # So distances: [9, 0, 6]
        expected = [
            [14, 0, 6],
            [9, 0, 6]
        ]
        result = dynamic_shortest_paths(N, M, edges, sources, Q, updates)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()