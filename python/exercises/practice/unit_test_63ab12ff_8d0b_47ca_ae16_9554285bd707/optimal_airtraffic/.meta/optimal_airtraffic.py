import heapq
import threading
from collections import defaultdict

class OptimalAirTraffic:
    def __init__(self, airports, routes):
        self.graph = defaultdict(dict)
        self.lock = threading.Lock()
        self.restrictions = defaultdict(list)
        
        for airport in airports:
            self.graph[airport] = {}
            
        for src, dest, cost in routes:
            self.graph[src][dest] = cost
            
    def get_route_cost(self, src, dest):
        with self.lock:
            return self.graph[src].get(dest)
            
    def apply_weather_update(self, update):
        src, dest, new_cost = update
        with self.lock:
            if dest in self.graph[src]:
                self.graph[src][dest] = new_cost
                
    def apply_restriction(self, restriction):
        src, dest, start, end = restriction
        with self.lock:
            self.restrictions[(src, dest)].append((start, end))
            if dest in self.graph[src]:
                del self.graph[src][dest]
                
    def lift_restriction(self, restriction):
        src, dest, start, end = restriction
        with self.lock:
            self.restrictions[(src, dest)].remove((start, end))
            if not self.restrictions[(src, dest)] and dest in self.graph[src]:
                self.graph[src][dest] = self.get_original_cost(src, dest)
                
    def is_restricted(self, src, dest, current_time):
        with self.lock:
            for start, end in self.restrictions.get((src, dest), []):
                if start <= current_time <= end:
                    return True
        return False
        
    def find_optimal_path(self, origin, destination):
        with self.lock:
            if origin not in self.graph or destination not in self.graph:
                return "No path found"
                
        heap = [(0, origin, [])]
        visited = set()
        
        while heap:
            current_cost, current_node, path = heapq.heappop(heap)
            
            if current_node == destination:
                return path + [current_node]
                
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            with self.lock:
                neighbors = list(self.graph[current_node].items())
                
            for neighbor, cost in neighbors:
                if neighbor not in visited:
                    heapq.heappush(heap, (current_cost + cost, neighbor, path + [current_node]))
                    
        return "No path found"
        
    def calculate_path_cost(self, path):
        if path == "No path found":
            return float('inf')
            
        total_cost = 0
        for i in range(len(path)-1):
            with self.lock:
                cost = self.graph[path[i]].get(path[i+1])
                if cost is None:
                    return float('inf')
                total_cost += cost
        return total_cost