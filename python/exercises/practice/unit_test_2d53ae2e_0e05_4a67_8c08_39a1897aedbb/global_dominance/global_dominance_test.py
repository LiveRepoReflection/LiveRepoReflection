import unittest
from global_dominance import find_dominating_set

class GlobalDominanceTest(unittest.TestCase):

    def test_single_node(self):
        # Graph with a single node and no edges. 
        # Only possible dominating set is the node itself.
        graph = {0: []}
        K = 5
        expected_size = 1
        expected_set = [0]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_chain_graph(self):
        # Graph: 0 -> [(1,10), (2,5)], 1 -> [(2,3)], 2 -> [(3,2)], 3 -> []
        # K = 7, valid dominating set: [0,1] is lexicographically smallest.
        graph = {
            0: [(1, 10), (2, 5)],
            1: [(2, 3)],
            2: [(3, 2)],
            3: []
        }
        K = 7
        expected_size = 2
        expected_set = [0, 1]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_disconnected_components(self):
        # Two disconnected components:
        # Component 1: 0 -> [(1,1)], 1 -> []
        # Component 2: 2 -> [(3,1)], 3 -> []
        # K = 2, expected dominating set is [0,2]
        graph = {
            0: [(1, 1)],
            1: [],
            2: [(3, 1)],
            3: []
        }
        K = 2
        expected_size = 2
        expected_set = [0, 2]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_small_K_requires_all_nodes(self):
        # Graph: 0 -> [(1,5)], 1 -> []
        # With K = 1, edge latencies exceed threshold, so entire set is needed.
        graph = {
            0: [(1, 5)],
            1: []
        }
        K = 1
        expected_size = 2
        expected_set = [0, 1]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_cycle_graph(self):
        # Graph with a cycle:
        # 0 -> [(1,2)], 1 -> [(2,2)], 2 -> [(0,2)]
        # K = 2, minimal dominating set is of size 2.
        # Possible answers: [0,1] or [0,2] or [1,2]; lexicographically smallest is [0,1]
        graph = {
            0: [(1,2)],
            1: [(2,2)],
            2: [(0,2)]
        }
        K = 2
        expected_size = 2
        expected_set = [0, 1]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_multiple_valid_solutions(self):
        # Graph:
        # 0 -> [(1,1), (2,4)]
        # 1 -> [(2,1)]
        # 2 -> [(3,1)]
        # 3 -> []
        # K = 2, possible dominating sets [0,1] or [0,2] are valid.
        # Lexicographically smallest is [0,1].
        graph = {
            0: [(1,1), (2,4)],
            1: [(2,1)],
            2: [(3,1)],
            3: []
        }
        K = 2
        expected_size = 2
        expected_set = [0, 1]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_unreachable_node(self):
        # Graph:
        # 0 -> [(1,2)], 1 -> [], 2 -> []
        # Here node 2 is isolated and must be in the dominating set.
        # K = 2, expected dominating set: [0,2] (since 0 covers 1).
        graph = {
            0: [(1,2)],
            1: [],
            2: []
        }
        K = 2
        expected_size = 2
        expected_set = [0, 2]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

    def test_zero_latency_threshold(self):
        # When K = 0, no edge can cover any node, so every node must be in the dominating set.
        # Graph: 0 -> [(1,1)], 1 -> [(2,1)], 2 -> []
        # Expected dominating set: [0,1,2]
        graph = {
            0: [(1,1)],
            1: [(2,1)],
            2: []
        }
        K = 0
        expected_size = 3
        expected_set = [0, 1, 2]
        size, dominating_set = find_dominating_set(graph, K)
        self.assertEqual(size, expected_size)
        self.assertEqual(dominating_set, expected_set)

if __name__ == '__main__':
    unittest.main()