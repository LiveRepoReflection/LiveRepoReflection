import math
import heapq

def build_graph(N, tracks, upgrade_schedule):
    # Build a dictionary for closures per track.
    # Use a key (min(city1, city2), max(city1, city2)) for each track.
    closure_dict = {}
    for (u, v, start, end) in upgrade_schedule:
        key = (min(u, v), max(u, v))
        if key not in closure_dict:
            closure_dict[key] = []
        closure_dict[key].append((start, end))
        
    # For each track, create two lists: one for baseline (all train times)
    # and one for upgraded schedule (only train times not falling in any closure interval).
    # Build graph as an adjacency list: graph[u] = list of edges (v, baseline_trains, closure_trains)
    graph = {i: [] for i in range(N)}
    for track in tracks:
        u, v, length, trains = track
        sorted_trains = sorted(trains)
        key = (min(u, v), max(u, v))
        # Filter train times for closure schedule.
        closure_intervals = closure_dict.get(key, [])
        filtered_trains = []
        for t in sorted_trains:
            in_closure = False
            for (s, e) in closure_intervals:
                if s <= t <= e:
                    in_closure = True
                    break
            if not in_closure:
                filtered_trains.append(t)
        # Add edge in both directions.
        graph[u].append((v, sorted_trains, filtered_trains))
        graph[v].append((u, sorted_trains, filtered_trains))
    return graph

def next_departure(time, schedule):
    # Given a sorted list of train departure times (schedule) and current time,
    # return the smallest t in schedule that is >= time. If none exists, return math.inf.
    lo = 0
    hi = len(schedule)
    res = math.inf
    while lo < hi:
        mid = (lo + hi) // 2
        if schedule[mid] >= time:
            res = schedule[mid]
            hi = mid
        else:
            lo = mid + 1
    return res

def earliest_arrival(source, start_time, destination, graph, use_closure):
    # Use Dijkstra-like algorithm over time.
    # Each state: (arrival_time, city).
    n = len(graph)
    dist = [math.inf] * n
    dist[source] = start_time
    heap = [(start_time, source)]
    while heap:
        current_time, city = heapq.heappop(heap)
        if current_time > dist[city]:
            continue
        if city == destination:
            # Found the best arrival at destination.
            return current_time
        for neighbor, baseline_schedule, closure_schedule in graph[city]:
            schedule = closure_schedule if use_closure else baseline_schedule
            next_time = next_departure(current_time, schedule)
            if next_time < dist[neighbor]:
                dist[neighbor] = next_time
                heapq.heappush(heap, (next_time, neighbor))
    return math.inf

def calculate_min_max_delay(N, tracks, upgrade_schedule, passenger_trips):
    graph = build_graph(N, tracks, upgrade_schedule)
    max_delay = 0
    for departure, arrival, desired_departure_time in passenger_trips:
        baseline_arrival = earliest_arrival(departure, desired_departure_time, arrival, graph, use_closure=False)
        actual_arrival = earliest_arrival(departure, desired_departure_time, arrival, graph, use_closure=True)
        # If baseline route is unreachable, consider delay as infinite.
        if baseline_arrival == math.inf or actual_arrival == math.inf:
            return math.inf
        delay = actual_arrival - baseline_arrival
        if delay > max_delay:
            max_delay = delay
    return max_delay