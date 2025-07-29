import heapq
from collections import defaultdict

def find_optimal_path(N, adj_matrix, capacity, S, D, decay_factor):
    if S == D:
        return []
    
    # Create adjacency list
    graph = defaultdict(list)
    for i in range(N):
        for j in range(N):
            if adj_matrix[i][j] > 0:
                graph[i].append((j, adj_matrix[i][j]))
    
    # Priority queue: (-fidelity, hops, node, path, remaining_capacities)
    # Using negative fidelity to simulate max-heap
    heap = []
    initial_capacities = capacity.copy()
    if initial_capacities[S] <= 0:
        return []
    
    initial_capacities[S] -= 1
    heapq.heappush(heap, (-1, 0, S, [S], initial_capacities))
    
    visited = {}
    
    while heap:
        neg_fidelity, hops, node, path, remaining_capacities = heapq.heappop(heap)
        current_fidelity = -neg_fidelity
        
        if node == D:
            return path
        
        if node in visited:
            existing_fidelity, existing_hops = visited[node]
            if existing_fidelity > current_fidelity or (
                existing_fidelity == current_fidelity and existing_hops <= hops
            ):
                continue
        
        visited[node] = (current_fidelity, hops)
        
        for neighbor, distance in graph[node]:
            if remaining_capacities[neighbor] <= 0:
                continue
            
            new_capacities = remaining_capacities.copy()
            new_capacities[neighbor] -= 1
            new_path = path + [neighbor]
            new_hops = hops + 1
            new_fidelity = current_fidelity * (decay_factor ** distance)
            
            if neighbor not in visited or (
                new_fidelity > visited[neighbor][0] or
                (new_fidelity == visited[neighbor][0] and new_hops < visited[neighbor][1])
            ):
                heapq.heappush(heap, (
                    -new_fidelity,
                    new_hops,
                    neighbor,
                    new_path,
                    new_capacities
                ))
    
    return []