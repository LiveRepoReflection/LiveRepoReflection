import math
import heapq

def find_most_reliable_path(N, edges, failure_probabilities, s, d, start_sol, end_sol):
    # If source is the same as destination, return trivial path.
    if s == d:
        return ([s], 1.0, 0)
    
    T = end_sol - start_sol + 1  # number of sols
    # Build the graph as an adjacency list.
    graph = {i: [] for i in range(N)}
    for (u, v, lat_func) in edges:
        graph[u].append((v, lat_func))
    
    # Define the cost tuple. We use lexicographic ordering of (reliability_cost, latency)
    # Reliability cost = accumulated T*(-log(1 - f)) for all non-destination nodes.
    # Since for each node i (which is not destination) we incur cost: T * (-log(1 - failure_probabilities[i]))
    # Lower reliability cost means higher reliability.
    # Latency is the accumulated sum of latencies along the path.
    
    # For the source node, if it is not destination, include its reliability cost.
    initial_rel_cost = 0 if s == d else T * (-math.log(1 - failure_probabilities[s]))
    initial_state = (initial_rel_cost, 0, s, [s])  # (reliability_cost, latency, current_node, path)
    
    heap = [initial_state]
    # best[node] stores the best tuple (reliability_cost, latency) achieved reaching node.
    best = {s: (initial_rel_cost, 0)}
    
    while heap:
        current_rel, current_lat, node, path = heapq.heappop(heap)
        # If we reached destination, we have our best result (by lexicographical order of cost).
        if node == d:
            reliability = math.exp(-current_rel)
            return (path, reliability, current_lat)
        
        # Skip this state if a better or equal cost has been found already.
        if (node in best) and ((current_rel, current_lat) > best[node]):
            continue
        
        for neighbor, lat_func in graph[node]:
            # Calculate edge latency: sum the latency over all sols in the provided range.
            edge_latency = sum(lat_func(sol) for sol in range(start_sol, end_sol + 1))
            new_latency = current_lat + edge_latency
            
            # If neighbor is the destination, do not add reliability cost.
            if neighbor == d:
                add_rel_cost = 0
            else:
                # If failure probability is 1 or more, the reliability becomes 0, treat cost as infinite.
                if failure_probabilities[neighbor] >= 1:
                    add_rel_cost = float('inf')
                else:
                    add_rel_cost = T * (-math.log(1 - failure_probabilities[neighbor]))
            new_rel = current_rel + add_rel_cost
            
            new_cost_tuple = (new_rel, new_latency)
            # If we find a better cost tuple for the neighbor, update and push to the heap.
            if neighbor not in best or new_cost_tuple < best[neighbor]:
                best[neighbor] = new_cost_tuple
                heapq.heappush(heap, (new_rel, new_latency, neighbor, path + [neighbor]))
    
    return ([], 0.0, 0)