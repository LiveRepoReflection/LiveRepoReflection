import heapq
from collections import defaultdict

def find_optimal_path(N, edges, risk_levels, transfer_risks, start, end, T, max_path_length):
    # Build adjacency list
    graph = defaultdict(list)
    for i, j in edges:
        graph[i].append(j)
    
    # Priority queue: (total_risk, current_node, path, path_length)
    heap = []
    heapq.heappush(heap, (0, start, [start], 0))
    
    # Best risk for (node, path_length)
    best_risks = defaultdict(lambda: float('inf'))
    best_risks[(start, 0)] = 0
    
    while heap:
        current_total_risk, node, path, path_length = heapq.heappop(heap)
        
        if node == end:
            return path
            
        if path_length >= max_path_length:
            continue
            
        for neighbor in graph[node]:
            if neighbor in path:  # Avoid cycles
                continue
                
            new_path = path + [neighbor]
            new_path_length = path_length + 1
            
            # Calculate cumulative risk for this path across all time steps
            new_total_risk = 0
            for t in range(T):
                path_risk = 0
                product = 1
                
                # Calculate risk for this path at time t
                for i in range(len(new_path)):
                    if i == 0:
                        path_risk += risk_levels(t)[new_path[i]]
                    else:
                        product *= transfer_risks(t).get((new_path[i-1], new_path[i]), 0)
                        path_risk += product * risk_levels(t)[new_path[i]]
                
                new_total_risk += path_risk
                
            # Only proceed if this is better than previous attempts
            if new_total_risk < best_risks[(neighbor, new_path_length)]:
                best_risks[(neighbor, new_path_length)] = new_total_risk
                heapq.heappush(heap, (new_total_risk, neighbor, new_path, new_path_length))
    
    return []  # No path found