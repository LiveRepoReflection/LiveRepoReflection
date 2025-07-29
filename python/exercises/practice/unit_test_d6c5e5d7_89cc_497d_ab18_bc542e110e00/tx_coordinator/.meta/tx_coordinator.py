import uuid
import threading
import time
from typing import Dict, List, Tuple, Any, Optional
from threading import Lock, RLock

class TransactionCoordinator:
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._services_lock = RLock()
        self._active_transactions: Dict[str, threading.Event] = {}
        self._transaction_locks: Dict[str, Lock] = {}
        self._MAX_RETRIES = 3
        self._RETRY_DELAY = 0.1  # seconds

    def register_service(self, service: Any) -> None:
        """Register a service with the coordinator."""
        with self._services_lock:
            if not hasattr(service, 'service_id'):
                raise ValueError("Service must have a service_id attribute")
            self._services[service.service_id] = service

    def begin_transaction(self) -> str:
        """Start a new transaction and return its ID."""
        transaction_id = str(uuid.uuid4())
        self._active_transactions[transaction_id] = threading.Event()
        self._transaction_locks[transaction_id] = Lock()
        return transaction_id

    def _retry_operation(self, operation, transaction_id: str, service: Any) -> bool:
        """Retry an operation with exponential backoff."""
        retry_count = 0
        while retry_count < self._MAX_RETRIES:
            try:
                operation(transaction_id)
                return True
            except Exception as e:
                retry_count += 1
                if retry_count == self._MAX_RETRIES:
                    return False
                time.sleep(self._RETRY_DELAY * (2 ** retry_count))
        return False

    def execute_transaction(self, transaction_id: str, 
                          operations: Dict[str, List[Tuple[str, Any]]]) -> bool:
        """Execute a distributed transaction using two-phase commit protocol."""
        if transaction_id not in self._active_transactions:
            raise ValueError("Invalid transaction ID")

        # Validate all services exist
        for service_id in operations.keys():
            if service_id not in self._services:
                raise ValueError(f"Unknown service: {service_id}")

        transaction_lock = self._transaction_locks[transaction_id]
        with transaction_lock:
            # Phase 1: Prepare
            prepared_services = []
            try:
                for service_id, ops in operations.items():
                    service = self._services[service_id]
                    try:
                        if service.prepare(transaction_id, ops):
                            prepared_services.append(service)
                        else:
                            # If any service fails to prepare, rollback all prepared services
                            self._rollback_services(prepared_services, transaction_id)
                            return False
                    except Exception as e:
                        # Handle service failure during prepare
                        self._rollback_services(prepared_services, transaction_id)
                        return False

                # Phase 2: Commit
                if not self._commit_services(prepared_services, transaction_id):
                    # If commit fails for any service, attempt rollback
                    self._rollback_services(prepared_services, transaction_id)
                    return False

                return True

            finally:
                # Cleanup
                self._cleanup_transaction(transaction_id)

    def _rollback_services(self, services: List[Any], transaction_id: str) -> None:
        """Rollback all prepared services."""
        for service in services:
            self._retry_operation(
                lambda tid: service.rollback(tid),
                transaction_id,
                service
            )

    def _commit_services(self, services: List[Any], transaction_id: str) -> bool:
        """Commit all prepared services."""
        for service in services:
            if not self._retry_operation(
                lambda tid: service.commit(tid),
                transaction_id,
                service
            ):
                return False
        return True

    def _cleanup_transaction(self, transaction_id: str) -> None:
        """Clean up transaction resources."""
        if transaction_id in self._active_transactions:
            self._active_transactions[transaction_id].set()
            del self._active_transactions[transaction_id]
        if transaction_id in self._transaction_locks:
            del self._transaction_locks[transaction_id]

    def get_service_state(self, service_id: str) -> Dict[str, Any]:
        """Get the current state of a service."""
        with self._services_lock:
            if service_id not in self._services:
                raise ValueError(f"Unknown service: {service_id}")
            return self._services[service_id].get_state()