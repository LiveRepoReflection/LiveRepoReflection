def best_path_reliability(n, edges, s, d, b):
    # Build graph filtering edges that meet the bandwidth requirement.
    graph = {i: [] for i in range(n)}
    for u, v, bandwidth, failure_prob in edges:
        if bandwidth >= b:
            reliability = 1 - failure_prob
            graph[u].append((v, reliability))
            graph[v].append((u, reliability))
            
    # Use a modified Dijkstra algorithm (max-heap based) to maximize reliability.
    import heapq
    best = [0.0] * n
    best[s] = 1.0
    heap = [(-1.0, s)]
    
    while heap:
        neg_rel, node = heapq.heappop(heap)
        current_rel = -neg_rel
        if node == d:
            return current_rel
        if current_rel < best[node]:
            continue
        for neighbor, edge_rel in graph[node]:
            new_rel = current_rel * edge_rel
            if new_rel > best[neighbor]:
                best[neighbor] = new_rel
                heapq.heappush(heap, (-new_rel, neighbor))
                
    return 0.0