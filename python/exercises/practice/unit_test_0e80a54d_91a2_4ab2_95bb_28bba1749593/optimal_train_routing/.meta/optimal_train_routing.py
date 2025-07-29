import heapq
from collections import defaultdict

def find_optimal_routes(N, M, tracks, K, trains):
    # Validate inputs
    if N <= 0 or M < 0 or K < 0:
        raise ValueError("Invalid network parameters")
    if len(tracks) != M or len(trains) != K:
        raise ValueError("Input size mismatch")
    
    # Build graph adjacency list
    graph = defaultdict(list)
    for u, v, capacity, time in tracks:
        if u < 0 or u >= N or v < 0 or v >= N:
            raise ValueError("Invalid station number")
        if capacity <= 0 or time <= 0:
            raise ValueError("Invalid track parameters")
        graph[u].append((v, capacity, time))
        graph[v].append((u, capacity, time))  # Tracks are bidirectional

    # Initialize track usage tracker
    track_usage = defaultdict(list)  # key: (u, v), value: list of (end_time, capacity)

    # Process trains in order of departure time
    trains_sorted = sorted([(departure, i) for i, (_, _, departure, _) in enumerate(trains)])
    results = [[] for _ in range(K)]

    for departure, train_idx in trains_sorted:
        origin, dest, _, weight = trains[train_idx]
        
        # Dijkstra's algorithm with capacity constraints
        heap = []
        heapq.heappush(heap, (departure, origin, [], defaultdict(int)))
        visited = set()
        found = False

        while heap and not found:
            current_time, current_station, path, used_capacity = heapq.heappop(heap)
            
            if current_station == dest:
                results[train_idx] = path + [current_station]
                found = True
                break

            if (current_station, current_time) in visited:
                continue
            visited.add((current_station, current_time))

            for neighbor, capacity, transit_time in graph[current_station]:
                # Determine track direction for usage tracking
                track_key = (min(current_station, neighbor), max(current_station, neighbor))
                
                # Find earliest available time slot on this track
                available_time = departure
                current_capacity_used = used_capacity.get(track_key, 0)
                
                if current_capacity_used >= capacity:
                    # Need to wait for capacity to free up
                    earliest_end = min([end for end, cap in track_usage[track_key] if cap > 0], default=departure)
                    available_time = max(available_time, earliest_end)
                
                arrival_time = available_time + transit_time
                
                # Update track usage for this path
                new_used_capacity = used_capacity.copy()
                new_used_capacity[track_key] = new_used_capacity.get(track_key, 0) + 1
                
                heapq.heappush(
                    heap,
                    (
                        arrival_time,
                        neighbor,
                        path + [current_station],
                        new_used_capacity
                    )
                )

    return results