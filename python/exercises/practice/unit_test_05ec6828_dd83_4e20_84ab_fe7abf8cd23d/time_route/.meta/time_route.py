import heapq

def optimal_route(graph, start_intersection, destination_intersection, start_time):
    if start_intersection == destination_intersection:
        return (0, [start_intersection])
    
    # Priority queue elements: (cumulative_travel_time, current_intersection, current_time, path_so_far)
    pq = [(0, start_intersection, start_time, [start_intersection])]
    # Dictionary to store the best known cumulative travel time to each intersection.
    best = {start_intersection: 0}
    
    while pq:
        cum_time, current_node, current_time, path = heapq.heappop(pq)
        
        # If reached destination, return the result.
        if current_node == destination_intersection:
            return (cum_time, path)
        
        # Check if we already found a better way to the current node.
        if cum_time > best.get(current_node, float('inf')):
            continue
        
        # Iterate over all neighbors.
        for neighbor, travel_time_func in graph.get(current_node, {}).items():
            # Compute travel time using the function, using current_time modulo 1440 (given periodic property).
            travel_duration = travel_time_func(current_time % 1440)
            new_cum_time = cum_time + travel_duration
            new_current_time = current_time + travel_duration
            # If this route to neighbor is better, update and push to the queue.
            if new_cum_time < best.get(neighbor, float('inf')):
                best[neighbor] = new_cum_time
                heapq.heappush(pq, (new_cum_time, neighbor, new_current_time, path + [neighbor]))
    
    return (float('inf'), [])