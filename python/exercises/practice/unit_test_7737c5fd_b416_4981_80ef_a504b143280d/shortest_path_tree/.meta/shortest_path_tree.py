import heapq

def shortest_path_tree(n, edges, sources):
    # Build the graph as an adjacency list.
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))

    INF = float('inf')
    # dist[v] will hold the shortest distance from any of the source nodes to v.
    dist = [INF] * n
    # parent_info[v] holds the tuple (u, w) representing an edge u -> v in the tree.
    parent_info = [None] * n

    # Priority queue item: (distance, edge_weight, node, parent)
    # For source nodes, parent is None and edge_weight is 0.
    pq = []
    for s in sources:
        dist[s] = 0
        heapq.heappush(pq, (0, 0, s, None))

    while pq:
        d, edge_w, u, par = heapq.heappop(pq)
        if d != dist[u]:
            continue
        # If the node is not a source, update its parent information.
        if par is not None:
            # For equal distances, we select the edge with the minimal weight.
            if parent_info[u] is None or edge_w < parent_info[u][1]:
                parent_info[u] = (par, edge_w)
        # Explore neighbors
        for v, w in graph[u]:
            nd = d + w
            # If found a strictly shorter path, update.
            if nd < dist[v]:
                dist[v] = nd
                parent_info[v] = (u, w)
                heapq.heappush(pq, (nd, w, v, u))
            # If the found path equals the current shortest path,
            # choose the one with smaller edge weight (tie-breaker).
            elif nd == dist[v]:
                # Check if the current parent's edge weight is greater than new candidate.
                if parent_info[v] is None or w < parent_info[v][1]:
                    parent_info[v] = (u, w)
                    heapq.heappush(pq, (nd, w, v, u))

    result = []
    for v in range(n):
        if v in sources:
            continue
        if dist[v] < INF and parent_info[v] is not None:
            u, w = parent_info[v]
            result.append((u, v, w))
    return result