from threading import Lock
from enum import Enum
from typing import Set, Dict, Optional

class TransactionStatus(Enum):
    PENDING = "PENDING"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    NOT_FOUND = "NOT_FOUND"

class Transaction:
    def __init__(self, transaction_id: int, involved_services: Set[int]):
        self.transaction_id = transaction_id
        self.involved_services = involved_services
        self.prepared_services: Set[int] = set()
        self.status = TransactionStatus.PENDING
        self.lock = Lock()

class TransactionCoordinator:
    def __init__(self, num_services: int):
        self.num_services = num_services
        self.transactions: Dict[int, Transaction] = {}
        self.global_lock = Lock()

    def begin_transaction(self, transaction_id: int, involved_services: Set[int]) -> bool:
        # Validate service IDs
        if not all(0 <= service_id < self.num_services for service_id in involved_services):
            return False

        with self.global_lock:
            # Check if transaction already exists
            if transaction_id in self.transactions:
                return False
            
            # Create new transaction
            self.transactions[transaction_id] = Transaction(transaction_id, involved_services)
            return True

    def prepare(self, transaction_id: int, service_id: int) -> bool:
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return False

        with transaction.lock:
            # Check if transaction can still accept preparations
            if transaction.status != TransactionStatus.PENDING:
                return False

            # Validate service is part of transaction
            if service_id not in transaction.involved_services:
                return False

            # Check if service already prepared
            if service_id in transaction.prepared_services:
                return False

            # Record preparation
            transaction.prepared_services.add(service_id)

            # Update status if all services have prepared
            if transaction.prepared_services == transaction.involved_services:
                transaction.status = TransactionStatus.PREPARED

            return True

    def commit_transaction(self, transaction_id: int) -> bool:
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return False

        with transaction.lock:
            # Can only commit if all services are prepared
            if transaction.status != TransactionStatus.PREPARED:
                return False

            transaction.status = TransactionStatus.COMMITTED
            return True

    def rollback_transaction(self, transaction_id: int) -> None:
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return

        with transaction.lock:
            # Can rollback if transaction hasn't committed
            if transaction.status not in {TransactionStatus.COMMITTED, TransactionStatus.ROLLED_BACK}:
                transaction.status = TransactionStatus.ROLLED_BACK

    def get_transaction_status(self, transaction_id: int) -> str:
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return TransactionStatus.NOT_FOUND.value
        return transaction.status.value

    def _get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        with self.global_lock:
            return self.transactions.get(transaction_id)