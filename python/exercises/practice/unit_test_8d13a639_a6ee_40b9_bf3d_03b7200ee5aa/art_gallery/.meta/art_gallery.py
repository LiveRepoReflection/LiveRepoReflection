def min_camera_cost(graph, artwork_values, camera_costs):
    # If no artworks exist anywhere, no camera is needed.
    has_artwork = False
    for art_list in artwork_values.values():
        if art_list:
            has_artwork = True
            break
    if not has_artwork:
        return 0

    # Identify nodes that have artworks.
    artwork_nodes = []
    for node, arts in artwork_values.items():
        if arts:  # non-empty list
            artwork_nodes.append(node)
    artwork_nodes = list(set(artwork_nodes))
    m = len(artwork_nodes)
    art_index = {node: idx for idx, node in enumerate(artwork_nodes)}

    # Precompute reachable sets for each node using DFS.
    # We compute for all nodes that appear in camera_costs, assuming camera_costs provided for every location.
    # Note: Some nodes might not be keys in 'graph' so we treat them as nodes with no outgoing edges.
    all_nodes = set(camera_costs.keys())
    for node in artwork_values.keys():
        all_nodes.add(node)
    for node in graph:
        all_nodes.add(node)
        for neigh in graph[node]:
            all_nodes.add(neigh)

    computed_reach = {}
    def dfs(start):
        if start in computed_reach:
            return computed_reach[start]
        visited = set()
        stack = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            # Get neighbors from graph if available; if not, assume no outgoing edges.
            for v in graph.get(u, []):
                if v not in visited:
                    stack.append(v)
        computed_reach[start] = visited
        return visited

    # Build candidate list: each candidate is (cost, coverage_mask)
    candidates = []
    for node in all_nodes:
        # Only consider nodes that have a defined camera cost.
        if node not in camera_costs:
            continue
        reachable = dfs(node)
        mask = 0
        for r in reachable:
            if r in art_index:
                mask |= (1 << art_index[r])
        if mask != 0:
            candidates.append((camera_costs[node], mask))

    # Use DP to solve weighted set cover optimally.
    full_mask = (1 << m) - 1
    INF = float('inf')
    dp = [INF] * (1 << m)
    dp[0] = 0

    # Iterate over all states and update with each candidate.
    for state in range(1 << m):
        if dp[state] == INF:
            continue
        for cost, cov in candidates:
            new_state = state | cov
            if dp[new_state] > dp[state] + cost:
                dp[new_state] = dp[state] + cost

    return dp[full_mask]


if __name__ == '__main__':
    # For local testing; remove or comment out when running unit tests.
    # Example: cycle graph test.
    graph = {
        0: [1],
        1: [2],
        2: [0]
    }
    artwork_values = {
        0: [15],
        1: [25],
        2: [35]
    }
    camera_costs = {
        0: 4,
        1: 10,
        2: 6
    }
    print(min_camera_cost(graph, artwork_values, camera_costs))