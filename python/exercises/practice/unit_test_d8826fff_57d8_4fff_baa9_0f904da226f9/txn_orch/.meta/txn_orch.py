import threading
import uuid

class TransactionCoordinator:
    def __init__(self):
        self.transactions = {}  # Mapping from transaction_id to list of participants.
        self.lock = threading.Lock()

    def begin_transaction(self):
        txn_id = uuid.uuid4().hex
        with self.lock:
            self.transactions[txn_id] = []
        return txn_id

    def register_participant(self, transaction_id, service_name, commit_function, rollback_function):
        with self.lock:
            if transaction_id not in self.transactions:
                raise ValueError("Transaction ID does not exist")
            self.transactions[transaction_id].append((service_name, commit_function, rollback_function))

    def commit_transaction(self, transaction_id):
        with self.lock:
            if transaction_id not in self.transactions:
                raise ValueError("Transaction ID does not exist")
            participants = self.transactions[transaction_id].copy()
        commit_exception = None
        for _, commit_func, _ in participants:
            try:
                commit_func()
            except Exception as e:
                commit_exception = e
                break
        if commit_exception is not None:
            self.rollback_transaction(transaction_id)
            raise commit_exception
        else:
            with self.lock:
                if transaction_id in self.transactions:
                    del self.transactions[transaction_id]

    def rollback_transaction(self, transaction_id):
        with self.lock:
            if transaction_id not in self.transactions:
                raise ValueError("Transaction ID does not exist")
            participants = self.transactions[transaction_id].copy()
            del self.transactions[transaction_id]
        for _, _, rollback_func in reversed(participants):
            try:
                rollback_func()
            except Exception:
                pass