import heapq
from collections import defaultdict

def solve(n, edges, sources):
    # Create graph as an adjacency list
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    
    # Initialize distances with infinity
    dist = [float('inf')] * n
    # If sources is empty, return all -1
    if not sources:
        return [-1] * n

    # Initialize priority queue and update distances for source nodes
    heap = []
    for src in set(sources):
        if 0 <= src < n:
            dist[src] = 0
            heapq.heappush(heap, (0, src))
    
    # Dijkstra's algorithm for multi-source shortest path
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    
    # Replace infinity distances with -1 to indicate unreachable nodes
    result = [d if d != float('inf') else -1 for d in dist]
    return result

if __name__ == "__main__":
    # Sample run to verify functionality; not part of unit tests.
    n = 4
    edges = [
        (0, 1, 2),
        (0, 2, 5),
        (1, 2, 1),
        (2, 3, 2)
    ]
    sources = [0]
    print(solve(n, edges, sources))