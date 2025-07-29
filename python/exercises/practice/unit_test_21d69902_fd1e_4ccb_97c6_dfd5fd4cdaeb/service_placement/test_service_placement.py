import unittest
from service_placement.service_placement import assign_microservices

class TestServicePlacement(unittest.TestCase):
    def test_basic_case(self):
        N = 4
        M = 2
        edges = [(0, 1, 10), (1, 2, 15), (2, 3, 20), (0, 3, 5)]
        latency_matrix = [[1, 50], [50, 1]]
        result = assign_microservices(N, M, edges, latency_matrix)
        self.assertEqual(len(result), N)
        self.assertTrue(all(dc in {0, 1} for dc in result))

    def test_single_data_center(self):
        N = 3
        M = 1
        edges = [(0, 1, 5), (1, 2, 10)]
        latency_matrix = [[0]]
        result = assign_microservices(N, M, edges, latency_matrix)
        self.assertEqual(result, [0, 0, 0])

    def test_disconnected_graph(self):
        N = 5
        M = 2
        edges = [(0, 1, 10), (2, 3, 15)]
        latency_matrix = [[1, 20], [20, 1]]
        result = assign_microservices(N, M, edges, latency_matrix)
        self.assertEqual(len(result), N)

    def test_more_data_centers_than_services(self):
        N = 2
        M = 4
        edges = [(0, 1, 100)]
        latency_matrix = [[0, 5, 5, 5], [5, 0, 5, 5], [5, 5, 0, 5], [5, 5, 5, 0]]
        result = assign_microservices(N, M, edges, latency_matrix)
        self.assertEqual(len(result), N)
        self.assertTrue(all(dc in {0, 1, 2, 3} for dc in result))

    def test_high_latency_case(self):
        N = 3
        M = 2
        edges = [(0, 1, 1), (1, 2, 1), (0, 2, 100)]
        latency_matrix = [[0, 1000], [1000, 0]]
        result = assign_microservices(N, M, edges, latency_matrix)
        self.assertEqual(len(result), N)
        self.assertEqual(result[0], result[2])

    def test_large_input(self):
        N = 100
        M = 10
        edges = [(i, i+1, 1) for i in range(N-1)]
        latency_matrix = [[1 if i == j else 10 for j in range(M)] for i in range(M)]
        result = assign_microservices(N, M, edges, latency_matrix)
        self.assertEqual(len(result), N)
        self.assertTrue(all(dc in range(M) for dc in result))

if __name__ == '__main__':
    unittest.main()