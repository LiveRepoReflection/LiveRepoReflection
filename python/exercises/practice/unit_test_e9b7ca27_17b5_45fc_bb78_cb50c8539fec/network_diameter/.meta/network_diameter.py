def find_min_network_diameter(N: int, B: int, connections: list[tuple[int, int, int, int]]) -> int:
    """
    Finds the minimum possible network diameter achievable under the given constraints.
    The solution uses a heuristic approach:
    1. Constructs a minimum spanning tree (MST) based solely on cost.
    2. If the MST cost exceeds B or the MST cannot be constructed (i.e. graph is disconnected),
       returns -1.
    3. Then, if budget remains, extra edges are greedily added to reduce the network's diameter.
       Edge selection is based on the improvement (reduction in diameter) per unit cost.
    Note: This heuristic does not guarantee an optimal solution for all instances, but given the 
    complexity (NP-hard nature) of the bounded-diameter spanning network problem, it aims to 
    produce competitive solutions for many practical inputs.
    """
    if N == 1:
        return 0

    # Helper: Union-Find (Disjoint Set Union) data structure for Kruskal's MST.
    parent = list(range(N + 1))
    rank = [0] * (N + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    # Build MST based on cost using Kruskal.
    sorted_edges = sorted(connections, key=lambda edge: edge[2])
    mst_edges = []
    mst_cost = 0
    for u, v, cost, latency in sorted_edges:
        if union(u, v):
            mst_edges.append((u, v, cost, latency))
            mst_cost += cost
            if len(mst_edges) == N - 1:
                break
    # If MST is not spanning all nodes, network cannot be connected.
    if len(mst_edges) != N - 1:
        return -1
    if mst_cost > B:
        return -1

    # Build initial graph from MST edges.
    graph = {i: [] for i in range(1, N + 1)}
    for u, v, cost, latency in mst_edges:
        graph[u].append((v, latency))
        graph[v].append((u, latency))
    total_cost = mst_cost

    # Helper: Compute all-pairs shortest path (Floyd-Warshall).
    def compute_diameter(graph):
        INF = float('inf')
        dist = [[INF] * (N + 1) for _ in range(N + 1)]
        for i in range(1, N + 1):
            dist[i][i] = 0
        for u in graph:
            for v, latency in graph[u]:
                if latency < dist[u][v]:
                    dist[u][v] = latency
        for k in range(1, N + 1):
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        diameter = 0
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if dist[i][j] == INF:
                    return INF  # Graph not connected.
                if dist[i][j] > diameter:
                    diameter = dist[i][j]
        return diameter

    current_diameter = compute_diameter(graph)

    # Greedy improvement: Consider extra edges (those not in the MST) that may reduce diameter.
    # We store extra edges from original connections. It's possible that some edges appear in MST multiple times;
    # so we consider all edges but skip if they are already in our graph with equal or lower latency.
    mst_edge_set = set()
    for u, v, cost, latency in mst_edges:
        # Store in sorted order to ease lookup.
        mst_edge_set.add((min(u, v), max(u, v), latency))

    # List all candidate extra edges from original connections.
    extra_edges = []
    for u, v, cost, latency in connections:
        key = (min(u, v), max(u, v), latency)
        # Allow adding an edge if it is not already in MST with equal or lower latency.
        if key not in mst_edge_set:
            extra_edges.append((u, v, cost, latency))
    # Sort extra edges by cost (low cost first) then by latency.
    extra_edges.sort(key=lambda x: (x[2], x[3]))

    # Greedy selection: try to add each extra edge if it reduces the network diameter and fits in budget.
    improved = True
    while improved:
        improved = False
        best_improvement = 0
        best_edge = None
        best_new_diam = current_diameter
        # Consider each candidate extra edge that we haven't yet added.
        # We also allow adding multiple copies if it helps improvement, but here we assume one addition per edge.
        for u, v, cost, latency in extra_edges:
            if total_cost + cost > B:
                continue
            # Temporarily add the edge.
            graph[u].append((v, latency))
            graph[v].append((u, latency))
            new_diam = compute_diameter(graph)
            # Check improvement.
            improvement = current_diameter - new_diam
            if improvement > best_improvement:
                best_improvement = improvement
                best_edge = (u, v, cost, latency)
                best_new_diam = new_diam
            # Remove the temporarily added edge.
            graph[u].pop()
            graph[v].pop()
        if best_edge is not None:
            # Add the best_edge permanently.
            u, v, cost, latency = best_edge
            graph[u].append((v, latency))
            graph[v].append((u, latency))
            total_cost += cost
            current_diameter = best_new_diam
            improved = True

    return current_diameter


if __name__ == "__main__":
    # For local debugging, you can include sample tests here.
    # For example:
    N = 4
    B = 200
    connections = [
        (1, 2, 50, 10),
        (1, 3, 75, 15),
        (1, 4, 100, 20),
        (2, 3, 60, 12),
        (2, 4, 80, 16),
        (3, 4, 40, 8)
    ]
    print(find_min_network_diameter(N, B, connections))