import threading
import time

class DistributedKVStore:
    def __init__(self, num_nodes, replication_factor):
        if replication_factor > num_nodes:
            raise ValueError("Replication factor cannot be greater than the number of nodes.")
        self.num_nodes = num_nodes
        self.replication_factor = replication_factor
        # Each node is represented as a dictionary: key -> (value, timestamp)
        self.nodes = {node_id: {} for node_id in range(num_nodes)}
        # Track node states: True means up, False means down.
        self.node_states = {node_id: True for node_id in range(num_nodes)}
        # Lock to protect shared data structures.
        self.lock = threading.Lock()

    def put(self, key, value):
        timestamp = time.time()
        replicas = self._get_replica_nodes(key)
        primary_node = self._choose_primary(replicas, timestamp)
        if primary_node is None:
            # If none of the replica nodes are up, we simulate failure by ignoring the put.
            return
        # Write to chosen primary node.
        with self.lock:
            self._update_node(primary_node, key, value, timestamp)
        # Asynchronously replicate to the other replicas.
        thread = threading.Thread(target=self._replicate_put, args=(replicas, primary_node, key, value, timestamp))
        thread.daemon = True
        thread.start()

    def get(self, key):
        replicas = self._get_replica_nodes(key)
        best_val = None
        best_ts = -1
        with self.lock:
            for node_id in replicas:
                if not self.node_states[node_id]:
                    continue
                node_data = self.nodes[node_id]
                if key in node_data:
                    value, ts = node_data[key]
                    if ts > best_ts:
                        best_val = value
                        best_ts = ts
        return best_val

    def delete(self, key):
        timestamp = time.time()
        replicas = self._get_replica_nodes(key)
        primary_node = self._choose_primary_for_delete(replicas)
        if primary_node is None:
            # If none of the replicas are up, nothing to delete.
            return
        with self.lock:
            self._delete_key_on_node(primary_node, key)
        # Asynchronously replicate the deletion
        thread = threading.Thread(target=self._replicate_delete, args=(replicas, primary_node, key))
        thread.daemon = True
        thread.start()

    def mark_node_down(self, node_id):
        with self.lock:
            self.node_states[node_id] = False

    def mark_node_up(self, node_id):
        with self.lock:
            self.node_states[node_id] = True

    def reconcile_node(self, node_id):
        with self.lock:
            # For every key in the system, find the latest version among nodes that are up.
            all_keys = set()
            for n in range(self.num_nodes):
                if not self.node_states[n]:
                    continue
                all_keys.update(self.nodes[n].keys())
            for key in all_keys:
                best_val = None
                best_ts = -1
                for n in self._get_replica_nodes(key):
                    if not self.node_states.get(n, False):
                        continue
                    if key in self.nodes[n]:
                        val, ts = self.nodes[n][key]
                        if ts > best_ts:
                            best_val = val
                            best_ts = ts
                # Update the recovered node with the best data if available.
                if best_val is not None:
                    self.nodes[node_id][key] = (best_val, best_ts)
                else:
                    if key in self.nodes[node_id]:
                        del self.nodes[node_id][key]

    def get_node_data(self, node_id):
        with self.lock:
            # Return a shallow copy to prevent external modifications.
            return self.nodes[node_id].copy()

    def _get_replica_nodes(self, key):
        # Determine the primary node based on built-in hash.
        primary = hash(key) % self.num_nodes
        replicas = []
        for i in range(self.replication_factor):
            replicas.append((primary + i) % self.num_nodes)
        return replicas

    def _choose_primary(self, replicas, timestamp):
        # Choose the first available node from the replica list as primary.
        for node_id in replicas:
            if self.node_states[node_id]:
                return node_id
        return None

    def _choose_primary_for_delete(self, replicas):
        # For deletion, choose the first available node.
        for node_id in replicas:
            if self.node_states[node_id]:
                return node_id
        return None

    def _update_node(self, node_id, key, value, timestamp):
        # Update the node's data only if the new timestamp is later.
        current = self.nodes[node_id].get(key)
        if current is None or timestamp >= current[1]:
            self.nodes[node_id][key] = (value, timestamp)

    def _delete_key_on_node(self, node_id, key):
        # Delete the key from the node if it exists.
        if key in self.nodes[node_id]:
            del self.nodes[node_id][key]

    def _replicate_put(self, replicas, primary_node, key, value, timestamp):
        # Replicate the put operation to all replica nodes except the primary.
        for node_id in replicas:
            if node_id == primary_node:
                continue
            with self.lock:
                if self.node_states[node_id]:
                    self._update_node(node_id, key, value, timestamp)
            # Simulate network delay
            time.sleep(0.001)

    def _replicate_delete(self, replicas, primary_node, key):
        # Replicate the delete operation to all replica nodes except the primary.
        for node_id in replicas:
            if node_id == primary_node:
                continue
            with self.lock:
                if self.node_states[node_id]:
                    self._delete_key_on_node(node_id, key)
            # Simulate network delay
            time.sleep(0.001)