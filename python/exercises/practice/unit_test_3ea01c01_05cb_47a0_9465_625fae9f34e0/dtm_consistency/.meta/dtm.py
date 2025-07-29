import threading
import os
from enum import Enum

class TransactionState(Enum):
    ACTIVE = "ACTIVE"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    NON_EXISTENT = "NON_EXISTENT"

class DTM:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.transactions = {}
        self.lock = threading.Lock()
        self._initialize_log_file()

    def _initialize_log_file(self):
        with open(self.log_file_path, 'a'):
            pass

    def _log_action(self, action, transaction_id, service_id=None):
        with open(self.log_file_path, 'a') as log_file:
            if service_id is not None:
                log_file.write(f"{action} {transaction_id} {service_id}\n")
            else:
                log_file.write(f"{action} {transaction_id}\n")

    def begin_transaction(self, transaction_id):
        with self.lock:
            if transaction_id in self.transactions:
                raise ValueError("Transaction ID already exists")
            self.transactions[transaction_id] = {
                'state': TransactionState.ACTIVE,
                'prepared_services': set()
            }
            self._log_action("BEGIN", transaction_id)

    def prepare(self, transaction_id, service_id):
        with self.lock:
            if transaction_id not in self.transactions:
                raise ValueError("Transaction does not exist")
            if self.transactions[transaction_id]['state'] != TransactionState.ACTIVE:
                raise ValueError("Transaction is not in ACTIVE state")
            
            self.transactions[transaction_id]['prepared_services'].add(service_id)
            self._log_action("PREPARE", transaction_id, service_id)
            
            if len(self.transactions[transaction_id]['prepared_services']) > 0:
                self.transactions[transaction_id]['state'] = TransactionState.PREPARED

    def commit(self, transaction_id):
        with self.lock:
            if transaction_id not in self.transactions:
                raise ValueError("Transaction does not exist")
            if self.transactions[transaction_id]['state'] != TransactionState.PREPARED:
                raise ValueError("Transaction is not in PREPARED state")
            
            self.transactions[transaction_id]['state'] = TransactionState.COMMITTED
            self._log_action("COMMIT", transaction_id)

    def rollback(self, transaction_id):
        with self.lock:
            if transaction_id not in self.transactions:
                raise ValueError("Transaction does not exist")
            if self.transactions[transaction_id]['state'] not in [TransactionState.ACTIVE, TransactionState.PREPARED]:
                raise ValueError("Transaction cannot be rolled back in current state")
            
            self.transactions[transaction_id]['state'] = TransactionState.ROLLED_BACK
            self.transactions[transaction_id]['prepared_services'].clear()
            self._log_action("ROLLBACK", transaction_id)

    def get_transaction_state(self, transaction_id):
        with self.lock:
            if transaction_id not in self.transactions:
                return TransactionState.NON_EXISTENT.value
            return self.transactions[transaction_id]['state'].value