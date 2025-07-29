import unittest
import threading
import time

from dist_keyval_tx import read, write, begin_transaction, commit_transaction, abort_transaction

class TestDistributedKeyValStore(unittest.TestCase):

    def setUp(self):
        # If a reset_store function is provided to clear state between tests, use it.
        try:
            from dist_keyval_tx import reset_store
            reset_store()
        except ImportError:
            pass

    def test_non_transactional_read_write(self):
        write("a", "1")
        self.assertEqual(read("a"), "1")

    def test_transaction_commit(self):
        # Write initial value outside transaction
        write("test", "initial")
        txn = begin_transaction()
        # Write within transaction
        write("test", "updated", txn)
        # In transactional context, the new value is visible
        self.assertEqual(read("test", txn), "updated")
        # Outside the transaction, the update is not yet visible
        self.assertEqual(read("test"), "initial")
        # Commit transaction
        self.assertTrue(commit_transaction(txn))
        # After commit, global read should reflect the update
        self.assertEqual(read("test"), "updated")

    def test_transaction_abort(self):
        # Write initial value outside transaction
        write("test", "initial")
        txn = begin_transaction()
        write("test", "new", txn)
        # In transaction, updated value is visible
        self.assertEqual(read("test", txn), "new")
        # Abort transaction
        self.assertTrue(abort_transaction(txn))
        # Global state should remain unchanged
        self.assertEqual(read("test"), "initial")

    def test_concurrent_transactions(self):
        results = {}
        def txn_task(key, value):
            txn = begin_transaction()
            write(key, value, txn)
            # Simulate work delay
            time.sleep(0.1)
            self.assertTrue(commit_transaction(txn))
            results[key] = read(key)

        threads = []
        keys = ['k1', 'k2', 'k3', 'k4']
        for key in keys:
            t = threading.Thread(target=txn_task, args=(key, key + "_val"))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        for key in keys:
            self.assertEqual(results[key], key + "_val")
            self.assertEqual(read(key), key + "_val")

    def test_transaction_isolation(self):
        # Set an initial value for the shared key
        write("shared", "start")
        txn1 = begin_transaction()
        txn2 = begin_transaction()
        # Transaction 1 updates the 'shared' key
        write("shared", "txn1", txn1)
        self.assertEqual(read("shared", txn1), "txn1")
        # Transaction 2 should still see the original value because it is isolated
        self.assertEqual(read("shared", txn2), "start")
        # Commit transaction 1 and verify global state updates, while txn2 remains with its snapshot
        self.assertTrue(commit_transaction(txn1))
        self.assertEqual(read("shared", txn2), "start")
        self.assertEqual(read("shared"), "txn1")
        # Abort transaction 2 to clean up
        self.assertTrue(abort_transaction(txn2))

    def test_durability_logging(self):
        # Write an initial durable value
        write("durable", "v1")
        txn = begin_transaction()
        write("durable", "v2", txn)
        self.assertTrue(commit_transaction(txn))
        # Simulate a store restart if a reload_store function is available
        try:
            from dist_keyval_tx import reload_store
            reload_store()
        except ImportError:
            pass
        # Verify that the committed value survives the restart
        self.assertEqual(read("durable"), "v2")

if __name__ == '__main__':
    unittest.main()