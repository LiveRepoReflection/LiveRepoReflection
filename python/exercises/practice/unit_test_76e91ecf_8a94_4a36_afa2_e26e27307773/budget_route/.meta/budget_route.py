import heapq

def budget_route(N, M, edges, sources, D, B, checkpoints, P):
    # Build the graph: graph[node] = list of (neighbor, travel_time, toll)
    graph = {i: [] for i in range(N)}
    for u, v, t, toll in edges:
        graph[u].append((v, t, toll))
    
    # Set to quickly check if a node is a checkpoint.
    cp_set = set(checkpoints)
    
    # Priority queue: (time, node, toll, cp_count)
    # Note: starting nodes do not count as checkpoint visit even if they are in cp_set.
    pq = []
    for src in sources:
        heapq.heappush(pq, (0, src, 0, 0))
    
    # Use dictionary to record the best time seen for a given state (node, cp_count, toll).
    # We will clamp cp_count to P (i.e., once we reach or exceed P, we treat it as exactly P).
    best = {}
    
    while pq:
        time, node, toll, cp = heapq.heappop(pq)
        
        # If this state is not optimal, skip it.
        state = (node, cp, toll)
        if state in best and best[state] < time:
            continue
        
        # Check destination condition: destination is not counted as a checkpoint.
        if node == D and cp >= P:
            return time
        
        # Explore neighbors.
        for nbr, t_cost, toll_cost in graph[node]:
            new_toll = toll + toll_cost
            if new_toll > B:
                continue
            new_time = time + t_cost
            # Determine new checkpoint count.
            # Do not count if the neighbor is the destination.
            new_cp = cp
            if nbr != D and nbr in cp_set:
                new_cp += 1
                # Clamp checkpoint count to maximum needed.
                if new_cp > P:
                    new_cp = P
            new_state = (nbr, new_cp, new_toll)
            
            if new_state not in best or new_time < best[new_state]:
                best[new_state] = new_time
                heapq.heappush(pq, (new_time, nbr, new_toll, new_cp))
    
    return -1