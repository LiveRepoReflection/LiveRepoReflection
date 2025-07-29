import heapq
from collections import defaultdict, deque

class SocialNetwork:
    def __init__(self):
        self.users = set()
        self.connections = defaultdict(dict)  # {user_id: {neighbor: latency}}
        self.neighbors_sorted = defaultdict(list)  # Cache for sorted neighbors

    def add_user(self, user_id):
        if user_id not in self.users:
            self.users.add(user_id)
            self.connections[user_id] = {}
            self.neighbors_sorted[user_id] = []

    def remove_user(self, user_id):
        if user_id in self.users:
            # Remove all connections to this user
            for neighbor in list(self.connections[user_id].keys()):
                self.disconnect(user_id, neighbor)
            self.users.remove(user_id)
            del self.connections[user_id]
            del self.neighbors_sorted[user_id]

    def connect(self, user_id1, user_id2, latency):
        if user_id1 in self.users and user_id2 in self.users:
            self.connections[user_id1][user_id2] = latency
            self.connections[user_id2][user_id1] = latency
            # Update sorted neighbors cache
            self._update_sorted_neighbors(user_id1)
            self._update_sorted_neighbors(user_id2)

    def disconnect(self, user_id1, user_id2):
        if user_id1 in self.users and user_id2 in self.users:
            self.connections[user_id1].pop(user_id2, None)
            self.connections[user_id2].pop(user_id1, None)
            # Update sorted neighbors cache
            self._update_sorted_neighbors(user_id1)
            self._update_sorted_neighbors(user_id2)

    def get_shortest_path(self, user_id1, user_id2):
        if user_id1 not in self.users or user_id2 not in self.users:
            return -1
        
        if user_id1 == user_id2:
            return 0
            
        # Dijkstra's algorithm
        heap = []
        heapq.heappush(heap, (0, user_id1))
        visited = set()
        distances = {user_id: float('inf') for user_id in self.users}
        distances[user_id1] = 0
        
        while heap:
            current_dist, current_user = heapq.heappop(heap)
            
            if current_user in visited:
                continue
                
            if current_user == user_id2:
                return current_dist
                
            visited.add(current_user)
            
            for neighbor, latency in self.connections[current_user].items():
                distance = current_dist + latency
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(heap, (distance, neighbor))
        
        return -1

    def get_kth_neighbor(self, user_id, k):
        if user_id not in self.users:
            return -1
        if k <= 0:
            raise ValueError("k must be positive")
            
        neighbors = self.neighbors_sorted[user_id]
        return neighbors[k-1] if k <= len(neighbors) else -1

    def _update_sorted_neighbors(self, user_id):
        if user_id in self.users:
            self.neighbors_sorted[user_id] = sorted(self.connections[user_id].keys())

    def get_all_users(self):
        return list(self.users)