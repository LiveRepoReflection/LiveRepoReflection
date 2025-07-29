import heapq
from collections import defaultdict

def find_optimal_path(routers, connections, source, destination, k):
    """
    Find the optimal path between source and destination routers in the ICN.
    
    Args:
        routers (dict): A dictionary where keys are router IDs and values are dictionaries
                       with an 'instability' key.
        connections (list): A list of tuples (router_id_1, router_id_2, latency).
        source (int): The ID of the source router.
        destination (int): The ID of the destination router.
        k (int): The instability penalty factor.
    
    Returns:
        tuple: A tuple containing:
            - int: The minimum cost of the path (or -1 if no path exists).
            - list: The path as a list of router IDs (or empty list if no path exists).
    """
    # If source and destination are the same
    if source == destination:
        return k * routers[source]["instability"], [source]
    
    # Build the graph
    graph = defaultdict(list)
    for r1, r2, latency in connections:
        graph[r1].append((r2, latency))
        graph[r2].append((r1, latency))  # Undirected graph
    
    # Priority queue for Dijkstra's algorithm
    # (cost, router_id, path)
    pq = [(routers[source]["instability"] * k, source, [source])]
    
    # Track visited nodes to avoid cycles
    visited = set()
    
    while pq:
        cost, current, path = heapq.heappop(pq)
        
        # If we've reached the destination
        if current == destination:
            return cost, path
        
        # Skip if we've already visited this node
        if current in visited:
            continue
        
        visited.add(current)
        
        # Explore neighbors
        for neighbor, latency in graph[current]:
            if neighbor not in visited:
                # Calculate new cost: 
                # - Add the latency of the connection
                # - Add the instability penalty of the neighbor
                new_cost = cost + latency + (routers[neighbor]["instability"] * k)
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_cost, neighbor, new_path))
    
    # If we've explored all reachable nodes and haven't found the destination
    return -1, []