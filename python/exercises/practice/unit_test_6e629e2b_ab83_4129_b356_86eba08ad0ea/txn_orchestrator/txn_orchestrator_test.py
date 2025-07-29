import unittest
from unittest.mock import patch, MagicMock
from txn_orchestrator import TransactionOrchestrator

class TestTransactionOrchestrator(unittest.TestCase):
    def setUp(self):
        self.services = {
            'order': MagicMock(),
            'inventory': MagicMock(),
            'payment': MagicMock(),
            'shipping': MagicMock()
        }
        self.orchestrator = TransactionOrchestrator(self.services)
        
        # Configure mock services
        for service in self.services.values():
            service.prepare.return_value = True
            service.commit.return_value = True
            service.rollback.return_value = True

    def test_successful_transaction(self):
        """Test complete successful transaction flow"""
        result = self.orchestrator.process_order({
            'user_id': 123,
            'items': [{'id': 1, 'quantity': 2}],
            'payment': {'amount': 100, 'method': 'credit'}
        })
        self.assertTrue(result['success'])
        
        # Verify all services were called in correct order
        self.services['order'].prepare.assert_called_once()
        self.services['inventory'].prepare.assert_called_once()
        self.services['payment'].prepare.assert_called_once()
        self.services['shipping'].prepare.assert_called_once()
        
        self.services['order'].commit.assert_called_once()
        self.services['inventory'].commit.assert_called_once()
        self.services['payment'].commit.assert_called_once()
        self.services['shipping'].commit.assert_called_once()

    def test_failed_prepare_phase(self):
        """Test transaction failure during prepare phase"""
        self.services['payment'].prepare.return_value = False
        
        result = self.orchestrator.process_order({
            'user_id': 123,
            'items': [{'id': 1, 'quantity': 2}],
            'payment': {'amount': 100, 'method': 'credit'}
        })
        self.assertFalse(result['success'])
        
        # Verify rollback was called on services that prepared successfully
        self.services['order'].rollback.assert_called_once()
        self.services['inventory'].rollback.assert_called_once()
        self.services['payment'].rollback.assert_not_called()  # Failed prepare
        self.services['shipping'].rollback.assert_not_called()  # Not reached

    def test_service_timeout(self):
        """Test handling of service timeout during prepare"""
        self.services['inventory'].prepare.side_effect = TimeoutError("Service timeout")
        
        result = self.orchestrator.process_order({
            'user_id': 123,
            'items': [{'id': 1, 'quantity': 2}],
            'payment': {'amount': 100, 'method': 'credit'}
        })
        self.assertFalse(result['success'])
        
        # Verify rollback was called on services that prepared successfully
        self.services['order'].rollback.assert_called_once()
        self.services['inventory'].rollback.assert_not_called()  # Failed prepare
        self.services['payment'].rollback.assert_not_called()  # Not reached
        self.services['shipping'].rollback.assert_not_called()  # Not reached

    def test_idempotent_retry(self):
        """Test idempotency of service operations"""
        # First call fails on payment commit
        self.services['payment'].commit.side_effect = [TimeoutError("First attempt"), True]
        
        result = self.orchestrator.process_order({
            'user_id': 123,
            'items': [{'id': 1, 'quantity': 2}],
            'payment': {'amount': 100, 'method': 'credit'}
        })
        self.assertTrue(result['success'])
        
        # Verify payment commit was retried
        self.assertEqual(self.services['payment'].commit.call_count, 2)
        
        # Verify other services weren't called multiple times
        self.services['order'].commit.assert_called_once()
        self.services['inventory'].commit.assert_called_once()
        self.services['shipping'].commit.assert_called_once()

    def test_concurrent_transactions(self):
        """Test handling of concurrent transactions"""
        from threading import Thread
        
        results = []
        
        def run_transaction():
            result = self.orchestrator.process_order({
                'user_id': 123,
                'items': [{'id': 1, 'quantity': 1}],
                'payment': {'amount': 100, 'method': 'credit'}
            })
            results.append(result['success'])
        
        threads = [Thread(target=run_transaction) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # All transactions should succeed
        self.assertEqual(sum(results), 10)
        
        # Verify inventory was properly reserved for each transaction
        self.assertEqual(self.services['inventory'].prepare.call_count, 10)

if __name__ == '__main__':
    unittest.main()