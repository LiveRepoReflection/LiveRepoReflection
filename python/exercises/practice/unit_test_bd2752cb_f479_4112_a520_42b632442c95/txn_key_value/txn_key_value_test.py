import unittest
import threading
from txn_key_value import (
    get_timestamp,
    begin_transaction,
    read,
    write,
    commit_transaction,
    abort_transaction,
)

class TestTxnKeyValueStore(unittest.TestCase):

    def setUp(self):
        # Assuming that the underlying implementation provides a way to reset state.
        # If not, tests should be designed to work with a global store state.
        pass

    def test_single_transaction_commit(self):
        # Begin transaction, write a key-value pair, commit and verify update.
        txn1 = begin_transaction()
        self.assertIsNone(read(txn1, "A"))
        write(txn1, "A", "value1")
        self.assertTrue(commit_transaction(txn1))
        
        txn2 = begin_transaction()
        self.assertEqual(read(txn2, "A"), "value1")
        self.assertTrue(commit_transaction(txn2))

    def test_single_transaction_abort(self):
        # Write to a key and abort the transaction. The key should remain unchanged.
        txn1 = begin_transaction()
        write(txn1, "B", "temp_value")
        abort_transaction(txn1)
        
        txn2 = begin_transaction()
        self.assertIsNone(read(txn2, "B"))
        self.assertTrue(commit_transaction(txn2))

    def test_conflict_write_write(self):
        # Two transactions writing to the same key concurrently.
        txn1 = begin_transaction()
        txn2 = begin_transaction()
        
        write(txn1, "C", "value1")
        write(txn2, "C", "value2")
        
        # Commit first transaction; it should succeed.
        self.assertTrue(commit_transaction(txn1))
        # Commit second transaction; it should detect conflict and fail.
        self.assertFalse(commit_transaction(txn2))
        
        txn3 = begin_transaction()
        self.assertEqual(read(txn3, "C"), "value1")
        self.assertTrue(commit_transaction(txn3))

    def test_conflict_read_write(self):
        # T1 reads a key and then writes based on the old snapshot.
        # T2 concurrently writes and commits a new value causing conflict for T1.
        txn0 = begin_transaction()
        write(txn0, "D", "initial")
        self.assertTrue(commit_transaction(txn0))
        
        txn1 = begin_transaction()
        self.assertEqual(read(txn1, "D"), "initial")
        
        txn2 = begin_transaction()
        write(txn2, "D", "updated")
        self.assertTrue(commit_transaction(txn2))
        
        write(txn1, "D", "txn1_update")
        self.assertFalse(commit_transaction(txn1))
        
        txn3 = begin_transaction()
        self.assertEqual(read(txn3, "D"), "updated")
        self.assertTrue(commit_transaction(txn3))

    def test_multiple_keys(self):
        # Transaction writes to multiple keys and commits.
        txn1 = begin_transaction()
        write(txn1, "E", "val_e")
        write(txn1, "F", "val_f")
        self.assertTrue(commit_transaction(txn1))
        
        txn2 = begin_transaction()
        self.assertEqual(read(txn2, "E"), "val_e")
        self.assertEqual(read(txn2, "F"), "val_f")
        self.assertTrue(commit_transaction(txn2))

    def test_concurrent_transactions(self):
        # Test thread-safety by executing multiple transactions concurrently.
        results = []

        def txn_thread(key, value):
            txn = begin_transaction()
            write(txn, key, value)
            result = commit_transaction(txn)
            results.append((key, value, result))

        threads = []
        for i in range(10):
            t = threading.Thread(target=txn_thread, args=(f"K{i}", f"V{i}"))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Validate all transactions have committed successfully.
        for key, value, result in results:
            self.assertTrue(result)
            txn = begin_transaction()
            self.assertEqual(read(txn, key), value)
            self.assertTrue(commit_transaction(txn))

if __name__ == '__main__':
    unittest.main()