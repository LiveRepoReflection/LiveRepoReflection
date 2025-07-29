import unittest
from task_schedule import schedule_tasks


class TaskScheduleTest(unittest.TestCase):
    def test_simple_schedule(self):
        """Test a simple case with a few tasks and no dependencies."""
        n = 3
        deadline = [10, 5, 8]
        duration = [2, 1, 3]
        dependencies = [[], [], []]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_with_dependencies(self):
        """Test with dependencies between tasks."""
        n = 4
        deadline = [10, 8, 12, 15]
        duration = [2, 3, 2, 4]
        dependencies = [[], [0], [1], [0, 2]]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_impossible_schedule(self):
        """Test a case where it's impossible to meet all deadlines."""
        n = 3
        deadline = [3, 4, 5]
        duration = [2, 2, 2]
        dependencies = [[1], [2], [0]]  # Circular dependency
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.assertEqual(result, [], "Should return empty list for impossible schedule")

    def test_tight_deadlines(self):
        """Test with very tight deadlines."""
        n = 3
        deadline = [3, 3, 3]
        duration = [1, 1, 1]
        dependencies = [[], [], []]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_large_input(self):
        """Test with a larger number of tasks."""
        n = 100
        deadline = [i + 50 for i in range(n)]
        duration = [1] * n
        dependencies = [[] for _ in range(n)]
        
        # Add some dependencies
        for i in range(1, n):
            if i % 10 == 0:
                dependencies[i] = [i-1]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_complex_dependencies(self):
        """Test with complex dependency graph."""
        n = 6
        deadline = [10, 10, 10, 10, 10, 10]
        duration = [1, 1, 1, 1, 1, 1]
        dependencies = [[], [0], [0], [1, 2], [1, 2], [3, 4]]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_all_tasks_dependent(self):
        """Test where all tasks depend on previous ones."""
        n = 5
        deadline = [5, 10, 15, 20, 25]
        duration = [1, 2, 3, 4, 5]
        dependencies = [[], [0], [1], [2], [3]]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_deadline_exceeded(self):
        """Test case where a deadline is exceeded."""
        n = 2
        deadline = [1, 2]
        duration = [2, 1]  # First task's duration exceeds its deadline
        dependencies = [[], []]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.assertEqual(result, [], "Should return empty list when deadline is exceeded")

    def test_impossible_due_to_dependencies(self):
        """Test where dependencies make it impossible to meet deadlines."""
        n = 3
        deadline = [5, 5, 5]
        duration = [2, 2, 2]
        dependencies = [[1], [2], []]  # Task 0 depends on 1, which depends on 2
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def test_edge_case_single_task(self):
        """Test with just one task."""
        n = 1
        deadline = [5]
        duration = [3]
        dependencies = [[]]
        
        result = schedule_tasks(n, deadline, duration, dependencies)
        self.validate_schedule(result, n, deadline, duration, dependencies)

    def validate_schedule(self, schedule, n, deadline, duration, dependencies):
        """Validate that the schedule meets all requirements."""
        if schedule == []:
            # If an empty schedule is returned, we can't validate further
            return
        
        # Check that all tasks are scheduled
        self.assertEqual(len(schedule), n, "Not all tasks are scheduled")
        self.assertEqual(set(schedule), set(range(n)), "Some tasks missing or duplicated")
        
        # Check dependencies and deadlines
        completion_time = {}
        current_time = 0
        
        for task_id in schedule:
            # Ensure all dependencies are satisfied
            for dep in dependencies[task_id]:
                self.assertIn(dep, completion_time, f"Dependency {dep} not completed before task {task_id}")
            
            # Execute the task
            start_time = current_time
            current_time += duration[task_id]
            completion_time[task_id] = current_time
            
            # Check deadline
            self.assertLessEqual(current_time, deadline[task_id], 
                               f"Task {task_id} exceeds deadline {deadline[task_id]}")


if __name__ == "__main__":
    unittest.main()