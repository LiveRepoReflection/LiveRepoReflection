import threading
import time

class TransactionManager:
    def __init__(self, service_interface, retry_count, retry_interval):
        self.service_interface = service_interface
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        # Dictionary to track active transactions.
        # Format: {transaction_id: {"services": [...], "abort_event": threading.Event()}}
        self.transactions = {}
        self._lock = threading.Lock()

    def _call_with_retry(self, func, service_id, transaction_id):
        for attempt in range(self.retry_count):
            try:
                result = func(service_id, transaction_id)
                if result is True:
                    return True
                # If result is explicitly False, no need to retry further.
                if result is False:
                    return False
            except Exception:
                # Exception encountered, wait and retry.
                time.sleep(self.retry_interval)
        return False

    def begin_transaction(self, transaction_id, participating_services):
        # Create and store an abort event for this transaction.
        abort_event = threading.Event()
        with self._lock:
            self.transactions[transaction_id] = {
                "services": participating_services,
                "abort_event": abort_event
            }

        prepared_services = []
        # Phase 1: Prepare
        for service_id in participating_services:
            if abort_event.is_set():
                self._rollback_services(transaction_id, prepared_services)
                self._cleanup_transaction(transaction_id)
                return False

            result = self._call_with_retry(self.service_interface.prepare, service_id, transaction_id)
            if result is True:
                prepared_services.append(service_id)
            else:
                # Prepare failed: rollback any prepared services.
                self._rollback_services(transaction_id, prepared_services)
                self._cleanup_transaction(transaction_id)
                return False

        # Before moving to commit phase, check if an abort was requested.
        if abort_event.is_set():
            self._rollback_services(transaction_id, prepared_services)
            self._cleanup_transaction(transaction_id)
            return False

        # Phase 2: Commit
        for service_id in participating_services:
            if abort_event.is_set():
                self._rollback_services(transaction_id, participating_services)
                self._cleanup_transaction(transaction_id)
                return False

            result = self._call_with_retry(self.service_interface.commit, service_id, transaction_id)
            if result is not True:
                # Commit failed, perform rollback on all services.
                self._rollback_services(transaction_id, participating_services)
                self._cleanup_transaction(transaction_id)
                return False

        self._cleanup_transaction(transaction_id)
        return True

    def abort_transaction(self, transaction_id):
        with self._lock:
            tx_data = self.transactions.get(transaction_id)
            if not tx_data:
                return
            tx_data["abort_event"].set()
            services = tx_data["services"]
        # Attempt to rollback all services for the aborted transaction.
        self._rollback_services(transaction_id, services)
        self._cleanup_transaction(transaction_id)

    def _rollback_services(self, transaction_id, services):
        for service_id in services:
            self._call_with_retry(self.service_interface.rollback, service_id, transaction_id)

    def _cleanup_transaction(self, transaction_id):
        with self._lock:
            if transaction_id in self.transactions:
                del self.transactions[transaction_id]