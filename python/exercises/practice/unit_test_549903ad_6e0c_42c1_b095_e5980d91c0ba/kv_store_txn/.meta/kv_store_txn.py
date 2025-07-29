import threading
import time
import uuid
import enum
import copy
import logging
from typing import Dict, List, Set, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class TransactionStatus(enum.Enum):
    ACTIVE = 1
    COMMITTED = 2
    ABORTED = 3


class Transaction:
    """Represents a transaction in the distributed key-value store."""
    
    def __init__(self, txn_id: str, manager: 'TransactionManager'):
        self.txn_id = txn_id
        self.manager = manager
        self.status = TransactionStatus.ACTIVE
        self.read_set: Dict[str, Optional[str]] = {}  # Keys read and their values at the time of read
        self.write_set: Dict[str, Optional[str]] = {}  # Keys written and their values
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[str]:
        """Get the value of a key within this transaction."""
        with self.lock:
            if self.status != TransactionStatus.ACTIVE:
                raise RuntimeError(f"Transaction {self.txn_id} is {self.status.name}, not ACTIVE")
            
            # If the key is in the write set, return that value (Read-your-writes)
            if key in self.write_set:
                return self.write_set[key]
            
            # Otherwise, read from the store and add to read set
            value = self.manager.get(key)
            self.read_set[key] = value
            return value
    
    def put(self, key: str, value: str) -> None:
        """Set the value of a key within this transaction."""
        with self.lock:
            if self.status != TransactionStatus.ACTIVE:
                raise RuntimeError(f"Transaction {self.txn_id} is {self.status.name}, not ACTIVE")
            
            # Add to write set (will be applied to store on commit)
            self.write_set[key] = value
    
    def delete(self, key: str) -> None:
        """Delete a key within this transaction."""
        with self.lock:
            if self.status != TransactionStatus.ACTIVE:
                raise RuntimeError(f"Transaction {self.txn_id} is {self.status.name}, not ACTIVE")
            
            # Mark as None in the write set (will be handled as delete during commit)
            self.write_set[key] = None
    
    def commit(self) -> bool:
        """
        Attempt to commit the transaction.
        
        Returns:
            bool: True if the transaction was committed successfully, False otherwise.
        """
        with self.lock:
            if self.status != TransactionStatus.ACTIVE:
                return self.status == TransactionStatus.COMMITTED
            
            try:
                # Check for conflicts and prepare the transaction
                if not self.manager.prepare(self):
                    self.status = TransactionStatus.ABORTED
                    return False
                
                # If prepare succeeded, commit through the consensus module
                if self.manager.commit(self):
                    self.status = TransactionStatus.COMMITTED
                    return True
                else:
                    self.status = TransactionStatus.ABORTED
                    return False
            except Exception as e:
                logger.error(f"Error committing transaction {self.txn_id}: {e}")
                self.status = TransactionStatus.ABORTED
                return False
    
    def rollback(self) -> None:
        """Rollback the transaction, discarding all changes."""
        with self.lock:
            if self.status == TransactionStatus.ACTIVE:
                self.status = TransactionStatus.ABORTED
                self.manager.rollback(self)


class ConsensusModule:
    """
    Abstract base class representing a consensus module like Raft or Paxos.
    This would be provided as a "black box" in the actual implementation.
    """
    
    def propose(self, transaction):
        """
        Proposes a transaction to the consensus group. Blocks until the transaction is committed.
        Returns True if the transaction was successfully committed, False otherwise (e.g., leader failure).
        """
        raise NotImplementedError("ConsensusModule.propose must be implemented by subclasses")
    
    def get_committed_transactions(self):
        """
        Returns a list of committed transactions in the order they were committed.
        """
        raise NotImplementedError("ConsensusModule.get_committed_transactions must be implemented by subclasses")


class Node:
    """Represents a single node in the distributed key-value store cluster."""
    
    def __init__(self, node_id: str, consensus_module: ConsensusModule):
        self.node_id = node_id
        self.consensus_module = consensus_module
        self.local_store: Dict[str, str] = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from the local store."""
        with self.lock:
            return self.local_store.get(key)
    
    def apply_transaction(self, txn: 'TransactionRecord') -> None:
        """Apply a committed transaction to the local store."""
        with self.lock:
            for key, value in txn.write_set.items():
                if value is None:
                    # Delete operation
                    if key in self.local_store:
                        del self.local_store[key]
                else:
                    # Put operation
                    self.local_store[key] = value


class TransactionRecord:
    """Immutable record of a transaction for consensus and replication."""
    
    def __init__(self, txn_id: str, write_set: Dict[str, Optional[str]]):
        self.txn_id = txn_id
        self.write_set = dict(write_set)  # Make a copy for immutability
        self.timestamp = time.time()


class TransactionManager:
    """Manages transactions across the distributed system."""
    
    def __init__(self, node: 'Node'):
        self.node = node
        self.active_transactions: Dict[str, Transaction] = {}
        self.committed_txn_ids: Set[str] = set()
        self.lock = threading.RLock()
        self.last_applied_index = 0
        self.version_map: Dict[str, int] = {}  # key -> version number
    
    def create_transaction(self) -> Transaction:
        """Create a new transaction."""
        txn_id = str(uuid.uuid4())
        txn = Transaction(txn_id, self)
        with self.lock:
            self.active_transactions[txn_id] = txn
        return txn
    
    def get(self, key: str) -> Optional[str]:
        """Get the current value of a key from the local store."""
        # First apply any pending committed transactions
        self._apply_committed_transactions()
        # Then get the value from the local store
        return self.node.get(key)
    
    def prepare(self, txn: Transaction) -> bool:
        """
        Prepare a transaction for commit by checking for conflicts.
        Uses optimistic concurrency control.
        """
        with self.lock:
            # Apply any pending committed transactions first
            self._apply_committed_transactions()
            
            # Check for conflicts with the read set
            for key, read_value in txn.read_set.items():
                current_value = self.node.get(key)
                if read_value != current_value:
                    logger.info(f"Conflict detected for key {key}: read {read_value}, current {current_value}")
                    return False
                
            # No conflicts found
            return True
    
    def commit(self, txn: Transaction) -> bool:
        """
        Commit a transaction through the consensus module.
        """
        try:
            # Create an immutable transaction record for consensus
            txn_record = TransactionRecord(txn.txn_id, txn.write_set)
            
            # Propose the transaction to the consensus group
            if self.node.consensus_module.propose(txn_record):
                with self.lock:
                    self.committed_txn_ids.add(txn.txn_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Error during consensus commit for transaction {txn.txn_id}: {e}")
            return False
    
    def rollback(self, txn: Transaction) -> None:
        """Roll back a transaction, cleaning up any resources."""
        with self.lock:
            if txn.txn_id in self.active_transactions:
                del self.active_transactions[txn.txn_id]
    
    def _apply_committed_transactions(self) -> None:
        """Apply all committed transactions from the consensus log that haven't been applied yet."""
        with self.lock:
            # Get all committed transactions
            committed_transactions = self.node.consensus_module.get_committed_transactions()
            
            # Apply transactions that haven't been applied yet
            for i, txn_record in enumerate(committed_transactions[self.last_applied_index:], self.last_applied_index):
                self.node.apply_transaction(txn_record)
                self.last_applied_index = i + 1


class KeyValueStore:
    """
    Main interface for the distributed key-value store.
    Handles client operations and transaction management.
    """
    
    def __init__(self, node_id: str = "node1", consensus_module: Optional[ConsensusModule] = None):
        # If no consensus module is provided, create a default local one for testing
        self.consensus_module = consensus_module if consensus_module else self._create_local_consensus_module()
        self.node = Node(node_id, self.consensus_module)
        self.transaction_manager = TransactionManager(self.node)
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[str]:
        """
        Get the value for a key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value associated with the key, or None if the key doesn't exist
        """
        return self.transaction_manager.get(key)
    
    def put(self, key: str, value: str) -> bool:
        """
        Set the value for a key.
        
        Args:
            key: The key to set
            value: The value to associate with the key
            
        Returns:
            True if the operation succeeded, False otherwise
        """
        # Create a single-operation transaction for this put
        txn = self.begin_transaction()
        txn.put(key, value)
        return txn.commit()
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the store.
        
        Args:
            key: The key to delete
            
        Returns:
            True if the operation succeeded, False otherwise
        """
        # Create a single-operation transaction for this delete
        txn = self.begin_transaction()
        txn.delete(key)
        return txn.commit()
    
    def begin_transaction(self) -> Transaction:
        """
        Begin a new transaction.
        
        Returns:
            A new Transaction object
        """
        return self.transaction_manager.create_transaction()
    
    def _create_local_consensus_module(self) -> ConsensusModule:
        """Create a simple, local consensus module for testing or single-node operation."""
        return _LocalConsensusModule()


class _LocalConsensusModule(ConsensusModule):
    """
    A simple local implementation of the consensus module for testing or single-node operation.
    Not for production use in a distributed setting.
    """
    
    def __init__(self):
        self.committed_transactions = []
        self.lock = threading.RLock()
    
    def propose(self, transaction):
        """Simply append the transaction to the committed list."""
        with self.lock:
            self.committed_transactions.append(transaction)
            return True
    
    def get_committed_transactions(self):
        """Return a copy of the committed transactions list."""
        with self.lock:
            return list(self.committed_transactions)


def main():
    """Example usage of the distributed key-value store."""
    # Create a key-value store instance
    store = KeyValueStore()
    
    # Basic put and get operations
    store.put("hello", "world")
    print(f"Value for key 'hello': {store.get('hello')}")
    
    # Use a transaction for multiple operations
    txn = store.begin_transaction()
    txn.put("counter", "1")
    txn.put("message", "Hello from transaction!")
    txn.commit()
    
    print(f"Counter: {store.get('counter')}")
    print(f"Message: {store.get('message')}")
    
    # Update within a transaction
    txn = store.begin_transaction()
    counter_value = txn.get("counter")
    if counter_value is not None:
        txn.put("counter", str(int(counter_value) + 1))
    txn.commit()
    
    print(f"Updated counter: {store.get('counter')}")


if __name__ == "__main__":
    main()