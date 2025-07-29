import hashlib
import threading
from collections import defaultdict
from typing import Callable, List, Optional, Dict, Tuple

class VirtualNode:
    def __init__(self, node_id: str, physical_node: str):
        self.node_id = node_id
        self.physical_node = physical_node
        self.data: Dict[str, Tuple[str, int]] = {}  # key: (value, version)

    def get(self, key: str) -> Optional[str]:
        return self.data.get(key, (None, 0))[0]

    def put(self, key: str, value: str, version: int) -> bool:
        current_version = self.data.get(key, (None, 0))[1]
        if version > current_version:
            self.data[key] = (value, version)
            return True
        return False

    def delete(self, key: str) -> bool:
        if key in self.data:
            del self.data[key]
            return True
        return False

class DistributedKVStore:
    def __init__(self, node_id: str, get_node_list_func: Callable[[], List[str]], replication_factor: int = 3):
        self.node_id = node_id
        self.get_node_list = get_node_list_func
        self.replication_factor = replication_factor
        self.ring: Dict[int, VirtualNode] = {}
        self.virtual_nodes: Dict[str, List[VirtualNode]] = defaultdict(list)
        self.lock = threading.Lock()
        self.version_counter = 0
        self.initialize_ring()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def initialize_ring(self):
        with self.lock:
            nodes = self.get_node_list()
            for node in nodes:
                for i in range(100):  # 100 virtual nodes per physical node
                    vnode_id = f"{node}-vnode-{i}"
                    hash_val = self._hash(vnode_id)
                    vnode = VirtualNode(vnode_id, node)
                    self.ring[hash_val] = vnode
                    self.virtual_nodes[node].append(vnode)
            self.ring = dict(sorted(self.ring.items()))

    def _get_replica_nodes(self, key: str) -> List[VirtualNode]:
        key_hash = self._hash(key)
        sorted_hashes = sorted(self.ring.keys())
        if not sorted_hashes:
            return []

        # Find the first node with hash >= key_hash
        idx = 0
        while idx < len(sorted_hashes) and sorted_hashes[idx] < key_hash:
            idx += 1

        if idx == len(sorted_hashes):
            idx = 0

        replica_nodes = []
        for i in range(self.replication_factor):
            node_hash = sorted_hashes[(idx + i) % len(sorted_hashes)]
            replica_nodes.append(self.ring[node_hash])

        return replica_nodes

    def put(self, key: str, value: str):
        with self.lock:
            self.version_counter += 1
            version = self.version_counter
            replica_nodes = self._get_replica_nodes(key)
            
            success_count = 0
            for node in replica_nodes:
                if node.put(key, value, version):
                    success_count += 1
            
            if success_count < (self.replication_factor // 2 + 1):
                raise Exception("Failed to achieve quorum for write operation")

    def get(self, key: str) -> Optional[str]:
        replica_nodes = self._get_replica_nodes(key)
        versions = []
        values = []
        
        for node in replica_nodes:
            value, version = node.data.get(key, (None, 0))
            if value is not None:
                versions.append(version)
                values.append(value)
        
        if not values:
            return None
        
        # Return the value with highest version (last write wins)
        max_version = max(versions)
        return values[versions.index(max_version)]

    def delete(self, key: str):
        with self.lock:
            self.version_counter += 1
            version = self.version_counter
            replica_nodes = self._get_replica_nodes(key)
            
            success_count = 0
            for node in replica_nodes:
                if node.delete(key):
                    success_count += 1
            
            if success_count < (self.replication_factor // 2 + 1):
                raise Exception("Failed to achieve quorum for delete operation")

    def handle_node_failure(self, failed_node: str):
        with self.lock:
            # Remove failed node from ring
            for vnode in self.virtual_nodes.get(failed_node, []):
                for hash_val, node in list(self.ring.items()):
                    if node.node_id == vnode.node_id:
                        del self.ring[hash_val]
            
            # Redistribute data from failed node
            for vnode in self.virtual_nodes.get(failed_node, []):
                for key, (value, version) in vnode.data.items():
                    self.put(key, value)  # This will redistribute to new nodes
            
            # Update node list
            if failed_node in self.virtual_nodes:
                del self.virtual_nodes[failed_node]