from collections import defaultdict, deque
import heapq

class GalacticTradeNetwork:
    def __init__(self):
        # Dictionary to store star systems: {id: demand}
        self.star_systems = {}
        
        # Dictionary to store trade routes: {source: {destination: (capacity, travel_time)}}
        self.trade_routes = defaultdict(dict)
    
    def add_star_system(self, system_id, demand):
        """Add a new star system to the network."""
        if system_id <= 0:
            raise ValueError("Star system ID must be a positive integer")
        self.star_systems[system_id] = demand
    
    def remove_star_system(self, system_id):
        """Remove a star system and all associated trade routes from the network."""
        if system_id in self.star_systems:
            del self.star_systems[system_id]
            
            # Remove all trade routes connected to this system
            self.trade_routes.pop(system_id, None)
            for source in self.trade_routes:
                self.trade_routes[source].pop(system_id, None)
    
    def add_trade_route(self, source, destination, capacity, travel_time):
        """Add a new trade route between two star systems."""
        if source not in self.star_systems or destination not in self.star_systems:
            raise ValueError("Source and destination must be existing star systems")
        if capacity < 0:
            raise ValueError("Capacity must be a non-negative integer")
        if travel_time < 0:
            raise ValueError("Travel time must be a non-negative integer")
        
        self.trade_routes[source][destination] = (capacity, travel_time)
    
    def remove_trade_route(self, source, destination):
        """Remove a trade route from the network."""
        if source in self.trade_routes and destination in self.trade_routes[source]:
            del self.trade_routes[source][destination]
    
    def update_trade_route_capacity(self, source, destination, new_capacity):
        """Update the capacity of an existing trade route."""
        if new_capacity < 0:
            raise ValueError("Capacity must be a non-negative integer")
        if source in self.trade_routes and destination in self.trade_routes[source]:
            _, travel_time = self.trade_routes[source][destination]
            self.trade_routes[source][destination] = (new_capacity, travel_time)
    
    def update_trade_route_travel_time(self, source, destination, new_travel_time):
        """Update the travel time of an existing trade route."""
        if new_travel_time < 0:
            raise ValueError("Travel time must be a non-negative integer")
        if source in self.trade_routes and destination in self.trade_routes[source]:
            capacity, _ = self.trade_routes[source][destination]
            self.trade_routes[source][destination] = (capacity, new_travel_time)
    
    def update_demand(self, system_id, new_demand):
        """Update the demand value of a star system."""
        if system_id in self.star_systems:
            self.star_systems[system_id] = new_demand
    
    def get_demand(self, system_id):
        """Get the current demand value of a star system."""
        return self.star_systems.get(system_id, 0)
    
    def _find_all_paths(self, source, destination, max_time):
        """Find all paths from source to destination within max_time."""
        if source == destination:
            return []
        
        # Use Dijkstra's algorithm to find all paths within time limit
        paths = []
        # Priority queue: (time, node, path, bottleneck)
        pq = [(0, source, [source], float('inf'))]
        
        while pq:
            time, node, path, bottleneck = heapq.heappop(pq)
            
            if node == destination:
                paths.append((path, bottleneck))
                continue
            
            for next_node, (capacity, travel_time) in self.trade_routes[node].items():
                if next_node not in path and time + travel_time <= max_time and capacity > 0:
                    new_path = path + [next_node]
                    new_bottleneck = min(bottleneck, capacity)
                    heapq.heappush(pq, (time + travel_time, next_node, new_path, new_bottleneck))
        
        return paths
    
    def max_flow(self, source, destination, max_time):
        """Calculate the maximum flow from source to destination within max_time."""
        if max_time < 0:
            raise ValueError("Maximum time must be a non-negative integer")
        
        if source not in self.star_systems or destination not in self.star_systems:
            return 0
        
        if source == destination:
            return 0
        
        # Build a residual graph to apply Ford-Fulkerson algorithm
        # Combined with time constraints
        residual_graph = self._build_residual_graph()
        
        max_flow_value = 0
        
        # Keep finding augmenting paths until no more are found
        while True:
            # Use BFS to find a valid augmenting path within time limit
            path = self._find_augmenting_path(residual_graph, source, destination, max_time)
            if not path:
                break
            
            # Find the bottleneck capacity (minimum residual capacity along the path)
            bottleneck = self._calculate_bottleneck(residual_graph, path)
            
            # Update the residual graph
            self._update_residual_graph(residual_graph, path, bottleneck)
            
            max_flow_value += bottleneck
        
        return max_flow_value
    
    def _build_residual_graph(self):
        """Build a residual graph for the Ford-Fulkerson algorithm."""
        residual_graph = defaultdict(dict)
        
        for source in self.trade_routes:
            for destination, (capacity, travel_time) in self.trade_routes[source].items():
                residual_graph[source][destination] = (capacity, travel_time, 0)  # (capacity, travel_time, flow)
                # Initialize reverse edge with zero capacity
                if destination not in residual_graph or source not in residual_graph[destination]:
                    residual_graph[destination][source] = (0, travel_time, 0)
        
        return residual_graph
    
    def _find_augmenting_path(self, residual_graph, source, destination, max_time):
        """
        Find an augmenting path in the residual graph within max_time.
        Returns the path as a list of nodes, or None if no path exists.
        """
        # Use a modified Dijkstra's algorithm to find a path
        distances = {node: float('inf') for node in self.star_systems}
        distances[source] = 0
        
        # Priority queue: (distance, node)
        pq = [(0, source)]
        # Keep track of predecessors to reconstruct the path
        predecessors = {node: None for node in self.star_systems}
        
        while pq:
            time, node = heapq.heappop(pq)
            
            if time > distances[node]:
                continue
            
            if node == destination:
                break
            
            for next_node, (capacity, travel_time, flow) in residual_graph[node].items():
                residual_capacity = capacity - flow
                if residual_capacity > 0 and time + travel_time <= max_time:
                    new_time = time + travel_time
                    if new_time < distances[next_node]:
                        distances[next_node] = new_time
                        predecessors[next_node] = node
                        heapq.heappush(pq, (new_time, next_node))
        
        # If no path to destination was found
        if distances[destination] == float('inf'):
            return None
        
        # Reconstruct the path
        path = [destination]
        while path[-1] != source:
            path.append(predecessors[path[-1]])
        
        path.reverse()
        return path
    
    def _calculate_bottleneck(self, residual_graph, path):
        """Calculate the bottleneck capacity of an augmenting path."""
        bottleneck = float('inf')
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            capacity, _, flow = residual_graph[u][v]
            residual_capacity = capacity - flow
            bottleneck = min(bottleneck, residual_capacity)
        
        return bottleneck
    
    def _update_residual_graph(self, residual_graph, path, bottleneck):
        """Update the residual graph after augmenting along a path."""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            
            # Update forward edge
            capacity, travel_time, flow = residual_graph[u][v]
            residual_graph[u][v] = (capacity, travel_time, flow + bottleneck)
            
            # Update reverse edge
            capacity, travel_time, flow = residual_graph[v][u]
            residual_graph[v][u] = (capacity, travel_time, flow - bottleneck)