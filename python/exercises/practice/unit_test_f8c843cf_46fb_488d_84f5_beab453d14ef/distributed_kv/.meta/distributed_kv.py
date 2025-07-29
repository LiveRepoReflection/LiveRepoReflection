class DistributedKVStore:
    def __init__(self, num_nodes, replication_factor):
        self.num_nodes = num_nodes
        self.replication_factor = replication_factor
        # Each node is represented as a dictionary
        self.nodes = [{} for _ in range(num_nodes)]
        # Active status for each node; True means active, False means failure.
        self.active = [True] * num_nodes
        # Global set to track all keys currently in the store (that haven't been removed)
        self.all_keys = set()

    def _get_primary_node(self, key):
        # Attempt to convert key to int, otherwise use hash of key
        try:
            k = int(key)
        except ValueError:
            k = abs(hash(key))
        return k % self.num_nodes

    def _get_replica_nodes(self, key):
        primary = self._get_primary_node(key)
        # Get replication nodes in circular order
        return [(primary + i) % self.num_nodes for i in range(self.replication_factor)]

    def put(self, key, value):
        replica_nodes = self._get_replica_nodes(key)
        # Add key to global set
        self.all_keys.add(key)
        # Propagate to active nodes among the replication set
        for node_id in replica_nodes:
            if self.active[node_id]:
                self.nodes[node_id][key] = value

    def get(self, key):
        replica_nodes = self._get_replica_nodes(key)
        # Try primary first, then replicas.
        for node_id in replica_nodes:
            if self.active[node_id]:
                if key in self.nodes[node_id]:
                    return self.nodes[node_id][key]
        return None

    def remove(self, key):
        replica_nodes = self._get_replica_nodes(key)
        if key in self.all_keys:
            self.all_keys.remove(key)
        # Remove the key from all active nodes in the replication set.
        for node_id in replica_nodes:
            if self.active[node_id]:
                if key in self.nodes[node_id]:
                    del self.nodes[node_id][key]

    def node_failure(self, node_id):
        # Mark the node as failed.
        if 0 <= node_id < self.num_nodes:
            self.active[node_id] = False

    def recover_node(self, node_id):
        if 0 <= node_id < self.num_nodes:
            # Mark the node as active.
            self.active[node_id] = True
            # Sync data: clear current store and reintegrate data meant for this node.
            self.nodes[node_id] = {}
            # For each key in the global key set, if this node is in its replication set,
            # then try to get the value from one of the other active replicas.
            for key in self.all_keys:
                replica_nodes = self._get_replica_nodes(key)
                if node_id in replica_nodes:
                    # Check all other nodes in the replica set to get the key's value.
                    for other_node in replica_nodes:
                        if other_node != node_id and self.active[other_node]:
                            if key in self.nodes[other_node]:
                                self.nodes[node_id][key] = self.nodes[other_node][key]
                                break