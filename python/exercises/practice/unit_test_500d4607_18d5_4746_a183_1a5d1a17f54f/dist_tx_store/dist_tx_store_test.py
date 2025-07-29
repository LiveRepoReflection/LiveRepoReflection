import unittest
import threading
import uuid
import time

# Assuming the implementation is in the 'store.py' within the 'dist_tx_store' package.
from dist_tx_store.store import connect, begin_transaction, put, get, commit_transaction, abort_transaction

class TestDistTxStore(unittest.TestCase):

    def setUp(self):
        # In a real scenario, we might want to reset the store state here.
        # For testing, we assume a clean state for each test or that the store
        # supports some form of reset.
        #
        # Connect to a set of nodes. Here we assume node1 and node2 are valid.
        self.assertTrue(connect("node1"), "Failed to connect to node1")
        self.assertTrue(connect("node2"), "Failed to connect to node2")

    def test_connection_validity(self):
        # Test that valid node connection returns True.
        self.assertTrue(connect("node1"))
        self.assertTrue(connect("node2"))
        
        # Testing an invalid node connection may require a defined behavior.
        # For this test, assume that if the node_id is unknown the connect function returns False.
        self.assertFalse(connect("invalid_node"))

    def test_begin_transaction_unique(self):
        tx_ids = set()
        for _ in range(5):
            tx_id = begin_transaction()
            # Check that transaction id is non-empty and unique.
            self.assertTrue(isinstance(tx_id, str) and len(tx_id) > 0)
            self.assertNotIn(tx_id, tx_ids)
            tx_ids.add(tx_id)

    def test_put_and_commit(self):
        # Begin a transaction and perform put operations.
        tx_id = begin_transaction()
        self.assertTrue(put(tx_id, "alpha", "first"))
        self.assertTrue(put(tx_id, "beta", "second"))
        
        # Prior to commit, get should return None for new keys.
        self.assertIsNone(get("alpha"))
        self.assertIsNone(get("beta"))

        # Commit the transaction
        self.assertTrue(commit_transaction(tx_id))
        
        # Now get should return the committed values.
        self.assertEqual(get("alpha"), "first")
        self.assertEqual(get("beta"), "second")

    def test_abort_transaction(self):
        # Begin a transaction, put some keys, then abort.
        tx_id = begin_transaction()
        self.assertTrue(put(tx_id, "gamma", "third"))
        
        # Abort the transaction.
        abort_transaction(tx_id)
        
        # Since the transaction was aborted, get should return None.
        self.assertIsNone(get("gamma"))

    def test_conflict_resolution_last_write_wins(self):
        # Two transactions from different nodes updating the same key.
        # We simulate the scenario by starting two transactions and performing put operations on same key.
        tx1 = begin_transaction()
        tx2 = begin_transaction()

        # Assume that when commit happens, the version vector takes node IDs into account.
        # We simulate this by performing put operations which internally record the node that performed the update.
        # For tx1 from node1:
        self.assertTrue(put(tx1, "delta", "node1_value"))
        # For tx2 from node2:
        self.assertTrue(put(tx2, "delta", "node2_value"))
        
        # Commit transactions in quick succession.
        commit1 = commit_transaction(tx1)
        commit2 = commit_transaction(tx2)
        
        # Both commits should succeed (depending on conflict resolution, one will override the other).
        self.assertTrue(commit1)
        self.assertTrue(commit2)
        
        # According to the rules, conflict resolution chooses the update from the lexicographically largest node id.
        # Given that "node2" > "node1", the value should be from node2.
        self.assertEqual(get("delta"), "node2_value")

    def test_concurrent_transactions(self):
        # Test concurrent transactions that update different keys
        results = {}

        def transaction_worker(key, value, sleep_time):
            tx_id = begin_transaction()
            time.sleep(sleep_time)  # simulate delay
            self.assertTrue(put(tx_id, key, value))
            commit_result = commit_transaction(tx_id)
            results[key] = commit_result

        threads = []
        keys = ["epsilon", "zeta", "eta", "theta"]
        for i, key in enumerate(keys):
            t = threading.Thread(target=transaction_worker, args=(key, f"value_{i}", 0.1 * i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Check all transactions committed successfully
        for key in keys:
            self.assertTrue(results[key])
            self.assertIsNotNone(get(key))
        
        # Verify the committed values.
        for i, key in enumerate(keys):
            self.assertEqual(get(key), f"value_{i}")

    def test_invalid_commit(self):
        # Test behavior when attempting to commit an invalid/non-existent transaction.
        fake_tx = str(uuid.uuid4())
        # According to the specification, commit_transaction should return False for invalid transaction.
        self.assertFalse(commit_transaction(fake_tx))
        
    def test_multiple_puts_in_same_transaction(self):
        # Begin a transaction, update the same key multiple times.
        tx_id = begin_transaction()
        self.assertTrue(put(tx_id, "iota", "first_update"))
        self.assertTrue(put(tx_id, "iota", "second_update"))
        # Commit the transaction.
        self.assertTrue(commit_transaction(tx_id))
        # The committed value should be the last update.
        self.assertEqual(get("iota"), "second_update")

if __name__ == '__main__':
    unittest.main()