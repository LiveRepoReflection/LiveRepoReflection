import hashlib
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

class Server:
    """
    Represents a server in the distributed key-value store.
    
    Each server stores key-value pairs and manages its own data.
    """
    
    def __init__(self, server_id: str):
        """
        Initialize a new server.
        
        Args:
            server_id: Unique identifier for this server
        """
        self._server_id = server_id
        self._data: Dict[str, Tuple[float, Any]] = {}  # key -> (timestamp, value)
        self._lock = threading.RLock()
        
    def put(self, key: str, value: Any) -> None:
        """
        Store a key-value pair.
        
        Args:
            key: The key to store
            value: The value to store
        """
        with self._lock:
            self._data[key] = (time.time(), value)
            
    def get(self, key: str) -> Tuple[Optional[float], Optional[Any]]:
        """
        Retrieve a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            Tuple of (timestamp, value) if key exists, else (None, None)
        """
        with self._lock:
            if key in self._data:
                return self._data[key]
            return None, None
            
    def delete(self, key: str) -> None:
        """
        Delete a key-value pair.
        
        Args:
            key: The key to delete
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
                
    def get_all_data(self) -> Dict[str, Tuple[float, Any]]:
        """
        Get all data stored on this server.
        
        Returns:
            Dictionary mapping keys to (timestamp, value) tuples
        """
        with self._lock:
            return dict(self._data)
            
    def bulk_put(self, data: Dict[str, Tuple[float, Any]]) -> None:
        """
        Store multiple key-value pairs at once.
        
        Args:
            data: Dictionary mapping keys to (timestamp, value) tuples
        """
        with self._lock:
            self._data.update(data)


class DistributedKVStore:
    """
    A distributed key-value store using consistent hashing.
    
    Implements data replication and handles server joins/leaves.
    """
    
    def __init__(self, num_servers: int, virtual_nodes: int, replication_factor: int):
        """
        Initialize a new distributed key-value store.
        
        Args:
            num_servers: Number of servers in the initial cluster
            virtual_nodes: Number of virtual nodes per physical server
            replication_factor: Number of replicas for each key-value pair
        """
        self._virtual_nodes = virtual_nodes
        self._replication_factor = min(replication_factor, num_servers)
        self._ring: Dict[int, str] = {}  # hash position -> server_id-replica_id
        self._servers: Dict[str, Server] = {}  # server_id -> Server
        self._lock = threading.RLock()
        
        # Initialize servers
        for i in range(1, num_servers + 1):
            server_id = f"server{i}"
            self._add_server(server_id)
    
    def _hash(self, key: str) -> int:
        """
        Compute the hash of a key.
        
        Args:
            key: The key to hash
            
        Returns:
            The hash value (32-bit integer)
        """
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
    
    def _add_server(self, server_id: str) -> None:
        """
        Add a server to the cluster (internal method).
        
        Args:
            server_id: Unique identifier for the new server
        """
        # Create the server object
        self._servers[server_id] = Server(server_id)
        
        # Add virtual nodes to the hash ring
        for i in range(self._virtual_nodes):
            node_name = f"{server_id}-{i}"
            node_hash = self._hash(node_name)
            self._ring[node_hash] = server_id
    
    def _remove_server(self, server_id: str) -> Dict[str, Tuple[float, Any]]:
        """
        Remove a server from the cluster (internal method).
        
        Args:
            server_id: Identifier of server to remove
            
        Returns:
            Dictionary of key-value pairs that were stored on the server
        """
        # Get all data from the server before removing it
        server_data = self._servers[server_id].get_all_data()
        
        # Remove virtual nodes from hash ring
        for i in range(self._virtual_nodes):
            node_name = f"{server_id}-{i}"
            node_hash = self._hash(node_name)
            if node_hash in self._ring:
                del self._ring[node_hash]
        
        # Remove server
        del self._servers[server_id]
        
        return server_data
    
    def _find_responsible_servers(self, key: str) -> List[str]:
        """
        Find the servers responsible for storing a key.
        
        Args:
            key: The key to look up
            
        Returns:
            List of server IDs responsible for the key
        """
        if not self._ring:
            return []
            
        key_hash = self._hash(key)
        
        # Sort the hash positions
        positions = sorted(self._ring.keys())
        
        # Find the first position >= key_hash
        responsible_positions = []
        
        # Find the R successors (might wrap around)
        for i in range(len(positions)):
            if positions[i] >= key_hash:
                start_idx = i
                break
        else:
            # If all positions are < key_hash, start from the beginning
            start_idx = 0
        
        # Collect unique server IDs (since virtual nodes map to the same server)
        responsible_servers = []
        unique_servers = set()
        
        i = start_idx
        while len(responsible_servers) < self._replication_factor and len(unique_servers) < len(self._servers):
            server_id = self._ring[positions[i]]
            if server_id not in unique_servers:
                unique_servers.add(server_id)
                responsible_servers.append(server_id)
            i = (i + 1) % len(positions)
        
        return responsible_servers
    
    def put(self, key: str, value: Any) -> None:
        """
        Store a key-value pair in the distributed store.
        
        Args:
            key: The key to store
            value: The value to store
        """
        with self._lock:
            servers = self._find_responsible_servers(key)
            timestamp = time.time()
            
            # Store on all responsible servers
            for server_id in servers:
                self._servers[server_id].put(key, value)
    
    def get(self, key: str) -> Any:
        """
        Retrieve a value by key from the distributed store.
        
        Handles potential inconsistencies by returning the most recent value.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if key exists, else None
        """
        with self._lock:
            servers = self._find_responsible_servers(key)
            
            latest_timestamp = None
            latest_value = None
            
            # Query all responsible servers
            for server_id in servers:
                timestamp, value = self._servers[server_id].get(key)
                
                # Keep the most recent value
                if timestamp is not None and (latest_timestamp is None or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    latest_value = value
            
            return latest_value
    
    def delete(self, key: str) -> None:
        """
        Delete a key-value pair from the distributed store.
        
        Args:
            key: The key to delete
        """
        with self._lock:
            servers = self._find_responsible_servers(key)
            
            # Delete from all responsible servers
            for server_id in servers:
                self._servers[server_id].delete(key)
    
    def join(self, server_id: str) -> None:
        """
        Add a new server to the cluster.
        
        Redistributes data according to consistent hashing rules.
        
        Args:
            server_id: Unique identifier for the new server
        """
        with self._lock:
            # Add the new server
            self._add_server(server_id)
            
            # Collect all keys in the system
            all_keys = set()
            for s_id, server in self._servers.items():
                for key in server.get_all_data().keys():
                    all_keys.add(key)
            
            # Re-route keys that should now go to the new server
            for key in all_keys:
                # Get current value
                current_value = self.get(key)
                if current_value is not None:
                    # Find new responsible servers
                    responsible_servers = self._find_responsible_servers(key)
                    
                    # If new server is responsible, update replication
                    if server_id in responsible_servers:
                        # Re-put to update all responsible servers
                        self.put(key, current_value)
    
    def leave(self, server_id: str) -> None:
        """
        Remove a server from the cluster.
        
        Redistributes data to maintain replication factor.
        
        Args:
            server_id: Identifier of server to remove
        """
        with self._lock:
            if server_id not in self._servers:
                return
                
            # Get all data from the server before removing it
            server_data = self._remove_server(server_id)
            
            # Re-distribute data
            for key, (timestamp, value) in server_data.items():
                # Find new responsible servers
                responsible_servers = self._find_responsible_servers(key)
                
                # Only re-distribute if there are still enough servers
                if responsible_servers:
                    # Get the most up-to-date value
                    latest_value = self.get(key)
                    
                    # If the key still exists, re-put it to ensure proper replication
                    if latest_value is not None:
                        self.put(key, latest_value)