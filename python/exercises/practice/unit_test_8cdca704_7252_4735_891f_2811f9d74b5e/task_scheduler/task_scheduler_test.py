import unittest
from math import isclose

# Import the solution's schedule_tasks function
from task_scheduler import schedule_tasks

class TestTaskScheduler(unittest.TestCase):
    def validate_schedule(self, schedule, num_nodes, worker_resources, task_requirements, network_bandwidth, execution_times):
        # Validate that the schedule is a list of the correct length with valid node indices
        num_tasks = len(task_requirements)
        self.assertEqual(len(schedule), num_tasks, "Schedule length does not match number of tasks.")
        for assigned_node in schedule:
            self.assertIsInstance(assigned_node, int, "Assigned node must be an integer.")
            self.assertGreaterEqual(assigned_node, 0, "Node index must be non-negative.")
            self.assertLess(assigned_node, num_nodes, "Node index exceeds number of available nodes.")
        
        # For each task, check that its resource requirements are met by the chosen worker node,
        # and that its finish time (execution + potential transfer penalty) does not exceed its deadline.
        # We assume that each task's data is originally located on node 0.
        # Transfer time penalty = (DataSize) / (bandwidth from node 0 to assigned_node), if assigned_node != 0,
        # and 0 if assigned_node == 0.
        for i in range(num_tasks):
            cpu_req, mem_req, disk_req, data_size, deadline = task_requirements[i]
            assigned_node = schedule[i]
            cpu_avail, mem_avail, disk_avail = worker_resources[assigned_node]
            # Check that resources of the task do not exceed what the worker node offers.
            self.assertGreaterEqual(cpu_avail, cpu_req, f"Task {i} CPU requirement not met on node {assigned_node}.")
            self.assertGreaterEqual(mem_avail, mem_req, f"Task {i} Memory requirement not met on node {assigned_node}.")
            self.assertGreaterEqual(disk_avail, disk_req, f"Task {i} Disk requirement not met on node {assigned_node}.")

            # Calculate execution time for task i on the assigned_node.
            exec_time = execution_times[i][assigned_node]
            # Calculate transfer time penalty, assuming task data originally resides on node 0.
            if assigned_node == 0:
                transfer_time = 0
            else:
                bandwidth = network_bandwidth[0][assigned_node]
                # Avoid division by zero, though bandwidth should be positive.
                transfer_time = data_size / bandwidth if bandwidth > 0 else float('inf')

            finish_time = exec_time + transfer_time
            # Allow a small tolerance for floating point comparisons
            self.assertTrue(finish_time <= deadline or isclose(finish_time, deadline, rel_tol=1e-9),
                            f"Task {i} finish_time ({finish_time}) exceeds deadline ({deadline}).")
    
    def test_single_node(self):
        # Single worker node scenario
        num_nodes = 1
        worker_resources = [(4, 8, 10)]
        num_tasks = 3
        # Each task: (CPU, Memory, Disk, DataSize, Deadline)
        task_requirements = [
            (2, 4, 5, 2, 20),  # Should finish in time on node 0
            (1, 2, 3, 1, 15),
            (2, 3, 4, 3, 25)
        ]
        # Network bandwidth: 1x1 matrix, high value for self-transfer
        network_bandwidth = [[1e9]]
        # Execution times: for each task on node 0
        execution_times = [
            [10],
            [12],
            [15]
        ]
        schedule = schedule_tasks(num_nodes, worker_resources, num_tasks, task_requirements, network_bandwidth, execution_times)
        self.validate_schedule(schedule, num_nodes, worker_resources, task_requirements, network_bandwidth, execution_times)

    def test_multiple_nodes(self):
        # Multiple nodes scenario
        num_nodes = 3
        worker_resources = [
            (4, 8, 10),   # Node 0
            (8, 16, 20),  # Node 1
            (6, 12, 15)   # Node 2
        ]
        num_tasks = 4
        task_requirements = [
            (2, 4, 5, 2, 30),  # Prefer node 0: if transferred remains within deadline
            (3, 6, 7, 3, 40),  # May only run on node 1 or 2 due to resource constraints
            (1, 2, 3, 1, 20),  # Can run on any node
            (4, 8, 9, 2, 50)   # High CPU/memory; only node 1 qualifies
        ]
        # Network bandwidth matrix (3x3)
        network_bandwidth = [
            [1e9, 5, 2],
            [5, 1e9, 3],
            [2, 3, 1e9]
        ]
        # Execution times for tasks on each node:
        execution_times = [
            [12, 15, 14],  # Task 0
            [20, 18, 19],  # Task 1
            [8, 10, 9],    # Task 2
            [25, 22, 30]   # Task 3
        ]
        schedule = schedule_tasks(num_nodes, worker_resources, num_tasks, task_requirements, network_bandwidth, execution_times)
        self.validate_schedule(schedule, num_nodes, worker_resources, task_requirements, network_bandwidth, execution_times)
    
    def test_edge_case_deadline(self):
        # Test where deadlines are tight and transfer time is significant
        num_nodes = 2
        worker_resources = [
            (4, 8, 10),   # Node 0: has data
            (8, 16, 20)   # Node 1
        ]
        num_tasks = 2
        task_requirements = [
            (2, 4, 5, 5, 16),  # Deadline is tight; if scheduled on node 1, transfer time = 5/1 = 5, plus exec time must be <= 16.
            (1, 2, 3, 3, 15)
        ]
        # Bandwidth: assume low bandwidth from node 0 to node 1
        network_bandwidth = [
            [1e9, 1],
            [1, 1e9]
        ]
        execution_times = [
            [10, 9],   # Task 0: 10 sec on node 0, 9 sec on node 1 (but transfer penalty if node is 1: 5 sec, total 14)
            [7, 6]     # Task 1: similar evaluation, total time on node 1 would be 6+3=9
        ]
        schedule = schedule_tasks(num_nodes, worker_resources, num_tasks, task_requirements, network_bandwidth, execution_times)
        self.validate_schedule(schedule, num_nodes, worker_resources, task_requirements, network_bandwidth, execution_times)

    def test_infeasible_task(self):
        # Test a scenario where one task cannot be scheduled on any node due to resource constraints.
        # The expected behavior is that the scheduler either raises an exception or returns an invalid schedule.
        num_nodes = 2
        worker_resources = [
            (4, 8, 10),  # Node 0
            (4, 8, 10)   # Node 1
        ]
        num_tasks = 1
        task_requirements = [
            (5, 4, 5, 1, 20)  # CPU requirement exceeds available resources on both nodes
        ]
        network_bandwidth = [
            [1e9, 10],
            [10, 1e9]
        ]
        execution_times = [
            [10, 12]
        ]
        # Expecting the scheduler to handle infeasible tasks.
        with self.assertRaises(Exception):
            schedule_tasks(num_nodes, worker_resources, num_tasks, task_requirements, network_bandwidth, execution_times)

if __name__ == '__main__':
    unittest.main()