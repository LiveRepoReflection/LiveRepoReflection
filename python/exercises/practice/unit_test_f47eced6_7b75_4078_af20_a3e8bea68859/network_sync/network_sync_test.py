import unittest
from network_sync import min_max_synchronization_time

class TestNetworkSync(unittest.TestCase):
    def test_single_data_center(self):
        n = 1
        edges = []
        data_sizes = [10]
        computational_capacities = [20]
        k = 1
        result = min_max_synchronization_time(n, edges, data_sizes, computational_capacities, k)
        self.assertEqual(result, 0.0)

    def test_singleton_clusters(self):
        n = 4
        edges = [(0, 1, 5), (1, 2, 5), (2, 3, 5)]
        data_sizes = [10, 20, 30, 40]
        computational_capacities = [100, 100, 100, 100]
        k = 4  # Each node in its own cluster; no data transfer needed.
        result = min_max_synchronization_time(n, edges, data_sizes, computational_capacities, k)
        self.assertEqual(result, 0.0)

    def test_invalid_leader_capacity(self):
        n = 3
        edges = [(0, 1, 10), (1, 2, 10), (0, 2, 5)]
        data_sizes = [70, 70, 70]
        computational_capacities = [50, 50, 50]
        k = 1
        result = min_max_synchronization_time(n, edges, data_sizes, computational_capacities, k)
        self.assertEqual(result, -1)

    def test_sample_network(self):
        n = 4
        edges = [(0, 1, 10), (1, 2, 5), (2, 3, 8), (0, 3, 3)]
        data_sizes = [10, 5, 7, 12]
        computational_capacities = [20, 10, 15, 25]
        k = 2
        result = min_max_synchronization_time(n, edges, data_sizes, computational_capacities, k)
        # Since the exact synchronization time depends on chosen paths and leader,
        # we validate that the result is a float and non-negative.
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertNotEqual(result, -1)

    def test_complex_network(self):
        n = 5
        edges = [(0, 1, 10), (0, 2, 15), (1, 3, 10), (2, 3, 10), (3, 4, 5), (1, 4, 20)]
        data_sizes = [5, 10, 20, 25, 30]
        computational_capacities = [50, 60, 70, 80, 100]
        k = 3
        result = min_max_synchronization_time(n, edges, data_sizes, computational_capacities, k)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertNotEqual(result, -1)

if __name__ == '__main__':
    unittest.main()