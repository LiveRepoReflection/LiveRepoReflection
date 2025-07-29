def reconstruct_network(n, measurements):
    # Validate n
    if n <= 0:
        return []
    
    # If no measurements exist, return a simple chain with default latency 1.0
    if not measurements:
        adj_list = [[] for _ in range(n)]
        for i in range(n - 1):
            adj_list[i].append((i + 1, 1.0))
            adj_list[i + 1].append((i, 1.0))
        for neighbors in adj_list:
            neighbors.sort(key=lambda x: x[0])
        return adj_list

    # Build a dictionary for measured edges; key is tuple (u,v) with u < v, value is min latency observed.
    measured_edges = {}
    for u, v, latency in measurements:
        if u < 0 or u >= n or v < 0 or v >= n or u == v:
            continue  # Skip invalid edges
        key = (u, v) if u < v else (v, u)
        if key not in measured_edges or latency < measured_edges[key]:
            measured_edges[key] = latency

    # Initialize union-find structure for connectivity based solely on measured edges.
    parent = list(range(n))

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    # Build union-find over measured edges.
    for (u, v), latency in measured_edges.items():
        union(u, v)

    # Find all connected components.
    components = {}
    for i in range(n):
        root = find(i)
        if root not in components:
            components[root] = []
        components[root].append(i)

    # Prepare a working dictionary of all edges that will be included in the final network.
    # Start by including all measured edges.
    final_edges = {}
    for (u, v), latency in measured_edges.items():
        final_edges[(u, v)] = latency

    # If the graph is not connected, connect components with dummy edges.
    comp_roots = sorted(components.keys())
    if len(comp_roots) > 1:
        # Choose one representative from each component, smallest index.
        representatives = [min(components[root]) for root in comp_roots]
        # Define a dummy latency. It could be the average of measured latencies.
        dummy_latency = sum(measured_edges.values()) / len(measured_edges) if measured_edges else 1.0
        # Alternatively, if average is 0, use default.
        if dummy_latency <= 0:
            dummy_latency = 1.0
        # Connect consecutive representatives to ensure overall connectivity.
        for i in range(len(representatives) - 1):
            u = representatives[i]
            v = representatives[i + 1]
            key = (u, v) if u < v else (v, u)
            # Add dummy edge if not already present
            if key not in final_edges:
                final_edges[key] = dummy_latency

    # Build adjacency list based on final_edges.
    adj_list = [[] for _ in range(n)]
    for (u, v), latency in final_edges.items():
        adj_list[u].append((v, float(latency)))
        adj_list[v].append((u, float(latency)))

    # Optional enhancement: If there are extra measured edges, one could try to optimize the graph further.
    # For this baseline solution, we simply include all edges we have.
    # Sort each neighbor list by neighbor label.
    for neighbors in adj_list:
        neighbors.sort(key=lambda x: x[0])
    return adj_list

if __name__ == "__main__":
    # Example run: This block is only for direct execution.
    n = 6
    measurements = [
        (0, 1, 1.0),
        (1, 2, 2.0),
        (2, 3, 1.5),
        (3, 4, 2.1),
        (4, 5, 1.1),
        (0, 5, 10.0),
        (1, 4, 3.0),
        (2, 5, 2.5)
    ]
    network = reconstruct_network(n, measurements)
    for i, edges in enumerate(network):
        print("Server {}: {}".format(i, edges))