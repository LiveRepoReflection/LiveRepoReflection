import heapq
import threading
from collections import defaultdict

class NetworkRouter:
    def __init__(self, N, graph):
        self.N = N
        self.graph = defaultdict(list)
        self.link_info = {}
        self.load_lock = threading.Lock()
        
        # Initialize graph and link information
        for u, v, latency, capacity in graph:
            self.graph[u].append((v, latency, capacity))
            self.graph[v].append((u, latency, capacity))
            self.link_info[(u, v)] = {'latency': latency, 'capacity': capacity, 'load': 0}
            self.link_info[(v, u)] = {'latency': latency, 'capacity': capacity, 'load': 0}

    def _get_effective_latency(self, u, v):
        with self.load_lock:
            info = self.link_info[(u, v)]
            load_factor = (info['load'] / info['capacity']) ** 2
            return info['latency'] * (1 + load_factor)

    def find_path(self, S, D):
        if S == D:
            return [S]
            
        # Dijkstra's algorithm with priority queue
        heap = []
        heapq.heappush(heap, (0, S, [S]))
        visited = set()
        
        while heap:
            total_latency, current, path = heapq.heappop(heap)
            
            if current == D:
                # Update loads for the chosen path
                with self.load_lock:
                    for i in range(len(path)-1):
                        u, v = path[i], path[i+1]
                        self.link_info[(u, v)]['load'] += 1
                        self.link_info[(v, u)]['load'] += 1
                return path
                
            if current in visited:
                continue
                
            visited.add(current)
            
            for neighbor, latency, capacity in self.graph[current]:
                if neighbor not in visited:
                    effective_latency = self._get_effective_latency(current, neighbor)
                    new_total = total_latency + effective_latency
                    new_path = path + [neighbor]
                    heapq.heappush(heap, (new_total, neighbor, new_path))
        
        return []  # No path found

    def update_loads(self, delta):
        with self.load_lock:
            for key in self.link_info:
                new_load = max(0, self.link_info[key]['load'] + delta)
                self.link_info[key]['load'] = new_load

    def get_link_load(self, u, v):
        with self.load_lock:
            return self.link_info[(u, v)]['load']