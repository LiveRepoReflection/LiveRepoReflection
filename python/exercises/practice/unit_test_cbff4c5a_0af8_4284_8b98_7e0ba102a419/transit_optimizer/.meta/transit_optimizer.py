import heapq
from collections import defaultdict

def optimize_routes(stations, routes, passenger_requests):
    """
    Optimizes routes for passengers based on their preferences and constraints.
    
    Args:
        stations (dict): A dictionary mapping station IDs to available transportation methods
        routes (list): A list of tuples (origin, destination, transportation, cost, time)
        passenger_requests (list): A list of tuples (origin, destination, max_cost, max_time, weight)
        
    Returns:
        list: For each passenger request, either a list of station IDs representing the optimal route,
              or the string "No suitable route found"
    """
    # Build a graph representation with weighted edges
    graph = defaultdict(list)
    for origin, destination, transport, cost, time in routes:
        # Only add the edge if the destination station supports this transport type
        if transport in stations[destination]:
            graph[origin].append((destination, transport, cost, time))
    
    results = []
    
    for origin, destination, max_cost, max_time, weight in passenger_requests:
        result = find_optimal_path(graph, stations, origin, destination, max_cost, max_time, weight)
        results.append(result)
    
    return results

def find_optimal_path(graph, stations, origin, destination, max_cost, max_time, weight):
    """
    Finds the optimal path between origin and destination based on weighted cost and time.
    
    Args:
        graph (dict): Graph representation of the transportation network
        stations (dict): Dictionary of stations and their transport methods
        origin (int): Starting station ID
        destination (int): Ending station ID
        max_cost (float): Maximum acceptable cost
        max_time (float): Maximum acceptable travel time
        weight (float): Weight parameter for time vs cost (higher means time is more important)
        
    Returns:
        list or str: The optimal path as a list of station IDs, or an error message if no path found
    """
    # Priority queue for Dijkstra's algorithm
    # Format: (weighted_score, total_cost, total_time, current_station, path)
    priority_queue = [(0, 0, 0, origin, [origin])]
    
    # Keep track of visited stations with their cost and time
    # We keep track of cost and time separately because the optimization is a weighted sum
    visited = {}  # Format: {station_id: (min_weighted_score, cost, time)}
    
    while priority_queue:
        weighted_score, current_cost, current_time, current, path = heapq.heappop(priority_queue)
        
        # If we've reached the destination
        if current == destination:
            # Check if constraints are satisfied
            if current_cost <= max_cost and current_time <= max_time:
                return path
            continue
        
        # If we've already found a better path to this station, skip it
        if current in visited and weighted_score >= visited[current][0]:
            continue
        
        # Mark as visited with current score, cost, and time
        visited[current] = (weighted_score, current_cost, current_time)
        
        # Explore neighbors
        for next_station, transport, cost, time in graph[current]:
            # Check if the transport type is available at the current station
            if transport in stations[current]:
                new_cost = current_cost + cost
                new_time = current_time + time
                
                # Calculate the weighted score for this path
                new_weighted_score = weight * new_time + (1 - weight) * new_cost
                
                # Only consider this path if it doesn't exceed the constraints
                # and if we haven't found a better path to this station yet
                if (new_cost <= max_cost and 
                    new_time <= max_time and 
                    (next_station not in visited or 
                     new_weighted_score < visited[next_station][0])):
                    
                    new_path = path + [next_station]
                    heapq.heappush(priority_queue, 
                                  (new_weighted_score, new_cost, new_time, next_station, new_path))
    
    # No path found that satisfies the constraints
    return "No suitable route found"