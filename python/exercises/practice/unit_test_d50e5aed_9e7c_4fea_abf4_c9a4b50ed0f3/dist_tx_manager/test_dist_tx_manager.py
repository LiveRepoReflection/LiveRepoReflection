import unittest
from threading import Thread
import time
from dist_tx_manager import DistributedTransactionManager

class TestDistributedTransactionManager(unittest.TestCase):
    def setUp(self):
        self.dtm = DistributedTransactionManager()
        
    def test_begin_transaction(self):
        txid = self.dtm.begin_transaction()
        self.assertIsNotNone(txid)
        self.assertEqual(self.dtm.get_transaction_state(txid), "PENDING")

    def test_add_operation_valid(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        self.dtm.add_operation(txid, "node2", "credit", 100)
        self.assertEqual(self.dtm.get_transaction_state(txid), "PENDING")

    def test_add_operation_invalid_type(self):
        txid = self.dtm.begin_transaction()
        with self.assertRaises(ValueError):
            self.dtm.add_operation(txid, "node1", "invalid_type", 100)

    def test_add_operation_invalid_txid(self):
        with self.assertRaises(ValueError):
            self.dtm.add_operation("invalid_txid", "node1", "debit", 100)

    def test_prepare_transaction_success(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        self.dtm.add_operation(txid, "node2", "credit", 100)
        self.assertTrue(self.dtm.prepare_transaction(txid))
        self.assertEqual(self.dtm.get_transaction_state(txid), "PREPARED")

    def test_prepare_transaction_failure(self):
        # Simulate a node that will fail preparation
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "failing_node", "debit", 999999)  # Amount too large
        self.assertFalse(self.dtm.prepare_transaction(txid))
        self.assertEqual(self.dtm.get_transaction_state(txid), "ABORTED")

    def test_commit_transaction_success(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        self.dtm.add_operation(txid, "node2", "credit", 100)
        self.dtm.prepare_transaction(txid)
        self.assertTrue(self.dtm.commit_transaction(txid))
        self.assertEqual(self.dtm.get_transaction_state(txid), "COMMITTED")

    def test_commit_unprepared_transaction(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        with self.assertRaises(ValueError):
            self.dtm.commit_transaction(txid)

    def test_abort_transaction(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        self.dtm.prepare_transaction(txid)
        self.assertTrue(self.dtm.abort_transaction(txid))
        self.assertEqual(self.dtm.get_transaction_state(txid), "ABORTED")

    def test_concurrent_transactions(self):
        def run_transaction():
            txid = self.dtm.begin_transaction()
            self.dtm.add_operation(txid, "node1", "debit", 50)
            self.dtm.add_operation(txid, "node2", "credit", 50)
            self.dtm.prepare_transaction(txid)
            self.dtm.commit_transaction(txid)

        threads = []
        for _ in range(10):
            t = Thread(target=run_transaction)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    def test_service_node_failure_during_prepare(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "failing_node", "debit", 100)
        self.assertFalse(self.dtm.prepare_transaction(txid))
        self.assertEqual(self.dtm.get_transaction_state(txid), "ABORTED")

    def test_service_node_failure_during_commit(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "failing_commit_node", "debit", 100)
        self.dtm.prepare_transaction(txid)
        self.assertFalse(self.dtm.commit_transaction(txid))
        self.assertEqual(self.dtm.get_transaction_state(txid), "ABORTED")

    def test_idempotent_commit(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        self.dtm.prepare_transaction(txid)
        self.dtm.commit_transaction(txid)
        # Second commit should not throw error
        self.dtm.commit_transaction(txid)
        self.assertEqual(self.dtm.get_transaction_state(txid), "COMMITTED")

    def test_idempotent_abort(self):
        txid = self.dtm.begin_transaction()
        self.dtm.add_operation(txid, "node1", "debit", 100)
        self.dtm.abort_transaction(txid)
        # Second abort should not throw error
        self.dtm.abort_transaction(txid)
        self.assertEqual(self.dtm.get_transaction_state(txid), "ABORTED")

    def test_transaction_isolation(self):
        txid1 = self.dtm.begin_transaction()
        txid2 = self.dtm.begin_transaction()
        
        self.dtm.add_operation(txid1, "node1", "debit", 100)
        self.dtm.add_operation(txid2, "node1", "debit", 50)
        
        # Prepare and commit first transaction
        self.dtm.prepare_transaction(txid1)
        self.dtm.commit_transaction(txid1)
        
        # Second transaction should still be independent
        self.assertEqual(self.dtm.get_transaction_state(txid2), "PENDING")

    def test_invalid_transaction_state_transitions(self):
        txid = self.dtm.begin_transaction()
        
        # Cannot commit without prepare
        with self.assertRaises(ValueError):
            self.dtm.commit_transaction(txid)
            
        # Cannot prepare after abort
        self.dtm.abort_transaction(txid)
        with self.assertRaises(ValueError):
            self.dtm.prepare_transaction(txid)
            
        # Cannot commit after abort
        with self.assertRaises(ValueError):
            self.dtm.commit_transaction(txid)

if __name__ == '__main__':
    unittest.main()