import unittest
from optimal_train_routing import find_optimal_routes

class TestOptimalTrainRouting(unittest.TestCase):
    def test_simple_network(self):
        N = 3
        M = 2
        tracks = [
            (0, 1, 2, 5),
            (1, 2, 2, 3)
        ]
        K = 2
        trains = [
            (0, 2, 0, 1),
            (0, 2, 1, 1)
        ]
        expected = [
            [0, 1, 2],
            [0, 1, 2]
        ]
        result = find_optimal_routes(N, M, tracks, K, trains)
        self.assertEqual(result, expected)

    def test_capacity_constraints(self):
        N = 2
        M = 1
        tracks = [
            (0, 1, 1, 2)
        ]
        K = 2
        trains = [
            (0, 1, 0, 1),
            (0, 1, 1, 1)
        ]
        expected = [
            [0, 1],
            [0, 1]  # Second train must wait until first clears track
        ]
        result = find_optimal_routes(N, M, tracks, K, trains)
        self.assertEqual(result, expected)

    def test_no_possible_route(self):
        N = 4
        M = 2
        tracks = [
            (0, 1, 1, 1),
            (2, 3, 1, 1)
        ]
        K = 1
        trains = [
            (0, 3, 0, 1)
        ]
        expected = [
            []
        ]
        result = find_optimal_routes(N, M, tracks, K, trains)
        self.assertEqual(result, expected)

    def test_complex_network(self):
        N = 5
        M = 6
        tracks = [
            (0, 1, 2, 3),
            (0, 2, 1, 5),
            (1, 2, 2, 2),
            (1, 3, 3, 4),
            (2, 4, 1, 6),
            (3, 4, 2, 3)
        ]
        K = 3
        trains = [
            (0, 4, 0, 2),
            (1, 4, 2, 1),
            (3, 0, 1, 1)
        ]
        # Multiple valid solutions possible due to different paths with same weighted time
        result = find_optimal_routes(N, M, tracks, K, trains)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(len(route) > 0 for route in result))

    def test_parallel_tracks(self):
        N = 2
        M = 2
        tracks = [
            (0, 1, 1, 5),
            (0, 1, 2, 8)
        ]
        K = 3
        trains = [
            (0, 1, 0, 1),
            (0, 1, 0, 1),
            (0, 1, 0, 1)
        ]
        result = find_optimal_routes(N, M, tracks, K, trains)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(len(route) == 2 for route in result))

    def test_large_network(self):
        N = 10
        M = 15
        tracks = [
            (0, 1, 3, 2), (1, 2, 2, 3), (2, 3, 4, 1),
            (3, 4, 2, 5), (4, 5, 3, 2), (5, 6, 1, 4),
            (6, 7, 2, 3), (7, 8, 3, 2), (8, 9, 2, 1),
            (0, 3, 2, 6), (1, 4, 3, 4), (2, 5, 2, 3),
            (3, 6, 1, 5), (4, 7, 2, 4), (5, 8, 3, 3)
        ]
        K = 5
        trains = [
            (0, 9, 0, 2),
            (1, 8, 1, 1),
            (2, 7, 2, 3),
            (3, 6, 3, 1),
            (4, 5, 4, 2)
        ]
        result = find_optimal_routes(N, M, tracks, K, trains)
        self.assertEqual(len(result), 5)
        self.assertTrue(all(len(route) > 0 for route in result))

    def test_empty_inputs(self):
        with self.assertRaises(ValueError):
            find_optimal_routes(0, 0, [], 0, [])

    def test_invalid_track(self):
        N = 2
        M = 1
        tracks = [
            (0, 1, 0, 5)  # Invalid capacity
        ]
        K = 1
        trains = [
            (0, 1, 0, 1)
        ]
        with self.assertRaises(ValueError):
            find_optimal_routes(N, M, tracks, K, trains)

if __name__ == '__main__':
    unittest.main()