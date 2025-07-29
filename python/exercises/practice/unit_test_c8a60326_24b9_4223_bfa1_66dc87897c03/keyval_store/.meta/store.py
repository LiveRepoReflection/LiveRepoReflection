import threading
import time

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.data = {}  # key -> (value, timestamp)
        self.lock = threading.Lock()
        self.is_alive = True

    def put(self, key, value, timestamp):
        with self.lock:
            if key in self.data:
                # Only update if the new timestamp is more recent
                if timestamp >= self.data[key][1]:
                    self.data[key] = (value, timestamp)
            else:
                self.data[key] = (value, timestamp)

    def get(self, key):
        with self.lock:
            return self.data.get(key, None)

class KeyValStore:
    def __init__(self, num_nodes=5, replication_factor=3):
        self.num_nodes = num_nodes
        self.replication_factor = replication_factor
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.hinted_handoff = {}  # Mapping: failed node_id -> list of (key, value, timestamp)
        self.hinted_lock = threading.Lock()

    def _get_replication_indices(self, key):
        primary_index = hash(key) % self.num_nodes
        indices = []
        for i in range(self.replication_factor):
            indices.append((primary_index + i) % self.num_nodes)
        return indices

    def put(self, key, value):
        timestamp = time.time()
        replica_indices = self._get_replication_indices(key)
        for idx in replica_indices:
            node = self.nodes[idx]
            if node.is_alive:
                node.put(key, value, timestamp)
            else:
                alternate = self._find_alternate_node(replica_indices)
                if alternate is not None:
                    alternate.put(key, value, timestamp)
                    with self.hinted_lock:
                        if idx not in self.hinted_handoff:
                            self.hinted_handoff[idx] = []
                        self.hinted_handoff[idx].append((key, value, timestamp))
        return

    def _find_alternate_node(self, excluded_indices):
        # Return the first available node not in the excluded_indices list.
        for node in self.nodes:
            if node.node_id not in excluded_indices and node.is_alive:
                return node
        return None

    def get(self, key):
        replica_indices = self._get_replication_indices(key)
        latest_value = None
        latest_timestamp = -1
        for idx in replica_indices:
            node = self.nodes[idx]
            if node.is_alive:
                record = node.get(key)
                if record is not None:
                    val, ts = record
                    if ts > latest_timestamp:
                        latest_timestamp = ts
                        latest_value = val
        return latest_value

    def crash_node(self, node_id):
        if node_id < 0 or node_id >= self.num_nodes:
            return
        node = self.nodes[node_id]
        node.is_alive = False

    def recover_node(self, node_id):
        if node_id < 0 or node_id >= self.num_nodes:
            return
        node = self.nodes[node_id]
        node.is_alive = True
        # Flush hinted handoff data to the recovered node.
        with self.hinted_lock:
            if node_id in self.hinted_handoff:
                for key, value, timestamp in self.hinted_handoff[node_id]:
                    node.put(key, value, timestamp)
                del self.hinted_handoff[node_id]