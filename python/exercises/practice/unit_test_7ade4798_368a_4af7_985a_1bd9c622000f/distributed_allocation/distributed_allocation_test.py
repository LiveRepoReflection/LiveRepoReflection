import unittest
from distributed_allocation import solve

class TestDistributedAllocation(unittest.TestCase):
    def validate_allocation(self, N, worker_capacities, task_resources, task_dependencies, allocation):
        # Check allocation length equals number of tasks
        total_tasks = len(task_resources)
        self.assertEqual(len(allocation), total_tasks)
        
        # Validate each task's allocation: if allocated, resource requirement must not exceed capacity (since tasks are serially executed in this model)
        for j, worker in enumerate(allocation):
            if worker != -1:
                self.assertGreaterEqual(worker, 0)
                self.assertLess(worker, N)
                # since resources are released after each task, we only check required resource does not exceed the worker's capacity.
                self.assertLessEqual(task_resources[j], worker_capacities[worker])
        
        # Validate dependency constraint: If a task is executed (i.e. allocated), all its dependencies must also be executed.
        for j, deps in enumerate(task_dependencies):
            if allocation[j] != -1:
                for dep in deps:
                    self.assertNotEqual(allocation[dep], -1, msg=f"Task {j} depends on task {dep} which was not allocated.")
    
    def test_basic_allocation(self):
        # Basic test with no dependencies and no dynamic tasks.
        N = 3
        M = 4
        worker_capacities = [10, 20, 30]
        task_resources = [5, 10, 15, 10]
        task_dependencies = [[], [], [], []]
        new_tasks = []
        
        allocation = solve(N, M, worker_capacities, task_resources, task_dependencies, new_tasks)
        # Expect output length equals M (as no new tasks provided)
        self.assertEqual(len(allocation), M)
        self.validate_allocation(N, worker_capacities, task_resources, task_dependencies, allocation)
        
    def test_allocation_with_dependencies(self):
        # Test where tasks have dependencies.
        N = 3
        M = 5
        worker_capacities = [50, 60, 70]
        # Task resources in such a way that they are not exceeding any worker's capacity.
        task_resources = [10, 20, 30, 40, 50]
        # Task dependencies: task 1 depends on 0; task 2 depends on 0 and 1; task 3 depends on 2; task 4 has no dependency.
        task_dependencies = [[], [0], [0, 1], [2], []]
        new_tasks = [(10, 25, [1, 3]), (20, 35, [4])]
        
        # Combined tasks count = initial M + len(new_tasks)
        allocation = solve(N, M, worker_capacities, task_resources, task_dependencies, new_tasks)
        self.assertEqual(len(allocation), M + len(new_tasks))
        
        # Create a combined task resources and dependencies list for validation.
        combined_task_resources = task_resources[:]
        combined_task_dependencies = [deps[:] for deps in task_dependencies]
        for arrival_time, res, deps in new_tasks:
            combined_task_resources.append(res)
            combined_task_dependencies.append(deps)
        
        self.validate_allocation(N, worker_capacities, combined_task_resources, combined_task_dependencies, allocation)
        
    def test_unassignable_tasks(self):
        # Test scenario where some tasks require more resource than any worker can provide.
        N = 2
        M = 3
        worker_capacities = [10, 15]
        task_resources = [5, 20, 10]  # task 1 requires 20 which is more than available
        task_dependencies = [[], [], [0]]
        new_tasks = [(5, 18, [])]  # also unsolvable: 18 > available capacities
        
        allocation = solve(N, M, worker_capacities, task_resources, task_dependencies, new_tasks)
        self.assertEqual(len(allocation), M + len(new_tasks))
        
        # In combined validation, tasks that require resource beyond all capacities must be assigned -1.
        combined_task_resources = task_resources[:]
        combined_task_dependencies = [deps[:] for deps in task_dependencies]
        for arrival_time, res, deps in new_tasks:
            combined_task_resources.append(res)
            combined_task_dependencies.append(deps)
        
        for idx, res in enumerate(combined_task_resources):
            if res > max(worker_capacities):
                self.assertEqual(allocation[idx], -1, msg=f"Task {idx} requiring {res} should not be allocated")
        
        # Also check dependency constraint: if a task is allocated but depends on a task that is unassigned,
        # then it must be flagged as error.
        for j, deps in enumerate(combined_task_dependencies):
            if allocation[j] != -1:
                for dep in deps:
                    self.assertNotEqual(allocation[dep], -1, msg=f"Task {j} depends on task {dep} which was not allocated")
        
if __name__ == '__main__':
    unittest.main()