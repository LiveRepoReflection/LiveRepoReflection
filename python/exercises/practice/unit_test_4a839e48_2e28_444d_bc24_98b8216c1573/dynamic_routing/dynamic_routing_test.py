import unittest
import math
from dynamic_routing import solve

class DynamicRoutingTest(unittest.TestCase):
    def test_no_updates(self):
        # Test when there are no update operations.
        N = 4
        edges = [(0, 1, 5), (1, 2, 3)]
        sources = [0]
        updates = []
        expected = []
        result = solve(N, edges, sources, updates)
        self.assertEqual(result, expected)

    def test_chain_updates(self):
        # Graph with 4 nodes and initial edges, then two updates:
        # Update 1: Add edge (2, 3) with weight 2.
        # Update 2: Change weight of edge (0, 1) from 5 to 2.
        # After first update:
        #   Graph becomes: (0, 1, 5), (1, 2, 3), (2, 3, 2)
        #   From source 0: distances are: 0->0 = 0, 0->1 = 5, 0->2 = 5+3 = 8, 0->3 = 5+3+2 = 10; total = 23.
        # After second update:
        #   Graph becomes: (0, 1, 2), (1, 2, 3), (2, 3, 2)
        #   From source 0: distances are: 0->0 = 0, 0->1 = 2, 0->2 = 2+3 = 5, 0->3 = 2+3+2 = 7; total = 14.
        N = 4
        edges = [(0, 1, 5), (1, 2, 3)]
        sources = [0]
        updates = [(1, 2, 3, 2), (2, 0, 1, 2)]
        expected = [23, 14]
        result = solve(N, edges, sources, updates)
        self.assertEqual(result, expected)

    def test_isolated_nodes(self):
        # Graph with three nodes and no initial edges.
        # Sources: [0, 2]. Update: create edge (0, 1) with weight 4.
        # After the update:
        #   For source 0: distances = [0, 4, inf]
        #   For source 2: distances = [inf, inf, 0]
        # Total cost becomes inf.
        N = 3
        edges = []
        sources = [0, 2]
        updates = [(1, 0, 1, 4)]
        expected = [float('inf')]
        result = solve(N, edges, sources, updates)
        # Check if the result is infinity.
        self.assertTrue(math.isinf(result[0]))

    def test_negative_update(self):
        # Test that a negative update weight results in a weight of 0.
        # Initial graph: 3 nodes, edges (0,1,10) and (1,2,10) with source 0.
        # Update: change weight of edge (0,1) to -5, which should be treated as 0.
        # New distances from source 0: [0, 0, 0+10=10]; total = 10.
        N = 3
        edges = [(0, 1, 10), (1, 2, 10)]
        sources = [0]
        updates = [(1, 0, 1, -5)]
        expected = [10]
        result = solve(N, edges, sources, updates)
        self.assertEqual(result, expected)

    def test_multi_source_update(self):
        # Multi-source graph with 5 nodes.
        # Initial graph: a straight line (0-1-2-3-4) with equal weights.
        # Sources: [0, 4].
        # Three updates:
        #   1) Update (1,2) weight from 2 to 1.
        #   2) Update (2,3) weight from 2 to 3.
        #   3) Add new edge (0,4) with weight 10.
        #
        # After update 1: Graph = (0,1,2), (1,2,1), (2,3,2), (3,4,2)
        #   From source 0: distances = [0, 2, 3, 5, 7] => sum = 17.
        #   From source 4: distances = [7, 5, 4, 2, 0] => sum = 18.
        #   Total = 17 + 18 = 35.
        #
        # After update 2: Graph = (0,1,2), (1,2,1), (2,3,3), (3,4,2)
        #   From source 0: distances = [0, 2, 3, 6, 8] => sum = 19.
        #   From source 4: distances = [8, 6, 5, 2, 0] => sum = 21.
        #   Total = 19 + 21 = 40.
        #
        # After update 3: New edge (0,4,10) is added, but the shortest paths remain unchanged.
        #   Total cost remains 40.
        N = 5
        edges = [(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2)]
        sources = [0, 4]
        updates = [
            (1, 1, 2, 1),
            (2, 2, 3, 3),
            (3, 0, 4, 10)
        ]
        expected = [35, 40, 40]
        result = solve(N, edges, sources, updates)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()