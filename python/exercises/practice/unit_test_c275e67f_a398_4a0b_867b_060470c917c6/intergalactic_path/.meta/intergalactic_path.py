import heapq

def find_shortest_path(n, adj, start, end, resources, resource_thresholds):
    # Priority queue elements: (total_distance, total_degradation, current_station, resources_tuple)
    init_resources = tuple(resources)
    pq = [(0, 0, start, init_resources)]
    # visited dictionary to store best (distance, degradation) for state (station, resources)
    visited = {(start, init_resources): (0, 0)}
    
    while pq:
        dist, degr, station, curr_resources = heapq.heappop(pq)
        
        # If we reach destination, return the total distance.
        if station == end:
            return dist
        
        # If this state is not better than a previously encountered one, skip.
        if visited.get((station, curr_resources), (float('inf'), float('inf'))) < (dist, degr):
            continue
        
        # Explore all wormholes from current station.
        for neighbor, d, degradation_list in adj[station]:
            new_dist = dist + d
            new_degr = degr + sum(amount for _, amount in degradation_list)
            new_resources = list(curr_resources)
            valid = True
            # Apply degradation for each affected resource.
            for res_id, amount in degradation_list:
                new_resources[res_id] -= amount
                if new_resources[res_id] < resource_thresholds[res_id]:
                    valid = False
                    break
            if not valid:
                continue
            new_resources_tuple = tuple(new_resources)
            state_key = (neighbor, new_resources_tuple)
            # Check if this state is better than a recorded one.
            if state_key in visited:
                recorded_dist, recorded_degr = visited[state_key]
                if (new_dist, new_degr) >= (recorded_dist, recorded_degr):
                    continue
            visited[state_key] = (new_dist, new_degr)
            heapq.heappush(pq, (new_dist, new_degr, neighbor, new_resources_tuple))
    
    return -1