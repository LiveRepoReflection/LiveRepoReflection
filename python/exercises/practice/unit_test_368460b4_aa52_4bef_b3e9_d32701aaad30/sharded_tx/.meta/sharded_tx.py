import threading
import time
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any, Union


class OperationType(Enum):
    READ = "READ"
    WRITE = "WRITE"


class TransactionStatus(Enum):
    RUNNING = "RUNNING"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"


@dataclass
class Operation:
    type: OperationType
    shard_id: int
    key: str
    value: Optional[str] = None


@dataclass
class Transaction:
    id: int
    operations: List[Operation]
    status: TransactionStatus = TransactionStatus.RUNNING
    start_time: float = 0.0
    commit_time: float = 0.0
    read_set: Set[Tuple[int, str]] = None
    write_set: Set[Tuple[int, str]] = None
    write_values: Dict[Tuple[int, str], str] = None
    read_values: Dict[Tuple[int, str], str] = None
    
    def __post_init__(self):
        self.read_set = set()
        self.write_set = set()
        self.write_values = {}
        self.read_values = {}
        self.start_time = time.time()


class ShardManager:
    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self.data = {}
        self.versions = defaultdict(list)  # key -> [(timestamp, value)]
        self.write_lock = threading.Lock()
        self.timestamp_lock = threading.Lock()
        self.current_timestamp = 0.0
    
    def get_current_timestamp(self) -> float:
        with self.timestamp_lock:
            if time.time() > self.current_timestamp:
                self.current_timestamp = time.time()
            else:
                self.current_timestamp += 0.000001  # Ensure unique timestamps
            return self.current_timestamp
    
    def read(self, key: str, read_timestamp: float) -> Optional[str]:
        """Read the most recent version of key that's older than read_timestamp"""
        with self.write_lock:
            if key not in self.versions:
                return None
            
            # Find the most recent version before read_timestamp
            for ts, value in reversed(self.versions[key]):
                if ts <= read_timestamp:
                    return value
            
            # No version found before read_timestamp
            return None
    
    def write(self, key: str, value: str, commit_timestamp: float) -> bool:
        """Write a new version of key with the given commit_timestamp"""
        with self.write_lock:
            # Add the new version
            self.versions[key].append((commit_timestamp, value))
            # Sort versions by timestamp
            self.versions[key].sort(key=lambda x: x[0])
            self.data[key] = value
            return True
    
    def check_write_conflict(self, key: str, read_timestamp: float, commit_timestamp: float) -> bool:
        """Check if there's a write conflict according to snapshot isolation rules"""
        with self.write_lock:
            # Look for any versions with timestamps between read_timestamp and commit_timestamp
            for ts, _ in self.versions[key]:
                if read_timestamp < ts < commit_timestamp:
                    return True  # Conflict found
            return False  # No conflict


class TransactionManager:
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.shards = [ShardManager(i) for i in range(num_shards)]
        self.transactions = {}
        self.global_lock = threading.Lock()
        self.committed_txs = set()
        self.aborted_txs = set()
    
    def start_transaction(self, tx_id: int, operations: List[dict]) -> Transaction:
        """Create and register a new transaction"""
        tx_operations = []
        for op in operations:
            # Validate operation format
            if "type" not in op or "shard_id" not in op or "key" not in op:
                raise ValueError(f"Invalid operation format: {op}")
            
            op_type = op["type"]
            if op_type not in [OperationType.READ.value, OperationType.WRITE.value]:
                raise ValueError(f"Invalid operation type: {op_type}")
            
            shard_id = op["shard_id"]
            if not (0 <= shard_id < self.num_shards):
                raise ValueError(f"Invalid shard_id: {shard_id}")
            
            if op_type == OperationType.WRITE.value and "value" not in op:
                raise ValueError(f"WRITE operation missing value: {op}")
            
            tx_operations.append(Operation(
                type=OperationType(op_type),
                shard_id=shard_id,
                key=op["key"],
                value=op.get("value")
            ))
        
        tx = Transaction(id=tx_id, operations=tx_operations)
        
        with self.global_lock:
            self.transactions[tx_id] = tx
        
        return tx
    
    def execute_transaction(self, tx: Transaction) -> bool:
        """Execute a transaction following snapshot isolation protocol"""
        try:
            # Phase 1: Read Phase - Read all data and buffer writes
            for op in tx.operations:
                if op.type == OperationType.READ:
                    # Add to read set
                    key_tuple = (op.shard_id, op.key)
                    tx.read_set.add(key_tuple)
                    
                    # Perform the read
                    result = self.shards[op.shard_id].read(op.key, tx.start_time)
                    tx.read_values[key_tuple] = result
                
                elif op.type == OperationType.WRITE:
                    # Add to write set
                    key_tuple = (op.shard_id, op.key)
                    tx.write_set.add(key_tuple)
                    tx.write_values[key_tuple] = op.value
                    
                    # For SI, we also need to read the current value to detect conflicts
                    if key_tuple not in tx.read_set:
                        tx.read_set.add(key_tuple)
                        result = self.shards[op.shard_id].read(op.key, tx.start_time)
                        tx.read_values[key_tuple] = result
            
            # Phase 2: Validation Phase - Check for write-write conflicts
            tx.commit_time = max([self.shards[shard_id].get_current_timestamp() 
                                for shard_id in set(s_id for s_id, _ in tx.write_set)])
            
            for shard_id, key in tx.write_set:
                # Check if any other transaction has written to this key since we started
                if self.shards[shard_id].check_write_conflict(key, tx.start_time, tx.commit_time):
                    raise ValueError(f"Write-write conflict detected for key {key} on shard {shard_id}")
            
            # Phase 3: Write Phase - Apply all writes
            for (shard_id, key), value in tx.write_values.items():
                self.shards[shard_id].write(key, value, tx.commit_time)
            
            # Commit the transaction
            tx.status = TransactionStatus.COMMITTED
            with self.global_lock:
                self.committed_txs.add(tx.id)
            
            return True
        
        except Exception as e:
            # Rollback the transaction
            tx.status = TransactionStatus.ABORTED
            with self.global_lock:
                self.aborted_txs.add(tx.id)
            
            return False


def process_transactions(num_shards: int, num_transactions: int, transactions: List[List[dict]]) -> List[bool]:
    """Process multiple transactions in parallel using snapshot isolation"""
    if num_transactions == 0:
        return []
    
    # Initialize the transaction manager
    tx_manager = TransactionManager(num_shards)
    
    # Start transactions
    tx_list = []
    for i in range(num_transactions):
        try:
            tx = tx_manager.start_transaction(i, transactions[i])
            tx_list.append(tx)
        except ValueError:
            # If transaction creation fails, mark it as aborted
            tx_manager.aborted_txs.add(i)
            tx_list.append(None)
    
    # Process transactions in parallel
    results = [False] * num_transactions
    
    with ThreadPoolExecutor(max_workers=min(32, num_transactions)) as executor:
        # Submit all valid transactions for execution
        future_to_tx = {}
        for tx in tx_list:
            if tx is not None:
                future = executor.submit(tx_manager.execute_transaction, tx)
                future_to_tx[future] = tx.id
        
        # Process results as they complete
        for future in as_completed(future_to_tx):
            tx_id = future_to_tx[future]
            try:
                result = future.result()
                results[tx_id] = result
            except Exception:
                results[tx_id] = False
    
    # Mark aborted transactions
    for tx_id in tx_manager.aborted_txs:
        if tx_id < len(results):
            results[tx_id] = False
    
    return results