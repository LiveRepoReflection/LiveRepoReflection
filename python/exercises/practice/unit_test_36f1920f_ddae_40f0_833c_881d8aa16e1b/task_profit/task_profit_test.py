import unittest
import random
from task_profit import task_profit_function

class TaskProfitTest(unittest.TestCase):
    def test_empty_tasks(self):
        tasks = []
        expected = 0
        self.assertEqual(task_profit_function(tasks), expected)

    def test_single_task(self):
        tasks = [(1, 100)]
        expected = 100
        self.assertEqual(task_profit_function(tasks), expected)

    def test_multiple_tasks(self):
        # Given tasks: each tuple (deadline, profit)
        # Optimal schedule: schedule task with profit 50 at deadline 1 and task with profit 100 at deadline 2.
        tasks = [(2, 100), (1, 50), (2, 10)]
        expected = 150
        self.assertEqual(task_profit_function(tasks), expected)

    def test_same_deadline(self):
        # All tasks have the same deadline; only the task with the highest profit can be scheduled.
        tasks = [(1, 20), (1, 30), (1, 10)]
        expected = 30
        self.assertEqual(task_profit_function(tasks), expected)

    def test_zero_profit_task(self):
        # Tasks with zero profit should not affect the overall profit.
        tasks = [(1, 0), (2, 50), (2, 0)]
        expected = 50
        self.assertEqual(task_profit_function(tasks), expected)

    def test_complex_tasks(self):
        # A more complex scenario with tasks of varying deadlines and profits.
        tasks = [(4, 70), (2, 60), (4, 50), (3, 40), (1, 30)]
        # Expected schedule:
        #  - Schedule (4,70) in slot 4.
        #  - Schedule (2,60) in slot 2.
        #  - For (4,50), slot 4 is taken so assign it to slot 3 (meeting deadline 4).
        #  - For (3,40), slot 3 is taken; assign it to slot 1 (meeting deadline 3).
        #  - (1,30) cannot be scheduled as slot 1 is occupied.
        # Total profit = 70 + 60 + 50 + 40 = 220.
        expected = 220
        self.assertEqual(task_profit_function(tasks), expected)

    def test_large_input(self):
        # Generate a large random test case.
        n = 10000
        tasks = []
        for _ in range(n):
            deadline = random.randint(1, n)
            profit = random.randint(0, 1000)
            tasks.append((deadline, profit))
        result = task_profit_function(tasks)
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

if __name__ == '__main__':
    unittest.main()