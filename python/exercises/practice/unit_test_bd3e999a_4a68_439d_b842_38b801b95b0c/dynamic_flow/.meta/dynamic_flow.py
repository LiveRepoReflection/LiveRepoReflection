from collections import deque
import copy

def solve_dynamic_flow(V, E, capacities, commodities, events, T):
    # Precompute effective capacities for each edge at each time step.
    # Start with the initial capacities provided.
    effective_caps = {}
    for edge in E:
        effective_caps[edge] = [capacities[edge][t] for t in range(T)]
    
    # Process events: For each event, update the capacity from the event time onward.
    # events: list of tuples (edge, t, new_capacity)
    # We sort events for deterministic behavior.
    events_sorted = sorted(events, key=lambda x: (x[0], x[1]))
    for ev in events_sorted:
        edge, t_event, new_cap = ev
        if edge not in effective_caps:
            continue
        for t in range(t_event, T):
            effective_caps[edge][t] = new_cap

    # Available capacities that we update as flows are assigned.
    avail = {edge: effective_caps[edge][:] for edge in E}

    # The solution flow dictionary: keys are (commodity_index, edge, time) and value is flow value.
    flow = {}

    # For each commodity, try to find a time step in which a full path from source to destination has enough capacity.
    for k, (src, dst, demand) in enumerate(commodities):
        path_found = False
        for t in range(T):
            path = bfs_find_path(V, E, avail, src, dst, demand, t)
            if path is not None:
                # Assign the flow along the found path at time t.
                for edge in path:
                    avail[edge][t] -= demand
                    flow[(k, edge, t)] = demand
                path_found = True
                break
        if not path_found:
            # If any commodity's demand cannot be routed, then no feasible solution exists.
            return {}
    return flow

def bfs_find_path(V, E, avail, src, dst, demand, t):
    # Build adjacency list based on available capacity at time t (only include those edges with capacity >= demand)
    adj = {v: [] for v in V}
    for edge in E:
        u, v = edge
        if avail[edge][t] >= demand:
            adj[u].append(edge)
    
    # Standard BFS to find any path from src to dst.
    queue = deque()
    queue.append(src)
    parent = {v: None for v in V}
    # record which edge was used to come to the vertex
    used_edge = {v: None for v in V}
    
    while queue:
        current = queue.popleft()
        if current == dst:
            # reconstruct path: list of edges in order from src to dst.
            path = []
            v = dst
            while v != src:
                edge_used = used_edge[v]
                path.append(edge_used)
                u, _ = edge_used
                v = u
            path.reverse()
            return path
        for edge in adj[current]:
            _, neighbor = edge
            if parent[neighbor] is None and neighbor != src:
                parent[neighbor] = current
                used_edge[neighbor] = edge
                queue.append(neighbor)
    return None