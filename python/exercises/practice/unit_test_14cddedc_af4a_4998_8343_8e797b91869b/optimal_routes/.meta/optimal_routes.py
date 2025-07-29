import heapq
from collections import defaultdict
import copy


def find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times):
    """
    Find optimal routes for a fleet of drones to complete delivery tasks.
    
    Args:
        graph: A dictionary representing the directed graph of the city.
        delivery_tasks: A list of tuples (pickup_location, delivery_location, start_time, end_time).
        depot_location: The node ID of the depot.
        max_flight_time: Maximum flight time for a drone before recharging.
        time_dependent_travel_times: A function to calculate travel time based on departure time.
        
    Returns:
        A list of routes, where each route is a list of node IDs.
    """
    routes = []
    
    # Process each delivery task
    for task_index, (pickup, delivery, start_time, end_time) in enumerate(delivery_tasks):
        # Find the optimal route for this task
        route = find_route_for_task(
            graph, 
            depot_location, 
            pickup, 
            delivery, 
            start_time, 
            end_time, 
            max_flight_time, 
            time_dependent_travel_times
        )
        
        if not route:
            # If any task is infeasible, return an empty list
            return []
        
        routes.append(route)
    
    return routes


def find_route_for_task(graph, depot, pickup, delivery, start_time, end_time, max_flight_time, time_dependent_travel_times):
    """
    Find an optimal route for a single delivery task.
    
    Args:
        graph: The city graph.
        depot: Depot location.
        pickup: Pickup location.
        delivery: Delivery location.
        start_time: Earliest pickup time.
        end_time: Latest delivery time.
        max_flight_time: Maximum flight time.
        time_dependent_travel_times: Function to calculate travel times.
        
    Returns:
        A list of node IDs representing the optimal route, or an empty list if infeasible.
    """
    # Step 1: Find the best time to depart from the depot
    best_route = None
    best_total_time = float('inf')
    
    # Try different departure times
    for departure_time in range(start_time - 1000, start_time + 1, 100):  # Try various departure times
        if departure_time < 0:
            continue
            
        # Find the fastest path from depot to pickup
        depot_to_pickup_result = find_time_dependent_path(
            graph, 
            depot, 
            pickup, 
            departure_time, 
            time_dependent_travel_times
        )
        
        if not depot_to_pickup_result:
            continue
        
        depot_to_pickup_time, depot_to_pickup_path = depot_to_pickup_result
        pickup_arrival_time = departure_time + depot_to_pickup_time
        
        # Check if we arrive at pickup location within the time window
        if pickup_arrival_time > end_time:
            continue
        
        # Find the fastest path from pickup to delivery
        pickup_to_delivery_result = find_time_dependent_path(
            graph, 
            pickup, 
            delivery, 
            pickup_arrival_time, 
            time_dependent_travel_times
        )
        
        if not pickup_to_delivery_result:
            continue
        
        pickup_to_delivery_time, pickup_to_delivery_path = pickup_to_delivery_result
        delivery_arrival_time = pickup_arrival_time + pickup_to_delivery_time
        
        # Check if we arrive at delivery location within the time window
        if delivery_arrival_time > end_time:
            continue
        
        # Find the fastest path from delivery back to depot
        delivery_to_depot_result = find_time_dependent_path(
            graph, 
            delivery, 
            depot, 
            delivery_arrival_time, 
            time_dependent_travel_times
        )
        
        if not delivery_to_depot_result:
            continue
        
        delivery_to_depot_time, delivery_to_depot_path = delivery_to_depot_result
        return_time = delivery_arrival_time + delivery_to_depot_time
        
        # Calculate total flight time
        total_flight_time = depot_to_pickup_time + pickup_to_delivery_time + delivery_to_depot_time
        
        # Check if total flight time exceeds max_flight_time
        if total_flight_time > max_flight_time:
            continue
        
        # Combine paths to form the complete route
        complete_route = depot_to_pickup_path[:-1] + pickup_to_delivery_path[:-1] + delivery_to_depot_path
        
        # Update best route if this one is better
        if total_flight_time < best_total_time:
            best_total_time = total_flight_time
            best_route = complete_route
    
    return best_route if best_route else []


def find_time_dependent_path(graph, start, end, departure_time, time_dependent_travel_times):
    """
    Find the fastest path from start to end, departing at departure_time.
    
    Args:
        graph: The city graph.
        start: Start node.
        end: End node.
        departure_time: Time of departure.
        time_dependent_travel_times: Function to calculate travel times.
        
    Returns:
        A tuple (travel_time, path) or None if no path is found.
    """
    # Modified Dijkstra's algorithm for time-dependent shortest path
    pq = [(0, departure_time, start, [start])]  # (time_so_far, current_time, current_node, path)
    visited = set()
    
    while pq:
        time_so_far, current_time, current, path = heapq.heappop(pq)
        
        if current == end:
            return time_so_far, path
        
        if (current, current_time) in visited:
            continue
        
        visited.add((current, current_time))
        
        if current not in graph:
            continue
        
        for neighbor in graph[current]:
            travel_time = time_dependent_travel_times(graph, current, neighbor, current_time)
            new_time = current_time + travel_time
            new_path = path + [neighbor]
            
            heapq.heappush(pq, (time_so_far + travel_time, new_time, neighbor, new_path))
    
    return None  # No path found