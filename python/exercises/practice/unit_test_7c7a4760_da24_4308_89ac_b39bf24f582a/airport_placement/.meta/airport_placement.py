import heapq

def optimal_airport_placement(N, roads, population):
    # Build adjacency list
    graph = {i: [] for i in range(1, N+1)}
    for city1, city2, time in roads:
        graph[city1].append((city2, time))
        graph[city2].append((city1, time))
    
    # Precompute all pairs shortest paths using Dijkstra's algorithm
    shortest_paths = {}
    for city in range(1, N+1):
        shortest_paths[city] = dijkstra(graph, city, N)
    
    total_population = sum(population)
    min_avg_time = float('inf')
    best_city = 1
    
    # Calculate weighted average for each potential airport city
    for airport_city in range(1, N+1):
        total_time = 0
        for city in range(1, N+1):
            total_time += population[city-1] * shortest_paths[city][airport_city]
        
        avg_time = total_time / total_population
        
        # Update best city if current is better
        if avg_time < min_avg_time or (avg_time == min_avg_time and airport_city < best_city):
            min_avg_time = avg_time
            best_city = airport_city
    
    return best_city

def dijkstra(graph, start, N):
    # Initialize distances
    distances = {i: float('inf') for i in range(1, N+1)}
    distances[start] = 0
    
    # Priority queue
    heap = []
    heapq.heappush(heap, (0, start))
    
    while heap:
        current_dist, current_city = heapq.heappop(heap)
        
        # Skip if we already found a better path
        if current_dist > distances[current_city]:
            continue
        
        # Explore neighbors
        for neighbor, time in graph[current_city]:
            distance = current_dist + time
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    
    return distances