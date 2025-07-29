import heapq
from collections import deque

def find_optimal_route(graph, start, destination, max_hops):
    """
    Find the route with the minimum bottleneck cost from start to destination
    within a specified maximum number of hops.
    
    Args:
        graph: Dictionary representing the weighted directed graph.
        start: The starting node ID.
        destination: The destination node ID.
        max_hops: The maximum number of hops allowed in the route.
        
    Returns:
        A list of node IDs representing the optimal route, or None if no route exists.
    """
    if start not in graph:
        return None
    
    # Special case: start and destination are the same
    if start == destination:
        if max_hops >= 0:
            return [start]
        return None
    
    # Validate the graph has positive costs
    for node, edges in graph.items():
        for _, cost in edges.items():
            if cost <= 0:
                raise ValueError("Edge costs must be positive integers")

    # Binary search on the bottleneck cost
    def can_reach_within_bottleneck(bottleneck):
        visited = set()
        # (node, hops so far, path)
        queue = deque([(start, 0, [start])])
        
        while queue:
            node, hops, path = queue.popleft()
            
            if node == destination:
                return path
            
            if hops >= max_hops:
                continue
            
            # Skip if we've already visited this node with fewer or equal hops
            state = (node, hops)
            if state in visited:
                continue
            visited.add(state)
            
            for neighbor, cost in graph.get(node, {}).items():
                if cost <= bottleneck:
                    new_path = path + [neighbor]
                    queue.append((neighbor, hops + 1, new_path))
        
        return None
    
    # Find all possible edge costs in ascending order
    all_costs = []
    for node, edges in graph.items():
        for _, cost in edges.items():
            all_costs.append(cost)
    
    if not all_costs:
        return None
    
    all_costs = sorted(set(all_costs))
    
    # Binary search for the minimum bottleneck cost
    left, right = 0, len(all_costs) - 1
    best_path = None
    
    while left <= right:
        mid = (left + right) // 2
        bottleneck = all_costs[mid]
        
        path = can_reach_within_bottleneck(bottleneck)
        if path:
            best_path = path
            right = mid - 1  # Try to find a lower bottleneck
        else:
            left = mid + 1  # Need a higher bottleneck
    
    return best_path

def find_optimal_route_dijkstra(graph, start, destination, max_hops):
    """
    Alternative implementation using a modified Dijkstra's algorithm.
    This approach prioritizes paths with lower bottleneck costs.
    
    Args:
        graph: Dictionary representing the weighted directed graph.
        start: The starting node ID.
        destination: The destination node ID.
        max_hops: The maximum number of hops allowed in the route.
        
    Returns:
        A list of node IDs representing the optimal route, or None if no route exists.
    """
    if start not in graph:
        return None
    
    # Special case: start and destination are the same
    if start == destination:
        if max_hops >= 0:
            return [start]
        return None
    
    # Min heap: (bottleneck cost, current node, hops used so far, path)
    pq = [(0, start, 0, [start])]
    # Keep track of the best bottleneck for each (node, hops) combination
    best_bottlenecks = {}
    
    while pq:
        bottleneck, node, hops, path = heapq.heappop(pq)
        
        # If we reached destination, this is the optimal path
        if node == destination:
            return path
        
        # If we've exceeded max hops, skip
        if hops >= max_hops:
            continue
        
        # Skip if we've already found a better path to this node with same or fewer hops
        if (node, hops) in best_bottlenecks and best_bottlenecks[(node, hops)] < bottleneck:
            continue
        
        for neighbor, cost in graph.get(node, {}).items():
            new_bottleneck = max(bottleneck, cost)
            new_hops = hops + 1
            
            # Only consider this path if it's better than what we've seen
            if ((neighbor, new_hops) not in best_bottlenecks or 
                new_bottleneck < best_bottlenecks[(neighbor, new_hops)]):
                best_bottlenecks[(neighbor, new_hops)] = new_bottleneck
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_bottleneck, neighbor, new_hops, new_path))
    
    return None