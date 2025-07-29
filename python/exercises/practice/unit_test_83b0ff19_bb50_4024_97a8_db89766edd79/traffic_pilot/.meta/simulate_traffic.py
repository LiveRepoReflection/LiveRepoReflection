import heapq

def simulate_traffic(city_graph, vehicles, simulation_time):
    # Initialize the event queue as a min-heap.
    # Each event is a tuple: (time, vehicle_id, event_type, *extra)
    events = []
    # Initialize the load on each edge: key = (u, v), value = current load
    edge_load = {}
    for u in city_graph:
        for v in city_graph[u]:
            edge_load[(u, v)] = 0

    # Track state for each vehicle. Key is vehicle id.
    vehicle_states = {}
    # Record travel times for vehicles that reach their destination.
    finished_travel_times = []

    # Schedule start events for each vehicle.
    for vid, vehicle in enumerate(vehicles):
        vehicle_states[vid] = {
            'start_time': vehicle['start_time'],
            'current_node': vehicle['origin'],
            'destination': vehicle['destination'],
            'size': vehicle['size']
        }
        # If vehicle starts at destination, record travel time 0.
        if vehicle['origin'] == vehicle['destination']:
            finished_travel_times.append(0)
        else:
            heapq.heappush(events, (vehicle['start_time'], vid, 'start'))

    # Helper function: Modified Dijkstra that considers capacity constraints.
    def dijkstra(start, destination, vehicle_size):
        # Initialize distances and predecessor dictionary.
        dist = {}
        prev = {}
        # Use all nodes from the graph. Some nodes might not appear as keys so we include them from edges.
        nodes = set(city_graph.keys())
        for u in city_graph:
            for v in city_graph[u]:
                nodes.add(v)
        for node in nodes:
            dist[node] = float('inf')
        dist[start] = 0
        heap = [(0, start)]
        while heap:
            d, u = heapq.heappop(heap)
            if u == destination:
                break
            if d > dist[u]:
                continue
            if u in city_graph:
                for v, edge in city_graph[u].items():
                    capacity = edge['capacity']
                    travel_time = edge['travel_time']
                    current_load = edge_load.get((u, v), 0)
                    if current_load + vehicle_size > capacity:
                        continue
                    new_dist = d + travel_time
                    if new_dist < dist.get(v, float('inf')):
                        dist[v] = new_dist
                        prev[v] = u
                        heapq.heappush(heap, (new_dist, v))
        if dist[destination] == float('inf'):
            return None
        # Reconstruct the path from start to destination.
        path = []
        node = destination
        while node != start:
            path.append(node)
            node = prev[node]
        path.append(start)
        path.reverse()
        return path

    current_time = 0
    # Process events until simulation time is reached.
    while events:
        event = heapq.heappop(events)
        time, vid, event_type, *args = event
        if time > simulation_time:
            break
        current_time = time
        vehicle = vehicle_states.get(vid)
        if vehicle is None:
            continue

        if event_type in ('start', 'wait'):
            # If the vehicle has reached its destination, record travel time.
            if vehicle['current_node'] == vehicle['destination']:
                finished_travel_times.append(current_time - vehicle['start_time'])
                continue
            # Compute the route from current node to destination.
            route = dijkstra(vehicle['current_node'], vehicle['destination'], vehicle['size'])
            if route is None or len(route) < 2:
                # No available route, wait and try again.
                heapq.heappush(events, (current_time + 1, vid, 'wait'))
                continue
            # Next edge to take is from current_node to the next node in the path.
            next_node = route[1]
            edge = city_graph[vehicle['current_node']][next_node]
            capacity = edge['capacity']
            current_edge_load = edge_load.get((vehicle['current_node'], next_node), 0)
            if current_edge_load + vehicle['size'] <= capacity:
                # Reserve capacity and schedule arrival event.
                edge_load[(vehicle['current_node'], next_node)] = current_edge_load + vehicle['size']
                arrival_time = current_time + edge['travel_time']
                heapq.heappush(events, (arrival_time, vid, 'arrival', vehicle['current_node'], next_node))
            else:
                # Edge is full; wait and try again in the next time unit.
                heapq.heappush(events, (current_time + 1, vid, 'wait'))
        elif event_type == 'arrival':
            # Extract the edge information.
            from_node, to_node = args
            # Release the capacity on the edge.
            edge_load[(from_node, to_node)] -= vehicle['size']
            # Update the vehicle's current location.
            vehicle['current_node'] = to_node
            if to_node == vehicle['destination']:
                finished_travel_times.append(current_time - vehicle['start_time'])
            else:
                # Schedule immediate routing decision.
                heapq.heappush(events, (current_time, vid, 'start'))

    # Compute the average travel time of vehicles that reached their destination.
    if finished_travel_times:
        average_travel_time = sum(finished_travel_times) / len(finished_travel_times)
    else:
        average_travel_time = 0.0

    return {"average_travel_time": average_travel_time}