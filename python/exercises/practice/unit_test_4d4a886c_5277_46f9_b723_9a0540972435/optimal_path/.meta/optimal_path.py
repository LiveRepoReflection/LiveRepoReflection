import heapq

def find_optimal_path(n, edges, start, end, min_bandwidth):
    # Special case: when source and destination are the same.
    # If there's an outgoing edge from start with sufficient bandwidth, return 0; otherwise, return -1.
    if start == end:
        valid = any(u == start and bandwidth >= min_bandwidth for u, v, cost, bandwidth in edges)
        return 0 if valid else -1

    # Build an adjacency list considering only the edges that have bandwidth >= min_bandwidth.
    graph = [[] for _ in range(n)]
    for u, v, cost, bandwidth in edges:
        if bandwidth >= min_bandwidth:
            graph[u].append((v, cost))
    
    # Use Dijkstra's algorithm to find the minimum cost path.
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]
    
    while heap:
        current_cost, node = heapq.heappop(heap)
        if current_cost > dist[node]:
            continue
        if node == end:
            return current_cost
        for neighbor, edge_cost in graph[node]:
            new_cost = current_cost + edge_cost
            if new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))
    
    return -1