import heapq

def get_edge_cost(cost_function, current_time):
    if not cost_function:
        return float('inf')
    
    # Before first time point
    if current_time <= cost_function[0][0]:
        return cost_function[0][1]
    
    # After last time point
    if current_time >= cost_function[-1][0]:
        return cost_function[-1][1]
    
    # Find interpolation points
    for i in range(len(cost_function) - 1):
        t1, c1 = cost_function[i]
        t2, c2 = cost_function[i+1]
        if t1 <= current_time < t2:
            # Linear interpolation
            alpha = (current_time - t1) / (t2 - t1)
            return c1 + alpha * (c2 - c1)
    
    return float('inf')

def min_cost_path(N, M, edges, start_node, end_node, start_time):
    # Build adjacency list
    graph = [[] for _ in range(N)]
    for source, dest, cost_func in edges:
        graph[source].append((dest, cost_func))
    
    # Priority queue: (total_cost, current_time, node)
    heap = []
    heapq.heappush(heap, (0, start_time, start_node))
    
    # Visited dictionary to track best times for each node
    visited = {}
    
    while heap:
        total_cost, current_time, node = heapq.heappop(heap)
        
        if node == end_node:
            return total_cost
        
        if node in visited and visited[node] <= current_time:
            continue
        
        visited[node] = current_time
        
        for neighbor, cost_func in graph[node]:
            edge_cost = get_edge_cost(cost_func, current_time)
            new_time = current_time + edge_cost
            new_cost = total_cost + edge_cost
            
            if neighbor not in visited or new_time < visited.get(neighbor, float('inf')):
                heapq.heappush(heap, (new_cost, new_time, neighbor))
    
    return -1