import unittest
from max_profit_schedule import solve_max_profit_scheduling

class MaxProfitScheduleTest(unittest.TestCase):
    def test_empty_tasks(self):
        tasks = []
        self.assertEqual(solve_max_profit_scheduling(tasks), 0)

    def test_single_task(self):
        tasks = [(1, 2, 50)]
        self.assertEqual(solve_max_profit_scheduling(tasks), 50)

    def test_non_overlapping_tasks(self):
        tasks = [(1, 2, 50), (2, 3, 60)]
        self.assertEqual(solve_max_profit_scheduling(tasks), 110)

    def test_overlapping_tasks(self):
        tasks = [(1, 3, 50), (2, 5, 70), (4, 6, 60)]
        # Optimal schedule: choose (1,3,50) and (4,6,60) for a total profit of 110.
        self.assertEqual(solve_max_profit_scheduling(tasks), 110)

    def test_complex_case(self):
        tasks = [(1, 2, 50), (3, 5, 20), (6, 19, 100), (2, 100, 200)]
        # One optimal schedule is (1,2,50) and (2,100,200) with total profit 250.
        self.assertEqual(solve_max_profit_scheduling(tasks), 250)

    def test_invalid_task_ignored(self):
        # A task with start_time > end_time is considered invalid and should be ignored.
        tasks = [(1, 3, 50), (5, 4, 100), (3, 5, 60)]
        # Only valid tasks: (1,3,50) and (3,5,60) which are non-overlapping, total profit 110.
        self.assertEqual(solve_max_profit_scheduling(tasks), 110)

    def test_zero_length_task(self):
        # Tasks with zero duration (start_time == end_time) are valid.
        tasks = [(3, 3, 10), (3, 4, 20)]
        # Both tasks can be scheduled as they do not overlap, total profit should be 30.
        self.assertEqual(solve_max_profit_scheduling(tasks), 30)

    def test_overlapping_on_boundary(self):
        tasks = [(1, 3, 10), (3, 5, 20), (5, 7, 30), (2, 6, 25)]
        # Most profitable selection is (1,3,10), (3,5,20), and (5,7,30) = 60.
        self.assertEqual(solve_max_profit_scheduling(tasks), 60)

    def test_large_input(self):
        # Create a large number of non-overlapping tasks to test performance.
        tasks = [(i, i + 1, 1) for i in range(10000)]
        # Total profit should be the sum of all tasks: 10000.
        self.assertEqual(solve_max_profit_scheduling(tasks), 10000)

if __name__ == "__main__":
    unittest.main()