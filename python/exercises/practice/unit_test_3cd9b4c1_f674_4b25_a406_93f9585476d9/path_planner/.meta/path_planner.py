import heapq

def find_optimal_path(graph, start_node, end_node, deadline, priority, energy_budget, distance_weight, energy_weight, time_weight):
    # Check if start and end node exist in graph
    if start_node not in graph or end_node not in graph:
        return []

    # Priority queue: (total_cost, current_node, cumulative_energy, cumulative_time, path, cumulative_distance)
    queue = []
    initial_cost = 0
    initial_state = (initial_cost, start_node, 0, 0, [start_node], 0)
    heapq.heappush(queue, initial_state)

    # For each node, maintain a list of non-dominated states: (energy, time, cost)
    best = {start_node: [(0, 0, initial_cost)]}

    while queue:
        current_cost, current_node, cumulative_energy, cumulative_time, path, cumulative_distance = heapq.heappop(queue)
        
        # If we have reached the destination, return the current path
        if current_node == end_node:
            return path
        
        # Explore neighbors
        for edge in graph.get(current_node, []):
            neighbor = edge["destination"]
            new_energy = cumulative_energy + edge["energy_cost"]
            new_time = cumulative_time + edge["time_cost"] * edge["weather_impact"]
            
            # Check if the new state violates the energy or deadline constraint
            if new_energy > energy_budget or new_time > deadline:
                continue
            
            new_distance = cumulative_distance + edge["distance"]
            new_cost = distance_weight * new_distance + energy_weight * new_energy + time_weight * new_time
            new_path = path + [neighbor]
            
            # Dominance check: if there's an existing state for neighbor that's better in all aspects, skip this state
            dominated = False
            if neighbor in best:
                for (e_val, t_val, c_val) in best[neighbor]:
                    if e_val <= new_energy and t_val <= new_time and c_val <= new_cost:
                        dominated = True
                        break
            else:
                best[neighbor] = []
            
            if dominated:
                continue
            
            # Remove any states that are dominated by this new state
            new_states = []
            for (e_val, t_val, c_val) in best[neighbor]:
                if not (new_energy <= e_val and new_time <= t_val and new_cost <= c_val):
                    new_states.append((e_val, t_val, c_val))
            new_states.append((new_energy, new_time, new_cost))
            best[neighbor] = new_states
            
            heapq.heappush(queue, (new_cost, neighbor, new_energy, new_time, new_path, new_distance))
    
    return []

def update_edge(graph, source, destination, new_distance, new_energy_cost, new_time_cost, new_weather_impact):
    if source in graph:
        for edge in graph[source]:
            if edge["destination"] == destination:
                edge["distance"] = new_distance
                edge["energy_cost"] = new_energy_cost
                edge["time_cost"] = new_time_cost
                edge["weather_impact"] = new_weather_impact
                break

def remove_edge(graph, source, destination):
    if source in graph:
        graph[source] = [edge for edge in graph[source] if edge["destination"] != destination]