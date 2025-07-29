import threading

class TransactionCoordinator:
    def __init__(self):
        self.lock = threading.RLock()
        # Maps transaction id to a set of locked resource ids.
        self.transaction_resources = {}
        # Maps resource id to the transaction id that currently holds the lock.
        self.resource_lock = {}
    
    def begin_transaction(self, transaction_id):
        with self.lock:
            if transaction_id in self.transaction_resources:
                raise ValueError("Transaction already in progress")
            self.transaction_resources[transaction_id] = set()

    def prepare(self, transaction_id, resource_ids):
        with self.lock:
            # Ensure the transaction has been started
            if transaction_id not in self.transaction_resources:
                raise ValueError("Transaction not found")
            # Check for duplicate resources in the list.
            if len(resource_ids) != len(set(resource_ids)):
                return False
            # Check if any resource is locked by another transaction.
            for res in resource_ids:
                if res in self.resource_lock:
                    if self.resource_lock[res] != transaction_id:
                        return False
            # Also check if any of these resources are already locked by the same transaction.
            # This is considered as duplicate prepare for the same resource.
            for res in resource_ids:
                if res in self.transaction_resources[transaction_id]:
                    return False
            # All checks passed. Lock the resources.
            for res in resource_ids:
                self.resource_lock[res] = transaction_id
                self.transaction_resources[transaction_id].add(res)
            return True
    
    def commit(self, transaction_id):
        with self.lock:
            if transaction_id in self.transaction_resources:
                for res in self.transaction_resources[transaction_id]:
                    if res in self.resource_lock and self.resource_lock[res] == transaction_id:
                        del self.resource_lock[res]
                del self.transaction_resources[transaction_id]
    
    def rollback(self, transaction_id):
        with self.lock:
            if transaction_id in self.transaction_resources:
                for res in self.transaction_resources[transaction_id]:
                    if res in self.resource_lock and self.resource_lock[res] == transaction_id:
                        del self.resource_lock[res]
                del self.transaction_resources[transaction_id]
    
    def status(self, resource_id):
        with self.lock:
            if resource_id in self.resource_lock:
                return "LOCKED"
            else:
                return "READY"