import heapq

def get_traffic_density(edge, arrival_time):
    # In a real-world scenario, this function would return a dynamic traffic density based on road conditions at 'arrival_time'.
    # For this implementation, we simply return the default traffic density provided in the edge information.
    return edge[2]

def plan_route(graph, request):
    start = request.get('start')
    end = request.get('end')
    departure_time = request.get('departure_time', 0)
    max_budget = request.get('max_budget', float('inf'))

    # If start and end are the same, return trivial route.
    if start == end:
        return [start], 0, 0

    # Build graph dictionary and gather all nodes.
    graph_dict = {}
    nodes = set()
    for edge in graph:
        u, v, travel_time, traffic_density, toll_cost = edge
        if travel_time < 0:
            raise ValueError("Negative travel time is not allowed")
        nodes.add(u)
        nodes.add(v)
        if u not in graph_dict:
            graph_dict[u] = []
        # Append edge information; each edge is represented as a tuple.
        graph_dict[u].append((v, travel_time, traffic_density, toll_cost))

    if start not in nodes or end not in nodes:
        return [], 0, 0

    # Priority queue holds tuples: (accumulated_effective_time, accumulated_toll, current_node, current_clock_time, path_taken)
    # current_clock_time is measured based on actual delay, i.e., effective travel time.
    heap = []
    heapq.heappush(heap, (0, 0, start, departure_time, [start]))
    
    # Dictionary to record the best effective time seen for a state (node, accumulated toll)
    visited = {}

    while heap:
        acc_time, acc_toll, node, current_time, path = heapq.heappop(heap)
        
        if node == end:
            return path, acc_time, acc_toll
        
        key = (node, acc_toll)
        if key in visited and visited[key] <= acc_time:
            continue
        visited[key] = acc_time

        if node not in graph_dict:
            continue

        for edge in graph_dict[node]:
            v, travel_time, default_density, toll_cost = edge
            new_toll = acc_toll + toll_cost
            if new_toll > max_budget:
                continue

            # Estimate arrival time by adding the base travel time.
            estimated_arrival = current_time + travel_time
            # Retrieve the effective traffic density for this edge at the estimated arrival time.
            effective_density = get_traffic_density(edge, estimated_arrival)
            effective_time = travel_time * effective_density

            new_time = acc_time + effective_time
            new_current_time = current_time + effective_time
            new_path = path + [v]

            heapq.heappush(heap, (new_time, new_toll, v, new_current_time, new_path))

    return [], 0, 0