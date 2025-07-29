import threading
import time
from typing import Dict, Optional, Tuple, Any
from collections import OrderedDict
import bisect
import hashlib

class CacheNode:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._lock = threading.Lock()
        self._cache: OrderedDict[str, Tuple[Any, int]] = OrderedDict()

    def put(self, key: str, value: Any, timestamp: int) -> None:
        with self._lock:
            if key in self._cache:
                current_value, current_timestamp = self._cache[key]
                if timestamp <= current_timestamp:
                    return
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._capacity:
                    self._cache.popitem(last=False)
            self._cache[key] = (value, timestamp)

    def get(self, key: str) -> Tuple[Optional[Any], int]:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return None, -1

    def remove(self, key: str, timestamp: int) -> None:
        with self._lock:
            if key in self._cache:
                current_value, current_timestamp = self._cache[key]
                if timestamp >= current_timestamp:
                    del self._cache[key]

    def get_all(self) -> Dict[str, Tuple[Any, int]]:
        with self._lock:
            return dict(self._cache)

class DistributedCache:
    def __init__(self, n_nodes: int = 10, replication_factor: int = 3, node_capacity: int = 1000):
        if n_nodes < 1 or replication_factor < 1 or replication_factor > n_nodes:
            raise ValueError("Invalid configuration")

        self._n_nodes = n_nodes
        self._replication_factor = replication_factor
        self._nodes: Dict[int, CacheNode] = {
            i: CacheNode(node_capacity) for i in range(n_nodes)
        }
        
        # For consistent hashing
        self._node_ring = []
        self._generate_hash_ring()
        
        self._global_lock = threading.Lock()

    def _generate_hash_ring(self) -> None:
        self._node_ring = []
        for node_id in self._nodes:
            # Generate multiple virtual nodes for better distribution
            for i in range(10):
                hash_key = f"{node_id}:{i}"
                hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
                self._node_ring.append((hash_value, node_id))
        self._node_ring.sort()

    def _get_responsible_nodes(self, key: str) -> list[int]:
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
        responsible_nodes = set()
        
        # Find first node
        index = bisect.bisect_right([(h, n) for h, n in self._node_ring], (key_hash, float('inf')))
        if index >= len(self._node_ring):
            index = 0

        # Get R unique nodes
        while len(responsible_nodes) < self._replication_factor:
            responsible_nodes.add(self._node_ring[index][1])
            index = (index + 1) % len(self._node_ring)

        return list(responsible_nodes)

    def _is_node_responsible(self, node_id: int, key_hash: int) -> bool:
        responsible_nodes = self._get_responsible_nodes(str(key_hash))
        return node_id in responsible_nodes

    def put(self, key: str, value: Any, timestamp: int) -> None:
        responsible_nodes = self._get_responsible_nodes(key)
        
        # Write to all responsible nodes
        for node_id in responsible_nodes:
            if node_id in self._nodes:
                self._nodes[node_id].put(key, value, timestamp)

    def get(self, key: str) -> Tuple[Optional[Any], int]:
        responsible_nodes = self._get_responsible_nodes(key)
        latest_value = None
        latest_timestamp = -1

        # Try to get from any responsible node
        for node_id in responsible_nodes:
            if node_id not in self._nodes:
                continue
                
            value, timestamp = self._nodes[node_id].get(key)
            if timestamp > latest_timestamp:
                latest_value = value
                latest_timestamp = timestamp

        return latest_value, latest_timestamp

    def remove(self, key: str, timestamp: int) -> None:
        responsible_nodes = self._get_responsible_nodes(key)
        
        # Remove from all responsible nodes
        for node_id in responsible_nodes:
            if node_id in self._nodes:
                self._nodes[node_id].remove(key, timestamp)

    def _sync_nodes(self) -> None:
        """Background process to sync data between nodes"""
        while True:
            with self._global_lock:
                # Get all data from all nodes
                all_data: Dict[str, Dict[int, Tuple[Any, int]]] = {}
                
                for node_id, node in self._nodes.items():
                    node_data = node.get_all()
                    for key, (value, timestamp) in node_data.items():
                        if key not in all_data:
                            all_data[key] = {}
                        all_data[key][node_id] = (value, timestamp)

                # Ensure each key is properly replicated with the latest version
                for key, node_versions in all_data.items():
                    latest_value = None
                    latest_timestamp = -1
                    
                    # Find latest version
                    for value, timestamp in node_versions.values():
                        if timestamp > latest_timestamp:
                            latest_value = value
                            latest_timestamp = timestamp

                    # Ensure all responsible nodes have the latest version
                    responsible_nodes = self._get_responsible_nodes(key)
                    for node_id in responsible_nodes:
                        if node_id in self._nodes:
                            self._nodes[node_id].put(key, latest_value, latest_timestamp)

            time.sleep(1)  # Sleep to prevent excessive CPU usage

    def start_sync(self) -> None:
        """Start the background sync process"""
        sync_thread = threading.Thread(target=self._sync_nodes, daemon=True)
        sync_thread.start()