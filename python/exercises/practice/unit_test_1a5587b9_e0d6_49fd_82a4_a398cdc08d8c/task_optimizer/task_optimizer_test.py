import unittest
from task_optimizer import min_total_cost

class TaskOptimizerTest(unittest.TestCase):
    def test_no_dependencies(self):
        # No dependencies means tasks can be executed in any order.
        N = 5
        M = 3
        C = [10, 20, 30, 40, 50]
        Dependencies = []
        K = 0
        # Since there's no dependency restrictions, the total cost is simply the sum.
        expected = sum(C)
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_chain_dependencies(self):
        # A simple chain dependency: 0 -> 1 -> 2 -> 3
        N = 4
        M = 10
        C = [10, 20, 30, 40]
        Dependencies = [(0, 1), (1, 2), (2, 3)]
        # Removing one dependency edge might enable a more efficient order,
        # but the cost is still the sum of all task costs.
        K = 1
        expected = sum(C)
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_already_topologically_sorted(self):
        # Graph is a DAG and already in topological order.
        N = 6
        M = 3
        C = [5, 10, 15, 20, 25, 30]
        Dependencies = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)]
        K = 0
        expected = sum(C)
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_cycle_with_removal_possible(self):
        # Introduce a cycle which can be fixed by removing one dependency.
        # Cycle: 0 -> 1, 1 -> 2, 2 -> 0. Removing one edge can break the cycle.
        N = 3
        M = 2
        C = [10, 20, 30]
        Dependencies = [(0, 1), (1, 2), (2, 0)]
        K = 1
        expected = sum(C)
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_cycle_with_removal_impossible(self):
        # Cycle remains even after using all available removals.
        # Imagine a case where multiple cycles exist that cannot all be broken with given K removals.
        N = 4
        M = 2
        C = [10, 20, 30, 40]
        Dependencies = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 1)]
        # Even if we remove one dependency, a cycle will remain.
        K = 1
        expected = -1
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_complex_graph(self):
        # Create a more complex DAG with several independent parts and one potential cycle if removal is not optimal.
        N = 7
        M = 4
        C = [7, 3, 8, 2, 5, 10, 1]
        Dependencies = [
            (0, 1),
            (2, 1),
            (3, 2),
            (4, 2),
            (5, 3),
            (5, 4),
            (6, 5)
        ]
        # Even if we remove one edge, proper ordering exists.
        K = 2
        expected = sum(C)
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_single_task(self):
        # Test with only one task.
        N = 1
        M = 1
        C = [100]
        Dependencies = []
        K = 0
        expected = 100
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_dense_graph_with_sufficient_removals(self):
        # Test with a dense graph where every task depends on every other task that comes before it.
        N = 5
        M = 3
        C = [1, 2, 3, 4, 5]
        Dependencies = []
        # Generate a chain like dependency (dense dependency in topologically sorted sequence)
        for i in range(1, N):
            for j in range(i):
                Dependencies.append((i, j))
        # With sufficient edge removals, it is possible to remove blocking dependencies.
        K = len(Dependencies) // 2
        expected = sum(C)
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

    def test_insufficient_removals_dense_cycle(self):
        # Create a dense graph that inherently forms a cycle that cannot be fixed with given K.
        # Cycle: 0 -> 1, 1 -> 0 and additional dependencies to form dense interconnected components.
        N = 3
        M = 2
        C = [10, 20, 30]
        Dependencies = [(0, 1), (1, 0), (1, 2), (2, 1)]
        K = 0  # No removals allowed, cycle present.
        expected = -1
        result = min_total_cost(N, M, C, Dependencies, K)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()