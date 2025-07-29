import math
import heapq
from collections import defaultdict
import threading
import time


class Node:
    def __init__(self, node_id, latitude, longitude, capacity=0, latency=float('inf')):
        self.node_id = node_id
        self.latitude = latitude
        self.longitude = longitude
        self.capacity = capacity
        self.latency = latency
        self.is_healthy = True
        self.current_load = 0
        self.lock = threading.Lock()

    def __repr__(self):
        return f"Node(id={self.node_id}, capacity={self.capacity}, latency={self.latency}, healthy={self.is_healthy})"

    def set_unhealthy(self):
        self.is_healthy = False

    def set_healthy(self):
        self.is_healthy = True


class Request:
    def __init__(self, request_id, latitude, longitude, priority="medium"):
        self.request_id = request_id
        self.latitude = latitude
        self.longitude = longitude
        self.priority = priority

    def __repr__(self):
        return f"Request(id={self.request_id}, priority={self.priority})"


class LoadBalancer:
    def __init__(self, nodes):
        self.nodes = {node.node_id: node for node in nodes}
        self.priority_weights = {
            "high": 1.0,
            "medium": 0.6,
            "low": 0.3
        }
        self.lock = threading.Lock()
        self.request_history = defaultdict(list)  # Node ID -> list of request timestamps
        self.history_window = 60  # 60 seconds window for request history

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate geographical distance using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def _clean_request_history(self):
        """Remove old requests from history"""
        current_time = time.time()
        with self.lock:
            for node_id in self.request_history:
                self.request_history[node_id] = [
                    t for t in self.request_history[node_id]
                    if current_time - t <= self.history_window
                ]

    def _get_current_load(self, node_id):
        """Calculate current load (requests per second) for a node"""
        self._clean_request_history()
        with self.lock:
            current_time = time.time()
            recent_requests = [
                t for t in self.request_history[node_id]
                if current_time - t <= 1  # Only consider last second
            ]
            return len(recent_requests)

    def update_node_capacity(self, node_id, capacity):
        """Update the capacity of a specific node"""
        if node_id in self.nodes:
            with self.nodes[node_id].lock:
                self.nodes[node_id].capacity = capacity

    def update_node_latency(self, node_id, latency):
        """Update the latency of a specific node"""
        if node_id in self.nodes:
            with self.nodes[node_id].lock:
                self.nodes[node_id].latency = latency

    def _calculate_node_score(self, node, request):
        """Calculate a score for a node based on multiple factors"""
        if not node.is_healthy:
            return float('-inf')

        current_load = self._get_current_load(node.node_id)
        if current_load >= node.capacity:
            return float('-inf')

        # Calculate distance factor (0 to 1, where 0 is furthest and 1 is closest)
        distance = self._calculate_distance(
            request.latitude, request.longitude,
            node.latitude, node.longitude
        )
        max_distance = 20000  # Maximum possible distance in km
        distance_factor = 1 - (distance / max_distance)

        # Calculate load factor (0 to 1, where 1 is empty and 0 is full)
        load_factor = 1 - (current_load / node.capacity)

        # Calculate latency factor (0 to 1, where 1 is fastest and 0 is slowest)
        max_latency = 1000  # Maximum acceptable latency in ms
        latency_factor = 1 - (node.latency / max_latency)

        # Weight factors based on request priority
        priority_weight = self.priority_weights[request.priority]
        
        # Combined score (higher is better)
        score = (
            distance_factor * 0.3 +
            load_factor * 0.3 +
            latency_factor * 0.4
        ) * priority_weight

        return score

    def handle_request(self, request):
        """Route a request to the most suitable node"""
        # Get available nodes and their scores
        node_scores = []
        for node in self.nodes.values():
            score = self._calculate_node_score(node, request)
            if score > float('-inf'):
                heapq.heappush(node_scores, (-score, node.node_id))  # Negative for max-heap

        if not node_scores:
            raise Exception("No suitable nodes available")

        # Select the node with the highest score
        selected_node_id = heapq.heappop(node_scores)[1]

        # Update request history
        with self.lock:
            self.request_history[selected_node_id].append(time.time())

        return selected_node_id

    def get_node_stats(self):
        """Get current statistics for all nodes"""
        stats = {}
        for node_id, node in self.nodes.items():
            with node.lock:
                stats[node_id] = {
                    'capacity': node.capacity,
                    'current_load': self._get_current_load(node_id),
                    'latency': node.latency,
                    'is_healthy': node.is_healthy
                }
        return stats