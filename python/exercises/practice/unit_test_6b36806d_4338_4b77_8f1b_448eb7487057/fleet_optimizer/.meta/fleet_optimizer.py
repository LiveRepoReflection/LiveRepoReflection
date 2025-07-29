import heapq

def find_path(city_graph, congestion_factor, origin, destination, start_time):
    # Each state: (current_time, current_node, path, total_energy)
    # We'll use current_time as the primary cost for Dijkstra.
    heap = [(start_time, origin, [origin], 0.0)]
    best_times = {origin: start_time}
    
    while heap:
        current_time, node, path, total_energy = heapq.heappop(heap)
        if node == destination:
            return path, total_energy, current_time
        # If we have already found a better time for this node, skip.
        if current_time > best_times.get(node, float('inf')):
            continue
        for (next_node, base_time, energy_rate) in city_graph.get(node, []):
            # Calculate congestion factor for this edge based on current time.
            cf = congestion_factor(node, next_node, current_time)
            travel_time = base_time * cf
            energy_cost = base_time * energy_rate * cf
            next_time = current_time + travel_time
            next_energy = total_energy + energy_cost
            if next_time < best_times.get(next_node, float('inf')):
                best_times[next_node] = next_time
                heapq.heappush(heap, (next_time, next_node, path + [next_node], next_energy))
    return None

def plan_routes(city_graph, congestion_factor, av_requests, max_avs, total_energy_budget):
    """
    Plans routes for autonomous vehicles given the city graph, congestion factor function,
    AV requests, and resource limits. Returns a list of routes (each route is a list of node IDs)
    for each AV request in the same order as provided, or None if no feasible solution exists.
    """
    # List to store each route's info: (departure_time, arrival_time, route, energy)
    scheduled_routes = []
    overall_energy = 0.0

    # Process requests in the order they are provided
    for request in av_requests:
        origin, destination, departure_time, priority = request
        # Find path from origin to destination starting at departure_time
        result = find_path(city_graph, congestion_factor, origin, destination, departure_time)
        if result is None:
            return None
        route, energy_used, arrival_time = result
        overall_energy += energy_used
        scheduled_routes.append((departure_time, arrival_time, route, energy_used))
    
    # Check total energy consumption resource constraint
    if overall_energy > total_energy_budget:
        return None

    # Check active AVs constraint: at any moment, number of vehicles in transit must not exceed max_avs.
    # Build events: each route gives a departure event and an arrival event.
    events = []
    for dep, arr, _, _ in scheduled_routes:
        events.append((dep, 1))
        events.append((arr, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    
    active = 0
    for time, change in events:
        active += change
        if active > max_avs:
            return None

    # Return only the routes in the order of av_requests (maintaining same order as scheduled_routes)
    return [route for (_, _, route, _) in scheduled_routes]