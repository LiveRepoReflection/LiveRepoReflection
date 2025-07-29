def min_trips(N: int, S: int, D: int, edges: list, delivery_units: int, max_latency: int) -> int:
    # Build graph representation where graph[u] is a list of (v, capacity, latency) edges from u
    graph = [[] for _ in range(N)]
    for u, v, capacity, latency in edges:
        graph[u].append((v, capacity, latency))
    
    # dp[t] will store a dictionary mapping node -> best bottleneck capacity achieved with exactly t latency.
    dp = [dict() for _ in range(max_latency + 1)]
    dp[0][S] = float('inf')
    
    # Traverse all possible time values up to max_latency
    for t in range(max_latency + 1):
        if not dp[t]:
            continue
        # For each state at time t
        for u, cap in list(dp[t].items()):
            for v, edge_cap, edge_latency in graph[u]:
                new_time = t + edge_latency
                if new_time > max_latency:
                    continue
                # The new capacity is the minimum of the current state's capacity and the edge's capacity.
                new_cap = edge_cap if cap == float('inf') else min(cap, edge_cap)
                if dp[new_time].get(v, 0) < new_cap:
                    dp[new_time][v] = new_cap

    # Find the maximum bottleneck capacity among states reaching D with latency <= max_latency.
    max_bottleneck = 0
    for t in range(max_latency + 1):
        if D in dp[t]:
            if dp[t][D] > max_bottleneck:
                max_bottleneck = dp[t][D]
    
    if max_bottleneck == 0:
        return -1

    # Calculate number of trips needed (ceiling division)
    trips = (delivery_units + int(max_bottleneck) - 1) // int(max_bottleneck)
    return trips