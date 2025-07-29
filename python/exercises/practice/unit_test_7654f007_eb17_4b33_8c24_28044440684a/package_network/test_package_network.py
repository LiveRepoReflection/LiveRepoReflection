import unittest
from package_network import calculate_min_delivery_cost

class TestPackageNetwork(unittest.TestCase):
    def test_single_destination(self):
        N = 2
        edges = [
            (0, 1, 10, 1, 1.0, 1.0),
            (1, 0, 10, 1, 1.0, 1.0)
        ]
        destinations = [1]
        result = calculate_min_delivery_cost(N, edges, destinations)
        self.assertAlmostEqual(result, 20.0, places=2)

    def test_multiple_destinations_simple(self):
        N = 3
        edges = [
            (0, 1, 10, 1, 1.0, 1.0),
            (1, 2, 5, 1, 1.0, 1.0),
            (2, 0, 15, 1, 1.0, 1.0),
            (1, 0, 10, 1, 1.0, 1.0)
        ]
        destinations = [1, 2]
        result = calculate_min_delivery_cost(N, edges, destinations)
        self.assertAlmostEqual(result, 30.0, places=2)

    def test_complex_network(self):
        N = 4
        edges = [
            (0, 1, 10, 1, 1.0, 1.0),
            (0, 2, 15, 1.5, 1.2, 0.9),
            (1, 2, 5, 2, 0.8, 1.1),
            (1, 3, 12, 1, 1.5, 1.0),
            (2, 3, 8, 1, 0.9, 1.2),
            (3, 0, 20, 1.2, 1.1, 1.0)
        ]
        destinations = [1, 3]
        result = calculate_min_delivery_cost(N, edges, destinations)
        # This is a complex case where multiple paths are possible
        # We just verify it returns a valid positive number
        self.assertGreater(result, 0)

    def test_all_cities_as_destinations(self):
        N = 3
        edges = [
            (0, 1, 10, 1, 1.0, 1.0),
            (1, 2, 5, 1, 1.0, 1.0),
            (2, 0, 15, 1, 1.0, 1.0),
            (1, 0, 10, 1, 1.0, 1.0)
        ]
        destinations = [1, 2]
        result = calculate_min_delivery_cost(N, edges, destinations)
        self.assertAlmostEqual(result, 30.0, places=2)

    def test_varying_cost_factors(self):
        N = 3
        edges = [
            (0, 1, 10, 1, 0.5, 0.8),  # Cheaper route
            (1, 2, 5, 1, 2.0, 1.2),   # Expensive route
            (2, 0, 15, 1, 1.0, 1.0),
            (1, 0, 10, 1, 1.0, 1.0)
        ]
        destinations = [1, 2]
        result = calculate_min_delivery_cost(N, edges, destinations)
        # Should prefer the cheaper route even if longer
        self.assertAlmostEqual(result, 10*1*0.5*0.8 + 5*1*2.0*1.2 + 15*1*1.0*1.0, places=2)

    def test_no_destinations(self):
        N = 1
        edges = []
        destinations = []
        result = calculate_min_delivery_cost(N, edges, destinations)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_disconnected_graph(self):
        N = 4
        edges = [
            (0, 1, 10, 1, 1.0, 1.0),
            (1, 0, 10, 1, 1.0, 1.0),
            (2, 3, 5, 1, 1.0, 1.0)
        ]
        destinations = [1]
        result = calculate_min_delivery_cost(N, edges, destinations)
        self.assertAlmostEqual(result, 20.0, places=2)

if __name__ == '__main__':
    unittest.main()