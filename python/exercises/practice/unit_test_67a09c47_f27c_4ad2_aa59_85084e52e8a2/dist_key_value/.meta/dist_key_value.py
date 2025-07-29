import threading
import time

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.store = {}  # key -> (value, version, deleted)
        self.available = True
        self.lock = threading.Lock()

    def write(self, key, value, version, deleted=False):
        with self.lock:
            current = self.store.get(key)
            if current is None or version > current[1]:
                self.store[key] = (value, version, deleted)

    def read(self, key):
        with self.lock:
            return self.store.get(key)

class KeyValueStore:
    def __init__(self, num_nodes, replication_factor):
        self.num_nodes = num_nodes
        self.replication_factor = replication_factor
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.version_lock = threading.Lock()
        self.version_counter = 0
        # Hinted handoff: mapping from node index to list of pending updates.
        # Each update is a tuple: (key, value, version, deleted)
        self.hinted = {i: [] for i in range(num_nodes)}

    def _get_new_version(self):
        with self.version_lock:
            self.version_counter += 1
            return self.version_counter

    def _get_replica_indices(self, key):
        home = hash(key) % self.num_nodes
        # Get replication_factor nodes starting from home in a circular fashion.
        return [(home + i) % self.num_nodes for i in range(self.replication_factor)]

    def put(self, key, value):
        version = self._get_new_version()
        replica_indices = self._get_replica_indices(key)
        for idx in replica_indices:
            node = self.nodes[idx]
            if node.available:
                node.write(key, value, version, deleted=False)
            else:
                # Store update in hinted handoff if node is unavailable.
                self.hinted[idx].append((key, value, version, False))

    def get(self, key):
        replica_indices = self._get_replica_indices(key)
        best_record = None
        for idx in replica_indices:
            node = self.nodes[idx]
            if node.available:
                record = node.read(key)
                if record:
                    if best_record is None or record[1] > best_record[1]:
                        best_record = record
        # If no available replica returns a value, then return None.
        if best_record is None:
            return None
        # If the record indicates deletion, return None.
        if best_record[2]:
            return None
        return best_record[0]

    def delete(self, key):
        version = self._get_new_version()
        replica_indices = self._get_replica_indices(key)
        for idx in replica_indices:
            node = self.nodes[idx]
            if node.available:
                node.write(key, None, version, deleted=True)
            else:
                self.hinted[idx].append((key, None, version, True))

    def set_node_availability(self, node_index, availability):
        node = self.nodes[node_index]
        node.available = availability
        if availability:
            # When a node becomes available, process its hinted handoff updates.
            updates = self.hinted[node_index]
            for update in updates:
                key, value, version, deleted = update
                node.write(key, value, version, deleted)
            # Clear hinted updates after processing.
            self.hinted[node_index] = []