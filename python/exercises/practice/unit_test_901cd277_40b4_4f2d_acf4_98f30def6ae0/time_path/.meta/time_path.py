import heapq

def find_min_time(n, edges, sources, destination, start_time):
    # Build adjacency list
    graph = [[] for _ in range(n)]
    for u, v, cost_profile in edges:
        graph[u].append((v, cost_profile))
    
    # Priority queue: (total_time, node, current_hour)
    heap = []
    for source in sources:
        heapq.heappush(heap, (0, source, start_time))
    
    # Track minimum time to reach each node at each possible hour (0-23)
    min_times = [{} for _ in range(n)]
    for source in sources:
        min_times[source][start_time] = 0
    
    while heap:
        current_time, node, current_hour = heapq.heappop(heap)
        
        if node == destination:
            return current_time
        
        if current_time > min_times[node].get(current_hour, float('inf')):
            continue
            
        for neighbor, cost_profile in graph[node]:
            # Calculate arrival hour and time taken
            edge_time = cost_profile[current_hour % 24]
            new_time = current_time + edge_time
            new_hour = (current_hour + edge_time) % 24
            
            # Check if we found a better path to neighbor at new_hour
            if (new_hour not in min_times[neighbor] or 
                new_time < min_times[neighbor].get(new_hour, float('inf'))):
                
                min_times[neighbor][new_hour] = new_time
                heapq.heappush(heap, (new_time, neighbor, new_hour))
    
    return -1