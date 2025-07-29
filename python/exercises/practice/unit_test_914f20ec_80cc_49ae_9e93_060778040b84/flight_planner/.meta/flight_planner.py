import heapq
from collections import defaultdict

def solve_flight_planner(n: int, flights: list[tuple[int, int, int]], queries: list[tuple[int, int, int, int]]) -> list[int]:
    # Build adjacency list
    graph = defaultdict(list)
    for u, v, cost in flights:
        graph[u].append((v, cost))
    
    results = []
    for start, end, max_flights, max_cost in queries:
        # Special case: start == end
        if start == end:
            results.append(0)
            continue
            
        # Initialize distance matrix: distance[flights_used][node] = min_cost
        distance = [[float('inf')] * n for _ in range(max_flights + 1)]
        distance[0][start] = 0
        
        # Priority queue: (current_cost, flights_used, current_node)
        heap = []
        heapq.heappush(heap, (0, 0, start))
        
        found = False
        while heap:
            current_cost, flights_used, node = heapq.heappop(heap)
            
            if node == end:
                results.append(current_cost)
                found = True
                break
                
            if flights_used >= max_flights:
                continue
                
            if current_cost > distance[flights_used][node]:
                continue
                
            for neighbor, cost in graph[node]:
                new_cost = current_cost + cost
                new_flights = flights_used + 1
                
                if new_cost > max_cost:
                    continue
                    
                if new_cost < distance[new_flights][neighbor]:
                    distance[new_flights][neighbor] = new_cost
                    heapq.heappush(heap, (new_cost, new_flights, neighbor))
        
        if not found:
            results.append(-1)
            
    return results