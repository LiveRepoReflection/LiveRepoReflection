import heapq
from collections import defaultdict

def find_dominating_set(n, edges):
    if n == 0:
        return []
    
    # Build adjacency list
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    
    # Initialize data structures
    dominated = set()
    dominating_set = []
    node_heap = []
    
    # Calculate initial priorities (degree + coverage potential)
    for node in range(1, n+1):
        degree = len(adj[node])
        heapq.heappush(node_heap, (-degree, node))
    
    while len(dominated) < n:
        if not node_heap:
            # Handle isolated nodes
            for node in range(1, n+1):
                if node not in dominated:
                    dominating_set.append(node)
                    dominated.add(node)
            break
        
        # Get node with highest degree/coverage
        _, current = heapq.heappop(node_heap)
        
        # Skip if already dominated
        if current in dominated:
            continue
        
        # Add to dominating set
        dominating_set.append(current)
        dominated.add(current)
        
        # Mark neighbors as dominated
        for neighbor in adj[current]:
            dominated.add(neighbor)
        
        # Update priorities of remaining nodes
        temp_heap = []
        while node_heap:
            priority, node = heapq.heappop(node_heap)
            if node in dominated:
                continue
            
            # Recalculate priority based on remaining uncovered neighbors
            uncovered_neighbors = [n for n in adj[node] if n not in dominated]
            new_priority = -len(uncovered_neighbors)
            
            if new_priority != 0:  # Only keep nodes that can still cover something
                heapq.heappush(temp_heap, (new_priority, node))
        
        node_heap = temp_heap
    
    return sorted(dominating_set)