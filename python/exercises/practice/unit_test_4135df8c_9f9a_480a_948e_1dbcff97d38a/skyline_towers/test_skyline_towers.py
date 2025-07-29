import unittest
from skyline_towers.skyline_towers import optimize_tower_placement

class TestSkylineTowers(unittest.TestCase):
    def test_small_grid_single_tower(self):
        city_blocks = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        cost = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ]
        result = optimize_tower_placement(city_blocks, cost, k=1, r=1, coverage_weight=0.5, cost_weight=0.5)
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], [(1,1)])

    def test_large_coverage_radius(self):
        city_blocks = [
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        cost = [
            [10, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ]
        result = optimize_tower_placement(city_blocks, cost, k=1, r=2, coverage_weight=0.9, cost_weight=0.1)
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], [(1,1), (0,1), (1,0)])

    def test_cost_optimization(self):
        city_blocks = [
            [1, 1],
            [1, 1]
        ]
        cost = [
            [100, 1],
            [1, 1]
        ]
        result = optimize_tower_placement(city_blocks, cost, k=1, r=1, coverage_weight=0.1, cost_weight=0.9)
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], [(0,1), (1,0), (1,1)])

    def test_multiple_towers(self):
        city_blocks = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]
        ]
        cost = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]
        ]
        result = optimize_tower_placement(city_blocks, cost, k=2, r=1, coverage_weight=0.5, cost_weight=0.5)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(0 <= x < 4 and 0 <= y < 4 for x, y in result))

    def test_edge_case_full_coverage(self):
        city_blocks = [
            [1, 1],
            [1, 1]
        ]
        cost = [
            [1, 1],
            [1, 1]
        ]
        result = optimize_tower_placement(city_blocks, cost, k=2, r=2, coverage_weight=1.0, cost_weight=0.0)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(set(result)), 2)

    def test_empty_grid(self):
        with self.assertRaises(ValueError):
            optimize_tower_placement([], [], k=1, r=1, coverage_weight=0.5, cost_weight=0.5)

    def test_invalid_weights(self):
        city_blocks = [[1]]
        cost = [[1]]
        with self.assertRaises(ValueError):
            optimize_tower_placement(city_blocks, cost, k=1, r=1, coverage_weight=0.5, cost_weight=0.6)

if __name__ == '__main__':
    unittest.main()