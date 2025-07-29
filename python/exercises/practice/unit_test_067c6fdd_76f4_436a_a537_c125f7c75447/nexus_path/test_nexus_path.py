import unittest
from nexus_path import find_most_efficient_path

class TestNexusPath(unittest.TestCase):
    def test_direct_connection(self):
        network = {
            1: {'friend_ids': [2], 'latency': 10},
            2: {'friend_ids': [1], 'latency': 20}
        }
        result = find_most_efficient_path(network, 1, 2, 1)
        self.assertEqual(result, [1, 2])

    def test_no_path_exists(self):
        network = {
            1: {'friend_ids': [2], 'latency': 10},
            2: {'friend_ids': [1], 'latency': 20},
            3: {'friend_ids': [], 'latency': 30}
        }
        result = find_most_efficient_path(network, 1, 3, 2)
        self.assertEqual(result, [])

    def test_same_start_and_end(self):
        network = {
            1: {'friend_ids': [2], 'latency': 10},
            2: {'friend_ids': [1], 'latency': 20}
        }
        result = find_most_efficient_path(network, 1, 1, 5)
        self.assertEqual(result, [1])

    def test_multiple_paths(self):
        network = {
            1: {'friend_ids': [2, 3], 'latency': 50},
            2: {'friend_ids': [1, 4], 'latency': 100},
            3: {'friend_ids': [1, 5], 'latency': 200},
            4: {'friend_ids': [2, 5, 6], 'latency': 50},
            5: {'friend_ids': [3, 4], 'latency': 150},
            6: {'friend_ids': [4], 'latency': 300}
        }
        result = find_most_efficient_path(network, 1, 6, 3)
        self.assertEqual(result, [1, 2, 4, 6])

    def test_max_hops_constraint(self):
        network = {
            1: {'friend_ids': [2], 'latency': 10},
            2: {'friend_ids': [1, 3], 'latency': 20},
            3: {'friend_ids': [2, 4], 'latency': 30},
            4: {'friend_ids': [3], 'latency': 40}
        }
        result = find_most_efficient_path(network, 1, 4, 2)
        self.assertEqual(result, [])

    def test_invalid_user_ids(self):
        network = {
            1: {'friend_ids': [2], 'latency': 10},
            2: {'friend_ids': [1], 'latency': 20}
        }
        result = find_most_efficient_path(network, 1, 3, 1)
        self.assertEqual(result, [])
        result = find_most_efficient_path(network, 3, 1, 1)
        self.assertEqual(result, [])

    def test_latency_vs_hops_tradeoff(self):
        network = {
            1: {'friend_ids': [2, 3], 'latency': 100},
            2: {'friend_ids': [1, 4], 'latency': 100},
            3: {'friend_ids': [1, 4], 'latency': 10},
            4: {'friend_ids': [2, 3], 'latency': 100}
        }
        result = find_most_efficient_path(network, 1, 4, 2)
        self.assertEqual(result, [1, 3, 4])

    def test_complex_network(self):
        network = {
            1: {'friend_ids': [2, 5], 'latency': 10},
            2: {'friend_ids': [1, 3], 'latency': 20},
            3: {'friend_ids': [2, 4], 'latency': 30},
            4: {'friend_ids': [3, 5, 6], 'latency': 40},
            5: {'friend_ids': [1, 4], 'latency': 50},
            6: {'friend_ids': [4, 7], 'latency': 60},
            7: {'friend_ids': [6], 'latency': 70}
        }
        result = find_most_efficient_path(network, 1, 7, 4)
        self.assertEqual(result, [1, 5, 4, 6, 7])

    def test_cyclic_graph(self):
        network = {
            1: {'friend_ids': [2, 3], 'latency': 10},
            2: {'friend_ids': [1, 3], 'latency': 20},
            3: {'friend_ids': [1, 2, 4], 'latency': 30},
            4: {'friend_ids': [3], 'latency': 40}
        }
        result = find_most_efficient_path(network, 1, 4, 3)
        self.assertEqual(result, [1, 3, 4])

    def test_sparse_network(self):
        network = {
            1: {'friend_ids': [2], 'latency': 10},
            2: {'friend_ids': [1, 3], 'latency': 20},
            3: {'friend_ids': [2, 4], 'latency': 30},
            4: {'friend_ids': [3, 5], 'latency': 40},
            5: {'friend_ids': [4], 'latency': 50}
        }
        result = find_most_efficient_path(network, 1, 5, 4)
        self.assertEqual(result, [1, 2, 3, 4, 5])

if __name__ == '__main__':
    unittest.main()