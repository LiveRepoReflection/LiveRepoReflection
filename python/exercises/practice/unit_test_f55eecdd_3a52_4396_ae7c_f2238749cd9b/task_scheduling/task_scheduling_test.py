import unittest
from task_scheduling import schedule_tasks

class TaskSchedulingTest(unittest.TestCase):
    def test_no_dependencies_parallel(self):
        # Two tasks with no dependencies on 2 machines.
        N = 2
        K = 2
        tasks = [
            (0, 3, 5, []),
            (1, 2, 5, [])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 0)

    def test_single_machine_with_dependency(self):
        # Two tasks on a single machine with one dependency.
        N = 2
        K = 1
        tasks = [
            (0, 3, 3, []),
            (1, 2, 5, [0])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 0)

    def test_delayed_tasks_single_machine(self):
        # Two tasks on a single machine resulting in tardiness.
        # Task0 finishes at 5 with deadline 4 (tardiness 1),
        # Task1 finishes at 8 with deadline 7 (tardiness 1).
        N = 2
        K = 1
        tasks = [
            (0, 5, 4, []),
            (1, 3, 7, [0])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 2)

    def test_parallel_complex_dependencies(self):
        # Three tasks with tree dependencies on 2 machines.
        # Optimal scheduling results in zero overall tardiness.
        N = 3
        K = 2
        tasks = [
            (0, 2, 4, []),
            (1, 4, 10, [0]),
            (2, 3, 7, [0])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 0)

    def test_mid_complex_multiple_tasks(self):
        # Five tasks with mixed dependencies on 2 machines.
        # Optimal scheduling should yield zero overall tardiness.
        N = 5
        K = 2
        tasks = [
            (0, 4, 6, []),
            (1, 3, 10, [0]),
            (2, 2, 7, [0]),
            (3, 5, 15, [1, 2]),
            (4, 1, 8, [0])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 0)

    def test_high_tardiness(self):
        # Two tasks on a single machine with high processing time causing tardiness.
        # Task0 finishes at 10 with deadline 8 (tardiness 2),
        # Task1 finishes at 11 with deadline 15 (tardiness 0).
        N = 2
        K = 1
        tasks = [
            (0, 10, 8, []),
            (1, 1, 15, [0])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 2)

    def test_cycle_dependency(self):
        # Two tasks with cyclic dependencies.
        # This should be identified as an impossible schedule and return -1.
        N = 2
        K = 2
        tasks = [
            (0, 2, 10, [1]),
            (1, 3, 10, [0])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), -1)

    def test_all_parallel_no_dependency(self):
        # Four tasks with no dependencies on 4 machines.
        # Tasks run in parallel with individual tardiness computed from finishing times.
        # Task0: finishes at 5, deadline 3 (tardiness 2)
        # Task1: finishes at 4, deadline 4 (tardiness 0)
        # Task2: finishes at 2, deadline 3 (tardiness 0)
        # Task3: finishes at 3, deadline 2 (tardiness 1)
        # Overall tardiness = 2 + 0 + 0 + 1 = 3
        N = 4
        K = 4
        tasks = [
            (0, 5, 3, []),
            (1, 4, 4, []),
            (2, 2, 3, []),
            (3, 3, 2, [])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 3)

    def test_sequential_dependency_chain(self):
        # A chain of 4 tasks on a single machine with dependencies.
        # Optimal scheduling should yield zero overall tardiness.
        N = 4
        K = 1
        tasks = [
            (0, 2, 3, []),
            (1, 3, 6, [0]),
            (2, 1, 8, [1]),
            (3, 4, 12, [2])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 0)

    def test_sequential_dependency_chain_with_delay(self):
        # A chain of 4 tasks on a single machine where deadlines force tardiness.
        # Task0: finishes at 3 (deadline 2, tardiness 1)
        # Task1: finishes at 7 (deadline 5, tardiness 2)
        # Task2: finishes at 9 (deadline 8, tardiness 1)
        # Task3: finishes at 12 (deadline 10, tardiness 2)
        # Overall tardiness = 1 + 2 + 1 + 2 = 6
        N = 4
        K = 1
        tasks = [
            (0, 3, 2, []),
            (1, 4, 5, [0]),
            (2, 2, 8, [1]),
            (3, 3, 10, [2])
        ]
        self.assertEqual(schedule_tasks(N, K, tasks), 6)

if __name__ == '__main__':
    unittest.main()