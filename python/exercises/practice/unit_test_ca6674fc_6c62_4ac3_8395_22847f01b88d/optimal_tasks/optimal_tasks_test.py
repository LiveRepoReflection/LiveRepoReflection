import unittest
from optimal_tasks import minimum_cost

class TestOptimalTasks(unittest.TestCase):
    def test_single_task_feasible(self):
        N = 1
        cost = [5]
        deadline = [10]
        dependencies = [[]]
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), 5)

    def test_single_task_infeasible(self):
        N = 1
        cost = [15]
        deadline = [10]
        dependencies = [[]]
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), -1)

    def test_multiple_tasks_no_dependencies(self):
        # Three tasks with no dependencies. Only tasks that can be scheduled alone count.
        N = 3
        cost = [5, 3, 4]
        deadline = [10, 2, 4]  # Task1: cost 3 but deadline 2 (infeasible if done alone); Task2: feasible exactly.
        dependencies = [[], [], []]
        # Valid tasks individually: task0 (5<=10) and task2 (4<=4). Minimum cost subset is {task2} with cost 4.
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), 4)

    def test_dependency_chain_basic(self):
        # Based on a chain: task0 -> task1 -> task2 -> task3 but only some subsets are feasible.
        N = 4
        cost = [5, 3, 8, 4]
        deadline = [10, 12, 15, 20]
        dependencies = [
            [],     # Task 0 has no dependency.
            [0],    # Task 1 depends on task 0.
            [0, 1], # Task 2 depends on tasks 0 and 1.
            [2]     # Task 3 depends on task 2.
        ]
        # Feasible subsets:
        # {0} -> cost=5 (finish at 5<=10)
        # {0,1} -> cost=8 (finish times: 5, 8 <= 10,12)
        # {0,1,2} -> cost=16, but task2 finishes at 16 >15, so infeasible.
        # {0,1,2,3} is also infeasible.
        # Minimum cost valid nonempty subset is {0} with cost 5.
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), 5)

    def test_cycle_detection(self):
        # Create a cycle: 0->1, 1->2, 2->0.
        N = 3
        cost = [3, 4, 5]
        deadline = [10, 10, 10]
        dependencies = [
            [1],  # Task 0 depends on task 1.
            [2],  # Task 1 depends on task 2.
            [0]   # Task 2 depends on task 0.
        ]
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), -1)

    def test_chain_with_tight_deadlines(self):
        # Chain: 0 -> 1 -> 2 -> 3 with deadlines exactly at cumulative times.
        N = 4
        cost = [3, 4, 5, 2]
        deadline = [3, 7, 13, 16]
        dependencies = [
            [],      # Task 0
            [0],     # Task 1
            [0, 1],  # Task 2
            [2]      # Task 3
        ]
        # Valid subsets:
        # {0} cost=3, finishing at 3 <= 3.
        # {0,1} cost=7, finishing times: 3 and 7.
        # {0,1,2} -> finish time = 3+4+5 = 12 <= 13, cost=12.
        # {0,1,2,3} -> finish time = 3+4+5+2 = 14 <= 16, cost=14.
        # Optimal is {0} with cost 3.
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), 3)

    def test_multiple_independent_chains(self):
        # Five tasks with two independent chains.
        N = 5
        cost = [10, 1, 2, 5, 3]
        deadline = [10, 2, 5, 8, 4]
        dependencies = [
            [],   # Task 0 independent (chain A)
            [],   # Task 1 independent (chain B)
            [1],  # Task 2 depends on Task 1 (chain B)
            [0],  # Task 3 depends on Task 0 (chain A)
            []    # Task 4 independent
        ]
        # Evaluate individual feasibility:
        # Task0: cost 10, deadline 10 -> valid.
        # Task1: cost 1, deadline 2 -> valid.
        # Task2: chain {1,2}: times: 1 then 3 (3>5 is ok? 3<=5) -> valid, total cost=3.
        # Task3: chain {0,3}: times: 10 then 15 (15 >8 invalid).
        # Task4: cost 3, deadline 4 -> valid if done alone.
        # Minimum cost valid subset among nonempty ones: {1} cost=1.
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), 1)

    def test_independent_task_exact_deadline(self):
        # Three tasks with one dependency and one independent.
        N = 3
        cost = [2, 2, 2]
        deadline = [2, 4, 6]
        dependencies = [
            [],    # Task 0
            [0],   # Task 1
            []     # Task 2 independent
        ]
        # Valid subsets:
        # {0} is valid (time 2<=2) cost=2.
        # {0,1} is valid (time: 2 then 4<= deadlines 2 and 4), cost=4.
        # {2} is valid (2<=6) cost=2.
        # Minimum cost is 2.
        self.assertEqual(minimum_cost(N, cost, deadline, dependencies), 2)

if __name__ == '__main__':
    unittest.main()