import heapq
from collections import defaultdict

def island_hopping(n, edges, sources, targets, k):
    if not sources or not targets:
        return -1
    
    # Build adjacency list
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    
    # Initialize priority queue with all sources (cost=0, steps=1, node)
    heap = []
    for source in sources:
        heapq.heappush(heap, (0, 1, source))
    
    # Visited dictionary to track minimum cost for each (node, steps) pair
    visited = {}
    
    while heap:
        current_cost, current_steps, current_node = heapq.heappop(heap)
        
        # Check if we've reached any target
        if current_node in targets:
            return current_cost
        
        # Skip if we've already visited this node with better or equal cost in same or fewer steps
        if (current_node, current_steps) in visited:
            if visited[(current_node, current_steps)] <= current_cost:
                continue
        visited[(current_node, current_steps)] = current_cost
        
        # If we've reached max steps, don't explore further
        if current_steps >= k:
            continue
        
        # Explore neighbors
        for neighbor, weight in graph.get(current_node, []):
            new_cost = current_cost + weight
            new_steps = current_steps + 1
            
            # Only push to heap if we haven't visited this neighbor with better cost in same or fewer steps
            if (neighbor, new_steps) not in visited or new_cost < visited.get((neighbor, new_steps), float('inf')):
                heapq.heappush(heap, (new_cost, new_steps, neighbor))
    
    return -1