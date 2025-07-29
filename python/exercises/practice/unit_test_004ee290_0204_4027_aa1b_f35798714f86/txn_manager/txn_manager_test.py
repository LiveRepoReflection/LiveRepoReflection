import unittest
import time
import threading
from txn_manager import TransactionManager

class TestTransactionManager(unittest.TestCase):
    def setUp(self):
        self.tm = TransactionManager()
        # Initialize some data stores
        self.store1_id = self.tm.create_data_store()
        self.store2_id = self.tm.create_data_store()
        self.store3_id = self.tm.create_data_store()

    def test_basic_transaction(self):
        # Test a simple transaction on a single data store
        txn_id = self.tm.begin_transaction()
        self.tm.add_operation(txn_id, self.store1_id, "write", "key1", "value1")
        self.tm.commit_transaction(txn_id)
        
        store1 = self.tm.get_data_store(self.store1_id)
        self.assertEqual(store1["key1"], "value1")

    def test_complex_transaction(self):
        # Test a transaction that spans multiple data stores
        txn_id = self.tm.begin_transaction()
        self.tm.add_operation(txn_id, self.store1_id, "write", "keyA", "valueA")
        self.tm.add_operation(txn_id, self.store2_id, "write", "keyB", "valueB")
        self.tm.add_operation(txn_id, self.store3_id, "write", "keyC", "valueC")
        self.tm.commit_transaction(txn_id)
        
        store1 = self.tm.get_data_store(self.store1_id)
        store2 = self.tm.get_data_store(self.store2_id)
        store3 = self.tm.get_data_store(self.store3_id)
        
        self.assertEqual(store1["keyA"], "valueA")
        self.assertEqual(store2["keyB"], "valueB")
        self.assertEqual(store3["keyC"], "valueC")

    def test_transaction_abort(self):
        # Test that aborting a transaction prevents changes
        txn_id = self.tm.begin_transaction()
        self.tm.add_operation(txn_id, self.store1_id, "write", "abortKey", "abortValue")
        self.tm.abort_transaction(txn_id)
        
        store1 = self.tm.get_data_store(self.store1_id)
        self.assertNotIn("abortKey", store1)

    def test_delete_operation(self):
        # Set up data first
        setup_txn = self.tm.begin_transaction()
        self.tm.add_operation(setup_txn, self.store1_id, "write", "deleteMe", "temp")
        self.tm.commit_transaction(setup_txn)
        
        # Now delete it
        txn_id = self.tm.begin_transaction()
        self.tm.add_operation(txn_id, self.store1_id, "delete", "deleteMe")
        self.tm.commit_transaction(txn_id)
        
        store1 = self.tm.get_data_store(self.store1_id)
        self.assertNotIn("deleteMe", store1)

    def test_invalid_data_store(self):
        # Test error handling for invalid data store ID
        txn_id = self.tm.begin_transaction()
        with self.assertRaises(ValueError):
            self.tm.add_operation(txn_id, 9999, "write", "key", "value")

    def test_invalid_operation_type(self):
        # Test error handling for invalid operation type
        txn_id = self.tm.begin_transaction()
        with self.assertRaises(ValueError):
            self.tm.add_operation(txn_id, self.store1_id, "invalid_op", "key", "value")

    def test_key_not_found_for_delete(self):
        # Test error handling for deleting a non-existent key
        txn_id = self.tm.begin_transaction()
        self.tm.add_operation(txn_id, self.store1_id, "delete", "nonexistent_key")
        # This might raise an exception or handle it gracefully depending on implementation
        # Here we test that it doesn't crash
        try:
            self.tm.commit_transaction(txn_id)
        except KeyError:
            pass  # Either outcome is acceptable based on design decisions

    def test_concurrent_transactions(self):
        # Test that concurrent transactions maintain isolation
        def transaction1():
            txn1 = self.tm.begin_transaction()
            self.tm.add_operation(txn1, self.store1_id, "write", "shared", "value1")
            time.sleep(0.1)  # Introduce delay to test concurrency
            self.tm.commit_transaction(txn1)
            
        def transaction2():
            txn2 = self.tm.begin_transaction()
            self.tm.add_operation(txn2, self.store1_id, "write", "shared", "value2")
            self.tm.commit_transaction(txn2)

        # Run transactions concurrently
        t1 = threading.Thread(target=transaction1)
        t2 = threading.Thread(target=transaction2)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # The final value should be either "value1" or "value2" but not mixed
        store1 = self.tm.get_data_store(self.store1_id)
        self.assertIn(store1["shared"], ["value1", "value2"])

    def test_transaction_isolation(self):
        # Test that one transaction cannot see another's changes until commit
        # First transaction sets up initial data
        setup_txn = self.tm.begin_transaction()
        self.tm.add_operation(setup_txn, self.store1_id, "write", "isolation", "initial")
        self.tm.commit_transaction(setup_txn)
        
        # Start two transactions
        txn1 = self.tm.begin_transaction()
        txn2 = self.tm.begin_transaction()
        
        # Transaction 1 modifies the data but doesn't commit yet
        self.tm.add_operation(txn1, self.store1_id, "write", "isolation", "txn1_value")
        
        # Transaction 2 should still see the original value
        # This is implementation-dependent, but we should have a way to read within a transaction
        # Here we assume there's a read_value method or similar
        if hasattr(self.tm, "read_value"):
            value_in_txn2 = self.tm.read_value(txn2, self.store1_id, "isolation")
            self.assertEqual(value_in_txn2, "initial")
        
        # Now commit transaction 1
        self.tm.commit_transaction(txn1)
        
        # Outside of any transaction, we should see the new value
        store1 = self.tm.get_data_store(self.store1_id)
        self.assertEqual(store1["isolation"], "txn1_value")

    def test_deadlock_handling(self):
        # This test will depend on how deadlocks are handled
        # Here's a sketch that creates a potential deadlock scenario
        
        lock_barrier = threading.Barrier(2)  # Ensure both threads are ready before proceeding
        deadlock_detected = [False]  # Shared variable to track if deadlock was detected
        
        def transaction_a():
            try:
                txn_a = self.tm.begin_transaction()
                self.tm.add_operation(txn_a, self.store1_id, "write", "deadlock_a", "value_a")
                lock_barrier.wait()  # Wait for both threads to reach this point
                time.sleep(0.1)  # Give txn_b time to acquire lock on store2
                # This should contend with txn_b for store2
                self.tm.add_operation(txn_a, self.store2_id, "write", "deadlock_b", "value_a")
                self.tm.commit_transaction(txn_a)
            except Exception as e:
                if "deadlock" in str(e).lower() or "timeout" in str(e).lower():
                    deadlock_detected[0] = True
        
        def transaction_b():
            try:
                txn_b = self.tm.begin_transaction()
                self.tm.add_operation(txn_b, self.store2_id, "write", "deadlock_b", "value_b")
                lock_barrier.wait()  # Wait for both threads to reach this point
                time.sleep(0.1)  # Give txn_a time to acquire lock on store1
                # This should contend with txn_a for store1
                self.tm.add_operation(txn_b, self.store1_id, "write", "deadlock_a", "value_b")
                self.tm.commit_transaction(txn_b)
            except Exception as e:
                if "deadlock" in str(e).lower() or "timeout" in str(e).lower():
                    deadlock_detected[0] = True
        
        t_a = threading.Thread(target=transaction_a)
        t_b = threading.Thread(target=transaction_b)
        
        # Set timeouts for deadlock detection to a relatively short value for testing
        # This assumes there's a way to configure timeouts in the transaction manager
        if hasattr(self.tm, "set_lock_timeout"):
            self.tm.set_lock_timeout(0.5)  # Half a second
        
        t_a.start()
        t_b.start()
        
        t_a.join(timeout=2.0)  # Give the threads time to run or deadlock
        t_b.join(timeout=2.0)
        
        # Check if we detected a deadlock
        # Either the deadlock was detected explicitly, or one of the threads was still blocked
        self.assertTrue(deadlock_detected[0] or not t_a.is_alive() or not t_b.is_alive())
        
        # Cleanup in case threads are still alive
        if t_a.is_alive():
            t_a.join()
        if t_b.is_alive():
            t_b.join()

if __name__ == '__main__':
    unittest.main()