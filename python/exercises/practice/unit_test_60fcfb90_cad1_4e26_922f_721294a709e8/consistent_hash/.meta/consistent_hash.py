import bisect
import hashlib

class ConsistentHash:
    def __init__(self, vnodes=100):
        self.vnodes = vnodes
        self.ring = dict()  # { hash: node_id }
        self.sorted_hashes = []
        self.nodes = set()

    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % (2**32)

    def _get_vnode_hash(self, node_id, replica):
        return self._hash(f"{node_id}_{replica}")

    def add_node(self, node_id):
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        
        self.nodes.add(node_id)
        
        for i in range(self.vnodes):
            vnode_hash = self._get_vnode_hash(node_id, i)
            if vnode_hash in self.ring:
                continue
            
            self.ring[vnode_hash] = node_id
            bisect.insort(self.sorted_hashes, vnode_hash)

    def remove_node(self, node_id):
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        
        self.nodes.remove(node_id)
        
        # Remove all virtual nodes for this physical node
        to_remove = []
        for h in self.sorted_hashes:
            if self.ring[h] == node_id:
                to_remove.append(h)
        
        for h in to_remove:
            del self.ring[h]
            index = bisect.bisect_left(self.sorted_hashes, h)
            if index < len(self.sorted_hashes) and self.sorted_hashes[index] == h:
                self.sorted_hashes.pop(index)

    def get_node(self, key):
        if not self.nodes:
            return -1
            
        key_hash = self._hash(key)
        index = bisect.bisect_left(self.sorted_hashes, key_hash) % len(self.sorted_hashes)
        return self.ring[self.sorted_hashes[index]]