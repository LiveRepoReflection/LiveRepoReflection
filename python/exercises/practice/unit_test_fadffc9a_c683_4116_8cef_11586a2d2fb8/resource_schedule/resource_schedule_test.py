import unittest
from resource_schedule import find_optimal_schedule

class ResourceScheduleTest(unittest.TestCase):
    def test_simple_case(self):
        n = 4
        resources = 10
        task_resources = [3, 6, 4, 2]
        task_deadlines = [4, 6, 5, 7]
        dependencies = [[], [0, 2], [0], []]
        
        schedule = find_optimal_schedule(n, resources, task_resources, task_deadlines, dependencies)
        self.validate_schedule(schedule, n, resources, task_resources, task_deadlines, dependencies)
        self.assertEqual(len(schedule), 4)  # All tasks should be scheduled

    def test_impossible_deadline(self):
        n = 3
        resources = 5
        task_resources = [3, 2, 2]
        task_deadlines = [1, 2, 1]
        dependencies = [[], [0], [0]]
        
        schedule = find_optimal_schedule(n, resources, task_resources, task_deadlines, dependencies)
        self.validate_schedule(schedule, n, resources, task_resources, task_deadlines, dependencies)
        self.assertLess(len(schedule), 3)  # Not all tasks can be scheduled

    def test_resource_constraint(self):
        n = 3
        resources = 4
        task_resources = [3, 2, 4]
        task_deadlines = [5, 5, 5]
        dependencies = [[], [], []]
        
        schedule = find_optimal_schedule(n, resources, task_resources, task_deadlines, dependencies)
        self.validate_schedule(schedule, n, resources, task_resources, task_deadlines, dependencies)

    def test_complex_dependencies(self):
        n = 5
        resources = 10
        task_resources = [2, 3, 4, 3, 2]
        task_deadlines = [5, 6, 7, 7, 8]
        dependencies = [[], [0], [1], [1, 2], [3]]
        
        schedule = find_optimal_schedule(n, resources, task_resources, task_deadlines, dependencies)
        self.validate_schedule(schedule, n, resources, task_resources, task_deadlines, dependencies)

    def test_tight_deadlines(self):
        n = 4
        resources = 8
        task_resources = [2, 3, 4, 5]
        task_deadlines = [2, 3, 3, 4]
        dependencies = [[], [], [], []]
        
        schedule = find_optimal_schedule(n, resources, task_resources, task_deadlines, dependencies)
        self.validate_schedule(schedule, n, resources, task_resources, task_deadlines, dependencies)

    def test_maximum_constraints(self):
        n = 10
        resources = 1000
        task_resources = [100] * 10
        task_deadlines = list(range(1, 11))
        dependencies = [[] for _ in range(10)]
        
        schedule = find_optimal_schedule(n, resources, task_resources, task_deadlines, dependencies)
        self.validate_schedule(schedule, n, resources, task_resources, task_deadlines, dependencies)

    def validate_schedule(self, schedule, n, resources, task_resources, task_deadlines, dependencies):
        if not schedule:
            return  # Empty schedule is valid when no solution exists
        
        # Check schedule format
        for start_time, task_idx in schedule:
            self.assertIsInstance(start_time, int)
            self.assertIsInstance(task_idx, int)
            self.assertGreaterEqual(task_idx, 0)
            self.assertLess(task_idx, n)

        # Create timeline of resource usage
        timeline = {}
        completed_tasks = set()
        
        for start_time, task_idx in schedule:
            # Check deadline constraint
            self.assertLess(start_time + 1, task_deadlines[task_idx])
            
            # Check dependency constraint
            for dep in dependencies[task_idx]:
                found = False
                for other_start, other_task in schedule:
                    if other_task == dep and other_start + 1 <= start_time:
                        found = True
                        break
                self.assertTrue(found, f"Dependency {dep} not met for task {task_idx}")
            
            # Check resource constraint
            for t in range(start_time, start_time + 1):
                timeline[t] = timeline.get(t, 0) + task_resources[task_idx]
                self.assertLessEqual(timeline[t], resources)
            
            completed_tasks.add(task_idx)
        
        # Check for task uniqueness
        self.assertEqual(len(completed_tasks), len(schedule))

if __name__ == '__main__':
    unittest.main()