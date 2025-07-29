import math
from heapq import heappop, heappush

def minimal_highway_cost(cities, C):
    if len(cities) <= 1:
        return 0.0
    
    n = len(cities)
    visited = [False] * n
    min_heap = []
    total_cost = 0.0
    
    # Start with the first city
    visited[0] = True
    for j in range(1, n):
        dx = cities[0][0] - cities[j][0]
        dy = cities[0][1] - cities[j][1]
        distance = math.sqrt(dx*dx + dy*dy)
        heappush(min_heap, (distance + C, j))
    
    while min_heap:
        cost, city = heappop(min_heap)
        if not visited[city]:
            visited[city] = True
            total_cost += cost
            for j in range(n):
                if not visited[j]:
                    dx = cities[city][0] - cities[j][0]
                    dy = cities[city][1] - cities[j][1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    heappush(min_heap, (distance + C, j))
    
    return total_cost