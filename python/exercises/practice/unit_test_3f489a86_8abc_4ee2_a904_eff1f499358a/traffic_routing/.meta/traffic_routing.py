import heapq
from collections import defaultdict

def optimal_traffic_flow(graph, requests, simulation_duration, get_capacity):
    """
    Calculate the optimal traffic flow for all vehicle requests.
    
    Args:
        graph: A dictionary where keys are node IDs and values are dictionaries
               mapping neighbor IDs to travel time and capacity.
        requests: A list of tuples (start_node, end_node, departure_time)
        simulation_duration: The duration of the simulation in seconds
        get_capacity: A function that returns the current capacity usage of a road segment
    
    Returns:
        The average travel time for all vehicles
    """
    # Store the travel times for each vehicle
    travel_times = []
    
    # Process each vehicle request
    for vehicle_id, (start, end, departure_time) in enumerate(requests):
        # Calculate the optimal route for this vehicle
        travel_time = route_vehicle(
            graph, 
            vehicle_id, 
            start, 
            end, 
            departure_time, 
            simulation_duration, 
            get_capacity
        )
        travel_times.append(travel_time)
    
    # Calculate the average travel time
    if not travel_times:
        return 0.0
    
    return sum(travel_times) / len(travel_times)

def route_vehicle(graph, vehicle_id, start, end, departure_time, simulation_duration, get_capacity):
    """
    Route a single vehicle from start to end, considering traffic conditions.
    
    Args:
        graph: The road network graph
        vehicle_id: ID of the vehicle being routed
        start: Start intersection
        end: End intersection
        departure_time: When the vehicle starts its journey
        simulation_duration: Maximum simulation time
        get_capacity: Function to check road capacity
    
    Returns:
        The travel time for this vehicle, or simulation_duration if it can't reach the destination
    """
    # If the vehicle starts after simulation ends, it's lost
    if departure_time >= simulation_duration:
        return simulation_duration
    
    # Initialize the priority queue (min-heap) for Dijkstra's algorithm
    # Format: (estimated_arrival_time, current_node, path, current_time)
    pq = [(departure_time, start, [start], departure_time)]
    heapq.heapify(pq)
    
    # Track visited nodes at specific times to avoid cycles
    visited = set()
    
    # Best arrival time at the destination
    best_arrival_time = None
    
    while pq:
        est_arrival, current, path, current_time = heapq.heappop(pq)
        
        # If we've already found a better path or exceeded simulation time, skip
        if best_arrival_time is not None and est_arrival >= best_arrival_time:
            continue
        if current_time >= simulation_duration:
            continue
        
        # Check if we've reached the destination
        if current == end:
            best_arrival_time = current_time
            continue
        
        # Use a unique key to track visited states (node + time)
        visit_key = (current, current_time)
        if visit_key in visited:
            continue
        visited.add(visit_key)
        
        # Explore all neighbors
        for neighbor, edge_data in graph.get(current, {}).items():
            travel_time = edge_data['time']
            capacity = edge_data['capacity']
            
            # Check if the road has capacity at this time
            current_capacity = get_capacity(graph, current, neighbor, current_time)
            if current_capacity >= capacity:
                continue  # Road is at full capacity
            
            # Calculate when we would arrive at the neighbor
            arrival_time = current_time + travel_time
            
            # If we can reach the neighbor before simulation ends
            if arrival_time < simulation_duration:
                new_path = path + [neighbor]
                
                # Heuristic: estimate remaining time to destination
                # We use a simple heuristic of 0 here (Dijkstra's)
                heuristic = 0
                est_total_time = arrival_time + heuristic
                
                heapq.heappush(pq, (est_total_time, neighbor, new_path, arrival_time))
    
    # If we found a path, return the travel time; otherwise, the vehicle is lost
    if best_arrival_time is not None:
        return best_arrival_time - departure_time
    else:
        return simulation_duration

def get_capacity_mock(graph, u, v, time):
    """
    A mock function for testing - always returns 0 (empty roads)
    """
    return 0