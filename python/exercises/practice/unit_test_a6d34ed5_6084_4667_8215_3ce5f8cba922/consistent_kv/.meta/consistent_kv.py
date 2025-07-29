import hashlib
import bisect
import threading
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set, Tuple


class Node:
    """Represents a node in the distributed key-value store."""
    
    def __init__(self, node_id: int):
        self.id = node_id
        self.data: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self.lock = threading.RLock()  # Reentrant lock for thread-safety
        self.active = True  # Node status
    
    def put(self, key: str, value: Any) -> None:
        """Store a key-value pair with current timestamp."""
        with self.lock:
            if self.active:
                self.data[key] = (value, time.time())
    
    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        """Retrieve a key-value pair with its timestamp."""
        with self.lock:
            if self.active and key in self.data:
                return self.data[key]
            return None
    
    def delete(self, key: str) -> None:
        """Delete a key-value pair."""
        with self.lock:
            if self.active and key in self.data:
                del self.data[key]
    
    def get_all_keys(self) -> Set[str]:
        """Return all keys stored in this node."""
        with self.lock:
            return set(self.data.keys())
    
    def count_keys(self) -> int:
        """Return the number of keys stored in this node."""
        with self.lock:
            return len(self.data)


class ConsistentKVStore:
    """Distributed key-value store with consistency guarantees."""
    
    def __init__(self, node_ids: List[int], replication_factor: int):
        """Initialize the distributed KV store.
        
        Args:
            node_ids: List of unique node IDs in the cluster
            replication_factor: Number of replicas for each key-value pair
        """
        if len(node_ids) < replication_factor:
            raise ValueError("Number of nodes must be at least equal to the replication factor")
        
        self.replication_factor = replication_factor
        self.nodes: Dict[int, Node] = {node_id: Node(node_id) for node_id in node_ids}
        self.lock = threading.RLock()
        
        # Create consistent hashing ring
        # Each node has multiple virtual nodes for better distribution
        self.ring: List[Tuple[int, int]] = []  # [(hash_value, node_id)]
        self.virtual_nodes = 100  # Number of virtual nodes per physical node
        self._build_ring()
    
    def _build_ring(self) -> None:
        """Build the consistent hashing ring with virtual nodes."""
        with self.lock:
            self.ring = []
            for node_id in self.nodes:
                for i in range(self.virtual_nodes):
                    # Create hash for each virtual node
                    key = f"{node_id}:{i}"
                    hash_val = self._hash(key)
                    self.ring.append((hash_val, node_id))
            
            # Sort ring by hash values
            self.ring.sort()
    
    def _hash(self, key: str) -> int:
        """Hash a key using MD5 and return a 32-bit integer."""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) & 0xFFFFFFFF
    
    def _get_node_for_key(self, key: str) -> int:
        """Find the node responsible for a key using consistent hashing."""
        if not self.ring:
            raise RuntimeError("Consistent hashing ring is empty")
        
        hash_val = self._hash(key)
        
        # Find the first node with hash >= key's hash
        idx = bisect.bisect_left(self.ring, (hash_val, 0))
        
        # Wrap around if needed
        if idx >= len(self.ring):
            idx = 0
            
        return self.ring[idx][1]  # Return node ID
    
    def _get_replica_nodes(self, key: str) -> List[int]:
        """Get the list of node IDs that should store replicas for a key."""
        with self.lock:
            if not self.ring:
                return []
            
            hash_val = self._hash(key)
            
            # Find starting position in the ring
            idx = bisect.bisect_left(self.ring, (hash_val, 0))
            if idx >= len(self.ring):
                idx = 0
            
            # Collect unique nodes moving clockwise
            replica_nodes = []
            unique_nodes = set()
            i = idx
            
            while len(unique_nodes) < self.replication_factor and len(unique_nodes) < len(self.nodes):
                node_id = self.ring[i][1]
                
                if node_id not in unique_nodes and self.nodes[node_id].active:
                    unique_nodes.add(node_id)
                    replica_nodes.append(node_id)
                
                i = (i + 1) % len(self.ring)
                
                # Avoid infinite loop if not enough active nodes
                if i == idx:
                    break
            
            return replica_nodes
    
    def put(self, key: str, value: Any) -> None:
        """Store a key-value pair in the distributed store."""
        replica_nodes = self._get_replica_nodes(key)
        
        # Store value in all replica nodes
        for node_id in replica_nodes:
            self.nodes[node_id].put(key, value)
    
    def get(self, key: str) -> Any:
        """Retrieve a key's value from the distributed store."""
        replica_nodes = self._get_replica_nodes(key)
        
        # Check all replicas and find the most recent value
        latest_value = None
        latest_timestamp = 0
        node_values = {}  # Track values from different nodes for read repair
        
        for node_id in replica_nodes:
            result = self.nodes[node_id].get(key)
            if result:
                value, timestamp = result
                node_values[node_id] = (value, timestamp)
                
                if timestamp > latest_timestamp:
                    latest_value = value
                    latest_timestamp = timestamp
        
        # Perform read repair if we found a value and there are inconsistencies
        if latest_value is not None and len(node_values) > 0:
            self._read_repair(key, latest_value, latest_timestamp, node_values, replica_nodes)
        
        return latest_value
    
    def _read_repair(self, key: str, latest_value: Any, latest_timestamp: float, 
                    node_values: Dict[int, Tuple[Any, float]], replica_nodes: List[int]) -> None:
        """Repair inconsistent replicas in the background."""
        
        def repair_worker():
            for node_id in replica_nodes:
                # If node doesn't have the value or has an outdated value
                if node_id not in node_values or node_values[node_id][1] < latest_timestamp:
                    if self.nodes[node_id].active:
                        self.nodes[node_id].put(key, latest_value)
        
        # Start repair in background thread
        thread = threading.Thread(target=repair_worker)
        thread.daemon = True
        thread.start()
    
    def delete(self, key: str) -> None:
        """Delete a key-value pair from the distributed store."""
        replica_nodes = self._get_replica_nodes(key)
        
        # Delete from all replica nodes
        for node_id in replica_nodes:
            self.nodes[node_id].delete(key)
    
    def node_failure(self, node_id: int) -> None:
        """Simulate a node failure."""
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].active = False
    
    def node_recovery(self, node_id: int) -> None:
        """Simulate a node recovery."""
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].active = True
                # Re-sync data for this node
                self._sync_recovered_node(node_id)
    
    def _sync_recovered_node(self, node_id: int) -> None:
        """Synchronize a recovered node with the latest data it's responsible for."""
        # Find all keys this node should have
        keys_to_sync = set()
        for node in self.nodes.values():
            if node.id != node_id and node.active:
                for key in node.get_all_keys():
                    if node_id in self._get_replica_nodes(key):
                        keys_to_sync.add(key)
        
        # Sync each key
        for key in keys_to_sync:
            value = self.get(key)  # This will trigger read repair
    
    def add_node(self, node_id: int) -> None:
        """Add a new node to the cluster."""
        with self.lock:
            if node_id in self.nodes:
                raise ValueError(f"Node with ID {node_id} already exists")
            
            # Add the new node
            self.nodes[node_id] = Node(node_id)
            
            # Rebuild the ring
            self._build_ring()
            
            # Rebalance data
            self._rebalance_after_node_change()
    
    def _rebalance_after_node_change(self) -> None:
        """Rebalance data after adding or removing a node."""
        # Get all keys from all nodes
        all_keys = set()
        for node in self.nodes.values():
            if node.active:
                all_keys.update(node.get_all_keys())
        
        # For each key, check if it's on the correct nodes, move if needed
        for key in all_keys:
            correct_nodes = self._get_replica_nodes(key)
            
            # Find current location of key
            current_value = None
            latest_timestamp = 0
            
            for node_id, node in self.nodes.items():
                if node.active:
                    result = node.get(key)
                    if result:
                        value, timestamp = result
                        if timestamp > latest_timestamp:
                            current_value = value
                            latest_timestamp = timestamp
                        
                        # Delete if node shouldn't have this key anymore
                        if node_id not in correct_nodes:
                            node.delete(key)
            
            # Add to nodes that should have this key but don't
            if current_value is not None:
                for node_id in correct_nodes:
                    node = self.nodes[node_id]
                    if node.active:
                        result = node.get(key)
                        if not result:
                            node.put(key, current_value)
    
    def create_inconsistency(self, key: str, incorrect_value: Any, num_replicas: int) -> None:
        """Create an inconsistency for testing read repair."""
        replica_nodes = self._get_replica_nodes(key)
        
        # Modify a subset of replicas with incorrect value
        for i in range(min(num_replicas, len(replica_nodes))):
            node_id = replica_nodes[i]
            self.nodes[node_id].put(key, incorrect_value)
            # Set an older timestamp
            self.nodes[node_id].data[key] = (incorrect_value, 
                                            self.nodes[node_id].data[key][1] - 100)
    
    def check_inconsistency(self, key: str) -> bool:
        """Check if there's any inconsistency for a key."""
        replica_nodes = self._get_replica_nodes(key)
        
        values = set()
        for node_id in replica_nodes:
            result = self.nodes[node_id].get(key)
            if result:
                values.add(result[0])
        
        # If there's more than one distinct value, there's inconsistency
        return len(values) > 1
    
    def get_key_distribution(self) -> Dict[int, int]:
        """Return the number of keys stored on each node."""
        distribution = {}
        for node_id, node in self.nodes.items():
            distribution[node_id] = node.count_keys()
        return distribution