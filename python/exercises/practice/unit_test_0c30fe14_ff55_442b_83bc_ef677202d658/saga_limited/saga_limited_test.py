import unittest
import threading
import time
from saga_limited import TransactionCoordinator

class SagaLimitedTest(unittest.TestCase):
    def setUp(self):
        # Initialize a new TransactionCoordinator instance for each test
        self.coordinator = TransactionCoordinator()

    def test_successful_transaction(self):
        # Start a transaction with all required services
        txn_id = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])
        # Simulate each service reporting success
        self.coordinator.service_success(txn_id, "Order")
        self.coordinator.service_success(txn_id, "Payment")
        self.coordinator.service_success(txn_id, "Inventory")
        self.coordinator.service_success(txn_id, "Shipping")
        # Check that the transaction was committed successfully
        status = self.coordinator.get_transaction_status(txn_id)
        self.assertEqual(status, "committed")

    def test_failed_transaction_compensation(self):
        # Start a transaction with all required services
        txn_id = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])
        # Simulate a mixture of service outcomes to trigger compensation
        self.coordinator.service_success(txn_id, "Order")
        self.coordinator.service_failure(txn_id, "Payment")
        # Even if subsequent services report success, the transaction should be compensated
        self.coordinator.service_success(txn_id, "Inventory")
        self.coordinator.service_success(txn_id, "Shipping")
        status = self.coordinator.get_transaction_status(txn_id)
        self.assertEqual(status, "compensated")

    def _simulate_service(self, txn_id, service, success, delay):
        time.sleep(delay)
        if success:
            self.coordinator.service_success(txn_id, service)
        else:
            self.coordinator.service_failure(txn_id, service)

    def test_concurrent_transactions(self):
        # Start two concurrent transactions
        txn_id1 = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])
        txn_id2 = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])

        threads = []

        # For txn_id1, simulate all services reporting success quickly.
        for service in ["Order", "Payment", "Inventory", "Shipping"]:
            t = threading.Thread(target=self._simulate_service, args=(txn_id1, service, True, 0.05))
            threads.append(t)

        # For txn_id2, simulate a failure in one service and success in others with a slight delay.
        for service in ["Order", "Payment", "Inventory", "Shipping"]:
            if service == "Payment":
                t = threading.Thread(target=self._simulate_service, args=(txn_id2, service, False, 0.1))
            else:
                t = threading.Thread(target=self._simulate_service, args=(txn_id2, service, True, 0.1))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        status1 = self.coordinator.get_transaction_status(txn_id1)
        status2 = self.coordinator.get_transaction_status(txn_id2)
        self.assertEqual(status1, "committed")
        self.assertEqual(status2, "compensated")

    def test_coordinator_restart(self):
        # Start a transaction and simulate partial success
        txn_id = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])
        self.coordinator.service_success(txn_id, "Order")
        # Simulate a coordinator crash and restart
        self.coordinator.restart()
        # After restart, the coordinator should preserve the state and continue processing responses
        self.coordinator.service_success(txn_id, "Payment")
        self.coordinator.service_success(txn_id, "Inventory")
        self.coordinator.service_success(txn_id, "Shipping")
        status = self.coordinator.get_transaction_status(txn_id)
        self.assertEqual(status, "committed")

    def test_idempotency(self):
        # Start a transaction and call the same service multiple times
        txn_id = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])
        self.coordinator.service_success(txn_id, "Order")
        self.coordinator.service_success(txn_id, "Order")
        self.coordinator.service_success(txn_id, "Payment")
        self.coordinator.service_success(txn_id, "Payment")
        self.coordinator.service_success(txn_id, "Inventory")
        self.coordinator.service_success(txn_id, "Shipping")
        self.coordinator.service_success(txn_id, "Shipping")
        status = self.coordinator.get_transaction_status(txn_id)
        self.assertEqual(status, "committed")

    def test_message_broker_outage_simulation(self):
        # Simulate a scenario where one of the service responses is delayed,
        # representing a temporary message broker outage.
        txn_id = self.coordinator.start_transaction(["Order", "Payment", "Inventory", "Shipping"])

        def delayed_response(txn_id, service, success, delay):
            time.sleep(delay)
            if success:
                self.coordinator.service_success(txn_id, service)
            else:
                self.coordinator.service_failure(txn_id, service)

        threads = []
        threads.append(threading.Thread(target=delayed_response, args=(txn_id, "Order", True, 0.1)))
        threads.append(threading.Thread(target=delayed_response, args=(txn_id, "Payment", True, 0.5)))
        threads.append(threading.Thread(target=delayed_response, args=(txn_id, "Inventory", True, 0.1)))
        threads.append(threading.Thread(target=delayed_response, args=(txn_id, "Shipping", True, 0.1)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        status = self.coordinator.get_transaction_status(txn_id)
        self.assertEqual(status, "committed")

if __name__ == '__main__':
    unittest.main()