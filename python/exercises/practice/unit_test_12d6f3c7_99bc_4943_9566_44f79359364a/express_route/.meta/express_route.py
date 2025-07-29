import heapq
import math

def find_best_path(start, end, max_time, adj):
    # Modified Dijkstra: state = (total_cost, total_time, current_node, path)
    # path: list of edges used; each edge is a tuple (u, v, travel_time, op_cost, capacity)
    heap = [(0.0, 0, start, [])]
    visited = {}  # (node, time) -> cost
    best = None

    while heap:
        cost, ttime, node, path = heapq.heappop(heap)
        if node == end:
            best = (cost, ttime, path)
            return best
        # If we've seen this state with lower cost, skip.
        if (node, ttime) in visited and visited[(node, ttime)] <= cost:
            continue
        visited[(node, ttime)] = cost
        for edge in adj.get(node, []):
            u, v, travel_time, op_cost, capacity = edge
            new_time = ttime + travel_time
            if new_time > max_time:
                continue
            new_cost = cost + travel_time * op_cost
            new_path = path + [edge]
            heapq.heappush(heap, (new_cost, new_time, v, new_path))
    return None

def optimize_network(N, graph, demand, train_capacity, time_windows, SLA_percentage, fixed_cost_per_train):
    # Build adjacency list from graph: dict from node to list of edges.
    # Each edge is represented as a tuple: (start, end, travel_time, op_cost, capacity)
    adj = {}
    for edge in graph:
        u, v, travel_time, op_cost, capacity = edge
        if u not in adj:
            adj[u] = []
        adj[u].append((u, v, travel_time, op_cost, capacity))

    total_cost = 0.0
    edge_train_usage = {}  # key: edge tuple (u,v,travel_time,op_cost,capacity), value: total trains used

    # For every city pair with demand
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            required_passengers = demand[i][j]
            if required_passengers <= 0:
                continue
            # Compute minimum number of trains required to satisfy SLA for (i,j)
            # Only a fraction SLA_percentage of passengers have to be served at minimum.
            required_trains = math.ceil(SLA_percentage * required_passengers / train_capacity)
            # Determine max allowable travel time from time window.
            earliest_departure, latest_arrival = time_windows[i][j]
            max_time = latest_arrival - earliest_departure
            # Find best valid path from i to j that satisfies travel time constraint.
            result = find_best_path(i, j, max_time, adj)
            if result is None:
                return -1.0
            route_cost, route_time, path_edges = result
            # Calculate cost per train for this route: fixed cost plus operating cost along the route.
            per_train_cost = fixed_cost_per_train + route_cost
            total_cost += required_trains * per_train_cost
            # Record usage for each edge in the path.
            for edge in path_edges:
                # Edge key is the same tuple (u,v,travel_time,op_cost,capacity)
                if edge in edge_train_usage:
                    edge_train_usage[edge] += required_trains
                else:
                    edge_train_usage[edge] = required_trains

    # Check rail line capacity constraints.
    for edge, trains_used in edge_train_usage.items():
        u, v, travel_time, op_cost, capacity = edge
        if trains_used > capacity:
            return -1.0
    return total_cost