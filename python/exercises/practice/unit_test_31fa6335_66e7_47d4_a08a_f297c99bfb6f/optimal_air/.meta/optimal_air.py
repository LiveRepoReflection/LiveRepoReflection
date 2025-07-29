import heapq

def read_graph(graph_filename):
    graph = {}
    with open(graph_filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 4:
                continue
            src, dest, distance_str, noise_str = parts
            try:
                distance = float(distance_str)
                noise_factor = float(noise_str)
            except ValueError:
                continue
            if src not in graph:
                graph[src] = []
            # Append an edge tuple: (destination, cost factor, distance, noise_factor)
            # cost of edge is computed as distance * noise_factor.
            graph[src].append((dest, distance, noise_factor))
    return graph

def read_zones(zone_filename):
    zones = {}
    with open(zone_filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            zone_id, threshold_str = parts
            try:
                threshold = float(threshold_str)
            except ValueError:
                continue
            zones[zone_id] = threshold
    return zones

def read_flights(flight_filename):
    flights = []
    with open(flight_filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            flight_id, start, destination = parts
            flights.append((flight_id, start, destination))
    return flights

def calculate_penalty(base_cost, zone_threshold, penalty_multiplier):
    excess = base_cost - zone_threshold
    if excess > 0:
        return (excess ** 2) * penalty_multiplier
    return 0

def dijkstra(start, destination, graph, penalty_multiplier, zone_threshold):
    # State: (effective_cost, base_cost, current_node, hops, path)
    # hops counts number of nodes in the current path.
    # For a direct flight (hops == 2 and current_node==destination), penalty is applied.
    heap = []
    initial_state = (0.0, 0.0, start, 1, [start])
    heapq.heappush(heap, initial_state)
    
    # Use a dictionary to store best effective cost for a given (node, hops) combination
    best = {}
    while heap:
        effective_cost, base_cost, current, hops, path = heapq.heappop(heap)
        
        # If we have reached the destination, decide on cost based on number of hops.
        if current == destination:
            if hops == 2:
                penalty = calculate_penalty(base_cost, zone_threshold, penalty_multiplier)
                total_cost = base_cost + penalty
                # Ensure that the effective cost matches the recalculated value.
                if abs(total_cost - effective_cost) > 1e-9:
                    effective_cost = total_cost
            return effective_cost, path
        
        # If no outgoing edges, continue.
        if current not in graph:
            continue

        # Traverse neighbors.
        for neighbor, distance, noise_factor in graph[current]:
            edge_cost = distance * noise_factor
            new_base_cost = base_cost + edge_cost
            new_hops = hops + 1
            new_path = path + [neighbor]
            # If neighbor is destination and the path length is 2 (direct flight),
            # then apply penalty from zone threshold.
            if neighbor == destination and new_hops == 2:
                penalty = calculate_penalty(new_base_cost, zone_threshold, penalty_multiplier)
                new_effective = new_base_cost + penalty
            else:
                new_effective = new_base_cost

            state_key = (neighbor, new_hops)
            if state_key not in best or new_effective < best[state_key]:
                best[state_key] = new_effective
                heapq.heappush(heap, (new_effective, new_base_cost, neighbor, new_hops, new_path))
    return None

def find_optimal_paths(graph_filename, zone_filename, flight_filename, output_filename, penalty_multiplier):
    graph = read_graph(graph_filename)
    zones = read_zones(zone_filename)
    flights = read_flights(flight_filename)
    # For this implementation, if zones file is not empty, use the threshold of the first zone (by sorted key)
    if zones:
        first_zone = sorted(zones.keys())[0]
        zone_threshold = zones[first_zone]
    else:
        zone_threshold = float("inf")  # No penalty if no zone is defined

    results = []
    for flight_id, start, destination in flights:
        res = dijkstra(start, destination, graph, penalty_multiplier, zone_threshold)
        if res is None:
            results.append(f"{flight_id}: No path found")
        else:
            cost, path = res
            results.append(f"{flight_id}: " + ",".join(path))
    with open(output_filename, "w") as out_file:
        out_file.write("\n".join(results))