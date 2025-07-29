import heapq

def plan_routes(city_graph, drones, base_speed):
    # Build adjacency list from the city graph
    # Each entry: node -> list of (neighbor, distance, traffic)
    graph = {node: [] for node in city_graph["nodes"]}
    for edge in city_graph["edges"]:
        src = edge["src"]
        dest = edge["dest"]
        distance = edge["distance"]
        traffic = edge["traffic"]
        graph[src].append((dest, distance, traffic))
    
    def get_multiplier(traffic, current_time):
        # Given a list of traffic conditions (start, end, multiplier)
        for interval in traffic:
            start, end, multiplier = interval
            if start <= current_time < end:
                return multiplier
        # fallback if no interval is found, use last available multiplier
        return traffic[-1][2]
    
    def dijkstra(start, end, departure_time):
        # returns minimal arrival time at end, starting at departure_time from start.
        times = {node: float('inf') for node in graph}
        times[start] = departure_time
        heap = [(departure_time, start)]
        while heap:
            current_time, node = heapq.heappop(heap)
            if node == end:
                return current_time
            if current_time > times[node]:
                continue
            for neighbor, distance, traffic in graph[node]:
                multiplier = get_multiplier(traffic, current_time)
                travel_time = distance / (base_speed * multiplier)
                arrival_time = current_time + travel_time
                if arrival_time < times.get(neighbor, float('inf')):
                    times[neighbor] = arrival_time
                    heapq.heappush(heap, (arrival_time, neighbor))
        return None

    result = {}
    for drone in drones:
        drone_id = drone["id"]
        current_node = drone["start"]
        current_time = 0.0
        route = []
        possible = True
        for delivery in drone["schedule"]:
            destination = delivery["destination"]
            window_start, window_end = delivery["time_window"]
            turnaround = delivery["turnaround"]
            arrival_time = dijkstra(current_node, destination, current_time)
            if arrival_time is None:
                possible = False
                break
            # Check if arrival is too late for the time window.
            if arrival_time > window_end:
                possible = False
                break
            # If arrival earlier than window_start, drone has to wait.
            if arrival_time < window_start:
                effective_arrival = window_start
            else:
                effective_arrival = arrival_time
            route.append((destination, effective_arrival))
            # After delivery, add turnaround time.
            current_time = effective_arrival + turnaround
            current_node = destination
        if not possible:
            result[drone_id] = []
        else:
            result[drone_id] = route
    return result