import unittest
import time
from unittest.mock import Mock, patch

from transaction_orchestrator import TransactionOrchestrator, Service

class TestTransactionOrchestrator(unittest.TestCase):
    def setUp(self):
        self.timeout = 5
        self.service1 = Service("service1", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})
        self.service2 = Service("service2", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})
        self.service3 = Service("service3", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})
        self.orchestrator = TransactionOrchestrator(timeout=self.timeout)

    def test_successful_transaction(self):
        services = [self.service1, self.service2, self.service3]
        result = self.orchestrator.execute_transaction(services)
        self.assertTrue(result)

    def test_failed_prepare_phase(self):
        self.service2 = Service("service2", {"prepare": 1.0, "commit": 0.0, "rollback": 0.0})
        services = [self.service1, self.service2, self.service3]
        result = self.orchestrator.execute_transaction(services)
        self.assertFalse(result)

    def test_timeout_during_prepare(self):
        def slow_prepare():
            time.sleep(6)
            return True

        mock_service = Mock()
        mock_service.prepare = slow_prepare
        mock_service.rollback.return_value = True
        
        services = [self.service1, mock_service, self.service3]
        result = self.orchestrator.execute_transaction(services)
        self.assertFalse(result)

    def test_failed_commit_phase(self):
        self.service3 = Service("service3", {"prepare": 0.0, "commit": 1.0, "rollback": 0.0})
        services = [self.service1, self.service2, self.service3]
        result = self.orchestrator.execute_transaction(services)
        self.assertFalse(result)

    def test_idempotent_commit(self):
        services = [self.service1]
        self.orchestrator.execute_transaction(services)
        # Second execution should not change the result
        result = self.orchestrator.execute_transaction(services)
        self.assertTrue(result)

    def test_idempotent_rollback(self):
        self.service1 = Service("service1", {"prepare": 1.0, "commit": 0.0, "rollback": 0.0})
        services = [self.service1]
        self.orchestrator.execute_transaction(services)
        # Second execution should not change the result
        result = self.orchestrator.execute_transaction(services)
        self.assertFalse(result)

    def test_large_scale_transaction(self):
        # Test with 100 services
        services = [Service(f"service{i}", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0}) 
                   for i in range(100)]
        start_time = time.time()
        result = self.orchestrator.execute_transaction(services)
        execution_time = time.time() - start_time
        
        self.assertTrue(result)
        self.assertLess(execution_time, 10)  # Should complete within 10 seconds

    def test_logging(self):
        services = [self.service1, self.service2]
        with self.assertLogs() as captured:
            self.orchestrator.execute_transaction(services)
        
        log_output = captured.output
        self.assertTrue(any("Phase 1: Prepare" in message for message in log_output))
        self.assertTrue(any("Phase 2: Commit" in message for message in log_output))

    @patch('transaction_orchestrator.Service')
    def test_deadlock_prevention(self, mock_service):
        # Simulate two services trying to access the same resource
        service1 = mock_service("service1")
        service2 = mock_service("service2")
        
        def prepare_with_lock():
            time.sleep(0.1)  # Simulate resource access delay
            return True
            
        service1.prepare.side_effect = prepare_with_lock
        service2.prepare.side_effect = prepare_with_lock
        
        services = [service1, service2]
        result = self.orchestrator.execute_transaction(services)
        self.assertTrue(result)

    def test_partial_failure_handling(self):
        # Test scenario where some services succeed and others fail
        self.service1 = Service("service1", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})
        self.service2 = Service("service2", {"prepare": 1.0, "commit": 0.0, "rollback": 0.0})
        self.service3 = Service("service3", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})
        
        services = [self.service1, self.service2, self.service3]
        result = self.orchestrator.execute_transaction(services)
        self.assertFalse(result)

    def test_concurrent_transactions(self):
        # Test multiple transactions running concurrently
        services1 = [Service("s1", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})]
        services2 = [Service("s2", {"prepare": 0.0, "commit": 0.0, "rollback": 0.0})]
        
        import threading
        results = []
        
        def run_transaction(services):
            result = self.orchestrator.execute_transaction(services)
            results.append(result)
            
        t1 = threading.Thread(target=run_transaction, args=(services1,))
        t2 = threading.Thread(target=run_transaction, args=(services2,))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(results))

if __name__ == '__main__':
    unittest.main()