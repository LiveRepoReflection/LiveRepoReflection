import unittest
from task_weaver import schedule_tasks


class TaskWeaverTest(unittest.TestCase):
    def test_simple_schedule(self):
        tasks = [
            {"task_id": "A", "dependencies": [], "cpu_requirement": 2, "memory_requirement": 4, "execution_time": 10},
            {"task_id": "B", "dependencies": ["A"], "cpu_requirement": 1, "memory_requirement": 2, "execution_time": 5},
            {"task_id": "C", "dependencies": ["A"], "cpu_requirement": 3, "memory_requirement": 6, "execution_time": 8},
            {"task_id": "D", "dependencies": ["B", "C"], "cpu_requirement": 2, "memory_requirement": 4, "execution_time": 7},
        ]
        
        machines = [
            {"machine_id": "M1", "cpu_capacity": 4, "memory_capacity": 8},
            {"machine_id": "M2", "cpu_capacity": 3, "memory_capacity": 6},
        ]
        
        parallelism_limit = 3
        
        schedule = schedule_tasks(tasks, machines, parallelism_limit)
        
        # Verify that all tasks are scheduled
        self.assertEqual(len(schedule), len(tasks))
        
        # Check if all task_ids are in schedule
        for task in tasks:
            self.assertIn(task["task_id"], schedule)
            self.assertIn("machine_id", schedule[task["task_id"]])
            self.assertIn("start_time", schedule[task["task_id"]])
        
        # Verify dependency constraints
        for task in tasks:
            task_id = task["task_id"]
            task_start_time = schedule[task_id]["start_time"]
            
            for dep_id in task["dependencies"]:
                dep_task = next(t for t in tasks if t["task_id"] == dep_id)
                dep_end_time = schedule[dep_id]["start_time"] + dep_task["execution_time"]
                self.assertGreaterEqual(task_start_time, dep_end_time, 
                                       f"Task {task_id} starts before dependency {dep_id} completes")
        
        # Check resource constraints at each point in time
        execution_timeline = self._generate_timeline(tasks, schedule)
        machine_usage = self._check_resource_constraints(tasks, machines, schedule, execution_timeline)
        
        # Check parallelism limit
        for time_point in execution_timeline:
            running_tasks = sum(1 for usage in machine_usage.values() if usage["tasks"].get(time_point))
            self.assertLessEqual(running_tasks, parallelism_limit, 
                               f"Parallelism limit exceeded at time {time_point}")
    
    def test_no_valid_schedule(self):
        # Test case where tasks require more resources than available
        tasks = [
            {"task_id": "A", "dependencies": [], "cpu_requirement": 10, "memory_requirement": 20, "execution_time": 5},
        ]
        
        machines = [
            {"machine_id": "M1", "cpu_capacity": 4, "memory_capacity": 8},
        ]
        
        parallelism_limit = 1
        
        with self.assertRaises(Exception):
            schedule_tasks(tasks, machines, parallelism_limit)
    
    def test_cyclic_dependencies(self):
        # Test case with cyclic dependencies
        tasks = [
            {"task_id": "A", "dependencies": ["C"], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 1},
            {"task_id": "B", "dependencies": ["A"], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 1},
            {"task_id": "C", "dependencies": ["B"], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 1},
        ]
        
        machines = [
            {"machine_id": "M1", "cpu_capacity": 2, "memory_requirement": 2, "execution_time": 2},
        ]
        
        parallelism_limit = 1
        
        with self.assertRaises(Exception):
            schedule_tasks(tasks, machines, parallelism_limit)
    
    def test_complex_schedule(self):
        tasks = [
            {"task_id": "A", "dependencies": [], "cpu_requirement": 2, "memory_requirement": 4, "execution_time": 5},
            {"task_id": "B", "dependencies": [], "cpu_requirement": 1, "memory_requirement": 2, "execution_time": 3},
            {"task_id": "C", "dependencies": ["A"], "cpu_requirement": 3, "memory_requirement": 5, "execution_time": 4},
            {"task_id": "D", "dependencies": ["A", "B"], "cpu_requirement": 2, "memory_requirement": 3, "execution_time": 6},
            {"task_id": "E", "dependencies": ["C"], "cpu_requirement": 1, "memory_requirement": 2, "execution_time": 2},
            {"task_id": "F", "dependencies": ["C", "D"], "cpu_requirement": 2, "memory_requirement": 4, "execution_time": 3},
            {"task_id": "G", "dependencies": ["E", "F"], "cpu_requirement": 3, "memory_requirement": 6, "execution_time": 5},
        ]
        
        machines = [
            {"machine_id": "M1", "cpu_capacity": 4, "memory_capacity": 8},
            {"machine_id": "M2", "cpu_capacity": 3, "memory_capacity": 6},
            {"machine_id": "M3", "cpu_capacity": 2, "memory_capacity": 4},
        ]
        
        parallelism_limit = 4
        
        schedule = schedule_tasks(tasks, machines, parallelism_limit)
        
        # Verify that all tasks are scheduled
        self.assertEqual(len(schedule), len(tasks))
        
        # Check if all task_ids are in schedule
        for task in tasks:
            self.assertIn(task["task_id"], schedule)
        
        # Verify dependency constraints
        for task in tasks:
            task_id = task["task_id"]
            task_start_time = schedule[task_id]["start_time"]
            
            for dep_id in task["dependencies"]:
                dep_task = next(t for t in tasks if t["task_id"] == dep_id)
                dep_end_time = schedule[dep_id]["start_time"] + dep_task["execution_time"]
                self.assertGreaterEqual(task_start_time, dep_end_time)
        
        # Check resource constraints at each point in time
        execution_timeline = self._generate_timeline(tasks, schedule)
        machine_usage = self._check_resource_constraints(tasks, machines, schedule, execution_timeline)
        
        # Check parallelism limit
        for time_point in execution_timeline:
            running_tasks = sum(1 for usage in machine_usage.values() if usage["tasks"].get(time_point))
            self.assertLessEqual(running_tasks, parallelism_limit)
    
    def test_makespan_optimization(self):
        # Test if the algorithm produces a schedule that minimizes makespan
        # This is a basic test to ensure the makespan is reasonable
        tasks = [
            {"task_id": "A", "dependencies": [], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 2},
            {"task_id": "B", "dependencies": [], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 2},
            {"task_id": "C", "dependencies": ["A"], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 2},
            {"task_id": "D", "dependencies": ["B"], "cpu_requirement": 1, "memory_requirement": 1, "execution_time": 2},
        ]
        
        machines = [
            {"machine_id": "M1", "cpu_capacity": 1, "memory_capacity": 2},
            {"machine_id": "M2", "cpu_capacity": 1, "memory_capacity": 2},
        ]
        
        parallelism_limit = 2
        
        schedule = schedule_tasks(tasks, machines, parallelism_limit)
        
        # Calculate makespan
        makespan = 0
        for task_id, task_schedule in schedule.items():
            task = next(t for t in tasks if t["task_id"] == task_id)
            task_end_time = task_schedule["start_time"] + task["execution_time"]
            makespan = max(makespan, task_end_time)
        
        # In the optimal case, A and B run in parallel, followed by C and D in parallel
        # So the best possible makespan is 4
        self.assertLessEqual(makespan, 6)  # Allow some suboptimality
    
    def test_large_workload(self):
        # Generate a large workload to test scalability
        tasks = []
        for i in range(100):
            deps = []
            if i > 0 and i % 10 == 0:
                deps = [f"Task{i-10}"]
            tasks.append({
                "task_id": f"Task{i}",
                "dependencies": deps,
                "cpu_requirement": 1,
                "memory_requirement": 2,
                "execution_time": 3
            })
        
        machines = []
        for i in range(10):
            machines.append({
                "machine_id": f"Machine{i}",
                "cpu_capacity": 4,
                "memory_capacity": 8
            })
        
        parallelism_limit = 20
        
        # Test if the scheduler can handle a large workload without crashing
        try:
            schedule = schedule_tasks(tasks, machines, parallelism_limit)
            self.assertEqual(len(schedule), len(tasks))
        except Exception as e:
            self.fail(f"schedule_tasks raised exception {e} on large workload")
    
    def _generate_timeline(self, tasks, schedule):
        # Generate a list of all time points where a task starts or ends
        timeline = set()
        for task in tasks:
            task_id = task["task_id"]
            start_time = schedule[task_id]["start_time"]
            end_time = start_time + task["execution_time"]
            timeline.add(start_time)
            timeline.add(end_time)
        return sorted(timeline)
    
    def _check_resource_constraints(self, tasks, machines, schedule, timeline):
        # Check if resource constraints are satisfied for each machine at each time point
        machine_usage = {m["machine_id"]: {"cpu": 0, "memory": 0, "tasks": {}} for m in machines}
        
        # For each time point
        for t in range(len(timeline) - 1):
            current_time = timeline[t]
            next_time = timeline[t + 1]
            
            # Reset usage
            for machine_id in machine_usage:
                machine_usage[machine_id]["cpu"] = 0
                machine_usage[machine_id]["memory"] = 0
                machine_usage[machine_id]["tasks"][current_time] = []
            
            # Calculate usage for this time point
            for task in tasks:
                task_id = task["task_id"]
                task_start = schedule[task_id]["start_time"]
                task_end = task_start + task["execution_time"]
                machine_id = schedule[task_id]["machine_id"]
                
                if task_start <= current_time < task_end:
                    machine_usage[machine_id]["cpu"] += task["cpu_requirement"]
                    machine_usage[machine_id]["memory"] += task["memory_requirement"]
                    machine_usage[machine_id]["tasks"][current_time].append(task_id)
            
            # Check if any machine exceeds its capacity
            for machine in machines:
                machine_id = machine["machine_id"]
                usage = machine_usage[machine_id]
                self.assertLessEqual(usage["cpu"], machine["cpu_capacity"], 
                                   f"CPU capacity exceeded for machine {machine_id} at time {current_time}")
                self.assertLessEqual(usage["memory"], machine["memory_capacity"], 
                                   f"Memory capacity exceeded for machine {machine_id} at time {current_time}")
        
        return machine_usage


if __name__ == "__main__":
    unittest.main()