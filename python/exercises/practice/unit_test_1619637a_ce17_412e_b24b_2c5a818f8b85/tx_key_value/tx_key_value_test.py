import unittest
import threading
import time
from tx_key_value import DistributedKeyValueStore

class TestDistributedKeyValueStore(unittest.TestCase):
    def setUp(self):
        self.store = DistributedKeyValueStore()

    def test_basic_get_put(self):
        self.assertIsNone(self.store.get("key1"))
        
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        self.store.put("key1", "updated_value")
        self.assertEqual(self.store.get("key1"), "updated_value")

    def test_transaction_isolation(self):
        # Set up initial state
        self.store.put("key1", "initial_value")
        
        # Start a transaction and modify a value
        tx_id = self.store.begin_transaction()
        self.store.transactional_put(tx_id, "key1", "tx_value")
        
        # Transaction should see its own changes
        self.assertEqual(self.store.transactional_get(tx_id, "key1"), "tx_value")
        
        # Non-transactional get should still see initial value
        self.assertEqual(self.store.get("key1"), "initial_value")
        
        # Commit the transaction
        self.assertTrue(self.store.commit_transaction(tx_id))
        
        # Now the non-transactional get should see the new value
        self.assertEqual(self.store.get("key1"), "tx_value")

    def test_transaction_abort(self):
        # Set up initial state
        self.store.put("key1", "initial_value")
        
        # Start a transaction and modify a value
        tx_id = self.store.begin_transaction()
        self.store.transactional_put(tx_id, "key1", "tx_value")
        
        # Abort the transaction
        self.store.abort_transaction(tx_id)
        
        # Value should remain unchanged
        self.assertEqual(self.store.get("key1"), "initial_value")
        
        # Transaction should no longer be valid after abort
        with self.assertRaises(Exception):
            self.store.transactional_get(tx_id, "key1")

    def test_multiple_transactions(self):
        self.store.put("shared_key", "initial")
        
        # Create two concurrent transactions
        tx1_id = self.store.begin_transaction()
        tx2_id = self.store.begin_transaction()
        
        # Each transaction makes its own updates
        self.store.transactional_put(tx1_id, "shared_key", "tx1_value")
        self.store.transactional_put(tx2_id, "shared_key", "tx2_value")
        
        # Each transaction sees its own updates
        self.assertEqual(self.store.transactional_get(tx1_id, "shared_key"), "tx1_value")
        self.assertEqual(self.store.transactional_get(tx2_id, "shared_key"), "tx2_value")
        
        # Non-transactional get still sees the initial value
        self.assertEqual(self.store.get("shared_key"), "initial")
        
        # Commit transaction 1
        self.assertTrue(self.store.commit_transaction(tx1_id))
        
        # Now the non-transactional get should see tx1's value
        self.assertEqual(self.store.get("shared_key"), "tx1_value")
        
        # Transaction 2 should still see its own updates
        self.assertEqual(self.store.transactional_get(tx2_id, "shared_key"), "tx2_value")
        
        # Commit transaction 2
        self.assertTrue(self.store.commit_transaction(tx2_id))
        
        # Now the non-transactional get should see tx2's value (last commit wins)
        self.assertEqual(self.store.get("shared_key"), "tx2_value")

    def test_global_abort(self):
        global_abort = True
        self.store.put("key", "original")
        
        # Start a transaction
        tx_id = self.store.begin_transaction()
        self.store.transactional_put(tx_id, "key", "new_value")
        
        # Try to commit with global_abort=True
        # We need to modify the store to check this flag
        setattr(self.store, "global_abort", global_abort)
        
        # Should fail to commit
        self.assertFalse(self.store.commit_transaction(tx_id))
        
        # Value should remain unchanged
        self.assertEqual(self.store.get("key"), "original")

    def test_concurrent_transactions(self):
        self.store.put("counter", "0")
        
        def increment_counter(iterations):
            for _ in range(iterations):
                tx_id = self.store.begin_transaction()
                current = self.store.transactional_get(tx_id, "counter")
                new_val = str(int(current) + 1)
                self.store.transactional_put(tx_id, "counter", new_val)
                self.assertTrue(self.store.commit_transaction(tx_id))
        
        # Create multiple threads to increment the counter concurrently
        threads = []
        num_threads = 5
        iterations_per_thread = 20
        
        for _ in range(num_threads):
            t = threading.Thread(target=increment_counter, args=(iterations_per_thread,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check final counter value
        self.assertEqual(self.store.get("counter"), str(num_threads * iterations_per_thread))

    def test_transaction_on_nonexistent_key(self):
        # Start a transaction for a key that doesn't exist
        tx_id = self.store.begin_transaction()
        
        # Should return None for a nonexistent key
        self.assertIsNone(self.store.transactional_get(tx_id, "nonexistent_key"))
        
        # Create the key in the transaction
        self.store.transactional_put(tx_id, "nonexistent_key", "new_value")
        self.assertEqual(self.store.transactional_get(tx_id, "nonexistent_key"), "new_value")
        
        # Non-transactional get should still not see the key
        self.assertIsNone(self.store.get("nonexistent_key"))
        
        # Commit and verify
        self.assertTrue(self.store.commit_transaction(tx_id))
        self.assertEqual(self.store.get("nonexistent_key"), "new_value")

    def test_multiple_keys_in_transaction(self):
        tx_id = self.store.begin_transaction()
        
        self.store.transactional_put(tx_id, "key1", "value1")
        self.store.transactional_put(tx_id, "key2", "value2")
        self.store.transactional_put(tx_id, "key3", "value3")
        
        self.assertEqual(self.store.transactional_get(tx_id, "key1"), "value1")
        self.assertEqual(self.store.transactional_get(tx_id, "key2"), "value2")
        self.assertEqual(self.store.transactional_get(tx_id, "key3"), "value3")
        
        # Before commit, nothing should be visible
        self.assertIsNone(self.store.get("key1"))
        self.assertIsNone(self.store.get("key2"))
        self.assertIsNone(self.store.get("key3"))
        
        # Commit and verify atomicity
        self.assertTrue(self.store.commit_transaction(tx_id))
        
        # All keys should now be visible
        self.assertEqual(self.store.get("key1"), "value1")
        self.assertEqual(self.store.get("key2"), "value2")
        self.assertEqual(self.store.get("key3"), "value3")

    def test_invalid_transaction_id(self):
        # Attempting operations with an invalid transaction ID should raise exceptions
        with self.assertRaises(Exception):
            self.store.transactional_get(999, "key")
            
        with self.assertRaises(Exception):
            self.store.transactional_put(999, "key", "value")
            
        with self.assertRaises(Exception):
            self.store.commit_transaction(999)
            
        with self.assertRaises(Exception):
            self.store.abort_transaction(999)

    def test_read_performance_during_transactions(self):
        # Populate the store with some data
        for i in range(1000):
            self.store.put(f"key{i}", f"value{i}")
        
        # Start a transaction and modify half of the keys
        tx_id = self.store.begin_transaction()
        for i in range(0, 1000, 2):
            self.store.transactional_put(tx_id, f"key{i}", f"tx_value{i}")
        
        # Measure read time outside the transaction
        start_time = time.time()
        for i in range(1000):
            self.store.get(f"key{i}")
        non_tx_read_time = time.time() - start_time
        
        # Transaction reads should be reasonably performant compared to non-transactional reads
        # This is a basic check - specific performance requirements would depend on the implementation
        self.assertLess(non_tx_read_time, 1.0, "Non-transactional reads should be reasonably fast")

if __name__ == "__main__":
    unittest.main()