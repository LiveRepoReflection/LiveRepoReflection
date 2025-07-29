import unittest
from task_assign_optimal import assign_tasks, calculate_runtime

class TestOptimalTaskAssignment(unittest.TestCase):
    def test_single_task_single_machine(self):
        # Single task with a single machine scenario.
        cpu_req = [2]
        mem_req = [4]
        io_req = [5]
        deadline = [50]
        estimated_runtime = [30]
        cpu_capacity = [4]
        mem_capacity = [8]
        io_speed = [1.0]
        overload_penalty = 2

        assignment = assign_tasks(cpu_req, mem_req, io_req, deadline, estimated_runtime,
                                  cpu_capacity, mem_capacity, io_speed, overload_penalty)
        # There is only one machine available.
        self.assertEqual(len(assignment), 1)
        self.assertEqual(assignment[0], 0)

    def test_multiple_tasks_multiple_machines(self):
        # Multiple tasks distributed across two machines.
        cpu_req = [2, 4, 1, 3]
        mem_req = [4, 8, 2, 6]
        io_req = [10, 5, 1, 7]
        deadline = [100, 200, 50, 120]
        estimated_runtime = [50, 100, 25, 80]
        cpu_capacity = [4, 8]
        mem_capacity = [8, 16]
        io_speed = [1.0, 2.0]
        overload_penalty = 2

        assignment = assign_tasks(cpu_req, mem_req, io_req, deadline, estimated_runtime,
                                  cpu_capacity, mem_capacity, io_speed, overload_penalty)
        self.assertEqual(len(assignment), 4)
        # Ensure each task is assigned to a valid machine index.
        for machine in assignment:
            self.assertTrue(0 <= machine < len(cpu_capacity))

    def test_overloaded_machine(self):
        # Scenario where tasks force the machine to be overloaded,
        # thus incurring penalty on estimated runtimes.
        cpu_req = [4, 4, 1]
        mem_req = [8, 8, 2]
        io_req = [10, 10, 1]
        deadline = [100, 100, 30]
        estimated_runtime = [40, 40, 20]
        cpu_capacity = [6]
        mem_capacity = [10]
        io_speed = [1.0]
        overload_penalty = 3

        assignment = assign_tasks(cpu_req, mem_req, io_req, deadline, estimated_runtime,
                                  cpu_capacity, mem_capacity, io_speed, overload_penalty)
        self.assertEqual(len(assignment), 3)
        # Only one machine exists, so every task must be assigned to machine 0.
        for machine in assignment:
            self.assertEqual(machine, 0)

    def test_tie_breaking_resource_usage(self):
        # Testing tie-breaking mechanism: In cases where multiple valid assignments exist,
        # the chosen assignment should minimize total resource usage. Due to multiple valid
        # solutions, we only check that each task is assigned to a valid machine.
        cpu_req = [1, 1, 1, 2]
        mem_req = [2, 2, 2, 4]
        io_req = [5, 2, 1, 3]
        deadline = [30, 30, 30, 50]
        estimated_runtime = [20, 25, 15, 40]
        cpu_capacity = [4, 4]
        mem_capacity = [8, 8]
        io_speed = [1.0, 1.5]
        overload_penalty = 2

        assignment = assign_tasks(cpu_req, mem_req, io_req, deadline, estimated_runtime,
                                  cpu_capacity, mem_capacity, io_speed, overload_penalty)
        self.assertEqual(len(assignment), 4)
        for machine in assignment:
            self.assertTrue(0 <= machine < len(cpu_capacity))

    def test_all_tasks_assigned(self):
        # Even when tasks cannot be completed before deadlines,
        # all tasks must be assigned to a machine.
        cpu_req = [10, 12, 8]
        mem_req = [20, 16, 15]
        io_req = [5, 5, 2]
        deadline = [30, 40, 25]
        estimated_runtime = [50, 60, 40]
        cpu_capacity = [8]
        mem_capacity = [16]
        io_speed = [1.0]
        overload_penalty = 2

        assignment = assign_tasks(cpu_req, mem_req, io_req, deadline, estimated_runtime,
                                  cpu_capacity, mem_capacity, io_speed, overload_penalty)
        self.assertEqual(len(assignment), 3)
        # Only one machine available so every task must be assigned to machine 0.
        for machine in assignment:
            self.assertEqual(machine, 0)

if __name__ == '__main__':
    unittest.main()