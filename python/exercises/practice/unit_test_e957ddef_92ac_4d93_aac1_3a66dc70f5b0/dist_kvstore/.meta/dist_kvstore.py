import threading
import hashlib
import bisect

class DistributedKVStore:
    class Node:
        def __init__(self, node_id):
            self.node_id = node_id
            self.store = {}
            self.active = True

    def __init__(self, replication_factor=3, virtual_replicas=10):
        self.replication_factor = replication_factor
        self.virtual_replicas = virtual_replicas
        self.nodes = {}  # node_id -> Node
        self.ring = []   # list of tuples (hash, node_id), sorted by hash
        self.lock = threading.Lock()

    def _hash(self, key):
        key_bytes = key.encode("utf-8")
        return int(hashlib.md5(key_bytes).hexdigest(), 16)

    def _build_virtual_node_keys(self, node_id):
        virtual_keys = []
        for i in range(self.virtual_replicas):
            composite_key = f"{node_id}#{i}"
            virtual_keys.append(self._hash(composite_key))
        return virtual_keys

    def _rebuild_ring(self):
        self.ring = []
        for node_id in self.nodes:
            for v_hash in self._build_virtual_node_keys(node_id):
                self.ring.append((v_hash, node_id))
        self.ring.sort(key=lambda x: x[0])

    def _rebalance(self):
        # Gather all keys from all nodes (even from inactive nodes)
        temp_data = {}
        for node in self.nodes.values():
            for key, value in node.store.items():
                # In case of duplicates, later occurrences will just reassign same value.
                temp_data[key] = value

        # Clear all keys from nodes
        for node in self.nodes.values():
            node.store.clear()

        # Re-distribute keys to the proper replica nodes according to the updated ring.
        for key, value in temp_data.items():
            replica_ids = self._get_replica_ids(key)
            for node_id in replica_ids:
                if node_id in self.nodes:
                    self.nodes[node_id].store[key] = value

    def _get_replica_ids(self, key):
        replica_ids = []
        if not self.ring:
            return replica_ids
        key_hash = self._hash(key)
        # Find index in ring
        idx = bisect.bisect(self.ring, (key_hash, None))
        ring_length = len(self.ring)
        # Collect unique physical nodes until replication_factor reached
        seen = set()
        i = idx
        while len(replica_ids) < self.replication_factor:
            node_hash, node_id = self.ring[i % ring_length]
            if node_id not in seen and node_id in self.nodes:
                seen.add(node_id)
                replica_ids.append(node_id)
            i += 1
            if i - idx >= ring_length:  # prevent infinite loop if nodes fewer than replication factor
                break
        return replica_ids

    def add_node(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                return
            self.nodes[node_id] = DistributedKVStore.Node(node_id)
            self._rebuild_ring()
            self._rebalance()

    def remove_node(self, node_id):
        with self.lock:
            if node_id not in self.nodes:
                return
            del self.nodes[node_id]
            self._rebuild_ring()
            self._rebalance()

    def simulate_node_failure(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].active = False

    def put(self, key, value):
        with self.lock:
            replica_ids = self._get_replica_ids(key)
            for node_id in replica_ids:
                if node_id in self.nodes:
                    self.nodes[node_id].store[key] = value

    def get(self, key):
        with self.lock:
            replica_ids = self._get_replica_ids(key)
            for node_id in replica_ids:
                node = self.nodes.get(node_id, None)
                if node and node.active and key in node.store:
                    return node.store[key]
            return None

    def delete(self, key):
        with self.lock:
            replica_ids = self._get_replica_ids(key)
            for node_id in replica_ids:
                if node_id in self.nodes and key in self.nodes[node_id].store:
                    del self.nodes[node_id].store[key]

    def get_replicas(self, key):
        with self.lock:
            return self._get_replica_ids(key)