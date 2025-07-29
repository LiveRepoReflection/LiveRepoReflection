import heapq
from collections import defaultdict


def find_optimal_routes(city_graph, emergency_events, service_providers):
    """
    Finds optimal routes for emergency vehicles to reach emergency events.
    
    Args:
        city_graph: Dictionary representing the city graph.
        emergency_events: List of tuples (location_id, event_time).
        service_providers: Dictionary mapping service types to lists of location IDs.
    
    Returns:
        Dictionary with event locations as keys and route information as values.
    """
    result = {}
    
    # Create a flat list of all service providers for easier processing
    all_providers = []
    for service_type, locations in service_providers.items():
        for location in locations:
            all_providers.append({
                "type": service_type,
                "location": location
            })
    
    # Process each emergency event
    for event_location, event_time in emergency_events:
        best_route = find_optimal_route_for_event(
            city_graph, event_location, event_time, all_providers)
        result[event_location] = best_route
    
    return result


def find_optimal_route_for_event(city_graph, event_location, event_time, all_providers):
    """
    Finds the optimal route for a single emergency event.
    
    Args:
        city_graph: Dictionary representing the city graph.
        event_location: Location ID of the emergency event.
        event_time: Time when the emergency event occurred.
        all_providers: List of service provider dictionaries.
    
    Returns:
        Dictionary with route information, or None if no route is found.
    """
    best_route = None
    best_arrival_time = float('inf')
    best_provider = None
    
    # Sort providers by type priority
    provider_priority = {"hospital": 0, "fire_station": 1, "police_station": 2}
    
    # Find the best route from any service provider to the event location
    for provider in all_providers:
        provider_location = provider["location"]
        
        # Skip if the provider and event are at the same location
        if provider_location == event_location:
            route_info = {
                "route": [provider_location],
                "arrival_time": event_time,
                "service_provider_type": provider["type"],
                "service_provider_location": provider_location
            }
            
            # Update best route if this is better
            if event_time < best_arrival_time:
                best_route = route_info
                best_arrival_time = event_time
                best_provider = provider
            elif event_time == best_arrival_time:
                # Break ties by service type, then by location ID
                if (provider_priority.get(provider["type"], float('inf')) < 
                    provider_priority.get(best_provider["type"], float('inf'))):
                    best_route = route_info
                    best_provider = provider
                elif (provider_priority.get(provider["type"], float('inf')) == 
                      provider_priority.get(best_provider["type"], float('inf')) and
                      provider_location < best_provider["location"]):
                    best_route = route_info
                    best_provider = provider
            
            continue
        
        # Find the fastest route from this provider to the event
        route, arrival_time = find_fastest_route(
            city_graph, provider_location, event_location, event_time)
        
        if route is not None:
            route_info = {
                "route": route,
                "arrival_time": arrival_time,
                "service_provider_type": provider["type"],
                "service_provider_location": provider_location
            }
            
            # Update best route if this is better
            if arrival_time < best_arrival_time:
                best_route = route_info
                best_arrival_time = arrival_time
                best_provider = provider
            elif arrival_time == best_arrival_time:
                # Break ties by service type, then by location ID
                if (provider_priority.get(provider["type"], float('inf')) < 
                    provider_priority.get(best_provider["type"], float('inf'))):
                    best_route = route_info
                    best_provider = provider
                elif (provider_priority.get(provider["type"], float('inf')) == 
                      provider_priority.get(best_provider["type"], float('inf')) and
                      provider_location < best_provider["location"]):
                    best_route = route_info
                    best_provider = provider
    
    return best_route


def find_fastest_route(city_graph, start_location, end_location, start_time):
    """
    Finds the fastest route from start_location to end_location starting at start_time.
    
    Args:
        city_graph: Dictionary representing the city graph.
        start_location: Starting location ID.
        end_location: Destination location ID.
        start_time: Time to start the journey.
    
    Returns:
        Tuple of (route, arrival_time) or (None, None) if no route is found.
    """
    # Initialize Dijkstra's algorithm
    priority_queue = [(start_time, start_location, [start_location])]
    visited = set()
    
    while priority_queue:
        current_time, current_location, path = heapq.heappop(priority_queue)
        
        # If we reached the destination, return the path
        if current_location == end_location:
            return path, current_time
        
        # Skip if we already processed this location
        if current_location in visited:
            continue
        
        visited.add(current_location)
        
        # Check each neighbor
        if current_location in city_graph:
            for neighbor, time_ranges in city_graph[current_location].items():
                # Calculate travel time based on current time
                travel_time = get_travel_time(time_ranges, current_time)
                
                if travel_time is not None:
                    new_time = current_time + travel_time
                    new_path = path + [neighbor]
                    heapq.heappush(priority_queue, (new_time, neighbor, new_path))
    
    # No route found
    return None, None


def get_travel_time(time_ranges, current_time):
    """
    Determines the travel time based on the current time and time-dependent travel times.
    
    Args:
        time_ranges: List of tuples (time1, time2, travel_time).
        current_time: The current time.
    
    Returns:
        Travel time or None if no applicable time range is found.
    """
    for time1, time2, travel_time in time_ranges:
        if time1 <= current_time <= time2:
            return travel_time
    
    # If no time range applies (should not happen with the problem constraints)
    return None