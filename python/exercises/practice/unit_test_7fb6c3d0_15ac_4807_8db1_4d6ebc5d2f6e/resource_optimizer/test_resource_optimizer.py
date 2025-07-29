import unittest
from resource_optimizer import optimize_allocation

class TestResourceOptimizer(unittest.TestCase):
    def test_no_tasks(self):
        resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
        tasks = []
        task_durations = {}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertEqual(result, [])

    def test_single_task_fits(self):
        resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
        tasks = [(1, 10, {"CPU": 4, "Memory": 8, "Disk": 100})]
        task_durations = {1: 5}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertEqual(result, [1])

    def test_single_task_exceeds_resources(self):
        resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
        tasks = [(1, 10, {"CPU": 32, "Memory": 64, "Disk": 1000})]
        task_durations = {1: 5}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertEqual(result, [])

    def test_multiple_tasks_with_conflicts(self):
        resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
        tasks = [
            (1, 10, {"CPU": 8, "Memory": 16, "Disk": 200}),
            (2, 15, {"CPU": 8, "Memory": 16, "Disk": 200}),
            (3, 20, {"CPU": 8, "Memory": 16, "Disk": 200})
        ]
        task_durations = {1: 5, 2: 5, 3: 5}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertTrue(len(result) >= 1 and len(result) <= 2)

    def test_optimal_scheduling(self):
        resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
        tasks = [
            (1, 10, {"CPU": 4, "Memory": 8, "Disk": 100}),
            (2, 15, {"CPU": 2, "Memory": 4, "Disk": 50}),
            (3, 20, {"CPU": 8, "Memory": 16, "Disk": 200}),
            (4, 12, {"CPU": 1, "Memory": 2, "Disk": 25}),
            (5, 18, {"CPU": 4, "Memory": 8, "Disk": 100})
        ]
        task_durations = {1: 5, 2: 3, 3: 10, 4: 2, 5: 6}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertTrue(len(result) >= 3)

    def test_identical_deadlines(self):
        resource_capacities = {"CPU": 16, "Memory": 32, "Disk": 500}
        tasks = [
            (1, 10, {"CPU": 4, "Memory": 8, "Disk": 100}),
            (2, 10, {"CPU": 4, "Memory": 8, "Disk": 100}),
            (3, 10, {"CPU": 4, "Memory": 8, "Disk": 100})
        ]
        task_durations = {1: 5, 2: 5, 3: 5}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertTrue(len(result) >= 1 and len(result) <= 2)

    def test_large_number_of_tasks(self):
        resource_capacities = {"CPU": 32, "Memory": 64, "Disk": 1000}
        tasks = [(i, 100, {"CPU": 2, "Memory": 4, "Disk": 50}) for i in range(100)]
        task_durations = {i: 5 for i in range(100)}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertTrue(len(result) > 10)

    def test_mixed_resource_types(self):
        resource_capacities = {"CPU": 8, "GPU": 4, "FPGA": 2}
        tasks = [
            (1, 10, {"CPU": 2, "GPU": 1}),
            (2, 15, {"GPU": 2, "FPGA": 1}),
            (3, 20, {"CPU": 4, "FPGA": 1})
        ]
        task_durations = {1: 5, 2: 5, 3: 5}
        result = optimize_allocation(resource_capacities, tasks, task_durations)
        self.assertTrue(len(result) >= 2)

if __name__ == '__main__':
    unittest.main()