from heapq import heappush, heappop
from collections import defaultdict
import math

def solve(graph, source_city, destination_city, departure_window_start, departure_window_end, get_travel_time):
    """
    Finds the earliest possible arrival time at the destination city using a modified Dijkstra's algorithm
    that accounts for time-dependent travel times.
    """
    # Input validation
    if departure_window_start > departure_window_end:
        raise ValueError("Invalid departure window: start time cannot be later than end time")
    if source_city not in graph:
        raise ValueError("Source city does not exist in the graph")
    if destination_city not in graph:
        raise ValueError("Destination city does not exist in the graph")

    # Initialize data structures
    earliest_arrival = defaultdict(lambda: math.inf)  # For each city, store the earliest arrival time
    pq = []  # Priority queue storing (arrival_time, city, departure_time) tuples

    # Try all possible departure times within the window
    # We use a discrete time step of 1 minute since the problem specifies integer departure times
    for departure_time in range(departure_window_start, departure_window_end + 1):
        heappush(pq, (departure_time, source_city, departure_time))
        earliest_arrival[(source_city, departure_time)] = departure_time

    best_arrival_time = math.inf

    # Modified Dijkstra's algorithm
    while pq:
        current_time, current_city, original_departure = heappop(pq)

        # If we've reached the destination and found a better arrival time
        if current_city == destination_city:
            best_arrival_time = min(best_arrival_time, current_time)
            continue

        # If current path is worse than best found so far, skip it
        if current_time >= best_arrival_time:
            continue

        # Explore all neighbors
        for next_city, base_travel_time in graph[current_city]:
            # Get actual travel time considering traffic conditions
            actual_travel_time = get_travel_time(current_city, next_city, current_time)
            
            if actual_travel_time == math.inf:
                continue

            new_arrival_time = current_time + actual_travel_time

            # If this creates a new earliest arrival time for this city
            if new_arrival_time < earliest_arrival[(next_city, original_departure)]:
                earliest_arrival[(next_city, original_departure)] = new_arrival_time
                heappush(pq, (new_arrival_time, next_city, original_departure))

    # If no path was found, return -1
    if best_arrival_time == math.inf:
        return -1

    # Round to nearest integer as specified in the requirements
    return round(best_arrival_time)
