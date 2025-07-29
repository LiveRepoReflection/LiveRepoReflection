import heapq
from collections import defaultdict

def optimal_route(N, edges, capacities, S, D):
    """
    Find the optimal route from source S to destination D that minimizes total latency
    while respecting capacity constraints.
    
    Args:
        N: Number of nodes
        edges: List of tuples (u, v, l, b) representing edges with latency l and bandwidth b
        capacities: List of node capacities
        S: Source node
        D: Destination node
        
    Returns:
        List of nodes representing the optimal route from S to D, or empty list if no valid route exists
    """
    # Build adjacency list for the graph
    graph = defaultdict(list)
    for u, v, latency, bandwidth in edges:
        if bandwidth > 0:  # Only consider edges with positive bandwidth
            graph[u].append((v, latency, bandwidth))
    
    # Use Dijkstra's algorithm to find shortest path
    # Priority queue elements are (total_latency, current_node, path)
    pq = [(0, S, [S])]
    visited = set()
    
    while pq:
        latency, node, path = heapq.heappop(pq)
        
        # If we've reached the destination, return the path
        if node == D:
            # Check if the path satisfies capacity constraints
            if _is_valid_path(path, graph, capacities):
                return path
            continue
        
        # Skip if we've already processed this node
        if (node, tuple(path)) in visited:
            continue
        
        visited.add((node, tuple(path)))
        
        # Process all neighbors
        for neighbor, edge_latency, edge_bandwidth in graph[node]:
            # Skip if neighbor has zero capacity
            if capacities[neighbor] == 0:
                continue
                
            new_latency = latency + edge_latency
            new_path = path + [neighbor]
            
            heapq.heappush(pq, (new_latency, neighbor, new_path))
            
    # If we've exhausted all paths and haven't found a valid one
    return []

def _is_valid_path(path, graph, capacities):
    """
    Check if the given path satisfies the capacity constraints.
    
    Args:
        path: List of nodes representing a path
        graph: Adjacency list representation of the graph
        capacities: List of node capacities
        
    Returns:
        Boolean indicating whether the path is valid
    """
    # Check node capacities (except source and destination)
    for i in range(1, len(path) - 1):
        node = path[i]
        if capacities[node] == 0:
            return False
            
    # Check edge bandwidths
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        
        # Find the edge from u to v
        edge_found = False
        for neighbor, _, bandwidth in graph[u]:
            if neighbor == v:
                if bandwidth == 0:
                    return False
                edge_found = True
                break
                
        if not edge_found:
            return False
            
    return True