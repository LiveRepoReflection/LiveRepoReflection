import unittest
from shard_txns import process_transactions

class TestShardTransactions(unittest.TestCase):
    def test_empty_transaction_list(self):
        self.assertTrue(process_transactions([], 1))

    def test_empty_transaction(self):
        self.assertTrue(process_transactions([[]], 1))

    def test_single_successful_transaction(self):
        transactions = [[(0, "read", 0), (0, "write", 1)]]
        self.assertTrue(process_transactions(transactions, 1))

    def test_multiple_successful_transactions(self):
        transactions = [
            [(0, "read", 0), (0, "write", 1)],
            [(0, "read", 1), (0, "write", 2)],
            [(0, "read", 2), (0, "write", 3)]
        ]
        self.assertTrue(process_transactions(transactions, 1))

    def test_failed_read_transaction(self):
        transactions = [
            [(0, "read", 0), (0, "write", 1)],
            [(0, "read", 0), (0, "write", 2)]  # Should fail as value is 1, not 0
        ]
        self.assertFalse(process_transactions(transactions, 1))

    def test_multiple_shards_success(self):
        transactions = [
            [(0, "read", 0), (1, "read", 0), (0, "write", 1), (1, "write", 1)],
            [(0, "read", 1), (1, "read", 1), (0, "write", 2), (1, "write", 2)]
        ]
        self.assertTrue(process_transactions(transactions, 2))

    def test_multiple_shards_failure(self):
        transactions = [
            [(0, "read", 0), (1, "read", 0), (0, "write", 1), (1, "write", 1)],
            [(0, "read", 2), (1, "read", 1)]  # Should fail as shard 0 is 1, not 2
        ]
        self.assertFalse(process_transactions(transactions, 2))

    def test_multiple_reads_same_shard(self):
        transactions = [
            [(0, "read", 0), (0, "read", 0), (0, "write", 1)]
        ]
        self.assertTrue(process_transactions(transactions, 1))

    def test_multiple_writes_same_shard(self):
        transactions = [
            [(0, "read", 0), (0, "write", 1), (0, "write", 2)]
        ]
        self.assertTrue(process_transactions(transactions, 1))

    def test_invalid_shard_id(self):
        transactions = [[(2, "read", 0)]]
        self.assertFalse(process_transactions(transactions, 2))

    def test_negative_shard_id(self):
        transactions = [[(-1, "read", 0)]]
        self.assertFalse(process_transactions(transactions, 1))

    def test_invalid_operation_type(self):
        transactions = [[(0, "invalid", 0)]]
        self.assertFalse(process_transactions(transactions, 1))

    def test_complex_scenario(self):
        transactions = [
            [(0, "read", 0), (1, "read", 0), (2, "read", 0), 
             (0, "write", 1), (1, "write", 2), (2, "write", 3)],
            [(0, "read", 1), (1, "read", 2), (2, "read", 3),
             (0, "write", 4), (1, "write", 5), (2, "write", 6)],
            [(0, "read", 4), (1, "read", 5), (2, "read", 6),
             (0, "write", 7), (1, "write", 8), (2, "write", 9)]
        ]
        self.assertTrue(process_transactions(transactions, 3))

    def test_rollback_scenario(self):
        transactions = [
            [(0, "read", 0), (1, "write", 1)],
            [(0, "write", 2), (1, "read", 0)]  # Should fail and rollback
        ]
        self.assertFalse(process_transactions(transactions, 2))

    def test_read_only_transaction(self):
        transactions = [
            [(0, "read", 0), (1, "read", 0)]
        ]
        self.assertTrue(process_transactions(transactions, 2))

    def test_write_only_transaction(self):
        transactions = [
            [(0, "write", 1), (1, "write", 1)]
        ]
        self.assertTrue(process_transactions(transactions, 2))

if __name__ == '__main__':
    unittest.main()