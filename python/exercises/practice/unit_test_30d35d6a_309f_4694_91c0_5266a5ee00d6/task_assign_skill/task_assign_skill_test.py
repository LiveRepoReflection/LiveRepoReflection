import unittest
from task_assign_skill import min_completion_time

class TestTaskAssignSkill(unittest.TestCase):
    def test_basic_assignment(self):
        employees = [
            {"A", "B"},
            {"B", "C"}
        ]
        tasks = [
            ({"A"}, 5),
            ({"B"}, 10),
            ({"C"}, 7)
        ]
        dependencies = [
            (0, 1),
            (1, 2)
        ]
        n = len(employees)
        m = len(tasks)
        # Expected total completion time is 22 based on optimal sequential scheduling with dependencies.
        self.assertEqual(min_completion_time(employees, tasks, dependencies, n, m), 22)

    def test_impossible_assignment(self):
        employees = [
            {"A"},
            {"B"}
        ]
        tasks = [
            ({"A", "C"}, 5),  # No employee has both "A" and "C"
            ({"B"}, 8)
        ]
        dependencies = []
        n = len(employees)
        m = len(tasks)
        # Expected to return -1 because not all tasks can be assigned.
        self.assertEqual(min_completion_time(employees, tasks, dependencies, n, m), -1)

    def test_no_dependencies(self):
        employees = [
            {"A", "B"},
            {"B", "C"},
            {"A", "C"}
        ]
        tasks = [
            ({"A"}, 5),
            ({"B"}, 6),
            ({"C"}, 7)
        ]
        dependencies = []
        n = len(employees)
        m = len(tasks)
        # With no dependencies, all tasks can be assigned and the total time is the sum of task times.
        self.assertEqual(min_completion_time(employees, tasks, dependencies, n, m), 18)

    def test_multiple_dependencies(self):
        employees = [
            {"A", "B", "C"},
            {"B", "C"},
            {"A", "C"}
        ]
        tasks = [
            ({"A"}, 4),
            ({"B"}, 5),
            ({"C"}, 6),
            ({"A", "C"}, 7)
        ]
        dependencies = [
            (0, 2),  # Task 0 must be completed before task 2 can start
            (1, 3)   # Task 1 must be completed before task 3 can start
        ]
        n = len(employees)
        m = len(tasks)
        # Expected total time is 4 + 5 + 6 + 7 = 22
        self.assertEqual(min_completion_time(employees, tasks, dependencies, n, m), 22)

    def test_complex_dependencies(self):
        employees = [
            {"A", "B", "C", "D"},
            {"A", "C"},
            {"B", "D"},
            {"C", "D"}
        ]
        tasks = [
            ({"A"}, 3),
            ({"B"}, 5),
            ({"C"}, 4),
            ({"D"}, 6),
            ({"A", "D"}, 7)
        ]
        dependencies = [
            (0, 4),  # Task 0 must be completed before task 4
            (1, 2),  # Task 1 must be completed before task 2
            (2, 3)   # Task 2 must be completed before task 3
        ]
        n = len(employees)
        m = len(tasks)
        # Expected total time is 3 + 5 + 4 + 6 + 7 = 25
        self.assertEqual(min_completion_time(employees, tasks, dependencies, n, m), 25)

if __name__ == '__main__':
    unittest.main()