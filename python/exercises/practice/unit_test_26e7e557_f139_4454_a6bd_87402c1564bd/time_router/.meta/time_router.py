import heapq
from collections import defaultdict
from math import inf

def find_optimal_route(graph, start_intersection, end_intersection, start_time):
    """
    Find the optimal route with minimum travel time considering time-dependent congestion.
    
    Args:
        graph: A dictionary representing the city graph.
        start_intersection: The starting intersection.
        end_intersection: The destination intersection.
        start_time: The starting time (minutes since midnight).
        
    Returns:
        The minimum travel time to reach the destination, or -1 if no path exists.
    """
    # Check if start or end intersections are valid
    if start_intersection not in graph or end_intersection not in graph:
        return -1
    
    # Special case: start equals end
    if start_intersection == end_intersection:
        return 0
    
    # Priority queue for Dijkstra's algorithm
    # Format: (estimated_time, current_time, current_intersection)
    priority_queue = [(0, start_time, start_intersection)]
    # To track the minimum time to reach each intersection
    min_time_to_reach = defaultdict(lambda: inf)
    min_time_to_reach[start_intersection] = 0
    
    while priority_queue:
        current_total_time, current_time, current_intersection = heapq.heappop(priority_queue)
        
        # If we've reached the destination, return the total travel time
        if current_intersection == end_intersection:
            return current_total_time
        
        # If we've found a better path to this intersection already, skip
        if current_total_time > min_time_to_reach[current_intersection]:
            continue
        
        # Explore all neighbors
        for neighbor, base_time, congestion_profile in graph[current_intersection]:
            # Calculate actual travel time considering congestion
            travel_time = calculate_travel_time(base_time, congestion_profile, current_time)
            
            # Calculate new total time and arrival time
            new_total_time = current_total_time + travel_time
            new_arrival_time = (current_time + travel_time) % 1440  # Wrap around at end of day
            
            # If this is a better path to the neighbor, update and add to queue
            if new_total_time < min_time_to_reach[neighbor]:
                min_time_to_reach[neighbor] = new_total_time
                heapq.heappush(priority_queue, (new_total_time, new_arrival_time, neighbor))
    
    # If we've exhausted all possible paths and haven't reached the destination
    return -1

def calculate_travel_time(base_time, congestion_profile, current_time):
    """
    Calculate the actual travel time for a road segment based on the current time and congestion profile.
    
    Args:
        base_time: The base travel time for the road segment.
        congestion_profile: List of (start_time, end_time, congestion_factor) tuples.
        current_time: The current time (minutes since midnight).
        
    Returns:
        The actual travel time considering congestion.
    """
    if not congestion_profile:
        return base_time
    
    # Find the maximum congestion factor that applies at the current time
    max_congestion_factor = 1.0
    
    for start_window, end_window, congestion_factor in congestion_profile:
        # Handle time window wrapping around midnight
        if start_window <= end_window:
            # Normal time window (e.g., 8am to 10am)
            if start_window <= current_time < end_window:
                max_congestion_factor = max(max_congestion_factor, congestion_factor)
        else:
            # Time window wraps around midnight (e.g., 10pm to 2am)
            if current_time >= start_window or current_time < end_window:
                max_congestion_factor = max(max_congestion_factor, congestion_factor)
    
    # Apply the congestion factor to the base travel time
    return base_time * max_congestion_factor