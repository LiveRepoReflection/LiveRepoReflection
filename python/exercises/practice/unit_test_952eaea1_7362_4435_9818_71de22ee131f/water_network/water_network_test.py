import unittest
from water_network import min_cost_water_network

class WaterNetworkTest(unittest.TestCase):
    def test_empty_city(self):
        """Test case for empty city (n=0)"""
        self.assertEqual(min_cost_water_network(0, []), 0)

    def test_single_building(self):
        """Test case for single building"""
        self.assertEqual(min_cost_water_network(1, [(0, 1, 5)]), 5)
        self.assertEqual(min_cost_water_network(1, []), -1)

    def test_two_buildings(self):
        """Test case for two buildings"""
        self.assertEqual(min_cost_water_network(2, [(0, 1, 1), (0, 2, 2), (1, 2, 3)]), 3)
        self.assertEqual(min_cost_water_network(2, [(1, 2, 3)]), -1)

    def test_disconnected_network(self):
        """Test case for disconnected network"""
        self.assertEqual(min_cost_water_network(3, [(0, 1, 1), (2, 3, 1)]), -1)
        self.assertEqual(min_cost_water_network(4, [(1, 2, 1), (2, 3, 1), (3, 4, 1)]), -1)

    def test_duplicate_pipes(self):
        """Test case for duplicate pipes with different costs"""
        self.assertEqual(
            min_cost_water_network(2, [(0, 1, 5), (0, 1, 2), (1, 2, 3)]), 5)

    def test_complex_network(self):
        """Test case for complex network"""
        pipes = [
            (0, 1, 1), (0, 2, 5), (1, 2, 2), (2, 3, 3),
            (1, 3, 6), (0, 3, 8)
        ]
        self.assertEqual(min_cost_water_network(3, pipes), 6)

    def test_large_network(self):
        """Test case for large network"""
        # Create a star-shaped network with center at 0
        pipes = [(0, i, i) for i in range(1, 1001)]
        self.assertEqual(min_cost_water_network(1000, pipes), sum(range(1, 1001)))

    def test_cyclic_network(self):
        """Test case for network with cycles"""
        pipes = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 1, 4), (0, 3, 5)]
        self.assertEqual(min_cost_water_network(3, pipes), 6)

    def test_alternative_paths(self):
        """Test case for network with multiple possible paths"""
        pipes = [
            (0, 1, 10), (0, 2, 10), (1, 2, 1),
            (1, 3, 5), (2, 3, 2)
        ]
        self.assertEqual(min_cost_water_network(3, pipes), 13)

    def test_maximum_constraints(self):
        """Test case for maximum constraints"""
        # Create a large network with maximum allowed values
        n = 10**5
        pipes = [(0, 1, 10**5)] + [(i, i+1, 1) for i in range(1, n)]
        self.assertEqual(min_cost_water_network(n, pipes), 10**5 + n-1)

if __name__ == '__main__':
    unittest.main()