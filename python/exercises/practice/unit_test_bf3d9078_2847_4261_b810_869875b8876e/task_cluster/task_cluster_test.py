import unittest
import threading
import time

import task_cluster

class DummyTask:
    def __init__(self, task_id, command, resources, dependencies, priority, max_time):
        self.task_id = task_id
        self.command = command
        self.resources = resources
        self.dependencies = dependencies
        self.priority = priority
        self.max_time = max_time

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "command": self.command,
            "resources": self.resources,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "max_time": self.max_time
        }

class DummyWorker:
    def __init__(self, worker_id, resources):
        self.worker_id = worker_id
        self.resources = resources

    def status(self):
        # Simulate a worker status report
        return {"worker_id": self.worker_id, "resources": self.resources, "healthy": True}

class TaskClusterTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize the scheduler with a default scheduling algorithm (e.g., FCFS)
        self.scheduler = task_cluster.TaskScheduler(scheduling_algo="fcfs")
        # Clear any existing state if necessary
        self.scheduler.reset()

    def test_submit_valid_task(self):
        # Create a valid task with complete metadata
        task = DummyTask(
            task_id="task_1",
            command="echo 'Hello World'",
            resources={"cpu": 2, "memory": 1024, "disk": 100},
            dependencies=[],
            priority=5,
            max_time=60
        ).to_dict()
        result = self.scheduler.submit_task(task)
        self.assertEqual(result, "task_1")
        self.assertIn("task_1", self.scheduler.get_all_tasks())

    def test_submit_invalid_task(self):
        # Create an invalid task missing a required field (e.g., no command)
        invalid_task = {
            "task_id": "task_invalid",
            "resources": {"cpu": 1, "memory": 512},
            "dependencies": [],
            "priority": 3,
            "max_time": 30
        }
        with self.assertRaises(ValueError):
            self.scheduler.submit_task(invalid_task)

    def test_task_dependencies_scheduling(self):
        # Create multiple tasks with dependencies; task_3 depends on task_1 and task_2
        task1 = DummyTask(
            task_id="task_1",
            command="run task 1",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=4,
            max_time=30
        ).to_dict()

        task2 = DummyTask(
            task_id="task_2",
            command="run task 2",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=4,
            max_time=30
        ).to_dict()

        task3 = DummyTask(
            task_id="task_3",
            command="run task 3",
            resources={"cpu": 2, "memory": 512},
            dependencies=["task_1", "task_2"],
            priority=5,
            max_time=45
        ).to_dict()

        self.scheduler.submit_task(task1)
        self.scheduler.submit_task(task2)
        self.scheduler.submit_task(task3)

        schedule = self.scheduler.schedule_tasks()
        # Ensure task_3 is scheduled only after task_1 and task_2
        idx1 = schedule.index("task_1")
        idx2 = schedule.index("task_2")
        idx3 = schedule.index("task_3")
        self.assertTrue(idx1 < idx3 and idx2 < idx3)

    def test_priority_scheduling(self):
        # Switch algorithm to priority based scheduling
        self.scheduler.set_scheduling_algo("priority")
        # Create tasks with different priorities
        task_low = DummyTask(
            task_id="task_low",
            command="low priority",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=1,
            max_time=20
        ).to_dict()

        task_high = DummyTask(
            task_id="task_high",
            command="high priority",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=10,
            max_time=20
        ).to_dict()

        self.scheduler.submit_task(task_low)
        self.scheduler.submit_task(task_high)

        schedule = self.scheduler.schedule_tasks()
        # In a priority algorithm, 'task_high' should be scheduled before 'task_low'
        self.assertEqual(schedule[0], "task_high")
        self.assertEqual(schedule[1], "task_low")

    def test_register_worker_and_status(self):
        # Register a worker and simulate status report
        worker = DummyWorker(worker_id="worker_1", resources={"cpu": 4, "memory": 4096, "disk": 500})
        self.scheduler.register_worker(worker.worker_id, worker.status())
        status = self.scheduler.get_worker_status(worker.worker_id)
        self.assertEqual(status["worker_id"], "worker_1")
        self.assertTrue(status["healthy"])

    def test_worker_failure_handling(self):
        # Register two workers and assign tasks. Then simulate failure of one worker.
        worker1 = DummyWorker(worker_id="worker_1", resources={"cpu": 4, "memory": 4096, "disk": 500})
        worker2 = DummyWorker(worker_id="worker_2", resources={"cpu": 2, "memory": 2048, "disk": 250})
        self.scheduler.register_worker(worker1.worker_id, worker1.status())
        self.scheduler.register_worker(worker2.worker_id, worker2.status())

        task = DummyTask(
            task_id="task_failure_test",
            command="simulate long computation",
            resources={"cpu": 2, "memory": 1024},
            dependencies=[],
            priority=5,
            max_time=120
        ).to_dict()
        self.scheduler.submit_task(task)
        # Initially schedule the tasks; assume task is assigned to worker_1
        assignment = self.scheduler.schedule_tasks()
        assigned_worker = self.scheduler.get_task_assignment("task_failure_test")
        # Simulate worker failure
        self.scheduler.simulate_worker_failure(assigned_worker)
        # After failure, the task should be rescheduled to a healthy worker
        new_assignment = self.scheduler.get_task_assignment("task_failure_test")
        self.assertNotEqual(assigned_worker, new_assignment)
        self.assertIn(new_assignment, [worker1.worker_id, worker2.worker_id])
    
    def test_switch_scheduling_algo(self):
        # Test switching between scheduling algorithms impacts the scheduling order
        # Submit tasks first using FCFS then switch to SJF
        task_a = DummyTask(
            task_id="task_a",
            command="run A",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=3,
            max_time=50
        ).to_dict()

        task_b = DummyTask(
            task_id="task_b",
            command="run B",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=3,
            max_time=20  # shorter max_time representing shorter task
        ).to_dict()

        self.scheduler.submit_task(task_a)
        self.scheduler.submit_task(task_b)
        # Initially, with FCFS, tasks are scheduled in insertion order.
        self.scheduler.set_scheduling_algo("fcfs")
        schedule_fcfs = self.scheduler.schedule_tasks()
        self.assertEqual(schedule_fcfs, ["task_a", "task_b"])
        # Switch to a shortest job first (SJF) scheduling
        self.scheduler.set_scheduling_algo("sjf")
        schedule_sjf = self.scheduler.schedule_tasks()
        # Expect task_b to come before task_a because of shorter max_time.
        self.assertEqual(schedule_sjf, ["task_b", "task_a"])

    def test_monitor_task(self):
        # Submit a task and simulate monitoring its progress
        task = DummyTask(
            task_id="task_monitor",
            command="simulate monitoring",
            resources={"cpu": 1, "memory": 256},
            dependencies=[],
            priority=5,
            max_time=60
        ).to_dict()
        self.scheduler.submit_task(task)
        # Simulate that the task is running
        self.scheduler.start_task("task_monitor")
        # Allow some time for simulated progress (if asynchronous monitoring is implemented)
        time.sleep(0.1)
        progress = self.scheduler.monitor_task("task_monitor")
        self.assertIn("progress", progress)
        self.assertGreaterEqual(progress["progress"], 0)
        self.assertLessEqual(progress["progress"], 100)

    def test_concurrent_task_submission(self):
        # Test that concurrent submissions are handled correctly.
        submission_results = []
        def submit_task(task_id):
            task = DummyTask(
                task_id=task_id,
                command="concurrent command",
                resources={"cpu": 1, "memory": 256},
                dependencies=[],
                priority=5,
                max_time=60
            ).to_dict()
            result = self.scheduler.submit_task(task)
            submission_results.append(result)

        threads = []
        for i in range(10):
            t = threading.Thread(target=submit_task, args=(f"concurrent_task_{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(submission_results), 10)
        all_tasks = self.scheduler.get_all_tasks()
        for i in range(10):
            self.assertIn(f"concurrent_task_{i}", all_tasks)

if __name__ == '__main__':
    unittest.main()