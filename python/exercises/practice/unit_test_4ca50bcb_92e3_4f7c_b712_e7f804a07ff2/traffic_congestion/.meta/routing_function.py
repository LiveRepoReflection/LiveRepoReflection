from math import floor

def routing_function(n, edges, current_vehicles, time_step):
    # Build mapping from each node to its outgoing edges (destination and capacity)
    out_edges = {i: [] for i in range(n)}
    for u, v, capacity in edges:
        out_edges[u].append((v, capacity))
    
    decision = {}
    
    for i in range(n):
        if not out_edges[i]:
            continue
        # Calculate total possible flow from node i without causing congestion
        total_possible = sum(cap for (_, cap) in out_edges[i])
        available = current_vehicles[i]
        # The maximum flow we can route without causing congestion is capped by total_possible.
        flow_to_route = available if available < total_possible else total_possible
        
        # Distribute flow proportionally to capacity using floor division
        assignments = {}
        total_assigned = 0
        for (v, cap) in out_edges[i]:
            flow = floor(flow_to_route * cap / total_possible)
            flow = min(flow, cap)
            assignments[v] = flow
            total_assigned += flow
        
        remainder = flow_to_route - total_assigned
        # Distribute any remaining vehicles greedily to edges with remaining capacity (slack)
        sorted_edges = sorted(out_edges[i], key=lambda x: x[1] - assignments[x[0]], reverse=True)
        for (v, cap) in sorted_edges:
            slack = cap - assignments[v]
            if slack > 0 and remainder > 0:
                extra = min(slack, remainder)
                assignments[v] += extra
                remainder -= extra
                if remainder == 0:
                    break
        
        for (v, cap) in out_edges[i]:
            decision[(i, v)] = assignments[v]
    
    return decision