def island_network(N, B, C, T):
    # Build list of valid edges: each edge is (u, v, cost, time)
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            if C[i][j] != -1 and T[i][j] != -1:
                edges.append((i, j, C[i][j], T[i][j]))
    # If there are not enough edges to possibly connect all islands, return -1
    if len(edges) < N - 1:
        return -1

    # Sort edges primarily by time (ascending) then by cost (ascending)
    edges.sort(key=lambda x: (x[3], x[2]))
    # global minimum time among edges (for lower bound estimation)
    global_min_time = min(edge[3] for edge in edges) if edges else 0

    # Union-Find helper functions
    def find(parent, i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(parent, i, j):
        root_i = find(parent, i)
        root_j = find(parent, j)
        if root_i != root_j:
            parent[root_j] = root_i

    # Global best answer (minimum total time)
    best_time = [float('inf')]
    
    # Branch and bound search on spanning trees using recursion.
    # idx: current index in edges list to consider
    # count: number of edges chosen so far
    # curr_time: sum of times so far
    # curr_cost: sum of costs so far
    # parent: current union-find parent list representing connectivity
    def search(idx, count, curr_time, curr_cost, parent):
        # If we already have N-1 edges and connectivity is complete, update best_time.
        if count == N - 1:
            # In a spanning tree built with N-1 edges, connectivity is guaranteed.
            if curr_cost <= B and curr_time < best_time[0]:
                best_time[0] = curr_time
            return

        # Prune if even adding the best possible times for remaining edges
        # we cannot beat the current best_time. (Lower bound bound)
        remaining = (N - 1) - count
        if curr_time + remaining * global_min_time >= best_time[0]:
            return
        # If we have exhausted all edges, return
        if idx >= len(edges):
            return

        # For every remaining edge, we have two choices: include or skip.
        for i in range(idx, len(edges)):
            u, v, cost, time_edge = edges[i]
            # Make a copy of the union-find for decision branch.
            u_root = find(parent, u)
            v_root = find(parent, v)
            # Option 1: If u and v are not already connected, try including this edge.
            if u_root != v_root:
                new_cost = curr_cost + cost
                new_time = curr_time + time_edge
                if new_cost > B:
                    # Prune branch where budget exceeded.
                    continue
                # Make a copy of parent for union operation.
                new_parent = parent[:]
                union(new_parent, u, v)
                search(i + 1, count + 1, new_time, new_cost, new_parent)
            # Option 2: Also explore skipping this edge.
            # Since edges are sorted by time, skipping may allow picking a different edge later.
            # But if the next edge has the same endpoints, then skipping might be redundant.
            # We try skipping only once per level.
            # We call search skipping the current edge.
            # To avoid exponential branching, we call skip only once per recursion level.
            # This is a standard trick in branch and bound for spanning tree enumeration.
            # After exploring the "include" branch for one edge, we then try skipping it.
            # Then we break out of the loop to avoid redundant skips.
            search(i + 1, count, curr_time, curr_cost, parent)
            # After exploring the option to skip this edge once, break so that 
            # we don't try skipping for every edge at the same recursion level.
            return

    # Initial union-find structure: each island is its own component.
    parent_init = list(range(N))
    search(0, 0, 0, 0, parent_init)
    
    return best_time[0] if best_time[0] != float('inf') else -1

if __name__ == "__main__":
    # Simple manual test (uncomment to run basic test)
    N = 4
    B = 100
    C = [[0, 20, 30, 40],
         [20, 0, 30, 30],
         [30, 30, 0, 20],
         [40, 30, 20, 0]]
    T = [[0, 5, 7, 9],
         [5, 0, 6, 6],
         [7, 6, 0, 4],
         [9, 6, 4, 0]]
    result = island_network(N, B, C, T)
    print(result)