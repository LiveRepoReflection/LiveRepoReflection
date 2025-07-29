import unittest
import threading
import time
from txn_keyvalue.node import Node

class TestTxnKeyValue(unittest.TestCase):
    def setUp(self):
        self.node = Node(node_id=0)
    
    def test_single_transaction(self):
        txn_id = self.node.start_transaction()
        self.node.write(txn_id, "key1", "value1")
        self.assertEqual(self.node.read(txn_id, "key1"), "value1")
        self.node.commit(txn_id)
        
        txn_id2 = self.node.start_transaction()
        self.assertEqual(self.node.read(txn_id2, "key1"), "value1")
        self.node.commit(txn_id2)
    
    def test_aborted_transaction(self):
        txn_id = self.node.start_transaction()
        self.node.write(txn_id, "key2", "value2")
        self.node.abort(txn_id)
        
        txn_id2 = self.node.start_transaction()
        self.assertIsNone(self.node.read(txn_id2, "key2"))
        self.node.commit(txn_id2)
    
    def test_snapshot_isolation(self):
        # Initial write
        txn_init = self.node.start_transaction()
        self.node.write(txn_init, "key3", "init_value")
        self.node.commit(txn_init)
        
        # Start two concurrent transactions
        txn1 = self.node.start_transaction()
        txn2 = self.node.start_transaction()
        
        # Transaction 1 reads initial value
        self.assertEqual(self.node.read(txn1, "key3"), "init_value")
        
        # Transaction 2 modifies the value
        self.node.write(txn2, "key3", "modified_by_txn2")
        self.node.commit(txn2)
        
        # Transaction 1 should still see initial value
        self.assertEqual(self.node.read(txn1, "key3"), "init_value")
        self.node.commit(txn1)
        
        # New transaction should see latest committed value
        txn3 = self.node.start_transaction()
        self.assertEqual(self.node.read(txn3, "key3"), "modified_by_txn2")
        self.node.commit(txn3)
    
    def test_concurrent_transactions(self):
        results = []
        
        def worker(txn_id, key, value):
            self.node.write(txn_id, key, value)
            time.sleep(0.1)  # Ensure some overlap
            results.append(self.node.read(txn_id, key))
            self.node.commit(txn_id)
        
        threads = []
        for i in range(5):
            txn_id = self.node.start_transaction()
            t = threading.Thread(target=worker, args=(txn_id, f"key{i}", f"value{i}"))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all transactions saw their own writes
        self.assertEqual(sorted(results), [f"value{i}" for i in range(5)])
        
        # Verify final state
        txn_verify = self.node.start_transaction()
        for i in range(5):
            self.assertEqual(self.node.read(txn_verify, f"key{i}"), f"value{i}")
        self.node.commit(txn_verify)
    
    def test_error_handling(self):
        # Invalid transaction ID
        with self.assertRaises(ValueError):
            self.node.read(999, "nonexistent")
        
        # Read after commit
        txn_id = self.node.start_transaction()
        self.node.commit(txn_id)
        with self.assertRaises(ValueError):
            self.node.read(txn_id, "any_key")
        
        # Write after abort
        txn_id2 = self.node.start_transaction()
        self.node.abort(txn_id2)
        with self.assertRaises(ValueError):
            self.node.write(txn_id2, "any_key", "any_value")

if __name__ == '__main__':
    unittest.main()