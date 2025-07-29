import threading
from enum import Enum

class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    NON_EXISTENT = "NON_EXISTENT"

class TransactionManager:
    def __init__(self):
        self.transactions = {}
        self.lock = threading.RLock()

    def begin_transaction(self, transaction_id):
        with self.lock:
            if transaction_id in self.transactions:
                return False
            
            self.transactions[transaction_id] = {
                'status': TransactionStatus.PENDING,
                'participants': set(),
                'committed': set(),
                'rolled_back': set()
            }
            return True

    def register_participant(self, transaction_id, service_id):
        with self.lock:
            tx = self.transactions.get(transaction_id)
            if not tx or tx['status'] != TransactionStatus.PENDING:
                return False
            
            if service_id in tx['participants']:
                return False
                
            tx['participants'].add(service_id)
            return True

    def service_commit(self, transaction_id, service_id):
        with self.lock:
            tx = self.transactions.get(transaction_id)
            if not tx or tx['status'] != TransactionStatus.PENDING:
                return False
                
            if service_id not in tx['participants']:
                return False
                
            if service_id in tx['committed'] or service_id in tx['rolled_back']:
                return False
                
            tx['committed'].add(service_id)
            
            if tx['committed'] == tx['participants']:
                tx['status'] = TransactionStatus.COMMITTED
                
            return True

    def service_rollback(self, transaction_id, service_id):
        with self.lock:
            tx = self.transactions.get(transaction_id)
            if not tx or tx['status'] != TransactionStatus.PENDING:
                return False
                
            if service_id not in tx['participants']:
                return False
                
            if service_id in tx['committed'] or service_id in tx['rolled_back']:
                return False
                
            tx['rolled_back'].add(service_id)
            tx['status'] = TransactionStatus.ROLLED_BACK
            return True

    def get_transaction_status(self, transaction_id):
        with self.lock:
            tx = self.transactions.get(transaction_id)
            if not tx:
                return TransactionStatus.NON_EXISTENT.value
            return tx['status'].value