import heapq

def find_route(cities, modes, connections, start_city, end_city, budget, time_limit, mode_restrictions):
    # Build graph: for each city, list of outgoing connections.
    graph = {city: [] for city in cities}
    for conn in connections:
        src, dest, mode, cost, t = conn
        graph[src].append(conn)

    # Priority queue: elements are (total_time, total_cost, current_city, path)
    heap = []
    heapq.heappush(heap, (0, 0, start_city, []))
    
    # Dictionary to store best known (time, cost) for each city: list of (time, cost)
    best = {city: [] for city in cities}
    best[start_city].append((0, 0))
    
    while heap:
        curr_time, curr_cost, curr_city, path = heapq.heappop(heap)
        
        # Check if reached end city with valid state.
        if curr_city == end_city:
            # this state is guaranteed to be within limits as they are checked during addition.
            return path
        
        # Expand successors from current city.
        for conn in graph.get(curr_city, []):
            src, dest, mode, cost, t = conn
            
            # Check mode restrictions. If current city has restrictions, then the mode must be allowed.
            if curr_city in mode_restrictions:
                allowed_modes = mode_restrictions[curr_city]
                if mode not in allowed_modes:
                    continue
            
            new_time = curr_time + t
            new_cost = curr_cost + cost
            
            # Check if new state violates constraints.
            if new_time > time_limit or new_cost > budget:
                continue
            
            # Dominance check: if there is an existing state for dest with both lower or equal time and cost, skip.
            dominated = False
            remove_list = []
            for (prev_time, prev_cost) in best.get(dest, []):
                if prev_time <= new_time and prev_cost <= new_cost:
                    dominated = True
                    break
                if new_time <= prev_time and new_cost <= prev_cost:
                    remove_list.append((prev_time, prev_cost))
            if dominated:
                continue
            # Remove dominated states.
            for item in remove_list:
                best[dest].remove(item)
            best[dest].append((new_time, new_cost))
            
            new_path = path + [conn]
            heapq.heappush(heap, (new_time, new_cost, dest, new_path))
    
    # If no route found, return empty list.
    return []

if __name__ == "__main__":
    # Example run
    cities = ["A", "B", "C", "D"]
    modes = {"train", "truck", "ship", "airplane"}
    connections = [
        ("A", "B", "train", 5, 10),
        ("A", "C", "truck", 8, 12),
        ("B", "D", "truck", 5, 10),
        ("C", "D", "airplane", 7, 8)
    ]
    start_city = "A"
    end_city = "D"
    budget = 20
    time_limit = 40
    mode_restrictions = {}
    result = find_route(cities, modes, connections, start_city, end_city, budget, time_limit, mode_restrictions)
    print("Optimal Route:", result)