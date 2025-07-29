import heapq
from collections import defaultdict

def find_optimal_route(edges, start_node, end_node, departure_time, vot):
    """
    Finds the optimal route between start_node and end_node for the given departure time and value of time.
    
    Args:
        edges: List of tuples (source, destination, travel_time, toll_schedule)
        start_node: Integer ID of starting intersection
        end_node: Integer ID of destination intersection
        departure_time: Integer representing departure time in minutes (0-1439)
        vot: Float representing driver's value of time in dollars per minute
    
    Returns:
        Tuple (optimal_route, total_travel_time, total_toll_cost)
    """
    # Handle the case where start and end are the same
    if start_node == end_node:
        return ([start_node], 0, 0)
    
    # Build the graph
    graph = defaultdict(list)
    for source, dest, travel_time, toll_schedule in edges:
        graph[source].append((dest, travel_time, toll_schedule))
    
    # Dijkstra's algorithm with priority queue
    priority_queue = [(0, departure_time, 0, start_node, [start_node])]  # (effective_cost, current_time, toll_cost, node, path)
    visited = set()
    
    while priority_queue:
        effective_cost, current_time, toll_cost, current_node, path = heapq.heappop(priority_queue)
        
        # Skip if we've already processed this node with a better cost
        if current_node in visited:
            continue
            
        # Check if we've reached the destination
        if current_node == end_node:
            # Calculate total travel time
            total_travel_time = (current_time - departure_time)
            return (path, total_travel_time, toll_cost)
            
        visited.add(current_node)
        
        # Explore neighbors
        for neighbor, travel_time, toll_schedule in graph[current_node]:
            if neighbor not in visited:
                # Calculate arrival time at the neighbor
                arrival_time = (current_time + travel_time) % 1440  # Wrap around at midnight
                
                # Calculate toll cost based on arrival time
                edge_toll = calculate_toll(toll_schedule, current_time)
                new_toll_cost = toll_cost + edge_toll
                
                # Calculate effective cost
                new_effective_cost = effective_cost + travel_time + (edge_toll / vot)
                
                # Update the path
                new_path = path + [neighbor]
                
                heapq.heappush(priority_queue, 
                               (new_effective_cost, arrival_time, new_toll_cost, neighbor, new_path))
    
    # If we reach here, no path was found
    return ([], 0, 0)

def calculate_toll(toll_schedule, current_time):
    """
    Calculate toll based on the toll schedule and current time.
    
    Args:
        toll_schedule: List of tuples (start_time, end_time, toll_amount)
        current_time: Integer representing current time in minutes (0-1439)
    
    Returns:
        Float representing the toll cost
    """
    for start_time, end_time, toll_amount in toll_schedule:
        # Handle schedules that span midnight
        if start_time <= end_time:
            if start_time <= current_time < end_time:
                return toll_amount
        else:  # start_time > end_time (spans midnight)
            if current_time >= start_time or current_time < end_time:
                return toll_amount
    
    # If no toll applies at the current time
    return 0.0