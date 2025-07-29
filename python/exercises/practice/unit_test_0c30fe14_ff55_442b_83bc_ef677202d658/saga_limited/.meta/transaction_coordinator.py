import threading
import uuid

class TransactionCoordinator:
    def __init__(self):
        self.lock = threading.Lock()
        # transactions: txn_id -> { "services": {service: status}, "final_status": "pending"/"committed"/"compensated" }
        self.transactions = {}
    
    def start_transaction(self, services):
        with self.lock:
            txn_id = str(uuid.uuid4())
            self.transactions[txn_id] = {
                "services": {service: "pending" for service in services},
                "final_status": "pending"
            }
            return txn_id

    def service_success(self, txn_id, service):
        with self.lock:
            if txn_id not in self.transactions:
                return
            txn = self.transactions[txn_id]
            # Ensure idempotency: if already marked success, ignore.
            if txn["services"].get(service) == "success":
                return
            txn["services"][service] = "success"
            self._update_transaction_status(txn_id)

    def service_failure(self, txn_id, service):
        with self.lock:
            if txn_id not in self.transactions:
                return
            txn = self.transactions[txn_id]
            # Ensure idempotency: if already marked failed, ignore.
            if txn["services"].get(service) == "failed":
                return
            txn["services"][service] = "failed"
            self._update_transaction_status(txn_id)

    def _update_transaction_status(self, txn_id):
        txn = self.transactions[txn_id]
        # Do not update if transaction is already finalized.
        if txn["final_status"] != "pending":
            return

        # If any service has failed, mark transaction for compensation.
        if any(status == "failed" for status in txn["services"].values()):
            txn["final_status"] = "compensated"
            self._compensate(txn_id)
        # If all services succeeded, mark transaction as committed.
        elif all(status == "success" for status in txn["services"].values()):
            txn["final_status"] = "committed"

    def _compensate(self, txn_id):
        # Simulate triggering compensating transactions for services that succeeded.
        txn = self.transactions[txn_id]
        # In a full implementation, each service's compensation logic would be invoked.
        # Here, we assume compensations are handled concurrently by external systems.
        pass

    def get_transaction_status(self, txn_id):
        with self.lock:
            if txn_id not in self.transactions:
                return None
            return self.transactions[txn_id]["final_status"]

    def restart(self):
        # Simulate a coordinator restart where state is reloaded.
        with self.lock:
            # In a production system, this method would reload state from persistent storage.
            # Here, we simply continue operating with the in-memory state.
            pass