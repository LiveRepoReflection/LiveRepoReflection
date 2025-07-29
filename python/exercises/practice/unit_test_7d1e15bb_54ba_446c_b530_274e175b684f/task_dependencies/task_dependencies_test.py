import unittest
from task_dependencies import minimum_cost

class TaskDependenciesTest(unittest.TestCase):
    def test_simple_chain(self):
        """Test a simple chain of dependencies."""
        N = 6
        K = 2
        C = [10, 20, 30, 40, 50, 60]
        dependencies = [[], [0], [0], [1, 2], [3], [4]]
        target_tasks = [5]
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), 210)

    def test_multiple_target_tasks(self):
        """Test with multiple target tasks."""
        N = 5
        K = 3
        C = [1, 2, 3, 4, 5]
        dependencies = [[], [0], [0], [1, 2], []]
        target_tasks = [3, 4]
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), 15)

    def test_independent_tasks(self):
        """Test with completely independent tasks."""
        N = 5
        K = 1
        C = [10, 20, 30, 40, 50]
        dependencies = [[], [], [], [], []]
        target_tasks = [1, 3]
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), 60)

    def test_single_task(self):
        """Test with a single task."""
        N = 1
        K = 1
        C = [100]
        dependencies = [[]]
        target_tasks = [0]
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), 100)

    def test_diamond_dependency(self):
        """Test with a diamond-shaped dependency structure."""
        N = 4
        K = 2
        C = [10, 20, 30, 40]
        dependencies = [[], [0], [0], [1, 2]]
        target_tasks = [3]
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), 100)

    def test_no_target_tasks(self):
        """Test with no target tasks (should return 0)."""
        N = 5
        K = 2
        C = [10, 20, 30, 40, 50]
        dependencies = [[], [0], [0], [1, 2], [3]]
        target_tasks = []
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), 0)

    def test_large_number_of_tasks(self):
        """Test with a larger number of tasks."""
        N = 100
        K = 10
        C = [i for i in range(N)]
        dependencies = [[] for _ in range(N)]
        # Create a linear dependency chain 0 <- 1 <- 2 <- ... <- 99
        for i in range(1, N):
            dependencies[i] = [i-1]
        target_tasks = [N-1]  # The last task
        expected_cost = sum(range(N))
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), expected_cost)

    def test_complex_dependency_graph(self):
        """Test with a more complex dependency graph."""
        N = 8
        K = 3
        C = [5, 10, 15, 20, 25, 30, 35, 40]
        dependencies = [
            [],        # 0
            [0],       # 1 depends on 0
            [0],       # 2 depends on 0
            [1, 2],    # 3 depends on 1 and 2
            [2],       # 4 depends on 2
            [3, 4],    # 5 depends on 3 and 4
            [4],       # 6 depends on 4
            [5, 6]     # 7 depends on 5 and 6
        ]
        target_tasks = [7]
        # To complete 7, we need 0, 1, 2, 3, 4, 5, 6, 7
        expected_cost = sum(C)
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), expected_cost)

    def test_overlapping_dependencies(self):
        """Test with overlapping dependencies for multiple target tasks."""
        N = 7
        K = 2
        C = [10, 20, 30, 40, 50, 60, 70]
        dependencies = [
            [],        # 0
            [0],       # 1 depends on 0
            [0],       # 2 depends on 0
            [1],       # 3 depends on 1
            [2],       # 4 depends on 2
            [3],       # 5 depends on 3
            [4]        # 6 depends on 4
        ]
        target_tasks = [5, 6]
        # To complete 5, we need 0, 1, 3, 5
        # To complete 6, we need 0, 2, 4, 6
        # Combined, we need 0, 1, 2, 3, 4, 5, 6
        expected_cost = sum(C)
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), expected_cost)

    def test_maximum_constraints(self):
        """Test with values close to the maximum constraints."""
        N = 1000  # Reduced from 100,000 for test time performance
        K = 100
        C = [i % 100000 for i in range(N)]
        dependencies = [[] for _ in range(N)]
        # Create a linear dependency chain for every 10th task
        for i in range(10, N, 10):
            dependencies[i] = [i-10]
        target_tasks = list(range(990, N, 10))  # Multiple target tasks
        
        # Calculate expected cost
        required_tasks = set()
        for task in target_tasks:
            current = task
            while current >= 0:
                required_tasks.add(current)
                if current >= 10:
                    current -= 10
                else:
                    break
        
        expected_cost = sum(C[task] for task in required_tasks)
        self.assertEqual(minimum_cost(N, K, C, dependencies, target_tasks), expected_cost)

if __name__ == '__main__':
    unittest.main()