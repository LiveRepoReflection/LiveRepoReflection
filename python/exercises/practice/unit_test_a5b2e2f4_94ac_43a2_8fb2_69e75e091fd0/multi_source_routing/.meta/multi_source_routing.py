import heapq
from collections import defaultdict

def optimal_multi_source_routing(N, edges, S, D):
    # Build adjacency list with minimum edge weights
    graph = defaultdict(dict)
    for u, v, w in edges:
        if v in graph[u]:
            if w < graph[u][v]:
                graph[u][v] = w
        else:
            graph[u][v] = w
    
    # Initialize distances with infinity
    distances = [float('inf')] * N
    heap = []
    
    # Set distance to 0 for all source nodes and add to heap
    for source in S:
        distances[source] = 0
        heapq.heappush(heap, (0, source))
    
    # Dijkstra's algorithm
    while heap:
        current_dist, u = heapq.heappop(heap)
        
        # Early termination if we reach destination
        if u == D:
            return current_dist
        
        # Skip if we already found a better path
        if current_dist > distances[u]:
            continue
            
        # Explore neighbors
        for v in graph[u]:
            new_dist = current_dist + graph[u][v]
            if new_dist < distances[v]:
                distances[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
    
    return -1 if distances[D] == float('inf') else distances[D]