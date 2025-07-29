import threading
import time
import uuid
from typing import Dict, Set, Optional, Any, List, Tuple

class TransactionalStore:
    """
    A distributed transactional key-value store with snapshot isolation.
    
    This implementation provides snapshot isolation for concurrent transactions,
    optimized for read-heavy workloads.
    """
    
    def __init__(self):
        """Initialize the transactional store."""
        # Main data store: maps keys to (version, value) tuples
        self._data: Dict[str, List[Tuple[int, Any]]] = {}
        
        # Active transactions: maps transaction IDs to their metadata
        self._transactions: Dict[str, Dict] = {}
        
        # Global transaction counter (used for versioning)
        self._global_tx_counter: int = 0
        
        # Set of committed transaction IDs
        self._committed_transactions: Set[str] = set()
        
        # Set of aborted transaction IDs
        self._aborted_transactions: Set[str] = set()
        
        # Lock for synchronizing access to shared data structures
        self._lock = threading.RLock()
        
        # Current highest committed version number
        self._highest_committed_version: int = 0
    
    def begin_transaction(self) -> str:
        """
        Start a new transaction and return its unique identifier.
        
        Returns:
            str: A unique transaction identifier (TID)
        """
        with self._lock:
            # Generate a unique transaction ID
            tid = str(uuid.uuid4())
            
            # Create transaction metadata
            transaction = {
                'start_time': time.time(),
                'start_version': self._highest_committed_version,
                'read_set': set(),       # Keys read by this transaction
                'write_set': {},         # Keys written by this transaction (key -> value)
                'status': 'active'       # One of: active, committed, aborted
            }
            
            self._transactions[tid] = transaction
            return tid
    
    def read(self, tid: str, key: str) -> Optional[Any]:
        """
        Read the value associated with the given key within the specified transaction.
        
        Args:
            tid: The transaction identifier
            key: The key to read
            
        Returns:
            The value associated with the key, or None if the key doesn't exist
            or the transaction is invalid.
        """
        # Check if transaction is valid
        if not self._is_transaction_active(tid):
            return None
        
        with self._lock:
            transaction = self._transactions[tid]
            
            # First check if the key has been written by this transaction
            if key in transaction['write_set']:
                return transaction['write_set'][key]
            
            # Add to read set
            transaction['read_set'].add(key)
            
            # If key doesn't exist in the data store, return None
            if key not in self._data:
                return None
            
            # Get the snapshot version for this transaction
            snapshot_version = transaction['start_version']
            
            # Find the appropriate version for this transaction's snapshot
            versions = self._data[key]
            appropriate_version = None
            
            # Iterate through versions in reverse (newest to oldest)
            for version, value in reversed(versions):
                if version <= snapshot_version:
                    appropriate_version = value
                    break
            
            return appropriate_version
    
    def write(self, tid: str, key: str, value: Any) -> None:
        """
        Write the given value to the key within the specified transaction.
        
        Args:
            tid: The transaction identifier
            key: The key to write
            value: The value to associate with the key
        """
        # Check if transaction is valid
        if not self._is_transaction_active(tid):
            return
        
        with self._lock:
            # Add to write set
            self._transactions[tid]['write_set'][key] = value
    
    def commit_transaction(self, tid: str) -> bool:
        """
        Attempt to commit the specified transaction.
        
        If successful, all writes performed by the transaction become visible
        to subsequent transactions.
        
        Args:
            tid: The transaction identifier
            
        Returns:
            bool: True if commit successful, False otherwise
        """
        # Check if transaction exists and is active
        if tid not in self._transactions or self._transactions[tid]['status'] != 'active':
            return False
        
        with self._lock:
            transaction = self._transactions[tid]
            
            # Check for write-write conflicts
            if not self._check_write_write_conflicts(tid):
                transaction['status'] = 'aborted'
                self._aborted_transactions.add(tid)
                return False
            
            # Increment global transaction counter
            self._global_tx_counter += 1
            commit_version = self._global_tx_counter
            
            # Apply all writes to the data store with the new version
            for key, value in transaction['write_set'].items():
                if key not in self._data:
                    self._data[key] = []
                
                self._data[key].append((commit_version, value))
            
            # Update transaction status
            transaction['status'] = 'committed'
            transaction['commit_version'] = commit_version
            self._committed_transactions.add(tid)
            
            # Update highest committed version
            self._highest_committed_version = commit_version
            
            return True
    
    def abort_transaction(self, tid: str) -> bool:
        """
        Abort the specified transaction.
        
        All writes performed by the transaction are discarded.
        
        Args:
            tid: The transaction identifier
            
        Returns:
            bool: True if abort successful, False if TID is invalid
        """
        # Check if transaction exists and is active
        if tid not in self._transactions or self._transactions[tid]['status'] != 'active':
            return False
        
        with self._lock:
            # Mark transaction as aborted
            self._transactions[tid]['status'] = 'aborted'
            self._aborted_transactions.add(tid)
            
            return True
    
    def _is_transaction_active(self, tid: str) -> bool:
        """
        Check if a transaction is active.
        
        Args:
            tid: The transaction identifier
            
        Returns:
            bool: True if the transaction is active, False otherwise
        """
        return (tid in self._transactions and 
                self._transactions[tid]['status'] == 'active')
    
    def _check_write_write_conflicts(self, tid: str) -> bool:
        """
        Check for write-write conflicts before committing a transaction.
        
        A write-write conflict occurs when another transaction has committed
        changes to keys that this transaction is trying to write, and those
        changes happened after this transaction's snapshot.
        
        Args:
            tid: The transaction identifier
            
        Returns:
            bool: True if no conflicts found, False otherwise
        """
        transaction = self._transactions[tid]
        start_version = transaction['start_version']
        
        # For each key in the write set
        for key in transaction['write_set']:
            if key in self._data:
                # Check if any versions of this key were committed after our snapshot
                for version, _ in self._data[key]:
                    if version > start_version:
                        # Write-write conflict detected
                        return False
        
        return True

    """
    Scaling to a Distributed Environment:
    
    To scale this implementation to a distributed environment, several enhancements would be needed:
    
    1. Sharding:
       - Partition the key space across multiple nodes
       - Use consistent hashing to distribute keys
       - Implement a routing layer to direct requests to appropriate shards
       
    2. Replication:
       - Maintain multiple copies of each shard for fault tolerance
       - Implement a leader-follower model where writes go to the leader
       - Use asynchronous replication to followers
       
    3. Distributed Transaction Coordination:
       - Implement two-phase commit (2PC) or a consensus algorithm like Paxos/Raft
       - For transactions spanning multiple shards, use a coordinator
       - Consider using a timestamp oracle for maintaining global ordering
       
    4. Consistency:
       - For distributed snapshot isolation, implement a global version clock
       - Could use Hybrid Logical Clocks (HLC) or similar mechanisms
       - Consider techniques like MVCC (Multi-Version Concurrency Control)
       
    5. Failure Handling:
       - Implement heartbeats to detect node failures
       - Use a gossip protocol for failure detection and membership
       - Implement automatic failover mechanisms
       
    6. Transaction Recovery:
       - Maintain transaction logs for recovery after failures
       - Implement mechanisms to resolve in-doubt transactions
       
    7. Metadata Management:
       - Use a separate metadata service (like ZooKeeper) to track shards and replicas
       - Maintain global configuration and cluster state
       
    8. Performance Optimizations:
       - Local caching on each node
       - Batch operations for efficiency
       - Read from local replicas when possible
    """