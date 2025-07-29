import heapq
from collections import defaultdict

def design_network(locations, potential_routes, budget, max_latency):
    # Check for negative cost values.
    for u, v, cost, capacity in potential_routes:
        if cost < 0:
            raise ValueError("Negative cost not allowed")

    # Filter potential routes based on the latency constraint.
    filtered_routes = []
    for u, v, cost, capacity in potential_routes:
        if (1 / capacity) <= max_latency:
            filtered_routes.append((u, v, cost, capacity))

    # Build graph and an edge lookup map.
    graph = defaultdict(list)
    edge_map = {}
    all_nodes = set()
    for u, v, cost, capacity in filtered_routes:
        graph[u].append((v, cost))
        graph[v].append((u, cost))
        key = frozenset((u, v))
        edge_map[key] = (cost, capacity)
        all_nodes.add(u)
        all_nodes.add(v)

    # Define required nodes as those with nonzero demand.
    required_nodes = set()
    for loc in locations:
        if loc.get('demand', 0) != 0:
            required_nodes.add(loc['id'])

    # Check connectivity of required nodes within the filtered graph.
    if required_nodes:
        visited = set()
        start = next(iter(required_nodes))
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for neighbor, _ in graph[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
        if not required_nodes.issubset(visited):
            raise ValueError("Required nodes are not fully connected")

    if not required_nodes:
        return []

    # Dijkstra's algorithm to compute shortest paths from source to all nodes.
    def dijkstra(src):
        dist = {node: float('inf') for node in all_nodes}
        prev = {node: None for node in all_nodes}
        dist[src] = 0
        heap = [(0, src)]
        while heap:
            d, node = heapq.heappop(heap)
            if d > dist[node]:
                continue
            for neighbor, cost in graph[node]:
                new_dist = d + cost
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = node
                    heapq.heappush(heap, (new_dist, neighbor))
        return dist, prev

    # Build a complete graph on the required nodes using shortest paths.
    complete_graph = defaultdict(dict)
    # Store the actual paths for reconstruction.
    paths = {}
    req_list = list(required_nodes)
    for i in range(len(req_list)):
        src = req_list[i]
        dist, prev = dijkstra(src)
        for j in range(i + 1, len(req_list)):
            dst = req_list[j]
            if dist[dst] == float('inf'):
                continue
            complete_graph[src][dst] = dist[dst]
            complete_graph[dst][src] = dist[dst]
            # Reconstruct the shortest path from src to dst.
            path = []
            cur = dst
            while cur != src:
                path.append(cur)
                cur = prev[cur]
            path.append(src)
            path.reverse()
            paths[(src, dst)] = path
            paths[(dst, src)] = list(reversed(path))

    # Compute a Minimum Spanning Tree (MST) on the complete graph of required nodes.
    mst_edges = []
    in_mst = set()
    in_mst.add(req_list[0])
    edge_candidates = []
    for neighbor, weight in complete_graph[req_list[0]].items():
        heapq.heappush(edge_candidates, (weight, req_list[0], neighbor))
    while len(in_mst) < len(required_nodes):
        if not edge_candidates:
            break
        weight, u, v = heapq.heappop(edge_candidates)
        if v in in_mst:
            continue
        in_mst.add(v)
        mst_edges.append((u, v))
        for neighbor, w in complete_graph[v].items():
            if neighbor not in in_mst:
                heapq.heappush(edge_candidates, (w, v, neighbor))

    # Reconstruct the set of routes (edges) from the MST using the precomputed shortest paths.
    selected_routes_set = set()
    for u, v in mst_edges:
        path = paths.get((u, v))
        if not path or len(path) < 2:
            continue
        for i in range(len(path) - 1):
            edge = frozenset((path[i], path[i + 1]))
            selected_routes_set.add(edge)

    # Compute the total cost of the selected routes.
    total_cost = 0
    for edge in selected_routes_set:
        if edge in edge_map:
            total_cost += edge_map[edge][0]
        else:
            raise ValueError("Edge missing in edge map")
    if total_cost > budget:
        raise ValueError("Budget constraint cannot be met")

    # Return the list of selected routes as tuples (sorted order).
    result = []
    for edge in selected_routes_set:
        u, v = sorted(list(edge))
        result.append((u, v))
    return result