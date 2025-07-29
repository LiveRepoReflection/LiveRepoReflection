import heapq

def find_routes(N, edges, requests):
    # Build graph structure with edge indices for updating capacity.
    graph = {u: [] for u in range(N)}
    # Create a list to keep track of remaining capacity for each edge.
    edge_remaining = []
    for idx, (u, v, time, capacity) in enumerate(edges):
        graph[u].append((v, time, idx))
        edge_remaining.append(capacity)

    # This will store the route (list of nodes) for each request.
    result_routes = []

    # Process each request in the order given.
    # For each request, find the shortest route (in terms of travel time)
    # from 0 to destination that meets the deadline and with sufficient residual capacity.
    for request in requests:
        destination, vehicles_required, deadline = request
        route, total_time = dijkstra(0, destination, N, graph, edge_remaining, vehicles_required)
        if route is None or total_time > deadline:
            return None
        # Update the residual capacities along the found route.
        # Reconstruct the edges used in the route.
        for u, v in zip(route, route[1:]):
            # Find the edge used from u to v that satisfies capacity requirement.
            found = False
            for neighbor, travel_time, edge_idx in graph[u]:
                if neighbor == v and edge_remaining[edge_idx] >= vehicles_required:
                    # Deduct the vehicles.
                    edge_remaining[edge_idx] -= vehicles_required
                    found = True
                    break
            if not found:
                # This should not happen as the path was computed with capacity check.
                return None
        result_routes.append(route)
    return result_routes

def dijkstra(start, destination, N, graph, edge_remaining, vehicles_required):
    # Initialize distances and predecessor dictionary.
    dist = [float('inf')] * N
    prev = [None] * N  # each entry is a tuple (prev_node, edge_idx)
    dist[start] = 0
    # Priority queue: (current cost, current node)
    pq = [(0, start)]
    while pq:
        current_time, u = heapq.heappop(pq)
        if current_time > dist[u]:
            continue
        if u == destination:
            break
        for v, travel_time, edge_idx in graph[u]:
            if edge_remaining[edge_idx] < vehicles_required:
                # Not enough capacity on this edge.
                continue
            new_time = current_time + travel_time
            if new_time < dist[v]:
                dist[v] = new_time
                prev[v] = (u, edge_idx)
                heapq.heappush(pq, (new_time, v))
    if dist[destination] == float('inf'):
        return None, None
    # Reconstruct path from destination back to start.
    path = []
    curr = destination
    while curr is not None:
        path.append(curr)
        if curr == start:
            break
        prev_info = prev[curr]
        if prev_info is None:
            break
        curr = prev_info[0]
    path.reverse()
    return path, dist[destination]