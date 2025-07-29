import threading
import unittest
import uuid
from txn_orch import TransactionCoordinator

class DummyException(Exception):
    pass

class TransactionCoordinatorTest(unittest.TestCase):

    def setUp(self):
        self.coordinator = TransactionCoordinator()
    
    def test_successful_commit(self):
        commit_order = []
        rollback_order = []
        
        def commit_func(name):
            def func():
                commit_order.append(name)
            return func
        
        def rollback_func(name):
            def func():
                rollback_order.append(name)
            return func
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.register_participant(txn_id, "order", commit_func("order"), rollback_func("order"))
        self.coordinator.register_participant(txn_id, "payment", commit_func("payment"), rollback_func("payment"))
        self.coordinator.register_participant(txn_id, "inventory", commit_func("inventory"), rollback_func("inventory"))
        self.coordinator.register_participant(txn_id, "notification", commit_func("notification"), rollback_func("notification"))
        
        # Commit should succeed without errors.
        self.coordinator.commit_transaction(txn_id)
        
        # Check that the commit functions were executed in registration order.
        self.assertEqual(commit_order, ["order", "payment", "inventory", "notification"])
        # Since commit succeeded, rollback should not be invoked.
        self.assertEqual(rollback_order, [])

    def test_failed_commit_triggers_rollback(self):
        commit_order = []
        rollback_order = []
        
        def commit_func(name, fail=False):
            def func():
                commit_order.append(name)
                if fail:
                    raise DummyException(f"{name} failed")
            return func
        
        def rollback_func(name):
            def func():
                rollback_order.append(name)
            return func
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.register_participant(txn_id, "order", commit_func("order"), rollback_func("order"))
        self.coordinator.register_participant(txn_id, "payment", commit_func("payment", fail=True), rollback_func("payment"))
        self.coordinator.register_participant(txn_id, "inventory", commit_func("inventory"), rollback_func("inventory"))
        self.coordinator.register_participant(txn_id, "notification", commit_func("notification"), rollback_func("notification"))
        
        with self.assertRaises(DummyException):
            self.coordinator.commit_transaction(txn_id)
        
        # Even if commit failed, commit functions before failure would have been executed.
        self.assertEqual(commit_order, ["order", "payment"])
        # Rollback functions should be called in reverse order of registration.
        self.assertEqual(rollback_order, ["notification", "inventory", "payment", "order"])

    def test_register_invalid_transaction(self):
        # Generate a random transaction id which is not started.
        invalid_txn_id = uuid.uuid4().hex
        with self.assertRaises(Exception):
            self.coordinator.register_participant(invalid_txn_id, "order", lambda: None, lambda: None)
    
    def test_commit_non_existent_transaction(self):
        invalid_txn_id = uuid.uuid4().hex
        with self.assertRaises(Exception):
            self.coordinator.commit_transaction(invalid_txn_id)
    
    def test_rollback_non_existent_transaction(self):
        invalid_txn_id = uuid.uuid4().hex
        with self.assertRaises(Exception):
            self.coordinator.rollback_transaction(invalid_txn_id)
    
    def test_multiple_same_service_registration(self):
        commit_calls = []
        rollback_calls = []
        
        def commit_func(name):
            def func():
                commit_calls.append(name)
            return func
        
        def rollback_func(name):
            def func():
                rollback_calls.append(name)
            return func
        
        txn_id = self.coordinator.begin_transaction()
        # Register two participants with the same service name.
        self.coordinator.register_participant(txn_id, "duplicate", commit_func("duplicate1"), rollback_func("duplicate1"))
        self.coordinator.register_participant(txn_id, "duplicate", commit_func("duplicate2"), rollback_func("duplicate2"))
        
        self.coordinator.commit_transaction(txn_id)
        self.assertEqual(commit_calls, ["duplicate1", "duplicate2"])
        self.assertEqual(rollback_calls, [])
    
    def test_concurrent_transactions(self):
        results_lock = threading.Lock()
        commit_results = {}
        
        def transaction_work(name):
            commit_order = []
            
            def commit_func(n):
                def func():
                    commit_order.append(n)
                return func
            
            def rollback_func(n):
                def func():
                    commit_order.append("rollback_" + n)
                return func
            
            txn_id = self.coordinator.begin_transaction()
            self.coordinator.register_participant(txn_id, f"{name}_1", commit_func(f"{name}_1"), rollback_func(f"{name}_1"))
            self.coordinator.register_participant(txn_id, f"{name}_2", commit_func(f"{name}_2"), rollback_func(f"{name}_2"))
            try:
                self.coordinator.commit_transaction(txn_id)
            except Exception:
                # In case of failure, rollback is already triggered
                pass
            with results_lock:
                commit_results[name] = list(commit_order)
        
        threads = []
        names = ["txnA", "txnB", "txnC", "txnD"]
        for name in names:
            t = threading.Thread(target=transaction_work, args=(name,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(set(commit_results.keys()), set(names))
        for name in names:
            # Check ordering is as registered for successful commits.
            # In our dummy functions, if no failure occurs, commit_order should be in order.
            self.assertEqual(commit_results[name], [f"{name}_1", f"{name}_2"])

if __name__ == '__main__':
    unittest.main()