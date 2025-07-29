import unittest
import time
import threading
from tx_kvstore import DistributedKVStore

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        # Initialize the distributed key-value store with 3 nodes
        self.store = DistributedKVStore(3)

    def test_basic_put_get_commit(self):
        tx_id = "tx1"
        self.store.put("key1", "value1", tx_id)
        # Before commit, another transaction should not see uncommitted changes
        self.assertIsNone(self.store.get("key1", "tx2"))
        self.store.commit(tx_id)
        # After commit, the value should be visible in new transactions
        res = self.store.get("key1", "tx3")
        self.assertEqual(res, "value1")

    def test_transaction_isolation(self):
        tx1 = "tx2"
        tx2 = "tx3"
        self.store.put("key2", "value_tx1", tx1)
        # Other transactions must not see uncommitted changes from tx1
        self.assertIsNone(self.store.get("key2", tx2))
        self.store.commit(tx1)
        self.assertEqual(self.store.get("key2", tx2), "value_tx1")

    def test_rollback(self):
        tx_id = "tx4"
        self.store.put("key3", "value3", tx_id)
        self.store.rollback(tx_id)
        # After rollback, the key should not exist
        self.assertIsNone(self.store.get("key3", "tx5"))

    def test_last_writer_wins(self):
        tx1 = "tx5"
        tx2 = "tx6"
        self.store.put("key4", "first_value", tx1)
        self.store.commit(tx1)
        self.store.put("key4", "second_value", tx2)
        # Introduce a delay to simulate proper timestamp ordering
        time.sleep(0.1)
        self.store.commit(tx2)
        # The last committed value should win
        self.assertEqual(self.store.get("key4", "tx7"), "second_value")

    def test_snapshot(self):
        tx1 = "tx7"
        tx2 = "tx8"
        self.store.put("key5", "value5", tx1)
        self.store.commit(tx1)
        snapshot_time = time.time()
        self.store.put("key6", "value6", tx2)
        self.store.commit(tx2)
        # Snapshot taken at snapshot_time should only include transactions committed before that time
        snapshot = self.store.snapshot(snapshot_time)
        self.assertIn("key5", snapshot)
        self.assertNotIn("key6", snapshot)

    def test_fault_tolerance_after_commit(self):
        tx_id = "tx9"
        self.store.put("key7", "value7", tx_id)
        self.store.commit(tx_id)
        # Simulate a node failure after commit; assume fail_node is supported
        self.store.fail_node(0)
        # Data should remain accessible despite node failure
        self.assertEqual(self.store.get("key7", "tx10"), "value7")
        # Recover the failed node; assume recover_node is supported
        self.store.recover_node(0)

    def test_concurrent_transactions(self):
        def transaction_put(tx_id, key, value):
            self.store.put(key, value, tx_id)
            time.sleep(0.05)
            self.store.commit(tx_id)

        threads = []
        for i in range(10):
            tx_id = f"tx_concurrent_{i}"
            t = threading.Thread(target=transaction_put, args=(tx_id, "key8", f"value_{i}"))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        # The final value of key8 should be one of the values from the concurrent transactions
        final_val = self.store.get("key8", "tx_final")
        expected_values = [f"value_{i}" for i in range(10)]
        self.assertIn(final_val, expected_values)

if __name__ == "__main__":
    unittest.main()