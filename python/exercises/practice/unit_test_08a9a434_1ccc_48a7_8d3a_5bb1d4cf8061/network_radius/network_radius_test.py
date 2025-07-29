import unittest
import math
from network_radius import find_minimum_radius

class NetworkRadiusTest(unittest.TestCase):
    def test_single_building(self):
        buildings = [(0, 0)]
        k = 1
        expected = 0.0
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

    def test_two_buildings_single_ap(self):
        buildings = [(0, 0), (4, 0)]
        k = 1
        expected = 2.0  # AP placed at (2,0) covers both buildings
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

    def test_two_buildings_two_aps(self):
        buildings = [(0, 0), (4, 0)]
        k = 2
        expected = 0.0  # Each building gets its own AP
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

    def test_square_buildings(self):
        # Four points forming a square: optimal grouping splits them into two pairs.
        buildings = [(0, 0), (0, 2), (2, 0), (2, 2)]
        k = 2
        expected = 1.0  # Each pair can be covered with an AP placed at the midpoint.
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

    def test_line_buildings(self):
        # Buildings in a straight line: clustering into two groups provides optimal coverage.
        buildings = [(0, 0), (2, 0), (4, 0), (6, 0)]
        k = 2
        expected = 1.0  # Group [(0,0),(2,0)] and [(4,0),(6,0)] => each covered by a circle of radius 1.0.
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

    def test_more_aps_than_buildings(self):
        # Extra APs allow each building to be individually covered.
        buildings = [(1, 2), (3, 4), (5, 6)]
        k = 5
        expected = 0.0
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

    def test_complex_scenario(self):
        # Multiple clusters: two tight clusters and one isolated building.
        buildings = [
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1),
            (10, 10),
            (10, 11),
            (11, 10),
            (11, 11),
            (5, 5)
        ]
        k = 3
        # Optimal grouping:
        # Cluster 1: first four points (optimal circle center ~ (0.5, 0.5), radius ≈ 0.70711)
        # Cluster 2: next four points (optimal circle center ~ (10.5, 10.5), radius ≈ 0.70711)
        # Cluster 3: the isolated building (5,5) covered exactly with 0 radius.
        # The minimum required radius is the maximum of these, ~0.70711.
        expected = 0.70710678
        result = find_minimum_radius(buildings, k)
        self.assertAlmostEqual(result, expected, delta=1e-5)

if __name__ == '__main__':
    unittest.main()