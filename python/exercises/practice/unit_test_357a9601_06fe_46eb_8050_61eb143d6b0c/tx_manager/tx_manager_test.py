import unittest
import threading
import time
from tx_manager.tx_manager import TransactionManager

# Exception definition (must match the one expected by TransactionManager)
class ServiceUnavailableException(Exception):
    pass

# A fake service interface to simulate various responses for testing.
class FakeServiceInterface:
    def __init__(self, behavior=None):
        """
        behavior: a dict mapping service_id to a dict containing keys:
          - 'prepare': a list of responses or exceptions for successive calls.
          - 'commit': a list of responses or exceptions for successive calls.
          - 'rollback': a list of responses or exceptions for successive calls.
        """
        self.behavior = behavior if behavior is not None else {}
        # Counters to track calls per service per method.
        self.counters = {}

    def _get_counter(self, service_id, method):
        key = (service_id, method)
        self.counters.setdefault(key, 0)
        cnt = self.counters[key]
        self.counters[key] += 1
        return cnt

    def prepare(self, service_id, transaction_id):
        cnt = self._get_counter(service_id, 'prepare')
        if service_id in self.behavior and 'prepare' in self.behavior[service_id]:
            responses = self.behavior[service_id]['prepare']
            # If counter exceeds provided responses, use the last one.
            resp = responses[min(cnt, len(responses) - 1)]
            if isinstance(resp, Exception):
                raise resp
            return resp
        # default: always ACK
        return True

    def commit(self, service_id, transaction_id):
        cnt = self._get_counter(service_id, 'commit')
        if service_id in self.behavior and 'commit' in self.behavior[service_id]:
            responses = self.behavior[service_id]['commit']
            resp = responses[min(cnt, len(responses) - 1)]
            if isinstance(resp, Exception):
                raise resp
            return resp
        # default: commit succeeds
        return True

    def rollback(self, service_id, transaction_id):
        cnt = self._get_counter(service_id, 'rollback')
        if service_id in self.behavior and 'rollback' in self.behavior[service_id]:
            responses = self.behavior[service_id]['rollback']
            resp = responses[min(cnt, len(responses) - 1)]
            if isinstance(resp, Exception):
                raise resp
            return resp
        # default: rollback succeeds
        return True


class TransactionManagerTest(unittest.TestCase):

    def test_successful_transaction(self):
        """All services acknowledge prepare and commit successfully."""
        # Fake service interface that always ACKs.
        service_interface = FakeServiceInterface()
        tm = TransactionManager(service_interface, retry_count=3, retry_interval=0.1)
        transaction_id = "tx_success"
        services = ["service1", "service2", "service3"]
        
        result = tm.begin_transaction(transaction_id, services)
        self.assertTrue(result, "Transaction should commit successfully when all services ACK.")

    def test_failed_prepare_transaction(self):
        """One service returns NACK during prepare phase, transaction should rollback."""
        # Configure one service to NACK.
        behavior = {
            "service2": {
                "prepare": [False]
            }
        }
        service_interface = FakeServiceInterface(behavior)
        tm = TransactionManager(service_interface, retry_count=2, retry_interval=0.1)
        transaction_id = "tx_fail_prepare"
        services = ["service1", "service2", "service3"]
        
        result = tm.begin_transaction(transaction_id, services)
        self.assertFalse(result, "Transaction should rollback if any service responds with NACK.")

    def test_retry_on_service_unavailable_prepare(self):
        """Simulate a service being temporarily unavailable during prepare, but eventually succeeding."""
        # Service3 will fail the first call with ServiceUnavailableException then ACK.
        behavior = {
            "service3": {
                "prepare": [ServiceUnavailableException("Service temporarily down"), True]
            }
        }
        service_interface = FakeServiceInterface(behavior)
        tm = TransactionManager(service_interface, retry_count=3, retry_interval=0.1)
        transaction_id = "tx_retry_prepare"
        services = ["service1", "service2", "service3"]

        result = tm.begin_transaction(transaction_id, services)
        self.assertTrue(result, "Transaction should commit when transient failures recover with retries.")

    def test_retry_on_service_unavailable_commit(self):
        """Simulate a service being temporarily unavailable during commit, but eventually succeeding."""
        # Service1 will succeed the prepare phase and then fail the first commit call.
        behavior = {
            "service1": {
                "commit": [ServiceUnavailableException("Service temporarily down"), True]
            }
        }
        service_interface = FakeServiceInterface(behavior)
        tm = TransactionManager(service_interface, retry_count=3, retry_interval=0.1)
        transaction_id = "tx_retry_commit"
        services = ["service1", "service2", "service3"]

        result = tm.begin_transaction(transaction_id, services)
        self.assertTrue(result, "Transaction should commit successfully after retrying commit phase.")

    def test_abort_transaction(self):
        """Test that an externally aborted transaction is rolled back."""
        # For this test, simulate a transaction that is in the midst of preparing.
        behavior = {
            "service1": {
                "prepare": [ServiceUnavailableException("Service busy")]
            },
            "service2": {
                "prepare": [True]
            }
        }
        service_interface = FakeServiceInterface(behavior)
        tm = TransactionManager(service_interface, retry_count=5, retry_interval=0.1)
        transaction_id = "tx_to_abort"
        services = ["service1", "service2"]

        # Start the transaction in a separate thread so we can abort it.
        transaction_result = [None]
        def run_transaction():
            transaction_result[0] = tm.begin_transaction(transaction_id, services)

        thread = threading.Thread(target=run_transaction)
        thread.start()
        # Allow some time for the transaction to begin.
        time.sleep(0.2)
        tm.abort_transaction(transaction_id)
        thread.join()
        # When aborted, the transaction should not commit.
        self.assertFalse(transaction_result[0], "Transaction should rollback when aborted externally.")

    def test_concurrent_transactions(self):
        """Test multiple transactions concurrently to ensure thread safety."""
        service_interface = FakeServiceInterface()
        tm = TransactionManager(service_interface, retry_count=3, retry_interval=0.05)
        
        transactions = [(f"tx_{i}", [f"service{i}", f"service_common"]) for i in range(5)]
        results = {}
        lock = threading.Lock()
        
        def run_transaction(tx_id, services):
            res = tm.begin_transaction(tx_id, services)
            with lock:
                results[tx_id] = res
        
        threads = []
        for tx_id, services in transactions:
            t = threading.Thread(target=run_transaction, args=(tx_id, services))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Expect all transactions to commit successfully.
        for tx_id, res in results.items():
            self.assertTrue(res, f"Transaction {tx_id} should commit successfully in concurrent execution.")

if __name__ == "__main__":
    unittest.main()