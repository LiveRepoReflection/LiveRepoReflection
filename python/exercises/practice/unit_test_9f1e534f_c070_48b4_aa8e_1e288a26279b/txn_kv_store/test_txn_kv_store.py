import unittest
import json
import os
import threading
import time
from txn_kv_store import TransactionalKeyValueStore

class TestTransactionalKeyValueStore(unittest.TestCase):
    def setUp(self):
        self.store = TransactionalKeyValueStore(num_nodes=3)
        if os.path.exists("state.json"):
            os.remove("state.json")

    def tearDown(self):
        if os.path.exists("state.json"):
            os.remove("state.json")

    def test_basic_transaction(self):
        txid = self.store.begin_transaction()
        self.store.put(txid, "key1", "value1")
        self.assertEqual(self.store.get(txid, "key1"), "value1")
        self.assertTrue(self.store.commit_transaction(txid))

    def test_transaction_isolation(self):
        txid1 = self.store.begin_transaction()
        txid2 = self.store.begin_transaction()
        
        self.store.put(txid1, "key1", "value1")
        self.store.put(txid2, "key1", "value2")
        
        self.assertEqual(self.store.get(txid1, "key1"), "value1")
        self.assertEqual(self.store.get(txid2, "key1"), "value2")
        
        self.assertTrue(self.store.commit_transaction(txid1))
        self.assertFalse(self.store.commit_transaction(txid2))  # Should fail due to conflict

    def test_concurrent_transactions(self):
        def run_transaction(key, value):
            txid = self.store.begin_transaction()
            self.store.put(txid, key, value)
            return self.store.commit_transaction(txid)

        threads = []
        for i in range(10):
            t = threading.Thread(target=run_transaction, args=(f"key{i}", f"value{i}"))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify all values
        txid = self.store.begin_transaction()
        for i in range(10):
            self.assertIsNotNone(self.store.get(txid, f"key{i}"))
        self.store.abort_transaction(txid)

    def test_abort_transaction(self):
        txid = self.store.begin_transaction()
        self.store.put(txid, "key1", "value1")
        self.store.abort_transaction(txid)
        
        txid2 = self.store.begin_transaction()
        self.assertIsNone(self.store.get(txid2, "key1"))
        self.store.abort_transaction(txid2)

    def test_persistence(self):
        txid = self.store.begin_transaction()
        self.store.put(txid, "key1", "value1")
        self.store.put(txid, "key2", "value2")
        self.assertTrue(self.store.commit_transaction(txid))

        # Create new instance and recover
        new_store = TransactionalKeyValueStore(num_nodes=3)
        new_store.recover()

        txid = new_store.begin_transaction()
        self.assertEqual(new_store.get(txid, "key1"), "value1")
        self.assertEqual(new_store.get(txid, "key2"), "value2")
        new_store.abort_transaction(txid)

    def test_multiple_puts_same_key(self):
        txid = self.store.begin_transaction()
        self.store.put(txid, "key1", "value1")
        self.store.put(txid, "key1", "value2")
        self.assertEqual(self.store.get(txid, "key1"), "value2")
        self.assertTrue(self.store.commit_transaction(txid))

    def test_non_existent_transaction(self):
        with self.assertRaises(ValueError):
            self.store.commit_transaction(999)
        with self.assertRaises(ValueError):
            self.store.abort_transaction(999)

    def test_double_commit(self):
        txid = self.store.begin_transaction()
        self.store.put(txid, "key1", "value1")
        self.assertTrue(self.store.commit_transaction(txid))
        with self.assertRaises(ValueError):
            self.store.commit_transaction(txid)

    def test_empty_values(self):
        txid = self.store.begin_transaction()
        self.store.put(txid, "key1", "")
        self.assertEqual(self.store.get(txid, "key1"), "")
        self.assertTrue(self.store.commit_transaction(txid))

    def test_concurrent_different_keys(self):
        txid1 = self.store.begin_transaction()
        txid2 = self.store.begin_transaction()
        
        self.store.put(txid1, "key1", "value1")
        self.store.put(txid2, "key2", "value2")
        
        self.assertTrue(self.store.commit_transaction(txid1))
        self.assertTrue(self.store.commit_transaction(txid2))

        txid3 = self.store.begin_transaction()
        self.assertEqual(self.store.get(txid3, "key1"), "value1")
        self.assertEqual(self.store.get(txid3, "key2"), "value2")
        self.store.abort_transaction(txid3)

if __name__ == '__main__':
    unittest.main()