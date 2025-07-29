import heapq

def shortest_path(graph, start, end):
    # Dijkstra algorithm to find shortest path (by travel time) from start to end.
    # Returns a tuple (path, total_cost) where path is a list of nodes.
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        if node == end:
            break
        for neighbor, weight in graph.get(node, []):
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))
    # Reconstruct path
    path = []
    cur = end
    if dist[end] == float('inf'):
        return None, float('inf')
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path, dist[end]

def find_nearest_charging(current, graph, charging_stations):
    # Dijkstra to find the nearest charging station from the current node.
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[current] = 0
    heap = [(0, current)]
    nearest_station = None
    while heap:
        d, node = heapq.heappop(heap)
        if node in charging_stations:
            nearest_station = node
            break
        if d > dist[node]:
            continue
        for neighbor, weight in graph.get(node, []):
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))
    if nearest_station is None:
        return None, None, float('inf')
    # Reconstruct path to nearest charging station
    path = []
    cur = nearest_station
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return nearest_station, path, dist[nearest_station]

def simulate_segment(start, end, start_time, current_battery, graph, vehicle_battery_capacity, battery_consumption_rate, charging_time_per_unit, charging_stations):
    """
    Simulate traveling from start to end along the shortest path.
    Insert charging actions if necessary.
    Returns (instructions, final_time, final_battery) where instructions is a list of tuples.
    Each tuple is (node_id, time, action, package_id) with action "idle" for movements.
    """
    instructions = []
    # Compute shortest path from start to end
    path, total_cost = shortest_path(graph, start, end)
    if path is None or len(path) == 0:
        # This should not happen as graph is fully connected per the problem
        return instructions, start_time, current_battery

    current_time = start_time
    current_node = path[0]
    # We assume the starting node is already recorded. Process each edge in the path.
    for i in range(1, len(path)):
        next_node = path[i]
        # Get travel time from current_node to next_node
        edge_cost = None
        for neighbor, t in graph[current_node]:
            if neighbor == next_node:
                edge_cost = t
                break
        if edge_cost is None:
            # Should not happen if path is correct
            edge_cost = 0

        # Check battery for the upcoming edge (consider consumption rate)
        required = edge_cost * battery_consumption_rate
        if current_battery < required:
            # If current node is a charging station, charge until full.
            if current_node in charging_stations:
                charge_units = vehicle_battery_capacity - current_battery
                charging_time = charge_units * charging_time_per_unit
                current_time += charging_time
                instructions.append((current_node, current_time, "charge", -1))
                current_battery = vehicle_battery_capacity
            else:
                # If not at a charging station, find the nearest one.
                station, detour_path, detour_cost = find_nearest_charging(current_node, graph, charging_stations)
                if station is None:
                    # Cannot detour so break (should not happen with valid input)
                    raise Exception("No charging station reachable, route invalid.")
                # Simulate traveling detour path from current_node to station.
                # Skip the first node because it's current_node.
                for j in range(1, len(detour_path)):
                    inter_next = detour_path[j]
                    edge_cost_detour = None
                    for neighbor, t in graph[current_node]:
                        if neighbor == inter_next:
                            edge_cost_detour = t
                            break
                    if edge_cost_detour is None:
                        edge_cost_detour = 0
                    required_detour = edge_cost_detour * battery_consumption_rate
                    if current_battery < required_detour:
                        # This should not occur if the detour path was computed correctly.
                        raise Exception("Battery insufficient even for detour.")
                    current_time += edge_cost_detour
                    current_battery -= required_detour
                    current_node = inter_next
                    instructions.append((current_node, current_time, "idle", -1))
                # Now at a charging station, charge.
                charge_units = vehicle_battery_capacity - current_battery
                charging_time = charge_units * charging_time_per_unit
                current_time += charging_time
                instructions.append((current_node, current_time, "charge", -1))
                current_battery = vehicle_battery_capacity
                # After detour charging, recompute shortest path from current_node to next_node.
                sub_path, sub_cost = shortest_path(graph, current_node, next_node)
                if sub_path is None or len(sub_path) == 0:
                    raise Exception("No path found after charging.")
                # Process the sub_path edges one by one.
                # Remove the starting node since it's current_node.
                for k in range(1, len(sub_path)):
                    seg_next = sub_path[k]
                    seg_cost = None
                    for neighbor, t in graph[current_node]:
                        if neighbor == seg_next:
                            seg_cost = t
                            break
                    if seg_cost is None:
                        seg_cost = 0
                    required_seg = seg_cost * battery_consumption_rate
                    if current_battery < required_seg:
                        # Ideally, should not happen because we just charged.
                        raise Exception("Battery error in sub path simulation.")
                    current_time += seg_cost
                    current_battery -= required_seg
                    current_node = seg_next
                    instructions.append((current_node, current_time, "idle", -1))
                continue  # Continue to next iteration of main path after detour recharge
        # Travel normally along the edge.
        current_time += edge_cost
        current_battery -= required
        current_node = next_node
        instructions.append((current_node, current_time, "idle", -1))
        # If arriving before the end and battery becomes exactly 0 at a charging station and more travel remains,
        # then simulate charging.
        if i < len(path) - 1 and current_battery == 0 and current_node in charging_stations:
            charge_units = vehicle_battery_capacity - current_battery
            charging_time = charge_units * charging_time_per_unit
            current_time += charging_time
            instructions.append((current_node, current_time, "charge", -1))
            current_battery = vehicle_battery_capacity
    return instructions, current_time, current_battery

def solve(N, M, graph, vehicle_start_locations, delivery_requests, vehicle_capacity, charging_stations, vehicle_battery_capacity, battery_consumption_rate, charging_time_per_unit):
    """
    Solves the optimal autonomous vehicle fleet routing problem.
    Returns a list of routes, one per vehicle.
    Each route is a list of tuples (node_id, time, action, package_id).
    """
    # Initialize state for each vehicle: current location, current time, current battery, route instructions.
    vehicles = []
    for loc in vehicle_start_locations:
        # Assume vehicles start fully charged.
        vehicles.append({
            "location": loc,
            "time": 0,
            "battery": vehicle_battery_capacity,
            "route": [(loc, 0, "idle", -1)]
        })
    
    # Assign delivery requests round-robin
    for pkg_id, request in enumerate(delivery_requests):
        pickup_node, dropoff_node, package_size, time_window_start, time_window_end = request
        # Assign vehicle in round-robin manner
        vehicle_index = pkg_id % N
        vehicle = vehicles[vehicle_index]
        # Simulate travel from current location to pickup_node.
        seg_instructions, arrival_time, battery_after = simulate_segment(
            vehicle["location"],
            pickup_node,
            vehicle["time"],
            vehicle["battery"],
            graph,
            vehicle_battery_capacity,
            battery_consumption_rate,
            charging_time_per_unit,
            charging_stations
        )
        # Append segment instructions (skip the first instruction if it's duplicate of current location).
        if seg_instructions and seg_instructions[0][0] == vehicle["location"]:
            vehicle["route"].extend(seg_instructions[1:])
        else:
            vehicle["route"].extend(seg_instructions)
        # If arrival is earlier than the pickup window, wait until time_window_start.
        current_time = arrival_time
        if current_time < time_window_start:
            current_time = time_window_start
            vehicle["route"].append((pickup_node, current_time, "idle", -1))
        # Add pickup event.
        vehicle["route"].append((pickup_node, current_time, "pickup", pkg_id))
        # Update vehicle state.
        vehicle["location"] = pickup_node
        vehicle["time"] = current_time
        vehicle["battery"] = battery_after

        # Simulate travel from pickup_node to dropoff_node.
        seg_instructions, arrival_time, battery_after = simulate_segment(
            vehicle["location"],
            dropoff_node,
            vehicle["time"],
            vehicle["battery"],
            graph,
            vehicle_battery_capacity,
            battery_consumption_rate,
            charging_time_per_unit,
            charging_stations
        )
        if seg_instructions and seg_instructions[0][0] == vehicle["location"]:
            vehicle["route"].extend(seg_instructions[1:])
        else:
            vehicle["route"].extend(seg_instructions)
        # If arrival is before dropoff (and within time window), no waiting is needed.
        current_time = arrival_time
        # Add dropoff event.
        vehicle["route"].append((dropoff_node, current_time, "dropoff", pkg_id))
        # Update vehicle state.
        vehicle["location"] = dropoff_node
        vehicle["time"] = current_time
        vehicle["battery"] = battery_after
    
    # Format routes: Return list of routes in order of vehicles.
    routes = []
    for vehicle in vehicles:
        routes.append(vehicle["route"])
    return routes