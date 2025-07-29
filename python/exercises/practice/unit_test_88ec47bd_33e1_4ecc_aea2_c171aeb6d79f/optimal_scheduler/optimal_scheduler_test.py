import unittest
from optimal_scheduler import find_min_max_lateness

class TestOptimalScheduler(unittest.TestCase):
    def test_single_task_no_lateness(self):
        # Single task, one worker, should complete before deadline.
        n = 1
        tasks = [(3, 5)]
        expected = 0  # Completion time 3, deadline 5 -> lateness = 0
        self.assertEqual(find_min_max_lateness(n, tasks), expected)

    def test_single_task_with_lateness(self):
        # Single task, one worker, task has processing time exceeding deadline.
        n = 1
        tasks = [(4, 3)]
        expected = 1  # Completion time 4, deadline 3 -> lateness = 1
        self.assertEqual(find_min_max_lateness(n, tasks), expected)

    def test_multiple_tasks_two_workers_no_lateness(self):
        # Example case: schedule tasks optimally on two workers to have 0 maximum lateness.
        n = 2
        tasks = [(2, 5), (1, 3), (3, 8), (2, 4)]
        expected = 0
        self.assertEqual(find_min_max_lateness(n, tasks), expected)

    def test_multiple_tasks_two_workers_with_lateness(self):
        # Two tasks with deadlines that force lateness even with optimal scheduling.
        n = 2
        tasks = [(3, 2), (2, 2)]
        # No matter how they are scheduled, at least one task will finish after its deadline.
        expected = 1  # One task will be late by at least 1 unit.
        self.assertEqual(find_min_max_lateness(n, tasks), expected)

    def test_multiple_workers_complex_schedule(self):
        # Multiple tasks with varying processing times and deadlines on three workers.
        n = 3
        tasks = [(3, 3), (3, 8), (2, 6), (1, 5), (4, 10)]
        # An optimal assignment can achieve zero lateness.
        expected = 0
        self.assertEqual(find_min_max_lateness(n, tasks), expected)

    def test_complex_case_two_workers(self):
        # A more complex case on two workers with tasks challenging the scheduler.
        n = 2
        tasks = [(5, 7), (4, 5), (3, 12), (8, 8), (6, 15)]
        # Optimal scheduling leads to a maximum lateness of 4.
        expected = 4
        self.assertEqual(find_min_max_lateness(n, tasks), expected)

    def test_large_number_of_tasks(self):
        # Test with a larger set of tasks to check the algorithm performance and correctness.
        n = 5
        tasks = []
        # Generate 100 tasks with varying processing times and gradually increasing deadlines.
        for i in range(1, 101):
            t = (i % 5) + 1       # processing time between 1 and 5
            d = t + (i // 2)      # deadline increases gradually
            tasks.append((t, d))
        # We only check that the result is an integer and non-negative.
        result = find_min_max_lateness(n, tasks)
        self.assertTrue(isinstance(result, int))
        self.assertGreaterEqual(result, 0)

if __name__ == '__main__':
    unittest.main()