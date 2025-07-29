import heapq
from collections import defaultdict

def optimize_network_flow(snapshot):
    nodes = snapshot["nodes"]
    links = snapshot["links"]
    commodities = snapshot["commodities"]

    # Build graph: mapping from source to list of (destination, link_info)
    graph = defaultdict(list)
    # Also maintain a dict for available capacities per link: keyed by (source, destination)
    available = {}
    # Store fixed attributes per link for cost and length lookup.
    link_attrs = {}
    
    for link in links:
        src = link["source"]
        dst = link["destination"]
        graph[src].append(dst)
        available[(src, dst)] = link["capacity"]
        link_attrs[(src, dst)] = {
            "length": link["length"],
            "cost": link["cost"]
        }
    
    # Allocations will be stored in a dictionary keyed by (commodity_id, source, destination)
    allocations_dict = defaultdict(int)
    
    # For each commodity, perform successive shortest path routing until full demand is met.
    for commodity in commodities:
        commodity_id = commodity["commodity_id"]
        origin = commodity["origin"]
        destination = commodity["destination"]
        demand = commodity["demand"]
        latency_weight = commodity["latency_weight"]
        remaining = demand
        
        while remaining > 0:
            # Use Dijkstra to find the shortest path from origin to destination 
            # in the residual network (links with positive available capacity).
            path, bottleneck = dijkstra_path(origin, destination, graph, available, link_attrs, latency_weight, nodes)
            if path is None:
                # If no path is found, break out (in practice, this should not happen for valid snapshots).
                break
            flow = min(remaining, bottleneck)
            # Update available capacities along the path
            for i in range(len(path) - 1):
                edge = (path[i], path[i+1])
                available[edge] -= flow
                # Aggregate allocation for this commodity and edge.
                allocations_dict[(commodity_id, edge[0], edge[1])] += flow
            remaining -= flow

    # Convert allocation dict to list of allocation dicts.
    allocations = []
    for (commodity_id, src, dst), flow in allocations_dict.items():
        allocations.append({
            "commodity_id": commodity_id,
            "source": src,
            "destination": dst,
            "flow": flow
        })
    return allocations

def dijkstra_path(start, end, graph, available, link_attrs, latency_weight, nodes):
    # Initialize distances and predecessor dictionaries.
    dist = {node: float('inf') for node in nodes}
    prev = {node: None for node in nodes}
    dist[start] = 0
    # Priority queue: (distance, node)
    heap = [(0, start)]
    
    while heap:
        cur_dist, u = heapq.heappop(heap)
        # If we reached the end node, we can stop.
        if u == end:
            break
        if cur_dist > dist[u]:
            continue
        for v in graph[u]:
            # Only consider edge if there is positive available capacity.
            if available[(u, v)] <= 0:
                continue
            # Compute cost for this edge: fixed cost + latency component.
            edge_cost = link_attrs[(u, v)]["cost"] + latency_weight * link_attrs[(u, v)]["length"]
            new_dist = cur_dist + edge_cost
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))
                
    if dist[end] == float('inf'):
        return None, 0
    
    # Reconstruct path from start to end.
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    
    # Determine bottleneck capacity along the path.
    bottleneck = float('inf')
    for i in range(len(path) - 1):
        edge = (path[i], path[i+1])
        bottleneck = min(bottleneck, available[edge])
    return path, bottleneck