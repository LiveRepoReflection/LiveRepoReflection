import heapq
from collections import defaultdict


def find_optimal_routes(n, edges, start, end, k):
    """
    Find the k best routes from start to end in a network.
    
    Args:
        n: Number of servers in the network.
        edges: List of tuples (u, v, w, c) representing edges.
        start: Starting server node.
        end: Destination server node.
        k: Number of best paths to find.
        
    Returns:
        List of paths sorted by descending utility.
    """
    # Handle special case where start equals end
    if start == end:
        return [[start]]
    
    # Build adjacency list
    graph = defaultdict(list)
    for u, v, bandwidth, cost in edges:
        # Skip invalid edges with zero bandwidth or cost
        if bandwidth == 0 or cost == 0:
            continue
        # Bidirectional edge
        graph[u].append((v, bandwidth, cost))
        graph[v].append((u, bandwidth, cost))
    
    # Use modified Dijkstra's algorithm to find paths with highest utility
    def find_paths():
        # Priority queue ordered by negative utility (for max heap)
        # Each element is (negative_utility, bandwidth, cost, current_node, path)
        paths_found = []
        visited_states = set()  # To avoid revisiting the same state
        
        # Start with the initial node
        pq = [(0, float('inf'), 0, start, [start])]
        
        while pq and len(paths_found) < k:
            neg_utility, bandwidth, cost, node, path = heapq.heappop(pq)
            
            # If we've reached the end node, we've found a path
            if node == end:
                paths_found.append(path)
                continue
            
            # State is (node, tuple of sorted visited nodes) to avoid cycles
            state = (node, tuple(sorted(path)))
            if state in visited_states:
                continue
            
            visited_states.add(state)
            
            # Explore neighbors
            for neighbor, edge_bandwidth, edge_cost in graph[node]:
                if neighbor in path:  # Avoid cycles
                    continue
                
                new_bandwidth = min(bandwidth, edge_bandwidth)
                new_cost = cost + edge_cost
                new_utility = new_bandwidth / new_cost if new_cost > 0 else float('inf')
                new_path = path + [neighbor]
                
                # Push to priority queue with negative utility for max heap
                heapq.heappush(pq, (-new_utility, new_bandwidth, new_cost, neighbor, new_path))
        
        return paths_found
    
    paths = find_paths()
    
    # If we couldn't find any paths, return empty list
    if not paths:
        return []
    
    return paths


def calculate_utility(path, graph):
    """
    Calculate the utility (bandwidth/cost) of a path.
    Helper function for testing and debugging.
    """
    if len(path) < 2:
        return float('inf')  # Single node path
    
    min_bandwidth = float('inf')
    total_cost = 0
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_found = False
        
        for neighbor, bandwidth, cost in graph[u]:
            if neighbor == v:
                min_bandwidth = min(min_bandwidth, bandwidth)
                total_cost += cost
                edge_found = True
                break
        
        if not edge_found:
            return -1  # Invalid path
    
    return min_bandwidth / total_cost if total_cost > 0 else float('inf')