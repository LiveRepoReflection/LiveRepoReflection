import unittest
from task_lateness.task_lateness import compute_min_total_lateness

class TestTaskLateness(unittest.TestCase):
    def test_no_dependencies_all_on_time(self):
        # Simple tasks with no dependencies and tasks can all complete before deadlines.
        tasks = [
            {"id": 1, "duration": 2, "deadline": 5, "dependencies": []},
            {"id": 2, "duration": 3, "deadline": 10, "dependencies": []},
            {"id": 3, "duration": 1, "deadline": 4, "dependencies": []},
        ]
        # Optimal schedule: Task 3 (finish 1), Task 1 (finish 3), Task 2 (finish 6)
        # Lateness: 0, 0, 0 => total lateness = 0
        self.assertEqual(compute_min_total_lateness(tasks), 0)

    def test_chain_dependencies(self):
        # Tasks in a sequential dependency chain.
        tasks = [
            {"id": 1, "duration": 4, "deadline": 4, "dependencies": []},
            {"id": 2, "duration": 3, "deadline": 8, "dependencies": [1]},
            {"id": 3, "duration": 2, "deadline": 12, "dependencies": [2]},
        ]
        # Optimal schedule: 1 finishes at 4 (late=0), 2 finishes at 7 (late=0), 3 finishes at 9 (late=0)
        self.assertEqual(compute_min_total_lateness(tasks), 0)

    def test_branching_dependencies(self):
        # Tasks with branching dependencies.
        tasks = [
            {"id": 1, "duration": 3, "deadline": 5, "dependencies": []},
            {"id": 2, "duration": 2, "deadline": 6, "dependencies": [1]},
            {"id": 3, "duration": 4, "deadline": 10, "dependencies": [1]},
            {"id": 4, "duration": 1, "deadline": 7, "dependencies": [2, 3]},
        ]
        # One optimal schedule could be:
        # Task 1: finish at 3 (lateness 0)
        # Task 2: finish at 5 (lateness 0)
        # Task 3: finish at 9 (lateness 0)
        # Task 4: finish at 10 (lateness 3, as deadline=7)
        # Total lateness: 0+0+0+3 = 3
        self.assertEqual(compute_min_total_lateness(tasks), 3)

    def test_tasks_exceeding_deadlines(self):
        # Tasks that have deadlines that are not met
        tasks = [
            {"id": 1, "duration": 5, "deadline": 3, "dependencies": []},
            {"id": 2, "duration": 2, "deadline": 5, "dependencies": [1]},
            {"id": 3, "duration": 3, "deadline": 8, "dependencies": [2]},
        ]
        # Optimal schedule:
        # Task 1: finishes at 5 => lateness = 2
        # Task 2: finishes at 7 => lateness = 2
        # Task 3: finishes at 10 => lateness = 2
        # Total lateness: 2+2+2 = 6
        self.assertEqual(compute_min_total_lateness(tasks), 6)

    def test_complex_graph(self):
        # More complex dependency graph.
        tasks = [
            {"id": 1, "duration": 3, "deadline": 8, "dependencies": []},
            {"id": 2, "duration": 2, "deadline": 6, "dependencies": [1]},
            {"id": 3, "duration": 4, "deadline": 15, "dependencies": [1]},
            {"id": 4, "duration": 1, "deadline": 10, "dependencies": [2, 3]},
            {"id": 5, "duration": 2, "deadline": 12, "dependencies": [2]},
            {"id": 6, "duration": 3, "deadline": 18, "dependencies": [4, 5]},
        ]
        # The optimal schedule order and resulting lateness:
        # One potential schedule:
        # Task 1: finish at 3 (lateness=0)
        # Task 2: finish at 5 (lateness=0)
        # Task 5: finish at 7 (lateness=0)
        # Task 3: finish at 11 (lateness=0)
        # Task 4: finish at 12 (lateness=2, deadline=10)
        # Task 6: finish at 15 (lateness=0)
        # Total lateness: 0+0+0+0+2+0 = 2
        self.assertEqual(compute_min_total_lateness(tasks), 2)

    def test_independent_tasks_mixed_deadlines(self):
        # Independent tasks not connected by dependencies
        tasks = [
            {"id": 1, "duration": 4, "deadline": 3, "dependencies": []},
            {"id": 2, "duration": 3, "deadline": 4, "dependencies": []},
            {"id": 3, "duration": 2, "deadline": 10, "dependencies": []},
            {"id": 4, "duration": 5, "deadline": 8, "dependencies": []},
        ]
        # The optimal ordering should try to minimize total lateness.
        # One optimal schedule might be:
        # Task 2: finish at 3 (lateness=0)
        # Task 1: finish at 7 (lateness=4)
        # Task 4: finish at 12 (lateness=4)
        # Task 3: finish at 14 (lateness=4)
        # Total lateness: 0+4+4+4 = 12
        self.assertEqual(compute_min_total_lateness(tasks), 12)

if __name__ == '__main__':
    unittest.main()