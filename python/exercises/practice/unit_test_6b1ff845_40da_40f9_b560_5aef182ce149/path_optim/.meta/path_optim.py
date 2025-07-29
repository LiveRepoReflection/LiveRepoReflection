import heapq

def find_optimal_path(graph, source, target, time_weight, cost_weight, max_fuel, MAX_TRAFFIC):
    # Edge cases:
    if source not in graph or target not in graph or max_fuel <= 0:
        return []
    # If source and target are same, return immediately.
    if source == target:
        return [source]

    # Priority queue element: (total_weighted_cost, current_node, fuel_consumed, path)
    heap = []
    heapq.heappush(heap, (0.0, source, 0.0, [source]))
    
    # For each node, store the visited states as a list of (fuel, cost)
    visited = {node: [] for node in graph}
    visited[source].append((0.0, 0.0))
    
    while heap:
        curr_cost, node, curr_fuel, path = heapq.heappop(heap)
        
        # If we have reached target, return the path.
        if node == target:
            return path
        
        for edge in graph.get(node, []):
            # Skip invalid edges: negative length, zero speed_limit or negative fuel_consumption_rate.
            length = edge.get('length', None)
            speed_limit = edge.get('speed_limit', None)
            fuel_rate = edge.get('fuel_consumption_rate', None)
            traffic_density = edge.get('traffic_density', None)
            toll_cost = edge.get('toll_cost', None)
            dest = edge.get('to', None)
            if length is None or speed_limit is None or fuel_rate is None or traffic_density is None or toll_cost is None or dest is None:
                continue
            if length < 0 or speed_limit <= 0 or fuel_rate < 0:
                continue
            # Check if road is impassable due to traffic.
            if traffic_density >= MAX_TRAFFIC:
                continue
                
            # Calculate traversal time using the formula.
            traffic_factor = 1 - (traffic_density / MAX_TRAFFIC)
            # To avoid division by zero, if traffic_factor is 0 skip.
            if traffic_factor <= 0:
                continue
            travel_time = length / (speed_limit * traffic_factor)
            
            # Fuel consumption for this edge.
            fuel_needed = length * fuel_rate
            new_fuel = curr_fuel + fuel_needed
            if new_fuel > max_fuel:
                continue
            
            # Compute weighted cost for this edge.
            edge_cost = time_weight * travel_time + cost_weight * toll_cost
            new_total_cost = curr_cost + edge_cost
            
            new_path = path + [dest]
            
            # State domination check: if we have reached dest before with less or equal fuel and cost, skip new state.
            dominated = False
            for recorded_fuel, recorded_cost in visited.get(dest, []):
                if recorded_fuel <= new_fuel and recorded_cost <= new_total_cost:
                    dominated = True
                    break
            if dominated:
                continue
            
            # Remove dominated states in visited[dest].
            new_states = []
            for recorded_fuel, recorded_cost in visited.get(dest, []):
                if not (new_fuel <= recorded_fuel and new_total_cost <= recorded_cost):
                    new_states.append((recorded_fuel, recorded_cost))
            new_states.append((new_fuel, new_total_cost))
            visited[dest] = new_states
            
            heapq.heappush(heap, (new_total_cost, dest, new_fuel, new_path))
    return []