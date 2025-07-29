import unittest
from resource_scheduler import schedule_tasks

class TestResourceScheduler(unittest.TestCase):

    def test_no_tasks(self):
        # No tasks provided, should return 0.
        tasks = []
        machines = [10, 20]
        result = schedule_tasks(0, len(machines), tasks, machines)
        self.assertEqual(result, 0)

    def test_single_machine_single_task_fits(self):
        # Single task that fits in the machine's resource capacity.
        tasks = [(5, 5)]  # (resource requirement, deadline)
        machines = [10]
        result = schedule_tasks(1, 1, tasks, machines)
        self.assertEqual(result, 1)

    def test_single_machine_single_task_does_not_fit(self):
        # Single task that does not fit in the machine's resource capacity.
        tasks = [(15, 5)]
        machines = [10]
        result = schedule_tasks(1, 1, tasks, machines)
        self.assertEqual(result, 0)

    def test_multiple_tasks_single_machine(self):
        # Multiple tasks on a single machine.
        # Tasks: each task takes one time unit.
        # Machine can execute tasks in different time slots,
        # and the resource capacity must be enough for the task in the slot it is scheduled.
        tasks = [(5, 1), (5, 2), (5, 2), (5, 3)]
        machines = [10]
        # Optimal scheduling example:
        # Slot 1: schedule one task with deadline 1 and one task with deadline 2 (total resource usage 5+5 = 10)
        # Slot 2: schedule remaining task with deadline 2 (5)
        # Slot 3: schedule task with deadline 3 (5)
        # Total tasks scheduled = 4
        result = schedule_tasks(4, 1, tasks, machines)
        self.assertEqual(result, 4)

    def test_multiple_machines(self):
        # Multiple machines allow parallel execution in the same time slot.
        tasks = [(4, 2), (6, 2), (8, 3), (3, 3)]
        machines = [7, 10]
        # Example optimal scheduling:
        # Time Slot 1: On machine1, schedule task (4,2) and on machine2, schedule task (6,2)
        # Time Slot 2: On machine1, schedule task (3,3) and on machine2, schedule task (8,3)
        # All tasks are scheduled before their deadlines.
        result = schedule_tasks(4, 2, tasks, machines)
        self.assertEqual(result, 4)

    def test_high_resource_tasks(self):
        # Some tasks require resources that exceed any machine capacity.
        tasks = [(50, 5), (200, 5), (30, 5)]
        machines = [100, 150]
        # The task with a resource requirement of 200 cannot be scheduled.
        # Only two tasks can be scheduled.
        result = schedule_tasks(3, 2, tasks, machines)
        self.assertEqual(result, 2)

    def test_tasks_with_early_deadlines(self):
        # Tasks have early deadlines forcing scheduling decisions.
        tasks = [(10, 1), (20, 1), (5, 2), (15, 2)]
        machines = [25, 25]
        # Optimal scheduling over different time slots:
        # Time slot 1: Both machines must handle tasks with deadline 1.
        # Time slot 2: Remaining tasks with deadline 2 can be scheduled.
        # All four tasks can be scheduled.
        result = schedule_tasks(4, 2, tasks, machines)
        self.assertEqual(result, 4)

    def test_tight_deadlines(self):
        # Tasks with very tight deadlines.
        tasks = [(5, 1), (5, 1), (5, 2), (5, 2)]
        machines = [10, 10]
        # At time slot 1, the two tasks with deadline 1 must be scheduled on separate machines.
        # At time slot 2, the tasks with deadline 2 can then be scheduled.
        result = schedule_tasks(4, 2, tasks, machines)
        self.assertEqual(result, 4)

if __name__ == '__main__':
    unittest.main()