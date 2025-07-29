import unittest
from city_response import find_optimal_stations

class CityResponseTest(unittest.TestCase):
    def test_basic_case(self):
        N, M, K = 4, 4, 2
        P = [100, 200, 300, 400]
        roads = [(1, 2, 10), (2, 3, 5), (3, 4, 20), (1, 4, 30)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertTrue(all(1 <= x <= N for x in result))
        self.assertTrue(len(set(result)) == len(result))  # No duplicates

    def test_minimal_case(self):
        N, M, K = 2, 1, 1
        P = [100, 100]
        roads = [(1, 2, 10)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertTrue(all(1 <= x <= N for x in result))

    def test_all_stations_case(self):
        N, M, K = 3, 3, 3
        P = [100, 100, 100]
        roads = [(1, 2, 10), (2, 3, 10), (1, 3, 15)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertEqual(set(result), set(range(1, N+1)))

    def test_large_case(self):
        N, M, K = 10, 15, 3
        P = [100] * 10
        roads = [(1, 2, 5), (2, 3, 5), (3, 4, 5), (4, 5, 5), (5, 6, 5),
                 (6, 7, 5), (7, 8, 5), (8, 9, 5), (9, 10, 5), (1, 5, 20),
                 (2, 6, 20), (3, 7, 20), (4, 8, 20), (5, 9, 20), (6, 10, 20)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertTrue(all(1 <= x <= N for x in result))

    def test_sparse_graph(self):
        N, M, K = 6, 5, 2
        P = [100, 200, 300, 400, 500, 600]
        roads = [(1, 2, 10), (2, 3, 20), (3, 4, 30), (4, 5, 40), (5, 6, 50)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertTrue(all(1 <= x <= N for x in result))

    def test_dense_graph(self):
        N, M, K = 5, 10, 2
        P = [100, 200, 300, 400, 500]
        roads = [(1, 2, 10), (1, 3, 20), (1, 4, 30), (1, 5, 40),
                 (2, 3, 50), (2, 4, 60), (2, 5, 70),
                 (3, 4, 80), (3, 5, 90),
                 (4, 5, 100)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertTrue(all(1 <= x <= N for x in result))

    def test_varied_populations(self):
        N, M, K = 4, 6, 2
        P = [1000, 100, 10, 1]
        roads = [(1, 2, 10), (1, 3, 10), (1, 4, 10),
                 (2, 3, 10), (2, 4, 10), (3, 4, 10)]
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(len(result), K)
        self.assertTrue(all(1 <= x <= N for x in result))

    def test_boundary_conditions(self):
        # Test with minimum possible values
        N, M, K = 1, 0, 1
        P = [100]
        roads = []
        result = find_optimal_stations(N, M, K, P, roads)
        self.assertEqual(result, [1])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            find_optimal_stations(0, 0, 0, [], [])
        with self.assertRaises(ValueError):
            find_optimal_stations(5, 4, 6, [100]*5, [(1,2,10)]*4)
        with self.assertRaises(ValueError):
            find_optimal_stations(5, 4, 2, [100]*4, [(1,2,10)]*4)

if __name__ == '__main__':
    unittest.main()