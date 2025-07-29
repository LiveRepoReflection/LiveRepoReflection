import heapq
from collections import defaultdict

def max_cities_visited(cities, transport, origin, budget, time_limit):
    # Build adjacency list
    graph = defaultdict(list)
    for city_a, city_b, cost, time in transport:
        graph[city_a].append((city_b, cost, time))
    
    # Priority queue: (negative_cities_visited, current_city, remaining_budget, remaining_time, visited_set)
    # Using negative cities for max heap behavior
    heap = []
    initial_visited = frozenset([origin])
    heapq.heappush(heap, (-1, origin, budget, time_limit, initial_visited))
    
    max_cities = 1  # At least the origin city
    
    while heap:
        neg_cities, current, remaining_b, remaining_t, visited = heapq.heappop(heap)
        current_cities = -neg_cities
        
        if current_cities > max_cities:
            max_cities = current_cities
        
        for neighbor, cost, time in graph.get(current, []):
            if neighbor not in visited:
                new_budget = remaining_b - cost
                new_time = remaining_t - time
                
                if new_budget >= 0 and new_time >= 0:
                    new_visited = set(visited)
                    new_visited.add(neighbor)
                    new_visited_frozen = frozenset(new_visited)
                    new_cities = current_cities + 1
                    
                    # Push to heap if this path is promising
                    heapq.heappush(heap, (-new_cities, neighbor, new_budget, new_time, new_visited_frozen))
    
    return max_cities