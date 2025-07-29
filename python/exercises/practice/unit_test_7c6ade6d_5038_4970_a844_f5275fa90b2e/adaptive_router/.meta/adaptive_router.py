import heapq
from collections import defaultdict

def adaptive_router(N, edges, requests, initial_load):
    # Build adjacency list
    graph = defaultdict(dict)
    for u, v, capacity in edges:
        graph[u][v] = {'capacity': capacity, 'load': initial_load.get((u, v), 0)}
        graph[v][u] = {'capacity': capacity, 'load': initial_load.get((v, u), 0)}
    
    # Process each request
    results = []
    for source, destination, message_size in requests:
        if source not in graph or destination not in graph:
            results.append(None)
            continue
            
        # Dijkstra's algorithm with congestion-aware cost
        heap = []
        heapq.heappush(heap, (0, source, [source]))
        visited = set()
        found = False
        
        while heap:
            current_cost, node, path = heapq.heappop(heap)
            
            if node in visited:
                continue
                
            if node == destination:
                results.append(path)
                found = True
                # Update loads for used edges
                for i in range(len(path)-1):
                    u, v = path[i], path[i+1]
                    graph[u][v]['load'] += message_size
                    graph[v][u]['load'] += message_size
                break
                
            visited.add(node)
            
            for neighbor, data in graph[node].items():
                if neighbor in visited:
                    continue
                    
                # Calculate congestion cost
                remaining_capacity = max(1, data['capacity'] - data['load'])
                congestion_cost = message_size / remaining_capacity
                
                # Add to heap with new cost and path
                new_cost = current_cost + congestion_cost
                new_path = path + [neighbor]
                heapq.heappush(heap, (new_cost, neighbor, new_path))
        
        if not found:
            results.append(None)
    
    return results