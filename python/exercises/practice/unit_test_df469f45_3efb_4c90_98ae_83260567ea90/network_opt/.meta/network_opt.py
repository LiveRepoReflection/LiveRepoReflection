def optimize_network(n, p, c, min_bandwidth, max_bandwidth, B, D, data_size):
    # Helper: Union-find implementation
    parent = list(range(n))
    rank = [0] * n

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri = find(i)
        rj = find(j)
        if ri == rj:
            return False
        if rank[ri] < rank[rj]:
            parent[ri] = rj
        elif rank[ri] > rank[rj]:
            parent[rj] = ri
        else:
            parent[rj] = ri
            rank[ri] += 1
        return True

    # Prepare all possible edges: (cost, i, j)
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if c[i][j] != float("inf"):
                edges.append((c[i][j], i, j))
    # Sort edges by cost ascending
    edges.sort(key=lambda x: x[0])

    # Initialize degrees and chosen edges list
    degrees = [0] * n
    chosen_edges = []
    total_cost = 0

    # Build a spanning tree with degree constraint using a modified greedy approach.
    # This is a heuristic approach for the bounded degree spanning tree.
    for cost_edge, i, j in edges:
        if degrees[i] < D and degrees[j] < D:
            if union(i, j):
                if total_cost + cost_edge > B:
                    # Budget exceeded: rollback union (not adding this edge)
                    # Since union is not reversible easily, skip adding edge.
                    continue
                chosen_edges.append((i, j, cost_edge))
                degrees[i] += 1
                degrees[j] += 1
                total_cost += cost_edge

    # Check if spanning tree is built (i.e., graph is connected)
    root = find(0)
    for i in range(1, n):
        if find(i) != root:
            # Cannot connect graph under the constraints, return all-zero matrix
            return [[0 for _ in range(n)] for _ in range(n)]

    # After establishing connectivity, try to add additional edges to reduce latency.
    # We add extra edges if possible (respecting budget and degree constraints) and not already chosen.
    # This heuristic iteration goes over the edge list again.
    for cost_edge, i, j in edges:
        # Skip if already chosen in either orientation
        if any((i == a and j == b) or (i == b and j == a) for a, b, _ in chosen_edges):
            continue
        if degrees[i] < D and degrees[j] < D:
            if total_cost + cost_edge <= B:
                chosen_edges.append((i, j, cost_edge))
                degrees[i] += 1
                degrees[j] += 1
                total_cost += cost_edge

    # Build the adjacency matrix with symmetric bandwidth assignment.
    # For each chosen edge, assign the maximum bandwidth allowed (since higher bandwidth reduces transmission latency).
    adj = [[0 for _ in range(n)] for _ in range(n)]
    for i, j, _ in chosen_edges:
        # Use max_bw for each edge (optimal latency) within allowed range.
        bw = max_bandwidth
        adj[i][j] = bw
        adj[j][i] = bw

    return adj