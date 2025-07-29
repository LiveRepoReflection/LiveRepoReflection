import unittest
import threading
import time
from tx_snapshot import DistributedTransactionManager

class TestDistributedTransactionManager(unittest.TestCase):
    def setUp(self):
        self.dtm = DistributedTransactionManager(num_shards=5)
    
    def test_basic_transaction(self):
        # Start a transaction
        tid = self.dtm.begin_transaction()
        
        # Write to a shard
        self.dtm.write(tid, 0, "key1", "value1")
        
        # Commit the transaction
        self.assertTrue(self.dtm.commit_transaction(tid))
        
        # Start a new transaction to read the value
        tid2 = self.dtm.begin_transaction()
        self.assertEqual(self.dtm.read(tid2, 0, "key1"), "value1")
        self.dtm.commit_transaction(tid2)

    def test_snapshot_isolation(self):
        # Transaction 1: Write key1=value1
        tid1 = self.dtm.begin_transaction()
        self.dtm.write(tid1, 0, "key1", "value1")
        self.assertTrue(self.dtm.commit_transaction(tid1))
        
        # Transaction 2: Begin, will see key1=value1
        tid2 = self.dtm.begin_transaction()
        self.assertEqual(self.dtm.read(tid2, 0, "key1"), "value1")
        
        # Transaction 3: Change key1=value2
        tid3 = self.dtm.begin_transaction()
        self.dtm.write(tid3, 0, "key1", "value2")
        self.assertTrue(self.dtm.commit_transaction(tid3))
        
        # Transaction 2 should still see key1=value1 (snapshot isolation)
        self.assertEqual(self.dtm.read(tid2, 0, "key1"), "value1")
        
        # Transaction 4 should see key1=value2
        tid4 = self.dtm.begin_transaction()
        self.assertEqual(self.dtm.read(tid4, 0, "key1"), "value2")
        self.dtm.commit_transaction(tid4)
        
        # Commit transaction 2
        self.dtm.commit_transaction(tid2)

    def test_rollback(self):
        # Start a transaction
        tid = self.dtm.begin_transaction()
        
        # Write to a shard
        self.dtm.write(tid, 0, "key1", "value1")
        
        # Rollback the transaction
        self.dtm.rollback_transaction(tid)
        
        # Start a new transaction to check the value doesn't exist
        tid2 = self.dtm.begin_transaction()
        self.assertIsNone(self.dtm.read(tid2, 0, "key1"))
        self.dtm.commit_transaction(tid2)

    def test_write_conflict(self):
        # Transaction 1: Write key1=value1
        tid1 = self.dtm.begin_transaction()
        self.dtm.write(tid1, 0, "key1", "value1")
        
        # Transaction 2: Write key1=value2
        tid2 = self.dtm.begin_transaction()
        self.dtm.write(tid2, 0, "key1", "value2")
        
        # Commit transaction 1
        self.assertTrue(self.dtm.commit_transaction(tid1))
        
        # Try to commit transaction 2, should fail due to write conflict
        self.assertFalse(self.dtm.commit_transaction(tid2))
        
        # Verify key1 still has value1
        tid3 = self.dtm.begin_transaction()
        self.assertEqual(self.dtm.read(tid3, 0, "key1"), "value1")
        self.dtm.commit_transaction(tid3)

    def test_multiple_shards(self):
        # Start a transaction
        tid = self.dtm.begin_transaction()
        
        # Write to multiple shards
        self.dtm.write(tid, 0, "key1", "value1")
        self.dtm.write(tid, 1, "key2", "value2")
        self.dtm.write(tid, 2, "key3", "value3")
        
        # Commit the transaction
        self.assertTrue(self.dtm.commit_transaction(tid))
        
        # Start a new transaction to read the values
        tid2 = self.dtm.begin_transaction()
        self.assertEqual(self.dtm.read(tid2, 0, "key1"), "value1")
        self.assertEqual(self.dtm.read(tid2, 1, "key2"), "value2")
        self.assertEqual(self.dtm.read(tid2, 2, "key3"), "value3")
        self.dtm.commit_transaction(tid2)

    def test_multiple_writes_same_key(self):
        # Start a transaction
        tid = self.dtm.begin_transaction()
        
        # Write to same key multiple times
        self.dtm.write(tid, 0, "key1", "value1")
        self.dtm.write(tid, 0, "key1", "value2")
        self.dtm.write(tid, 0, "key1", "value3")
        
        # Commit the transaction
        self.assertTrue(self.dtm.commit_transaction(tid))
        
        # Start a new transaction to read the value
        tid2 = self.dtm.begin_transaction()
        self.assertEqual(self.dtm.read(tid2, 0, "key1"), "value3")
        self.dtm.commit_transaction(tid2)

    def test_delete_key(self):
        # Start a transaction to create a key
        tid1 = self.dtm.begin_transaction()
        self.dtm.write(tid1, 0, "key1", "value1")
        self.assertTrue(self.dtm.commit_transaction(tid1))
        
        # Start a transaction to delete the key
        tid2 = self.dtm.begin_transaction()
        self.dtm.write(tid2, 0, "key1", None)
        self.assertTrue(self.dtm.commit_transaction(tid2))
        
        # Start a new transaction to verify key doesn't exist
        tid3 = self.dtm.begin_transaction()
        self.assertIsNone(self.dtm.read(tid3, 0, "key1"))
        self.dtm.commit_transaction(tid3)

    def test_concurrent_transactions(self):
        # Define a worker function that creates and commits a transaction
        def worker(shard_id, key, value):
            tid = self.dtm.begin_transaction()
            self.dtm.write(tid, shard_id, key, value)
            return self.dtm.commit_transaction(tid)
        
        # Create 10 threads to concurrently update different keys
        threads = []
        for i in range(10):
            shard_id = i % 5
            thread = threading.Thread(target=worker, args=(shard_id, f"key{i}", f"value{i}"))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all keys were written correctly
        tid = self.dtm.begin_transaction()
        for i in range(10):
            shard_id = i % 5
            self.assertEqual(self.dtm.read(tid, shard_id, f"key{i}"), f"value{i}")
        self.dtm.commit_transaction(tid)

    def test_concurrent_write_conflicts(self):
        # Track commit results
        results = [None] * 10
        
        # Define a worker function that creates and commits a transaction
        def worker(thread_id):
            tid = self.dtm.begin_transaction()
            # All threads write to the same key
            self.dtm.write(tid, 0, "conflicted_key", f"value{thread_id}")
            # Sleep for a random time to increase chance of conflicts
            time.sleep(0.01 * (thread_id % 5))
            results[thread_id] = self.dtm.commit_transaction(tid)
        
        # Create 10 threads to concurrently update the same key
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify that at least one transaction committed successfully
        self.assertTrue(any(results))
        
        # Verify that at least one transaction failed due to write conflict
        self.assertTrue(not all(results))
        
        # Verify that the key has a value from one of the transactions
        tid = self.dtm.begin_transaction()
        value = self.dtm.read(tid, 0, "conflicted_key")
        self.assertIsNotNone(value)
        self.assertTrue(value.startswith("value"))
        self.dtm.commit_transaction(tid)

    def test_large_transaction(self):
        # Start a transaction
        tid = self.dtm.begin_transaction()
        
        # Write 100 keys across all shards
        for i in range(100):
            shard_id = i % 5
            self.dtm.write(tid, shard_id, f"large_key{i}", f"large_value{i}")
        
        # Commit the transaction
        self.assertTrue(self.dtm.commit_transaction(tid))
        
        # Start a new transaction to read the values
        tid2 = self.dtm.begin_transaction()
        for i in range(100):
            shard_id = i % 5
            self.assertEqual(self.dtm.read(tid2, shard_id, f"large_key{i}"), f"large_value{i}")
        self.dtm.commit_transaction(tid2)

    def test_long_running_transaction(self):
        # Start transaction 1
        tid1 = self.dtm.begin_transaction()
        
        # Write initial values
        self.dtm.write(tid1, 0, "long_key", "initial_value")
        
        # Start transaction 2 and commit changes
        tid2 = self.dtm.begin_transaction()
        self.dtm.write(tid2, 0, "long_key", "new_value")
        self.assertTrue(self.dtm.commit_transaction(tid2))
        
        # Transaction 1 should still see the initial state
        self.assertIsNone(self.dtm.read(tid1, 0, "long_key"))
        
        # Trying to commit transaction 1 should fail due to write conflict
        self.assertFalse(self.dtm.commit_transaction(tid1))

if __name__ == '__main__':
    unittest.main()