import threading
from collections import defaultdict, deque

class TransactionOrderingService:
    def __init__(self):
        self.resource_queues = defaultdict(deque)
        self.lock = threading.Lock()
        self.submission_order = 0
        self.submission_records = {}
        self.global_order = []

    def add_transaction(self, client_id, transaction_id, resource_id, operation):
        with self.lock:
            submission_id = self.submission_order
            self.submission_order += 1
            
            transaction = {
                'client_id': client_id,
                'transaction_id': transaction_id,
                'resource_id': resource_id,
                'operation': operation,
                'submission_id': submission_id
            }
            
            self.submission_records[submission_id] = transaction
            self.global_order.append(submission_id)
            self.resource_queues[resource_id].append(submission_id)

    def get_ordered_transactions(self, resource_id):
        with self.lock:
            if resource_id not in self.resource_queues:
                return []
                
            # Get all submission IDs for this resource
            submission_ids = list(self.resource_queues[resource_id])
            
            # Sort by submission order
            submission_ids.sort()
            
            # Reconstruct transactions in order
            ordered_transactions = []
            for sub_id in submission_ids:
                tx = self.submission_records[sub_id]
                ordered_transactions.append(
                    (tx['client_id'], tx['transaction_id'], tx['resource_id'], tx['operation'])
                )
            
            return ordered_transactions

    def get_all_ordered_transactions(self):
        with self.lock:
            ordered_transactions = []
            for sub_id in self.global_order:
                tx = self.submission_records[sub_id]
                ordered_transactions.append(
                    (tx['client_id'], tx['transaction_id'], tx['resource_id'], tx['operation'])
                )
            return ordered_transactions