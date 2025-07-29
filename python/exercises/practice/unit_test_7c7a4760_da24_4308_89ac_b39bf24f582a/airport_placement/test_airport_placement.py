import unittest
from airport_placement import optimal_airport_placement

class TestAirportPlacement(unittest.TestCase):
    def test_small_graph(self):
        N = 4
        roads = [(1, 2, 5), (1, 3, 9), (2, 3, 3), (2, 4, 6), (3, 4, 4)]
        population = [1000, 1500, 800, 1200]
        self.assertEqual(optimal_airport_placement(N, roads, population), 2)

    def test_single_city(self):
        N = 1
        roads = []
        population = [500]
        self.assertEqual(optimal_airport_placement(N, roads, population), 1)

    def test_equal_populations(self):
        N = 3
        roads = [(1, 2, 10), (2, 3, 10)]
        population = [1000, 1000, 1000]
        self.assertEqual(optimal_airport_placement(N, roads, population), 2)

    def test_linear_graph(self):
        N = 5
        roads = [(1, 2, 2), (2, 3, 2), (3, 4, 2), (4, 5, 2)]
        population = [100, 200, 300, 400, 500]
        self.assertEqual(optimal_airport_placement(N, roads, population), 4)

    def test_star_graph(self):
        N = 4
        roads = [(1, 2, 1), (1, 3, 1), (1, 4, 1)]
        population = [100, 200, 300, 400]
        self.assertEqual(optimal_airport_placement(N, roads, population), 1)

    def test_multiple_roads_between_cities(self):
        N = 3
        roads = [(1, 2, 5), (1, 2, 3), (2, 3, 10), (2, 3, 4)]
        population = [500, 1000, 1500]
        self.assertEqual(optimal_airport_placement(N, roads, population), 2)

    def test_tie_breaker(self):
        N = 3
        roads = [(1, 2, 2), (2, 3, 2)]
        population = [1000, 1000, 1000]
        self.assertEqual(optimal_airport_placement(N, roads, population), 2)

    def test_large_graph(self):
        N = 6
        roads = [
            (1, 2, 7), (1, 3, 9), (1, 6, 14),
            (2, 3, 10), (2, 4, 15),
            (3, 4, 11), (3, 6, 2),
            (4, 5, 6),
            (5, 6, 9)
        ]
        population = [100, 200, 300, 400, 500, 600]
        self.assertEqual(optimal_airport_placement(N, roads, population), 6)

if __name__ == '__main__':
    unittest.main()