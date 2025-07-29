from collections import deque

def optimal_meeting_point(n, edges, w):
    if n == 1:
        return 0

    # Build adjacency list
    adj = [[] for _ in range(n)]
    for u, v, cost in edges:
        adj[u].append((v, cost))
        adj[v].append((u, cost))

    # Precompute parent and size for each node using BFS from root (0)
    parent = [-1] * n
    size = [0] * n
    total_weight = sum(w)
    
    # First pass: compute size and parent relationships
    stack = [(0, -1)]
    order = []
    while stack:
        u, p = stack.pop()
        parent[u] = p
        order.append(u)
        for v, cost in adj[u]:
            if v != p:
                stack.append((v, u))

    # Second pass (post-order): compute size
    size = [0] * n
    for u in reversed(order):
        size[u] = w[u]
        for v, cost in adj[u]:
            if v != parent[u]:
                size[u] += size[v]

    # Compute initial cost for root (0)
    cost = [0] * n
    stack = [(0, -1, 0)]
    while stack:
        u, p, dist = stack.pop()
        cost[0] += dist * w[u]
        for v, c in adj[u]:
            if v != p:
                stack.append((v, u, dist + c))

    # Perform BFS to compute costs for all nodes
    q = deque([0])
    while q:
        u = q.popleft()
        for v, c in adj[u]:
            if v != parent[u]:
                cost[v] = cost[u] - size[v] * c + (total_weight - size[v]) * c
                q.append(v)

    # Find node with minimum cost
    min_cost = min(cost)
    candidates = [i for i in range(n) if cost[i] == min_cost]
    return min(candidates)