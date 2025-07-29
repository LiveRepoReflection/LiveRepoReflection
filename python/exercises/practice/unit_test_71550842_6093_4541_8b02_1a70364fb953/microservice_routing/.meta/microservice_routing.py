import math

def min_router_capacity(N, k, T):
    # Edge case: if only one service, no internal routers exist.
    if N <= 1:
        return 0

    # Compute the depth L of the tree (number of internal levels)
    # N = k^L, where leaves are at level L and internal nodes are at levels 0..L-1.
    L = int(round(math.log(N, k)))
    
    # Precompute the path for each leaf.
    # Each path is a list of internal nodes represented as (level, pos).
    # Level 0 is the root: always represented as (0, 0).
    # For level l (1 <= l <= L-1), the node id is computed by: pos = leaf_index // (k ** (L - l))
    paths = []
    for i in range(N):
        path = []
        for l in range(0, L):
            factor = k ** (L - l)
            pos = i // factor
            path.append((l, pos))
        paths.append(path)
    
    # Dictionary to accumulate the load for each internal node.
    load = {}
    
    # Function to add weight to a node in the load dictionary.
    def add_load(node, w):
        if node in load:
            load[node] += w
        else:
            load[node] = w

    # For each pair (i, j) with i != j and T[i][j] > 0, compute the nodes along the route.
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            w = T[i][j]
            if w == 0:
                continue

            path_i = paths[i]
            path_j = paths[j]
            # Find Lowest Common Ancestor (LCA)
            # Iterate until nodes differ; the last common node is the LCA.
            lca_index = 0
            while lca_index < L and path_i[lca_index] == path_j[lca_index]:
                lca_index += 1
            # lca_index is now one index past the last common node.
            lca_index -= 1  # Adjust to get LCA index (at least 0, because root is always common)
            # Add weight to all nodes on the upward path from leaf i to LCA (inclusive)
            for node in path_i[lca_index:]:
                add_load(node, w)
            # Add weight to all nodes on the upward path from leaf j to LCA, excluding LCA (to avoid double-counting)
            for node in path_j[lca_index+1:]:
                add_load(node, w)

    # The answer is the maximum load among all routers.
    max_load = 0
    for l in load.values():
        if l > max_load:
            max_load = l
    return max_load