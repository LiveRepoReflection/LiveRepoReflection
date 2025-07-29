import heapq

def find_optimal_route(cities, tracks, start_city, destination_city, budget, time_limit, penalty):
    # Build graph as adjacency list
    graph = {city: [] for city in cities}
    for track in tracks:
        # Each edge: (neighbor, travel_time, maintenance_cost, scenic_flag)
        travel_time = track["length"] / track["speed_limit"]
        graph[track["start_city"]].append({
            "end_city": track["end_city"],
            "travel_time": travel_time,
            "maintenance_cost": track["maintenance_cost"],
            "is_scenic": track["is_scenic"]
        })
    
    # Use a priority queue: ordering by (total_time, -scenic_count, total_cost)
    # Each state: (total_time, -scenic_count, total_cost, current_city, path, visited_set)
    initial_state = (0.0, 0, 0.0, start_city, [start_city], {start_city})
    heap = [initial_state]
    
    best_solution = None

    while heap:
        current_time, neg_scenic, current_cost, current_city, path, visited = heapq.heappop(heap)
        scenic_count = -neg_scenic

        # If we've reached destination and within constraints, return path immediately.
        if current_city == destination_city:
            if current_time <= time_limit and current_cost <= budget:
                # Because we use time as primary key and tie-breaker, this is optimal.
                return path
            
        # Explore neighbors
        for edge in graph.get(current_city, []):
            next_city = edge["end_city"]
            # Avoid cycles: do not visit a city already in path
            if next_city in visited:
                continue
            
            edge_time = edge["travel_time"]
            edge_cost = edge["maintenance_cost"]
            new_time = current_time + edge_time
            
            # Penalty applies if the next city is an intermediate city (not destination)
            add_penalty = penalty if (next_city != destination_city and next_city != start_city) else 0
            new_cost = current_cost + edge_cost + add_penalty
            
            # Early constraint check
            if new_time > time_limit or new_cost > budget:
                continue
                
            new_scenic = scenic_count + (1 if edge["is_scenic"] else 0)
            new_path = path + [next_city]
            new_visited = visited | {next_city}
            
            heapq.heappush(heap, (new_time, -new_scenic, new_cost, next_city, new_path, new_visited))
            
    return []