import heapq

def find_dominating_set(graph, K):
    # Obtain sorted list of all nodes in the graph.
    nodes = sorted(graph.keys())
    
    # Precompute reachable sets (coverage) for each node using Dijkstra's algorithm.
    coverage = {}
    for node in nodes:
        dist = {node: 0}
        heap = [(0, node)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, weight in graph.get(u, []):
                nd = d + weight
                if nd <= K and (v not in dist or nd < dist[v]):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        coverage[node] = set(dist.keys())
    
    # Use a brute-force approach to find the minimum dominating set.
    # A set S of nodes is dominating if every node not in S
    # is reachable from at least one node in S (i.e. is covered by S).
    n = len(nodes)
    best = None
    best_size = float('inf')
    
    # Iterate over all non-empty subsets of nodes using bitmask iteration.
    for mask in range(1, 1 << n):
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nodes[i])
        subset_set = set(subset)
        
        # Compute the union of coverage for all nodes in the current subset.
        union_cov = set()
        for s in subset:
            union_cov |= coverage[s]
        
        # Check if every node not in the subset is covered.
        if (set(nodes) - subset_set) <= union_cov:
            sorted_subset = sorted(subset)
            if len(sorted_subset) < best_size:
                best_size = len(sorted_subset)
                best = sorted_subset
            elif len(sorted_subset) == best_size and sorted_subset < best:
                best = sorted_subset

    if best is None:
        return 0, []
    return best_size, best