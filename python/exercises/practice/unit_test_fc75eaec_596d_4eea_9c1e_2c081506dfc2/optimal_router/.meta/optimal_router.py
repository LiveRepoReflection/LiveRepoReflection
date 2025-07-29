from heapq import heappush, heappop
from collections import defaultdict
import time

class OptimalRouter:
    def __init__(self):
        self.distance_cache = {}
        self.path_cache = {}
        self.last_update_time = {}

    def _clear_affected_cache(self, source, destination):
        """Clear cached results affected by an edge update."""
        affected_keys = set()
        for key in list(self.distance_cache.keys()):
            if source in self.path_cache.get(key, []) or destination in self.path_cache.get(key, []):
                affected_keys.add(key)
        
        for key in affected_keys:
            self.distance_cache.pop(key, None)
            self.path_cache.pop(key, None)

    def _modified_dijkstra(self, graph, start, end, max_travel_time):
        """Modified Dijkstra's algorithm that considers both distance and number of hops."""
        if start == end:
            return [start], 0

        # Priority queue entries are (total_time, hops, current_node, path)
        pq = [(0, 0, start, [start])]
        visited = set()
        
        while pq:
            total_time, hops, current, path = heappop(pq)
            
            if current == end:
                return path, total_time
                
            if current in visited or total_time > max_travel_time:
                continue
                
            visited.add(current)
            
            for next_node, time in graph.get(current, {}).items():
                if next_node not in visited and total_time + time <= max_travel_time:
                    new_path = path + [next_node]
                    # Use composite priority: primary is time, secondary is number of hops
                    heappush(pq, (total_time + time, hops + 1, next_node, new_path))
        
        return [], float('inf')

    def _get_cache_key(self, source, destination, max_travel_time):
        """Generate a unique cache key for a route request."""
        return f"{source}_{destination}_{max_travel_time}"

    def find_optimal_route(self, graph, request):
        """Find the optimal route for a delivery request."""
        source = request['source']
        destination = request['destination']
        max_travel_time = request['max_travel_time']
        
        # Check cache first
        cache_key = self._get_cache_key(source, destination, max_travel_time)
        current_time = time.time()
        
        if (cache_key in self.distance_cache and 
            current_time - self.last_update_time.get(cache_key, 0) < 1.0):  # Cache valid for 1 second
            if self.distance_cache[cache_key] <= max_travel_time:
                return self.path_cache[cache_key]
            return []

        # Find optimal route using modified Dijkstra's algorithm
        path, total_time = self._modified_dijkstra(graph, source, destination, max_travel_time)
        
        # Update cache
        if path:
            self.distance_cache[cache_key] = total_time
            self.path_cache[cache_key] = path
            self.last_update_time[cache_key] = current_time
        
        return path

    def update_edge(self, graph, source, destination, new_travel_time):
        """Update an edge weight in the graph and clear affected cache entries."""
        if source in graph:
            graph[source][destination] = new_travel_time
            self._clear_affected_cache(source, destination)

# Function to be called by the test suite
def find_optimal_route(graph, request):
    router = OptimalRouter()
    return router.find_optimal_route(graph, request)