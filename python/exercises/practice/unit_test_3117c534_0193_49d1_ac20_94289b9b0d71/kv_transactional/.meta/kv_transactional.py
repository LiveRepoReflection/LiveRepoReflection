import threading
from time import sleep

class TransactionError(Exception):
    pass

class Node:
    def __init__(self):
        self.store = {}  # key -> (value, vector_clock)
        self.alive = True
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            return self.store.get(key, (None, {}))

    def put(self, key, value, vector_clock):
        with self.lock:
            self.store[key] = (value, vector_clock)

class KVStore:
    def __init__(self, num_nodes=5, replication_factor=3):
        self.num_nodes = num_nodes
        self.replication_factor = replication_factor
        self.nodes = [Node() for _ in range(num_nodes)]
        self.global_lock = threading.Lock()
        self.max_txn_ops = 100

    def _get_replica_indices(self, key):
        primary_index = hash(key) % self.num_nodes
        return [(primary_index + i) % self.num_nodes for i in range(self.replication_factor)]
    
    def get(self, key):
        replica_indices = self._get_replica_indices(key)
        for idx in replica_indices:
            node = self.nodes[idx]
            if node.alive:
                value, _ = node.get(key)
                return value
        return None

    def put(self, key, value):
        # Non-transactional put: use a temporary transaction.
        txn = self.begin_transaction()
        txn.put(key, value)
        txn.commit()

    def begin_transaction(self):
        return Transaction(self)

    def simulate_node_failure(self, key):
        # Simulate failure of the primary node responsible for key.
        replica_indices = self._get_replica_indices(key)
        primary_node = self.nodes[replica_indices[0]]
        with primary_node.lock:
            primary_node.alive = False

    def max_transaction_size(self):
        return self.max_txn_ops

class Transaction:
    def __init__(self, kv_store):
        self.kv_store = kv_store
        self.operations = {}  # key -> new value
        self.snapshots = {}   # key -> snapshot vector clock
        self.committed = False
        self.aborted = False
        self.op_count = 0

    def put(self, key, value):
        if self.committed or self.aborted:
            raise TransactionError("Transaction already closed.")
        if self.op_count >= self.kv_store.max_transaction_size():
            raise TransactionError("Exceeded max transaction size.")
        # Take a snapshot if not already
        if key not in self.snapshots:
            # Get snapshot from first alive replica
            replica_indices = self.kv_store._get_replica_indices(key)
            snapshot_vc = {}
            with self.kv_store.global_lock:
                for idx in replica_indices:
                    node = self.kv_store.nodes[idx]
                    if node.alive:
                        _, vc = node.get(key)
                        # copy the vector clock
                        snapshot_vc = dict(vc)
                        break
            self.snapshots[key] = snapshot_vc
        self.operations[key] = value
        self.op_count += 1

    def commit(self):
        if self.committed or self.aborted:
            raise TransactionError("Transaction already closed.")
        # Lock global store for commit to ensure atomic check-update across nodes.
        with self.kv_store.global_lock:
            # First, verify that for every key, the current vector clock matches the snapshot.
            for key, new_value in self.operations.items():
                replica_indices = self.kv_store._get_replica_indices(key)
                for idx in replica_indices:
                    node = self.kv_store.nodes[idx]
                    if node.alive:
                        _, current_vc = node.get(key)
                        snapshot_vc = self.snapshots.get(key, {})
                        if current_vc != snapshot_vc:
                            self.rollback()
                            raise TransactionError("Conflict detected during commit.")
            # All checks passed, apply the updates with new vector clocks.
            for key, new_value in self.operations.items():
                replica_indices = self.kv_store._get_replica_indices(key)
                # Create new vector clock by merging snapshot and updating.
                snapshot_vc = self.snapshots.get(key, {})
                new_vc = dict(snapshot_vc)
                # Use a fixed identifier "txn" to simulate version increment.
                new_vc["txn"] = new_vc.get("txn", 0) + 1
                for idx in replica_indices:
                    node = self.kv_store.nodes[idx]
                    if node.alive:
                        node.put(key, new_value, new_vc)
            self.committed = True

    def rollback(self):
        self.aborted = True
        self.operations.clear()
        self.snapshots.clear()