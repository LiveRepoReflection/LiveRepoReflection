import unittest
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import random

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        # Import here to avoid circular imports
        from kv_snapshot import DistributedKVStore
        self.store = DistributedKVStore(num_nodes=3)

    def test_basic_transaction(self):
        txn_id = self.store.begin_transaction()
        self.store.write(txn_id, "key1", b"value1")
        self.assertEqual(self.store.read(txn_id, "key1"), b"value1")
        self.assertTrue(self.store.commit_transaction(txn_id))

    def test_snapshot_isolation(self):
        # Start first transaction
        txn1 = self.store.begin_transaction()
        self.store.write(txn1, "key1", b"value1")
        
        # Start second transaction before first commits
        txn2 = self.store.begin_transaction()
        
        # First transaction commits
        self.assertTrue(self.store.commit_transaction(txn1))
        
        # Second transaction shouldn't see the committed value
        self.assertIsNone(self.store.read(txn2, "key1"))
        
        # Start third transaction after first commits
        txn3 = self.store.begin_transaction()
        
        # Third transaction should see the committed value
        self.assertEqual(self.store.read(txn3, "key1"), b"value1")

    def test_write_write_conflict(self):
        txn1 = self.store.begin_transaction()
        txn2 = self.store.begin_transaction()
        
        self.store.write(txn1, "key1", b"value1")
        self.store.write(txn2, "key1", b"value2")
        
        self.assertTrue(self.store.commit_transaction(txn1))
        self.assertFalse(self.store.commit_transaction(txn2))

    def test_abort_transaction(self):
        txn_id = self.store.begin_transaction()
        self.store.write(txn_id, "key1", b"value1")
        self.store.abort_transaction(txn_id)
        
        # Start new transaction and verify the write was not committed
        new_txn = self.store.begin_transaction()
        self.assertIsNone(self.store.read(new_txn, "key1"))

    def test_multiple_keys_atomic(self):
        txn_id = self.store.begin_transaction()
        self.store.write(txn_id, "key1", b"value1")
        self.store.write(txn_id, "key2", b"value2")
        self.store.write(txn_id, "key3", b"value3")
        self.assertTrue(self.store.commit_transaction(txn_id))
        
        read_txn = self.store.begin_transaction()
        self.assertEqual(self.store.read(read_txn, "key1"), b"value1")
        self.assertEqual(self.store.read(read_txn, "key2"), b"value2")
        self.assertEqual(self.store.read(read_txn, "key3"), b"value3")

    def test_concurrent_transactions(self):
        def run_transaction(key, value):
            txn_id = self.store.begin_transaction()
            self.store.write(txn_id, key, value)
            return self.store.commit_transaction(txn_id)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(100):
                key = f"key{i}"
                value = f"value{i}".encode()
                futures.append(executor.submit(run_transaction, key, value))
            
            results = [f.result() for f in futures]
            self.assertEqual(sum(results), 100)  # All transactions should succeed

    def test_read_nonexistent_key(self):
        txn_id = self.store.begin_transaction()
        self.assertIsNone(self.store.read(txn_id, "nonexistent_key"))

    def test_commit_already_committed(self):
        txn_id = self.store.begin_transaction()
        self.store.write(txn_id, "key1", b"value1")
        self.assertTrue(self.store.commit_transaction(txn_id))
        with self.assertRaises(ValueError):
            self.store.commit_transaction(txn_id)

    def test_node_failure_simulation(self):
        # Write data
        txn1 = self.store.begin_transaction()
        self.store.write(txn1, "key1", b"value1")
        self.assertTrue(self.store.commit_transaction(txn1))
        
        # Simulate node failure by forcing a node to restart
        self.store.simulate_node_failure(0)  # Restart node 0
        
        # Verify data is still accessible
        txn2 = self.store.begin_transaction()
        self.assertEqual(self.store.read(txn2, "key1"), b"value1")

    def test_concurrent_reads_and_writes(self):
        def random_operation():
            txn_id = self.store.begin_transaction()
            op_type = random.choice(["read", "write"])
            key = f"key{random.randint(1, 10)}"
            
            if op_type == "read":
                self.store.read(txn_id, key)
            else:
                self.store.write(txn_id, key, str(random.randint(1, 1000)).encode())
            
            return self.store.commit_transaction(txn_id)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(random_operation) for _ in range(100)]
            _ = [f.result() for f in futures]

    def test_large_values(self):
        large_value = b"x" * 1000000  # 1MB value
        txn_id = self.store.begin_transaction()
        self.store.write(txn_id, "large_key", large_value)
        self.assertTrue(self.store.commit_transaction(txn_id))
        
        read_txn = self.store.begin_transaction()
        self.assertEqual(self.store.read(read_txn, "large_key"), large_value)

if __name__ == '__main__':
    unittest.main()