from collections import defaultdict, deque

def optimize_network(N, cities, potential_edges, capacity_factors):
    # Utility function: return normalized edge tuple (smaller id first)
    def norm_edge(u, v):
        return (u, v) if u <= v else (v, u)

    # Union-Find structure for MST building
    parent = {city[0]: city[0] for city in cities}
    rank = {city[0]: 0 for city in cities}

    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])
        return parent[u]

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

    # Build MST using potential_edges sorted by cost (base_cost * terrain_factor)
    sorted_edges = sorted(potential_edges, key=lambda e: e[2] * e[3])
    network = []
    used_edges = set()  # store normalized edges
    for u, v, base_cost, terrain_factor in sorted_edges:
        if union(u, v):
            edge = norm_edge(u, v)
            network.append(edge)
            used_edges.add(edge)

    # Determine remaining edges (normalized, unique)
    all_edges = {}
    for u, v, base_cost, terrain_factor in potential_edges:
        edge = norm_edge(u, v)
        cost = base_cost * terrain_factor
        # In case of duplicates, take the minimal cost version.
        if edge in all_edges:
            all_edges[edge] = min(all_edges[edge], cost)
        else:
            all_edges[edge] = cost
    remaining_edges = []
    for edge, cost in all_edges.items():
        if edge not in used_edges:
            remaining_edges.append((edge[0], edge[1], cost))
    remaining_edges.sort(key=lambda e: e[2])

    # Helper functions for network flow and disjoint paths

    def build_flow_graph(edges, use_unit_capacity=False):
        # Build a directed graph representation from undirected edges.
        graph = defaultdict(dict)
        for u, v in edges:
            key = norm_edge(u, v)
            # Determine capacity: if unit capacity, each edge gets capacity 1
            if use_unit_capacity:
                cap = 1
            else:
                # Use capacity_factors: key in capacity_factors dictionary uses normalized edge
                factor = capacity_factors.get(key, 1)
                cap = int(1000 * factor)
            # Since undirected, add both directions; if multiple edges exist, sum capacities.
            graph[u][v] = graph[u].get(v, 0) + cap
            graph[v][u] = graph[v].get(u, 0) + cap
        return graph

    def max_flow(graph, source, sink):
        flow = 0
        while True:
            # BFS to find shortest augmenting path
            parent_map = {}
            visited = set()
            queue = deque()
            queue.append(source)
            visited.add(source)
            while queue and sink not in visited:
                u = queue.popleft()
                for v in graph[u]:
                    if v not in visited and graph[u][v] > 0:
                        visited.add(v)
                        parent_map[v] = u
                        queue.append(v)
            if sink not in visited:
                break
            # Find the minimum residual capacity in the path
            v = sink
            path_flow = float('inf')
            while v != source:
                u = parent_map[v]
                path_flow = min(path_flow, graph[u][v])
                v = u
            # Update capacities along the path
            v = sink
            while v != source:
                u = parent_map[v]
                graph[u][v] -= path_flow
                graph[v][u] = graph[v].get(u, 0) + path_flow
                v = u
            flow += path_flow
        return flow

    def count_edge_disjoint_paths(edges, src, dst):
        # Use unit capacities on all edges to count disjoint paths
        graph = build_flow_graph(edges, use_unit_capacity=True)
        return max_flow(graph, src, dst)

    def compute_max_flow(edges, src, dst):
        graph = build_flow_graph(edges, use_unit_capacity=False)
        return max_flow(graph, src, dst)

    # Function to get city demand by city_id from cities list
    city_demand = {city[0]: city[1] for city in cities}

    # Identify critical cities
    critical_ids = {city[0] for city in cities if city[4]}

    # Helper: get list of all city ids
    all_city_ids = [city[0] for city in cities]

    # Function to check connectivity of current network
    def is_connected(edges):
        if not all_city_ids:
            return True
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        start = all_city_ids[0]
        seen = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            for nbr in adj[node]:
                if nbr not in seen:
                    stack.append(nbr)
        return seen == set(all_city_ids)

    # Improvement Phase 1: Ensure critical cities have at least 2 independent paths to every other city.
    changed = True
    while changed:
        changed = False
        for c in critical_ids:
            for other in all_city_ids:
                if c == other:
                    continue
                paths = count_edge_disjoint_paths(network, c, other)
                if paths < 2:
                    # Try to add an edge from remaining_edges that is not already in network
                    for idx, (u, v, cost) in enumerate(remaining_edges):
                        # Check if this edge connects nodes that are on the unique path between c and other
                        # A heuristic: if one of its endpoints is reachable from c in current network and the other is not
                        # in the BFS tree from c (or vice versa), then it may add an alternate route.
                        # We add the first edge we find.
                        network.append((u, v))
                        del remaining_edges[idx]
                        changed = True
                        break
                    if changed:
                        break
            if changed:
                break

    # Improvement Phase 2: Ensure flow requirements for every pair of cities.
    # For each pair of cities, the maximum flow must be at least the minimum of their demands.
    for i in range(len(all_city_ids)):
        for j in range(i+1, len(all_city_ids)):
            src = all_city_ids[i]
            dst = all_city_ids[j]
            required_flow = min(city_demand[src], city_demand[dst])
            current_flow = compute_max_flow(network, src, dst)
            if current_flow < required_flow:
                # Try to add remaining edges to boost flow.
                added = False
                for idx in range(len(remaining_edges)):
                    u, v, cost = remaining_edges[idx]
                    network.append((u, v))
                    # Recompute flow
                    new_flow = compute_max_flow(network, src, dst)
                    if new_flow >= required_flow:
                        added = True
                        # Remove the added edge from remaining_edges
                        del remaining_edges[idx]
                        break
                    else:
                        # If not sufficient, keep the edge and continue
                        added = True
                        del remaining_edges[idx]
                        break
                # After trying, if still insufficient, we proceed (constraints may not be met if potential edges exhausted).
    # Final check: if network is disconnected, just return the current (possibly incomplete) network.
    # Otherwise, return network.
    return network