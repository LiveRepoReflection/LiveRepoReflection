import heapq

def allocate_flow(num_nodes, edges, commodities):
    # Build graph with unique edge ids and corresponding residual capacities.
    graph = [[] for _ in range(num_nodes)]
    edge_list = []  # Each element is a dictionary with keys: u, v, capacity, cost, residual.
    for idx, (u, v, cap, cost) in enumerate(edges):
        edge_obj = {'u': u, 'v': v, 'capacity': cap, 'cost': cost, 'residual': cap}
        edge_list.append(edge_obj)
        graph[u].append(idx)

    # Prepare allocation dictionary.
    # Key: (u, v) tuple; Value: dictionary mapping commodity index to allocated flow.
    allocation = {}
    for (u, v, cap, cost) in edges:
        alloc_key = (u, v)
        if alloc_key not in allocation:
            allocation[alloc_key] = {}

    # Process each commodity independently using a successive shortest path approach.
    for commodity_index, (src, dst, demand) in enumerate(commodities):
        remaining = demand
        while remaining > 0:
            # Use Dijkstra's algorithm to find the lowest cost path from src to dst
            dist = [float('inf')] * num_nodes
            dist[src] = 0
            prev = [None] * num_nodes  # Stores the edge id used to reach node
            visited = [False] * num_nodes
            heap = [(0, src)]

            while heap:
                d, u = heapq.heappop(heap)
                if visited[u]:
                    continue
                visited[u] = True
                if u == dst:
                    break
                for edge_id in graph[u]:
                    edge = edge_list[edge_id]
                    v = edge['v']
                    if edge['residual'] > 0 and not visited[v]:
                        new_dist = d + edge['cost']
                        if new_dist < dist[v]:
                            dist[v] = new_dist
                            prev[v] = edge_id
                            heapq.heappush(heap, (new_dist, v))

            # If no path is found that can push flow, return None.
            if prev[dst] is None:
                return None

            # Reconstruct the path from src to dst and determine the bottleneck.
            path_edges = []
            cur = dst
            bottleneck = float('inf')
            while cur != src:
                edge_id = prev[cur]
                edge = edge_list[edge_id]
                bottleneck = min(bottleneck, edge['residual'])
                path_edges.append(edge_id)
                cur = edge['u']

            # Determine the amount of flow to push along this path.
            flow = min(remaining, bottleneck)

            # Update the residual capacities along the found path and record allocations.
            for edge_id in path_edges:
                edge = edge_list[edge_id]
                edge['residual'] -= flow
                key = (edge['u'], edge['v'])
                allocation.setdefault(key, {})
                allocation[key][commodity_index] = allocation[key].get(commodity_index, 0) + flow

            remaining -= flow

    return allocation