import heapq
from collections import defaultdict

def optimize_routing(n, links, queries):
    """
    Optimizes packet routing based on network conditions and QoS requirements.
    
    Args:
        n: Number of servers in the data center.
        links: List of tuples (u, v, latency) representing network links.
        queries: List of tuples (source, destination, deadline, priority) representing routing requests.
    
    Returns:
        List of routing decisions ("ROUTE", "DELAY", or "DROP") for each query.
    """
    # Build adjacency list representation of the network
    graph = defaultdict(list)
    for u, v, latency in links:
        graph[u].append((v, latency))
        graph[v].append((u, latency))  # Bidirectional links
    
    results = []
    
    # Process each query
    for source, destination, deadline, priority in queries:
        # Same source and destination is a special case
        if source == destination:
            results.append("ROUTE")
            continue
        
        # Try to find the shortest path
        shortest_latency, has_path = find_shortest_path(graph, source, destination)
        
        if not has_path:
            results.append("DROP")
        elif shortest_latency <= deadline:
            results.append("ROUTE")
        else:
            # No route meeting the deadline, but a path exists
            results.append("DELAY")
    
    return results

def find_shortest_path(graph, source, destination):
    """
    Finds the shortest path from source to destination using Dijkstra's algorithm.
    Can handle negative latencies but not negative cycles.
    
    Args:
        graph: Adjacency list representation of the network.
        source: Source server.
        destination: Destination server.
    
    Returns:
        Tuple (shortest_latency, has_path) where:
        - shortest_latency: The total latency of the shortest path.
        - has_path: Boolean indicating whether a path exists.
    """
    # Check for negative edges to determine algorithm
    has_negative_latency = any(latency < 0 for u in graph for v, latency in graph[u])
    
    if has_negative_latency:
        # Use Bellman-Ford algorithm for graphs with negative latencies
        return bellman_ford_shortest_path(graph, source, destination)
    else:
        # Use Dijkstra's algorithm for graphs with non-negative latencies (more efficient)
        return dijkstra_shortest_path(graph, source, destination)

def dijkstra_shortest_path(graph, source, destination):
    """
    Implements Dijkstra's algorithm for shortest path finding.
    Efficient for graphs with non-negative edge weights.
    """
    # Priority queue for Dijkstra's algorithm
    pq = [(0, source)]
    
    # Dictionary to store the shortest distance to each node
    distances = {source: 0}
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # If we've reached the destination, return the distance
        if current_node == destination:
            return current_distance, True
        
        # If we've already found a shorter path to the current node, skip it
        if current_distance > distances.get(current_node, float('inf')):
            continue
        
        # Explore neighbors
        for neighbor, latency in graph[current_node]:
            distance = current_distance + latency
            
            # If we found a shorter path to the neighbor
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    # Check if destination is reachable
    return float('inf'), destination in distances

def bellman_ford_shortest_path(graph, source, destination):
    """
    Implements the Bellman-Ford algorithm for shortest path finding.
    Can handle negative edge weights but not negative cycles.
    """
    # Convert adjacency list to edge list for Bellman-Ford
    edges = []
    for u in graph:
        for v, latency in graph[u]:
            edges.append((u, v, latency))
    
    # Initialize distances
    distances = {node: float('inf') for node in range(1, max(graph.keys()) + 2)}
    distances[source] = 0
    
    # Relax edges |V| - 1 times
    for _ in range(len(graph) - 1):
        for u, v, latency in edges:
            if distances[u] != float('inf') and distances[u] + latency < distances[v]:
                distances[v] = distances[u] + latency
    
    # Check for negative cycles (not required by the problem, but added for robustness)
    # In a real implementation, we might handle negative cycles differently
    for u, v, latency in edges:
        if distances[u] != float('inf') and distances[u] + latency < distances[v]:
            # Negative cycle detected, affecting paths
            # For simplicity, we'll return a very negative value to indicate a route can be found
            if is_reachable(graph, source, destination) and is_reachable(graph, u, destination):
                return float('-inf'), True
    
    # Check if destination is reachable
    has_path = distances[destination] != float('inf')
    return distances[destination], has_path

def is_reachable(graph, source, destination):
    """
    Check if destination is reachable from source using BFS.
    """
    if source == destination:
        return True
    
    visited = set()
    queue = [source]
    visited.add(source)
    
    while queue:
        current = queue.pop(0)
        
        for neighbor, _ in graph[current]:
            if neighbor == destination:
                return True
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False