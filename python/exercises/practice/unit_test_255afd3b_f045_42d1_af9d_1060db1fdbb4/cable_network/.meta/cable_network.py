import heapq
from collections import defaultdict

def find_min_latency_path(nodes, edges, source, destination, min_bandwidth):
    """
    Find the path from source to destination that satisfies the minimum bandwidth requirement
    while minimizing the total latency.
    
    Args:
        nodes: Number of nodes in the network
        edges: List of tuples (u, v, bandwidth, latency) representing the cables
        source: Source dimension ID
        destination: Destination dimension ID
        min_bandwidth: Minimum required bandwidth
        
    Returns:
        The minimum latency path from source to destination with bandwidth >= min_bandwidth,
        or -1 if no such path exists
    """
    # Handle the case where source and destination are the same
    if source == destination:
        return 0
    
    # Build an adjacency list representation of the graph
    # Each edge contains (neighbor, bandwidth, latency)
    graph = defaultdict(list)
    for u, v, bandwidth, latency in edges:
        if bandwidth >= min_bandwidth:  # Only consider edges with sufficient bandwidth
            graph[u].append((v, bandwidth, latency))
            graph[v].append((u, bandwidth, latency))  # Undirected graph
    
    # Dijkstra's algorithm to find shortest path based on latency
    # Priority queue entries: (total_latency, node)
    priority_queue = [(0, source)]
    # Keep track of visited nodes and their minimum latency
    distances = {source: 0}
    
    while priority_queue:
        current_latency, current_node = heapq.heappop(priority_queue)
        
        # If we've reached the destination, return the total latency
        if current_node == destination:
            return current_latency
        
        # If we've already found a better path to this node, skip
        if current_latency > distances.get(current_node, float('inf')):
            continue
        
        # Explore neighbors
        for neighbor, bandwidth, latency in graph[current_node]:
            # Calculate new latency for this path
            new_latency = current_latency + latency
            
            # If this is a better path, update the distance and add to queue
            if new_latency < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_latency
                heapq.heappush(priority_queue, (new_latency, neighbor))
    
    # If we've exhausted all paths and haven't reached the destination
    return -1