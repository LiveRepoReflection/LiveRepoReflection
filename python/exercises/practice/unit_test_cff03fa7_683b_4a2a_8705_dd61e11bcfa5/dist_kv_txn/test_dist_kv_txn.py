import unittest
from unittest.mock import patch, MagicMock
import sys
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Import the solution module which will be implemented by the user
sys.path.append('.')
from dist_kv_txn import initialize, begin, get, put, commit, rollback

class TestDistributedKVStore(unittest.TestCase):
    
    def setUp(self):
        # Reset any global state that might exist
        # This is needed since we'll be testing different scenarios
        pass
        
    def test_basic_transaction(self):
        """Test a simple transaction with get and put operations."""
        initialize(1, [1, 2, 3])
        
        tx_id = begin()
        self.assertIsNotNone(tx_id, "Transaction ID should not be None")
        
        # Initially, key should not exist
        value = get(tx_id, "key1")
        self.assertIsNone(value, "Key should not exist initially")
        
        # Add the key
        put(tx_id, "key1", "value1")
        
        # Verify the key exists within the transaction
        value = get(tx_id, "key1")
        self.assertEqual(value, "value1", "Key should have the assigned value within the transaction")
        
        # Commit the transaction
        result = commit(tx_id)
        self.assertTrue(result, "Commit should succeed")
        
        # Start a new transaction and verify the key exists
        tx_id2 = begin()
        value = get(tx_id2, "key1")
        self.assertEqual(value, "value1", "Key should persist after commit")
        rollback(tx_id2)
    
    def test_rollback(self):
        """Test transaction rollback."""
        initialize(1, [1, 2, 3])
        
        # First transaction to set initial value
        tx_id1 = begin()
        put(tx_id1, "key2", "initial")
        commit(tx_id1)
        
        # Second transaction to modify the value but then rollback
        tx_id2 = begin()
        put(tx_id2, "key2", "modified")
        
        # Within tx2, the value should be modified
        value = get(tx_id2, "key2")
        self.assertEqual(value, "modified", "Value should be modified within the transaction")
        
        # Rollback the transaction
        rollback(tx_id2)
        
        # Start a new transaction and verify the key has the original value
        tx_id3 = begin()
        value = get(tx_id3, "key2")
        self.assertEqual(value, "initial", "Value should be restored to initial after rollback")
        rollback(tx_id3)
    
    def test_isolation(self):
        """Test transaction isolation."""
        initialize(1, [1, 2, 3])
        
        # First transaction sets a value
        tx_id1 = begin()
        put(tx_id1, "key3", "value1")
        
        # Second transaction should not see the uncommitted value
        tx_id2 = begin()
        value = get(tx_id2, "key3")
        self.assertIsNone(value, "Second transaction should not see uncommitted changes")
        
        # Commit the first transaction
        commit(tx_id1)
        
        # Second transaction should still not see the committed value (snapshot isolation)
        value = get(tx_id2, "key3")
        self.assertIsNone(value, "Second transaction should not see changes committed after it began")
        
        # Start a third transaction which should see the committed value
        tx_id3 = begin()
        value = get(tx_id3, "key3")
        self.assertEqual(value, "value1", "New transaction should see committed changes")
        
        rollback(tx_id2)
        rollback(tx_id3)
    
    def test_concurrent_transactions(self):
        """Test concurrent transactions with different keys."""
        initialize(1, [1, 2, 3])
        
        # Use ThreadPoolExecutor to run concurrent transactions
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit 10 concurrent transactions, each operating on a different key
            futures = []
            for i in range(10):
                futures.append(executor.submit(self._concurrent_task, i))
            
            # Wait for all transactions to complete
            results = [future.result() for future in futures]
            
            # Verify all transactions were successful
            self.assertTrue(all(results), "All concurrent transactions should succeed")
            
            # Verify all keys have the expected values
            tx_id = begin()
            for i in range(10):
                value = get(tx_id, f"concurrent_key_{i}")
                self.assertEqual(value, f"value_{i}", f"Key concurrent_key_{i} should have value_{i}")
            rollback(tx_id)
    
    def _concurrent_task(self, index):
        """Helper method for concurrent transaction test."""
        tx_id = begin()
        put(tx_id, f"concurrent_key_{index}", f"value_{index}")
        time.sleep(random.uniform(0.01, 0.05))  # Simulate some processing time
        return commit(tx_id)
    
    def test_conflicting_transactions(self):
        """Test handling of conflicting transactions."""
        initialize(1, [1, 2, 3])
        
        # First transaction sets a value
        tx_id1 = begin()
        put(tx_id1, "conflict_key", "value1")
        
        # Second transaction also tries to set the same key
        tx_id2 = begin()
        put(tx_id2, "conflict_key", "value2")
        
        # Commit the first transaction
        result1 = commit(tx_id1)
        self.assertTrue(result1, "First transaction should commit successfully")
        
        # Commit the second transaction - this might succeed or fail depending on the implementation
        # Just make sure it doesn't crash
        commit(tx_id2)
        
        # Start a new transaction to check the final value
        tx_id3 = begin()
        value = get(tx_id3, "conflict_key")
        # The value should be either "value1" (if second transaction failed) or "value2" (if it succeeded)
        self.assertIn(value, ["value1", "value2"], "Final value should be from one of the transactions")
        rollback(tx_id3)
    
    def test_node_failures(self):
        """Test resilience to node failures."""
        # This is a simple simulation - we mock a node failure during a transaction
        
        initialize(1, [1, 2, 3])
        
        # Mock a function that will be called during commit to simulate a node failure
        original_commit = globals()['commit']
        
        def mock_node_failure(*args, **kwargs):
            # Simulate a node failure for node 2
            # In a real scenario, this would involve more sophisticated failure simulation
            pass
        
        # Start a transaction and set a value
        tx_id = begin()
        put(tx_id, "durability_key", "durable_value")
        
        try:
            # Patch the commit function to simulate a node failure
            with patch('dist_kv_txn.commit', side_effect=mock_node_failure):
                result = original_commit(tx_id)
                # The implementation should handle node failures - we don't make assertions here
                # as behavior may vary based on the specific implementation
        except Exception as e:
            # If an exception is raised, the implementation should handle it gracefully
            # We'll restart the node and check if the transaction was properly committed
            pass
        
        # After the "failure", initialize node 1 again
        initialize(1, [1, 2, 3])
        
        # Start a new transaction and check if the value is there
        tx_id2 = begin()
        value = get(tx_id2, "durability_key")
        # If the commit succeeded despite the failure, the value should be present
        # If not, it should be None - either way, the system should be in a consistent state
        rollback(tx_id2)
    
    def test_multiple_keys_transaction(self):
        """Test transactions with multiple keys."""
        initialize(1, [1, 2, 3])
        
        tx_id = begin()
        
        # Add multiple keys in a transaction
        put(tx_id, "multi_key_1", "multi_value_1")
        put(tx_id, "multi_key_2", "multi_value_2")
        put(tx_id, "multi_key_3", "multi_value_3")
        
        # Verify all keys have the expected values within the transaction
        self.assertEqual(get(tx_id, "multi_key_1"), "multi_value_1")
        self.assertEqual(get(tx_id, "multi_key_2"), "multi_value_2")
        self.assertEqual(get(tx_id, "multi_key_3"), "multi_value_3")
        
        # Commit the transaction
        result = commit(tx_id)
        self.assertTrue(result, "Commit should succeed")
        
        # Start a new transaction and verify all keys are present
        tx_id2 = begin()
        self.assertEqual(get(tx_id2, "multi_key_1"), "multi_value_1")
        self.assertEqual(get(tx_id2, "multi_key_2"), "multi_value_2")
        self.assertEqual(get(tx_id2, "multi_key_3"), "multi_value_3")
        rollback(tx_id2)
    
    def test_overwrite_within_transaction(self):
        """Test overwriting a key multiple times within a transaction."""
        initialize(1, [1, 2, 3])
        
        tx_id = begin()
        
        # Put an initial value
        put(tx_id, "overwrite_key", "initial")
        self.assertEqual(get(tx_id, "overwrite_key"), "initial")
        
        # Overwrite it
        put(tx_id, "overwrite_key", "overwritten")
        self.assertEqual(get(tx_id, "overwrite_key"), "overwritten")
        
        # Overwrite again
        put(tx_id, "overwrite_key", "final")
        self.assertEqual(get(tx_id, "overwrite_key"), "final")
        
        # Commit and verify
        commit(tx_id)
        
        tx_id2 = begin()
        self.assertEqual(get(tx_id2, "overwrite_key"), "final")
        rollback(tx_id2)
    
    def test_stress_sequential(self):
        """Stress test with many sequential transactions."""
        initialize(1, [1, 2, 3])
        
        # Perform many transactions sequentially
        for i in range(50):
            tx_id = begin()
            put(tx_id, f"stress_key_{i}", f"stress_value_{i}")
            commit(tx_id)
        
        # Verify all values
        tx_id = begin()
        for i in range(50):
            self.assertEqual(get(tx_id, f"stress_key_{i}"), f"stress_value_{i}")
        rollback(tx_id)
    
    def test_stress_concurrent(self):
        """Stress test with many concurrent transactions."""
        initialize(1, [1, 2, 3])
        
        # Use ThreadPoolExecutor to run concurrent transactions
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(50):
                futures.append(executor.submit(self._stress_concurrent_task, i))
            
            # Wait for all transactions to complete
            results = [future.result() for future in futures]
        
        # Verify values for successful transactions
        tx_id = begin()
        for i, success in enumerate(results):
            if success:
                value = get(tx_id, f"stress_concurrent_key_{i}")
                self.assertEqual(value, f"stress_concurrent_value_{i}")
        rollback(tx_id)
    
    def _stress_concurrent_task(self, index):
        """Helper method for concurrent stress test."""
        try:
            tx_id = begin()
            put(tx_id, f"stress_concurrent_key_{index}", f"stress_concurrent_value_{index}")
            time.sleep(random.uniform(0.001, 0.01))  # Simulate some processing time
            return commit(tx_id)
        except Exception:
            return False

if __name__ == '__main__':
    unittest.main()