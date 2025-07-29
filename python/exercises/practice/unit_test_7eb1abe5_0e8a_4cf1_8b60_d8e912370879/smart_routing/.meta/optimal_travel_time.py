import heapq
from math import floor

def optimal_travel_time(n, edges, k, s, d):
    if s == d:
        return 0

    # Build the graph as an adjacency list.
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))

    # dp[node][used] stores the minimum cost to reach 'node' using 'used' STCs.
    dp = [[float('inf')] * (k + 1) for _ in range(n)]
    dp[s][0] = 0
    
    # Priority queue for Dijkstra's algorithm: (current cost, current node, STCs used)
    heap = [(0, s, 0)]
    
    while heap:
        cost, node, used = heapq.heappop(heap)
        
        # If destination reached, return the cost.
        if node == d:
            return cost
        
        if cost > dp[node][used]:
            continue
        
        for v, w in graph[node]:
            # Option 1: Do not place an STC at the current node.
            new_cost = cost + w
            if new_cost < dp[v][used]:
                dp[v][used] = new_cost
                heapq.heappush(heap, (new_cost, v, used))
            
            # Option 2: Place an STC at the current node if available.
            if used < k:
                # When STC is installed, the travel time is reduced to floor(w/2).
                reduced_cost = cost + (w // 2)
                if reduced_cost < dp[v][used + 1]:
                    dp[v][used + 1] = reduced_cost
                    heapq.heappush(heap, (reduced_cost, v, used + 1))
                    
    # If destination cannot be reached, return -1.
    return -1