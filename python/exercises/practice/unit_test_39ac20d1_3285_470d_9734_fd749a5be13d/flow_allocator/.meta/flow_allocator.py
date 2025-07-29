import heapq

def allocate_flow(nodes, commodities, edges, T, capacity, cost):
    # Basic validation
    if not nodes or not edges:
        raise ValueError("No feasible solution found")
    node_set = set(nodes)
    for c in commodities:
        src, dst, demand = c
        if src not in node_set or dst not in node_set:
            raise ValueError("No feasible solution found")
        if demand <= 0:
            raise ValueError("No feasible solution found")

    # Initialize remaining capacities for each edge at each time step.
    rem_cap = {}
    for (u, v) in edges:
        for t in range(T):
            cap_val = capacity(u, v, t)
            rem_cap[(u, v, t)] = cap_val

    # This will store the final allocation for each commodity.
    # allocation[commodity_index] = { (u, v, t): flow, ... }
    allocation = {}
    
    # For each commodity, allocate flows greedily based on cheapest path in some time step.
    for idx, (src, dst, demand) in enumerate(commodities):
        remaining_demand = demand
        allocation[idx] = {}
        
        # Continue until the commodity's demand is fully satisfied.
        while remaining_demand > 0:
            best_total_cost = None
            best_path = None
            best_time = None
            best_bottleneck = None
            
            # For each time step, try to find a cheapest path from src to dst.
            for t in range(T):
                path, total_cost, bottleneck = _dijkstra(nodes, edges, rem_cap, src, dst, t, cost)
                if path is not None:
                    # If found, check if cost is better
                    if best_total_cost is None or total_cost < best_total_cost:
                        best_total_cost = total_cost
                        best_path = path
                        best_time = t
                        best_bottleneck = bottleneck
            
            # If no path is found in any time step, no feasible solution.
            if best_path is None:
                raise ValueError("No feasible solution found")
            
            # Determine the flow to allocate along the chosen path.
            flow_alloc = min(remaining_demand, best_bottleneck)
            
            # Update allocation for this commodity.
            # best_path is a list of nodes constituting the path.
            # Convert it to edges: (node[i], node[i+1], best_time)
            for i in range(len(best_path) - 1):
                edge_key = (best_path[i], best_path[i+1], best_time)
                allocation[idx][edge_key] = allocation[idx].get(edge_key, 0) + flow_alloc
                # Update remaining capacity for this edge at this time step.
                rem_cap[edge_key] -= flow_alloc
            
            remaining_demand -= flow_alloc

    return allocation

def _dijkstra(nodes, edges, rem_cap, src, dst, t, cost_func):
    # Build graph for time t where capacity > 0.
    # Represent graph as: graph[u] = list of (v, edge_cost)
    graph = {}
    for u in nodes:
        graph[u] = []
    for (u, v) in edges:
        cap = rem_cap.get((u, v, t), 0)
        if cap > 0:
            # For linear cost function, we evaluate per unit cost with flow=1.
            edge_cost = cost_func(u, v, t, 1)
            graph[u].append((v, edge_cost, cap))
    
    # Standard Dijkstra initialization.
    dist = {node: float('inf') for node in nodes}
    prev = {node: None for node in nodes}
    # For bottleneck value along path, store the minimum residual capacity encountered.
    bottleneck = {node: 0 for node in nodes}
    dist[src] = 0
    bottleneck[src] = float('inf')
    heap = [(0, src)]
    
    while heap:
        curr_dist, u = heapq.heappop(heap)
        if curr_dist > dist[u]:
            continue
        if u == dst:
            break
        for v, edge_cost, cap in graph[u]:
            alt = curr_dist + edge_cost
            # The new bottleneck is the minimum of the current bottleneck and this edge's capacity.
            new_bottle = min(bottleneck[u], cap)
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                bottleneck[v] = new_bottle
                heapq.heappush(heap, (alt, v))
    
    if dist[dst] == float('inf'):
        return None, None, None

    # Reconstruct path from src to dst.
    path = []
    node = dst
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return path, dist[dst], bottleneck[dst]