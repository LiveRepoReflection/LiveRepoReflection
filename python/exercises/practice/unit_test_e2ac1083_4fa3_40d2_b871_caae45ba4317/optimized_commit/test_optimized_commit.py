import unittest
from optimized_commit import optimize_commit_protocol

class TestOptimizedCommit(unittest.TestCase):
    def test_single_node_always_commit(self):
        N = 1
        transactions = [(0, {0}, 1.0)]
        result = optimize_commit_protocol(N, transactions)
        self.assertAlmostEqual(result, 3.0)

    def test_single_node_always_abort(self):
        N = 1
        transactions = [(0, {0}, 0.0)]
        result = optimize_commit_protocol(N, transactions)
        self.assertAlmostEqual(result, 3.0)

    def test_two_nodes_high_commit_prob(self):
        N = 2
        transactions = [(0, {0, 1}, 0.9)]
        result = optimize_commit_protocol(N, transactions)
        self.assertAlmostEqual(result, 3.0)

    def test_multiple_transactions(self):
        N = 3
        transactions = [
            (0, {0, 1, 2}, 0.9),
            (1, {1, 2}, 0.5)
        ]
        result = optimize_commit_protocol(N, transactions)
        self.assertTrue(5.0 <= result <= 6.0)

    def test_large_network_low_probability(self):
        N = 100
        transactions = [(0, set(range(100)), 0.1)]
        result = optimize_commit_protocol(N, transactions)
        self.assertTrue(result < 30.0)

    def test_coordinator_only_transaction(self):
        N = 5
        transactions = [(2, {2}, 0.7)]
        result = optimize_commit_protocol(N, transactions)
        self.assertAlmostEqual(result, 3.0)

    def test_mixed_protocol_selection(self):
        N = 4
        transactions = [
            (0, {0, 1, 2, 3}, 0.8),
            (1, {1, 2}, 0.3),
            (2, {2, 3}, 0.6)
        ]
        result = optimize_commit_protocol(N, transactions)
        self.assertTrue(7.0 <= result <= 9.0)

    def test_edge_case_all_nodes(self):
        N = 10
        transactions = [(0, set(range(10)), 0.5)]
        result = optimize_commit_protocol(N, transactions)
        self.assertTrue(3.0 <= result <= 5.0)

if __name__ == '__main__':
    unittest.main()