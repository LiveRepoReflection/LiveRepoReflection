import bisect
import hashlib

class ConsistentBalancer:
    def __init__(self, servers=None, virtual_nodes=100):
        self.virtual_nodes = virtual_nodes
        self.ring = []
        self.nodes = {}
        self.server_map = {}
        
        if servers:
            for server in servers:
                self.add_server(server)
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
    
    def _get_virtual_nodes(self, server):
        return [f"{server}#{i}" for i in range(self.virtual_nodes)]
    
    def add_server(self, server):
        if server in self.server_map:
            return
            
        virtual_nodes = self._get_virtual_nodes(server)
        self.server_map[server] = virtual_nodes
        
        for vnode in virtual_nodes:
            key = self._hash(vnode)
            bisect.insort(self.ring, key)
            self.nodes[key] = server
    
    def remove_server(self, server):
        if server not in self.server_map:
            return
            
        virtual_nodes = self.server_map[server]
        del self.server_map[server]
        
        for vnode in virtual_nodes:
            key = self._hash(vnode)
            index = bisect.bisect_left(self.ring, key)
            if index < len(self.ring) and self.ring[index] == key:
                self.ring.pop(index)
                del self.nodes[key]
    
    def get_server(self, content_id):
        if not self.ring:
            raise ValueError("No servers available in the ring")
            
        key = self._hash(content_id)
        index = bisect.bisect_right(self.ring, key) % len(self.ring)
        return self.nodes[self.ring[index]]
    
    def get_all_servers(self):
        return list(self.server_map.keys())