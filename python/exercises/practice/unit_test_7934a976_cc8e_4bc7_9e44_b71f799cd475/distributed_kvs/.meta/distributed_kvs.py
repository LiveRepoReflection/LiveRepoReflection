import hashlib
import bisect

class DistributedKVS:
    def __init__(self, nodes, replication_factor):
        self.replication_factor = replication_factor
        self.nodes = nodes[:]  # list of node identifiers (strings)
        self.node_data = {}
        for node in self.nodes:
            self.node_data[node] = {}
        self.build_ring()

    def get_hash(self, key):
        # Use MD5 to generate a hash and then take modulo 2^32.
        md5_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return int(md5_hash, 16) % (2**32)

    def build_ring(self):
        # Build the hash ring as a sorted list of tuples: (node_hash, node)
        self.ring = []
        for node in self.nodes:
            node_hash = self.get_hash(node)
            self.ring.append((node_hash, node))
        self.ring.sort(key=lambda x: x[0])

    def get_nodes_for_key(self, key):
        key_hash = self.get_hash(key)
        # Create a list of node hash values to perform binary search.
        hash_list = [pair[0] for pair in self.ring]
        index = bisect.bisect_left(hash_list, key_hash)
        if index == len(self.ring):
            index = 0
        selected = []
        # Ensure we do not exceed the number of available nodes.
        replicas = min(self.replication_factor, len(self.nodes))
        for i in range(replicas):
            selected.append(self.ring[(index + i) % len(self.ring)][1])
        return selected

    def put(self, key, value):
        nodes = self.get_nodes_for_key(key)
        # Insert the key-value pair into each replica's store.
        for node in nodes:
            self.node_data[node][key] = value

    def get(self, key):
        nodes = self.get_nodes_for_key(key)
        # Retrieve from the primary node.
        primary = nodes[0]
        return self.node_data[primary].get(key, None)

    def delete(self, key):
        nodes = self.get_nodes_for_key(key)
        # Delete the key-value pair from all replicas.
        for node in nodes:
            if key in self.node_data[node]:
                del self.node_data[node][key]

    def update_nodes(self, new_nodes):
        # Gather all existing key-value pairs from current stores.
        all_items = {}
        for store in self.node_data.values():
            for key, value in store.items():
                all_items[key] = value

        # Update nodes, ensuring replication_factor is at most the number of nodes.
        self.nodes = new_nodes[:]
        self.replication_factor = min(self.replication_factor, len(self.nodes))

        # Reset the node data and rebuild the hash ring.
        self.node_data = {}
        for node in self.nodes:
            self.node_data[node] = {}
        self.build_ring()

        # Reinsert all key-value pairs into the new structure.
        for key, value in all_items.items():
            self.put(key, value)