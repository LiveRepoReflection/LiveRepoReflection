import heapq

def optimize_traffic_flow(graph, demand, light_cycles, optimization_target):
    if optimization_target not in ("travel_time", "throughput"):
        raise ValueError("Invalid optimization target. Must be 'travel_time' or 'throughput'.")

    # Helper function: Compute travel time weight for an edge
    # travel_time = length / (speed_limit_in_mps), where speed_limit_in_mps = speed_limit * (5/18)
    def edge_travel_time(length, speed_limit):
        return (18 * length) / (5 * speed_limit)

    # Helper function: Dijkstra's algorithm to compute shortest path in terms of travel time
    def dijkstra_shortest_path(start, end, graph):
        heap = [(0, start, [start])]
        visited = set()
        while heap:
            curr_time, node, path = heapq.heappop(heap)
            if node == end:
                return path
            if node in visited:
                continue
            visited.add(node)
            for neighbor, properties in graph.get(node, {}).items():
                travel_time = edge_travel_time(properties["length"], properties["speed_limit"])
                new_time = curr_time + travel_time
                new_path = path + [neighbor]
                heapq.heappush(heap, (new_time, neighbor, new_path))
        return None

    # Initialize load for each intersection in the light_cycles
    intersection_load = {}
    for intersection in light_cycles:
        intersection_load[intersection] = 0

    # For each demand pair, find the shortest path and accumulate the vehicle flow for every intersection in that path.
    for (origin, destination), vehicles in demand.items():
        path = dijkstra_shortest_path(origin, destination, graph)
        if path is not None:
            for node in path:
                if node in intersection_load:
                    intersection_load[node] += vehicles

    # Determine maximum load to normalize the adjustment
    max_load = max(intersection_load.values()) if intersection_load else 0

    # Compute new light cycles based on the load.
    # Each cycle must have each interval >=5, and sum remains constant.
    new_light_cycles = {}
    for intersection, cycles in light_cycles.items():
        total_cycle = sum(cycles)
        # Reserved minimum for green and red: each must be at least 5 seconds.
        bonus_time = total_cycle - 10  # extra time that can be distributed
        load = intersection_load[intersection]
        if max_load > 0:
            normalized_load = load / max_load
        else:
            normalized_load = 0

        if optimization_target == "travel_time":
            # For travel time, allocate green time proportionally to the load.
            new_green = 5 + round(normalized_load * bonus_time)
        else:  # throughput
            # For throughput, be slightly more aggressive in increasing green time.
            adjusted_norm = normalized_load * 1.2
            if adjusted_norm > 1.0:
                adjusted_norm = 1.0
            new_green = 5 + round(adjusted_norm * bonus_time)
        new_red = total_cycle - new_green
        if new_red < 5:
            new_red = 5
            new_green = total_cycle - 5
        new_light_cycles[intersection] = [new_red, new_green]

    return new_light_cycles