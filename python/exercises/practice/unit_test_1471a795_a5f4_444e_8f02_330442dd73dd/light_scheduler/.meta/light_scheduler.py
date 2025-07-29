import heapq

def optimal_average_travel_time(n, m, roads, intersections, od_pairs):
    # Build bidirectional graph
    graph = {i: [] for i in range(1, n+1)}
    for u, v, travel_time in roads:
        graph[u].append((v, travel_time))
        graph[v].append((u, travel_time))
    
    def compute_waiting_time(intersection, incoming, arrival_time):
        phases = intersections[intersection]['phases']
        period = sum(duration for duration, _ in phases)
        if period == 0:
            return 0
        arrival_mod = arrival_time % period
        cumulative = []
        s = 0
        for duration, allowed in phases:
            s += duration
            cumulative.append(s)
        # Find the current phase index
        current_phase = 0
        for idx, end_time in enumerate(cumulative):
            if arrival_mod < end_time:
                current_phase = idx
                break
        # Check if current phase allows the incoming road
        if (incoming, intersection) in phases[current_phase][1]:
            return 0
        # Look forward in the current cycle
        for j in range(current_phase + 1, len(phases)):
            if (incoming, intersection) in phases[j][1]:
                return cumulative[j] - arrival_mod
        # Wrap around to the next cycle
        for j in range(0, current_phase):
            if (incoming, intersection) in phases[j][1]:
                return (period - arrival_mod) + cumulative[j]
        # If no phase ever allows the incoming road, then the road is effectively blocked.
        return float('inf')
    
    def dijkstra(origin, destination):
        # Time-dependent Dijkstra. State: (current_time, current_node)
        best_time = {i: float('inf') for i in range(1, n+1)}
        best_time[origin] = 0
        heap = [(0, origin)]
        while heap:
            cur_time, node = heapq.heappop(heap)
            if cur_time > best_time[node]:
                continue
            if node == destination:
                return cur_time
            for neighbor, travel in graph[node]:
                time_after_travel = cur_time + travel
                # If neighbor is destination, no traffic light waiting is applied
                if neighbor == destination:
                    total_time = time_after_travel
                else:
                    wait = compute_waiting_time(neighbor, node, time_after_travel)
                    if wait == float('inf'):
                        continue
                    total_time = time_after_travel + wait
                if total_time < best_time[neighbor]:
                    best_time[neighbor] = total_time
                    heapq.heappush(heap, (total_time, neighbor))
        return float('inf')
    
    total_volume = 0
    weighted_sum = 0.0
    for origin, destination, volume in od_pairs:
        travel = dijkstra(origin, destination)
        if travel == float('inf'):
            # Skip unreachable pairs
            continue
        weighted_sum += travel * volume
        total_volume += volume
    if total_volume == 0:
        return 0.0
    average_time = weighted_sum / total_volume
    return round(average_time, 6)