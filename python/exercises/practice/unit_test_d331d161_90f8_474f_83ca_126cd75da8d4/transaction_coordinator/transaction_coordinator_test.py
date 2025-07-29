import threading
import unittest
from transaction_coordinator import TransactionCoordinator

class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator()

    def test_begin_transaction_success(self):
        # Start a new transaction and verify it exists
        txn_id = 1
        self.coordinator.begin_transaction(txn_id)
        # Attempting to begin the same transaction again should raise an exception
        with self.assertRaises(ValueError):
            self.coordinator.begin_transaction(txn_id)

    def test_prepare_success(self):
        txn_id = 2
        resources = [101, 102, 103]
        self.coordinator.begin_transaction(txn_id)
        # Prepare should lock all resources and return True
        result = self.coordinator.prepare(txn_id, resources)
        self.assertTrue(result)
        for res in resources:
            self.assertEqual(self.coordinator.status(res), "LOCKED")

    def test_prepare_duplicate_resource_in_same_transaction(self):
        txn_id = 3
        resources = [201, 202, 201]  # Duplicate resource 201
        self.coordinator.begin_transaction(txn_id)
        # Prepare should fail due to duplicate resource in the request
        result = self.coordinator.prepare(txn_id, resources)
        self.assertFalse(result)
        # Resources should remain in READY state
        for res in set(resources):
            self.assertEqual(self.coordinator.status(res), "READY")

    def test_prepare_fail_due_to_resource_locked_by_another_transaction(self):
        txn1 = 4
        txn2 = 5
        resources_txn1 = [301, 302]
        resources_txn2 = [302, 303]  # Resource 302 is common

        self.coordinator.begin_transaction(txn1)
        self.coordinator.begin_transaction(txn2)
        result1 = self.coordinator.prepare(txn1, resources_txn1)
        self.assertTrue(result1)
        # Attempt to prepare txn2 should fail because 302 is locked
        result2 = self.coordinator.prepare(txn2, resources_txn2)
        self.assertFalse(result2)
        
        # Verify resource status
        self.assertEqual(self.coordinator.status(301), "LOCKED")
        self.assertEqual(self.coordinator.status(302), "LOCKED")
        self.assertEqual(self.coordinator.status(303), "READY")

    def test_commit_releases_resources(self):
        txn_id = 6
        resources = [401, 402]
        self.coordinator.begin_transaction(txn_id)
        result = self.coordinator.prepare(txn_id, resources)
        self.assertTrue(result)
        # Confirm resources are locked
        for res in resources:
            self.assertEqual(self.coordinator.status(res), "LOCKED")
        self.coordinator.commit(txn_id)
        # Resources should be released after commit
        for res in resources:
            self.assertEqual(self.coordinator.status(res), "READY")

    def test_rollback_releases_resources(self):
        txn_id = 7
        resources = [501, 502]
        self.coordinator.begin_transaction(txn_id)
        result = self.coordinator.prepare(txn_id, resources)
        self.assertTrue(result)
        # Confirm resources are locked
        for res in resources:
            self.assertEqual(self.coordinator.status(res), "LOCKED")
        self.coordinator.rollback(txn_id)
        # Resources should be released after rollback
        for res in resources:
            self.assertEqual(self.coordinator.status(res), "READY")

    def test_commit_unknown_transaction(self):
        # Commit on a non-existent transaction should be ignored without error
        try:
            self.coordinator.commit(999)
        except Exception as e:
            self.fail("Commit on unknown transaction raised an exception: {}".format(e))

    def test_rollback_unknown_transaction(self):
        # Rollback on a non-existent transaction should be ignored without error
        try:
            self.coordinator.rollback(1000)
        except Exception as e:
            self.fail("Rollback on unknown transaction raised an exception: {}".format(e))

    def test_concurrent_prepare(self):
        txn_ids = list(range(10, 20))
        resource = 601  # Single shared resource for contention

        # Function for thread to attempt to acquire the resource
        def worker(txn_id, results):
            try:
                self.coordinator.begin_transaction(txn_id)
                res = self.coordinator.prepare(txn_id, [resource])
                results[txn_id] = res
            except Exception:
                results[txn_id] = False

        threads = []
        results = {}
        for txn_id in txn_ids:
            thread = threading.Thread(target=worker, args=(txn_id, results))
            threads.append(thread)

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Only one transaction should succeed in acquiring the lock for the shared resource
        successes = sum(1 for res in results.values() if res)
        self.assertEqual(successes, 1)
        # The resource should be locked
        self.assertEqual(self.coordinator.status(resource), "LOCKED")

    def test_resource_status_default(self):
        # Test that the status of an unaccessed resource is READY
        self.assertEqual(self.coordinator.status(701), "READY")

if __name__ == '__main__':
    unittest.main()