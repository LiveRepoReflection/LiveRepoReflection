import hashlib
from enum import Enum
import threading

class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    CONSISTENT_HASHING = "consistent_hashing"

class LoadBalancer:
    def __init__(self):
        self.servers = []
        self.round_robin_index = 0
        self.consistent_hash_ring = {}
        self.lock = threading.Lock()

    def add_server(self, server_id):
        with self.lock:
            if server_id not in self.servers:
                self.servers.append(server_id)
                if LoadBalancingAlgorithm.CONSISTENT_HASHING in LoadBalancingAlgorithm:
                    self._add_to_hash_ring(server_id)

    def remove_server(self, server_id):
        with self.lock:
            if server_id in self.servers:
                self.servers.remove(server_id)
                if LoadBalancingAlgorithm.CONSISTENT_HASHING in LoadBalancingAlgorithm:
                    self._remove_from_hash_ring(server_id)
                if self.round_robin_index >= len(self.servers):
                    self.round_robin_index = 0

    def get_server(self, client_id, algorithm):
        if not self.servers:
            return None

        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._get_round_robin_server()
        elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASHING:
            return self._get_consistent_hash_server(client_id)
        else:
            raise ValueError("Invalid load balancing algorithm")

    def get_all_servers(self):
        return self.servers.copy()

    def _get_round_robin_server(self):
        with self.lock:
            if not self.servers:
                return None
            server = self.servers[self.round_robin_index]
            self.round_robin_index = (self.round_robin_index + 1) % len(self.servers)
            return server

    def _get_consistent_hash_server(self, client_id):
        if not self.consistent_hash_ring:
            return None

        hash_key = self._hash(client_id)
        sorted_keys = sorted(self.consistent_hash_ring.keys())
        for key in sorted_keys:
            if hash_key <= key:
                return self.consistent_hash_ring[key]
        return self.consistent_hash_ring[sorted_keys[0]]

    def _add_to_hash_ring(self, server_id):
        hash_key = self._hash(server_id)
        self.consistent_hash_ring[hash_key] = server_id

    def _remove_from_hash_ring(self, server_id):
        hash_key = self._hash(server_id)
        if hash_key in self.consistent_hash_ring:
            del self.consistent_hash_ring[hash_key]

    @staticmethod
    def _hash(key):
        return int(hashlib.sha256(key.encode()).hexdigest(), 16)