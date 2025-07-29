import heapq
import itertools
from typing import List, Tuple, Set, Dict

def optimal_drone_network(grid_size: int, location_data: List[Tuple[int, int, int, int]], max_hubs: int) -> Tuple[List[Tuple[int, int]], int]:
    """
    Determine the optimal locations for drone delivery hubs that minimize the total cost.
    
    Args:
        grid_size: An integer representing the size of the grid.
        location_data: A list of tuples, where each tuple is (x, y, hub_cost, demand).
        max_hubs: An integer representing the maximum number of hubs that can be established.
    
    Returns:
        A tuple containing:
        - A list of tuples, where each tuple is the (x, y) coordinates of a selected hub location.
        - An integer representing the minimum total cost.
    """
    # Validate input
    validate_input(grid_size, location_data, max_hubs)
    
    # Extract locations without duplicate coordinates
    locations = {}
    for x, y, hub_cost, demand in location_data:
        if (x, y) in locations:
            raise ValueError(f"Duplicate location coordinates found: {(x, y)}")
        locations[(x, y)] = (hub_cost, demand)
    
    # If max_hubs equals the number of locations, all locations should be hubs
    if max_hubs >= len(locations):
        hub_locs = [(x, y) for x, y, _, _ in location_data]
        total_cost = sum(hub_cost for _, _, hub_cost, _ in location_data)
        return hub_locs, total_cost
    
    # If all demands are zero, select locations with minimum hub costs
    total_demand = sum(demand for _, _, _, demand in location_data)
    if total_demand == 0:
        sorted_by_cost = sorted(location_data, key=lambda loc: loc[2])
        hub_locs = [(x, y) for x, y, _, _ in sorted_by_cost[:max_hubs]]
        total_cost = sum(hub_cost for _, _, hub_cost, _ in sorted_by_cost[:max_hubs])
        return hub_locs, total_cost
    
    # For the actual optimization, we'll use a greedy algorithm with local search
    best_hub_locs, best_cost = greedy_with_local_search(grid_size, location_data, max_hubs)
    
    return best_hub_locs, best_cost

def validate_input(grid_size: int, location_data: List[Tuple[int, int, int, int]], max_hubs: int) -> None:
    """
    Validate the input parameters.
    
    Args:
        grid_size: An integer representing the size of the grid.
        location_data: A list of tuples, where each tuple is (x, y, hub_cost, demand).
        max_hubs: An integer representing the maximum number of hubs that can be established.
    
    Raises:
        ValueError: If any of the input parameters are invalid.
    """
    if grid_size < 1 or grid_size > 50:
        raise ValueError(f"Invalid grid_size: {grid_size}. Must be between 1 and 50.")
    
    if not location_data:
        raise ValueError("location_data cannot be empty.")
    
    if len(location_data) > grid_size * grid_size:
        raise ValueError(f"location_data length ({len(location_data)}) exceeds grid capacity ({grid_size * grid_size}).")
    
    if max_hubs < 1 or max_hubs > min(10, len(location_data)):
        raise ValueError(f"Invalid max_hubs: {max_hubs}. Must be between 1 and min(10, len(location_data)).")
    
    for x, y, hub_cost, demand in location_data:
        if x < 0 or x >= grid_size:
            raise ValueError(f"Invalid x-coordinate: {x}. Must be between 0 and {grid_size-1}.")
        if y < 0 or y >= grid_size:
            raise ValueError(f"Invalid y-coordinate: {y}. Must be between 0 and {grid_size-1}.")
        if hub_cost < 0 or hub_cost > 1000:
            raise ValueError(f"Invalid hub_cost: {hub_cost}. Must be between 0 and 1000.")
        if demand < 0 or demand > 100:
            raise ValueError(f"Invalid demand: {demand}. Must be between 0 and 100.")

def calculate_total_cost(hub_locations: List[Tuple[int, int]], location_data: List[Tuple[int, int, int, int]]) -> int:
    """
    Calculate the total cost for a given set of hub locations.
    
    Args:
        hub_locations: A list of tuples, where each tuple is the (x, y) coordinates of a hub.
        location_data: A list of tuples, where each tuple is (x, y, hub_cost, demand).
    
    Returns:
        An integer representing the total cost.
    """
    # Create a dictionary to lookup hub cost
    hub_cost_dict = {(x, y): cost for x, y, cost, _ in location_data}
    
    # Calculate hub establishment cost
    hub_establishment_cost = sum(hub_cost_dict[loc] for loc in hub_locations)
    
    # Calculate delivery cost
    delivery_cost = 0
    for x, y, _, demand in location_data:
        if demand == 0:
            continue
        
        # Find the closest hub
        min_distance = float('inf')
        for hub_x, hub_y in hub_locations:
            distance = abs(x - hub_x) + abs(y - hub_y)
            min_distance = min(min_distance, distance)
        
        # Add the delivery cost for this location
        delivery_cost += min_distance * demand
    
    return hub_establishment_cost + delivery_cost

def greedy_with_local_search(grid_size: int, location_data: List[Tuple[int, int, int, int]], max_hubs: int) -> Tuple[List[Tuple[int, int]], int]:
    """
    Use a greedy algorithm followed by local search to find near-optimal hub locations.
    
    Args:
        grid_size: An integer representing the size of the grid.
        location_data: A list of tuples, where each tuple is (x, y, hub_cost, demand).
        max_hubs: An integer representing the maximum number of hubs that can be established.
    
    Returns:
        A tuple containing:
        - A list of tuples, where each tuple is the (x, y) coordinates of a selected hub location.
        - An integer representing the minimum total cost.
    """
    # Initial greedy selection based on a combination of hub cost and total demand
    location_scores = []
    for i, (x, y, hub_cost, demand) in enumerate(location_data):
        # Calculate a score for each location (lower is better)
        # Consider both hub cost and the potential to serve nearby demand
        # This is a simple heuristic and can be improved
        score = hub_cost - demand
        for j, (other_x, other_y, _, other_demand) in enumerate(location_data):
            if i != j:
                distance = abs(x - other_x) + abs(y - other_y)
                # Nearby locations with high demand improve the score
                if distance <= grid_size // 2:
                    score -= other_demand / (1 + distance)
        
        location_scores.append((score, (x, y)))
    
    # Sort locations by score (lower is better)
    location_scores.sort()
    
    # Select the top max_hubs locations
    initial_hub_locs = [loc for _, loc in location_scores[:max_hubs]]
    initial_cost = calculate_total_cost(initial_hub_locs, location_data)
    
    # Perform local search to improve the solution
    hub_locs = initial_hub_locs.copy()
    best_cost = initial_cost
    
    # Extract all possible locations from location_data
    all_locations = [(x, y) for x, y, _, _ in location_data]
    
    improved = True
    while improved:
        improved = False
        
        # Try replacing each hub with a non-hub location
        for i, current_hub in enumerate(hub_locs):
            for potential_hub in all_locations:
                if potential_hub not in hub_locs:
                    # Create a new configuration by replacing one hub
                    new_hub_locs = hub_locs.copy()
                    new_hub_locs[i] = potential_hub
                    
                    # Calculate the cost of the new configuration
                    new_cost = calculate_total_cost(new_hub_locs, location_data)
                    
                    # If the new configuration is better, keep it
                    if new_cost < best_cost:
                        hub_locs = new_hub_locs
                        best_cost = new_cost
                        improved = True
                        break
            
            if improved:
                break
    
    return hub_locs, best_cost