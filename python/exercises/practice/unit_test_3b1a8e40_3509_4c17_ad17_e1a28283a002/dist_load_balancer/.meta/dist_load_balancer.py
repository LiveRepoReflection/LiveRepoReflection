import hashlib
import threading
import time
import bisect
import heapq
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Set


class HealthCheckStatus(Enum):
    """Health check status enumeration."""
    HEALTHY = auto()
    UNHEALTHY = auto()


class CircuitState(Enum):
    """Circuit breaker state enumeration."""
    CLOSED = auto()  # Normal operation
    OPEN = auto()    # Stop sending traffic
    HALF_OPEN = auto()  # Testing if system has recovered


class Server:
    """Represents a backend server in the load balancing system."""
    
    def __init__(self, server_id: str, address: str, weight: int = 1, ttl: Optional[int] = None):
        self.server_id = server_id
        self.address = address
        self.weight = weight
        self.health_status = HealthCheckStatus.HEALTHY
        self.active_connections = 0
        self.total_requests = 0
        self.created_at = time.time()
        self.ttl = ttl  # Time to live in seconds
        
        # Circuit breaker properties
        self.circuit_state = "CLOSED"  # Initially closed
        self.failure_count = 0
        self.failure_threshold = 5
        self.recovery_timeout = 30  # seconds
        self.last_failure_time = 0
        
        # Thread safety
        self.lock = threading.RLock()
    
    def is_healthy(self) -> bool:
        """Check if the server is healthy and available to receive traffic."""
        with self.lock:
            # Check if circuit is open
            if self.circuit_state == "OPEN":
                # Check if we should try half-open state
                current_time = time.time()
                if current_time - self.last_failure_time >= self.recovery_timeout:
                    self.circuit_state = "HALF_OPEN"
                else:
                    return False
            
            # Check actual health status
            return self.health_status == HealthCheckStatus.HEALTHY
    
    def is_expired(self) -> bool:
        """Check if the server has exceeded its TTL."""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def mark_healthy(self) -> None:
        """Mark the server as healthy."""
        with self.lock:
            self.health_status = HealthCheckStatus.HEALTHY
            if self.circuit_state == "HALF_OPEN":
                # Server recovered, close the circuit
                self.circuit_state = "CLOSED"
                self.failure_count = 0
    
    def mark_unhealthy(self) -> None:
        """Mark the server as unhealthy and update circuit breaker state."""
        with self.lock:
            self.health_status = HealthCheckStatus.UNHEALTHY
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Check if we need to open the circuit
            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
    
    def increment_connections(self) -> None:
        """Increment the active connections counter."""
        with self.lock:
            self.active_connections += 1
            self.total_requests += 1
    
    def decrement_connections(self) -> None:
        """Decrement the active connections counter."""
        with self.lock:
            if self.active_connections > 0:
                self.active_connections -= 1


class LoadBalancingStrategy:
    """Base class for load balancing strategies."""
    
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
    
    def get_next_server(self) -> str:
        """Get the next server to handle a request."""
        raise NotImplementedError("Subclasses must implement get_next_server()")


class WeightedRoundRobinStrategy(LoadBalancingStrategy):
    """Implements a weighted round robin load balancing strategy."""
    
    def __init__(self, load_balancer):
        super().__init__(load_balancer)
        self.current_index = 0
        self.lock = threading.Lock()
    
    def get_next_server(self) -> str:
        """Get the next server based on weighted round robin."""
        with self.lock:
            # Get all healthy servers
            healthy_servers = self.load_balancer.get_healthy_servers()
            if not healthy_servers:
                raise Exception("No healthy servers available")
            
            # Create a weighted list of servers
            weighted_servers = []
            for server in healthy_servers:
                weighted_servers.extend([server.address] * server.weight)
            
            # Get the next server and update the index
            if not weighted_servers:
                raise Exception("No weighted servers available")
            
            self.current_index %= len(weighted_servers)
            server_address = weighted_servers[self.current_index]
            self.current_index += 1
            
            # Increment active connections
            server_id = self.load_balancer.address_to_id.get(server_address)
            if server_id:
                self.load_balancer.servers[server_id].increment_connections()
            
            return server_address


class LeastConnectionsStrategy(LoadBalancingStrategy):
    """Implements a least connections load balancing strategy."""
    
    def get_next_server(self) -> str:
        """Get the server with the least active connections."""
        with self.load_balancer.lock:
            # Get all healthy servers
            healthy_servers = self.load_balancer.get_healthy_servers()
            if not healthy_servers:
                raise Exception("No healthy servers available")
            
            # Find the server with the least active connections
            min_connections = float('inf')
            selected_server = None
            
            for server in healthy_servers:
                # Consider both active connections and server weight
                effective_load = server.active_connections / server.weight
                if effective_load < min_connections:
                    min_connections = effective_load
                    selected_server = server
            
            if selected_server:
                selected_server.increment_connections()
                return selected_server.address
            else:
                raise Exception("No server selected")


class ConsistentHashingStrategy(LoadBalancingStrategy):
    """Implements consistent hashing for load balancing."""
    
    def __init__(self, load_balancer):
        super().__init__(load_balancer)
        self.ring = {}  # Hash ring
        self.sorted_keys = []  # Sorted hash keys
        self.replicas = 100  # Number of virtual nodes per server
        self.lock = threading.Lock()
    
    def _hash(self, key: str) -> int:
        """Hash a key to get its position on the ring."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_server(self, server_id: str, server_address: str) -> None:
        """Add a server to the hash ring."""
        with self.lock:
            for i in range(self.replicas):
                key = f"{server_address}:{i}"
                hash_key = self._hash(key)
                self.ring[hash_key] = server_id
                bisect.insort(self.sorted_keys, hash_key)
    
    def remove_server(self, server_id: str, server_address: str) -> None:
        """Remove a server from the hash ring."""
        with self.lock:
            keys_to_remove = []
            for i in range(self.replicas):
                key = f"{server_address}:{i}"
                hash_key = self._hash(key)
                if hash_key in self.ring and self.ring[hash_key] == server_id:
                    keys_to_remove.append(hash_key)
            
            for hash_key in keys_to_remove:
                self.ring.pop(hash_key, None)
                try:
                    idx = self.sorted_keys.index(hash_key)
                    self.sorted_keys.pop(idx)
                except ValueError:
                    pass
    
    def get_server_for_key(self, key: str) -> str:
        """Get the server responsible for handling a specific key."""
        if not self.ring:
            raise Exception("Hash ring is empty, no servers available")
        
        with self.lock:
            hash_key = self._hash(key)
            
            # Find the server responsible for this key
            for idx in range(len(self.sorted_keys)):
                if hash_key <= self.sorted_keys[idx]:
                    server_id = self.ring[self.sorted_keys[idx]]
                    return server_id
            
            # If we reached here, use the first server in the ring
            server_id = self.ring[self.sorted_keys[0]]
            return server_id
    
    def get_next_server(self) -> str:
        """For general use, we'll use a random key."""
        key = str(time.time())  # Use current time as a random key
        server_id = self.get_server_for_key(key)
        
        # Get the server address from the ID
        server = self.load_balancer.servers.get(server_id)
        if not server or not server.is_healthy():
            # Try to find a healthy server
            healthy_servers = self.load_balancer.get_healthy_servers()
            if not healthy_servers:
                raise Exception("No healthy servers available")
            server = healthy_servers[0]
        
        server.increment_connections()
        return server.address


class LoadBalancer:
    """
    The main load balancer class implementing a distributed load balancing system.
    """
    
    def __init__(self, instance_id: str = "lb_default"):
        self.instance_id = instance_id
        self.servers: Dict[str, Server] = {}
        self.address_to_id: Dict[str, str] = {}
        self.strategies = {
            "weighted_round_robin": WeightedRoundRobinStrategy(self),
            "least_connections": LeastConnectionsStrategy(self),
            "consistent_hashing": ConsistentHashingStrategy(self)
        }
        self.current_strategy = "weighted_round_robin"
        self.lock = threading.RLock()  # Reentrant lock for thread safety
    
    def add_server(self, server_id: str, address: str, weight: int = 1, ttl: Optional[int] = None) -> None:
        """
        Add a new backend server to the load balancer.
        
        Args:
            server_id: Unique identifier for the server
            address: Network address of the server
            weight: Weight for weighted round robin distribution
            ttl: Time to live in seconds, after which the server will be automatically removed
        """
        with self.lock:
            if server_id in self.servers:
                raise ValueError(f"Server with ID {server_id} already exists")
            
            server = Server(server_id, address, weight, ttl)
            self.servers[server_id] = server
            self.address_to_id[address] = server_id
            
            # Add to consistent hashing ring
            if "consistent_hashing" in self.strategies:
                self.strategies["consistent_hashing"].add_server(server_id, address)
    
    def remove_server(self, server_id: str) -> None:
        """
        Remove a backend server from the load balancer.
        
        Args:
            server_id: Unique identifier for the server to remove
        """
        with self.lock:
            if server_id in self.servers:
                server = self.servers[server_id]
                
                # Remove from consistent hashing ring
                if "consistent_hashing" in self.strategies:
                    self.strategies["consistent_hashing"].remove_server(server_id, server.address)
                
                # Remove from address mapping
                if server.address in self.address_to_id:
                    del self.address_to_id[server.address]
                
                # Remove server
                del self.servers[server_id]
    
    def health_check_passed(self, server_id: str) -> None:
        """
        Notify that a health check passed for a specific server.
        
        Args:
            server_id: Unique identifier for the server
        """
        with self.lock:
            if server_id in self.servers:
                self.servers[server_id].mark_healthy()
    
    def health_check_failed(self, server_id: str) -> None:
        """
        Notify that a health check failed for a specific server.
        
        Args:
            server_id: Unique identifier for the server
        """
        with self.lock:
            if server_id in self.servers:
                self.servers[server_id].mark_unhealthy()
    
    def get_next_server(self) -> str:
        """
        Get the address of the next server to handle a request based on the current load balancing strategy.
        
        Returns:
            str: The address of the selected server
        
        Raises:
            Exception: If no healthy servers are available
        """
        strategy = self.strategies[self.current_strategy]
        return strategy.get_next_server()
    
    def set_strategy(self, strategy_name: str) -> None:
        """
        Set the load balancing strategy to use.
        
        Args:
            strategy_name: Name of the strategy to use
        
        Raises:
            ValueError: If the strategy name is invalid
        """
        with self.lock:
            if strategy_name not in self.strategies:
                raise ValueError(f"Invalid strategy name: {strategy_name}")
            self.current_strategy = strategy_name
    
    def get_healthy_servers(self) -> List[Server]:
        """
        Get a list of all healthy servers.
        
        Returns:
            List[Server]: List of healthy server objects
        """
        with self.lock:
            return [server for server in self.servers.values() if server.is_healthy()]
    
    def _get_server_for_key(self, key: str) -> str:
        """
        Get the server responsible for handling a specific key using consistent hashing.
        
        Args:
            key: The key to find a server for
        
        Returns:
            str: The server ID for the key
        
        Raises:
            Exception: If no servers are available
        """
        return self.strategies["consistent_hashing"].get_server_for_key(key)
    
    def remove_expired_servers(self) -> None:
        """Remove any servers that have exceeded their TTL."""
        with self.lock:
            expired_server_ids = []
            current_time = time.time()
            
            for server_id, server in self.servers.items():
                if server.is_expired():
                    expired_server_ids.append(server_id)
            
            for server_id in expired_server_ids:
                self.remove_server(server_id)
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the current load balancer state.
        
        Returns:
            Dict: Dictionary containing load balancer statistics
        """
        with self.lock:
            return {
                "instance_id": self.instance_id,
                "server_count": len(self.servers),
                "healthy_server_count": len(self.get_healthy_servers()),
                "current_strategy": self.current_strategy,
                "servers": {
                    server_id: {
                        "address": server.address,
                        "healthy": server.is_healthy(),
                        "active_connections": server.active_connections,
                        "total_requests": server.total_requests,
                        "weight": server.weight,
                        "circuit_state": server.circuit_state
                    } for server_id, server in self.servers.items()
                }
            }