import heapq

def optimize_delivery(network, commodities):
    # Build graph from network list
    graph = {}
    for edge in network:
        u = edge["start_node"]
        v = edge["end_node"]
        travel_time = edge["travel_time"]
        capacity = edge["capacity"]
        if u not in graph:
            graph[u] = []
        graph[u].append({"end": v, "travel_time": travel_time, "capacity": capacity})
    # A dictionary to track edge usage: key = (u, v, minute), value = usage count
    usage = {}
    
    # Function to get shortest path (in travel time) from source to destination using Dijkstra
    def find_shortest_path(source, destination):
        # Each element: (total_travel_time, current_node, path_taken)
        heap = [(0, source, [source])]
        visited = {}
        while heap:
            ttime, node, path = heapq.heappop(heap)
            if node == destination:
                return path, ttime
            if node in visited and visited[node] <= ttime:
                continue
            visited[node] = ttime
            for edge in graph.get(node, []):
                new_time = ttime + edge["travel_time"]
                new_path = path + [edge["end"]]
                heapq.heappush(heap, (new_time, edge["end"], new_path))
        return None, None

    schedule = {}
    # Process each commodity one at a time
    for commodity in commodities:
        cid = commodity["commodity_id"]
        source = commodity["source"]
        destination = commodity["destination"]
        demand = commodity["demand"]
        start_time = commodity["start_time"]
        end_time = commodity["end_time"]
        schedule[cid] = []
        
        # Special case: source equals destination, no travel needed.
        if source == destination:
            for _ in range(demand):
                schedule[cid].append({"route": [source], "departure_time": start_time})
            continue

        # Find the shortest route from source to destination
        path, total_travel_time = find_shortest_path(source, destination)
        if path is None:
            raise Exception(f"No path from {source} to {destination} for commodity {cid}")
        # For each truck required, try to find a departure time that satisfies the constraints
        for _ in range(demand):
            scheduled = False
            # Latest departure time candidate ensuring arrival at destination not later than end_time.
            latest_departure = end_time - total_travel_time
            for candidate_departure in range(start_time, latest_departure + 1):
                feasible = True
                cumulative_time = 0
                # To store time slots that would be occupied if schedule is feasible (for later update)
                temp_usage = []
                # Check each edge along the path
                for i in range(len(path) - 1):
                    u = path[i]
                    v = path[i+1]
                    # Find edge info from network list that matches u->v
                    edge_info = None
                    for edge in network:
                        if edge["start_node"] == u and edge["end_node"] == v:
                            edge_info = edge
                            break
                    if edge_info is None:
                        feasible = False
                        break
                    edge_travel = edge_info["travel_time"]
                    cap = edge_info["capacity"]
                    edge_start_time = candidate_departure + cumulative_time
                    # Truck occupies every minute on the edge from edge_start_time to edge_start_time + edge_travel - 1
                    for minute in range(edge_start_time, edge_start_time + edge_travel):
                        key = (u, v, minute)
                        current_usage = usage.get(key, 0)
                        if current_usage >= cap:
                            feasible = False
                            break
                        temp_usage.append(key)
                    if not feasible:
                        break
                    cumulative_time += edge_travel
                # After checking all edges, if feasible and arrival time met
                if feasible and (candidate_departure + total_travel_time) <= end_time:
                    # Commit the truck schedule by updating usage counts
                    for key in temp_usage:
                        usage[key] = usage.get(key, 0) + 1
                    schedule[cid].append({
                        "route": path,
                        "departure_time": candidate_departure
                    })
                    scheduled = True
                    break
            if not scheduled:
                raise Exception(f"Cannot schedule all trucks for commodity {cid}")
    return schedule