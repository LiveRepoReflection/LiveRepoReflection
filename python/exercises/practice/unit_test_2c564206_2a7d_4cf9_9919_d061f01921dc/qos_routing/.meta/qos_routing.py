import heapq
from collections import defaultdict, deque

def find_best_paths(n, edges, source, destination, min_bandwidth, max_latency, w1, w2, w3, w4, k):
    """
    Find the k best paths from source to destination that satisfy the QoS constraints.
    
    Args:
        n: The number of nodes in the network
        edges: List of tuples (u, v, latency, bandwidth, cost) representing directed edges
        source: The source node
        destination: The destination node
        min_bandwidth: Minimum required bandwidth for a valid path
        max_latency: Maximum allowed latency for a valid path
        w1, w2, w3, w4: Weights for scoring function
        k: Number of best paths to find
        
    Returns:
        List of at most k best paths, each represented as a list of node indices
    """
    # Handle the special case where source and destination are the same
    if source == destination:
        return [[source]]
    
    # Build the adjacency list
    graph = defaultdict(list)
    for u, v, latency, bandwidth, cost in edges:
        # Filter out edges that don't meet bandwidth requirement
        if bandwidth >= min_bandwidth:
            graph[u].append((v, latency, bandwidth, cost))
    
    # Initialize data structures
    best_paths = []
    seen_edges = defaultdict(int)  # Maps edge (u,v) to the number of times it's used in best paths
    
    # Priority queue for Dijkstra's algorithm
    # Format: (score, -bandwidth, path_latency, path_cost, path)
    # We use -bandwidth because we want higher bandwidth to be prioritized
    pq = [(0, -float('inf'), 0, 0, [source])]
    
    # Track visited states to avoid cycles
    # We use (node, min_bandwidth_so_far) as state to avoid duplicate states
    visited = set()
    
    while pq and len(best_paths) < k:
        score, neg_bandwidth, path_latency, path_cost, path = heapq.heappop(pq)
        
        current = path[-1]
        
        # Skip if we've already found a path to the destination
        if current == destination:
            # Calculate path edges for penalty calculations
            path_edges = []
            for i in range(len(path) - 1):
                path_edges.append((path[i], path[i+1]))
            
            # Check if path is valid (meets latency constraint)
            if path_latency <= max_latency:
                # Include path in best_paths
                best_paths.append(path)
                
                # Update seen_edges for future penalty calculations
                for edge in path_edges:
                    seen_edges[edge] += 1
            
            continue
        
        # Skip if this state has been visited
        state = (current, -neg_bandwidth)
        if state in visited:
            continue
        visited.add(state)
        
        # Explore neighbors
        for neighbor, edge_latency, edge_bandwidth, edge_cost in graph[current]:
            # Skip if adding this edge would exceed max latency
            if path_latency + edge_latency > max_latency:
                continue
            
            # Path bandwidth is the minimum bandwidth of all edges
            path_bandwidth = min(-neg_bandwidth, edge_bandwidth) if neg_bandwidth != -float('inf') else edge_bandwidth
            
            # Skip if path bandwidth falls below minimum
            if path_bandwidth < min_bandwidth:
                continue
            
            new_path = path + [neighbor]
            new_path_latency = path_latency + edge_latency
            new_path_cost = path_cost + edge_cost
            
            # Calculate basic score
            new_score = w1 * new_path_latency + w2 * (1 / path_bandwidth) + w3 * new_path_cost
            
            # Calculate penalty for edge overlap with existing best paths
            penalty = 0
            if w4 > 0:
                # Get the edges in the new path
                new_path_edges = []
                for i in range(len(new_path) - 1):
                    new_path_edges.append((new_path[i], new_path[i+1]))
                
                # Calculate total path bandwidth (sum of all edge bandwidths)
                total_path_bandwidth = 0
                avg_edge_cost = 0
                for u, v in new_path_edges:
                    # Find bandwidth and cost for this edge
                    for node, lat, bw, cst in graph[u]:
                        if node == v:
                            total_path_bandwidth += bw
                            avg_edge_cost += cst
                            break
                
                if new_path_edges:  # Avoid division by zero
                    avg_edge_cost /= len(new_path_edges)
                
                # Calculate overlap penalty
                overlap_edges = [edge for edge in new_path_edges if seen_edges[edge] > 0]
                
                if overlap_edges and total_path_bandwidth > 0:
                    # Calculate minimum bandwidth of overlapping edges
                    overlap_bandwidth = float('inf')
                    for u, v in overlap_edges:
                        for node, lat, bw, cst in graph[u]:
                            if node == v and bw < overlap_bandwidth:
                                overlap_bandwidth = bw
                                break
                    
                    # Apply penalty formula
                    penalty = w4 * (overlap_bandwidth / total_path_bandwidth) * avg_edge_cost
            
            # Add penalty to score
            new_score += penalty
            
            # Add to priority queue
            heapq.heappush(pq, (new_score, -path_bandwidth, new_path_latency, new_path_cost, new_path))
    
    return best_paths