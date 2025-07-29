import heapq
import math

def min_total_weighted_response_time(N, roads, damaged_roads, H, emergency_requests):
    # Build graph as an adjacency list with dictionary for quick updates.
    graph = {i: {} for i in range(N)}
    for u, v, w in roads:
        graph[u][v] = w
        graph[v][u] = w

    # Apply damaged roads: update if road exists, add otherwise.
    for u, v, new_w in damaged_roads:
        graph[u][v] = new_w
        graph[v][u] = new_w

    # Multi-source Dijkstra: initialize distances from every hospital.
    dist = [math.inf] * N
    heap = []
    for h in H:
        dist[h] = 0
        heapq.heappush(heap, (0, h))
    
    # Standard Dijkstra while processing multi-source starting points.
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node].items():
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    # Calculate total weighted response time.
    total_cost = 0
    for location, severity in emergency_requests:
        total_cost += dist[location] * severity
    return total_cost