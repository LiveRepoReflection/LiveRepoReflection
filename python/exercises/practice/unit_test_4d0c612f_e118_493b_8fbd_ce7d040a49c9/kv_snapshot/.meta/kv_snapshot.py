import threading
import time
from collections import defaultdict
from typing import Dict, Optional, Set, List
import uuid
from dataclasses import dataclass
from threading import Lock
import copy

@dataclass
class Version:
    value: bytes
    timestamp: int
    txn_id: str

@dataclass
class Transaction:
    id: str
    start_timestamp: int
    status: str  # 'active', 'committed', 'aborted'
    write_set: Set[str]
    read_set: Set[str]
    writes: Dict[str, bytes]

class Node:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.data: Dict[str, List[Version]] = defaultdict(list)
        self.lock = Lock()

    def read(self, key: str, timestamp: int) -> Optional[bytes]:
        with self.lock:
            versions = self.data.get(key, [])
            # Find the latest version that's earlier than our read timestamp
            for version in reversed(versions):
                if version.timestamp <= timestamp:
                    return version.value
        return None

    def write(self, key: str, value: bytes, timestamp: int, txn_id: str):
        with self.lock:
            version = Version(value, timestamp, txn_id)
            self.data[key].append(version)
            # Keep versions sorted by timestamp
            self.data[key].sort(key=lambda x: x.timestamp)

    def get_latest_version(self, key: str) -> Optional[Version]:
        with self.lock:
            versions = self.data.get(key, [])
            return versions[-1] if versions else None

class DistributedKVStore:
    def __init__(self, num_nodes: int = 3):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.transactions: Dict[str, Transaction] = {}
        self.global_lock = Lock()
        self.timestamp_counter = 0
        self.transaction_locks: Dict[str, Lock] = {}

    def _get_timestamp(self) -> int:
        with self.global_lock:
            self.timestamp_counter += 1
            return self.timestamp_counter

    def _get_node_for_key(self, key: str) -> Node:
        # Simple hash-based partitioning
        node_idx = hash(key) % len(self.nodes)
        return self.nodes[node_idx]

    def begin_transaction(self) -> str:
        txn_id = str(uuid.uuid4())
        timestamp = self._get_timestamp()
        
        transaction = Transaction(
            id=txn_id,
            start_timestamp=timestamp,
            status='active',
            write_set=set(),
            read_set=set(),
            writes={}
        )
        
        with self.global_lock:
            self.transactions[txn_id] = transaction
            self.transaction_locks[txn_id] = Lock()
        
        return txn_id

    def read(self, transaction_id: str, key: str) -> Optional[bytes]:
        if transaction_id not in self.transactions:
            raise ValueError("Invalid transaction ID")

        transaction = self.transactions[transaction_id]
        if transaction.status != 'active':
            raise ValueError("Transaction is not active")

        # If we've written to this key in this transaction, return that value
        if key in transaction.writes:
            return transaction.writes[key]

        # Add to read set
        transaction.read_set.add(key)

        # Get the appropriate version based on snapshot isolation
        node = self._get_node_for_key(key)
        return node.read(key, transaction.start_timestamp)

    def write(self, transaction_id: str, key: str, value: bytes):
        if transaction_id not in self.transactions:
            raise ValueError("Invalid transaction ID")

        transaction = self.transactions[transaction_id]
        if transaction.status != 'active':
            raise ValueError("Transaction is not active")

        # Buffer the write
        transaction.writes[key] = value
        transaction.write_set.add(key)

    def _check_conflicts(self, transaction: Transaction) -> bool:
        # Check for write-write conflicts
        for key in transaction.write_set:
            node = self._get_node_for_key(key)
            latest_version = node.get_latest_version(key)
            if latest_version and latest_version.timestamp > transaction.start_timestamp:
                return False
        return True

    def commit_transaction(self, transaction_id: str) -> bool:
        if transaction_id not in self.transactions:
            raise ValueError("Invalid transaction ID")

        transaction = self.transactions[transaction_id]
        if transaction.status != 'active':
            raise ValueError("Transaction is not active")

        with self.transaction_locks[transaction_id]:
            # Check for conflicts
            if not self._check_conflicts(transaction):
                transaction.status = 'aborted'
                return False

            # Get commit timestamp
            commit_timestamp = self._get_timestamp()

            # Write all changes to nodes
            for key, value in transaction.writes.items():
                node = self._get_node_for_key(key)
                node.write(key, value, commit_timestamp, transaction_id)

            transaction.status = 'committed'
            return True

    def abort_transaction(self, transaction_id: str):
        if transaction_id not in self.transactions:
            raise ValueError("Invalid transaction ID")

        with self.transaction_locks[transaction_id]:
            transaction = self.transactions[transaction_id]
            if transaction.status == 'active':
                transaction.status = 'aborted'

    def simulate_node_failure(self, node_id: int):
        """Simulate a node failure by clearing its data and recovering from other nodes"""
        if node_id < 0 or node_id >= len(self.nodes):
            raise ValueError("Invalid node ID")

        # In a real implementation, this would involve more sophisticated recovery
        # mechanisms using consensus algorithms and replication
        self.nodes[node_id] = Node(node_id)

        # Simple recovery: copy data from other nodes
        for other_node in self.nodes:
            if other_node.node_id != node_id:
                with other_node.lock:
                    for key, versions in other_node.data.items():
                        if hash(key) % len(self.nodes) == node_id:
                            self.nodes[node_id].data[key] = copy.deepcopy(versions)