import heapq
import math

def dijkstra(graph, tolls, origin, destination):
    # Build adjacency list: node -> list of (neighbor, cost, edge_index)
    adj = {}
    for idx, edge in enumerate(graph['edges']):
        start = edge['start']
        end = edge['end']
        # cost = free_flow_time + toll on the edge
        cost = edge['free_flow_time'] + tolls[idx]
        if start not in adj:
            adj[start] = []
        adj[start].append((end, cost, idx))
    
    # Dijkstra algorithm
    # Distance dictionary: node -> (total_cost, path_edge_indices)
    dist = {node: (math.inf, []) for node in graph['nodes']}
    dist[origin] = (0, [])
    heap = [(0, origin, [])]
    while heap:
        cost_so_far, current, path = heapq.heappop(heap)
        if current == destination:
            return path
        if cost_so_far > dist[current][0]:
            continue
        for neighbor, edge_cost, edge_idx in adj.get(current, []):
            new_cost = cost_so_far + edge_cost
            if new_cost < dist[neighbor][0]:
                dist[neighbor] = (new_cost, path + [edge_idx])
                heapq.heappush(heap, (new_cost, neighbor, path + [edge_idx]))
    # If no path exists, return empty list.
    return []

def optimize_tolls(graph, od_pairs, T, max_toll):
    num_edges = len(graph['edges'])
    toll_matrix = []
    # For each time period, optimize tolls independently.
    # A simple iterative best-response heuristic is used.
    for t in range(T):
        # Start with initial tolls as zeros
        current_tolls = [0] * num_edges
        max_iterations = 5
        for _ in range(max_iterations):
            # Initialize flow on each edge to 0 for this iteration.
            flows = [0] * num_edges
            # For each OD pair, compute the shortest path using current tolls
            for od in od_pairs:
                origin = od['origin']
                destination = od['destination']
                demand = od['demand']
                path = dijkstra(graph, current_tolls, origin, destination)
                # If no valid path found, skip this OD pair.
                if not path:
                    continue
                for edge_idx in path:
                    flows[edge_idx] += demand
            # Update tolls: heuristic: toll = min(max_toll, round((flow/capacity)*max_toll))
            new_tolls = []
            converged = True
            for idx, edge in enumerate(graph['edges']):
                capacity = edge['capacity']
                flow = flows[idx]
                est_toll = int(round((flow / capacity) * max_toll)) if capacity > 0 else max_toll
                est_toll = min(max_toll, est_toll)
                new_tolls.append(est_toll)
                if est_toll != current_tolls[idx]:
                    converged = False
            current_tolls = new_tolls
            if converged:
                break
        toll_matrix.append(current_tolls)
    return toll_matrix