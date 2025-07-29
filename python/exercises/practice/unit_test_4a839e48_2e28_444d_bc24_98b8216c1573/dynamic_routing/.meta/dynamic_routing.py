import heapq
import math

def dijkstra(graph, source, N):
    dist = [math.inf] * N
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        current_dist, u = heapq.heappop(heap)
        if current_dist > dist[u]:
            continue
        for v, weight in graph[u].items():
            new_dist = current_dist + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
    return dist

def solve(N, edges, sources, updates):
    # Build the initial undirected graph as a dictionary of dictionaries.
    graph = {i: {} for i in range(N)}
    for u, v, w in edges:
        graph[u][v] = w
        graph[v][u] = w

    results = []
    # Process each update.
    for update in updates:
        t, u, v, new_w = update
        # Treat negative weights as 0.
        if new_w < 0:
            new_w = 0
        # Update the weight if the edge exists or add the new edge.
        graph[u][v] = new_w
        graph[v][u] = new_w

        # For each source, compute the shortest paths using Dijkstra's algorithm.
        total_cost = 0
        has_infinite = False
        for source in sources:
            distances = dijkstra(graph, source, N)
            # If any node is unreachable, the total cost becomes infinite.
            if any(math.isinf(d) for d in distances):
                has_infinite = True
                break
            total_cost += sum(distances)
        if has_infinite:
            results.append(float('inf'))
        else:
            results.append(total_cost)
    return results