import heapq

def find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers):
    graph = {i: [] for i in range(N)}
    for u, v, travel_time, cost, capacity in routes:
        graph[u].append((v, travel_time, cost, capacity))
        graph[v].append((u, travel_time, cost, capacity))
    
    results = []
    for start, end, num_passengers in station_pairs:
        if start == end:
            results.append(0)
            continue
        result = _dijkstra(graph, start, end, num_passengers, max_travel_time, max_transfers)
        results.append(result)
    return results

def _dijkstra(graph, start, end, passengers, max_travel_time, max_transfers):
    # State: (total_cost, current_station, steps_taken, total_travel_time)
    # Note: steps_taken is the number of edges used; transfers = steps_taken - 1.
    heap = []
    heapq.heappush(heap, (0, start, 0, 0))
    # best stores the minimal travel_time encountered for (station, steps)
    best = {}
    
    while heap:
        total_cost, station, steps, current_time = heapq.heappop(heap)
        
        if station == end:
            return total_cost
        
        # Prune states that are worse than previously encountered
        if (station, steps) in best and best[(station, steps)] < current_time:
            continue
        best[(station, steps)] = current_time
        
        for neighbor, travel_time, cost, capacity in graph[station]:
            if capacity < passengers:
                continue
            new_steps = steps + 1
            if new_steps > max_transfers + 1:
                continue
            new_time = current_time + travel_time
            if new_time > max_travel_time:
                continue
            new_cost = total_cost + cost
            # If this state leads to neighbor with same steps and offers a better travel time, update
            if (neighbor, new_steps) not in best or best[(neighbor, new_steps)] > new_time:
                best[(neighbor, new_steps)] = new_time
                heapq.heappush(heap, (new_cost, neighbor, new_steps, new_time))
    return -1