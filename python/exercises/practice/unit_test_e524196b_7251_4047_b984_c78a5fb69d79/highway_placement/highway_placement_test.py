import unittest
from highway_placement.highway_placement import minimal_highway_cost

class TestHighwayPlacement(unittest.TestCase):
    def test_single_city(self):
        cities = [(0, 0)]
        C = 1.0
        self.assertEqual(minimal_highway_cost(cities, C), 0.0)

    def test_two_cities(self):
        cities = [(0, 0), (3, 4)]
        C = 1.0
        expected = 5.0 + C  # sqrt(3² + 4²) + C
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected)

    def test_three_cities_line(self):
        cities = [(0, 0), (1, 0), (2, 0)]
        C = 0.5
        expected = 2.0 + 2*C  # Two segments of length 1
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected)

    def test_three_cities_triangle(self):
        cities = [(0, 0), (1, 1), (2, 0)]
        C = 0.1
        expected = 2.8284271247461903 + 2*C  # Two segments of sqrt(2)
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected)

    def test_four_cities_square(self):
        cities = [(0, 0), (1, 0), (1, 1), (0, 1)]
        C = 0.5
        expected = 3.0 + 3*C  # Three segments of length 1
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected)

    def test_large_setup_cost(self):
        cities = [(0, 0), (1, 1), (2, 2), (3, 3)]
        C = 10.0
        expected = 4.242640687119285 + 3*C  # One long segment plus two short ones
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected)

    def test_floating_point_precision(self):
        cities = [(0.000001, 0.000001), (0.000002, 0.000002)]
        C = 0.000001
        expected = 0.000001414213562373095 + C
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected, places=10)

    def test_negative_coordinates(self):
        cities = [(-1, -1), (1, 1), (0, 0)]
        C = 1.0
        expected = 2.8284271247461903 + 2*C
        self.assertAlmostEqual(minimal_highway_cost(cities, C), expected)

    def test_large_input(self):
        cities = [(x, x) for x in range(100)]
        C = 0.01
        result = minimal_highway_cost(cities, C)
        self.assertTrue(result > 0)
        self.assertTrue(result < float('inf'))

    def test_no_connection_needed(self):
        cities = [(0, 0)]
        C = 1.0
        self.assertEqual(minimal_highway_cost(cities, C), 0.0)

if __name__ == '__main__':
    unittest.main()