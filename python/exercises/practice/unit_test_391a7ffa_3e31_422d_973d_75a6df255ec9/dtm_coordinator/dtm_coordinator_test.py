import unittest
from threading import Thread
from random import randint
import time
from dtm_coordinator import TransactionCoordinator

class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator(5)  # Create coordinator with 5 services

    def test_basic_transaction_flow(self):
        # Test basic happy path
        self.assertTrue(self.coordinator.begin_transaction(1, {0, 1, 2}))
        self.assertEqual(self.coordinator.get_transaction_status(1), "PENDING")
        
        self.assertTrue(self.coordinator.prepare(1, 0))
        self.assertTrue(self.coordinator.prepare(1, 1))
        self.assertTrue(self.coordinator.prepare(1, 2))
        
        self.assertEqual(self.coordinator.get_transaction_status(1), "PREPARED")
        self.assertTrue(self.coordinator.commit_transaction(1))
        self.assertEqual(self.coordinator.get_transaction_status(1), "COMMITTED")

    def test_invalid_service_prepare(self):
        # Test preparing with invalid service
        self.coordinator.begin_transaction(1, {0, 1})
        self.assertFalse(self.coordinator.prepare(1, 2))  # Service 2 not part of transaction
        self.assertFalse(self.coordinator.prepare(1, 5))  # Service 5 doesn't exist

    def test_rollback(self):
        # Test rollback functionality
        self.coordinator.begin_transaction(1, {0, 1})
        self.coordinator.prepare(1, 0)
        self.coordinator.rollback_transaction(1)
        self.assertEqual(self.coordinator.get_transaction_status(1), "ROLLED_BACK")
        self.assertFalse(self.coordinator.commit_transaction(1))

    def test_commit_requirements(self):
        # Test that commit requires all services to prepare
        self.coordinator.begin_transaction(1, {0, 1, 2})
        self.coordinator.prepare(1, 0)
        self.coordinator.prepare(1, 1)
        # Service 2 hasn't prepared
        self.assertFalse(self.coordinator.commit_transaction(1))

    def test_nonexistent_transaction(self):
        # Test operations on non-existent transaction
        self.assertEqual(self.coordinator.get_transaction_status(999), "NOT_FOUND")
        self.assertFalse(self.coordinator.prepare(999, 0))
        self.assertFalse(self.coordinator.commit_transaction(999))

    def test_duplicate_prepare(self):
        # Test that a service can't prepare twice
        self.coordinator.begin_transaction(1, {0, 1})
        self.assertTrue(self.coordinator.prepare(1, 0))
        self.assertFalse(self.coordinator.prepare(1, 0))

    def test_concurrent_transactions(self):
        def run_transaction(tid, services):
            self.coordinator.begin_transaction(tid, services)
            for service in services:
                self.coordinator.prepare(tid, service)
            self.coordinator.commit_transaction(tid)

        # Create 10 concurrent transactions
        threads = []
        for i in range(10):
            services = set(range(3))  # Use first 3 services
            t = Thread(target=run_transaction, args=(i, services))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify all transactions committed
        for i in range(10):
            self.assertEqual(self.coordinator.get_transaction_status(i), "COMMITTED")

    def test_concurrent_prepare(self):
        self.coordinator.begin_transaction(1, {0, 1, 2})
        
        def prepare_service(service_id):
            time.sleep(randint(1, 10) / 1000)  # Random delay
            self.coordinator.prepare(1, service_id)

        threads = []
        for service_id in range(3):
            t = Thread(target=prepare_service, args=(service_id,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(self.coordinator.get_transaction_status(1), "PREPARED")
        self.assertTrue(self.coordinator.commit_transaction(1))

    def test_rollback_after_partial_prepare(self):
        self.coordinator.begin_transaction(1, {0, 1, 2})
        self.coordinator.prepare(1, 0)
        self.coordinator.prepare(1, 1)
        self.coordinator.rollback_transaction(1)
        self.coordinator.prepare(1, 2)  # Try to prepare after rollback
        self.assertEqual(self.coordinator.get_transaction_status(1), "ROLLED_BACK")
        self.assertFalse(self.coordinator.commit_transaction(1))

    def test_large_scale_transaction(self):
        # Test with maximum number of services
        large_coordinator = TransactionCoordinator(10**5)
        services = set(range(10**5))
        self.assertTrue(large_coordinator.begin_transaction(1, services))
        
        # Test prepare for first and last service
        self.assertTrue(large_coordinator.prepare(1, 0))
        self.assertTrue(large_coordinator.prepare(1, 10**5 - 1))

if __name__ == '__main__':
    unittest.main()