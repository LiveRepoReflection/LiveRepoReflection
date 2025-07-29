import unittest
import threading
from time import sleep

# Import the transaction API from the kv_transaction module.
# It is assumed that the solution implements these functions:
# begin_transaction, read, write, commit_transaction, abort_transaction
from kv_transaction import begin_transaction, read, write, commit_transaction, abort_transaction

class KVTransactionTest(unittest.TestCase):

    def test_simple_commit(self):
        # Begin a transaction, write a key and commit. Verify that another transaction sees the change.
        txid = begin_transaction()
        write(txid, "a", "apple")
        commit_success = commit_transaction(txid)
        self.assertTrue(commit_success, "Transaction should commit successfully")
        
        # New transaction should see the committed value.
        txid2 = begin_transaction()
        value = read(txid2, "a")
        self.assertEqual(value, "apple", "Value for key 'a' should be 'apple' after commit")
        commit_transaction(txid2)

    def test_abort_transaction(self):
        # Begin a transaction, write a key and then abort. Verify that value is not visible.
        txid = begin_transaction()
        write(txid, "b", "banana")
        abort_transaction(txid)
        
        txid2 = begin_transaction()
        value = read(txid2, "b")
        self.assertIsNone(value, "Value for key 'b' should be None after abort")
        commit_transaction(txid2)

    def test_conflict_resolution(self):
        # Two transactions concurrently modify the same key.
        txid1 = begin_transaction()
        txid2 = begin_transaction()
        
        write(txid1, "c", "cherry")
        write(txid2, "c", "cranberry")
        
        # First transaction commits successfully.
        commit1 = commit_transaction(txid1)
        self.assertTrue(commit1, "First transaction should commit successfully")
        
        # Second transaction should encounter a conflict.
        commit2 = commit_transaction(txid2)
        self.assertFalse(commit2, "Second transaction should be aborted due to conflict")

        # Verify the committed value is from txid1.
        txid3 = begin_transaction()
        value = read(txid3, "c")
        self.assertEqual(value, "cherry", "The final value for key 'c' should be from the successful transaction")
        commit_transaction(txid3)

    def test_snapshot_isolation(self):
        # Test that a transaction sees a consistent snapshot.
        # Begin a transaction and read a key that has not been set; it should see None.
        txid1 = begin_transaction()
        initial = read(txid1, "d")
        self.assertIsNone(initial, "Initial snapshot for key 'd' should be None")
        
        # In a separate transaction, write to "d" and commit.
        txid2 = begin_transaction()
        write(txid2, "d", "date")
        commit_success = commit_transaction(txid2)
        self.assertTrue(commit_success, "Second transaction should commit successfully")
        
        # The first transaction should still see the old snapshot (None).
        snapshot = read(txid1, "d")
        self.assertIsNone(snapshot, "Snapshot isolation should keep old value view during tx1")
        commit_transaction(txid1)
        
        # A new transaction should see the updated value.
        txid3 = begin_transaction()
        new_value = read(txid3, "d")
        self.assertEqual(new_value, "date", "New transaction should see the committed value")
        commit_transaction(txid3)

    def test_concurrent_transactions_different_nodes(self):
        # Simulate concurrent transactions on different keys (assumed to be handled by different nodes).
        results = {}
        lock = threading.Lock()

        def transaction_worker(key, value, txn_label):
            txid = begin_transaction()
            write(txid, key, value)
            # Sleep to simulate work and possible concurrency issues.
            sleep(0.1)
            success = commit_transaction(txid)
            with lock:
                results[txn_label] = success

        threads = []
        transactions = [
            ("e", "elderberry", "tx1"),
            ("f", "fig", "tx2"),
            ("g", "grape", "tx3")
        ]
        for key, value, label in transactions:
            thread = threading.Thread(target=transaction_worker, args=(key, value, label))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All transactions on different keys should succeed.
        for label in results:
            self.assertTrue(results[label], f"Transaction {label} should commit successfully")

        # Verify that each key holds the correct value.
        for key, value, _ in transactions:
            txid = begin_transaction()
            stored = read(txid, key)
            self.assertEqual(stored, value, f"Key '{key}' should have the value '{value}' after commit")
            commit_transaction(txid)

if __name__ == "__main__":
    unittest.main()