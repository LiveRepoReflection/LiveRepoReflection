import heapq

def find_optimal_route(graph, edges, aev, origin, destination, departure_time, max_travel_time):
    battery_capacity = aev['battery_capacity']
    charging_rate = aev['charging_rate']
    energy_consumption_rate = aev['energy_consumption_rate']

    # Discretization helper: round battery level to 2 decimals
    def discretize(battery):
        return round(battery, 2)

    # Priority Queue: (current_time, current_node, battery_level, path)
    start_state = (departure_time, origin, discretize(aev['initial_charge']), [origin])
    heap = [start_state]
    
    # Visited dictionary to store the best time we've reached a state (node, battery)
    visited = {}
    
    # For charging, define a fixed time increment (in hours)
    charging_delta = 0.1

    while heap:
        current_time, current_node, battery, path = heapq.heappop(heap)
        
        # If we've reached destination within allowed travel time, return the path
        if current_node == destination:
            if current_time - departure_time <= max_travel_time:
                return path
            else:
                continue

        # If current time already exceeds max_travel_time, skip this branch
        if current_time - departure_time > max_travel_time:
            continue

        state_key = (current_node, battery)
        if state_key in visited and visited[state_key] <= current_time:
            continue
        visited[state_key] = current_time

        # For each neighbor from current node
        for neighbor in graph[current_node]['neighbors']:
            edge_key = (current_node, neighbor)
            if edge_key not in edges:
                continue
            edge_info = edges[edge_key]
            length = edge_info['length']
            speed_limit = edge_info['speed_limit']
            traffic_func = edge_info['traffic']
            # Determine effective speed at current time by calling traffic function
            effective_speed = traffic_func(current_time)
            # Ensure we don't exceed the speed limit (as guaranteed, but add min for safety)
            effective_speed = min(effective_speed, speed_limit)
            if effective_speed <= 0:
                continue  # Cannot traverse if no speed is available

            travel_time = length / effective_speed
            # Calculate energy consumption on this edge; using effective_speed for consumption rate
            energy_needed = energy_consumption_rate(effective_speed) * length

            # If there is enough battery to travel
            if battery >= energy_needed:
                new_battery = discretize(battery - energy_needed)
                new_time = current_time + travel_time
                # Skip if new_time exceeds max_travel_time relative to departure time
                if new_time - departure_time > max_travel_time:
                    continue
                new_path = path + [neighbor]
                new_state = (new_time, neighbor, new_battery, new_path)
                heapq.heappush(heap, new_state)

        # If current node has a charging station, consider charging action
        if graph[current_node]['charging_station'] and battery < battery_capacity:
            # Charge for a fixed delta time, compute new battery and time.
            new_time = current_time + charging_delta
            if new_time - departure_time > max_travel_time:
                # Charging would exceed max travel time, do not add this state.
                pass
            else:
                charged_amount = charging_rate * charging_delta
                new_battery = min(battery + charged_amount, battery_capacity)
                new_battery = discretize(new_battery)
                # Only add if battery improved
                if new_battery > battery:
                    new_state = (new_time, current_node, new_battery, path)
                    heapq.heappush(heap, new_state)

    return None