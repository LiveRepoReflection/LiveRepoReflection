import threading
import uuid
import time
import copy
from enum import Enum


class TransactionStatus(Enum):
    ACTIVE = 1
    PREPARING = 2
    PREPARED = 3
    COMMITTING = 4
    COMMITTED = 5
    ABORTING = 6
    ABORTED = 7


class TransactionManager:
    def __init__(self, lock_timeout=2.0):
        self.data_stores = {}
        self.transactions = {}
        self.store_locks = {}
        self.transaction_locks = {}
        self.global_lock = threading.RLock()
        self.lock_timeout = lock_timeout
        self.next_store_id = 0
        
    def create_data_store(self):
        """Creates a new data store and returns its ID."""
        with self.global_lock:
            store_id = self._get_next_store_id()
            self.data_stores[store_id] = {}
            self.store_locks[store_id] = threading.RLock()
            return store_id
    
    def _get_next_store_id(self):
        """Generate the next store ID and increment the counter."""
        store_id = self.next_store_id
        self.next_store_id += 1
        return store_id
    
    def get_data_store(self, data_store_id):
        """Returns a copy of the data store with the specified ID."""
        with self.global_lock:
            if data_store_id not in self.data_stores:
                raise ValueError(f"Data store with ID {data_store_id} not found.")
            with self.store_locks[data_store_id]:
                return copy.deepcopy(self.data_stores[data_store_id])
    
    def begin_transaction(self):
        """Starts a new transaction and returns a unique transaction ID."""
        with self.global_lock:
            transaction_id = str(uuid.uuid4())
            self.transactions[transaction_id] = {
                'status': TransactionStatus.ACTIVE,
                'operations': [],
                'acquired_locks': set(),
                'started_at': time.time()
            }
            self.transaction_locks[transaction_id] = threading.RLock()
            return transaction_id
    
    def add_operation(self, transaction_id, data_store_id, operation_type, key, value=None):
        """Adds an operation to the specified transaction."""
        if operation_type not in ["write", "delete"]:
            raise ValueError(f"Invalid operation type: {operation_type}")
        
        if data_store_id not in self.data_stores:
            raise ValueError(f"Data store with ID {data_store_id} not found.")
        
        with self.global_lock:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")
            
            transaction = self.transactions[transaction_id]
            if transaction['status'] != TransactionStatus.ACTIVE:
                raise ValueError(f"Transaction {transaction_id} is not active.")
            
            operation = {
                'data_store_id': data_store_id,
                'operation_type': operation_type,
                'key': key,
                'value': value
            }
            
            with self.transaction_locks[transaction_id]:
                transaction['operations'].append(operation)
    
    def read_value(self, transaction_id, data_store_id, key):
        """Reads a value from a data store within a transaction context."""
        if data_store_id not in self.data_stores:
            raise ValueError(f"Data store with ID {data_store_id} not found.")
        
        with self.global_lock:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")
            
            transaction = self.transactions[transaction_id]
            if transaction['status'] != TransactionStatus.ACTIVE:
                raise ValueError(f"Transaction {transaction_id} is not active.")
            
            # Try to acquire lock for reading
            data_store_lock = self.store_locks[data_store_id]
            if not data_store_lock.acquire(timeout=self.lock_timeout):
                self._abort_transaction_internal(transaction_id)
                raise TimeoutError(f"Deadlock detected - couldn't acquire lock on data store {data_store_id}")
            
            try:
                transaction['acquired_locks'].add(data_store_id)
                
                # Check if this transaction has a pending write for this key
                for op in transaction['operations']:
                    if op['data_store_id'] == data_store_id and op['key'] == key:
                        if op['operation_type'] == 'write':
                            return op['value']
                        elif op['operation_type'] == 'delete':
                            raise KeyError(f"Key {key} has been deleted in this transaction.")
                
                # If no pending write, read from the data store
                if key in self.data_stores[data_store_id]:
                    return self.data_stores[data_store_id][key]
                else:
                    raise KeyError(f"Key {key} not found in data store {data_store_id}")
            
            finally:
                data_store_lock.release()
    
    def commit_transaction(self, transaction_id):
        """Attempts to commit the specified transaction using two-phase commit."""
        with self.global_lock:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")
            
            transaction = self.transactions[transaction_id]
            with self.transaction_locks[transaction_id]:
                if transaction['status'] != TransactionStatus.ACTIVE:
                    raise ValueError(f"Transaction {transaction_id} is not active.")
                
                # Phase 1: Prepare
                transaction['status'] = TransactionStatus.PREPARING
                
                # Acquire locks for all involved data stores
                data_store_ids = {op['data_store_id'] for op in transaction['operations']}
                
                try:
                    for data_store_id in data_store_ids:
                        data_store_lock = self.store_locks[data_store_id]
                        if not data_store_lock.acquire(timeout=self.lock_timeout):
                            # Deadlock detected
                            self._abort_transaction_internal(transaction_id)
                            raise TimeoutError(f"Deadlock detected - couldn't acquire lock on data store {data_store_id}")
                        transaction['acquired_locks'].add(data_store_id)
                    
                    # Validate operations (e.g., check if keys to be deleted exist)
                    for operation in transaction['operations']:
                        data_store_id = operation['data_store_id']
                        key = operation['key']
                        operation_type = operation['operation_type']
                        
                        if operation_type == "delete" and key not in self.data_stores[data_store_id]:
                            # If delete operation and key doesn't exist, consider it an error
                            # Alternatively, you could make this a no-op
                            self._abort_transaction_internal(transaction_id)
                            raise KeyError(f"Key {key} not found in data store {data_store_id} for delete operation")
                    
                    # All validations passed
                    transaction['status'] = TransactionStatus.PREPARED
                    
                    # Phase 2: Commit
                    transaction['status'] = TransactionStatus.COMMITTING
                    
                    # Apply all operations
                    for operation in transaction['operations']:
                        data_store_id = operation['data_store_id']
                        operation_type = operation['operation_type']
                        key = operation['key']
                        value = operation['value']
                        
                        if operation_type == "write":
                            self.data_stores[data_store_id][key] = value
                        elif operation_type == "delete":
                            if key in self.data_stores[data_store_id]:
                                del self.data_stores[data_store_id][key]
                    
                    transaction['status'] = TransactionStatus.COMMITTED
                    
                except Exception as e:
                    # Any error during commit should trigger an abort
                    self._abort_transaction_internal(transaction_id)
                    raise e
                
                finally:
                    # Release all locks
                    self._release_all_locks(transaction_id)
    
    def abort_transaction(self, transaction_id):
        """Aborts the specified transaction."""
        with self.global_lock:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")
            
            self._abort_transaction_internal(transaction_id)
    
    def _abort_transaction_internal(self, transaction_id):
        """Internal method to abort a transaction and clean up resources."""
        with self.transaction_locks[transaction_id]:
            transaction = self.transactions[transaction_id]
            transaction['status'] = TransactionStatus.ABORTING
            
            # No changes to apply, just mark as aborted
            transaction['status'] = TransactionStatus.ABORTED
            
            # Release all locks
            self._release_all_locks(transaction_id)
    
    def _release_all_locks(self, transaction_id):
        """Releases all locks held by a transaction."""
        transaction = self.transactions[transaction_id]
        for data_store_id in transaction['acquired_locks']:
            if data_store_id in self.store_locks:
                try:
                    self.store_locks[data_store_id].release()
                except RuntimeError:
                    # Lock might not be held, which is fine
                    pass
        transaction['acquired_locks'].clear()
    
    def set_lock_timeout(self, timeout):
        """Sets the lock acquisition timeout for deadlock detection."""
        self.lock_timeout = timeout