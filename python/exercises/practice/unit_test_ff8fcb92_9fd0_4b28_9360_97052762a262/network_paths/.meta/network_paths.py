import heapq
from collections import defaultdict

def find_k_edge_disjoint_paths(N, edges, source, destination, k):
    if source == destination:
        return [([source], 0, float('inf'))] if k == 1 else []
    
    # Build adjacency list with capacity and latency
    graph = defaultdict(list)
    for u, v, capacity, latency in edges:
        graph[u].append((v, capacity, latency))
    
    paths = []
    used_edges = set()
    
    for _ in range(k):
        # Dijkstra's algorithm modified to find path with maximum bottleneck capacity
        # and among those, minimum latency
        heap = []
        heapq.heappush(heap, (-float('inf'), 0, source, [source]))
        
        visited = {}
        best_path = None
        best_bottleneck = 0
        best_latency = float('inf')
        
        while heap:
            neg_bottleneck, latency, node, path = heapq.heappop(heap)
            current_bottleneck = -neg_bottleneck
            
            if node == destination:
                if current_bottleneck > best_bottleneck or \
                   (current_bottleneck == best_bottleneck and latency < best_latency):
                    best_path = path
                    best_bottleneck = current_bottleneck
                    best_latency = latency
                continue
            
            if node in visited:
                if visited[node][0] > current_bottleneck or \
                   (visited[node][0] == current_bottleneck and visited[node][1] <= latency):
                    continue
            
            visited[node] = (current_bottleneck, latency)
            
            for neighbor, capacity, edge_latency in graph[node]:
                edge = (node, neighbor)
                if edge in used_edges:
                    continue
                
                new_bottleneck = min(current_bottleneck, capacity)
                new_latency = latency + edge_latency
                new_path = path + [neighbor]
                
                heapq.heappush(heap, (-new_bottleneck, new_latency, neighbor, new_path))
        
        if not best_path:
            break
        
        # Add the found path to our solution
        path_edges = list(zip(best_path[:-1], best_path[1:]))
        used_edges.update(path_edges)
        paths.append((best_path, best_latency, best_bottleneck))
    
    return paths if len(paths) == k else []