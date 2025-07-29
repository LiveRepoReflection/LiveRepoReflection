import heapq

def shortest_distances(N, edges, alpha, sources, queries):
    """
    Calculates shortest distances from source nodes to target nodes, considering dynamic edge weights.

    Args:
        N: The number of nodes in the network.
        edges: A list of tuples, where each tuple (u, v, base_cost) represents an undirected edge.
        alpha: The system-wide sensitivity factor.
        sources: A list of source nodes.
        queries: A list of tuples, where each tuple (node, load_updates) represents a query.

    Returns:
        A list of the calculated shortest distances, corresponding to the order of the input queries.
        If the target node is unreachable from all source nodes, returns -1 for that query.
    """
    # Initialize the graph as an adjacency list
    graph = [[] for _ in range(N)]
    for u, v, base_cost in edges:
        graph[u].append((v, base_cost))
        graph[v].append((u, base_cost))
        
    # Initialize the network load for each node as zero
    loads = [0] * N
    results = []
    
    # Process each query sequentially
    for target, load_updates in queries:
        # Update the current loads with the provided increments (cumulatively)
        for node, increment in load_updates.items():
            loads[node] += increment

        # Multi-source Dijkstra: initialize distances
        dist = [float('inf')] * N
        heap = []
        for s in sources:
            if dist[s] > 0:
                dist[s] = 0
                heapq.heappush(heap, (0, s))
        
        # Standard Dijkstra's algorithm using a min-heap / priority queue.
        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist != dist[u]:
                continue
            # Early exit if we reached the target node
            if u == target:
                break
            for v, base_cost in graph[u]:
                # Compute dynamic weight for edge (u, v)
                weight = base_cost + alpha * (loads[u] + loads[v])
                new_dist = current_dist + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    heapq.heappush(heap, (new_dist, v))
        
        # Append the result for the query: -1 if unreachable
        results.append(dist[target] if dist[target] != float('inf') else -1)
        
    return results