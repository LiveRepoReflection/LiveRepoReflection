def min_vehicles_required(N, graph, requests, C, T):
    # Precompute shortest paths using Floyd‐Warshall
    dist = [[float('inf')] * N for _ in range(N)]
    for i in range(N):
        dist[i][i] = 0
    for u in graph:
        for v, w in graph[u].items():
            if w < dist[u][v]:
                dist[u][v] = w
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Function to check if a group of requests can be served by one vehicle
    # within the time limit T and the capacity constraint C.
    def feasible_route(requests_group):
        m = len(requests_group)
        # Each request gives two stops: pickup and dropoff.
        # Format: (node, event_type, packages, request_id)
        # event_type: 0 for pickup, 1 for dropoff.
        stops = []
        for idx, (src, dst, packages) in enumerate(requests_group):
            stops.append((src, 0, packages, idx))
            stops.append((dst, 1, packages, idx))
        n_stops = len(stops)

        from functools import lru_cache

        # DFS with memoization to check for a valid ordering.
        # We use a bitmask to represent visited stops.
        # current_node: last visited node. Use -1 to indicate starting state (no travel cost incurred).
        # load: current number of packages in vehicle.
        # cost: current travel time cost accumulated.
        @lru_cache(maxsize=None)
        def dfs(visited_mask, current_node, load, cost):
            if visited_mask == (1 << n_stops) - 1:
                return cost <= T

            for i in range(n_stops):
                if visited_mask & (1 << i):
                    continue
                node, event_type, pkg, req_id = stops[i]
                # For dropoff events, ensure that the corresponding pickup has been visited.
                if event_type == 1:
                    # Find the pickup index for this request
                    pickup_index = None
                    for j in range(n_stops):
                        if stops[j][3] == req_id and stops[j][1] == 0:
                            pickup_index = j
                            break
                    if not (visited_mask & (1 << pickup_index)):
                        continue
                new_load = load + pkg if event_type == 0 else load - pkg
                if new_load > C:
                    continue
                # Calculate additional cost. If no current node, no travel cost is incurred.
                new_cost = cost if current_node == -1 else cost + dist[current_node][node]
                if new_cost > T:
                    continue
                new_mask = visited_mask | (1 << i)
                if dfs(new_mask, node, new_load, new_cost):
                    return True
            return False

        return dfs(0, -1, 0, 0)

    # Greedy algorithm to group requests into single vehicle routes.
    # This heuristic repeatedly picks a seed request and tries to add as many other
    # requests as possible into the same group if the combined route is feasible.
    requests_remaining = requests[:]
    # Sort requests by the individual travel time (shortest path) from source to destination.
    requests_remaining.sort(key=lambda r: dist[r[0]][r[1]])
    vehicle_count = 0

    while requests_remaining:
        group = []
        # Use the first remaining request as the seed for this vehicle route.
        seed = requests_remaining.pop(0)
        group.append(seed)
        changed = True
        while changed:
            changed = False
            # Create a copy of the current list since we may remove items.
            for candidate in requests_remaining[:]:
                tentative_group = group + [candidate]
                if feasible_route(tentative_group):
                    group.append(candidate)
                    requests_remaining.remove(candidate)
                    changed = True
        vehicle_count += 1

    return vehicle_count


if __name__ == '__main__':
    # Example usage for manual testing.
    N = 5
    graph = {
        0: {1: 10, 2: 15},
        1: {3: 20},
        2: {4: 25},
        3: {4: 10},
        4: {}
    }
    requests = [(0, 1, 5), (2, 3, 10), (1, 4, 15)]
    C = 20
    T = 60
    print(min_vehicles_required(N, graph, requests, C, T))