import unittest
import time
import random

from task_orchestrator import orchestrate_tasks

class TestTaskOrchestrator(unittest.TestCase):

    def test_no_dependencies_success(self):
        # Scenario 1: Tasks with no dependencies, all tasks should complete successfully.
        tasks = [
            {"id": "task1", "execution_time": 1, "dependencies": [], "resources_required": 2},
            {"id": "task2", "execution_time": 1, "dependencies": [], "resources_required": 2},
            {"id": "task3", "execution_time": 1, "dependencies": [], "resources_required": 2}
        ]
        num_workers = 3
        total_resources = 10
        failure_rate = 0.0  # No failures expected.

        result = orchestrate_tasks(tasks, num_workers, total_resources, failure_rate)

        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertIn("completion_time", result)
        self.assertGreater(result["completion_time"], 0)
        self.assertIn("task_states", result)
        for task in tasks:
            self.assertIn(task["id"], result["task_states"])
            self.assertEqual(result["task_states"][task["id"]], "completed")

    def test_linear_dependencies_success(self):
        # Scenario 2: A linear chain of dependencies: task1 -> task2 -> task3.
        tasks = [
            {"id": "task1", "execution_time": 1, "dependencies": [], "resources_required": 3},
            {"id": "task2", "execution_time": 1, "dependencies": ["task1"], "resources_required": 2},
            {"id": "task3", "execution_time": 1, "dependencies": ["task2"], "resources_required": 1}
        ]
        num_workers = 2
        total_resources = 10
        failure_rate = 0.0  # All tasks will run successfully.

        result = orchestrate_tasks(tasks, num_workers, total_resources, failure_rate)

        self.assertEqual(result["status"], "success")
        self.assertGreater(result["completion_time"], 0)
        task_states = result["task_states"]
        for task in tasks:
            self.assertIn(task["id"], task_states)
            self.assertEqual(task_states[task["id"]], "completed")

    def test_dependency_failure(self):
        # Scenario 3: Introduce a failure into a task with dependents. 
        # Use a failure_rate of 1.0 for deterministic failure for one of the tasks.
        # Expect that tasks depending on the failed task are cancelled.
        tasks = [
            {"id": "task1", "execution_time": 1, "dependencies": [], "resources_required": 2},
            {"id": "task2", "execution_time": 1, "dependencies": ["task1"], "resources_required": 2},
            {"id": "task3", "execution_time": 1, "dependencies": ["task2"], "resources_required": 2},
            {"id": "task4", "execution_time": 1, "dependencies": ["task1"], "resources_required": 1}
        ]
        num_workers = 2
        total_resources = 10
        # Use a failure_rate high enough to ensure one failure in the tasks with dependency.
        failure_rate = 1.0

        result = orchestrate_tasks(tasks, num_workers, total_resources, failure_rate)

        self.assertEqual(result["status"], "failure")
        self.assertGreater(result["completion_time"], 0)
        task_states = result["task_states"]
        # Since failure_rate is 1.0, the tasks with no dependencies should fail.
        # Dependent tasks should be cancelled.
        # Check for at least one failure and its effect on dependents.
        failed_found = any(state == "failed" for state in task_states.values())
        cancelled_found = any(state == "cancelled" for state in task_states.values())
        self.assertTrue(failed_found)
        self.assertTrue(cancelled_found)

    def test_complex_dag_with_resource_constraints(self):
        # Scenario 4: Complex dependency graph (DAG) with branching and resource constraints.
        tasks = [
            {"id": "A", "execution_time": 1, "dependencies": [], "resources_required": 3},
            {"id": "B", "execution_time": 2, "dependencies": ["A"], "resources_required": 4},
            {"id": "C", "execution_time": 1, "dependencies": ["A"], "resources_required": 2},
            {"id": "D", "execution_time": 2, "dependencies": ["B", "C"], "resources_required": 3},
            {"id": "E", "execution_time": 1, "dependencies": ["C"], "resources_required": 1},
            {"id": "F", "execution_time": 1, "dependencies": ["D", "E"], "resources_required": 2},
            {"id": "G", "execution_time": 1, "dependencies": ["F"], "resources_required": 1}
        ]
        num_workers = 3
        total_resources = 8
        failure_rate = 0.0  # Force all tasks to complete successfully.

        result = orchestrate_tasks(tasks, num_workers, total_resources, failure_rate)

        self.assertEqual(result["status"], "success")
        self.assertGreater(result["completion_time"], 0)
        task_states = result["task_states"]
        for task in tasks:
            self.assertIn(task["id"], task_states)
            self.assertEqual(task_states[task["id"]], "completed")

if __name__ == '__main__':
    unittest.main()