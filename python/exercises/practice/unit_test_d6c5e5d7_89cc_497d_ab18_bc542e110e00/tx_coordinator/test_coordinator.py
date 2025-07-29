import unittest
from threading import Thread
import time
import uuid
from typing import Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class MockService:
    def __init__(self, service_id: str, should_fail: bool = False, fail_on_phase: str = None):
        self.service_id = service_id
        self.state: Dict[str, Any] = {}
        self.transaction_log: Dict[str, List[Tuple[str, Any]]] = {}
        self.should_fail = should_fail
        self.fail_on_phase = fail_on_phase
        self.prepare_called = False
        self.commit_called = False
        self.rollback_called = False

    def prepare(self, transaction_id: str, operations: List[Tuple[str, Any]]) -> bool:
        if self.should_fail and self.fail_on_phase == 'prepare':
            raise Exception(f"Simulated failure during prepare for service {self.service_id}")
        
        self.prepare_called = True
        self.transaction_log[transaction_id] = operations
        return True

    def commit(self, transaction_id: str):
        if self.should_fail and self.fail_on_phase == 'commit':
            raise Exception(f"Simulated failure during commit for service {self.service_id}")
        
        self.commit_called = True
        if transaction_id in self.transaction_log:
            operations = self.transaction_log[transaction_id]
            for key, value in operations:
                self.state[key] = value
            del self.transaction_log[transaction_id]

    def rollback(self, transaction_id: str):
        if self.should_fail and self.fail_on_phase == 'rollback':
            raise Exception(f"Simulated failure during rollback for service {self.service_id}")
        
        self.rollback_called = True
        if transaction_id in self.transaction_log:
            del self.transaction_log[transaction_id]

    def get_state(self) -> Dict[str, Any]:
        return self.state.copy()

class TransactionCoordinatorTest(unittest.TestCase):
    def setUp(self):
        try:
            from tx_coordinator import TransactionCoordinator
            self.coordinator_class = TransactionCoordinator
        except ImportError:
            self.fail("Could not import TransactionCoordinator class")

    def test_basic_successful_transaction(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        service2 = MockService("service2")
        
        coordinator.register_service(service1)
        coordinator.register_service(service2)
        
        transaction_id = coordinator.begin_transaction()
        
        operations = {
            "service1": [("key1", "value1")],
            "service2": [("key2", "value2")]
        }
        
        success = coordinator.execute_transaction(transaction_id, operations)
        
        self.assertTrue(success)
        self.assertEqual(service1.get_state(), {"key1": "value1"})
        self.assertEqual(service2.get_state(), {"key2": "value2"})

    def test_rollback_on_prepare_failure(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        service2 = MockService("service2", should_fail=True, fail_on_phase='prepare')
        
        coordinator.register_service(service1)
        coordinator.register_service(service2)
        
        transaction_id = coordinator.begin_transaction()
        
        operations = {
            "service1": [("key1", "value1")],
            "service2": [("key2", "value2")]
        }
        
        success = coordinator.execute_transaction(transaction_id, operations)
        
        self.assertFalse(success)
        self.assertEqual(service1.get_state(), {})
        self.assertEqual(service2.get_state(), {})

    def test_concurrent_transactions(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        service2 = MockService("service2")
        
        coordinator.register_service(service1)
        coordinator.register_service(service2)
        
        def run_transaction(tx_id: int):
            transaction_id = coordinator.begin_transaction()
            operations = {
                "service1": [(f"key{tx_id}", f"value{tx_id}")],
                "service2": [(f"key{tx_id}", f"value{tx_id}")]
            }
            return coordinator.execute_transaction(transaction_id, operations)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_transaction, i) for i in range(5)]
            results = [f.result() for f in as_completed(futures)]
        
        self.assertTrue(all(results))
        self.assertEqual(len(service1.get_state()), 5)
        self.assertEqual(len(service2.get_state()), 5)

    def test_retry_on_commit_failure(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        service2 = MockService("service2", should_fail=True, fail_on_phase='commit')
        
        coordinator.register_service(service1)
        coordinator.register_service(service2)
        
        transaction_id = coordinator.begin_transaction()
        
        operations = {
            "service1": [("key1", "value1")],
            "service2": [("key2", "value2")]
        }
        
        success = coordinator.execute_transaction(transaction_id, operations)
        
        self.assertFalse(success)

    def test_invalid_service_id(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        
        coordinator.register_service(service1)
        
        transaction_id = coordinator.begin_transaction()
        
        operations = {
            "service1": [("key1", "value1")],
            "nonexistent_service": [("key2", "value2")]
        }
        
        with self.assertRaises(Exception):
            coordinator.execute_transaction(transaction_id, operations)

    def test_empty_transaction(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        
        coordinator.register_service(service1)
        
        transaction_id = coordinator.begin_transaction()
        operations = {}
        
        success = coordinator.execute_transaction(transaction_id, operations)
        
        self.assertTrue(success)
        self.assertEqual(service1.get_state(), {})

    def test_get_service_state(self):
        coordinator = self.coordinator_class()
        service1 = MockService("service1")
        
        coordinator.register_service(service1)
        
        transaction_id = coordinator.begin_transaction()
        operations = {
            "service1": [("key1", "value1")]
        }
        
        coordinator.execute_transaction(transaction_id, operations)
        
        state = coordinator.get_service_state("service1")
        self.assertEqual(state, {"key1": "value1"})
        
        with self.assertRaises(Exception):
            coordinator.get_service_state("nonexistent_service")

if __name__ == '__main__':
    unittest.main()