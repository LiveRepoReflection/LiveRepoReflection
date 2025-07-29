def optimal_train_network(n, edges, budget, revenue_per_passenger):
    if n == 1:
        return 0

    m = len(edges)
    processed_edges = []
    for (u, v, cost, p) in edges:
        processed_edges.append((u, v, cost, p * revenue_per_passenger))

    best = [-1]

    def find(x, parent):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def connected(parent):
        root = find(0, parent)
        for i in range(1, n):
            if find(i, parent) != root:
                return False
        return True

    def backtrack(i, curr_cost, curr_revenue, parent, size):
        if curr_cost > budget:
            return
        if i == m:
            if connected(parent):
                if curr_revenue > best[0]:
                    best[0] = curr_revenue
            return

        # Option 1: skip current edge
        backtrack(i + 1, curr_cost, curr_revenue, parent, size)

        # Option 2: include current edge
        u, v, cost, rev = processed_edges[i]
        new_cost = curr_cost + cost
        if new_cost > budget:
            return

        # Save current state for backtracking
        parent_copy = parent[:]
        size_copy = size[:]

        ru = find(u, parent)
        rv = find(v, parent)
        if ru != rv:
            # Union by size
            if size[ru] < size[rv]:
                ru, rv = rv, ru
            parent[rv] = ru
            size[ru] += size[rv]

        backtrack(i + 1, new_cost, curr_revenue + rev, parent, size)

        # Restore state
        parent[:] = parent_copy
        size[:] = size_copy

    parent = list(range(n))
    size = [1] * n
    backtrack(0, 0, 0, parent, size)
    return best[0]