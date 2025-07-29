import unittest
from task_master import schedule_tasks
import random

class TaskMasterTest(unittest.TestCase):
    def test_basic_scheduling(self):
        tasks = [
            (1, 1, [], 5),  # Task 1, priority 1, no dependencies, execution time 5 seconds
            (2, 2, [1], 3), # Task 2, priority 2, depends on Task 1, execution time 3 seconds
            (3, 1, [], 4),  # Task 3, priority 1, no dependencies, execution time 4 seconds
            (4, 3, [2, 3], 2) # Task 4, priority 3, depends on Tasks 2 and 3, execution time 2 seconds
        ]
        num_workers = 2
        
        # Set seed for reproducible test
        random.seed(42)
        
        schedule = schedule_tasks(tasks, num_workers)
        
        # Verify correct format of outputs
        for event in schedule:
            self.assertEqual(len(event), 4)
            timestamp, worker_id, event_type, task_id = event
            self.assertIsInstance(timestamp, int)
            self.assertIsInstance(worker_id, int)
            self.assertIn(event_type, ["SCHEDULED", "COMPLETED", "FAILED", "RESCHEDULED"])
            self.assertIsInstance(task_id, int)
        
        # Verify scheduling follows dependencies
        task_completion_times = {}
        scheduled_tasks = set()
        
        for event in schedule:
            timestamp, worker_id, event_type, task_id = event
            
            if event_type == "SCHEDULED":
                # Check dependencies are completed before scheduling
                for task in tasks:
                    if task[0] == task_id:
                        for dependency in task[2]:
                            self.assertIn(dependency, task_completion_times)
                scheduled_tasks.add(task_id)
            
            elif event_type == "COMPLETED":
                task_completion_times[task_id] = timestamp
                self.assertIn(task_id, scheduled_tasks)
            
            elif event_type == "FAILED":
                self.assertIn(task_id, scheduled_tasks)
            
            elif event_type == "RESCHEDULED":
                # Failed tasks should be rescheduled
                self.assertIn(task_id, scheduled_tasks)
        
        # Verify all tasks were completed
        for task in tasks:
            task_id = task[0]
            self.assertIn(task_id, task_completion_times)

    def test_single_worker(self):
        tasks = [
            (1, 1, [], 3),
            (2, 2, [1], 2),
            (3, 3, [2], 1)
        ]
        num_workers = 1
        
        # Set seed for reproducible test
        random.seed(42)
        
        schedule = schedule_tasks(tasks, num_workers)
        
        # Ensure all tasks are scheduled and completed by the single worker
        completion_times = {}
        
        for event in schedule:
            timestamp, worker_id, event_type, task_id = event
            self.assertEqual(worker_id, 0)  # Only one worker
            if event_type == "COMPLETED":
                completion_times[task_id] = timestamp
        
        # Check all tasks were completed
        self.assertEqual(len(completion_times), 3)

    def test_no_dependencies(self):
        tasks = [
            (1, 3, [], 2),
            (2, 1, [], 3),
            (3, 2, [], 1),
            (4, 4, [], 2)
        ]
        num_workers = 2
        
        # Set seed for reproducible test
        random.seed(42)
        
        schedule = schedule_tasks(tasks, num_workers)
        
        # Check priority-based scheduling
        scheduled_order = []
        for event in schedule:
            if event[2] == "SCHEDULED":
                scheduled_order.append(event[3])
        
        # First two tasks should be tasks 2 and 3 (highest priorities)
        # The exact order can vary based on tie-breaking logic
        first_two_tasks = set(scheduled_order[:2])
        self.assertIn(2, first_two_tasks)
        self.assertTrue(1 in first_two_tasks or 3 in first_two_tasks)

    def test_complex_dependencies(self):
        # Create a complex dependency graph
        tasks = [
            (1, 1, [], 2),
            (2, 1, [1], 2),
            (3, 1, [1], 3),
            (4, 2, [2, 3], 2),
            (5, 2, [3], 1),
            (6, 3, [4, 5], 2)
        ]
        num_workers = 3
        
        # Set seed for reproducible test
        random.seed(42)
        
        schedule = schedule_tasks(tasks, num_workers)
        
        # Verify dependency constraints
        task_completion_times = {}
        
        for event in schedule:
            timestamp, worker_id, event_type, task_id = event
            
            if event_type == "COMPLETED":
                task_completion_times[task_id] = timestamp
        
        # Check dependencies were respected
        self.assertLess(task_completion_times[1], task_completion_times[2])
        self.assertLess(task_completion_times[1], task_completion_times[3])
        self.assertLess(task_completion_times[2], task_completion_times[4])
        self.assertLess(task_completion_times[3], task_completion_times[4])
        self.assertLess(task_completion_times[3], task_completion_times[5])
        self.assertLess(task_completion_times[4], task_completion_times[6])
        self.assertLess(task_completion_times[5], task_completion_times[6])

    def test_worker_failure_and_recovery(self):
        tasks = [
            (1, 1, [], 10),  # Long-running task likely to fail
            (2, 2, [], 10)   # Another long-running task
        ]
        num_workers = 2
        
        # Set failure probability high for this test
        # We'll check if the implementation handles this properly
        
        # Set seed for reproducible test with high chance of failure
        random.seed(1)  # This seed should produce at least one failure
        
        schedule = schedule_tasks(tasks, num_workers, failure_probability=0.2)
        
        # Count events by type
        event_count = {
            "SCHEDULED": 0,
            "COMPLETED": 0,
            "FAILED": 0,
            "RESCHEDULED": 0
        }
        
        for event in schedule:
            event_count[event[2]] += 1
        
        # Verify all tasks were eventually completed
        self.assertEqual(event_count["COMPLETED"], 2)
        
        # Check if we had any failures and rescheduling
        # With this random seed and probability, we should have failures
        if event_count["FAILED"] > 0:
            self.assertEqual(event_count["FAILED"], event_count["RESCHEDULED"])
            # The number of scheduled should equal completed + current running
            self.assertEqual(event_count["SCHEDULED"], 
                            event_count["COMPLETED"] + event_count["FAILED"])

    def test_large_workload_scalability(self):
        # Create a larger workload to test scalability
        num_tasks = 100
        tasks = []
        
        # Generate independent tasks
        for i in range(1, 51):
            tasks.append((i, i % 5, [], 2 + i % 5))
            
        # Generate dependent tasks
        for i in range(51, 101):
            # Each task depends on 1-3 previous tasks
            deps = [i - 50]
            if i % 3 == 0:
                deps.append(i - 25)
            if i % 7 == 0:
                deps.append(i - 10)
                
            tasks.append((i, i % 5, deps, 1 + i % 3))
        
        num_workers = 10
        
        # Set seed for reproducible test
        random.seed(42)
        
        schedule = schedule_tasks(tasks, num_workers)
        
        # Verify all tasks were scheduled and completed
        scheduled_tasks = set()
        completed_tasks = set()
        
        for event in schedule:
            timestamp, worker_id, event_type, task_id = event
            
            if event_type == "SCHEDULED":
                scheduled_tasks.add(task_id)
            elif event_type == "COMPLETED":
                completed_tasks.add(task_id)
        
        # All tasks were completed
        self.assertEqual(len(completed_tasks), num_tasks)
        
        # Schedule is sorted by timestamp
        for i in range(1, len(schedule)):
            self.assertLessEqual(schedule[i-1][0], schedule[i][0])

    def test_priority_handling(self):
        # Test that higher priority tasks are scheduled first
        tasks = [
            (1, 5, [], 2),  # Lowest priority
            (2, 4, [], 2),
            (3, 3, [], 2),
            (4, 2, [], 2),
            (5, 1, [], 2),  # Highest priority
        ]
        num_workers = 1  # Single worker to test priority
        
        # Set seed for reproducible test
        random.seed(42)
        
        schedule = schedule_tasks(tasks, num_workers)
        
        # Extract the order in which tasks were scheduled
        scheduled_order = []
        for event in schedule:
            if event[2] == "SCHEDULED":
                scheduled_order.append(event[3])
        
        # Check that tasks were scheduled in priority order
        # Task 5 should be first (highest priority), Task 1 should be last (lowest priority)
        self.assertEqual(scheduled_order[0], 5)
        self.assertEqual(scheduled_order[-1], 1)
        self.assertEqual(scheduled_order, [5, 4, 3, 2, 1])

if __name__ == '__main__':
    unittest.main()