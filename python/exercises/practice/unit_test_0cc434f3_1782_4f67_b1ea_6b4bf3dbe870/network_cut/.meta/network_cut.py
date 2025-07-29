def min_removal_cost(n, edges, k):
    # Calculate the total cost of all edges
    total_cost = sum(cost for _, _, cost in edges)

    # Edge case: if k == n, no edge is kept and removal cost is total_cost.
    if k == n:
        return total_cost
    # Edge case: if k < 1 or k > n, it is an invalid input; we can raise an error.
    if k < 1 or k > n:
        raise ValueError("k must be between 1 and n, inclusive.")
        
    # Union-Find data structure for cycle detection in maximum spanning forest
    parent = list(range(n))
    rank = [0] * n

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        if root_u == root_v:
            return False
        # Union by rank
        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        elif rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        else:
            parent[root_v] = root_u
            rank[root_u] += 1
        return True

    # Sort edges in descending order by cost for maximum spanning forest
    sorted_edges = sorted(edges, key=lambda x: x[2], reverse=True)
    
    kept_cost = 0
    components = n
    # We need to add edges until we have exactly k connected components.
    for u, v, cost in sorted_edges:
        if components <= k:
            break
        if union(u, v):
            kept_cost += cost
            components -= 1

    # After processing, if we did not reach exactly k components, 
    # then the graph was initially disconnected or input error.
    if components != k:
        raise ValueError("Cannot partition the network into exactly k subnetworks.")

    removal_cost = total_cost - kept_cost
    return removal_cost

if __name__ == "__main__":
    # Minimal manual test to verify the implementation works standalone.
    # For more comprehensive testing, run network_cut_test.py.
    n = 4
    edges = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 0, 4)]
    k = 2
    print("Minimum removal cost:", min_removal_cost(n, edges, k))