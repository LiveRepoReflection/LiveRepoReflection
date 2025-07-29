def optimize_routes(graph, vehicle_routes, depot, traffic_prediction):
    def compute_travel_time(u, v, current_time):
        # Compute travel time using the provided traffic_prediction function.
        travel_time = traffic_prediction(u, v, current_time)
        # Validate that travel time is a non-negative integer.
        if not isinstance(travel_time, int) or travel_time < 0:
            raise ValueError(f"Invalid travel time from {u} to {v} at time {current_time}.")
        return travel_time

    optimized_routes = []
    for deliveries in vehicle_routes:
        # Start at the depot at time 0.
        current_node = depot
        current_time = 0
        route = [[depot, current_time]]
        # Make a mutable copy of delivery points to visit.
        remaining = deliveries.copy()
        
        # If there are no delivery points, simply return to the depot.
        if not remaining:
            travel_time = compute_travel_time(current_node, depot, current_time)
            current_time += travel_time
            route.append([depot, current_time])
            optimized_routes.append(route)
            continue

        # Use a greedy heuristic: from the current node, choose the next delivery with minimal travel time.
        while remaining:
            next_node = None
            min_time = None
            # Evaluate travel time to each remaining delivery point.
            for candidate in remaining:
                travel_time = compute_travel_time(current_node, candidate, current_time)
                if min_time is None or travel_time < min_time:
                    min_time = travel_time
                    next_node = candidate
            if next_node is None:
                raise ValueError("No valid edge found for next delivery point.")
            # Travel to the chosen delivery point.
            current_time += min_time
            route.append([next_node, current_time])
            current_node = next_node
            remaining.remove(next_node)
        # After visiting all delivery points, return to the depot.
        travel_time = compute_travel_time(current_node, depot, current_time)
        current_time += travel_time
        route.append([depot, current_time])
        optimized_routes.append(route)
    return optimized_routes

if __name__ == '__main__':
    # Example usage of optimize_routes via a simple simulation.
    # This block can be used for manual testing.
    graph = {
        0: [(1, 10), (2, 15)],
        1: [(0, 10), (2, 9)],
        2: [(0, 15), (1, 9)]
    }
    
    def traffic_prediction(u, v, current_time):
        # Simple traffic prediction: lookup the base travel time from the graph.
        if u not in graph:
            raise ValueError(f"Node {u} has no outgoing edges.")
        for neighbor, base_time in graph[u]:
            if neighbor == v:
                # Add slight variation based on current time.
                return base_time + (current_time % 60) // 10
        raise ValueError(f"Edge from {u} to {v} not found in the graph.")
    
    vehicle_routes = [
        [1, 2],
        [2]
    ]
    depot = 0
    routes = optimize_routes(graph, vehicle_routes, depot, traffic_prediction)
    for r in routes:
        print(r)