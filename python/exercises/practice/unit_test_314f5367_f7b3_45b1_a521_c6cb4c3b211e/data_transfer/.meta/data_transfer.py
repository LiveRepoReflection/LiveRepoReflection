import heapq
import math
from collections import defaultdict

def optimal_transfer(N, routes, S, D, alpha):
    """
    Find the optimal data transfer path that minimizes Total Cost + (alpha * Total Transfer Time).
    
    Args:
        N: Number of nodes in the network
        routes: List of tuples (u, v, c, t) representing transfer routes
        S: Source node
        D: Destination node
        alpha: Weighting factor
        
    Returns:
        The minimum value of Total Cost + (alpha * Total Transfer Time) or -1 if no path exists.
    """
    # Early return if source and destination are the same
    if S == D:
        return 0.00
    
    # Build an adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v, c, t in routes:
        graph[u].append((v, c, t))
    
    # Initialize the priority queue for Dijkstra's algorithm
    # Format: (composite_cost, time, cost, node)
    pq = [(0, 0, 0, S)]
    
    # Initialize distance tracking dictionaries
    # We need to track both cost and time separately
    best_composite = {S: 0}  # Best composite value (cost + alpha*time) for each node
    best_time = {S: 0}       # Best time for nodes with equal composite value (for tie-breaking)
    
    while pq:
        composite, time, cost, node = heapq.heappop(pq)
        
        # If we've reached the destination, return the result
        if node == D:
            return round(composite, 2)
        
        # Skip if we've found a better path to this node already
        if composite > best_composite.get(node, float('inf')):
            continue
        
        # Check all neighbors
        for neighbor, edge_cost, edge_time in graph[node]:
            new_cost = cost + edge_cost
            new_time = time + edge_time
            new_composite = new_cost + (alpha * new_time)
            
            # Update if we found a better path or equal composite but better time
            if (neighbor not in best_composite or 
                new_composite < best_composite[neighbor] or
                (math.isclose(new_composite, best_composite[neighbor]) and 
                 new_time < best_time[neighbor])):
                
                best_composite[neighbor] = new_composite
                best_time[neighbor] = new_time
                heapq.heappush(pq, (new_composite, new_time, new_cost, neighbor))
    
    # If we can't reach the destination
    return -1