import heapq

def allocate_flows(snapshot):
    num_nodes = snapshot['num_nodes']
    edges = snapshot['edges']
    commodities = snapshot['commodities']
    
    # Build residual graph: For each edge (u,v), store latency and residual capacity
    # The graph is directed.
    graph = {i: [] for i in range(num_nodes)}
    # We also maintain a dictionary for quick capacity lookup for an edge (u,v)
    residual = {}
    for u, v, capacity, latency in edges:
        graph[u].append((v, latency))
        residual[(u, v)] = capacity

    # Helper function: Dijkstra algorithm to find min latency path from source to target
    def dijkstra(source, target):
        # distances and parent pointers
        dist = {i: float('inf') for i in range(num_nodes)}
        parent = {}
        dist[source] = 0
        # (distance, node)
        heap = [(0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == target:
                break
            for v, latency in graph[u]:
                # Only consider edge if residual capacity > 0
                if residual.get((u, v), 0) > 0:
                    new_cost = d + latency
                    if new_cost < dist[v]:
                        dist[v] = new_cost
                        parent[v] = u
                        heapq.heappush(heap, (new_cost, v))
        if target not in parent and source != target:
            return None  # No path found
        # Reconstruct path from source to target as list of edges (u, v)
        path = []
        cur = target
        while cur != source:
            prev = parent.get(cur)
            # if prev is None, then source==target or no path exists
            if prev is None and cur != source:
                return None
            path.append((prev, cur))
            cur = prev
        path.reverse()
        return path

    # Process commodities by descending priority. Keep original indices.
    indexed_commodities = []
    for idx, commodity in enumerate(commodities):
        s, t, demand, priority = commodity
        indexed_commodities.append((priority, idx, s, t, demand))
    # Higher priority first (if same, earlier index first)
    indexed_commodities.sort(key=lambda x: (-x[0], x[1]))

    # Allocate flows for each commodity
    allocation = [0] * len(commodities)
    for prio, idx, s, t, demand in indexed_commodities:
        remaining = demand
        # While there's demand remaining and a path exists
        while remaining > 0:
            path = dijkstra(s, t)
            if path is None:
                break  # no more path available
            # Find the minimum residual capacity along the path
            path_capacity = min(residual[(u, v)] for u, v in path)
            flow = min(remaining, path_capacity)
            # Update residual capacities for each edge in the path
            for u, v in path:
                residual[(u, v)] -= flow
            remaining -= flow
            allocation[idx] += flow

    return allocation