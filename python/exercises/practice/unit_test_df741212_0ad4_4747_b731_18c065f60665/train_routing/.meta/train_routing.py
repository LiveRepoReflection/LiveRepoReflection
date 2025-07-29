import heapq
import math
from collections import defaultdict

def min_train_trips(num_cities, edges, train_capacity, passenger_requests):
    """
    Calculate the minimum number of train trips required to fulfill all passenger requests.
    
    Args:
        num_cities: Number of cities in the network.
        edges: List of tuples (city1, city2, travel_time) representing direct train lines.
        train_capacity: Maximum number of passengers a train can carry.
        passenger_requests: List of tuples (source, destination, num_passengers).
    
    Returns:
        Minimum number of train trips required, or -1 if impossible.
    """
    if not passenger_requests:
        return 0
    
    # Build adjacency list
    graph = defaultdict(list)
    for city1, city2, travel_time in edges:
        graph[city1].append((city2, travel_time))
        graph[city2].append((city1, travel_time))  # Undirected graph
    
    total_trips = 0
    
    for source, dest, num_passengers in passenger_requests:
        if num_passengers == 0:  # No need for any trips if no passengers
            continue
            
        # Edge case: Same source and destination
        if source == dest:
            total_trips += math.ceil(num_passengers / train_capacity)
            continue
            
        # Find shortest path using Dijkstra's algorithm
        shortest_path = find_shortest_path(graph, source, dest, num_cities)
        
        # If no path exists, it's impossible to fulfill the request
        if not shortest_path:
            return -1
        
        # Calculate number of trips needed for this request
        trips_needed = math.ceil(num_passengers / train_capacity)
        total_trips += trips_needed
    
    return total_trips

def find_shortest_path(graph, start, end, num_cities):
    """
    Find the shortest path between start and end cities using Dijkstra's algorithm.
    
    Args:
        graph: Adjacency list representation of the graph.
        start: Starting city.
        end: Destination city.
        num_cities: Number of cities in the network.
        
    Returns:
        A list representing the shortest path from start to end, or None if no path exists.
    """
    # Priority queue for Dijkstra's algorithm
    pq = [(0, start, [])]  # (distance, city, path)
    visited = set()
    
    while pq:
        dist, current, path = heapq.heappop(pq)
        
        if current == end:
            return path + [current]
            
        if current in visited:
            continue
            
        visited.add(current)
        path = path + [current]
        
        for neighbor, weight in graph[current]:
            if neighbor not in visited:
                heapq.heappush(pq, (dist + weight, neighbor, path))
    
    # No path found
    return None