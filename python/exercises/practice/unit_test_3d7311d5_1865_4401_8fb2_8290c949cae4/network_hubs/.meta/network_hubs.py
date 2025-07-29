import math
from functools import lru_cache

def min_max_latency(graph, num_hubs):
    # Determine number of nodes: include nodes that appear as keys or in edges.
    nodes = set(graph.keys())
    for nbrs in graph.values():
        for nbr, _ in nbrs:
            nodes.add(nbr)
    n = max(nodes) + 1

    # Ensure every node from 0 to n-1 is in the graph dictionary.
    for i in range(n):
        if i not in graph:
            graph[i] = []

    # Initialize distance matrix using Floyd-Warshall approach.
    dist = [[math.inf] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    for u in range(n):
        for v, w in graph[u]:
            if w < dist[u][v]:
                dist[u][v] = w
                dist[v][u] = w  # because the graph is undirected

    for k in range(n):
        for i in range(n):
            # Skip if dist[i][k] == inf to avoid unnecessary loop iterations.
            if dist[i][k] == math.inf:
                continue
            for j in range(n):
                if dist[k][j] < math.inf and dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Check if all nodes are reachable from at least one node.
    # This isn't necessary for the algorithm because unreachable nodes can be covered if a hub is placed on them.
    # But if any node is isolated and no hub is placed there, it is unreachable.
    # We handle this in the covering decision.

    # Pre-calculate candidate upper bound for binary search: maximum finite distance.
    max_distance = 0
    for i in range(n):
        for j in range(n):
            if dist[i][j] < math.inf:
                if dist[i][j] > max_distance:
                    max_distance = dist[i][j]

    # Build coverage sets for a given L will be computed inside the decision check.
    def can_cover_within(L):
        # For each node i, compute the set of nodes it can cover if chosen as a hub.
        covers = []
        for i in range(n):
            cover_set = set()
            for j in range(n):
                if dist[i][j] <= L:
                    cover_set.add(j)
            covers.append(cover_set)

        all_nodes = set(range(n))
        memo = {}

        @lru_cache(maxsize=None)
        def helper(uncovered_frozenset, hubs_left):
            uncovered = set(uncovered_frozenset)
            if not uncovered:
                return True
            if hubs_left == 0:
                return False
            state = (uncovered_frozenset, hubs_left)
            if state in memo:
                return memo[state]
            # Choose an uncovered node with the smallest number of hubs that can cover it to prune search.
            candidate = None
            min_options = n + 1
            for node in uncovered:
                options = 0
                for i in range(n):
                    if node in covers[i]:
                        options += 1
                if options < min_options:
                    min_options = options
                    candidate = node
            # Try all hub placements that cover the candidate node.
            for hub in range(n):
                if candidate in covers[hub]:
                    new_uncovered = uncovered - covers[hub]
                    new_uncovered_frozen = frozenset(new_uncovered)
                    if helper(new_uncovered_frozen, hubs_left - 1):
                        memo[state] = True
                        return True
            memo[state] = False
            return False

        return helper(frozenset(all_nodes), num_hubs)

    # Binary search over the possible maximum latency values.
    low, high = 0, max_distance
    result = -1
    while low <= high:
        mid = (low + high) // 2
        if can_cover_within(mid):
            result = mid
            high = mid - 1
        else:
            low = mid + 1

    return result