import heapq

def lowest_latency_path(graph, s, d, start_time, end_time):
    """
    Finds the actual lowest latency path from s to d, given that edge cost is computed as:
    cost = base_cost + c(e, time)*(max_cost - base_cost)
    For this implementation, since actual dynamic congestion is not provided, we assume c(e, time)=0.
    Traversal time for an edge is fixed to base_cost.
    """
    # Priority queue items: (total_cost, current_node, current_time, path)
    heap = []
    heapq.heappush(heap, (0, s, start_time, [s]))
    
    # visited dictionary to store the minimum cost encountered for (node, time)
    visited = {}
    
    while heap:
        total_cost, node, curr_time, path = heapq.heappop(heap)
        
        # If the current time exceeds end_time, then skip this state.
        if curr_time > end_time:
            continue
        
        # If destination is reached and within allowed time, return path.
        if node == d:
            return path
        
        # Check if we have visited this node at a similar or better time with lower cost.
        state_key = (node, curr_time)
        if state_key in visited and visited[state_key] <= total_cost:
            continue
        visited[state_key] = total_cost
        
        # Explore neighbors.
        for neighbor, base_cost, max_cost in graph.get(node, []):
            arrival_time = curr_time + base_cost
            if arrival_time > end_time:
                continue
            # For actual routing, dynamic congestion function would be used here.
            # Since we do not have one, assume congestion = 0.
            congestion = 0.0
            edge_cost = base_cost + congestion * (max_cost - base_cost)
            new_total_cost = total_cost + edge_cost
            new_path = path + [neighbor]
            heapq.heappush(heap, (new_total_cost, neighbor, arrival_time, new_path))
            
    return []

def predictive_routing(graph, s, d, start_time, max_travel_time, congestion_prediction):
    """
    Finds the predicted best path from s to d using a congestion_prediction function.
    The cost for each edge is computed as:
      cost = base_cost + congestion_prediction(edge, time) * (max_cost - base_cost)
    where edge is represented as a tuple (current_node, neighbor, base_cost, max_cost).
    The traversal time for an edge is the base_cost and the accumulated travel time must not exceed max_travel_time.
    """
    # Priority queue items: (total_predicted_cost, current_node, current_time, path)
    heap = []
    heapq.heappush(heap, (0, s, start_time, [s]))
    
    # visited dictionary: key = (node, current_time) with cost
    visited = {}
    
    while heap:
        total_cost, node, curr_time, path = heapq.heappop(heap)
        
        if node == d:
            # Check if total travel time is within allowed maximum travel time.
            if curr_time - start_time <= max_travel_time:
                return path
            else:
                continue
        
        state_key = (node, curr_time)
        if state_key in visited and visited[state_key] <= total_cost:
            continue
        visited[state_key] = total_cost
        
        for neighbor, base_cost, max_cost in graph.get(node, []):
            arrival_time = curr_time + base_cost
            total_travel_time = arrival_time - start_time
            if total_travel_time > max_travel_time:
                continue
            
            # Create an edge representation to send to the congestion_prediction function.
            edge = (node, neighbor, base_cost, max_cost)
            predicted_congestion = congestion_prediction(edge, curr_time)
            edge_cost = base_cost + predicted_congestion * (max_cost - base_cost)
            new_total_cost = total_cost + edge_cost
            new_path = path + [neighbor]
            heapq.heappush(heap, (new_total_cost, neighbor, arrival_time, new_path))
    return []