import threading
import time

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.data = {}  # key: (value, timestamp)

    def put(self, key, value, timestamp):
        if key in self.data:
            existing_value, existing_timestamp = self.data[key]
            if timestamp >= existing_timestamp:
                self.data[key] = (value, timestamp)
        else:
            self.data[key] = (value, timestamp)

    def get(self, key):
        return self.data.get(key, None)

    def clear_data(self):
        self.data.clear()

class DistributedKeyValueStore:
    def __init__(self, initial_nodes, replication_factor, ring_size):
        self.ring_size = ring_size
        self.replication_factor = replication_factor
        self.lock = threading.Lock()
        self.VNODE_COUNT = 3  # Number of virtual nodes per physical node
        self.nodes = {}  # Mapping of node_id to Node instance
        self.ring = []   # List of tuples (hash, node_id) representing virtual nodes
        self.next_node_id = 0
        for _ in range(initial_nodes):
            self._add_physical_node()

    def _hash(self, key_str):
        return hash(key_str) % self.ring_size

    def _add_physical_node(self):
        node_id = self.next_node_id
        self.next_node_id += 1
        new_node = Node(node_id)
        self.nodes[node_id] = new_node
        for i in range(self.VNODE_COUNT):
            vnode_key = f"{node_id}-{i}"
            vnode_hash = self._hash(vnode_key)
            self.ring.append((vnode_hash, node_id))
        self.ring.sort(key=lambda x: x[0])
        self._rebalance_keys()

    def add_node(self):
        with self.lock:
            self._add_physical_node()

    def _remove_physical_node(self, node_id):
        if node_id in self.nodes:
            del self.nodes[node_id]
        self.ring = [entry for entry in self.ring if entry[1] != node_id]
        self.ring.sort(key=lambda x: x[0])
        self._rebalance_keys()

    def remove_node(self):
        with self.lock:
            if not self.nodes:
                return
            node_id = max(self.nodes.keys())
            self._remove_physical_node(node_id)

    def _get_nodes_for_key(self, key):
        if not self.ring:
            return []
        h = self._hash(key)
        unique_node_ids = []
        ring_len = len(self.ring)
        idx = 0
        for i, (pos, node_id) in enumerate(self.ring):
            if pos >= h:
                idx = i
                break
        else:
            idx = 0
        i = idx
        while len(unique_node_ids) < self.replication_factor:
            pos, node_id = self.ring[i % ring_len]
            if node_id not in unique_node_ids and node_id in self.nodes:
                unique_node_ids.append(node_id)
            i += 1
            if i - idx >= ring_len:
                break
        return [self.nodes[nid] for nid in unique_node_ids if nid in self.nodes]

    def _store_key(self, key, value, timestamp):
        nodes_for_key = self._get_nodes_for_key(key)
        for node in nodes_for_key:
            node.put(key, value, timestamp)

    def _rebalance_keys(self):
        all_data = {}
        for node in self.nodes.values():
            for key, (value, timestamp) in node.data.items():
                if key in all_data:
                    if timestamp > all_data[key][1]:
                        all_data[key] = (value, timestamp)
                else:
                    all_data[key] = (value, timestamp)
        for node in self.nodes.values():
            node.clear_data()
        for key, (value, timestamp) in all_data.items():
            self._store_key(key, value, timestamp)

    def put(self, key, value):
        with self.lock:
            timestamp = time.time()
            self._store_key(key, value, timestamp)

    def get(self, key):
        with self.lock:
            nodes_for_key = self._get_nodes_for_key(key)
            candidate = None
            latest_timestamp = -1
            for node in nodes_for_key:
                result = node.get(key)
                if result is not None:
                    val, ts = result
                    if ts > latest_timestamp:
                        candidate = val
                        latest_timestamp = ts
            return candidate