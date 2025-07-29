import unittest
from edge_connect import min_edge_weight_for_k_components


class EdgeConnectTest(unittest.TestCase):
    def test_k_equals_n(self):
        points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        k = 4
        expected = 0.0
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_k_equals_one(self):
        points = [(0, 0), (1, 1), (2, 2)]
        k = 1
        # Minimum spanning tree: (0,0)-(1,1) + (1,1)-(2,2) = sqrt(2) + sqrt(2) = 2*sqrt(2)
        expected = 2 * (2 ** 0.5)
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_simple_square(self):
        points = [(0, 0), (0, 1), (1, 0), (1, 1)]
        k = 2
        # MST has 3 edges, removing heaviest creates 2 components
        expected = 2.0  # Two edges of length 1
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_six_points_in_grid(self):
        points = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        k = 3
        # MST has 5 edges, removing 2 heaviest creates 3 components
        expected = 3.0  # Three edges of length 1
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_collinear_points(self):
        points = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        k = 2
        # If we remove the middle edge, we get two components with total weight 3
        expected = 3.0
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_duplicated_points(self):
        points = [(0, 0), (0, 0), (1, 1), (1, 1)]
        k = 2
        # Two groups of duplicated points, one edge with sqrt(2) distance
        expected = 0.0
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_large_random_case(self):
        # Create a larger test case with a grid of points
        grid_size = 10
        points = [(i, j) for i in range(grid_size) for j in range(grid_size)]
        k = 20
        
        # We won't validate exact result, but make sure the function completes
        result = min_edge_weight_for_k_components(points, k)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_scattered_points(self):
        points = [(1, 1), (4, 5), (7, 2), (3, 8), (10, 4), (2, 6)]
        k = 3
        # We're testing the algorithm works, not the specific value
        result = min_edge_weight_for_k_components(points, k)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_edge_case_k_equals_n_minus_one(self):
        points = [(0, 0), (3, 0), (0, 4)]
        k = 2
        # Only need to connect two closest points
        expected = 3.0  # min distance between any two points
        self.assertAlmostEqual(min_edge_weight_for_k_components(points, k), expected, places=5)

    def test_invalid_k_greater_than_n(self):
        points = [(0, 0), (1, 1)]
        k = 3
        with self.assertRaises(ValueError):
            min_edge_weight_for_k_components(points, k)

    def test_invalid_k_less_than_one(self):
        points = [(0, 0), (1, 1)]
        k = 0
        with self.assertRaises(ValueError):
            min_edge_weight_for_k_components(points, k)

    def test_precision_handling(self):
        # Points that would produce floating point precision issues
        points = [(0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4)]
        k = 2
        result = min_edge_weight_for_k_components(points, k)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()