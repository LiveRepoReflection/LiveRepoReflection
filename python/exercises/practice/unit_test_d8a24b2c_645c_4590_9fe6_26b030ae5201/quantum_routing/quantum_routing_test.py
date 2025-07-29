import unittest
from quantum_routing.quantum_routing import find_optimal_path

class TestQuantumRouting(unittest.TestCase):
    def test_basic_path(self):
        N = 4
        adj_matrix = [
            [0, 1, 0, 0],
            [1, 0, 1, 1],
            [0, 1, 0, 1],
            [0, 1, 1, 0]
        ]
        capacity = [1, 2, 1, 2]
        S = 0
        D = 3
        decay_factor = 0.9
        expected = [0, 1, 3]
        self.assertEqual(find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor), expected)

    def test_no_path_exists(self):
        N = 4
        adj_matrix = [
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ]
        capacity = [1, 1, 1, 1]
        S = 0
        D = 3
        decay_factor = 0.9
        expected = []
        self.assertEqual(find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor), expected)

    def test_capacity_constraint(self):
        N = 4
        adj_matrix = [
            [0, 1, 1, 0],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [0, 1, 1, 0]
        ]
        capacity = [1, 0, 1, 1]
        S = 0
        D = 3
        decay_factor = 0.9
        expected = [0, 2, 3]
        self.assertEqual(find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor), expected)

    def test_multiple_paths_same_fidelity(self):
        N = 5
        adj_matrix = [
            [0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0],
            [1, 1, 0, 1, 1],
            [0, 1, 1, 0, 1],
            [0, 0, 1, 1, 0]
        ]
        capacity = [1, 1, 2, 1, 1]
        S = 0
        D = 4
        decay_factor = 0.9
        possible_paths = [[0, 1, 2, 4], [0, 2, 4]]
        result = find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor)
        self.assertTrue(result in possible_paths)

    def test_large_network(self):
        N = 6
        adj_matrix = [
            [0, 1, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0],
            [0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 1, 1, 0]
        ]
        capacity = [1, 1, 1, 2, 1, 1]
        S = 0
        D = 5
        decay_factor = 0.8
        expected = [0, 1, 2, 3, 5]
        self.assertEqual(find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor), expected)

    def test_decay_factor_impact(self):
        N = 4
        adj_matrix = [
            [0, 1, 0, 0],
            [1, 0, 1, 2],
            [0, 1, 0, 1],
            [0, 2, 1, 0]
        ]
        capacity = [1, 2, 1, 2]
        S = 0
        D = 3
        decay_factor = 0.5
        expected = [0, 1, 3]
        self.assertEqual(find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor), expected)

    def test_all_nodes_zero_capacity(self):
        N = 3
        adj_matrix = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ]
        capacity = [0, 0, 0]
        S = 0
        D = 2
        decay_factor = 0.9
        expected = []
        self.assertEqual(find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor), expected)

if __name__ == '__main__':
    unittest.main()