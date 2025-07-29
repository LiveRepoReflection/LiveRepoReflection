import heapq

def dijkstra(network, start, end):
    dist = {node: float('inf') for node in network}
    dist[start] = 0
    prev = {}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if node == end:
            break
        if d > dist[node]:
            continue
        for edge in network[node]:
            neighbor = edge["to"]
            alt = d + edge["travel_time"]
            if alt < dist.get(neighbor, float('inf')):
                dist[neighbor] = alt
                prev[neighbor] = node
                heapq.heappush(heap, (alt, neighbor))
    if dist[end] < float('inf'):
        path = []
        cur = end
        while cur != start:
            path.append(cur)
            cur = prev[cur]
        path.append(start)
        path.reverse()
        return dist[end], path
    else:
        return float('inf'), []

def route_vehicles(network, vehicles, packages, dynamic_traffic_updates):
    # Update network travel times with dynamic traffic updates.
    for update in dynamic_traffic_updates:
        start, end, new_time = update
        if start in network:
            for edge in network[start]:
                if edge["to"] == end:
                    edge["travel_time"] = new_time

    # Initialize vehicle states.
    vehicles_state = {}
    for veh in vehicles:
        vehicles_state[veh["id"]] = {
            "current": veh["location"],
            "remaining_time": veh["remaining_time"],
            "capacity": veh["capacity"],
            "plan": []
        }

    # Sort packages by descending priority.
    sorted_packages = sorted(packages, key=lambda p: -p["priority"])

    # Greedy assignment of packages to vehicles.
    for pkg in sorted_packages:
        best_vehicle = None
        best_cost = float('inf')
        for vid, state in vehicles_state.items():
            # Compute the time cost from current location to pickup and then to delivery.
            cost_to_pickup, _ = dijkstra(network, state["current"], pkg["pickup_location"])
            cost_to_delivery, _ = dijkstra(network, pkg["pickup_location"], pkg["delivery_location"])
            total_cost = cost_to_pickup + cost_to_delivery
            if total_cost <= state["remaining_time"]:
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_vehicle = vid
        if best_vehicle is not None:
            state = vehicles_state[best_vehicle]
            # Create actions for the vehicle.
            if state["current"] != pkg["pickup_location"]:
                state["plan"].append(("move", pkg["pickup_location"], None))
            state["plan"].append(("pickup", pkg["pickup_location"], pkg["id"]))
            if pkg["pickup_location"] != pkg["delivery_location"]:
                state["plan"].append(("move", pkg["delivery_location"], None))
            state["plan"].append(("deliver", pkg["delivery_location"], pkg["id"]))
            # Update vehicle state.
            state["remaining_time"] -= best_cost
            state["current"] = pkg["delivery_location"]

    # Build result dictionary.
    result = {vid: state["plan"] for vid, state in vehicles_state.items()}
    return result