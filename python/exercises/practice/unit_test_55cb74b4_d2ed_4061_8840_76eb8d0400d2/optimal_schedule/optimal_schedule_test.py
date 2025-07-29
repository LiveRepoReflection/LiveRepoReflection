import unittest
from optimal_schedule import schedule_tasks

class OptimalScheduleTest(unittest.TestCase):
    def test_example_case(self):
        n = 5
        k = 2
        deadlines = [2, 2, 3, 4, 4]
        affinities = [0, 1, 0, 1, 0]
        expected = 5
        self.assertEqual(schedule_tasks(n, k, deadlines, affinities), expected)

    def test_single_core_conflict(self):
        # All tasks on single core with deadlines that force a limit on scheduling.
        n = 3
        k = 1
        deadlines = [1, 1, 2]
        affinities = [0, 0, 0]
        # Only one task with deadline 1 can be scheduled at time 0
        # and the task with deadline 2 can be scheduled at time 1.
        expected = 2
        self.assertEqual(schedule_tasks(n, k, deadlines, affinities), expected)

    def test_multiple_cores_sequential(self):
        # Tasks can be scheduled on two cores independently.
        n = 4
        k = 2
        deadlines = [2, 2, 2, 2]
        affinities = [0, 0, 1, 1]
        # For each core, tasks can be scheduled at time slots 0 and 1.
        expected = 4
        self.assertEqual(schedule_tasks(n, k, deadlines, affinities), expected)

    def test_core_with_varied_deadlines(self):
        # More complex case with varied deadlines on different cores.
        n = 6
        k = 2
        deadlines = [1, 2, 2, 3, 3, 4]
        # Core 0 tasks: deadlines from indices 0,2,4 -> [1,2,3]
        #    Schedule: time 0 (task with deadline 1), time 1 (task with deadline 2), time 2 (task with deadline 3)
        # Core 1 tasks: deadlines from indices 1,3,5 -> [2,3,4]
        #    Schedule: time 0 (task with deadline 2), time 1 (task with deadline 3), time 2 (task with deadline 4)
        # Total scheduled tasks: 3 + 3 = 6
        affinities = [0, 1, 0, 1, 0, 1]
        expected = 6
        self.assertEqual(schedule_tasks(n, k, deadlines, affinities), expected)

    def test_mixed_affinity(self):
        # Case with three cores and uneven distribution of deadlines.
        n = 7
        k = 3
        deadlines = [3, 3, 3, 4, 4, 5, 5]
        affinities = [0, 0, 1, 1, 2, 2, 2]
        # Core 0: tasks with deadlines [3, 3] -> can schedule 2 tasks.
        # Core 1: tasks with deadlines [3, 4] -> can schedule 2 tasks.
        # Core 2: tasks with deadlines [4, 5, 5] -> can schedule 3 tasks.
        # Total expected = 2 + 2 + 3 = 7
        expected = 7
        self.assertEqual(schedule_tasks(n, k, deadlines, affinities), expected)

    def test_all_tasks_unschedulable(self):
        # Tasks with deadlines too tight to schedule more than a few.
        # For core 0, two tasks with deadline 1 can only schedule 1 task.
        n = 4
        k = 2
        deadlines = [1, 1, 2, 2]
        affinities = [0, 0, 1, 1]
        # Core 0: Only one task can be scheduled.
        # Core 1: For deadlines [2,2], at time 0 schedule one, time 1 schedule the other.
        expected = 1 + 2
        self.assertEqual(schedule_tasks(n, k, deadlines, affinities), expected)

if __name__ == '__main__':
    unittest.main()