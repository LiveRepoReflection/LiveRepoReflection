import threading
import shelve
import os
import tempfile
from collections import OrderedDict
from typing import Optional

class Node:
    def __init__(self, capacity: int, node_id: int):
        self.capacity = capacity
        self.node_id = node_id
        self.cache = OrderedDict()  # In-memory LRU cache
        self.lock = threading.Lock()
        
        # Create a temporary directory for disk storage
        self.temp_dir = tempfile.mkdtemp()
        self.disk_path = os.path.join(self.temp_dir, f"node_{node_id}")

    def _get_from_disk(self, key: str) -> Optional[str]:
        """Retrieve value from disk storage."""
        with shelve.open(self.disk_path) as disk_store:
            return disk_store.get(key)

    def _put_to_disk(self, key: str, value: str) -> None:
        """Store value to disk storage."""
        with shelve.open(self.disk_path) as disk_store:
            disk_store[key] = value

    def _delete_from_disk(self, key: str) -> None:
        """Delete value from disk storage."""
        with shelve.open(self.disk_path) as disk_store:
            if key in disk_store:
                del disk_store[key]

    def get(self, key: str) -> Optional[str]:
        """Get value for key from either memory or disk."""
        with self.lock:
            # Try to get from memory first
            if key in self.cache:
                # Update LRU order
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            
            # If not in memory, try to get from disk
            return self._get_from_disk(key)

    def put(self, key: str, value: str) -> None:
        """Store key-value pair in both memory and disk."""
        with self.lock:
            # Always store in disk for durability
            self._put_to_disk(key, value)
            
            # Update or insert into memory cache
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # Evict least recently used item if cache is full
                self.cache.popitem(last=False)
            
            self.cache[key] = value

    def delete(self, key: str) -> None:
        """Delete key-value pair from both memory and disk."""
        with self.lock:
            # Remove from memory if present
            if key in self.cache:
                del self.cache[key]
            
            # Remove from disk
            self._delete_from_disk(key)

    def cleanup(self):
        """Clean up temporary disk storage."""
        try:
            os.remove(self.disk_path)
            os.rmdir(self.temp_dir)
        except:
            pass

class TieredKVStore:
    def __init__(self, num_nodes: int, cache_capacity: int):
        if num_nodes <= 0 or cache_capacity <= 0:
            raise ValueError("Number of nodes and cache capacity must be positive")
        
        self.num_nodes = num_nodes
        self.nodes = [Node(cache_capacity, i) for i in range(num_nodes)]
        self.lock = threading.Lock()

    def _get_node(self, key: str) -> Node:
        """Get the responsible node for a given key using consistent hashing."""
        node_id = hash(key) % self.num_nodes
        return self.nodes[node_id]

    def put(self, key: str, value: str) -> None:
        """Store a key-value pair in the distributed store."""
        if key is None or value is None:
            raise ValueError("Key and value cannot be None")
        
        node = self._get_node(key)
        node.put(key, value)

    def get(self, key: str) -> Optional[str]:
        """Retrieve value for given key from the distributed store."""
        if key is None:
            raise ValueError("Key cannot be None")
        
        node = self._get_node(key)
        return node.get(key)

    def delete(self, key: str) -> None:
        """Delete key-value pair from the distributed store."""
        if key is None:
            raise ValueError("Key cannot be None")
        
        node = self._get_node(key)
        node.delete(key)

    def cleanup(self):
        """Clean up all nodes' disk storage."""
        for node in self.nodes:
            node.cleanup()

    def __del__(self):
        """Destructor to ensure cleanup of disk storage."""
        self.cleanup()