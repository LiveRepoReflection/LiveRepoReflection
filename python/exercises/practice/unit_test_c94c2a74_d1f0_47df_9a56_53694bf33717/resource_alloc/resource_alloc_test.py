import unittest
from resource_alloc import schedule_tasks

class TestResourceAlloc(unittest.TestCase):
    def check_schedule(self, schedule, N, M, W, node_capacities, task_definitions, C):
        # Build a mapping from task_id to (worker_node_id, start_time)
        task_assigns = {}
        for assignment in schedule:
            task_id, worker_node_id, start_time = assignment
            if task_id in task_assigns:
                self.fail(f"Duplicate assignment for task {task_id}")
            task_assigns[task_id] = (worker_node_id, start_time)

        # Ensure all tasks have been assigned exactly once
        self.assertEqual(len(task_assigns), len(task_definitions), "Not all tasks are assigned")

        # Convert task_definitions into a dict for easier access.
        tasks = {}
        for i, (arrival_time, resource_requirements, execution_time, dependencies, output_data_size) in enumerate(task_definitions):
            tasks[i] = {
                'arrival': arrival_time,
                'req': resource_requirements,
                'exec': execution_time,
                'deps': dependencies,
                'output': output_data_size
            }

        # Check start_time >= arrival time and finish time within time window W
        for task_id, (node, start_time) in task_assigns.items():
            task = tasks[task_id]
            self.assertGreaterEqual(start_time, task['arrival'], f"Task {task_id} starts before its arrival time")
            finish_time = start_time + task['exec']
            self.assertLessEqual(finish_time, W, f"Task {task_id} finishes after the time window W")

        # Dependency constraints: A task must start only after all its dependencies have finished.
        for task_id, (node, start_time) in task_assigns.items():
            task = tasks[task_id]
            for dep in task['deps']:
                self.assertIn(dep, task_assigns, f"Dependency {dep} for task {task_id} was not assigned")
                dep_node, dep_start_time = task_assigns[dep]
                dep_finish_time = dep_start_time + tasks[dep]['exec']
                self.assertGreaterEqual(start_time, dep_finish_time, f"Task {task_id} starts before its dependency {dep} finishes")

        # Resource constraints: For each worker node, ensure that at any point in time, the summed resource usage does not exceed the node's capacity.
        for node in range(N):
            events = []
            for task_id, (assigned_node, start_time) in task_assigns.items():
                if assigned_node == node:
                    exec_time = tasks[task_id]['exec']
                    finish_time = start_time + exec_time
                    # Add event for task start (resource addition)
                    events.append((start_time, tasks[task_id]['req']))
                    # Add event for task finish (resource subtraction)
                    events.append((finish_time, [-r for r in tasks[task_id]['req']]))
            # Sort events by time; if times are identical, removals (negative changes) occur before additions.
            events.sort(key=lambda x: (x[0], x[1][0] if x[1][0] < 0 else 1))
            current_usage = [0] * M
            for time, delta in events:
                for j in range(M):
                    current_usage[j] += delta[j]
                    self.assertLessEqual(current_usage[j], node_capacities[node][j],
                        f"Node {node} exceeds capacity on resource {j} at time {time}")

    def test_sample_schedule(self):
        N = 2
        M = 2
        W = 10
        node_capacities = [
            [4, 8],
            [2, 4]
        ]
        task_definitions = [
            (0, [1, 2], 3, [], 10),    # Task 0: arrives at 0, requires [1,2], executes 3.
            (1, [2, 1], 2, [0], 5),     # Task 1: arrives at 1, requires [2,1], depends on Task 0.
            (2, [1, 1], 4, [], 0)       # Task 2: arrives at 2, requires [1,1], executes 4.
        ]
        C = 0.1
        schedule = schedule_tasks(N, M, W, node_capacities, task_definitions, C)
        self.check_schedule(schedule, N, M, W, node_capacities, task_definitions, C)

    def test_dependency_chain(self):
        # Test a linear dependency chain on a single node.
        N = 1
        M = 1
        W = 20
        node_capacities = [
            [5]
        ]
        task_definitions = [
            (0, [2], 3, [], 5),   # Task 0
            (1, [2], 3, [0], 5),  # Task 1 depends on Task 0
            (2, [2], 3, [1], 5),  # Task 2 depends on Task 1
            (3, [2], 3, [2], 5)   # Task 3 depends on Task 2
        ]
        C = 0.0
        schedule = schedule_tasks(N, M, W, node_capacities, task_definitions, C)
        self.check_schedule(schedule, N, M, W, node_capacities, task_definitions, C)

    def test_concurrent_tasks(self):
        # Test multiple tasks scheduled concurrently on the same node.
        N = 1
        M = 2
        W = 15
        node_capacities = [
            [4, 4]
        ]
        task_definitions = [
            (0, [2, 2], 5, [], 3),  # Task 0
            (1, [2, 1], 4, [], 2),  # Task 1
            (2, [1, 2], 3, [], 1),  # Task 2
            (3, [1, 1], 2, [], 0)   # Task 3
        ]
        C = 0.2
        schedule = schedule_tasks(N, M, W, node_capacities, task_definitions, C)
        self.check_schedule(schedule, N, M, W, node_capacities, task_definitions, C)

    def test_complex_graph(self):
        # Test a more complex task graph with multiple nodes and dependencies.
        N = 3
        M = 3
        W = 30
        node_capacities = [
            [4, 4, 4],
            [3, 3, 3],
            [5, 5, 5]
        ]
        task_definitions = [
            (0, [1, 1, 1], 4, [], 5),      # Task 0
            (1, [1, 2, 1], 3, [0], 4),      # Task 1 depends on Task 0
            (2, [2, 1, 1], 5, [0], 3),      # Task 2 depends on Task 0
            (3, [1, 1, 2], 6, [1, 2], 2),   # Task 3 depends on Task 1 and Task 2
            (4, [1, 1, 1], 2, [0], 1),      # Task 4 depends on Task 0
            (5, [2, 2, 2], 4, [3, 4], 6),   # Task 5 depends on Task 3 and Task 4
            (6, [1, 1, 1], 3, [2], 2)       # Task 6 depends on Task 2
        ]
        C = 0.15
        schedule = schedule_tasks(N, M, W, node_capacities, task_definitions, C)
        self.check_schedule(schedule, N, M, W, node_capacities, task_definitions, C)

if __name__ == '__main__':
    unittest.main()