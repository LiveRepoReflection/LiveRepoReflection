def solve_delivery_problem(cities, road_network, delivery_demands, truck_capacity, truck_cost, distance_cost_per_unit):
    # Build graph as dictionary for Floyd-Warshall
    INF = float('inf')
    nodes = list(cities.keys())
    # Initialize distance dictionary
    dist = {u: {v: INF for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 0
    for u, v, d in road_network:
        dist[u][v] = min(dist[u][v], d)
        dist[v][u] = min(dist[v][u], d)
    
    # Floyd-Warshall to compute all pairs shortest paths
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Expand each delivery request into chunks to fit into a truck.
    # Each request: (source, destination, num_packages)
    # If num_packages > truck_capacity, split into multiple chunks.
    delivery_chunks_by_source = {}
    for source, dest, num in delivery_demands:
        if source not in delivery_chunks_by_source:
            delivery_chunks_by_source[source] = []
        remaining = num
        while remaining > 0:
            chunk = min(remaining, truck_capacity)
            delivery_chunks_by_source[source].append((source, dest, chunk))
            remaining -= chunk

    trucks = []
    total_cost = 0.0

    # For each source, group deliveries that start at that source
    for source in delivery_chunks_by_source:
        requests = delivery_chunks_by_source[source]
        # Process requests by repeatedly filling a truck until all chunks are assigned.
        while requests:
            capacity_remaining = truck_capacity
            truck_deliveries = []
            # Use a simple greedy approach: iterate through the list and assign deliveries if they fit.
            i = 0
            while i < len(requests) and capacity_remaining > 0:
                req_source, req_dest, req_num = requests[i]
                if req_num <= capacity_remaining:
                    truck_deliveries.append((req_source, req_dest, req_num))
                    capacity_remaining -= req_num
                    requests.pop(i)
                else:
                    # Split the request if it exceeds the remaining capacity
                    truck_deliveries.append((req_source, req_dest, capacity_remaining))
                    requests[i] = (req_source, req_dest, req_num - capacity_remaining)
                    capacity_remaining = 0
                    break
            # Determine route for this truck.
            # Start at the source. The truck will deliver to each destination in the order of appearance.
            route = [source]
            for delivery in truck_deliveries:
                # Append destination if not already the current last destination.
                dest = delivery[1]
                if route[-1] != dest:
                    route.append(dest)
            # Return to the starting city.
            if route[-1] != source:
                route.append(source)
            
            # Compute route distance using precomputed shortest paths
            route_distance = 0
            for j in range(len(route) - 1):
                route_distance += dist[route[j]][route[j+1]]
            
            truck_total_cost = truck_cost + (route_distance * distance_cost_per_unit)
            total_cost += truck_total_cost
            
            trucks.append({
                "route": route,
                "packages": truck_deliveries
            })
    
    # For any deliveries that originate from a source not in the delivery_chunks_by_source (should not happen), 
    # they would be processed here.
    return {
        "trucks": trucks,
        "total_cost": total_cost
    }