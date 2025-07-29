import heapq
import math

def optimal_travel_time(N, M, edges, S, D, T, G):
    # Build the graph as an adjacency list.
    graph = [[] for _ in range(N)]
    for u, v, w in edges:
        graph[u].append((v, w))
    
    # Since we can choose the offsets arbitrarily,
    # for any simple path from S to D we can set each node's offset to match
    # the arrival time modulo T so that no waiting occurs.
    # Thus, the minimal travel time is simply the sum of weights along the shortest path.
    # We use Dijkstra's algorithm to compute the shortest path.
    
    dist = [math.inf] * N
    dist[S] = 0
    heap = [(0, S)]
    
    while heap:
        cur_time, u = heapq.heappop(heap)
        if cur_time > dist[u]:
            continue
        for v, travel in graph[u]:
            new_time = cur_time + travel
            if new_time < dist[v]:
                dist[v] = new_time
                heapq.heappush(heap, (new_time, v))
    
    return dist[D] if dist[D] != math.inf else -1