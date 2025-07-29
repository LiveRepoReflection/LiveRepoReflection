import unittest
from dynamic_route import RoutePlanner

class TestDynamicRoute(unittest.TestCase):
    def setUp(self):
        self.grid = [
            [0, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0]
        ]
        self.planner = RoutePlanner(self.grid)

    def test_initial_path(self):
        expected_path = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3)]
        result = self.planner.find_shortest_path(0, 0, 3, 3)
        self.assertEqual(len(result), len(expected_path))
        self.assertEqual(result[0], (0, 0))
        self.assertEqual(result[-1], (3, 3))

    def test_path_with_temporary_obstacle(self):
        self.planner.add_obstacle(2, 1)
        result = self.planner.find_shortest_path(0, 0, 3, 3)
        self.assertNotIn((2, 1), result)
        self.assertEqual(result[0], (0, 0))
        self.assertEqual(result[-1], (3, 3))

    def test_path_after_removing_obstacle(self):
        self.planner.add_obstacle(2, 1)
        self.planner.remove_obstacle(2, 1)
        result = self.planner.find_shortest_path(0, 0, 3, 3)
        self.assertEqual(result[0], (0, 0))
        self.assertEqual(result[-1], (3, 3))

    def test_no_path_when_blocked(self):
        self.planner.add_obstacle(0, 1)
        self.planner.add_obstacle(1, 0)
        result = self.planner.find_shortest_path(0, 0, 3, 3)
        self.assertEqual(result, [])

    def test_edge_case_start_on_obstacle(self):
        self.planner.add_obstacle(0, 0)
        result = self.planner.find_shortest_path(0, 0, 3, 3)
        self.assertEqual(result, [])

    def test_edge_case_end_on_obstacle(self):
        self.planner.add_obstacle(3, 3)
        result = self.planner.find_shortest_path(0, 0, 3, 3)
        self.assertEqual(result, [])

    def test_large_grid_performance(self):
        large_grid = [[0] * 100 for _ in range(100)]
        large_planner = RoutePlanner(large_grid)
        result = large_planner.find_shortest_path(0, 0, 99, 99)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()