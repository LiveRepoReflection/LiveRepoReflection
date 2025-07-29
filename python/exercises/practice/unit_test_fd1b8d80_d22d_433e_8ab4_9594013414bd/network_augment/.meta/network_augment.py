import heapq
from itertools import combinations

def optimize_network(existing_network, commute_data, potential_hubs, hub_distances, budget, hub_capacity, edge_capacity):
    """
    Optimize public transportation network by strategically adding new hubs.
    
    Args:
        existing_network (dict): Directed graph representing the existing transportation network.
                                Each node maps to a dict of {target: (travel_time, capacity)}.
        commute_data (list): List of tuples (start, end, count) representing citizen commutes.
        potential_hubs (list): List of tuples (location_id, construction_cost) for potential new hubs.
        hub_distances (dict): Maps each potential hub to dict of distances to existing locations.
        budget (int): Maximum budget for constructing new hubs.
        hub_capacity (int): Maximum number of citizens that can pass through each hub.
        edge_capacity (int): Capacity of new edges created by hubs.
    
    Returns:
        list: List of location IDs where new hubs should be built.
    """
    # Extract all locations in the existing network
    all_existing_locations = set(existing_network.keys())
    for location in existing_network:
        for target in existing_network[location]:
            all_existing_locations.add(target)
    
    # Calculate total number of citizens
    total_citizens = sum(count for _, _, count in commute_data)
    
    # Sort potential hubs by cost (ascending) for faster pruning
    potential_hubs = sorted(potential_hubs, key=lambda x: x[1])
    potential_hub_locations = [loc for loc, _ in potential_hubs]
    
    # Best solution tracking
    best_solution = []
    best_avg_commute_time = float('inf')
    
    # Try all possible combinations of hubs within budget
    for num_hubs in range(len(potential_hubs) + 1):
        for hub_combination in combinations(potential_hubs, num_hubs):
            # Skip if over budget
            total_cost = sum(cost for _, cost in hub_combination)
            if total_cost > budget:
                continue
            
            hub_ids = [loc for loc, _ in hub_combination]
            
            # Create augmented network with selected hubs
            augmented_network = create_augmented_network(
                existing_network, 
                all_existing_locations,
                hub_ids, 
                hub_distances,
                edge_capacity
            )
            
            # Calculate commute times and hub usage
            total_commute_time, hub_usage = calculate_commute_metrics(
                augmented_network,
                commute_data,
                hub_ids
            )
            
            # Check if any hub exceeds capacity
            if any(usage > hub_capacity for usage in hub_usage.values()):
                continue
            
            # Calculate average commute time
            avg_commute_time = total_commute_time / total_citizens if total_citizens > 0 else float('inf')
            
            # Update best solution if this one is better
            if avg_commute_time < best_avg_commute_time:
                best_avg_commute_time = avg_commute_time
                best_solution = hub_ids
    
    return best_solution

def create_augmented_network(existing_network, all_existing_locations, hub_ids, hub_distances, edge_capacity):
    """
    Create an augmented network by adding new hubs and their connections.
    
    Args:
        existing_network (dict): The existing transportation network.
        all_existing_locations (set): Set of all existing locations.
        hub_ids (list): List of hub IDs to add to the network.
        hub_distances (dict): Maps each potential hub to distances to existing locations.
        edge_capacity (int): Capacity of new edges created by hubs.
    
    Returns:
        dict: The augmented network with new hubs and connections.
    """
    # Create a deep copy of the existing network
    augmented_network = {}
    for node in existing_network:
        augmented_network[node] = existing_network[node].copy()
    
    # Ensure all locations have entries in the network
    for location in all_existing_locations:
        if location not in augmented_network:
            augmented_network[location] = {}
    
    # Add new hubs and their connections
    for hub_id in hub_ids:
        # Initialize the hub in the network
        augmented_network[hub_id] = {}
        
        # Add connections from existing locations to the hub
        for location in all_existing_locations:
            # Add edge from location to hub
            travel_time = hub_distances[hub_id][location]
            if location not in augmented_network:
                augmented_network[location] = {}
            augmented_network[location][hub_id] = (travel_time, edge_capacity)
            
            # Add edge from hub to location
            augmented_network[hub_id][location] = (travel_time, edge_capacity)
    
    return augmented_network

def calculate_commute_metrics(network, commute_data, hub_ids):
    """
    Calculate the total commute time and hub usage for all commutes.
    
    Args:
        network (dict): The augmented transportation network.
        commute_data (list): List of commuter data (start, end, count).
        hub_ids (list): List of hub IDs to track usage of.
    
    Returns:
        tuple: (total_commute_time, hub_usage) where hub_usage is a dict mapping hub_id to usage count.
    """
    total_commute_time = 0
    hub_usage = {hub_id: 0 for hub_id in hub_ids}
    
    for start, end, count in commute_data:
        # Find shortest path
        path, path_time = dijkstra(network, start, end)
        
        # Update total commute time
        total_commute_time += path_time * count
        
        # Update hub usage
        for hub_id in hub_ids:
            if hub_id in path:
                hub_usage[hub_id] += count
    
    return total_commute_time, hub_usage

def dijkstra(graph, start, end):
    """
    Find the shortest path and its travel time from start to end using Dijkstra's algorithm.
    
    Args:
        graph (dict): The transportation network.
        start (int): The starting location.
        end (int): The destination location.
    
    Returns:
        tuple: (path, travel_time) where path is a list of locations in the shortest path.
    """
    # Initialize distances with infinity for all nodes except start
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    
    # Initialize priority queue and visited set
    priority_queue = [(0, start)]
    visited = set()
    
    # For path reconstruction
    previous = {node: None for node in graph}
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_node == end:
            break
            
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        # Check all neighbors of the current node
        for neighbor, (travel_time, _) in graph[current_node].items():
            distance = current_distance + travel_time
            
            # If we found a shorter path to the neighbor
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # Reconstruct the path
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()  # Reverse to get from start to end
    
    # If no path was found, return empty path and infinite travel time
    if not path or path[0] != start:
        return [], float('infinity')
        
    return path, distances[end]