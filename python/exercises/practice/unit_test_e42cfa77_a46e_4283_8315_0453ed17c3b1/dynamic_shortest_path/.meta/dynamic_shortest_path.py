import heapq
from collections import defaultdict

def dynamic_shortest_path(N, edges, sources, updates):
    # Build initial adjacency list
    adj = defaultdict(dict)
    for u, v, w in edges:
        adj[u][v] = w
    
    # Apply updates to the graph
    for u, v, new_w in updates:
        adj[u][v] = new_w
    
    # Initialize distances
    dist = [float('inf')] * N
    heap = []
    
    # Set distance for source nodes to 0 and add to heap
    for source in sources:
        dist[source] = 0
        heapq.heappush(heap, (0, source))
    
    # Dijkstra's algorithm with priority queue
    while heap:
        current_dist, u = heapq.heappop(heap)
        
        # Skip if we already found a better path
        if current_dist > dist[u]:
            continue
            
        # Explore neighbors
        for v, weight in adj[u].items():
            if dist[v] > dist[u] + weight:
                dist[v] = dist[u] + weight
                heapq.heappush(heap, (dist[v], v))
    
    return dist