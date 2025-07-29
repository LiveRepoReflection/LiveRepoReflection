import heapq
import math

def solve_routing(graph, commodity_requests):
    num_nodes = graph["num_nodes"]
    edges = graph["edges"]
    
    # Build adjacency list: For each node, list of (neighbor, capacity)
    adj = {i: [] for i in range(num_nodes)}
    # Also keep a mapping of edge data for quick access: (u, v) -> capacity.
    edge_capacity = {}
    for (u, v, cap) in edges:
        adj[u].append(v)
        edge_capacity[(u, v)] = cap

    # Global dictionary to keep track of current flow on each edge.
    edge_flow = {}
    for (u, v, cap) in edges:
        edge_flow[(u, v)] = 0.0

    # The routing result dictionary.
    routing = {}

    # Process each commodity and its requests sequentially.
    for commodity_index, commodity in enumerate(commodity_requests):
        requests = commodity["requests"]
        for request_index, (src, dst, demand) in enumerate(requests):
            # Use Dijkstra's algorithm to select a single path that minimizes increase in congestion cost.
            dist = {i: math.inf for i in range(num_nodes)}
            prev = {i: None for i in range(num_nodes)}
            dist[src] = 0.0
            # Priority queue: (cost, node)
            heap = [(0.0, src)]
            while heap:
                current_cost, u = heapq.heappop(heap)
                if current_cost > dist[u]:
                    continue
                if u == dst:
                    break
                for v in adj.get(u, []):
                    # Compute additional cost for using edge (u, v) if demand is routed.
                    current_flow = edge_flow[(u, v)]
                    cap = edge_capacity[(u, v)]
                    # Compute new congestion cost after adding demand
                    new_excess = max(0.0, current_flow + demand - cap)
                    old_excess = max(0.0, current_flow - cap)
                    cost_increase = new_excess ** 2 - old_excess ** 2
                    new_cost = current_cost + cost_increase
                    if new_cost < dist[v]:
                        dist[v] = new_cost
                        prev[v] = u
                        heapq.heappush(heap, (new_cost, v))
            
            # Reconstruct path if exists.
            path = []
            if dist[dst] < math.inf:
                cur = dst
                while cur is not None:
                    path.append(cur)
                    cur = prev[cur]
                path.reverse()
                path_tuple = tuple(path)
                # Update global flows along the chosen path.
                for i in range(len(path) - 1):
                    edge = (path[i], path[i+1])
                    edge_flow[edge] += demand
                routing[(commodity_index, request_index)] = {path_tuple: float(demand)}
            else:
                # No path found; assign an empty routing.
                routing[(commodity_index, request_index)] = {}
    
    return routing