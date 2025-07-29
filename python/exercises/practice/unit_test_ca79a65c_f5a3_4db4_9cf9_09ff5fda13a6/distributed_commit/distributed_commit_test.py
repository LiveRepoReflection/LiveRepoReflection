import unittest
import threading
import time

from distributed_commit.distributed_commit import TransactionManager

# Dummy service classes for testing

class AlwaysSuccessService:
    def prepare(self, transaction_id):
        return True
    def commit(self, transaction_id):
        return True
    def rollback(self, transaction_id):
        return True

class PrepareFailureService:
    def prepare(self, transaction_id):
        return False
    def commit(self, transaction_id):
        return True
    def rollback(self, transaction_id):
        return True

class CommitFailureService:
    def __init__(self, fail_attempts=2):
        self.attempts = 0
        self.fail_attempts = fail_attempts

    def prepare(self, transaction_id):
        return True

    def commit(self, transaction_id):
        # Fail for the first few attempts then succeed
        self.attempts += 1
        if self.attempts <= self.fail_attempts:
            return False
        return True

    def rollback(self, transaction_id):
        return True

class ExceptionService:
    def prepare(self, transaction_id):
        raise Exception("Simulated exception in prepare")
    def commit(self, transaction_id):
        return True
    def rollback(self, transaction_id):
        return True

class SlowService:
    # Simulate a service that takes longer than the timeout value
    def prepare(self, transaction_id):
        time.sleep(6)  # longer than the 5-second timeout
        return True
    def commit(self, transaction_id):
        time.sleep(6)
        return True
    def rollback(self, transaction_id):
        time.sleep(6)
        return True

class DistributedCommitTestCase(unittest.TestCase):

    def test_successful_transaction(self):
        tm = TransactionManager()
        service1 = AlwaysSuccessService()
        service2 = AlwaysSuccessService()
        tm.enlist_service(service1)
        tm.enlist_service(service2)
        tx_id = tm.begin_transaction()
        result = tm.commit_transaction(tx_id)
        self.assertTrue(result, "Transaction should commit successfully when all services succeed.")

    def test_prepare_failure_transaction(self):
        tm = TransactionManager()
        service1 = AlwaysSuccessService()
        service2 = PrepareFailureService()
        tm.enlist_service(service1)
        tm.enlist_service(service2)
        tx_id = tm.begin_transaction()
        result = tm.commit_transaction(tx_id)
        self.assertFalse(result, "Transaction should fail commit when a service fails during prepare.")

    def test_commit_retry_success(self):
        tm = TransactionManager()
        # Service that fails initial commit attempts but eventually succeeds after retries
        commit_fail_service = CommitFailureService(fail_attempts=2)
        service1 = AlwaysSuccessService()
        tm.enlist_service(service1)
        tm.enlist_service(commit_fail_service)
        tx_id = tm.begin_transaction()
        result = tm.commit_transaction(tx_id)
        self.assertTrue(result, "Transaction should eventually commit after retrying commit on a failing service.")

    def test_exception_during_prepare(self):
        tm = TransactionManager()
        service1 = AlwaysSuccessService()
        exception_service = ExceptionService()
        tm.enlist_service(service1)
        tm.enlist_service(exception_service)
        tx_id = tm.begin_transaction()
        result = tm.commit_transaction(tx_id)
        self.assertFalse(result, "Transaction should fail commit when a service raises an exception during prepare.")

    def test_manual_rollback(self):
        tm = TransactionManager()
        service1 = AlwaysSuccessService()
        tm.enlist_service(service1)
        tx_id = tm.begin_transaction()
        # Directly invoke rollback without attempting commit
        result = tm.rollback_transaction(tx_id)
        self.assertTrue(result, "Manual rollback should always return True.")

    def test_timeout_handling(self):
        tm = TransactionManager()
        slow_service = SlowService()
        tm.enlist_service(slow_service)
        tx_id = tm.begin_transaction()
        # The slow service should cause a timeout during the prepare phase.
        result = tm.commit_transaction(tx_id)
        self.assertFalse(result, "Transaction should fail if a service call times out.")

    def test_concurrent_transactions(self):
        tm = TransactionManager()
        results = []
        lock = threading.Lock()

        def run_transaction():
            # Each thread creates its own transaction using always success service.
            service = AlwaysSuccessService()
            tm.enlist_service(service)
            tx_id = tm.begin_transaction()
            res = tm.commit_transaction(tx_id)
            with lock:
                results.append(res)

        threads = []
        num_threads = 5
        for _ in range(num_threads):
            thread = threading.Thread(target=run_transaction)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(results), num_threads)
        self.assertTrue(all(results), "All concurrent transactions should commit successfully.")

if __name__ == '__main__':
    unittest.main()