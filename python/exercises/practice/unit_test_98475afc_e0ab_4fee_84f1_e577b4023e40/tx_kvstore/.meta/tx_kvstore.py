import time
import threading

class Node:
    def __init__(self):
        self.active = True
        self.data = {}  # key -> (commit_time, value)
        self.lock = threading.Lock()

    def update_key(self, key, commit_time, value):
        with self.lock:
            if key not in self.data or commit_time > self.data[key][0]:
                self.data[key] = (commit_time, value)

    def get_key(self, key):
        with self.lock:
            if key in self.data:
                return self.data[key]
            return None

    def sync(self, global_data):
        with self.lock:
            self.data = global_data.copy()

class DistributedKVStore:
    def __init__(self, num_nodes):
        # Create a list of nodes simulating the distributed cluster.
        self.nodes = [Node() for _ in range(num_nodes)]
        # Global committed data: key -> (commit_time, value)
        self.committed_data = {}
        # Transaction buffers: tx_id -> { key: value }
        self.transaction_buffer = {}
        self.lock = threading.Lock()

    def put(self, key, value, tx_id):
        with self.lock:
            if tx_id not in self.transaction_buffer:
                self.transaction_buffer[tx_id] = {}
            # Immutability: We always overwrite with a new value.
            self.transaction_buffer[tx_id][key] = value

    def get(self, key, tx_id):
        with self.lock:
            # If the transaction has an uncommitted write for key, return it
            if tx_id in self.transaction_buffer and key in self.transaction_buffer[tx_id]:
                return self.transaction_buffer[tx_id][key]
            # Otherwise, read from the global committed data
            if key in self.committed_data:
                return self.committed_data[key][1]
            return None

    def commit(self, tx_id):
        commit_time = time.time()
        with self.lock:
            if tx_id not in self.transaction_buffer:
                return  # No operations to commit
            tx_data = self.transaction_buffer[tx_id]
            # Apply each key update using Last Writer Wins (comparing commit_time)
            for key, value in tx_data.items():
                # Update global committed data if newer
                if key not in self.committed_data or commit_time > self.committed_data[key][0]:
                    self.committed_data[key] = (commit_time, value)
                # Replicate to all active nodes. Inactive nodes remain unchanged.
                for node in self.nodes:
                    if node.active:
                        node.update_key(key, commit_time, value)
            # Remove the transaction buffer after commit
            del self.transaction_buffer[tx_id]

    def rollback(self, tx_id):
        with self.lock:
            if tx_id in self.transaction_buffer:
                del self.transaction_buffer[tx_id]

    def snapshot(self, timestamp):
        with self.lock:
            snapshot_data = {}
            for key, (commit_time, value) in self.committed_data.items():
                if commit_time <= timestamp:
                    snapshot_data[key] = value
            return snapshot_data

    def fail_node(self, node_id):
        with self.lock:
            if 0 <= node_id < len(self.nodes):
                self.nodes[node_id].active = False

    def recover_node(self, node_id):
        with self.lock:
            if 0 <= node_id < len(self.nodes):
                self.nodes[node_id].active = True
                # Sync the recovered node with the current global committed data
                self.nodes[node_id].sync(self.committed_data)