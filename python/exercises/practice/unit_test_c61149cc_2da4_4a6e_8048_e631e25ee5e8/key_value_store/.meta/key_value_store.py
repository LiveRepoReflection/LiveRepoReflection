import hashlib
import random
from collections import defaultdict

class DistributedKeyValueStore:
    def __init__(self, n_nodes):
        """
        Initialize the distributed key-value store with n_nodes.
        
        Args:
            n_nodes (int): Number of nodes in the system
        """
        self.n_nodes = n_nodes
        
        # Each node maintains its own storage
        # node_storage[node_id] = {key: (value, version)}
        self.node_storage = [defaultdict(lambda: (-1, -1)) for _ in range(n_nodes)]
        
        # Keep track of which nodes store which keys
        # key_mapping[key] = {node_id1, node_id2, ...}
        self.key_mapping = defaultdict(set)
        
        # Global version counter for updates
        self.version_counter = 0
    
    def _hash_key(self, key):
        """
        Hash the key to determine the primary node.
        
        Args:
            key (str): The key to hash
        
        Returns:
            int: The node ID
        """
        # Use a more robust hash function to reduce collisions
        hash_object = hashlib.md5(key.encode())
        digest = hash_object.hexdigest()
        hash_int = int(digest, 16)
        return hash_int % self.n_nodes
    
    def _get_nodes_for_key(self, key, replication_factor):
        """
        Determine which nodes should store a key based on consistent hashing.
        
        Args:
            key (str): The key
            replication_factor (int): Number of nodes to replicate to
        
        Returns:
            list: List of node IDs
        """
        # Get the starting node based on the key hash
        start_node = self._hash_key(key)
        
        # Generate replication_factor distinct nodes
        nodes = set()
        nodes.add(start_node)
        
        # Add subsequent nodes by incrementing modulo n_nodes
        current = start_node
        while len(nodes) < replication_factor:
            current = (current + 1) % self.n_nodes
            nodes.add(current)
        
        return list(nodes)
    
    def put(self, key, value, replication_factor):
        """
        Store a key-value pair across multiple nodes.
        
        Args:
            key (str): The key
            value (int): The value
            replication_factor (int): Number of nodes to replicate to
        """
        # Validate inputs
        if not (1 <= len(key) <= 50 and key.isalnum()):
            raise ValueError("Key must be alphanumeric and 1-50 characters")
        
        if not (1 <= value <= 10**9):
            raise ValueError("Value must be between 1 and 10^9")
        
        if not (1 <= replication_factor <= self.n_nodes):
            raise ValueError(f"Replication factor must be between 1 and {self.n_nodes}")
        
        # Increment version counter
        self.version_counter += 1
        current_version = self.version_counter
        
        # First update key_mapping - remove old node mappings if any
        if key in self.key_mapping:
            for node_id in self.key_mapping[key]:
                if key in self.node_storage[node_id]:
                    # This only removes if key exists to avoid defaultdict creation
                    del self.node_storage[node_id][key]
        
        # Clear existing mapping and create new one
        self.key_mapping[key] = set()
        
        # Determine nodes for storage using consistent hashing
        nodes = self._get_nodes_for_key(key, replication_factor)
        
        # Store on the selected nodes
        for node_id in nodes:
            self.node_storage[node_id][key] = (value, current_version)
            self.key_mapping[key].add(node_id)
    
    def get(self, key):
        """
        Retrieve a value for a key.
        
        Args:
            key (str): The key to retrieve
        
        Returns:
            int: The value or -1 if key doesn't exist
        """
        if key not in self.key_mapping:
            return -1
        
        # Find all values and versions across nodes that have this key
        values_with_versions = []
        for node_id in self.key_mapping[key]:
            value, version = self.node_storage[node_id][key]
            if version != -1:  # Ensure the key exists on the node
                values_with_versions.append((value, version))
        
        if not values_with_versions:
            return -1
        
        # Return the value with the most recent version
        return max(values_with_versions, key=lambda x: x[1])[0]
    
    def delete(self, key):
        """
        Delete a key from all nodes.
        
        Args:
            key (str): The key to delete
        """
        if key not in self.key_mapping:
            return
        
        # Remove key from all nodes that have it
        for node_id in self.key_mapping[key]:
            if key in self.node_storage[node_id]:
                del self.node_storage[node_id][key]
        
        # Remove key mapping
        del self.key_mapping[key]

# For handling input/output format as described in the problem
def process_command(store, command):
    parts = command.strip().split()
    operation = parts[0]
    
    if operation == "PUT":
        key = parts[1]
        value = int(parts[2])
        replication_factor = int(parts[3])
        store.put(key, value, replication_factor)
        return None  # No output for PUT
    
    elif operation == "GET":
        key = parts[1]
        return store.get(key)
    
    elif operation == "DELETE":
        key = parts[1]
        store.delete(key)
        return None  # No output for DELETE
    
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Example usage
if __name__ == "__main__":
    # Example from problem statement
    commands = [
        "PUT key1 123 3",
        "GET key1",
        "PUT key2 456 2",
        "GET key2",
        "DELETE key1",
        "GET key1",
        "PUT key1 789 1",
        "GET key1"
    ]
    
    store = DistributedKeyValueStore(100)
    for cmd in commands:
        result = process_command(store, cmd)
        if result is not None:  # Only print output for GET operations
            print(result)