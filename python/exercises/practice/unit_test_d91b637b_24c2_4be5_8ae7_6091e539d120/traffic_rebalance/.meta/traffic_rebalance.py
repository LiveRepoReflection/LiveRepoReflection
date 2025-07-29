import math
import heapq

def optimal_traffic_rebalance(graph, vehicle_routes, K):
    # Build adjacency list and edge data dictionary.
    adj = {}
    edge_data = {}
    nodes = set()
    for u, v, cap, flow in graph:
        edge_data[(u, v)] = [cap, flow]
        if u not in adj:
            adj[u] = []
        adj[u].append(v)
        nodes.add(u)
        nodes.add(v)
    node_list = list(nodes)
    
    # Initialize vehicle status: False means not rerouted.
    rerouted = [False] * len(vehicle_routes)
    remaining_reroutes = K

    # Greedy iterative improvement.
    improvement_found = True
    while remaining_reroutes > 0 and improvement_found:
        best_net_improvement = 0
        best_vehicle_index = None
        best_default_path = None
        best_alt_path = None
        
        # Evaluate each vehicle that has not been rerouted.
        for i, (s, t) in enumerate(vehicle_routes):
            if rerouted[i]:
                continue
            default_path = _find_default_path(s, t, adj, edge_data, node_list)
            alt_path = _find_alt_path(s, t, adj, edge_data)
            if default_path is None or alt_path is None:
                continue
            # If the alternative path is identical to default, no improvement.
            if default_path == alt_path:
                continue

            # Compute total removal benefit on the default path.
            default_benefit = 0
            for (u, v) in default_path:
                cap, f = edge_data[(u, v)]
                if f > cap:
                    default_benefit += (2 * (f - cap) - 1)
            # Compute total addition cost on the alternative path.
            alt_addition = 0
            for (u, v) in alt_path:
                cap, f = edge_data[(u, v)]
                if f < cap:
                    alt_addition += 0
                else:
                    alt_addition += (2 * (f - cap) + 1)
            net_improvement = default_benefit - alt_addition
            if net_improvement > best_net_improvement:
                best_net_improvement = net_improvement
                best_vehicle_index = i
                best_default_path = default_path
                best_alt_path = alt_path

        if best_vehicle_index is None or best_net_improvement <= 0:
            improvement_found = False
            break
        
        # Perform the reroute for the selected vehicle.
        for (u, v) in best_default_path:
            edge_data[(u, v)][1] -= 1
        for (u, v) in best_alt_path:
            edge_data[(u, v)][1] += 1
        rerouted[best_vehicle_index] = True
        remaining_reroutes -= 1

    # Compute total congestion: sum of square of excess flow on each edge.
    total_congestion = 0
    for (u, v), (cap, f) in edge_data.items():
        if f > cap:
            total_congestion += (f - cap) ** 2
    return total_congestion

def _find_default_path(source, target, adj, edge_data, node_list):
    """
    Finds a path from source to target that maximizes the total removal benefit.
    Removal benefit on an edge = 2*(f - cap) - 1 if f > cap, else 0.
    This is done via a modified Bellman-Ford algorithm over simple paths (up to n-1 relaxations).
    """
    # Initialize: use -infinity for maximum benefit.
    benefit = {node: -math.inf for node in node_list}
    benefit[source] = 0
    predecessor = {node: None for node in node_list}
    
    # Relax edges |V|-1 times.
    for _ in range(len(node_list) - 1):
        updated = False
        for u in adj:
            if benefit[u] == -math.inf:
                continue
            for v in adj[u]:
                cap, f = edge_data[(u, v)]
                edge_benefit = (2 * (f - cap) - 1) if f > cap else 0
                if benefit[u] + edge_benefit > benefit[v]:
                    benefit[v] = benefit[u] + edge_benefit
                    predecessor[v] = u
                    updated = True
        if not updated:
            break

    if benefit[target] == -math.inf:
        return None
    
    # Reconstruct the path from source to target.
    path_nodes = []
    curr = target
    while curr != source:
        if predecessor[curr] is None:
            return None
        path_nodes.append(curr)
        curr = predecessor[curr]
    path_nodes.append(source)
    path_nodes.reverse()
    
    # Convert node path to list of edges.
    path_edges = []
    for i in range(len(path_nodes) - 1):
        path_edges.append((path_nodes[i], path_nodes[i+1]))
    return path_edges

def _find_alt_path(source, target, adj, edge_data):
    """
    Finds a path from source to target that minimizes the additional cost.
    Additional cost on an edge = 0 if f < cap, else 2*(f - cap) + 1.
    Uses Dijkstra's algorithm.
    """
    dist = {}
    prev = {}
    for u in adj:
        dist[u] = math.inf
        prev[u] = None
    # It's possible some nodes are not in adj if they have no outgoing edges.
    dist[source] = 0
    heap = [(0, source)]
    
    visited = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == target:
            break
        if u not in adj:
            continue
        for v in adj[u]:
            cap, f = edge_data[(u, v)]
            add_cost = 0 if f < cap else (2 * (f - cap) + 1)
            if dist[u] + add_cost < dist.get(v, math.inf):
                dist[v] = dist[u] + add_cost
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
                
    if dist.get(target, math.inf) == math.inf:
        return None
    
    # Reconstruct the path.
    path_nodes = []
    curr = target
    while curr is not None:
        path_nodes.append(curr)
        curr = prev.get(curr)
    path_nodes.reverse()
    
    # Convert to list of edges.
    path_edges = []
    for i in range(len(path_nodes) - 1):
        path_edges.append((path_nodes[i], path_nodes[i+1]))
    return path_edges