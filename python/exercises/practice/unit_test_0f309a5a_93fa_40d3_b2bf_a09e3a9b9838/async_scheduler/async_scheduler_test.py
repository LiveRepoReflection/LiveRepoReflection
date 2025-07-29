import asyncio
import unittest
from async_scheduler.async_scheduler import run_scheduler, CycleError

class TestAsyncScheduler(unittest.IsolatedAsyncioTestCase):
    async def test_simple_execution(self):
        tasks = {
            "task1": {"function": "fetch_data", "dependencies": [], "priority": 1},
            "task2": {"function": "clean_data", "dependencies": ["task1"], "priority": 2},
            "task3": {"function": "analyze_data", "dependencies": ["task2"], "priority": 3}
        }
        num_workers = 2
        max_concurrency_per_worker = 1
        execution_times = {
            "fetch_data": 1,
            "clean_data": 1,
            "analyze_data": 1
        }
        task_failures = {}

        result = await run_scheduler(tasks, num_workers, max_concurrency_per_worker, execution_times, task_failures)
        expected = {
            "task1": "success",
            "task2": "success",
            "task3": "success"
        }
        self.assertEqual(result, expected)

    async def test_dependency_failure(self):
        tasks = {
            "task1": {"function": "fetch_data", "dependencies": [], "priority": 1},
            "task2": {"function": "clean_data", "dependencies": ["task1"], "priority": 2},
            "task3": {"function": "analyze_data", "dependencies": ["task2"], "priority": 3},
            "task4": {"function": "generate_report", "dependencies": ["task3"], "priority": 4}
        }
        num_workers = 2
        max_concurrency_per_worker = 1
        execution_times = {
            "fetch_data": 1,
            "clean_data": 1,
            "analyze_data": 1,
            "generate_report": 1
        }
        task_failures = {"task2": True}  # Simulate task2 failure

        result = await run_scheduler(tasks, num_workers, max_concurrency_per_worker, execution_times, task_failures)
        expected = {
            "task1": "success",
            "task2": "failed",
            "task3": "skipped",
            "task4": "skipped"
        }
        self.assertEqual(result, expected)

    async def test_independent_tasks(self):
        tasks = {
            "task1": {"function": "task_a", "dependencies": [], "priority": 1},
            "task2": {"function": "task_b", "dependencies": [], "priority": 2},
            "task3": {"function": "task_c", "dependencies": [], "priority": 3}
        }
        num_workers = 2
        max_concurrency_per_worker = 2
        execution_times = {
            "task_a": 1,
            "task_b": 1,
            "task_c": 1
        }
        task_failures = {}

        result = await run_scheduler(tasks, num_workers, max_concurrency_per_worker, execution_times, task_failures)
        expected = {
            "task1": "success",
            "task2": "success",
            "task3": "success"
        }
        self.assertEqual(result, expected)

    async def test_cycle_detection(self):
        tasks = {
            "task1": {"function": "func1", "dependencies": ["task3"], "priority": 1},
            "task2": {"function": "func2", "dependencies": ["task1"], "priority": 2},
            "task3": {"function": "func3", "dependencies": ["task2"], "priority": 3}
        }
        num_workers = 1
        max_concurrency_per_worker = 1
        execution_times = {
            "func1": 1,
            "func2": 1,
            "func3": 1
        }
        task_failures = {}

        with self.assertRaises(CycleError):
            await run_scheduler(tasks, num_workers, max_concurrency_per_worker, execution_times, task_failures)

    async def test_prioritization(self):
        tasks = {
            "task1": {"function": "task_low", "dependencies": [], "priority": 5},
            "task2": {"function": "task_high", "dependencies": [], "priority": 1},
            "task3": {"function": "task_medium", "dependencies": [], "priority": 3}
        }
        num_workers = 1
        max_concurrency_per_worker = 3
        execution_times = {
            "task_low": 1,
            "task_high": 1,
            "task_medium": 1
        }
        task_failures = {}

        result = await run_scheduler(tasks, num_workers, max_concurrency_per_worker, execution_times, task_failures)
        expected = {
            "task1": "success",
            "task2": "success",
            "task3": "success"
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()