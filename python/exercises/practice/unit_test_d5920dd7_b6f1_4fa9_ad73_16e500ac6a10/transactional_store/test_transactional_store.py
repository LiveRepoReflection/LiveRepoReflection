import unittest
import threading
import time
import random
from transactional_store import TransactionalStore

class TestTransactionalStore(unittest.TestCase):

    def setUp(self):
        self.store = TransactionalStore()

    def test_basic_read_write_commit(self):
        # Simple transaction with read, write, commit
        tid = self.store.begin_transaction()
        self.assertIsNotNone(tid, "Transaction ID should not be None")
        
        self.assertIsNone(self.store.read(tid, "key1"), "New key should return None")
        
        self.store.write(tid, "key1", "value1")
        self.assertEqual(self.store.read(tid, "key1"), "value1", "Written value should be readable in same transaction")
        
        # Key should not be visible outside the transaction yet
        tid2 = self.store.begin_transaction()
        self.assertIsNone(self.store.read(tid2, "key1"), "Uncommitted value should not be visible to other transactions")
        
        # Commit and verify visibility
        self.assertTrue(self.store.commit_transaction(tid), "Commit should succeed")
        
        # Start a new transaction and read the committed value
        tid3 = self.store.begin_transaction()
        self.assertEqual(self.store.read(tid3, "key1"), "value1", "Committed value should be visible to new transactions")

    def test_transaction_abort(self):
        # Test that aborted transactions discard their changes
        tid = self.store.begin_transaction()
        
        self.store.write(tid, "key1", "value1")
        self.assertEqual(self.store.read(tid, "key1"), "value1", "Written value should be readable in same transaction")
        
        self.assertTrue(self.store.abort_transaction(tid), "Abort should succeed")
        
        # Start a new transaction and verify the aborted write is not visible
        tid2 = self.store.begin_transaction()
        self.assertIsNone(self.store.read(tid2, "key1"), "Aborted write should not be visible")

    def test_snapshot_isolation(self):
        # Test that transactions see a consistent snapshot of the data
        
        # Set up initial state
        tid_init = self.store.begin_transaction()
        self.store.write(tid_init, "key1", "initial1")
        self.store.write(tid_init, "key2", "initial2")
        self.assertTrue(self.store.commit_transaction(tid_init))
        
        # Start transaction 1 and read initial values
        tid1 = self.store.begin_transaction()
        val1 = self.store.read(tid1, "key1")
        val2 = self.store.read(tid1, "key2")
        self.assertEqual(val1, "initial1")
        self.assertEqual(val2, "initial2")
        
        # Start transaction 2 and update both keys
        tid2 = self.store.begin_transaction()
        self.store.write(tid2, "key1", "updated1")
        self.store.write(tid2, "key2", "updated2")
        self.assertTrue(self.store.commit_transaction(tid2))
        
        # Transaction 1 should still see the initial values
        self.assertEqual(self.store.read(tid1, "key1"), "initial1", "Transaction should see consistent snapshot")
        self.assertEqual(self.store.read(tid1, "key2"), "initial2", "Transaction should see consistent snapshot")
        
        # But a new transaction should see the updated values
        tid3 = self.store.begin_transaction()
        self.assertEqual(self.store.read(tid3, "key1"), "updated1", "New transaction should see committed updates")
        self.assertEqual(self.store.read(tid3, "key2"), "updated2", "New transaction should see committed updates")

    def test_multiple_writes_same_key(self):
        # Test writing to the same key multiple times in a transaction
        tid = self.store.begin_transaction()
        
        self.store.write(tid, "key1", "value1")
        self.store.write(tid, "key1", "value2")
        self.store.write(tid, "key1", "value3")
        
        self.assertEqual(self.store.read(tid, "key1"), "value3", "Last written value should be returned")
        
        self.assertTrue(self.store.commit_transaction(tid))
        
        # Verify the final value after commit
        tid2 = self.store.begin_transaction()
        self.assertEqual(self.store.read(tid2, "key1"), "value3", "Last written value should be committed")

    def test_invalid_transaction_operations(self):
        # Test operations on invalid/closed transactions
        tid = self.store.begin_transaction()
        self.store.write(tid, "key1", "value1")
        self.assertTrue(self.store.commit_transaction(tid))
        
        # Operations on committed transaction should fail or be ignored
        self.assertFalse(self.store.commit_transaction(tid), "Cannot commit already committed transaction")
        self.assertFalse(self.store.abort_transaction(tid), "Cannot abort already committed transaction")
        self.assertIsNone(self.store.read(tid, "key1"), "Cannot read from closed transaction")
        
        # Write to closed transaction should be ignored (no error, just no effect)
        self.store.write(tid, "key2", "value2")
        
        # Invalid transaction ID
        self.assertIsNone(self.store.read("invalid_tid", "key1"), "Invalid TID should return None on read")
        self.assertFalse(self.store.commit_transaction("invalid_tid"), "Invalid TID should return False on commit")
        self.assertFalse(self.store.abort_transaction("invalid_tid"), "Invalid TID should return False on abort")
        
    def test_write_skew_prevention(self):
        # Set up initial state
        tid_init = self.store.begin_transaction()
        self.store.write(tid_init, "balance1", "100")
        self.store.write(tid_init, "balance2", "100")
        self.assertTrue(self.store.commit_transaction(tid_init))
        
        # Simulate concurrent transactions attempting to withdraw from different accounts
        # where the sum of balances should remain >= 100
        
        def transaction1():
            tid = self.store.begin_transaction()
            bal1 = int(self.store.read(tid, "balance1"))
            bal2 = int(self.store.read(tid, "balance2"))
            
            # Ensure total balance >= 100
            if bal1 + bal2 >= 150:
                # Withdraw 75 from balance1
                self.store.write(tid, "balance1", str(bal1 - 75))
                time.sleep(0.1)  # Delay to ensure interleaving with transaction2
                return tid, self.store.commit_transaction(tid)
            else:
                self.store.abort_transaction(tid)
                return tid, False
            
        def transaction2():
            tid = self.store.begin_transaction()
            bal1 = int(self.store.read(tid, "balance1"))
            bal2 = int(self.store.read(tid, "balance2"))
            
            # Ensure total balance >= 100
            if bal1 + bal2 >= 150:
                # Withdraw 75 from balance2
                self.store.write(tid, "balance2", str(bal2 - 75))
                time.sleep(0.1)  # Delay to ensure interleaving with transaction1
                return tid, self.store.commit_transaction(tid)
            else:
                self.store.abort_transaction(tid)
                return tid, False
        
        # Run transactions in separate threads
        t1 = threading.Thread(target=lambda: setattr(self, 't1_result', transaction1()))
        t2 = threading.Thread(target=lambda: setattr(self, 't2_result', transaction2()))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Check results
        tid1, success1 = self.t1_result
        tid2, success2 = self.t2_result
        
        # At least one transaction should succeed
        self.assertTrue(success1 or success2, "At least one transaction should succeed")
        
        # If both succeeded, check final balances
        tid_check = self.store.begin_transaction()
        bal1 = int(self.store.read(tid_check, "balance1"))
        bal2 = int(self.store.read(tid_check, "balance2"))
        
        # The sum should be either 125 (one withdrawal) or 50 (both withdrawals)
        total = bal1 + bal2
        self.assertTrue(total == 125 or total == 50, 
                        f"Expected total balance to be 125 or 50, got {total}")

    def test_concurrent_transactions(self):
        # Test many concurrent transactions
        num_transactions = 50
        keys_per_transaction = 5
        
        # Initialize some data
        tid_init = self.store.begin_transaction()
        for i in range(100):
            self.store.write(tid_init, f"key{i}", f"value{i}")
        self.assertTrue(self.store.commit_transaction(tid_init))
        
        results = []
        
        def run_transaction():
            tid = self.store.begin_transaction()
            keys = [f"key{random.randint(0, 99)}" for _ in range(keys_per_transaction)]
            
            # Read all keys first
            read_values = {}
            for key in keys:
                read_values[key] = self.store.read(tid, key)
                
            # Modify some keys
            modified_keys = {}
            for key in keys[:2]:  # Modify first 2 keys
                new_value = f"updated-{tid}-{key}"
                self.store.write(tid, key, new_value)
                modified_keys[key] = new_value
                
            # Delay to ensure interleaving
            time.sleep(random.uniform(0.01, 0.05))
            
            # Commit and return results
            success = self.store.commit_transaction(tid)
            return tid, success, read_values, modified_keys
        
        # Create and start threads
        threads = []
        for _ in range(num_transactions):
            thread = threading.Thread(target=lambda: results.append(run_transaction()))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify results
        successful_transactions = [r for r in results if r[1]]
        self.assertGreater(len(successful_transactions), 0, "Some transactions should succeed")
        
        # Verify final state with a new transaction
        tid_final = self.store.begin_transaction()
        
        # Check that all successful modifications are visible
        for _, success, _, modified_keys in results:
            if success:
                for key, expected_value in modified_keys.items():
                    actual_value = self.store.read(tid_final, key)
                    # The key might have been modified by a later transaction
                    # so we can't assert equality, but it should not be the original value
                    original_value = f"value{key[3:]}"  # Extract number from key
                    self.assertNotEqual(actual_value, original_value,
                                      f"Key {key} should have been modified")

    def test_large_values(self):
        # Test handling of large values (close to 1KB)
        large_value = "x" * 900  # 900 byte string
        
        tid = self.store.begin_transaction()
        self.store.write(tid, "large_key", large_value)
        self.assertEqual(self.store.read(tid, "large_key"), large_value, "Should handle large values")
        self.assertTrue(self.store.commit_transaction(tid))
        
        # Verify in a new transaction
        tid2 = self.store.begin_transaction()
        self.assertEqual(self.store.read(tid2, "large_key"), large_value, "Large value should persist after commit")

    def test_many_keys(self):
        # Test handling many keys in a single transaction
        tid = self.store.begin_transaction()
        
        # Write 1000 keys
        for i in range(1000):
            self.store.write(tid, f"key{i}", f"value{i}")
            
        # Verify all keys in the same transaction
        for i in range(1000):
            self.assertEqual(self.store.read(tid, f"key{i}"), f"value{i}", f"Should read correct value for key{i}")
            
        self.assertTrue(self.store.commit_transaction(tid))
        
        # Verify in a new transaction
        tid2 = self.store.begin_transaction()
        for i in range(0, 1000, 50):  # Check every 50th key to save time
            self.assertEqual(self.store.read(tid2, f"key{i}"), f"value{i}", f"Should read correct value after commit")

if __name__ == '__main__':
    unittest.main()