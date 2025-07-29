import unittest
from byzantine_consensus import consensus

class ByzantineConsensusTest(unittest.TestCase):
    def test_basic_consensus_no_faults(self):
        initial_values = [1, 2, 3, 4]
        adjacency_list = [
            [1, 2, 3],
            [0, 2, 3],
            [0, 1, 3],
            [0, 1, 2]
        ]
        f = 0
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

    def test_minimal_graph_with_fault(self):
        initial_values = [2, 2, 3, 4]
        adjacency_list = [
            [1, 2, 3],
            [0, 2, 3],
            [0, 1, 3],
            [0, 1, 2]
        ]
        f = 1
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

    def test_larger_network(self):
        initial_values = [1, 1, 1, 2, 2, 2, 3, 3, 3]
        adjacency_list = [
            [1, 2, 3], [0, 2, 4], [0, 1, 5],
            [0, 4, 6], [1, 3, 7], [2, 6, 8],
            [3, 5, 7], [4, 6, 8], [5, 7, 6]
        ]
        f = 2
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

    def test_chain_topology(self):
        initial_values = [1, 2, 3, 4, 5]
        adjacency_list = [
            [1, 2],
            [0, 2, 3],
            [1, 3, 4],
            [2, 4],
            [2, 3]
        ]
        f = 1
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

    def test_all_same_values(self):
        initial_values = [5, 5, 5, 5, 5, 5]
        adjacency_list = [
            [1, 2, 3], [0, 2, 4],
            [0, 1, 5], [0, 4, 5],
            [1, 3, 5], [2, 3, 4]
        ]
        f = 1
        result = consensus(initial_values, adjacency_list, f)
        self.assertEqual(result, 5)

    def test_sparse_graph(self):
        initial_values = [1, 2, 3, 4, 5, 6, 7]
        adjacency_list = [
            [1, 2],
            [0, 3],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 6],
            [4, 5]
        ]
        f = 2
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

    def test_maximum_allowed_faults(self):
        initial_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        adjacency_list = [
            [1, 2, 3], [0, 2, 4], [0, 1, 5],
            [0, 4, 6], [1, 3, 7], [2, 6, 8],
            [3, 5, 9], [4, 8, 9], [5, 7, 9],
            [6, 7, 8]
        ]
        f = 3
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

    def test_edge_cases(self):
        # Minimum number of nodes
        initial_values = [1, 1, 1]
        adjacency_list = [[1, 2], [0, 2], [0, 1]]
        f = 0
        result = consensus(initial_values, adjacency_list, f)
        self.assertEqual(result, 1)

        # Maximum value in allowed range
        initial_values = [1000, 1000, 1000, 1000]
        adjacency_list = [
            [1, 2, 3],
            [0, 2, 3],
            [0, 1, 3],
            [0, 1, 2]
        ]
        result = consensus(initial_values, adjacency_list, f)
        self.assertEqual(result, 1000)

    def test_invalid_inputs(self):
        # Too many Byzantine nodes
        initial_values = [1, 2, 3]
        adjacency_list = [[1, 2], [0, 2], [0, 1]]
        f = 2
        with self.assertRaises(ValueError):
            consensus(initial_values, adjacency_list, f)

        # Empty graph
        with self.assertRaises(ValueError):
            consensus([], [], 0)

        # Mismatched lengths
        initial_values = [1, 2]
        adjacency_list = [[1], [0], [1]]
        with self.assertRaises(ValueError):
            consensus(initial_values, adjacency_list, 0)

    def test_cycle_topology(self):
        initial_values = [1, 2, 3, 4, 5, 6]
        adjacency_list = [
            [1, 5], [0, 2],
            [1, 3], [2, 4],
            [3, 5], [4, 0]
        ]
        f = 1
        result = consensus(initial_values, adjacency_list, f)
        self.assertIn(result, initial_values)

if __name__ == '__main__':
    unittest.main()