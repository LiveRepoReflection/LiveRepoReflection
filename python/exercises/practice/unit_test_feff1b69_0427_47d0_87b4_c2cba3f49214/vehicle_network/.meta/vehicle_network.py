import heapq

def route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit):
    # Build the graph as an adjacency list: graph[u] = list of (v, length, congestion)
    graph = {i: [] for i in range(num_intersections)}
    for u, v, length, congestion in roads:
        graph[u].append((v, length, congestion))

    # Initialize schedule for each edge: dictionary mapping (u,v) -> list of (start_time, end_time)
    schedule = {}
    for u, v, length, congestion in roads:
        schedule.setdefault((u, v), [])

    total_energy = 0
    result_paths = []

    # Process each vehicle sequentially.
    for start, end in vehicle_routes:
        route_result = find_route(start, end, graph, schedule, max_vehicles_per_road)
        if route_result is None:
            # No route found for this vehicle.
            result_paths.append([])
            continue

        path_edges, path_nodes, energy_cost, finish_time = route_result

        # Check if adding this vehicle's route exceeds the energy limit.
        if total_energy + energy_cost > energy_limit:
            result_paths.append([])
            continue

        # Update the schedule with the intervals for each edge on the chosen path.
        for edge, t_start, t_end in path_edges:
            schedule.setdefault(edge, []).append((t_start, t_end))

        total_energy += energy_cost
        result_paths.append(path_nodes)

    return result_paths

def find_route(start, end, graph, schedule, capacity):
    # Modified Dijkstra: state = (total_energy, current_time, current_node, path_nodes, path_edges)
    # path_edges: list of (edge, start_time, end_time) used so far.
    heap = []
    heapq.heappush(heap, (0, 0, start, [start], []))
    # visited dictionary to prevent reprocessing states; key is (node, current_time) with best energy.
    visited = {}
    while heap:
        energy, cur_time, node, path_nodes, path_edges = heapq.heappop(heap)
        if node == end:
            return (path_edges, path_nodes, energy, cur_time)

        key = (node, cur_time)
        if key in visited and visited[key] <= energy:
            continue
        visited[key] = energy

        for v, length, congestion in graph[node]:
            edge = (node, v)
            current_schedule = schedule.get(edge, [])
            t_start, concurrent = get_next_available_time(cur_time, length, current_schedule, capacity)
            t_finish = t_start + length
            # Energy cost on the edge = length (base cost) + congestion penalty * (number of vehicles concurrently + 1)
            edge_energy = length + congestion * (concurrent + 1)
            new_energy = energy + edge_energy
            new_time = t_finish
            new_path_nodes = path_nodes + [v]
            new_path_edges = path_edges + [(edge, t_start, t_finish)]
            heapq.heappush(heap, (new_energy, new_time, v, new_path_nodes, new_path_edges))
    return None

def get_next_available_time(t, length, intervals, capacity):
    # For a given edge with existing intervals (each as (s, e)) and candidate start time t,
    # find the smallest t' >= t such that the interval [t', t'+length) has less than capacity overlapping intervals.
    # Also return the count of overlapping intervals at that time.
    candidate = t
    while True:
        count = 0
        for s, e in intervals:
            if s < candidate + length and candidate < e:
                count += 1
        if count < capacity:
            return candidate, count
        candidate += 1

if __name__ == '__main__':
    # Example usage; this block can be removed if running tests separately.
    num_intersections = 4
    roads = [
        (0, 1, 10, 1),
        (1, 2, 15, 2),
        (2, 3, 10, 1),
        (0, 2, 25, 2),
        (1, 3, 30, 3)
    ]
    vehicle_routes = [
        (0, 3),
        (0, 3)
    ]
    max_vehicles_per_road = 1
    energy_limit = 1000
    routes = route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit)
    print(routes)