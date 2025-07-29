import threading
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import random

@dataclass
class Operation:
    op_type: str
    key: str
    value: Optional[int] = None

@dataclass
class Transaction:
    id: str
    operations: List[Operation]
    status: str = "PENDING"
    locks: Set[str] = None

    def __post_init__(self):
        if self.locks is None:
            self.locks = set()

class Node:
    def __init__(self, node_id: int, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.data: Dict[str, int] = {}
        self.locks: Dict[str, str] = {}  # key -> transaction_id
        self.transactions: Dict[str, Transaction] = {}
        self.replicas: Dict[str, List[int]] = {}
        self.lock = threading.Lock()

    def get_responsible_node(self, key: str) -> int:
        """Determine which node is responsible for a key using consistent hashing."""
        hash_val = int(hashlib.sha1(key.encode()).hexdigest(), 16)
        return hash_val % self.total_nodes

    def is_responsible(self, key: str) -> bool:
        return self.get_responsible_node(key) == self.node_id

class DistributedKVStore:
    def __init__(self, num_nodes: int, fault_tolerance: int):
        self.num_nodes = num_nodes
        self.fault_tolerance = fault_tolerance
        self.nodes = [Node(i, num_nodes) for i in range(num_nodes)]
        self.transaction_counter = 0
        self.lock = threading.Lock()

    def _get_replica_nodes(self, primary_node: int) -> List[int]:
        """Get replica nodes for a given primary node."""
        replicas = [(primary_node + i) % self.num_nodes 
                   for i in range(1, self.fault_tolerance + 1)]
        return [primary_node] + replicas

    def _acquire_locks(self, transaction_id: str, keys: List[str]) -> bool:
        """Acquire locks for all keys in the transaction."""
        acquired_locks = set()
        
        # Sort keys to prevent deadlock
        sorted_keys = sorted(keys)
        
        try:
            for key in sorted_keys:
                primary_node = self.nodes[0].get_responsible_node(key)
                replica_nodes = self._get_replica_nodes(primary_node)
                
                for node_id in replica_nodes:
                    node = self.nodes[node_id]
                    with node.lock:
                        if key in node.locks and node.locks[key] != transaction_id:
                            # Lock held by another transaction
                            raise Exception("Lock acquisition failed")
                        node.locks[key] = transaction_id
                        acquired_locks.add((node_id, key))
            
            return True
            
        except Exception:
            # Release any acquired locks
            for node_id, key in acquired_locks:
                self.nodes[node_id].locks.pop(key, None)
            return False

    def _release_locks(self, transaction_id: str, keys: List[str]):
        """Release all locks held by the transaction."""
        for key in keys:
            primary_node = self.nodes[0].get_responsible_node(key)
            replica_nodes = self._get_replica_nodes(primary_node)
            
            for node_id in replica_nodes:
                node = self.nodes[node_id]
                with node.lock:
                    if key in node.locks and node.locks[key] == transaction_id:
                        node.locks.pop(key)

    def execute_transaction(self, operations: List[Tuple]) -> List[str]:
        """Execute a transaction with the given operations."""
        with self.lock:
            transaction_id = f"tx_{self.transaction_counter}"
            self.transaction_counter += 1

        results = []
        tx_operations = []
        affected_keys = set()

        # Convert operation tuples to Operation objects
        for op in operations:
            if op[0] == "PUT":
                tx_operations.append(Operation("PUT", op[1], op[2]))
                affected_keys.add(op[1])
            elif op[0] == "GET":
                tx_operations.append(Operation("GET", op[1]))
                affected_keys.add(op[1])
            elif op[0] == "DELETE":
                tx_operations.append(Operation("DELETE", op[1]))
                affected_keys.add(op[1])
            elif op[0] in ["COMMIT", "ROLLBACK"]:
                tx_operations.append(Operation(op[0], ""))

        transaction = Transaction(transaction_id, tx_operations)

        try:
            # Try to acquire all necessary locks
            if not self._acquire_locks(transaction_id, list(affected_keys)):
                results.append("Transaction aborted: could not acquire locks")
                return results

            # Execute operations
            for op in transaction.operations:
                if op.op_type == "GET":
                    primary_node = self.nodes[0].get_responsible_node(op.key)
                    node = self.nodes[primary_node]
                    with node.lock:
                        value = node.data.get(op.key, "NULL")
                    results.append(value)
                
                elif op.op_type == "PUT":
                    primary_node = self.nodes[0].get_responsible_node(op.key)
                    replica_nodes = self._get_replica_nodes(primary_node)
                    
                    for node_id in replica_nodes:
                        node = self.nodes[node_id]
                        with node.lock:
                            node.data[op.key] = op.value
                    results.append(None)
                
                elif op.op_type == "DELETE":
                    primary_node = self.nodes[0].get_responsible_node(op.key)
                    replica_nodes = self._get_replica_nodes(primary_node)
                    
                    for node_id in replica_nodes:
                        node = self.nodes[node_id]
                        with node.lock:
                            node.data.pop(op.key, None)
                    results.append(None)
                
                elif op.op_type == "COMMIT":
                    results.append("COMMIT OK")
                
                elif op.op_type == "ROLLBACK":
                    raise Exception("Transaction rolled back")

        except Exception as e:
            # Rollback changes
            for op in transaction.operations:
                if op.op_type == "PUT":
                    primary_node = self.nodes[0].get_responsible_node(op.key)
                    replica_nodes = self._get_replica_nodes(primary_node)
                    for node_id in replica_nodes:
                        node = self.nodes[node_id]
                        with node.lock:
                            node.data.pop(op.key, None)

            results = []
            for _ in range(len(transaction.operations) - 1):
                results.append(None)
            results.append("ROLLBACK OK")

        finally:
            # Release all locks
            self._release_locks(transaction_id, list(affected_keys))

        return results