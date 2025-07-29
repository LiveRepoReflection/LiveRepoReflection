import unittest
import random
from txn_commit_opt import optimize_commit_time

class TxnCommitOptTest(unittest.TestCase):
    def test_single_node(self):
        # Single node: expected time is simply the sum of prepare and commit times.
        N = 1
        prepare_time = [10]
        commit_time = [5]
        failure_probability = 0.0
        replication_factor = 1
        result = optimize_commit_time(N, prepare_time, commit_time, failure_probability, replication_factor)
        # Expected: 10 (prepare) + 5 (commit) = 15.0
        self.assertAlmostEqual(result, 15.0, places=2)

    def test_multiple_nodes_no_fail(self):
        # With no failures, the optimal strategy yields total time equal to
        # max(prepare_time) + max(commit_time) assuming full parallelism in commit phase.
        N = 3
        prepare_time = [10, 20, 15]
        commit_time = [8, 5, 10]
        failure_probability = 0.0
        replication_factor = 2
        result = optimize_commit_time(N, prepare_time, commit_time, failure_probability, replication_factor)
        # Expected: max(prepare_time)=20, max(commit_time)=10, total = 30.0
        self.assertAlmostEqual(result, 30.0, places=2)

    def test_multiple_nodes_with_fail_prob(self):
        # When there is a risk of failure, the expected time may increase due to the need for replication.
        # This test assumes the optimal scheduler accounts for failure probability and replication overhead.
        # Expected value here is a pre-computed target based on a reference solution.
        N = 4
        prepare_time = [12, 7, 9, 15]
        commit_time = [8, 6, 10, 5]
        failure_probability = 0.1
        replication_factor = 3
        result = optimize_commit_time(N, prepare_time, commit_time, failure_probability, replication_factor)
        # For this test input, assume the expected optimized time is 32.50.
        self.assertAlmostEqual(result, 32.50, places=2)

    def test_randomized_large_input(self):
        # Test a larger instance to ensure the algorithm performs within acceptable limits.
        N = 100
        random.seed(0)
        prepare_time = [random.randint(0, 100) for _ in range(N)]
        commit_time = [random.randint(0, 100) for _ in range(N)]
        failure_probability = 0.05
        replication_factor = 2
        result = optimize_commit_time(N, prepare_time, commit_time, failure_probability, replication_factor)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0.0)

if __name__ == '__main__':
    unittest.main()