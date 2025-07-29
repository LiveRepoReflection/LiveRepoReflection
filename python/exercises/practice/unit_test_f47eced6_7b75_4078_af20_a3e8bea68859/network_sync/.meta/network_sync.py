from collections import defaultdict, deque

def min_max_synchronization_time(n, edges, data_sizes, computational_capacities, k):
    # Edge case: if each node is its own cluster, sync time is 0.
    if k >= n:
        return 0.0

    # Build Maximum Spanning Tree (MST) using Kruskal’s algorithm.
    parent = list(range(n))
    rank = [0] * n

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        if rank[ru] < rank[rv]:
            parent[ru] = rv
        elif rank[ru] > rank[rv]:
            parent[rv] = ru
        else:
            parent[rv] = ru
            rank[ru] += 1
        return True

    # Sort edges descending by bandwidth to build a maximum spanning tree.
    sorted_edges = sorted(edges, key=lambda x: x[2], reverse=True)
    mst_edges = []
    for u, v, bw in sorted_edges:
        if union(u, v):
            mst_edges.append((u, v, bw))
            if len(mst_edges) == n - 1:
                break

    # Build adjacency list for the MST.
    mst_adj = defaultdict(list)
    for u, v, bw in mst_edges:
        mst_adj[u].append((v, bw))
        mst_adj[v].append((u, bw))

    # Partition the MST into clusters by removing (k-1) edges.
    # We use a heuristic: remove the (k-1) edges with the smallest bandwidth in the MST.
    # Sort mst_edges by bandwidth ascending.
    mst_edges_sorted = sorted(mst_edges, key=lambda x: x[2])
    remove_edges_set = set()
    for i in range(k - 1):
        u, v, bw = mst_edges_sorted[i]
        # Use tuple sorted order to mark removal.
        remove_edges_set.add(tuple(sorted((u, v))))

    # Build clusters (connected components) by doing DFS on the MST with removed edges.
    visited = [False] * n
    clusters = []
    for i in range(n):
        if not visited[i]:
            comp = []
            queue = deque([i])
            visited[i] = True
            while queue:
                u = queue.popleft()
                comp.append(u)
                for v, bw in mst_adj[u]:
                    if visited[v]:
                        continue
                    # Check if edge (u,v) is removed.
                    if tuple(sorted((u, v))) in remove_edges_set:
                        continue
                    visited[v] = True
                    queue.append(v)
            clusters.append(comp)

    # Precompute for each cluster: total data.
    cluster_total_data = {}
    for idx, comp in enumerate(clusters):
        total = sum(data_sizes[node] for node in comp)
        cluster_total_data[idx] = total

    # For each cluster, compute the best possible synchronization time with a valid leader.
    def compute_cluster_sync_time(cluster):
        # If only one node, sync time is 0.
        if len(cluster) == 1:
            # Check leader capacity.
            node = cluster[0]
            if computational_capacities[node] < data_sizes[node]:
                return None
            return 0.0

        # Build tree (adjacency list) for the current cluster from MST.
        tree = defaultdict(list)
        in_cluster = set(cluster)
        def build_tree(u, par):
            for v, bw in mst_adj[u]:
                if v == par or v not in in_cluster:
                    continue
                # If the edge between u and v is removed, skip.
                if tuple(sorted((u, v))) in remove_edges_set:
                    continue
                tree[u].append((v, bw))
                tree[v].append((u, bw))
                build_tree(v, u)
        # Choose an arbitrary node as root.
        root = cluster[0]
        build_tree(root, -1)

        best_cluster_time = float('inf')
        # Try each node in the cluster as candidate leader.
        for leader in cluster:
            # Check computational capacity constraint.
            if computational_capacities[leader] < sum(data_sizes[node] for node in cluster):
                continue

            # Do a DFS/BFS from leader over the tree to compute the bottleneck on the path.
            bottlenecks = {leader: float("inf")}
            dq = deque([leader])
            while dq:
                u = dq.popleft()
                for v, bw in tree[u]:
                    # If v not visited yet, update bottleneck.
                    if v not in bottlenecks:
                        bottlenecks[v] = min(bottlenecks[u], bw)
                        dq.append(v)
            # If not all nodes reached, skip this leader (should not happen in connected tree).
            if len(bottlenecks) != len(cluster):
                continue

            # Compute aggregation and distribution times.
            agg_time = 0.0
            min_bw = float("inf")
            for node in cluster:
                if node == leader:
                    continue
                # To avoid division by zero.
                if bottlenecks[node] == 0:
                    agg_time = float("inf")
                    break
                time_val = data_sizes[node] / bottlenecks[node]
                if time_val > agg_time:
                    agg_time = time_val
                if bottlenecks[node] < min_bw:
                    min_bw = bottlenecks[node]
            if min_bw == 0:
                continue
            total_data = sum(data_sizes[node] for node in cluster)
            disp_time = total_data / min_bw
            cluster_time = agg_time + disp_time
            if cluster_time < best_cluster_time:
                best_cluster_time = cluster_time
        if best_cluster_time == float('inf'):
            return None
        return best_cluster_time

    cluster_sync_times = []
    for idx, comp in enumerate(clusters):
        time_val = compute_cluster_sync_time(comp)
        if time_val is None:
            return -1
        cluster_sync_times.append(time_val)

    overall_sync_time = max(cluster_sync_times)
    return overall_sync_time