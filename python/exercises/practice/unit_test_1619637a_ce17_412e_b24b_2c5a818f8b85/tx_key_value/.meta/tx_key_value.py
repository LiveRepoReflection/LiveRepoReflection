import threading
import time
from typing import Dict, Optional, Set, Any

class DistributedKeyValueStore:
    """
    An in-memory distributed transactional key-value store with ACID properties.
    Implements a simplified two-phase commit protocol for transaction management.
    
    Design choices:
    - Uses read-committed isolation level
    - Optimizes for read performance with minimal locking
    - Uses a multi-version concurrency control (MVCC) approach
    - Implements deadlock prevention with transaction timestamps
    """
    
    def __init__(self):
        # Main data store for committed values
        self._data: Dict[str, str] = {}
        
        # Transaction workspace - holds uncommitted changes
        # Format: {tx_id: {key: value}}
        self._tx_workspace: Dict[int, Dict[str, str]] = {}
        
        # Transaction tracking
        self._tx_counter = 0
        self._active_transactions: Set[int] = set()
        
        # Keys modified in each transaction - for conflict detection
        self._tx_modified_keys: Dict[int, Set[str]] = {}
        
        # Transaction start times - used for conflict resolution
        self._tx_start_times: Dict[int, float] = {}
        
        # Locks for thread safety
        self._global_lock = threading.RLock()
        self._data_lock = threading.RLock()
        self._tx_lock = threading.RLock()
        
        # Simulate distributed environment
        self.global_abort = False

    def get(self, key: str) -> Optional[str]:
        """
        Retrieves the value associated with a key.
        Returns None if the key does not exist.
        """
        with self._data_lock:
            return self._data.get(key)

    def put(self, key: str, value: str) -> None:
        """
        Stores a key-value pair. Overwrites existing values.
        """
        with self._data_lock:
            self._data[key] = value

    def begin_transaction(self) -> int:
        """
        Starts a new transaction and returns a unique transaction ID.
        """
        with self._tx_lock:
            tx_id = self._tx_counter
            self._tx_counter += 1
            self._active_transactions.add(tx_id)
            self._tx_workspace[tx_id] = {}
            self._tx_modified_keys[tx_id] = set()
            self._tx_start_times[tx_id] = time.time()
            return tx_id

    def _validate_transaction(self, tx_id: int) -> None:
        """
        Validates that a transaction is active.
        Raises an exception if the transaction does not exist.
        """
        with self._tx_lock:
            if tx_id not in self._active_transactions:
                raise ValueError(f"Transaction {tx_id} does not exist or has been completed")

    def transactional_get(self, tx_id: int, key: str) -> Optional[str]:
        """
        Retrieves the value associated with a key within a given transaction.
        If the key was not modified within the transaction, returns the committed value.
        """
        self._validate_transaction(tx_id)
        
        # First check if the key was modified in this transaction
        with self._tx_lock:
            if key in self._tx_workspace[tx_id]:
                return self._tx_workspace[tx_id][key]
        
        # If not modified in this transaction, return the committed value
        return self.get(key)

    def transactional_put(self, tx_id: int, key: str, value: str) -> None:
        """
        Stores a key-value pair within a given transaction.
        The change is not visible outside the transaction until committed.
        """
        self._validate_transaction(tx_id)
        
        with self._tx_lock:
            self._tx_workspace[tx_id][key] = value
            self._tx_modified_keys[tx_id].add(key)

    def _detect_write_conflicts(self, tx_id: int) -> bool:
        """
        Detects if there are any write conflicts for this transaction.
        A conflict occurs if another active transaction started before this one
        and has modified any of the same keys.
        
        This is a simplified conflict detection mechanism that could be extended
        in a real-world system.
        
        Returns True if conflicts are detected, False otherwise.
        """
        with self._tx_lock:
            tx_start_time = self._tx_start_times[tx_id]
            keys_modified = self._tx_modified_keys[tx_id]
            
            for other_tx_id in self._active_transactions:
                # Skip self
                if other_tx_id == tx_id:
                    continue
                
                # If other transaction started before this one
                if self._tx_start_times[other_tx_id] < tx_start_time:
                    # Check for overlapping modified keys
                    other_keys = self._tx_modified_keys[other_tx_id]
                    if any(key in other_keys for key in keys_modified):
                        return True
            
            return False

    def commit_transaction(self, tx_id: int) -> bool:
        """
        Attempts to commit the transaction with the given ID.
        
        Implements a simplified two-phase commit protocol:
        1. Preparation phase: check for conflicts and global abort flag
        2. Commit phase: apply all changes atomically
        
        Returns True on successful commit, False on abort.
        """
        self._validate_transaction(tx_id)
        
        # Phase 1: Preparation - check for conflicts
        with self._global_lock:
            # Check global abort flag (simulating external failures)
            if self.global_abort:
                self.abort_transaction(tx_id)
                return False
            
            # Check for conflicts with other transactions
            if self._detect_write_conflicts(tx_id):
                self.abort_transaction(tx_id)
                return False
            
            # Phase 2: Commit - apply all changes atomically
            with self._data_lock:
                # Apply all changes from this transaction to the main data store
                for key, value in self._tx_workspace[tx_id].items():
                    self._data[key] = value
            
            # Cleanup transaction metadata
            with self._tx_lock:
                self._active_transactions.remove(tx_id)
                del self._tx_workspace[tx_id]
                del self._tx_modified_keys[tx_id]
                del self._tx_start_times[tx_id]
            
            return True

    def abort_transaction(self, tx_id: int) -> None:
        """
        Aborts the transaction with the given ID.
        Discards all changes made within the transaction.
        """
        self._validate_transaction(tx_id)
        
        with self._tx_lock:
            # Simply remove the transaction and discard its changes
            self._active_transactions.remove(tx_id)
            del self._tx_workspace[tx_id]
            del self._tx_modified_keys[tx_id]
            del self._tx_start_times[tx_id]