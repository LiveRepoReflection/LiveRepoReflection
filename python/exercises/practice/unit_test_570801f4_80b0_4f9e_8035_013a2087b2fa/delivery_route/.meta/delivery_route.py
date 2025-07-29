import heapq

def find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range):
    # Build graph as adjacency list: graph[u] = list of (v, length, congestion)
    graph = {i: [] for i in range(num_intersections)}
    for u, v, length, congestion in edges:
        graph[u].append((v, length, congestion))
    
    # Set of charging stations for quick membership testing
    charging_set = set(charging_stations)
    
    # Priority queue state: (objective, cumulative_time, current_node, battery_remaining, path)
    # objective = cumulative_time + cumulative_risk, where:
    #   cumulative_time is sum of travel times along the path
    #   cumulative_risk is sum of (length * congestion * risk_factor)
    start_state = (0.0, 0.0, start_intersection, max_range, [start_intersection])
    heap = [start_state]
    
    # To avoid reprocessing dominating states.
    # best_states[(node, battery)] = (objective, cumulative_time)
    best_states = {}
    best_states[(start_intersection, max_range)] = (0.0, 0.0)
    
    while heap:
        objective, curr_time, node, battery, path = heapq.heappop(heap)
        
        # If reached destination with valid time, return path.
        if node == end_intersection:
            return path
        
        # If current node is a charging station, consider recharging (if not already full)
        if node in charging_set and battery < max_range:
            new_battery = max_range
            # Recharging does not consume additional time or add risk
            new_state = (objective, curr_time, node, new_battery, path)
            state_key = (node, new_battery)
            if state_key not in best_states or (objective, curr_time) < best_states[state_key]:
                best_states[state_key] = (objective, curr_time)
                heapq.heappush(heap, new_state)
        
        # Explore neighbors
        for neighbor, length, congestion in graph[node]:
            # Edge can only be traversed if enough battery (max_range and battery are in meters)
            if battery < length:
                continue
            
            # Calculate travel time for the edge
            travel_time = (length * (1 + congestion)) / 30.0
            new_time = curr_time + travel_time
            if new_time > max_delivery_time:
                continue
            
            # Calculate congestion risk for the edge
            risk = length * congestion * risk_factor
            
            new_objective = objective + travel_time + risk
            new_battery = battery - length
            new_path = path + [neighbor]
            
            state_key = (neighbor, new_battery)
            # If we reached neighbor and this state is not dominated by a previous one, push it.
            if state_key not in best_states or (new_objective, new_time) < best_states[state_key]:
                best_states[state_key] = (new_objective, new_time)
                heapq.heappush(heap, (new_objective, new_time, neighbor, new_battery, new_path))
                
            # If neighbor is a charging station, simulate immediate recharge upon arrival.
            if neighbor in charging_set:
                recharge_key = (neighbor, max_range)
                # Recharging doesn't add extra time/risk.
                if state_key != recharge_key:
                    if recharge_key not in best_states or (new_objective, new_time) < best_states[recharge_key]:
                        best_states[recharge_key] = (new_objective, new_time)
                        heapq.heappush(heap, (new_objective, new_time, neighbor, max_range, new_path))
                    
    # No valid route found
    return []
    
if __name__ == "__main__":
    # Example manual test (optional)
    num_intersections = 3
    edges = [
        (0, 1, 100, 0.1),
        (1, 2, 100, 0.1),
        (0, 2, 250, 0.3)
    ]
    start_intersection = 0
    end_intersection = 2
    max_delivery_time = 60  # seconds
    risk_factor = 0.5
    charging_stations = []
    max_range = 300  # meters
    route = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
    print("Route:", route)