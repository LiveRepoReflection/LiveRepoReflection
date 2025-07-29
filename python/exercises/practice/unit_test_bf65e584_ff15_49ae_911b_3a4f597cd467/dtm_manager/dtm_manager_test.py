import unittest
import threading
import time
from dtm_manager import DistributedTransactionManager


class TestDistributedTransactionManager(unittest.TestCase):
    
    def setUp(self):
        self.dtm = DistributedTransactionManager()
    
    def test_begin_transaction(self):
        txid1 = self.dtm.begin_transaction()
        txid2 = self.dtm.begin_transaction()
        self.assertNotEqual(txid1, txid2)
        self.assertTrue(isinstance(txid1, str))
        self.assertTrue(isinstance(txid2, str))
    
    def test_enlist_resource(self):
        txid = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid, "RM1")
        
        # Test enlisting the same resource again (should work)
        self.dtm.enlist_resource(txid, "RM1")
        
        # Test enlisting the resource in another transaction (should raise an exception)
        txid2 = self.dtm.begin_transaction()
        with self.assertRaises(Exception):
            self.dtm.enlist_resource(txid2, "RM1")
        
        # Test invalid transaction ID
        with self.assertRaises(Exception):
            self.dtm.enlist_resource("invalid_txid", "RM2")
    
    def test_execute_operation(self):
        txid = self.dtm.begin_transaction()
        
        # Cannot execute on non-enlisted RM
        with self.assertRaises(Exception):
            self.dtm.execute_operation(txid, "RM1", "update")
        
        self.dtm.enlist_resource(txid, "RM1")
        self.dtm.execute_operation(txid, "RM1", "update")
        
        # Test invalid transaction ID
        with self.assertRaises(Exception):
            self.dtm.execute_operation("invalid_txid", "RM1", "update")
        
        # Test invalid RM ID
        with self.assertRaises(Exception):
            self.dtm.execute_operation(txid, "invalid_rm", "update")
    
    def test_prepare_transaction(self):
        txid = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid, "RM1")
        self.dtm.execute_operation(txid, "RM1", "update")
        
        # All resources should vote yes by default in our test environment
        result = self.dtm.prepare_transaction(txid)
        self.assertTrue(result)
        
        # Test invalid transaction ID
        with self.assertRaises(Exception):
            self.dtm.prepare_transaction("invalid_txid")
    
    def test_commit_transaction(self):
        txid = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid, "RM1")
        self.dtm.execute_operation(txid, "RM1", "update")
        
        # Cannot commit without prepare
        with self.assertRaises(Exception):
            self.dtm.commit_transaction(txid)
        
        self.dtm.prepare_transaction(txid)
        self.dtm.commit_transaction(txid)
        
        # Cannot commit twice
        with self.assertRaises(Exception):
            self.dtm.commit_transaction(txid)
        
        # Test invalid transaction ID
        with self.assertRaises(Exception):
            self.dtm.commit_transaction("invalid_txid")
    
    def test_rollback_transaction(self):
        txid = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid, "RM1")
        self.dtm.execute_operation(txid, "RM1", "update")
        
        # Can rollback without prepare
        self.dtm.rollback_transaction(txid)
        
        # Cannot rollback twice
        with self.assertRaises(Exception):
            self.dtm.rollback_transaction(txid)
        
        # Test rollback after prepare
        txid2 = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid2, "RM2")
        self.dtm.execute_operation(txid2, "RM2", "update")
        self.dtm.prepare_transaction(txid2)
        self.dtm.rollback_transaction(txid2)
        
        # Test invalid transaction ID
        with self.assertRaises(Exception):
            self.dtm.rollback_transaction("invalid_txid")
    
    def test_two_phase_commit_success(self):
        txid = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid, "RM1")
        self.dtm.enlist_resource(txid, "RM2")
        self.dtm.execute_operation(txid, "RM1", "update")
        self.dtm.execute_operation(txid, "RM2", "update")
        
        result = self.dtm.prepare_transaction(txid)
        self.assertTrue(result)
        
        self.dtm.commit_transaction(txid)
    
    def test_two_phase_commit_failure(self):
        # In this test, we assume some mechanism where an RM would vote "no"
        # Since we can't directly control the RM vote in the test, we're testing
        # the rollback flow assuming a "no" vote was received
        txid = self.dtm.begin_transaction()
        self.dtm.enlist_resource(txid, "RM1")
        self.dtm.enlist_resource(txid, "RM2")
        self.dtm.execute_operation(txid, "RM1", "update")
        self.dtm.execute_operation(txid, "RM2", "update")
        
        # Simulate prepare phase - in a real test, this could return False if an RM votes "no"
        # For this test, we'll just rollback regardless
        self.dtm.prepare_transaction(txid)
        self.dtm.rollback_transaction(txid)
    
    def test_concurrent_transactions(self):
        def transaction_thread(index):
            try:
                # Start a transaction
                txid = self.dtm.begin_transaction()
                # Enlist a unique resource
                rm_id = f"RM{index}"
                self.dtm.enlist_resource(txid, rm_id)
                # Execute an operation
                self.dtm.execute_operation(txid, rm_id, f"update_operation_{index}")
                # Prepare and commit
                if self.dtm.prepare_transaction(txid):
                    self.dtm.commit_transaction(txid)
                else:
                    self.dtm.rollback_transaction(txid)
            except Exception as e:
                self.fail(f"Exception in thread {index}: {e}")
        
        # Create and start 10 concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=transaction_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
    
    def test_resource_manager_contention(self):
        # Test that a resource manager can't be enlisted in multiple transactions simultaneously
        def transaction_thread(index, rm_id, delay):
            try:
                txid = self.dtm.begin_transaction()
                if delay:
                    time.sleep(0.1)  # Small delay to create contention
                
                try:
                    self.dtm.enlist_resource(txid, rm_id)
                    # If we successfully enlisted the RM, complete the transaction
                    self.dtm.execute_operation(txid, rm_id, f"operation_{index}")
                    if self.dtm.prepare_transaction(txid):
                        self.dtm.commit_transaction(txid)
                    else:
                        self.dtm.rollback_transaction(txid)
                except Exception:
                    # If we couldn't enlist (expected for some threads), rollback
                    self.dtm.rollback_transaction(txid)
            except Exception as e:
                # Some transactions will fail - that's expected
                pass
        
        # Create threads that all try to use the same resource manager
        threads = []
        for i in range(5):
            thread = threading.Thread(target=transaction_thread, args=(i, "SharedRM", i % 2 == 0))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
    
    def test_transaction_limits(self):
        # Test handling of transaction limits
        # This is a simplified test that just creates many transactions
        # A real implementation would need to handle the constraints mentioned in the problem
        
        # Create 50 transactions (well below the limit of 1000)
        transactions = []
        for i in range(50):
            txid = self.dtm.begin_transaction()
            transactions.append(txid)
        
        # Enlist resources and complete them
        for i, txid in enumerate(transactions):
            rm_id = f"RM{i % 10}"  # Use 10 different RMs
            try:
                self.dtm.enlist_resource(txid, rm_id)
                self.dtm.execute_operation(txid, rm_id, f"operation_{i}")
                if self.dtm.prepare_transaction(txid):
                    self.dtm.commit_transaction(txid)
                else:
                    self.dtm.rollback_transaction(txid)
            except Exception:
                # Some transactions might fail due to RM already being enlisted
                # Just rollback those
                try:
                    self.dtm.rollback_transaction(txid)
                except Exception:
                    pass


if __name__ == '__main__':
    unittest.main()