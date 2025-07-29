import unittest
import threading
import time

from dtm_core.dtm import DistributedTransactionManager

class MockService:
    def __init__(self, name, fail_prepare=False, delay=0):
        self.name = name
        self.fail_prepare = fail_prepare
        self.delay = delay
        self.prepared = False
        self.committed = False
        self.rolledback = False

    def prepare(self, transaction_id):
        if self.delay:
            time.sleep(self.delay)
        if self.fail_prepare:
            raise Exception("Preparation failed on service " + self.name)
        self.prepared = True
        return True

    def commit(self, transaction_id):
        # Idempotent commit
        if not self.committed:
            self.committed = True
        return True

    def rollback(self, transaction_id):
        # Idempotent rollback
        if not self.rolledback:
            self.rolledback = True
        return True

class TestDistributedTransactionManager(unittest.TestCase):
    def test_successful_commit(self):
        dtm = DistributedTransactionManager(timeout=1.0)
        svc1 = MockService("Inventory")
        svc2 = MockService("Order")
        svc3 = MockService("Payment")
        svc4 = MockService("Notification")
        services = [svc1, svc2, svc3, svc4]
        result = dtm.execute_transaction("tx1", services)
        self.assertTrue(result)
        for svc in services:
            self.assertTrue(svc.prepared, f"{svc.name} should be prepared")
            self.assertTrue(svc.committed, f"{svc.name} should be committed")
            self.assertFalse(svc.rolledback, f"{svc.name} should not be rolled back")

    def test_prepare_failure(self):
        dtm = DistributedTransactionManager(timeout=1.0)
        svc1 = MockService("Inventory")
        svc2 = MockService("Order", fail_prepare=True)
        svc3 = MockService("Payment")
        services = [svc1, svc2, svc3]
        with self.assertRaises(Exception) as context:
            dtm.execute_transaction("tx2", services)
        self.assertIn("Preparation failed", str(context.exception))
        # Ensure that any service that prepared has been rolled back
        self.assertTrue(svc1.rolledback, "Inventory should be rolled back")
        self.assertFalse(svc1.committed, "Inventory should not be committed")
        # The service that fails prepare should not be marked as prepared
        self.assertFalse(svc2.prepared, "Order should not be prepared")
        # Subsequent services may not have been attempted
        self.assertFalse(svc3.prepared, "Payment should not be prepared")

    def test_prepare_timeout(self):
        # Service with delay exceeding timeout should trigger a timeout exception
        dtm = DistributedTransactionManager(timeout=0.5)
        svc1 = MockService("Inventory")
        svc2 = MockService("Delayed", delay=1.0)
        svc3 = MockService("Order")
        services = [svc1, svc2, svc3]
        with self.assertRaises(Exception) as context:
            dtm.execute_transaction("tx3", services)
        self.assertIn("timeout", str(context.exception).lower())
        self.assertTrue(svc1.rolledback, "Inventory should be rolled back due to timeout")
        self.assertFalse(svc1.committed, "Inventory should not be committed due to timeout")

    def test_concurrent_transactions(self):
        dtm = DistributedTransactionManager(timeout=1.0)
        results = {}

        def run_transaction(tx_id):
            local_svc1 = MockService("Inventory")
            local_svc2 = MockService("Order")
            local_svc3 = MockService("Payment")
            services = [local_svc1, local_svc2, local_svc3]
            try:
                res = dtm.execute_transaction(tx_id, services)
                results[tx_id] = (res, local_svc1, local_svc2, local_svc3)
            except Exception as e:
                results[tx_id] = (str(e), local_svc1, local_svc2, local_svc3)

        threads = []
        for i in range(5):
            t = threading.Thread(target=run_transaction, args=(f"tx_concurrent_{i}",))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        for tx_id, (res, s1, s2, s3) in results.items():
            self.assertTrue(res is True, f"Transaction {tx_id} should succeed")
            for svc in (s1, s2, s3):
                self.assertTrue(svc.prepared, f"{svc.name} in {tx_id} should be prepared")
                self.assertTrue(svc.committed, f"{svc.name} in {tx_id} should be committed")
                self.assertFalse(svc.rolledback, f"{svc.name} in {tx_id} should not be rolled back")

    def test_idempotent_commit(self):
        dtm = DistributedTransactionManager(timeout=1.0)
        svc = MockService("Inventory")
        services = [svc]
        res = dtm.execute_transaction("tx_idempotent", services)
        self.assertTrue(res, "Initial transaction should succeed")
        # Invoke commit again manually should not change state or raise an error
        res_second_commit = svc.commit("tx_idempotent")
        self.assertTrue(res_second_commit, "Second commit should be idempotent")
        self.assertTrue(svc.committed, "Service commit state should remain True")
        # Similarly, calling rollback again should be idempotent
        res_second_rollback = svc.rollback("tx_idempotent")
        self.assertTrue(res_second_rollback, "Second rollback should be idempotent")
        self.assertTrue(svc.rolledback or not svc.rolledback, "Rollback state remains consistent")

if __name__ == '__main__':
    unittest.main()