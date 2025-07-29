import unittest
from collections import defaultdict
from quorum_assign import assign_quorums

class TestQuorumAssign(unittest.TestCase):
    def test_single_node(self):
        N = 1
        K = 1
        transactions = [1, 2, 3]
        result = assign_quorums(N, K, transactions)
        self.assertEqual(len(result), len(transactions))
        for trans_id, quorum in result:
            self.assertIn(trans_id, transactions)
            self.assertEqual(len(quorum), 1)
            for node in quorum:
                self.assertEqual(node, 0)

    def test_basic_case(self):
        N = 5
        K = 3
        transactions = [101, 102, 103, 104, 105]
        result = assign_quorums(N, K, transactions)
        self.assertEqual(len(result), len(transactions))
        for trans_id, quorum in result:
            # Check transaction exists
            self.assertIn(trans_id, transactions)
            # Ensure quorum length is exactly K
            self.assertEqual(len(quorum), K)
            # Ensure nodes in quorum are distinct
            self.assertEqual(len(set(quorum)), K)
            # Each node id must be in range [0, N-1]
            for node in quorum:
                self.assertTrue(0 <= node < N)

    def test_deterministic(self):
        N = 10
        K = 4
        transactions = list(range(100, 110))
        result1 = assign_quorums(N, K, transactions)
        result2 = assign_quorums(N, K, transactions)
        self.assertEqual(result1, result2)

    def test_load_balancing(self):
        # Test to check that the node usage is balanced across transactions
        N = 10
        K = 3
        transactions = list(range(50))
        result = assign_quorums(N, K, transactions)
        
        node_usage = defaultdict(int)
        for trans_id, quorum in result:
            for node in quorum:
                node_usage[node] += 1

        usage_values = list(node_usage.values())
        max_usage = max(usage_values)
        min_usage = min(usage_values)
        # Allowing a difference margin of 2 between most and least used nodes
        self.assertLessEqual(max_usage - min_usage, 2)

    def test_large_dataset(self):
        N = 50
        K = 5
        transactions = list(range(1000))
        result = assign_quorums(N, K, transactions)
        self.assertEqual(len(result), len(transactions))
        for trans_id, quorum in result:
            self.assertEqual(len(quorum), K)
            self.assertEqual(len(set(quorum)), K)
            for node in quorum:
                self.assertTrue(0 <= node < N)

if __name__ == '__main__':
    unittest.main()