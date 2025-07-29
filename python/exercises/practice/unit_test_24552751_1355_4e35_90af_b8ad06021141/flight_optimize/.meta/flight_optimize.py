import heapq

def optimize_flight_paths(graph_edges, aircraft_list, events, penalty_per_minute):
    # Initialize data structures for events modifications
    # Build initial edge mapping: key=(source, destination), value = {"base_cost": ..., "base_time": ...}
    edge_map = {}
    for edge in graph_edges:
        key = (edge["source"], edge["destination"])
        edge_map[key] = {"base_cost": edge["base_cost"], "base_time": edge["base_time"]}
    
    # Weather delays per airport (affects departure only)
    weather_delay = {}
    
    # Global fuel multiplier
    fuel_multiplier = 1.0

    # Process events in order
    for event in events:
        if event["type"] == "WeatherDelay":
            airport = event["airport_code"]
            delay = event["delay_time"]
            weather_delay[airport] = weather_delay.get(airport, 0) + delay
        elif event["type"] == "RouteClosure":
            key = (event["source"], event["destination"])
            if key in edge_map:
                del edge_map[key]
        elif event["type"] == "IncreasedDemand":
            key = (event["source"], event["destination"])
            if key in edge_map:
                edge_map[key]["base_cost"] += event["cost_increase"]
                edge_map[key]["base_time"] += event["time_increase"]
        elif event["type"] == "FuelPriceChange":
            fuel_multiplier *= (1 + event["price_change_percentage"])
    
    # Build adjacency list using processed edge_map.
    adj = {}
    for (src, dst), vals in edge_map.items():
        effective_cost = vals["base_cost"] * fuel_multiplier
        effective_time = vals["base_time"]
        if src not in adj:
            adj[src] = []
        adj[src].append((dst, effective_cost, effective_time))
    
    # Define function to perform Dijkstra for one aircraft.
    def dijkstra(source, destination):
        # Priority queue items: (total_cost, total_time, node, path)
        # total_time is sum of flight times only (not including departure delay)
        heap = []
        heapq.heappush(heap, (0, 0, source, [source]))
        best = {source: (0, 0)}
        while heap:
            cur_cost, cur_time, node, path = heapq.heappop(heap)
            if node == destination:
                return cur_cost, cur_time, path
            if node not in adj:
                continue
            for neighbor, edge_cost, edge_time in adj[node]:
                new_cost = cur_cost + edge_cost
                new_time = cur_time + edge_time
                # Use lexicographical order (cost, time)
                if neighbor not in best or (new_cost, new_time) < best[neighbor]:
                    best[neighbor] = (new_cost, new_time)
                    heapq.heappush(heap, (new_cost, new_time, neighbor, path + [neighbor]))
        return None

    results = []
    for aircraft in aircraft_list:
        aircraft_id = aircraft["aircraft_id"]
        source = aircraft["current_location"]
        destination = aircraft["destination"]
        desired_departure = aircraft["departure_time"]
        # Calculate departure delay: only weather delay at source counts
        departure_delay = weather_delay.get(source, 0) if source != destination else 0

        # If source equals destination, output immediate result.
        if source == destination:
            results.append({
                "aircraft_id": aircraft_id,
                "path": [source],
                "total_cost": 0,
                "total_time": 0,
                "departure_delay": 0
            })
            continue

        dijkstra_result = dijkstra(source, destination)
        if dijkstra_result is None:
            results.append({
                "aircraft_id": aircraft_id,
                "path": [],
                "total_cost": 0,
                "total_time": 0,
                "departure_delay": 0
            })
        else:
            total_cost, total_time, path = dijkstra_result
            # Apply penalty if actual departure is later than desired.
            # Actual departure time is desired_departure + departure_delay.
            # Penalty is computed separately but does not affect reported total_time.
            penalty = max(0, departure_delay) * penalty_per_minute
            # The problem expects total_time to be the sum of flight times (without penalty),
            # and departure_delay is reported separately.
            results.append({
                "aircraft_id": aircraft_id,
                "path": path,
                "total_cost": int(total_cost),
                "total_time": int(total_time),
                "departure_delay": departure_delay
            })
    return results