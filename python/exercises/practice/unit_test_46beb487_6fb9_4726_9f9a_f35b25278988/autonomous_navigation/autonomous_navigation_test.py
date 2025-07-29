import unittest
from autonomous_navigation import find_optimal_path

class TestAutonomousNavigation(unittest.TestCase):
    def test_basic_path(self):
        # A basic scenario with a clear path
        grid_snapshots = [
            (
                [
                    ["E", "E", "E", "E"],
                    ["O", "O", "E", "E"],
                    ["S", "E", "D", "E"],
                    ["E", "E", "E", "C"],
                ],
                20,
                50,
            )
        ]
        battery_capacity = 50
        move_cost = 5
        
        # Expected: path from S to D (positions are (row, col))
        result = find_optimal_path(grid_snapshots, battery_capacity, move_cost)
        # Basic assertions: non-empty, starting at S and ending at D.
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0], (2, 0))  # S is at (2, 0)
        self.assertEqual(result[-1], (2, 2))  # D is at (2, 2)
    
    def test_no_possible_path_due_to_obstacles(self):
        # A grid where obstacles block any possible path.
        grid_snapshots = [
            (
                [
                    ["S", "O", "D"],
                    ["O", "O", "O"],
                    ["E", "E", "C"],
                ],
                10,
                20,
            )
        ]
        battery_capacity = 20
        move_cost = 2
        
        result = find_optimal_path(grid_snapshots, battery_capacity, move_cost)
        self.assertEqual(result, [])

    def test_insufficient_moves(self):
        # The remaining moves is too low to allow any valid delivery
        grid_snapshots = [
            (
                [
                    ["S", "E", "E"],
                    ["E", "E", "E"],
                    ["E", "E", "D"],
                ],
                2,
                20,
            )
        ]
        battery_capacity = 20
        move_cost = 1
        
        result = find_optimal_path(grid_snapshots, battery_capacity, move_cost)
        self.assertEqual(result, [])
    
    def test_battery_limitation_with_charging(self):
        # A scenario where the robot has to use the charging station to succeed.
        grid_snapshots = [
            (
                [
                    ["S", "E", "E", "C"],
                    ["O", "O", "E", "O"],
                    ["E", "E", "E", "D"],
                    ["E", "O", "E", "E"],
                ],
                25,
                15,  # starting battery level is low
            )
        ]
        battery_capacity = 20
        move_cost = 5
        
        result = find_optimal_path(grid_snapshots, battery_capacity, move_cost)
        # Check that result is not empty and starts and ends with correct coordinates
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0], (0, 0))
        self.assertEqual(result[-1], (2, 3))
    
    def test_dynamic_snapshot_change(self):
        # Multiple snapshots mimicking changes in the warehouse.
        # In the first snapshot obstacles block the direct path,
        # but in the second snapshot some obstacles are removed.
        grid_snapshot1 = (
            [
                ["S", "O", "E", "D"],
                ["E", "O", "E", "E"],
                ["E", "E", "O", "C"],
                ["E", "E", "E", "E"],
            ],
            15,
            30,
        )
        
        grid_snapshot2 = (
            [
                ["S", "E", "E", "D"],
                ["E", "O", "E", "E"],
                ["E", "E", "E", "C"],
                ["E", "E", "E", "E"],
            ],
            15,
            30,
        )
        
        grid_snapshots = [grid_snapshot1, grid_snapshot2]
        battery_capacity = 30
        move_cost = 3
        
        result = find_optimal_path(grid_snapshots, battery_capacity, move_cost)
        # Check that the result starts at S and ends at D, and a path exists.
        self.assertIsInstance(result, list)
        if result:
            self.assertEqual(result[0], (0, 0))
            self.assertEqual(result[-1], (0, 3))
        else:
            self.fail("Expected a valid path but got an empty path.")
    
    def test_exact_deadline_usage(self):
        # Test scenario where the solution exactly uses the remaining moves available.
        grid_snapshots = [
            (
                [
                    ["S", "E", "D"],
                    ["E", "O", "E"],
                    ["E", "E", "C"],
                ],
                4,  # remaining moves are just enough
                20,
            )
        ]
        battery_capacity = 20
        move_cost = 1
        
        result = find_optimal_path(grid_snapshots, battery_capacity, move_cost)
        # Check for starting and ending coordinates
        if result:
            self.assertEqual(result[0], (0, 0))
            self.assertEqual(result[-1], (0, 2))
            self.assertLessEqual(len(result) - 1, 4)
        else:
            self.fail("Expected a valid path using exactly the available moves.")

if __name__ == '__main__':
    unittest.main()