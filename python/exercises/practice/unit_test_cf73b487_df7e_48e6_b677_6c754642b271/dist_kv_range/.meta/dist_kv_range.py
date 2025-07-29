import threading
import bisect
import hashlib
from typing import Dict, List, Tuple, Optional, Set

class Node:
    def __init__(self, node_id: int, replicas: int = 3):
        """Initialize a node in the distributed key-value store.
        
        Args:
            node_id: Unique identifier for this node.
            replicas: Number of replicas to maintain for fault tolerance.
        """
        self.node_id = node_id
        self.data = {}  # In-memory storage for key-value pairs
        self.sorted_keys = []  # Maintain a sorted list of keys for range queries
        self.active = True  # Node status flag
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        self.replicas = replicas
    
    def put(self, key: int, value: str) -> None:
        """Store a key-value pair in this node.
        
        Args:
            key: The integer key.
            value: The string value.
        """
        with self.lock:
            is_new_key = key not in self.data
            self.data[key] = value
            
            # Update the sorted keys list
            if is_new_key:
                bisect.insort(self.sorted_keys, key)
    
    def get(self, key: int) -> Optional[str]:
        """Retrieve the value for a given key.
        
        Args:
            key: The integer key.
            
        Returns:
            The value associated with the key, or None if not found.
        """
        with self.lock:
            return self.data.get(key)
    
    def range_query(self, start_key: int, end_key: int) -> List[Tuple[int, str]]:
        """Retrieve all key-value pairs within the given range.
        
        Args:
            start_key: The lower bound of the range (inclusive).
            end_key: The upper bound of the range (exclusive).
            
        Returns:
            A list of (key, value) tuples, sorted by key.
        """
        with self.lock:
            # Find the position where start_key would be inserted
            start_pos = bisect.bisect_left(self.sorted_keys, start_key)
            # Find the position where end_key would be inserted
            end_pos = bisect.bisect_left(self.sorted_keys, end_key)
            
            # Get the keys in the range
            keys_in_range = self.sorted_keys[start_pos:end_pos]
            
            # Return the key-value pairs
            result = [(k, self.data[k]) for k in keys_in_range]
            return result


class DistributedKVStore:
    def __init__(self, num_nodes: int = 10, key_range: int = 1000000, virtual_nodes: int = 100, replicas: int = 3):
        """Initialize a distributed key-value store with consistent hashing.
        
        Args:
            num_nodes: Number of nodes in the system.
            key_range: Maximum key value (exclusive).
            virtual_nodes: Number of virtual nodes per physical node for better distribution.
            replicas: Number of replicas to maintain for fault tolerance.
        """
        self.key_range = key_range
        self.virtual_nodes = virtual_nodes
        self.replicas = replicas
        
        # Create the physical nodes
        self.nodes = [Node(i, replicas) for i in range(num_nodes)]
        
        # Create the hash ring for consistent hashing
        self.hash_ring = []  # List of (hash_value, node_id) tuples
        self.lock = threading.RLock()
        
        # Initialize the hash ring with virtual nodes
        self._init_hash_ring()
    
    def _init_hash_ring(self) -> None:
        """Initialize the hash ring with virtual nodes."""
        with self.lock:
            self.hash_ring = []
            for node_id, node in enumerate(self.nodes):
                if node.active:
                    for v in range(self.virtual_nodes):
                        # Create a hash for each virtual node
                        key = f"{node_id}:{v}"
                        hash_value = self._hash(key)
                        self.hash_ring.append((hash_value, node_id))
            
            # Sort the hash ring
            self.hash_ring.sort()
    
    def _hash(self, key: str) -> int:
        """Hash a string key to an integer value.
        
        Args:
            key: The string key to hash.
            
        Returns:
            An integer hash value.
        """
        md5 = hashlib.md5(key.encode('utf-8')).hexdigest()
        return int(md5, 16) % (2**32)
    
    def _get_node_for_key(self, key: int) -> int:
        """Find the node responsible for a given key using consistent hashing.
        
        Args:
            key: The integer key.
            
        Returns:
            The node ID responsible for the key.
        """
        if not self.hash_ring:
            raise ValueError("Hash ring is empty. No active nodes.")
        
        # Hash the key to find its position on the ring
        hash_key = self._hash(str(key))
        
        # Binary search to find the first node with hash >= hash_key
        idx = bisect.bisect_left(self.hash_ring, (hash_key, 0))
        if idx == len(self.hash_ring):
            idx = 0  # Wrap around
        
        # Return the node ID
        return self.hash_ring[idx][1]
    
    def _get_replica_nodes(self, key: int) -> List[int]:
        """Find all nodes that should store replicas of the key.
        
        Args:
            key: The integer key.
            
        Returns:
            A list of node IDs that should store the key and its replicas.
        """
        if len(self.hash_ring) < self.replicas:
            # If we don't have enough nodes, return all available nodes
            return list(set(node_id for _, node_id in self.hash_ring))
        
        # Hash the key to find its position on the ring
        hash_key = self._hash(str(key))
        
        # Find the primary node
        idx = bisect.bisect_left(self.hash_ring, (hash_key, 0))
        if idx == len(self.hash_ring):
            idx = 0  # Wrap around
        
        # Get the required number of replicas
        replica_nodes = set()
        count = 0
        while count < self.replicas:
            node_id = self.hash_ring[idx][1]
            if node_id not in replica_nodes and self.nodes[node_id].active:
                replica_nodes.add(node_id)
                count += 1
            
            idx = (idx + 1) % len(self.hash_ring)
        
        return list(replica_nodes)
    
    def put(self, key: int, value: str) -> None:
        """Store a key-value pair in the distributed store.
        
        Args:
            key: The integer key.
            value: The string value.
            
        Raises:
            ValueError: If the key is outside the valid range.
        """
        if key < 0 or key >= self.key_range:
            raise ValueError(f"Key must be in range [0, {self.key_range})")
        
        # Find all nodes that should store this key (primary + replicas)
        replica_nodes = self._get_replica_nodes(key)
        
        # Store the key-value pair on all replica nodes
        for node_id in replica_nodes:
            if self.nodes[node_id].active:
                self.nodes[node_id].put(key, value)
    
    def get(self, key: int) -> Optional[str]:
        """Retrieve the value for a given key.
        
        Args:
            key: The integer key.
            
        Returns:
            The value associated with the key, or None if not found.
            
        Raises:
            ValueError: If the key is outside the valid range.
        """
        if key < 0 or key >= self.key_range:
            raise ValueError(f"Key must be in range [0, {self.key_range})")
        
        # Find all nodes that should store this key
        replica_nodes = self._get_replica_nodes(key)
        
        # Try each replica node until we find the value
        for node_id in replica_nodes:
            if self.nodes[node_id].active:
                value = self.nodes[node_id].get(key)
                if value is not None:
                    return value
        
        return None
    
    def range_query(self, start_key: int, end_key: int) -> List[Tuple[int, str]]:
        """Retrieve all key-value pairs within the given range.
        
        Args:
            start_key: The lower bound of the range (inclusive).
            end_key: The upper bound of the range (exclusive).
            
        Returns:
            A list of (key, value) tuples, sorted by key.
            
        Raises:
            ValueError: If the range is invalid.
        """
        if start_key >= end_key:
            raise ValueError("Start key must be less than end key")
        
        if start_key < 0 or end_key > self.key_range:
            raise ValueError(f"Keys must be in range [0, {self.key_range})")
        
        # Collect results from all nodes
        all_results = []
        
        # Create a set to track keys we've already seen (to avoid duplicates from replicas)
        seen_keys = set()
        
        # Query each active node for keys in the range
        for node in self.nodes:
            if node.active:
                node_results = node.range_query(start_key, end_key)
                for key, value in node_results:
                    if key not in seen_keys:
                        all_results.append((key, value))
                        seen_keys.add(key)
        
        # Sort the combined results by key
        all_results.sort(key=lambda x: x[0])
        return all_results
    
    def add_node(self) -> int:
        """Add a new node to the system.
        
        Returns:
            The ID of the new node.
        """
        with self.lock:
            # Create a new node
            new_node_id = len(self.nodes)
            new_node = Node(new_node_id, self.replicas)
            self.nodes.append(new_node)
            
            # Update the hash ring
            for v in range(self.virtual_nodes):
                key = f"{new_node_id}:{v}"
                hash_value = self._hash(key)
                bisect.insort(self.hash_ring, (hash_value, new_node_id))
            
            # Redistribute data
            self._redistribute_data()
            
            return new_node_id
    
    def remove_node(self, node_id: int) -> None:
        """Remove a node from the system.
        
        Args:
            node_id: The ID of the node to remove.
            
        Raises:
            ValueError: If the node ID is invalid.
        """
        if node_id < 0 or node_id >= len(self.nodes):
            raise ValueError(f"Invalid node ID: {node_id}")
        
        with self.lock:
            # Mark the node as inactive
            self.nodes[node_id].active = False
            
            # Remove the node's virtual nodes from the hash ring
            self.hash_ring = [(h, n) for h, n in self.hash_ring if n != node_id]
            
            # Redistribute data
            self._redistribute_data()
    
    def _redistribute_data(self) -> None:
        """Redistribute data after adding or removing nodes."""
        # Collect all key-value pairs from all nodes
        all_data = {}
        for node in self.nodes:
            if node.active:
                for key in node.sorted_keys:
                    if key not in all_data:
                        all_data[key] = node.get(key)
        
        # Clear all nodes
        for node in self.nodes:
            if node.active:
                node.data = {}
                node.sorted_keys = []
        
        # Redistribute all key-value pairs
        for key, value in all_data.items():
            self.put(key, value)