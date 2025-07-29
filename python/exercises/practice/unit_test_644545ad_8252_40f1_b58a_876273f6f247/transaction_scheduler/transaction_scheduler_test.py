import unittest
from transaction_scheduler import schedule_transactions

class TransactionSchedulerTest(unittest.TestCase):
    def test_single_transaction_no_conflict(self):
        # A single transaction with multiple operations; no conflict should occur.
        transaction_logs = [
            [(1, 1, 'A', 'R', 1), (1, 1, 'B', 'W', 2), (1, 2, 'C', 'R', 3)]
        ]
        # With only one transaction, it should be committed.
        expected = [1]
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)

    def test_conflict_on_same_data(self):
        # Two transactions conflict on the same data item at the same node.
        # Transaction 1 writes to data item 'A' and Transaction 2 reads it.
        # According to conflict resolution, we choose the one that minimizes conflicts.
        transaction_logs = [
            [(1, 1, 'A', 'W', 1)],
            [(2, 1, 'A', 'R', 2)]
        ]
        # Assuming our scheduler prefers the earlier transaction, only transaction 1 is committed.
        expected = [1]
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)

    def test_multiple_transactions_conflict_resolution(self):
        # Test using a more complex log containing three transactions.
        # Transaction 1 has operations on nodes 1 and 2 with data items A, B, and C.
        # Transaction 2 conflicts with Transaction 1 on node 1 and node 2.
        # Transaction 3 conflicts with Transaction 1 on node 2 and Transaction 2 on node 1.
        transaction_logs = [
            [(1, 1, 'A', 'W', 1), (1, 2, 'B', 'R', 3), (1, 1, 'C', 'R', 5)],
            [(2, 1, 'A', 'R', 2), (2, 2, 'C', 'W', 4), (2, 1, 'D', 'W', 6)],
            [(3, 2, 'B', 'W', 7), (3, 1, 'C', 'W', 8)]
        ]
        # Expected result: Scheduler should resolve conflicts to maximize committed transactions.
        # One valid serializable schedule is to commit Transaction 1 and Transaction 3.
        expected = [1, 3]
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)

    def test_different_nodes_no_conflict(self):
        # Two transactions both access data item 'A', but on different nodes.
        # This should not be counted as a conflict.
        transaction_logs = [
            [(1, 1, 'A', 'R', 1), (1, 1, 'B', 'W', 2)],
            [(2, 2, 'A', 'W', 3), (2, 2, 'C', 'R', 4)]
        ]
        # Both transactions should be committed.
        expected = [1, 2]
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)

    def test_empty_transaction_logs(self):
        # When given an empty list of transaction logs, the scheduler should return an empty list.
        transaction_logs = []
        expected = []
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)
        
    def test_multiple_operations_same_transaction(self):
        # A transaction might have multiple operations on the same data item on the same node.
        # Internal operations within the same transaction do not cause conflicts.
        transaction_logs = [
            [(1, 1, 'A', 'R', 1), (1, 1, 'A', 'W', 2), (1, 1, 'A', 'R', 3)],
            [(2, 1, 'B', 'W', 1), (2, 1, 'B', 'R', 2)]
        ]
        # Both transactions should commit since self-conflicts inside a transaction are ignored.
        expected = [1, 2]
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)

    def test_tie_breaking_determinism(self):
        # Both transactions conflict with each other.
        # The scheduler should apply a deterministic tie-breaking strategy.
        transaction_logs = [
            [(1, 1, 'A', 'W', 1)],
            [(2, 1, 'A', 'W', 2)]
        ]
        # Assuming the scheduler prefers the transaction with the smallest TID when conflicts occur.
        expected = [1]
        result = schedule_transactions(transaction_logs)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()