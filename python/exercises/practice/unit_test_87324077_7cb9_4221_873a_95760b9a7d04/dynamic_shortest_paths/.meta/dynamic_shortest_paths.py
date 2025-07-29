import heapq
import math

def dynamic_shortest_paths(N, M, edges, sources, Q, updates):
    # Build graph as an adjacency list: graph[u] = list of (v, weight)
    graph = [[] for _ in range(N)]
    # For efficient update, also store a mapping from (u, v) to index in graph[u]
    edge_index = {}
    for i, (u, v, w) in enumerate(edges):
        graph[u].append([v, w])
        edge_index[(u, v)] = len(graph[u]) - 1

    results = []
    for update in updates:
        u, v, new_weight = update
        # Update the weight of the edge (u, v)
        if (u, v) in edge_index:
            idx = edge_index[(u, v)]
            graph[u][idx][1] = new_weight
        # Recompute multi-source shortest paths using Dijkstra's algorithm
        distances = multi_source_dijkstra(N, graph, sources)
        results.append(distances)
    return results

def multi_source_dijkstra(N, graph, sources):
    distances = [math.inf] * N
    heap = []
    # Initialize with multiple sources
    for src in sources:
        if 0 <= src < N:
            distances[src] = 0
            heapq.heappush(heap, (0, src))
    while heap:
        cur_dist, u = heapq.heappop(heap)
        if cur_dist > distances[u]:
            continue
        for v, weight in graph[u]:
            new_dist = cur_dist + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
    return distances