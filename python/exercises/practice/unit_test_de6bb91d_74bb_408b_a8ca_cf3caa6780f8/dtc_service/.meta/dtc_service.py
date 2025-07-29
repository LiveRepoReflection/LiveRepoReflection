import uuid
import threading
import time

class ResourceManager:
    def __init__(self, rm_id):
        self.rm_id = rm_id

    def write(self, transaction_id, key, value):
        raise NotImplementedError("Subclasses must implement write method")

    def prepare(self, transaction_id):
        raise NotImplementedError("Subclasses must implement prepare method")

    def commit(self, transaction_id):
        raise NotImplementedError("Subclasses must implement commit method")

    def rollback(self, transaction_id):
        raise NotImplementedError("Subclasses must implement rollback method")

class TransactionCoordinator:
    def __init__(self):
        # mapping from rm_id to ResourceManager instance
        self.resource_managers = {}
        # mapping from transaction_id to set of rm_ids that participated
        self.transactions = {}
        self.lock = threading.Lock()

    def register_rm(self, rm_instance):
        self.resource_managers[rm_instance.rm_id] = rm_instance

    def begin_transaction(self):
        tid = str(uuid.uuid4())
        with self.lock:
            self.transactions[tid] = set()
        return tid

    def write(self, transaction_id, rm_id, key, value):
        with self.lock:
            if transaction_id not in self.transactions:
                self.transactions[transaction_id] = set()
        if rm_id not in self.resource_managers:
            return False
        rm = self.resource_managers[rm_id]
        result = rm.write(transaction_id, key, value)
        if result:
            with self.lock:
                self.transactions[transaction_id].add(rm_id)
        return result

    def prepare_transaction(self, transaction_id):
        # Get list of resource managers involved in the transaction
        with self.lock:
            rm_ids = list(self.transactions.get(transaction_id, []))
        prepare_results = {}
        threads = []

        def call_prepare(rm, tid, rm_id):
            try:
                res = rm.prepare(tid)
                prepare_results[rm_id] = res
            except Exception:
                prepare_results[rm_id] = False

        for rm_id in rm_ids:
            rm = self.resource_managers.get(rm_id)
            t = threading.Thread(target=call_prepare, args=(rm, transaction_id, rm_id))
            threads.append(t)
            t.start()

        # Wait for thread to finish with timeout of 1 second each
        for t in threads:
            t.join(timeout=1)

        # If any thread did not complete, mark its prepare as failed
        for rm_id in rm_ids:
            if rm_id not in prepare_results:
                prepare_results[rm_id] = False

        if all(prepare_results[rm_id] for rm_id in rm_ids):
            return True
        return False

    def commit_transaction(self, transaction_id):
        with self.lock:
            rm_ids = list(self.transactions.get(transaction_id, []))
        for rm_id in rm_ids:
            rm = self.resource_managers.get(rm_id)
            try:
                rm.commit(transaction_id)
            except Exception:
                pass
        with self.lock:
            if transaction_id in self.transactions:
                del self.transactions[transaction_id]

    def rollback_transaction(self, transaction_id):
        with self.lock:
            rm_ids = list(self.transactions.get(transaction_id, []))
        for rm_id in rm_ids:
            rm = self.resource_managers.get(rm_id)
            try:
                rm.rollback(transaction_id)
            except Exception:
                pass
        with self.lock:
            if transaction_id in self.transactions:
                del self.transactions[transaction_id]