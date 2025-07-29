import unittest
from constrained_scheduler import schedule_tasks

class TestConstrainedScheduler(unittest.TestCase):
    def setUp(self):
        # Default machines used across multiple tests
        self.default_machines = [
            {"machine_id": 1, "total_cpu_cores": 4, "total_memory_gb": 16},
            {"machine_id": 2, "total_cpu_cores": 8, "total_memory_gb": 32}
        ]

    def validate_schedule(self, tasks, machines, schedule):
        # Validate that each task is scheduled exactly once.
        self.assertEqual(set(schedule.keys()), {task["task_id"] for task in tasks})
        machine_lookup = {m["machine_id"]: m for m in machines}

        # Validate scheduled tasks regarding time and machine eligibility.
        for task in tasks:
            tid = task["task_id"]
            machine_id, start_time, end_time = schedule[tid]
            self.assertIn(machine_id, machine_lookup)
            self.assertGreaterEqual(start_time, 0)
            self.assertGreater(end_time, start_time)
            # The duration should be at least the estimated runtime.
            self.assertGreaterEqual(end_time - start_time, task["estimated_runtime"])

        # Validate dependency constraints: a task must start after all its dependencies have finished.
        for task in tasks:
            for dep in task["dependencies"]:
                self.assertIn(dep, schedule)
                _, dep_start, dep_end = schedule[dep]
                self.assertLessEqual(dep_end, schedule[task["task_id"]][1])

    def test_empty_tasks(self):
        tasks = []
        machines = self.default_machines
        schedule = schedule_tasks(tasks, machines)
        self.assertEqual(schedule, {})

    def test_no_machines(self):
        tasks = [
            {"task_id": 1, "cpu_cores": 2, "memory_gb": 4, "dependencies": [], "estimated_runtime": 3.0}
        ]
        machines = []
        with self.assertRaises(ValueError):
            schedule_tasks(tasks, machines)

    def test_single_task(self):
        tasks = [
            {"task_id": 1, "cpu_cores": 2, "memory_gb": 4, "dependencies": [], "estimated_runtime": 5.0}
        ]
        machines = [
            {"machine_id": 101, "total_cpu_cores": 4, "total_memory_gb": 16}
        ]
        schedule = schedule_tasks(tasks, machines)
        self.validate_schedule(tasks, machines, schedule)

    def test_dependency_order(self):
        tasks = [
            {"task_id": 1, "cpu_cores": 2, "memory_gb": 4, "dependencies": [], "estimated_runtime": 2.0},
            {"task_id": 2, "cpu_cores": 2, "memory_gb": 4, "dependencies": [1], "estimated_runtime": 3.0},
            {"task_id": 3, "cpu_cores": 1, "memory_gb": 2, "dependencies": [1], "estimated_runtime": 1.0},
            {"task_id": 4, "cpu_cores": 2, "memory_gb": 4, "dependencies": [2, 3], "estimated_runtime": 4.0}
        ]
        machines = [
            {"machine_id": 201, "total_cpu_cores": 4, "total_memory_gb": 16},
            {"machine_id": 202, "total_cpu_cores": 4, "total_memory_gb": 16}
        ]
        schedule = schedule_tasks(tasks, machines)
        self.validate_schedule(tasks, machines, schedule)

    def test_insufficient_resources(self):
        # Task requires more resources than available on any machine.
        tasks = [
            {"task_id": 1, "cpu_cores": 16, "memory_gb": 64, "dependencies": [], "estimated_runtime": 5.0}
        ]
        machines = [
            {"machine_id": 301, "total_cpu_cores": 4, "total_memory_gb": 16},
            {"machine_id": 302, "total_cpu_cores": 8, "total_memory_gb": 32}
        ]
        with self.assertRaises(ValueError):
            schedule_tasks(tasks, machines)

    def test_overlapping_tasks_resource_usage(self):
        # Schedule several tasks on a single machine to test concurrent resource usage.
        tasks = [
            {"task_id": 1, "cpu_cores": 2, "memory_gb": 8, "dependencies": [], "estimated_runtime": 5.0},
            {"task_id": 2, "cpu_cores": 2, "memory_gb": 8, "dependencies": [], "estimated_runtime": 5.0},
            {"task_id": 3, "cpu_cores": 2, "memory_gb": 8, "dependencies": [], "estimated_runtime": 5.0},
            {"task_id": 4, "cpu_cores": 2, "memory_gb": 8, "dependencies": [], "estimated_runtime": 5.0}
        ]
        machines = [
            {"machine_id": 401, "total_cpu_cores": 4, "total_memory_gb": 16}
        ]
        schedule = schedule_tasks(tasks, machines)
        self.validate_schedule(tasks, machines, schedule)

        # For each machine, verify that at any point in time the total resource usage does not exceed available limits.
        machine_resources = {m["machine_id"]: (m["total_cpu_cores"], m["total_memory_gb"]) for m in machines}
        tasks_by_machine = {}
        for tid, (machine_id, start, end) in schedule.items():
            tasks_by_machine.setdefault(machine_id, []).append((start, end, tid))
        
        time_points = set()
        for intervals in tasks_by_machine.values():
            for start, end, _ in intervals:
                time_points.add(start)
                time_points.add(end)
        time_points = sorted(time_points)
        
        for i in range(len(time_points) - 1):
            t_start = time_points[i]
            t_end = time_points[i + 1]
            for machine_id, intervals in tasks_by_machine.items():
                cpu_used = 0
                mem_used = 0
                for s, e, tid in intervals:
                    # Check if the interval [t_start, t_end] overlaps with the task execution interval.
                    if s < t_end and e > t_start:
                        task = next(task for task in tasks if task["task_id"] == tid)
                        cpu_used += task["cpu_cores"]
                        mem_used += task["memory_gb"]
                available_cpu, available_mem = machine_resources[machine_id]
                self.assertLessEqual(cpu_used, available_cpu)
                self.assertLessEqual(mem_used, available_mem)

if __name__ == '__main__':
    unittest.main()