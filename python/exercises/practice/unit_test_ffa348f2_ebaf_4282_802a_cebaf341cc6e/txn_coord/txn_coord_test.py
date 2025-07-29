import unittest
import threading
import time
from txn_coord import TransactionCoordinator

class MockService:
    def __init__(self, prepare_result=True, prepare_delay=0, commit_delay=0, 
                 prepare_fails=False, commit_fails=False):
        self.prepared = set()
        self.committed = set()
        self.prepare_result = prepare_result
        self.prepare_delay = prepare_delay
        self.commit_delay = commit_delay
        self.prepare_fails = prepare_fails
        self.commit_fails = commit_fails
        self.prepare_called = 0
        self.commit_called = 0

    def __call__(self, action, transaction_id, data=None):
        if action == "prepare":
            return self.prepare(transaction_id, data)
        elif action == "commit":
            return self.commit(transaction_id)
        raise ValueError(f"Unknown action: {action}")

    def prepare(self, transaction_id, data):
        self.prepare_called += 1
        if self.prepare_fails:
            raise Exception("Prepare failed")
        time.sleep(self.prepare_delay)
        if self.prepare_result:
            self.prepared.add(transaction_id)
        return self.prepare_result

    def commit(self, transaction_id):
        self.commit_called += 1
        if self.commit_fails:
            raise Exception("Commit failed")
        time.sleep(self.commit_delay)
        if transaction_id in self.prepared:
            self.committed.add(transaction_id)
            return True
        return False

class TransactionCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator()

    def test_basic_successful_transaction(self):
        service1 = MockService()
        service2 = MockService()
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.enlist_service(txn_id, service1, "data1")
        self.coordinator.enlist_service(txn_id, service2, "data2")
        
        result = self.coordinator.commit_transaction(txn_id)
        
        self.assertTrue(result)
        self.assertEqual(len(service1.committed), 1)
        self.assertEqual(len(service2.committed), 1)
        self.assertTrue(txn_id in service1.committed)
        self.assertTrue(txn_id in service2.committed)

    def test_prepare_phase_failure(self):
        service1 = MockService()
        service2 = MockService(prepare_result=False)
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.enlist_service(txn_id, service1, "data1")
        self.coordinator.enlist_service(txn_id, service2, "data2")
        
        result = self.coordinator.commit_transaction(txn_id)
        
        self.assertFalse(result)
        self.assertEqual(len(service1.committed), 0)
        self.assertEqual(len(service2.committed), 0)

    def test_concurrent_transactions(self):
        service = MockService()
        results = []
        
        def run_transaction():
            txn_id = self.coordinator.begin_transaction()
            self.coordinator.enlist_service(txn_id, service, "data")
            results.append(self.coordinator.commit_transaction(txn_id))
        
        threads = [threading.Thread(target=run_transaction) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))
        self.assertEqual(len(service.committed), 10)

    def test_service_timeout(self):
        service = MockService(prepare_delay=6)  # Longer than default timeout
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.enlist_service(txn_id, service, "data")
        
        result = self.coordinator.commit_transaction(txn_id)
        
        self.assertFalse(result)
        self.assertEqual(len(service.committed), 0)

    def test_idempotent_commit(self):
        service = MockService()
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.enlist_service(txn_id, service, "data")
        
        first_result = self.coordinator.commit_transaction(txn_id)
        second_result = self.coordinator.commit_transaction(txn_id)
        
        self.assertTrue(first_result)
        self.assertTrue(second_result)
        self.assertEqual(service.prepare_called, 1)
        self.assertEqual(service.commit_called, 1)

    def test_commit_retry_on_failure(self):
        service = MockService(commit_fails=True)
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.enlist_service(txn_id, service, "data")
        
        result = self.coordinator.commit_transaction(txn_id)
        
        self.assertFalse(result)
        self.assertTrue(service.commit_called > 1)  # Should have retried

    def test_unique_transaction_ids(self):
        txn_ids = set()
        for _ in range(1000):
            txn_ids.add(self.coordinator.begin_transaction())
        
        self.assertEqual(len(txn_ids), 1000)

    def test_no_services_enrolled(self):
        txn_id = self.coordinator.begin_transaction()
        result = self.coordinator.commit_transaction(txn_id)
        self.assertTrue(result)

    def test_invalid_transaction_id(self):
        with self.assertRaises(ValueError):
            self.coordinator.commit_transaction("invalid_id")

    def test_prepare_exception_handling(self):
        service = MockService(prepare_fails=True)
        
        txn_id = self.coordinator.begin_transaction()
        self.coordinator.enlist_service(txn_id, service, "data")
        
        result = self.coordinator.commit_transaction(txn_id)
        
        self.assertFalse(result)
        self.assertEqual(len(service.committed), 0)

if __name__ == '__main__':
    unittest.main()