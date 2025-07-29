import unittest
from task_penalty import task_penalty

class TaskPenaltyTest(unittest.TestCase):
    def test_empty_tasks(self):
        tasks = []
        # No tasks means no penalty.
        self.assertEqual(task_penalty(tasks), 0)

    def test_single_task_on_time(self):
        tasks = [
            (1, 5, 10, 20, [])
        ]
        # Task finishes at time 5, within deadline 10.
        self.assertEqual(task_penalty(tasks), 0)

    def test_single_task_late(self):
        tasks = [
            (1, 5, 4, 20, [])
        ]
        # Task finishes at time 5, past deadline 4; penalty = 20.
        self.assertEqual(task_penalty(tasks), 20)

    def test_two_tasks_on_time(self):
        tasks = [
            (1, 3, 5, 10, []),
            (2, 4, 9, 15, [1])
        ]
        # Schedule: task1 finishes at 3, task2 finishes at 7.
        # Both within their deadlines, so penalty = 0.
        self.assertEqual(task_penalty(tasks), 0)

    def test_two_tasks_late(self):
        tasks = [
            (1, 5, 4, 20, []),
            (2, 4, 8, 15, [1])
        ]
        # Schedule: task1 finishes at 5 -> exceeds deadline 4 (penalty 20)
        #           task2 finishes at 9 -> exceeds deadline 8 (penalty 15)
        # Total penalty = 20 + 15 = 35.
        self.assertEqual(task_penalty(tasks), 35)

    def test_complex_tasks_no_penalty(self):
        tasks = [
            (1, 5, 10, 20, []),
            (2, 3, 15, 10, [1]),
            (3, 2, 12, 30, [1]),
            (4, 4, 20, 5, [2, 3])
        ]
        # One valid schedule is: 1 -> 3 -> 2 -> 4 which finishes all tasks before their deadlines.
        self.assertEqual(task_penalty(tasks), 0)

    def test_complex_tasks_with_penalty(self):
        tasks = [
            (1, 4, 3, 50, []),
            (2, 2, 10, 10, [1]),
            (3, 3, 9, 20, [1]),
            (4, 5, 20, 5, [2, 3]),
            (5, 1, 25, 15, [4])
        ]
        # Task 1 must be executed first and will finish at time 4 (past its deadline 3: penalty 50).
        # The other tasks can be arranged to finish on time.
        # Expected total penalty = 50.
        self.assertEqual(task_penalty(tasks), 50)

    def test_unordered_input(self):
        tasks = [
            (3, 2, 12, 30, [1]),
            (1, 5, 10, 20, []),
            (4, 4, 20, 5, [2, 3]),
            (2, 3, 15, 10, [1])
        ]
        # The tasks are provided in an unsorted order.
        # With correct dependency processing, the optimal schedule should complete tasks on time.
        self.assertEqual(task_penalty(tasks), 0)

if __name__ == '__main__':
    unittest.main()