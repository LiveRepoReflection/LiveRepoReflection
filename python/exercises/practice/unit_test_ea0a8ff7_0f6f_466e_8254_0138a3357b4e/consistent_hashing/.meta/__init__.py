import threading

class DistributedHashStore:
    def __init__(self, virtual_nodes=3):
        self.virtual_nodes = virtual_nodes
        self.ring = []  # list of tuples (hash_value, node_id)
        self.node_data = {}  # mapping physical node id to key-value store (dictionary)
        self.nodes = set()  # set of active physical node ids
        self.lock = threading.RLock()

    def _hash(self, key):
        # Use built-in hash and ensure non-negative integer value.
        h = hash(key)
        return h if h >= 0 else -h

    def _update_ring(self):
        # Rebuild the hash ring based on the current physical nodes and virtual nodes.
        new_ring = []
        for node in self.nodes:
            for replica in range(self.virtual_nodes):
                replica_key = f"{node}#{replica}"
                hash_value = self._hash(replica_key)
                new_ring.append((hash_value, node))
        new_ring.sort(key=lambda x: x[0])
        self.ring = new_ring

    def _get_node_for_key(self, key):
        # Return the physical node id responsible for the provided key.
        if not self.ring:
            return None
        key_hash = self._hash(key)
        low, high = 0, len(self.ring)
        while low < high:
            mid = (low + high) // 2
            if self.ring[mid][0] < key_hash:
                low = mid + 1
            else:
                high = mid
        if low == len(self.ring):
            low = 0
        return self.ring[low][1]

    def _reassign_keys(self):
        # Reassign keys from all physical nodes based on the current hash ring.
        all_items = []
        for node in list(self.node_data.keys()):
            for k, v in self.node_data[node].items():
                all_items.append((k, v))
            self.node_data[node].clear()
        for k, v in all_items:
            dest_node = self._get_node_for_key(k)
            if dest_node is not None:
                self.node_data[dest_node][k] = v

    def add_node(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                return
            self.nodes.add(node_id)
            self.node_data[node_id] = {}
            self._update_ring()
            self._reassign_keys()

    def remove_node(self, node_id):
        with self.lock:
            if node_id not in self.nodes:
                return
            # Capture keys stored in the node to be removed.
            data_to_move = self.node_data[node_id].copy()
            self.nodes.remove(node_id)
            del self.node_data[node_id]
            self._update_ring()
            # Reassign keys from the removed node.
            for k, v in data_to_move.items():
                dest_node = self._get_node_for_key(k)
                if dest_node is not None:
                    self.node_data[dest_node][k] = v
            # Reassign keys across all nodes to ensure consistency.
            self._reassign_keys()

    def put(self, key, value):
        with self.lock:
            dest_node = self._get_node_for_key(key)
            if dest_node is None:
                return
            self.node_data[dest_node][key] = value

    def get(self, key):
        with self.lock:
            dest_node = self._get_node_for_key(key)
            if dest_node is None:
                return None
            return self.node_data.get(dest_node, {}).get(key, None)