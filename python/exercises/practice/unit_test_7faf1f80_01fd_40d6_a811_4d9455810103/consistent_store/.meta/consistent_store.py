import hashlib
import bisect
import threading

class ConsistentStore:
    def __init__(self, virtual_nodes=100):
        self.virtual_nodes = virtual_nodes
        self.ring = []
        self.nodes = {}
        self.data = {}
        self.lock = threading.Lock()
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def _get_virtual_nodes(self, node_id):
        return [f"{node_id}-{i}" for i in range(self.virtual_nodes)]
    
    def _find_node(self, key_hash):
        if not self.ring:
            return None
        
        idx = bisect.bisect_right(self.ring, key_hash) % len(self.ring)
        return self.ring[idx]
    
    def add_node(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                raise ValueError(f"Node {node_id} already exists")
            
            virtual_nodes = self._get_virtual_nodes(node_id)
            self.nodes[node_id] = virtual_nodes
            
            for vnode in virtual_nodes:
                vnode_hash = self._hash(vnode)
                bisect.insort(self.ring, vnode_hash)
                self.data[vnode] = {}
    
    def remove_node(self, node_id):
        with self.lock:
            if node_id not in self.nodes:
                raise ValueError(f"Node {node_id} does not exist")
            
            virtual_nodes = self.nodes[node_id]
            del self.nodes[node_id]
            
            for vnode in virtual_nodes:
                vnode_hash = self._hash(vnode)
                idx = bisect.bisect_left(self.ring, vnode_hash)
                if idx < len(self.ring) and self.ring[idx] == vnode_hash:
                    self.ring.pop(idx)
                del self.data[vnode]
    
    def get_node(self, key):
        if not self.ring:
            return None
            
        key_hash = self._hash(key)
        vnode_hash = self._find_node(key_hash)
        
        for node_id, virtual_nodes in self.nodes.items():
            for vnode in virtual_nodes:
                if self._hash(vnode) == vnode_hash:
                    return node_id
        return None
    
    def put(self, key, value):
        with self.lock:
            if not self.ring:
                raise ValueError("No nodes available in the cluster")
                
            key_hash = self._hash(key)
            vnode_hash = self._find_node(key_hash)
            
            for vnode, data_store in self.data.items():
                if self._hash(vnode) == vnode_hash:
                    data_store[key] = value
                    return
            
            raise ValueError("Failed to find appropriate node for storage")
    
    def get(self, key):
        with self.lock:
            if not self.ring:
                return None
                
            key_hash = self._hash(key)
            vnode_hash = self._find_node(key_hash)
            
            for vnode, data_store in self.data.items():
                if self._hash(vnode) == vnode_hash:
                    return data_store.get(key, None)
            
            return None