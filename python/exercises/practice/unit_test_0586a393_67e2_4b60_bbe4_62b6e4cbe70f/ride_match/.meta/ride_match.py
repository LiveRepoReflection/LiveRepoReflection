import heapq
from collections import defaultdict, deque

def maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time):
    """
    Maximize the number of fulfilled ride requests.

    Args:
        city_graph: A weighted graph represented as an adjacency list.
        ride_requests: A list of tuples (rider_id, start_location, end_location).
        driver_availabilities: A list of tuples (driver_id, current_location).
        communication_radius: Maximum travel time for direct communication.
        max_ride_time: Maximum allowable travel time for a fulfilled ride.
    
    Returns:
        List of tuples (driver_id, rider_id) representing matched rides.
    """
    if not ride_requests or not driver_availabilities:
        return []
    
    # Calculate shortest paths for all nodes
    shortest_paths = {}
    for node in city_graph:
        shortest_paths[node] = dijkstra(city_graph, node)
    
    # Build a bipartite graph for matching
    bipartite_graph = defaultdict(list)
    
    # For each driver, find all riders they can communicate with and serve
    for driver_id, driver_location in driver_availabilities:
        for rider_id, start_location, end_location in ride_requests:
            # Check if driver and rider can communicate
            if driver_location in shortest_paths and start_location in shortest_paths[driver_location]:
                dist_to_rider = shortest_paths[driver_location][start_location]
                if dist_to_rider <= communication_radius:
                    # Check if the ride is feasible
                    if start_location in shortest_paths and end_location in shortest_paths[start_location]:
                        dist_start_to_end = shortest_paths[start_location][end_location]
                        total_ride_time = dist_to_rider + dist_start_to_end
                        if total_ride_time <= max_ride_time:
                            # Add edge to bipartite graph (driver -> rider)
                            bipartite_graph[driver_id].append(rider_id)
    
    # Use Ford-Fulkerson algorithm (augmenting paths) to find maximum bipartite matching
    return find_maximum_bipartite_matching(bipartite_graph, driver_availabilities, ride_requests)

def dijkstra(graph, start):
    """
    Compute shortest paths from start node to all other nodes in the graph.
    
    Args:
        graph: A weighted graph represented as an adjacency list.
        start: The starting node.
        
    Returns:
        A dictionary of shortest distances from start to each node.
    """
    distances = {start: 0}
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # If we've already found a shorter path, skip
        if current_distance > distances.get(current_node, float('inf')):
            continue
        
        # Check all neighboring nodes
        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight
            
            # If this path is shorter than the previously known path
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

def find_maximum_bipartite_matching(graph, drivers, riders):
    """
    Find the maximum bipartite matching using Ford-Fulkerson algorithm.
    
    Args:
        graph: A bipartite graph represented as an adjacency list.
        drivers: List of driver tuples.
        riders: List of rider tuples.
        
    Returns:
        List of matched (driver_id, rider_id) pairs.
    """
    # Create a mapping of rider_id to index
    rider_id_to_index = {rider[0]: i for i, rider in enumerate(riders)}
    
    # Initial matching: no drivers are matched
    matching = {}  # Maps rider_id to driver_id
    
    for driver_id in [d[0] for d in drivers]:
        # Try to find an augmenting path for this driver
        if augment_path(graph, driver_id, set(), matching, rider_id_to_index):
            continue
    
    # Convert matching to the required output format
    result = []
    for rider_id, driver_id in matching.items():
        result.append((driver_id, rider_id))
    
    return result

def augment_path(graph, driver_id, visited, matching, rider_id_to_index):
    """
    Try to find an augmenting path using DFS.
    
    Args:
        graph: A bipartite graph represented as an adjacency list.
        driver_id: The current driver ID to match.
        visited: Set of visited riders in current DFS.
        matching: Current matching (maps rider_id -> driver_id).
        rider_id_to_index: Mapping of rider_id to index.
        
    Returns:
        Boolean indicating if an augmenting path was found.
    """
    for rider_id in graph[driver_id]:
        if rider_id in visited:
            continue
            
        visited.add(rider_id)
        
        # If rider is not matched or we can reassign its match
        if rider_id not in matching or augment_path(graph, matching[rider_id], visited, matching, rider_id_to_index):
            matching[rider_id] = driver_id
            return True
            
    return False

def find_path_with_min_travel_time(graph, start, end):
    """
    Find a path from start to end with minimum travel time.
    
    Args:
        graph: A weighted graph represented as an adjacency list.
        start: Starting node.
        end: Ending node.
        
    Returns:
        (path, travel_time) where path is a list of nodes and travel_time is the total travel time.
    """
    if start == end:
        return [start], 0
        
    # Use Dijkstra's algorithm
    distances = {start: 0}
    previous = {start: None}
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_node == end:
            break
            
        if current_distance > distances.get(current_node, float('inf')):
            continue
        
        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight
            
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # Reconstruct path
    if end not in previous:
        return None, float('inf')  # No path exists
        
    path = []
    current = end
    
    while current:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    return path, distances[end]