import unittest
from distributed_tx import coordinate_transaction

class TestDistributedTransaction(unittest.TestCase):
    def setUp(self):
        self.transaction_id = 1
        self.server_mapping = {
            1: 1,  # Account 1 on Server 1
            2: 2,  # Account 2 on Server 2
            3: 1,  # Account 3 on Server 1
            4: 2   # Account 4 on Server 2
        }

    def test_successful_transaction(self):
        transfers = [(1, 2, 100), (3, 4, 50)]
        
        def mock_commit(tx_id, _):
            self.assertEqual(tx_id, self.transaction_id)
            return True
            
        def mock_rollback(tx_id, _):
            self.fail("Rollback should not be called for successful transaction")
            
        result = coordinate_transaction(
            self.transaction_id,
            transfers,
            self.server_mapping,
            mock_commit,
            mock_rollback
        )
        self.assertTrue(result)

    def test_failed_transaction(self):
        transfers = [(1, 2, 100), (3, 4, 50)]
        
        def mock_commit(tx_id, _):
            self.assertEqual(tx_id, self.transaction_id)
            return False
            
        rollback_called = False
        def mock_rollback(tx_id, _):
            nonlocal rollback_called
            self.assertEqual(tx_id, self.transaction_id)
            rollback_called = True
            return True
            
        result = coordinate_transaction(
            self.transaction_id,
            transfers,
            self.server_mapping,
            mock_commit,
            mock_rollback
        )
        self.assertFalse(result)
        self.assertTrue(rollback_called)

    def test_single_server_transaction(self):
        transfers = [(1, 3, 100)]  # Both accounts on Server 1
        
        def mock_commit(tx_id, _):
            self.assertEqual(tx_id, self.transaction_id)
            return True
            
        def mock_rollback(tx_id, _):
            self.fail("Rollback should not be called for successful transaction")
            
        result = coordinate_transaction(
            self.transaction_id,
            transfers,
            self.server_mapping,
            mock_commit,
            mock_rollback
        )
        self.assertTrue(result)

    def test_invalid_account(self):
        transfers = [(1, 99, 100)]  # Account 99 doesn't exist
        
        with self.assertRaises(KeyError):
            coordinate_transaction(
                self.transaction_id,
                transfers,
                self.server_mapping,
                lambda *_: True,
                lambda *_: True
            )

    def test_rollback_failure(self):
        transfers = [(1, 2, 100), (3, 4, 50)]
        
        def mock_commit(tx_id, _):
            return False
            
        def mock_rollback(tx_id, _):
            return False
            
        with self.assertRaises(RuntimeError):
            coordinate_transaction(
                self.transaction_id,
                transfers,
                self.server_mapping,
                mock_commit,
                mock_rollback
            )

    def test_empty_transaction(self):
        transfers = []
        
        result = coordinate_transaction(
            self.transaction_id,
            transfers,
            self.server_mapping,
            lambda *_: True,
            lambda *_: True
        )
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()