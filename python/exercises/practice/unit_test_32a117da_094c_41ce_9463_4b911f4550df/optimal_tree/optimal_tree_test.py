import unittest
from optimal_tree.optimal_tree import optimal_tree

class TestOptimalTree(unittest.TestCase):
    def test_basic_small(self):
        # Graph: 0->1(2), 0->2(4), 1->2(1), 1->3(7), 2->4(3), 3->5(1), 4->5(5)
        N = 6
        M = 7
        edges = [
            (0, 1, 2),
            (0, 2, 4),
            (1, 2, 1),
            (1, 3, 7),
            (2, 4, 3),
            (3, 5, 1),
            (4, 5, 5)
        ]
        K = 2
        sources = [0, 5]
        # Expected output as per problem description example
        result = optimal_tree(N, M, edges, K, sources)
        self.assertEqual(result, 10)

    def test_disconnected_graph(self):
        # Graph where some nodes are unreachable from the given sources.
        N = 4
        M = 1
        edges = [
            (0, 1, 3)
        ]
        K = 1
        sources = [0]
        # Nodes 2 and 3 are unreachable so the function should return -1.
        result = optimal_tree(N, M, edges, K, sources)
        self.assertEqual(result, -1)

    def test_cycle_graph(self):
        # Graph with a cycle: 0->1, 1->2, 2->0, plus an extra edge from 0 to 2.
        N = 3
        M = 4
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 0, 1),
            (0, 2, 2)
        ]
        K = 1
        sources = [0]
        # Shortest distances: 0:0, 1:1, 2:2. Optimal tree can be built with edges (0,1,1) and (1,2,1).
        result = optimal_tree(N, M, edges, K, sources)
        self.assertEqual(result, 2)

    def test_multiple_paths(self):
        # Graph with multiple valid paths leading to trade-offs.
        N = 5
        M = 7
        edges = [
            (0, 1, 1),
            (0, 2, 5),
            (1, 2, 1),
            (1, 3, 2),
            (2, 3, 1),
            (2, 4, 2),
            (3, 4, 1)
        ]
        K = 1
        sources = [0]
        # Shortest distances:
        # 0:0, 1:1, 2:2, 3:3, 4:4.
        # An optimal tree may choose edges (0,1,1), (1,2,1), (1,3,2), (3,4,1) with a total cost of 5.
        result = optimal_tree(N, M, edges, K, sources)
        self.assertEqual(result, 5)

    def test_multiple_sources(self):
        # Graph with two sources where different nodes may approach from different roots.
        N = 5
        M = 6
        edges = [
            (0, 1, 3),
            (1, 2, 4),
            (2, 3, 5),
            (3, 4, 6),
            (4, 1, 2),
            (2, 4, 1)
        ]
        K = 2
        sources = [0, 3]
        # Expected shortest distances:
        # Node 0: 0, Node 1: 3, Node 2: 7, Node 3: 0, Node 4: 6.
        # One optimal selection: For node 1 choose edge (0,1,3), for node 2 choose (1,2,4), for node 4 choose (3,4,6)
        # Total cost = 3 + 4 + 6 = 13.
        result = optimal_tree(N, M, edges, K, sources)
        self.assertEqual(result, 13)

if __name__ == '__main__':
    unittest.main()