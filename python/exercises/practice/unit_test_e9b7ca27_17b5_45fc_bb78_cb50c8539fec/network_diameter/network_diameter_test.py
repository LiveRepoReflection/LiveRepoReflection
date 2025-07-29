import unittest
from network_diameter import find_min_network_diameter

class TestNetworkDiameter(unittest.TestCase):
    def test_single_city(self):
        # With one city, no connections are needed; diameter is 0.
        N = 1
        B = 10
        connections = []
        self.assertEqual(find_min_network_diameter(N, B, connections), 0)

    def test_disconnected_cities(self):
        # More than one city but no connections available, should return -1.
        N = 3
        B = 50
        connections = []
        self.assertEqual(find_min_network_diameter(N, B, connections), -1)

    def test_simple_connection(self):
        # Two cities with one direct connection equal to the budget.
        N = 2
        B = 20
        connections = [(1, 2, 20, 15)]
        self.assertEqual(find_min_network_diameter(N, B, connections), 15)
    
    def test_sample_example(self):
        # Provided sample scenario:
        N = 4
        B = 200
        connections = [
            (1, 2, 50, 10),
            (1, 3, 75, 15),
            (1, 4, 100, 20),
            (2, 3, 60, 12),
            (2, 4, 80, 16),
            (3, 4, 40, 8)
        ]
        # Expected optimal network deployment gives the minimal network diameter of 30.
        self.assertEqual(find_min_network_diameter(N, B, connections), 30)

    def test_complex_case(self):
        # A more complex graph with 5 cities and multiple possible paths.
        N = 5
        B = 40
        connections = [
            (1, 2, 10, 5),
            (2, 3, 10, 5),
            (3, 4, 10, 5),
            (4, 5, 10, 5),
            (1, 3, 50, 20),
            (2, 4, 5, 3),
            (1, 5, 100, 50),
            (2, 5, 20, 10)
        ]
        # One optimal deployment is to use:
        # (1,2,10,5), (2,3,10,5), (2,4,5,3), (4,5,10,5)
        # Total cost = 10 + 10 + 5 + 10 = 35 <= B, and maximum shortest path latency is 13.
        self.assertEqual(find_min_network_diameter(N, B, connections), 13)

if __name__ == '__main__':
    unittest.main()