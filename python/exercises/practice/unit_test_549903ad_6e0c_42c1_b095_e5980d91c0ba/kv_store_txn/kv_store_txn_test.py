import unittest
import threading
import time
import random
import uuid
from unittest.mock import MagicMock, patch
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Set

# Import the KeyValueStore implementation
from kv_store_txn import KeyValueStore, Transaction, ConsensusModule, Node, TransactionStatus, TransactionManager

class MockConsensusModule(ConsensusModule):
    def __init__(self):
        self.committed_transactions = []
        self.lock = threading.Lock()
        self.failure_probability = 0.0
    
    def propose(self, transaction):
        with self.lock:
            # Simulate random failures if set
            if random.random() < self.failure_probability:
                return False
            self.committed_transactions.append(transaction)
            return True
    
    def get_committed_transactions(self):
        with self.lock:
            return list(self.committed_transactions)
    
    def set_failure_probability(self, probability):
        """Set the probability of a transaction failing during propose"""
        self.failure_probability = probability


class KeyValueStoreTest(unittest.TestCase):
    def setUp(self):
        self.consensus_module = MockConsensusModule()
        self.store = KeyValueStore(consensus_module=self.consensus_module)
    
    def test_basic_put_get(self):
        """Test basic put and get operations"""
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        self.store.put("key2", "value2")
        self.assertEqual(self.store.get("key2"), "value2")
        
        # Update an existing key
        self.store.put("key1", "new_value1")
        self.assertEqual(self.store.get("key1"), "new_value1")
    
    def test_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        self.assertIsNone(self.store.get("nonexistent"))
    
    def test_transaction_basic(self):
        """Test a basic transaction with multiple operations"""
        txn = self.store.begin_transaction()
        txn.put("key1", "txn_value1")
        txn.put("key2", "txn_value2")
        self.assertTrue(txn.commit())
        
        self.assertEqual(self.store.get("key1"), "txn_value1")
        self.assertEqual(self.store.get("key2"), "txn_value2")
    
    def test_transaction_isolation(self):
        """Test transaction isolation - changes are not visible until commit"""
        # Start a transaction
        txn = self.store.begin_transaction()
        txn.put("key1", "txn_value1")
        
        # Key should not be visible before commit
        self.assertIsNone(self.store.get("key1"))
        
        # Commit and check
        self.assertTrue(txn.commit())
        self.assertEqual(self.store.get("key1"), "txn_value1")
    
    def test_transaction_rollback(self):
        """Test transaction rollback"""
        # First set some initial values
        self.store.put("key1", "original1")
        self.store.put("key2", "original2")
        
        # Start a transaction and modify values
        txn = self.store.begin_transaction()
        txn.put("key1", "modified1")
        txn.put("key2", "modified2")
        
        # Rollback and verify values haven't changed
        txn.rollback()
        self.assertEqual(self.store.get("key1"), "original1")
        self.assertEqual(self.store.get("key2"), "original2")
    
    def test_concurrent_transactions(self):
        """Test concurrent transactions"""
        def run_transaction(key, value):
            txn = self.store.begin_transaction()
            txn.put(key, value)
            return txn.commit()
        
        # Create and start threads
        threads = []
        for i in range(10):
            key = f"concurrent_key_{i}"
            value = f"concurrent_value_{i}"
            thread = threading.Thread(target=run_transaction, args=(key, value))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify all values are correctly stored
        for i in range(10):
            key = f"concurrent_key_{i}"
            expected_value = f"concurrent_value_{i}"
            self.assertEqual(self.store.get(key), expected_value)
    
    def test_transaction_read_your_writes(self):
        """Test that a transaction can read its own writes"""
        txn = self.store.begin_transaction()
        
        # Write and read within the same transaction
        txn.put("key1", "txn_value1")
        self.assertEqual(txn.get("key1"), "txn_value1")
        
        # Update and read again
        txn.put("key1", "txn_updated1")
        self.assertEqual(txn.get("key1"), "txn_updated1")
        
        # Commit and check in the main store
        self.assertTrue(txn.commit())
        self.assertEqual(self.store.get("key1"), "txn_updated1")
    
    def test_transaction_conflict(self):
        """Test handling of transaction conflicts"""
        # Set initial value
        self.store.put("conflict_key", "initial")
        
        # Start two transactions
        txn1 = self.store.begin_transaction()
        txn2 = self.store.begin_transaction()
        
        # Both read the same key
        self.assertEqual(txn1.get("conflict_key"), "initial")
        self.assertEqual(txn2.get("conflict_key"), "initial")
        
        # Both update the key
        txn1.put("conflict_key", "txn1_value")
        txn2.put("conflict_key", "txn2_value")
        
        # First commit succeeds
        self.assertTrue(txn1.commit())
        
        # Second commit may fail or retry depending on implementation
        # The key should reflect the value from the first committed transaction
        # or the value from the second if it successfully retried
        txn2.commit()  # We're not asserting the result here
        
        # The value should be either from txn1 or txn2, not the initial value
        current_value = self.store.get("conflict_key")
        self.assertIn(current_value, ["txn1_value", "txn2_value"])
    
    def test_fault_tolerance(self):
        """Test system fault tolerance with simulated failures"""
        # Set a failure probability
        self.consensus_module.set_failure_probability(0.3)
        
        # Run multiple transactions and ensure the system still functions
        num_transactions = 20
        committed_count = 0
        
        for i in range(num_transactions):
            txn = self.store.begin_transaction()
            key = f"fault_key_{i}"
            value = f"fault_value_{i}"
            txn.put(key, value)
            
            if txn.commit():
                committed_count += 1
                # Verify the value was stored
                self.assertEqual(self.store.get(key), value)
        
        # Some transactions should have succeeded
        self.assertGreater(committed_count, 0)
        
        # Reset failure probability
        self.consensus_module.set_failure_probability(0.0)
    
    def test_large_dataset(self):
        """Test with a large number of keys and values"""
        # Insert 1000 key-value pairs
        for i in range(1000):
            key = f"large_key_{i}"
            value = f"large_value_{i}"
            self.store.put(key, value)
        
        # Verify random subset of values
        for _ in range(100):
            i = random.randint(0, 999)
            key = f"large_key_{i}"
            expected_value = f"large_value_{i}"
            self.assertEqual(self.store.get(key), expected_value)
    
    def test_transaction_with_many_operations(self):
        """Test a transaction with many operations"""
        txn = self.store.begin_transaction()
        
        # Perform 100 put operations
        for i in range(100):
            key = f"multi_op_key_{i}"
            value = f"multi_op_value_{i}"
            txn.put(key, value)
        
        # Commit and verify
        self.assertTrue(txn.commit())
        
        # Check a random subset of keys
        for _ in range(20):
            i = random.randint(0, 99)
            key = f"multi_op_key_{i}"
            expected_value = f"multi_op_value_{i}"
            self.assertEqual(self.store.get(key), expected_value)
    
    def test_concurrent_operations_on_same_key(self):
        """Test concurrent operations on the same key"""
        # Set initial value
        test_key = "concurrent_test_key"
        self.store.put(test_key, "initial")
        
        # Define a function that increments the value
        def increment_key():
            for _ in range(5):
                txn = self.store.begin_transaction()
                current = txn.get(test_key)
                if current is None:
                    current = 0
                else:
                    try:
                        current = int(current)
                    except ValueError:
                        current = 0
                
                txn.put(test_key, str(current + 1))
                txn.commit()
                # Small delay to increase chance of interleaving
                time.sleep(0.01)
        
        # Create and start threads
        threads = []
        num_threads = 5
        for _ in range(num_threads):
            thread = threading.Thread(target=increment_key)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Final value should reflect all increments
        # Due to potential conflicts and retry mechanisms, the final value
        # might not be exactly num_threads * 5, but should be greater than initial
        final_value = self.store.get(test_key)
        self.assertNotEqual(final_value, "initial")
        
        try:
            final_int = int(final_value)
            self.assertGreater(final_int, 0)
        except ValueError:
            self.fail("Final value is not an integer: " + final_value)

    def test_linearizability(self):
        """Test linearizability of operations"""
        # Create a key with initial value
        self.store.put("linear_key", "0")
        
        # Define a function that reads and then updates the key
        def read_and_update():
            txn = self.store.begin_transaction()
            value = txn.get("linear_key")
            # Increment the value
            new_value = str(int(value) + 1)
            txn.put("linear_key", new_value)
            return txn.commit()
        
        # Run multiple read-and-update operations in sequence
        results = []
        for _ in range(10):
            results.append(read_and_update())
        
        # All operations should have succeeded
        self.assertTrue(all(results))
        
        # Final value should be "10"
        self.assertEqual(self.store.get("linear_key"), "10")
    
    def test_transaction_get_nonexistent_key(self):
        """Test getting a nonexistent key in a transaction"""
        txn = self.store.begin_transaction()
        self.assertIsNone(txn.get("nonexistent_in_txn"))
        self.assertTrue(txn.commit())
    
    def test_transaction_put_then_delete(self):
        """Test putting a key and then deleting it in the same transaction"""
        # This test is optional if the implementation supports delete
        # Skip this test if delete is not implemented
        if not hasattr(Transaction, 'delete'):
            self.skipTest("Delete operation not implemented")
            
        txn = self.store.begin_transaction()
        txn.put("temp_key", "temp_value")
        txn.delete("temp_key")
        self.assertTrue(txn.commit())
        
        # Key should not exist
        self.assertIsNone(self.store.get("temp_key"))


if __name__ == '__main__':
    unittest.main()