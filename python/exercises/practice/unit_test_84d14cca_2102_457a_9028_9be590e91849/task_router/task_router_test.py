import unittest
from task_router import route_tasks


class TaskRouterTest(unittest.TestCase):
    def test_basic_routing(self):
        tasks = [
            {"task_id": 1, "task_type": "CPU-bound", "priority": 2, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 2, "task_type": "IO-bound", "priority": 1, "cpu_needed": 1, "memory_needed": 2, "disk_io_needed": 3},
            {"task_id": 3, "task_type": "CPU-bound", "priority": 3, "cpu_needed": 3, "memory_needed": 6, "disk_io_needed": 2},
        ]

        workers = [
            {"worker_id": 1, "cpu_available": 4, "memory_available": 8, "disk_io_capacity": 4, "task_types_supported": ["CPU-bound", "IO-bound"]},
            {"worker_id": 2, "cpu_available": 3, "memory_available": 6, "disk_io_capacity": 2, "task_types_supported": ["CPU-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Ensure all tasks are assigned or in unassigned list
        all_assigned_tasks = []
        for worker_id, task_ids in result.items():
            if worker_id != 'unassigned':
                all_assigned_tasks.extend(task_ids)
        all_assigned_tasks.extend(result.get('unassigned', []))
        
        self.assertEqual(sorted(all_assigned_tasks), [1, 2, 3])
        
        # Check that assignments respect resource constraints
        for worker_id, task_ids in result.items():
            if worker_id == 'unassigned':
                continue
                
            worker = next(w for w in workers if w["worker_id"] == worker_id)
            assigned_tasks = [t for t in tasks if t["task_id"] in task_ids]
            
            total_cpu = sum(t["cpu_needed"] for t in assigned_tasks)
            total_memory = sum(t["memory_needed"] for t in assigned_tasks)
            total_io = sum(t["disk_io_needed"] for t in assigned_tasks)
            
            self.assertLessEqual(total_cpu, worker["cpu_available"])
            self.assertLessEqual(total_memory, worker["memory_available"])
            self.assertLessEqual(total_io, worker["disk_io_capacity"])
            
            # Check that task types are supported
            for task in assigned_tasks:
                self.assertIn(task["task_type"], worker["task_types_supported"])

    def test_unassigned_tasks(self):
        tasks = [
            {"task_id": 1, "task_type": "CPU-bound", "priority": 2, "cpu_needed": 5, "memory_needed": 10, "disk_io_needed": 3},
            {"task_id": 2, "task_type": "IO-bound", "priority": 1, "cpu_needed": 1, "memory_needed": 2, "disk_io_needed": 3},
        ]

        workers = [
            {"worker_id": 1, "cpu_available": 2, "memory_available": 4, "disk_io_capacity": 2, "task_types_supported": ["CPU-bound", "IO-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Task 1 should be unassigned due to resource constraints
        self.assertIn(1, result.get('unassigned', []))
        
        # Task 2 could be assigned to worker 1
        if 1 in result:
            self.assertIn(2, result[1])

    def test_unsupported_task_type(self):
        tasks = [
            {"task_id": 1, "task_type": "Memory-intensive", "priority": 2, "cpu_needed": 1, "memory_needed": 2, "disk_io_needed": 1},
        ]

        workers = [
            {"worker_id": 1, "cpu_available": 4, "memory_available": 8, "disk_io_capacity": 4, "task_types_supported": ["CPU-bound", "IO-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Task 1 should be unassigned due to unsupported task type
        self.assertIn(1, result.get('unassigned', []))

    def test_priority_handling(self):
        tasks = [
            {"task_id": 1, "task_type": "CPU-bound", "priority": 1, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 2, "task_type": "CPU-bound", "priority": 3, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 3, "task_type": "CPU-bound", "priority": 2, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
        ]

        workers = [
            {"worker_id": 1, "cpu_available": 4, "memory_available": 8, "disk_io_capacity": 4, "task_types_supported": ["CPU-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Check if worker 1 has tasks assigned
        if 1 in result and len(result[1]) >= 2:
            # The highest priority task (task_id 2) should be assigned first
            task_ids = result[1]
            self.assertEqual(task_ids[0], 2)
            
            # The medium priority task (task_id 3) should be assigned second
            if len(task_ids) > 1:
                self.assertEqual(task_ids[1], 3)

    def test_tie_breaking(self):
        tasks = [
            {"task_id": 1, "task_type": "CPU-bound", "priority": 2, "cpu_needed": 1, "memory_needed": 2, "disk_io_needed": 1},
        ]

        workers = [
            {"worker_id": 2, "cpu_available": 2, "memory_available": 4, "disk_io_capacity": 2, "task_types_supported": ["CPU-bound"]},
            {"worker_id": 1, "cpu_available": 2, "memory_available": 4, "disk_io_capacity": 2, "task_types_supported": ["CPU-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Since both workers are equally suitable, worker 1 should be chosen due to smallest worker_id
        self.assertIn(1, result.get(1, []))

    def test_large_scale_routing(self):
        # Generate a large number of tasks and workers
        tasks = []
        for i in range(1, 501):  # 500 tasks
            task_type = "CPU-bound" if i % 3 == 0 else "IO-bound" if i % 3 == 1 else "Memory-intensive"
            priority = i % 10 + 1
            cpu_needed = i % 4 + 1
            memory_needed = i % 8 + 1
            disk_io_needed = i % 6 + 1
            tasks.append({
                "task_id": i,
                "task_type": task_type,
                "priority": priority,
                "cpu_needed": cpu_needed,
                "memory_needed": memory_needed,
                "disk_io_needed": disk_io_needed
            })
        
        workers = []
        for i in range(1, 51):  # 50 workers
            cpu_available = (i % 5 + 2) * 2
            memory_available = (i % 10 + 3) * 2
            disk_io_capacity = (i % 7 + 1) * 3
            
            # Each worker supports at least one task type
            task_types_supported = []
            if i % 3 == 0 or i % 3 == 1:
                task_types_supported.append("CPU-bound")
            if i % 3 == 1 or i % 3 == 2:
                task_types_supported.append("IO-bound")
            if i % 3 == 2 or i % 3 == 0:
                task_types_supported.append("Memory-intensive")
                
            workers.append({
                "worker_id": i,
                "cpu_available": cpu_available,
                "memory_available": memory_available,
                "disk_io_capacity": disk_io_capacity,
                "task_types_supported": task_types_supported
            })
        
        result = route_tasks(tasks, workers)
        
        # Verify that the output structure is correct
        self.assertIn('unassigned', result)
        
        # Check that tasks are either assigned or in the unassigned list
        assigned_task_ids = []
        for worker_id, task_ids in result.items():
            if worker_id != 'unassigned':
                assigned_task_ids.extend(task_ids)
        unassigned_task_ids = result.get('unassigned', [])
        
        total_tasks_accounted_for = len(assigned_task_ids) + len(unassigned_task_ids)
        self.assertEqual(total_tasks_accounted_for, len(tasks))
        
        # Check for optimal distribution - the makespan should be somewhat balanced
        worker_loads = {}
        for worker_id, task_ids in result.items():
            if worker_id != 'unassigned':
                assigned_tasks = [t for t in tasks if t["task_id"] in task_ids]
                worker_loads[worker_id] = sum(t["cpu_needed"] for t in assigned_tasks)
        
        if worker_loads:
            # Calculate the standard deviation of worker loads
            avg_load = sum(worker_loads.values()) / len(worker_loads)
            variance = sum((load - avg_load) ** 2 for load in worker_loads.values()) / len(worker_loads)
            std_dev = variance ** 0.5
            
            # Check that the standard deviation is not too high (indicating reasonable load balancing)
            # This is a heuristic and may need adjustment
            self.assertLessEqual(std_dev / avg_load, 1.0, "Worker loads are not well balanced")

    def test_resource_utilization(self):
        tasks = [
            {"task_id": 1, "task_type": "CPU-bound", "priority": 3, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 2, "task_type": "CPU-bound", "priority": 2, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 3, "task_type": "CPU-bound", "priority": 1, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
        ]

        workers = [
            {"worker_id": 1, "cpu_available": 10, "memory_available": 20, "disk_io_capacity": 10, "task_types_supported": ["CPU-bound"]},
            {"worker_id": 2, "cpu_available": 10, "memory_available": 20, "disk_io_capacity": 10, "task_types_supported": ["CPU-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Check that tasks are distributed to multiple workers for better resource utilization
        assigned_workers = [worker_id for worker_id in result.keys() if worker_id != 'unassigned']
        self.assertGreater(len(assigned_workers), 1, "Tasks should be distributed across multiple workers")

    def test_makespan_minimization(self):
        tasks = [
            {"task_id": 1, "task_type": "CPU-bound", "priority": 1, "cpu_needed": 5, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 2, "task_type": "CPU-bound", "priority": 1, "cpu_needed": 3, "memory_needed": 4, "disk_io_needed": 1},
            {"task_id": 3, "task_type": "CPU-bound", "priority": 1, "cpu_needed": 2, "memory_needed": 4, "disk_io_needed": 1},
        ]

        workers = [
            {"worker_id": 1, "cpu_available": 6, "memory_available": 10, "disk_io_capacity": 5, "task_types_supported": ["CPU-bound"]},
            {"worker_id": 2, "cpu_available": 6, "memory_available": 10, "disk_io_capacity": 5, "task_types_supported": ["CPU-bound"]},
        ]

        result = route_tasks(tasks, workers)
        
        # Calculate the makespan
        worker_loads = {}
        for worker_id, task_ids in result.items():
            if worker_id != 'unassigned':
                assigned_tasks = [t for t in tasks if t["task_id"] in task_ids]
                worker_loads[worker_id] = sum(t["cpu_needed"] for t in assigned_tasks)
        
        if worker_loads:
            makespan = max(worker_loads.values())
            
            # For this example, the optimal makespan would be 5 (task 1 on one worker, tasks 2 and 3 on the other)
            self.assertEqual(makespan, 5, "Makespan was not minimized correctly")

if __name__ == '__main__':
    unittest.main()