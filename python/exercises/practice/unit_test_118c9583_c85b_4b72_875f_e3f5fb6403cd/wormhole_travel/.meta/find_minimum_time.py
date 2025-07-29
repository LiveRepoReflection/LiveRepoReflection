import heapq

def find_minimum_time(N, wormholes, start_dimension, end_dimension, departure_time):
    # Build graph: for each dimension, store list of wormholes as (destination, start_time, end_time, travel_time)
    graph = [[] for _ in range(N)]
    for u, v, start_time, end_time, travel_time in wormholes:
        graph[u].append((v, start_time, end_time, travel_time))
        graph[v].append((u, start_time, end_time, travel_time))
    
    # Initialize earliest arrival times: start time for start_dimension and infinity for others.
    dist = [float('inf')] * N
    dist[start_dimension] = departure_time
    
    # Priority queue: (current time, current dimension)
    heap = [(departure_time, start_dimension)]
    
    while heap:
        current_time, u = heapq.heappop(heap)
        
        # If this is an outdated route, skip it.
        if current_time != dist[u]:
            continue
        
        # If we reached the destination, return the arrival time.
        if u == end_dimension:
            return current_time
        
        # Explore all available wormholes from current dimension u.
        for v, wh_start, wh_end, travel_time in graph[u]:
            # Wait if necessary until the wormhole becomes active.
            departure_time_effective = max(current_time, wh_start)
            # If the wormhole is still active after waiting, can take this wormhole.
            if departure_time_effective < wh_end:
                arrival_time = departure_time_effective + travel_time
                if arrival_time < dist[v]:
                    dist[v] = arrival_time
                    heapq.heappush(heap, (arrival_time, v))
    
    # If end_dimension was unreachable, return -1.
    return -1