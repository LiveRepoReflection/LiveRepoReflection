import unittest
from unittest.mock import MagicMock, patch
from tx_orchestrator.transaction_coordinator import TransactionCoordinator

class TestService:
    def __init__(self, name):
        self.name = name
    
    def prepare(self, tx_id):
        return True
    
    def commit(self, tx_id):
        pass
    
    def rollback(self, tx_id):
        pass

class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        self.services = [
            TestService("InventoryService"),
            TestService("PaymentService"),
            TestService("ShippingService")
        ]
        self.tx_id = "tx_123"
        self.timeout = 5
        self.coordinator = TransactionCoordinator()

    def test_successful_transaction(self):
        with patch.object(TestService, 'prepare', return_value=True) as mock_prepare:
            result = self.coordinator.execute_transaction(
                self.services, self.tx_id, self.timeout
            )
            self.assertTrue(result)
            for service in self.services:
                mock_prepare.assert_any_call(self.tx_id)

    def test_failed_prepare_phase(self):
        failing_service = self.services[1]
        with patch.object(failing_service, 'prepare', return_value=False):
            result = self.coordinator.execute_transaction(
                self.services, self.tx_id, self.timeout
            )
            self.assertFalse(result)

    def test_timeout_during_prepare(self):
        def mock_prepare(tx_id):
            import time
            time.sleep(6)  # Exceeds timeout
            return True
            
        with patch.object(self.services[0], 'prepare', side_effect=mock_prepare):
            result = self.coordinator.execute_transaction(
                self.services, self.tx_id, self.timeout
            )
            self.assertFalse(result)

    def test_commit_after_successful_prepare(self):
        with patch.object(TestService, 'prepare', return_value=True), \
             patch.object(TestService, 'commit') as mock_commit:
            
            result = self.coordinator.execute_transaction(
                self.services, self.tx_id, self.timeout
            )
            self.assertTrue(result)
            for service in self.services:
                mock_commit.assert_any_call(self.tx_id)

    def test_rollback_after_failed_prepare(self):
        failing_service = self.services[1]
        with patch.object(failing_service, 'prepare', return_value=False), \
             patch.object(TestService, 'rollback') as mock_rollback:
            
            result = self.coordinator.execute_transaction(
                self.services, self.tx_id, self.timeout
            )
            self.assertFalse(result)
            for service in self.services:
                mock_rollback.assert_any_call(self.tx_id)

    def test_concurrent_transactions(self):
        import threading
        
        results = []
        def run_transaction(tx_id):
            result = self.coordinator.execute_transaction(
                self.services, tx_id, self.timeout
            )
            results.append(result)
        
        threads = [
            threading.Thread(target=run_transaction, args=(f"tx_{i}",))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))

if __name__ == '__main__':
    unittest.main()