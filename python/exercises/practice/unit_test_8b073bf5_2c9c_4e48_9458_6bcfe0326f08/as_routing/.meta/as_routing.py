import heapq

def find_optimal_path(topology, as_metrics, origin_as, destination_as):
    # Each state: (penalty, total_latency, path_length, current_node, last_edge, second_last_edge, path)
    # last_edge and second_last_edge are relationship types (strings) from the previous edges.
    # total_latency includes the latency of nodes in the path.
    # Start with origin_as having its latency.
    start_latency = as_metrics.get(origin_as, 0)
    start_state = (0, start_latency, 1, origin_as, None, None, [origin_as])
    # Priority queue for Dijkstra-like search.
    heap = []
    heapq.heappush(heap, start_state)
    
    # Use a dictionary to store the best (penalty, latency, path_length) encountered for a given state defined by (node, last_edge, second_last_edge)
    best = {}
    
    while heap:
        penalty, total_latency, path_length, current, last_edge, second_last_edge, path = heapq.heappop(heap)
        
        # If reached destination, return path immediately.
        if current == destination_as:
            return path
        
        state_key = (current, last_edge, second_last_edge)
        if state_key in best:
            prev_penalty, prev_latency, prev_length = best[state_key]
            # If we've seen a better or equal state before, skip.
            if (penalty, total_latency, path_length) >= (prev_penalty, prev_latency, prev_length):
                continue
        best[state_key] = (penalty, total_latency, path_length)
        
        # Explore neighbors
        if current not in topology:
            continue
        for neighbor, relation in topology[current]:
            # Avoid cycles: if neighbor is already in path, skip.
            if neighbor in path:
                continue
            
            # Compute new penalty increment based on the relationship transition rules:
            new_penalty = penalty
            # Rule 1: If the last edge was "customer" and current edge is "customer", add penalty.
            if last_edge == "customer" and relation == "customer":
                new_penalty += 1
            # Rule 2: If we have at least two edges and pattern is ("customer", "provider", "customer"), add penalty.
            if second_last_edge == "customer" and last_edge == "provider" and relation == "customer":
                new_penalty += 1

            # Compute new total latency: add the neighbor's latency.
            neighbor_latency = as_metrics.get(neighbor, 0)
            new_total_latency = total_latency + neighbor_latency
            
            new_path_length = path_length + 1
            new_path = path + [neighbor]
            new_state = (new_penalty, new_total_latency, new_path_length, neighbor, relation, last_edge, new_path)
            heapq.heappush(heap, new_state)
    
    return []