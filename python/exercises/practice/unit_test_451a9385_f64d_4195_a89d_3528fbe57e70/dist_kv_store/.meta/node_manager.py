from typing import List, Optional, Dict
import threading
import time

class NodeManager:
    def __init__(self, node_id: int, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.is_alive = True
        self.heartbeat_interval = 1.0  # seconds
        self.last_heartbeat: Dict[int, float] = {}
        self.lock = threading.Lock()
        
    def start_heartbeat(self):
        """Start sending heartbeat signals."""
        def heartbeat_loop():
            while self.is_alive:
                with self.lock:
                    current_time = time.time()
                    self.last_heartbeat[self.node_id] = current_time
                time.sleep(self.heartbeat_interval)
                
        thread = threading.Thread(target=heartbeat_loop)
        thread.daemon = True
        thread.start()
        
    def check_node_health(self, node_id: int) -> bool:
        """Check if a node is healthy based on its last heartbeat."""
        with self.lock:
            if node_id not in self.last_heartbeat:
                return False
            current_time = time.time()
            last_beat = self.last_heartbeat[node_id]
            return (current_time - last_beat) <= (self.heartbeat_interval * 3)
    
    def get_healthy_nodes(self) -> List[int]:
        """Get a list of currently healthy nodes."""
        healthy_nodes = []
        for node_id in range(self.total_nodes):
            if self.check_node_health(node_id):
                healthy_nodes.append(node_id)
        return healthy_nodes
    
    def shutdown(self):
        """Gracefully shutdown the node."""
        self.is_alive = False