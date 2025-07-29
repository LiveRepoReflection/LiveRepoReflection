import itertools
from collections import defaultdict, deque

def net_partition(n, k, edges, dependencies, min_size, max_size):
    # Build adjacency list for connectivity check
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Precompute all possible connected clusters
    all_clusters = []
    for size in range(min_size, max_size + 1):
        for nodes in itertools.combinations(range(n), size):
            if is_connected(nodes, adj):
                all_clusters.append(set(nodes))

    # Try all possible combinations of k clusters
    best_solution = None
    min_cross_deps = float('inf')

    for cluster_combination in itertools.combinations(all_clusters, k):
        # Check if clusters are disjoint and cover all nodes
        all_nodes = set()
        overlapping = False
        for cluster in cluster_combination:
            if all_nodes & cluster:
                overlapping = True
                break
            all_nodes.update(cluster)
        
        if overlapping or len(all_nodes) != n:
            continue

        # Count cross-cluster dependencies
        cross_deps = 0
        for u, v in dependencies:
            u_cluster = None
            v_cluster = None
            for i, cluster in enumerate(cluster_combination):
                if u in cluster:
                    u_cluster = i
                if v in cluster:
                    v_cluster = i
            if u_cluster != v_cluster:
                cross_deps += 1

        # Update best solution
        if cross_deps < min_cross_deps:
            min_cross_deps = cross_deps
            best_solution = [list(cluster) for cluster in cluster_combination]

    return best_solution

def is_connected(nodes, adj):
    if not nodes:
        return True
    visited = set()
    queue = deque([nodes[0]])
    visited.add(nodes[0])
    
    while queue:
        node = queue.popleft()
        for neighbor in adj[node]:
            if neighbor in nodes and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return len(visited) == len(nodes)