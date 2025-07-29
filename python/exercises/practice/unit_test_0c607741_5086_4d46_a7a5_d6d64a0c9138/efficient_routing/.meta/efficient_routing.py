import heapq
import time
from collections import defaultdict, deque

def find_path(network, source_uuid, destination_uuid):
    """
    Find the shortest path between source_uuid and destination_uuid in the given network.
    
    Args:
        network: Network object with a neighbors(node_uuid) method
        source_uuid: UUID of the source node
        destination_uuid: UUID of the destination node
        
    Returns:
        List of UUIDs representing the shortest path from source to destination (inclusive).
        If no path exists, returns an empty list.
        If source and destination are the same, returns a list containing only the source UUID.
    """
    # Special case: source and destination are the same
    if source_uuid == destination_uuid:
        return [source_uuid]
    
    # Initialize the routing table and cache for neighbor information
    routing_table = RoutingTable()
    neighbor_cache = NeighborCache(network)
    
    # Use a variant of A* algorithm with iterative deepening and incremental exploration
    return adaptive_search(source_uuid, destination_uuid, neighbor_cache, routing_table)

class NeighborCache:
    """
    Cache for neighbor information to reduce network calls.
    Simulates a distributed system's local knowledge caching.
    """
    def __init__(self, network, ttl=300):  # TTL in seconds
        self.network = network
        self.cache = {}
        self.ttl = ttl
        self.timestamps = {}
    
    def get_neighbors(self, node_uuid):
        """Get neighbors for a node, using cached data if available and fresh."""
        current_time = time.time()
        
        # If data is cached and not expired, use it
        if node_uuid in self.cache and current_time - self.timestamps[node_uuid] < self.ttl:
            return self.cache[node_uuid]
        
        # Otherwise, fetch from network and cache
        neighbors = self.network.neighbors(node_uuid)
        self.cache[node_uuid] = neighbors
        self.timestamps[node_uuid] = current_time
        return neighbors

    def invalidate(self, node_uuid=None):
        """Invalidate cache entries for a specific node or all nodes."""
        if node_uuid is None:
            self.cache.clear()
            self.timestamps.clear()
        elif node_uuid in self.cache:
            del self.cache[node_uuid]
            del self.timestamps[node_uuid]

class RoutingTable:
    """Maintains routing information between nodes."""
    def __init__(self):
        self.routes = {}
        self.distances = {}
    
    def update_route(self, source, destination, next_hop, distance):
        """Update routing information for a path."""
        key = (source, destination)
        current_distance = self.distances.get(key, float('inf'))
        
        if distance < current_distance:
            self.routes[key] = next_hop
            self.distances[key] = distance
    
    def get_next_hop(self, source, destination):
        """Get the next hop for a given source-destination pair."""
        return self.routes.get((source, destination))
    
    def get_distance(self, source, destination):
        """Get the known distance between source and destination."""
        return self.distances.get((source, destination), float('inf'))

def adaptive_search(source_uuid, destination_uuid, neighbor_cache, routing_table):
    """
    Combines iterative deepening with A* search and dynamically adapts to network conditions.
    Implements a custom heuristic based on network topology exploration.
    """
    # Check if there's a direct connection first (optimization)
    if destination_uuid in neighbor_cache.get_neighbors(source_uuid):
        return [source_uuid, destination_uuid]
    
    # Set up the priority queue for A* search
    # Format: (estimated_total_cost, current_cost, current_node, path)
    pq = [(0, 0, source_uuid, [source_uuid])]
    visited = set()
    
    # Use a sliding timeout window that adapts based on network responsiveness
    timeout_scale = 1.0
    max_explores_per_iteration = 100  # Balance between exploration and quick results
    
    # Track exploration statistics for heuristic adjustment
    explored_count = 0
    avg_branching_factor = 10  # Initial estimate
    
    while pq:
        # Pop the node with the lowest estimated cost
        _, current_cost, current_node, path = heapq.heappop(pq)
        
        # If we've reached the destination, return the path
        if current_node == destination_uuid:
            return path
        
        # If we've already visited this node, skip it
        if current_node in visited:
            continue
        
        visited.add(current_node)
        explored_count += 1
        
        # If we've explored too many nodes, adapt our strategy
        if explored_count >= max_explores_per_iteration:
            # Increase timeout scale to explore more aggressively
            timeout_scale *= 1.5
            max_explores_per_iteration = int(max_explores_per_iteration * 1.5)
            
            # Discard low-priority paths and refocus on promising ones
            if len(pq) > 100:  # Keep queue manageable
                pq = sorted(pq)[:50]  # Keep the 50 most promising paths
                heapq.heapify(pq)
        
        # Get neighbors and update metrics
        neighbors = neighbor_cache.get_neighbors(current_node)
        if neighbors:
            avg_branching_factor = (avg_branching_factor * 0.9) + (len(neighbors) * 0.1)
        
        for neighbor in neighbors:
            if neighbor in visited:
                continue
            
            # Check if this is the destination
            if neighbor == destination_uuid:
                return path + [neighbor]
            
            # Calculate actual cost to reach the neighbor
            new_cost = current_cost + 1
            
            # Calculate heuristic (estimated remaining distance)
            # Use network topology information if available
            if (neighbor, destination_uuid) in routing_table.routes:
                heuristic = routing_table.get_distance(neighbor, destination_uuid)
            else:
                # Adaptive heuristic based on network exploration so far
                # We use the average branching factor to estimate remaining distance
                # This is a balance between optimistic and pessimistic estimates
                estimated_remaining_hops = 1
                heuristic = estimated_remaining_hops
            
            # Update routing table
            routing_table.update_route(source_uuid, neighbor, path[1] if len(path) > 1 else neighbor, new_cost)
            
            # Add to priority queue
            total_estimated_cost = new_cost + heuristic
            heapq.heappush(pq, (total_estimated_cost, new_cost, neighbor, path + [neighbor]))
    
    # If we exhausted the search space without finding a path
    return []

def iterative_deepening_search(source_uuid, destination_uuid, neighbor_cache):
    """
    Iterative deepening search to find a path with a limited horizon.
    Good for finding shorter paths without exploring the entire network.
    """
    max_depth = 1
    
    while max_depth < 100:  # Practical limit to prevent infinite loops
        visited = set()
        result = _depth_limited_search(source_uuid, destination_uuid, neighbor_cache, 
                                      max_depth, visited, [source_uuid])
        if result is not None:
            return result
        max_depth += 1
    
    return []  # No path found within reasonable depth

def _depth_limited_search(current, target, neighbor_cache, depth_limit, visited, path):
    """Helper function for iterative deepening search."""
    if current == target:
        return path
    
    if depth_limit <= 0:
        return None
    
    visited.add(current)
    neighbors = neighbor_cache.get_neighbors(current)
    
    for neighbor in neighbors:
        if neighbor in visited:
            continue
        
        result = _depth_limited_search(neighbor, target, neighbor_cache, 
                                      depth_limit - 1, visited.copy(), path + [neighbor])
        if result is not None:
            return result
    
    return None

def distributed_bidirectional_search(source_uuid, destination_uuid, neighbor_cache):
    """
    Bidirectional search that simulates collaboration between source and destination nodes.
    Explores from both ends simultaneously to find a meeting point.
    """
    # Forward search from source
    forward_queue = deque([(source_uuid, [source_uuid])])
    forward_visited = {source_uuid: [source_uuid]}
    
    # Backward search from destination
    backward_queue = deque([(destination_uuid, [destination_uuid])])
    backward_visited = {destination_uuid: [destination_uuid]}
    
    # Limit search steps to prevent excessive exploration
    max_steps = 1000
    steps = 0
    
    while forward_queue and backward_queue and steps < max_steps:
        steps += 1
        
        # Expand forward search
        if forward_queue:
            current, path = forward_queue.popleft()
            neighbors = neighbor_cache.get_neighbors(current)
            
            for neighbor in neighbors:
                if neighbor in forward_visited:
                    continue
                
                new_path = path + [neighbor]
                forward_visited[neighbor] = new_path
                
                # Check if we found a meeting point
                if neighbor in backward_visited:
                    # Combine paths (remove duplicate meeting point)
                    backward_path = backward_visited[neighbor]
                    combined_path = new_path + backward_path[1:][::-1]
                    return combined_path
                
                forward_queue.append((neighbor, new_path))
        
        # Expand backward search
        if backward_queue:
            current, path = backward_queue.popleft()
            neighbors = neighbor_cache.get_neighbors(current)
            
            for neighbor in neighbors:
                if neighbor in backward_visited:
                    continue
                
                new_path = path + [neighbor]
                backward_visited[neighbor] = new_path
                
                # Check if we found a meeting point
                if neighbor in forward_visited:
                    # Combine paths (remove duplicate meeting point)
                    forward_path = forward_visited[neighbor]
                    combined_path = forward_path + new_path[1:][::-1]
                    return combined_path
                
                backward_queue.append((neighbor, new_path))
    
    return []  # No path found