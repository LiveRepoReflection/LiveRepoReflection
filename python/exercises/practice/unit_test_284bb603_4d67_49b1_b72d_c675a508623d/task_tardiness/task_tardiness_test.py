import unittest
from task_tardiness import compute_min_tardiness

class TaskTardinessTest(unittest.TestCase):

    def test_no_tardiness(self):
        tasks = [
            {"id": 0, "duration": 5, "deadline": 10, "dependencies": []},
            {"id": 1, "duration": 3, "deadline": 8, "dependencies": [0]},
            {"id": 2, "duration": 7, "deadline": 15, "dependencies": [1]},
            {"id": 3, "duration": 2, "deadline": 20, "dependencies": []}
        ]
        # Expected schedule:
        # Task 0: start 0, finish 5 (deadline 10, tardiness 0)
        # Task 3: start 0, finish 2 (deadline 20, tardiness 0)
        # Task 1: start 5, finish 8 (deadline 8, tardiness 0)
        # Task 2: start 8, finish 15 (deadline 15, tardiness 0)
        self.assertEqual(compute_min_tardiness(tasks), 0)

    def test_single_task_tardiness(self):
        tasks = [
            {"id": 0, "duration": 10, "deadline": 5, "dependencies": []}
        ]
        # Only one task, tardiness = 10 - 5 = 5.
        self.assertEqual(compute_min_tardiness(tasks), 5)
    
    def test_parallel_independent_tasks(self):
        tasks = [
            {"id": 0, "duration": 5, "deadline": 3, "dependencies": []},
            {"id": 1, "duration": 3, "deadline": 5, "dependencies": []}
        ]
        # Both can start at time 0 concurrently.
        # Task 0 finishes at 5, tardiness = 5 - 3 = 2.
        # Task 1 finishes at 3, tardiness = 0.
        # Total tardiness = 2.
        self.assertEqual(compute_min_tardiness(tasks), 2)
    
    def test_complex_dependency_chain(self):
        tasks = [
            {"id": 0, "duration": 3, "deadline": 4, "dependencies": []},
            {"id": 1, "duration": 2, "deadline": 5, "dependencies": [0]},
            {"id": 2, "duration": 1, "deadline": 3, "dependencies": [0]},
            {"id": 3, "duration": 4, "deadline": 10, "dependencies": [1, 2]},
            {"id": 4, "duration": 2, "deadline": 7, "dependencies": [2]}
        ]
        # One possible optimal schedule:
        # Task 0 starts at 0, finishes at 3.
        # Tasks 1 and 2 can both start at 3.
        #     Task 1 finishes at 5 (deadline 5, tardiness = 0).
        #     Task 2 finishes at 4 (deadline 3, tardiness = 1).
        # Task 3 can start after both task 1 and 2 finish, so at 5, finishes at 9 (deadline 10, tardiness = 0).
        # Task 4 can start after task 2 finishes, so at 4, finishes at 6 (deadline 7, tardiness = 0).
        # Total tardiness = 1.
        self.assertEqual(compute_min_tardiness(tasks), 1)
    
    def test_multiple_independent_chains(self):
        tasks = [
            # Chain A
            {"id": 0, "duration": 4, "deadline": 7, "dependencies": []},
            {"id": 1, "duration": 3, "deadline": 10, "dependencies": [0]},
            # Chain B
            {"id": 2, "duration": 2, "deadline": 3, "dependencies": []},
            {"id": 3, "duration": 5, "deadline": 9, "dependencies": [2]},
            # Independent task
            {"id": 4, "duration": 6, "deadline": 8, "dependencies": []}
        ]
        # Optimal scheduling (executed concurrently):
        # Chain A:
        # Task 0: start at 0, finish at 4 (tardiness = 0, 4-7=0)
        # Task 1: start at 4, finish at 7 (tardiness = 0, 7-10=0)
        # Chain B:
        # Task 2: start at 0, finish at 2 (tardiness = 0, 2-3=0)
        # Task 3: start at 2, finish at 7 (tardiness = 0, 7-9=0)
        # Independent task:
        # Task 4: start at 0, finish at 6 (tardiness = 6-8=0)
        # Total tardiness = 0.
        self.assertEqual(compute_min_tardiness(tasks), 0)

if __name__ == '__main__':
    unittest.main()