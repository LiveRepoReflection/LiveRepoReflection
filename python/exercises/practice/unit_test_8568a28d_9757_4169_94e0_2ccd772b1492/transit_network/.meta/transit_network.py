from itertools import combinations

def maximum_ridership(N, edges, budget, start_node):
    # If there are no nodes, or impossible to span
    if N == 0 or len(edges) < N - 1:
        return 0

    # Union-find helper functions
    def find(parent, i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(parent, rank, x, y):
        xroot = find(parent, x)
        yroot = find(parent, y)
        if xroot == yroot:
            return False
        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot
        else:
            parent[yroot] = xroot
            rank[xroot] += 1
        return True

    best_ridership = 0
    m = len(edges)
    # Pre-sort edges to try combinations with higher likelihood of higher ridership
    # Sort by ridership descending; this doesn't reduce complexity but might help in some cases.
    sorted_edges = sorted(edges, key=lambda x: x[3], reverse=True)

    # Enumerate all combinations of length N-1 among the edges.
    # For small graphs (as in test cases) this brute-force approach is acceptable.
    for subset in combinations(sorted_edges, N - 1):
        parent = list(range(N))
        rank = [0] * N
        total_cost = 0
        total_ridership = 0
        edge_count = 0

        valid_tree = True
        for (u, v, cost, ridership) in subset:
            # If u and v are already connected, then adding this edge would create a cycle.
            if find(parent, u) == find(parent, v):
                valid_tree = False
                break
            # Otherwise, union the two sets.
            union(parent, rank, u, v)
            total_cost += cost
            total_ridership += ridership
            edge_count += 1

        # Check if we have formed a valid spanning tree
        # It must have exactly N-1 edges and all nodes connected.
        if valid_tree and edge_count == N - 1:
            # Verify full connectivity by checking that all nodes share the same root
            root = find(parent, start_node)
            connected = all(find(parent, i) == root for i in range(N))
            if connected and total_cost <= budget:
                best_ridership = max(best_ridership, total_ridership)

    return best_ridership