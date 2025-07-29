import threading
import time
from typing import Dict, List, Optional, Set, Tuple

class DistributedTransactionManager:
    def __init__(self, num_shards: int):
        # Basic configuration
        self.num_shards = num_shards
        
        # Data structures for shards and their data
        self.shards: List[Dict[str, Dict[int, str]]] = [
            {} for _ in range(num_shards)
        ]
        # Each shard stores key -> {timestamp -> value} mapping
        
        # Data structures for transaction management
        self.active_transactions: Dict[int, Dict] = {}  # tid -> transaction data
        self.transaction_writes: Dict[int, List[Tuple[int, str, str]]] = {}  # tid -> [(shard_id, key, value)]
        self.committed_timestamps: Dict[int, int] = {}  # tid -> commit timestamp
        self.last_modified: Dict[int, Dict[str, int]] = [
            {} for _ in range(num_shards)
        ]  # shard_id -> {key -> timestamp}
        
        # Global timestamp for transaction management
        self.global_timestamp = 0
        
        # Locks for thread safety
        self.global_lock = threading.RLock()  # For global timestamp and transaction state
        self.shard_locks = [threading.RLock() for _ in range(num_shards)]  # One lock per shard
        self.transaction_locks: Dict[int, threading.RLock] = {}  # One lock per transaction
        
    def _get_next_timestamp(self) -> int:
        """Get the next global timestamp with thread safety."""
        with self.global_lock:
            self.global_timestamp += 1
            return self.global_timestamp
    
    def begin_transaction(self) -> int:
        """Begin a new transaction and return its TID."""
        with self.global_lock:
            # Assign a transaction ID
            tid = self._get_next_timestamp()
            
            # Initialize transaction data
            self.active_transactions[tid] = {
                'snapshot_id': self.global_timestamp,
                'read_set': set(),  # Track read keys for potential optimization
                'write_set': set(),  # Track write keys to check conflicts
            }
            
            self.transaction_writes[tid] = []
            self.transaction_locks[tid] = threading.RLock()
            
            return tid
    
    def read(self, tid: int, shard_id: int, key: str) -> Optional[str]:
        """Read a key from a shard at the transaction's snapshot time."""
        # Validate inputs
        if tid not in self.active_transactions or shard_id < 0 or shard_id >= self.num_shards:
            return None
        
        # Get transaction's snapshot ID
        snapshot_id = self.active_transactions[tid]['snapshot_id']
        
        # Track read for potential optimizations
        with self.transaction_locks[tid]:
            self.active_transactions[tid]['read_set'].add((shard_id, key))
        
        # Acquire lock for the shard
        with self.shard_locks[shard_id]:
            # Check if key exists in shard
            if key not in self.shards[shard_id]:
                return None
            
            # Find the most recent value as of the snapshot time
            versions = self.shards[shard_id][key]
            valid_timestamps = [ts for ts in versions.keys() if ts <= snapshot_id]
            
            if not valid_timestamps:
                return None  # No valid version exists at snapshot time
            
            latest_valid_timestamp = max(valid_timestamps)
            return versions[latest_valid_timestamp]
    
    def write(self, tid: int, shard_id: int, key: str, value: Optional[str]) -> None:
        """Record a write operation in the transaction's write set."""
        # Validate inputs
        if tid not in self.active_transactions or shard_id < 0 or shard_id >= self.num_shards:
            return
        
        # Track write for conflict detection
        with self.transaction_locks[tid]:
            self.active_transactions[tid]['write_set'].add((shard_id, key))
            self.transaction_writes[tid].append((shard_id, key, value))
    
    def commit_transaction(self, tid: int) -> bool:
        """Try to commit a transaction. Return True if successful, False otherwise."""
        # Validate inputs
        if tid not in self.active_transactions:
            return False
        
        # First phase: Check for write conflicts
        with self.global_lock:
            snapshot_id = self.active_transactions[tid]['snapshot_id']
            write_set = self.active_transactions[tid]['write_set']
            
            # Check for conflicts: any key in our write set modified after our snapshot?
            for shard_id, key in write_set:
                with self.shard_locks[shard_id]:
                    if key in self.last_modified[shard_id]:
                        last_mod_time = self.last_modified[shard_id][key]
                        if last_mod_time > snapshot_id:
                            # Conflict detected! Another transaction modified this key since we took our snapshot
                            self._rollback_internal(tid)
                            return False
            
            # No conflicts, prepare to commit with a new timestamp
            commit_timestamp = self._get_next_timestamp()
            self.committed_timestamps[tid] = commit_timestamp
            
            # Second phase: Apply changes to shards
            for shard_id, key, value in self.transaction_writes[tid]:
                with self.shard_locks[shard_id]:
                    # Update the last modified time for this key
                    self.last_modified[shard_id][key] = commit_timestamp
                    
                    # Handle key deletion
                    if value is None:
                        if key in self.shards[shard_id]:
                            # Add a tombstone marker at this timestamp
                            self.shards[shard_id][key][commit_timestamp] = None
                        continue
                    
                    # Create the key if it doesn't exist
                    if key not in self.shards[shard_id]:
                        self.shards[shard_id][key] = {}
                    
                    # Add the new version with the commit timestamp
                    self.shards[shard_id][key][commit_timestamp] = value
            
            # Clean up transaction state
            self._cleanup_transaction(tid)
            return True
    
    def rollback_transaction(self, tid: int) -> None:
        """Rollback a transaction, discarding all pending writes."""
        if tid in self.active_transactions:
            self._rollback_internal(tid)
    
    def _rollback_internal(self, tid: int) -> None:
        """Internal method to rollback a transaction."""
        # Clean up transaction resources
        self._cleanup_transaction(tid)
    
    def _cleanup_transaction(self, tid: int) -> None:
        """Clean up transaction data after commit or rollback."""
        with self.global_lock:
            if tid in self.active_transactions:
                del self.active_transactions[tid]
            if tid in self.transaction_writes:
                del self.transaction_writes[tid]
            if tid in self.transaction_locks:
                del self.transaction_locks[tid]
    
    def _vacuum_old_versions(self) -> None:
        """
        Clean up old versions of data that are no longer needed.
        This would be called periodically in a real implementation.
        """
        # Find the oldest active snapshot ID
        with self.global_lock:
            if not self.active_transactions:
                return  # No active transactions
            
            oldest_snapshot = min(tx['snapshot_id'] for tx in self.active_transactions.values())
            
            # Clean up versions older than the oldest snapshot
            for shard_id in range(self.num_shards):
                with self.shard_locks[shard_id]:
                    for key in list(self.shards[shard_id].keys()):
                        versions = self.shards[shard_id][key]
                        # Keep only versions newer than or equal to the oldest snapshot
                        # and the newest version older than the oldest snapshot
                        old_timestamps = [ts for ts in versions.keys() if ts < oldest_snapshot]
                        if old_timestamps:
                            # Keep only the newest version older than oldest_snapshot
                            newest_old = max(old_timestamps)
                            to_delete = [ts for ts in old_timestamps if ts != newest_old]
                            for ts in to_delete:
                                del versions[ts]
                        
                        # If all versions are None (tombstones), we can remove the key entirely
                        if all(v is None for v in versions.values()):
                            del self.shards[shard_id][key]