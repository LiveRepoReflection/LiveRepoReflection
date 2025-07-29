import unittest
from task_assign.task_assign import assign_tasks

class TestAssignTasks(unittest.TestCase):
    def test_single_assignment(self):
        current_time = 0
        tasks = [
            # (task_id, deadline, duration, cpu, memory, network)
            (1, 10, 5, 2, 1024, 100)
        ]
        workers = [
            # (worker_id, cpu_capacity, memory_capacity, network_capacity, cost_per_unit_time)
            (100, 4, 2048, 200, 1.0)
        ]
        expected = {1: 100}
        result = assign_tasks(current_time, tasks, workers)
        self.assertEqual(result, expected)

    def test_multiple_assignments_sequential(self):
        current_time = 0
        tasks = [
            (1, 20, 5, 2, 1024, 100),
            (2, 20, 5, 2, 1024, 100)
        ]
        workers = [
            (101, 4, 2048, 200, 2.0),
            (102, 2, 1024, 100, 1.0)
        ]
        # Optimal to schedule both tasks sequentially on worker 102 if deadlines are met.
        expected = {1: 102, 2: 102}
        result = assign_tasks(current_time, tasks, workers)
        self.assertEqual(result, expected)

    def test_infeasible_resource(self):
        current_time = 0
        tasks = [
            (1, 10, 5, 10, 1024, 100)  # Requires 10 CPU cores which exceed the available capacity.
        ]
        workers = [
            (100, 4, 2048, 200, 1.0)
        ]
        expected = {}
        result = assign_tasks(current_time, tasks, workers)
        self.assertEqual(result, expected)

    def test_infeasible_deadline(self):
        current_time = 0
        tasks = [
            (1, 5, 10, 2, 1024, 100)  # Duration makes it impossible to complete before deadline.
        ]
        workers = [
            (100, 4, 2048, 200, 1.0)
        ]
        expected = {}
        result = assign_tasks(current_time, tasks, workers)
        self.assertEqual(result, expected)

    def test_complex_assignment(self):
        current_time = 0
        tasks = [
            (1, 15, 5, 2, 1500, 200),
            (2, 15, 7, 2, 1500, 200),
            (3, 15, 4, 3, 3000, 300)
        ]
        workers = [
            (203, 2, 2000, 250, 1.0),  # Can only process tasks 1 and 2 due to resource limits.
            (202, 4, 4000, 500, 3.0),  # Can process all tasks.
            (201, 4, 4000, 500, 5.0)   # More expensive option.
        ]
        # Expected optimal assignment:
        # Tasks 1 and 2 scheduled sequentially on worker 203, and task 3 on worker 202.
        expected = {1: 203, 2: 203, 3: 202}
        result = assign_tasks(current_time, tasks, workers)
        self.assertEqual(result, expected)

    def test_sequential_scheduling_constraints(self):
        # This test verifies that tasks can be scheduled sequentially on the same worker when deadlines allow.
        current_time = 0
        tasks = [
            (1, 10, 5, 2, 1024, 100),  # Can finish by time 5.
            (2, 12, 5, 2, 1024, 100)   # Must start after the first ends at 5 and finish by 10, which is within deadline.
        ]
        workers = [
            (100, 4, 2048, 200, 1.0)
        ]
        expected = {1: 100, 2: 100}
        result = assign_tasks(current_time, tasks, workers)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()