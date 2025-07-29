import heapq
from collections import defaultdict, deque

def optimal_evacuation(locations, evacuation_centers, roads):
    """
    Find the optimal evacuation route for residents to evacuation centers.
    
    Args:
        locations: List of tuples (location_id, resident_count)
        evacuation_centers: List of tuples (center_id, capacity)
        roads: List of tuples (location_id_1, location_id_2, travel_time)
    
    Returns:
        Dictionary mapping location_id to assigned center_id, or None if evacuation is impossible
    """
    # Check for empty inputs
    if not locations:
        return {}
    if not evacuation_centers or not roads:
        return None
    
    # Build the graph
    graph = defaultdict(list)
    for loc1, loc2, time in roads:
        graph[loc1].append((loc2, time))
        graph[loc2].append((loc1, time))  # Undirected graph
    
    # Check for disconnected locations
    location_ids = [loc[0] for loc in locations]
    center_ids = [center[0] for center in evacuation_centers]
    
    # Check if all locations can reach at least one evacuation center
    for loc_id in location_ids:
        if not can_reach_any_center(graph, loc_id, center_ids):
            return None
    
    # Create dictionaries for easier lookup
    location_dict = {loc[0]: loc[1] for loc in locations}
    center_dict = {center[0]: center[1] for center in evacuation_centers}
    
    # Check if total capacity is sufficient
    total_residents = sum(location_dict.values())
    total_capacity = sum(center_dict.values())
    if total_residents > total_capacity:
        return None
    
    # Calculate shortest paths from each location to each evacuation center
    shortest_paths = {}
    for loc_id in location_ids:
        distances = dijkstra(graph, loc_id)
        shortest_paths[loc_id] = {center_id: distances.get(center_id, float('inf')) 
                                 for center_id in center_ids}
    
    # Solve the assignment problem using minimum cost flow approach
    # (Implemented as a greedy algorithm with sorting)
    
    # Sort locations by number of residents (descending)
    loc_by_residents = sorted(locations, key=lambda x: x[1], reverse=True)
    
    # Initialize remaining capacities
    remaining_capacity = center_dict.copy()
    
    # Initialize assignment dictionary
    assignment = {}
    
    # Assign locations to centers based on shortest path and capacity constraints
    for loc_id, residents in loc_by_residents:
        # Calculate the cost (travel time * residents) for each center
        costs = [(center_id, shortest_paths[loc_id][center_id] * residents) 
                for center_id in center_ids 
                if shortest_paths[loc_id][center_id] != float('inf')]
        
        # Sort centers by cost (ascending)
        costs.sort(key=lambda x: x[1])
        
        # Try to assign to the center with the lowest cost and sufficient capacity
        assigned = False
        for center_id, _ in costs:
            if remaining_capacity[center_id] >= residents:
                assignment[loc_id] = center_id
                remaining_capacity[center_id] -= residents
                assigned = True
                break
        
        if not assigned:
            # If we couldn't assign directly, try to reassign some locations
            success = try_reassignment(assignment, shortest_paths, location_dict, 
                                     remaining_capacity, loc_id, residents)
            if not success:
                return None  # Evacuation is impossible with current capacities
    
    # If there are locations with 0 residents, assign them to any center
    for loc_id, residents in locations:
        if residents == 0 and loc_id not in assignment:
            for center_id in center_ids:
                if shortest_paths[loc_id][center_id] != float('inf'):
                    assignment[loc_id] = center_id
                    break
    
    # Final check that all locations are assigned
    if len(assignment) != len(locations):
        return None
    
    return assignment

def can_reach_any_center(graph, start, center_ids):
    """Check if a location can reach any evacuation center using BFS."""
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()
        
        if node in center_ids:
            return True
        
        for neighbor, _ in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False

def dijkstra(graph, start):
    """Compute shortest paths from start node to all other nodes."""
    distances = {start: 0}
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # If we've already found a better path, skip
        if current_distance > distances.get(current_node, float('inf')):
            continue
        
        # Check all neighbors
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            
            # If we found a better path, update it
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

def try_reassignment(assignment, shortest_paths, location_dict, remaining_capacity, new_loc_id, new_residents):
    """
    Try to reassign some locations to make room for a new location.
    
    Args:
        assignment: Current assignment dictionary
        shortest_paths: Dictionary of shortest paths from locations to centers
        location_dict: Dictionary of location_id to resident count
        remaining_capacity: Dictionary of center_id to remaining capacity
        new_loc_id: ID of the new location to assign
        new_residents: Number of residents at the new location
    
    Returns:
        Boolean indicating whether reassignment was successful
    """
    # Get all possible centers for the new location
    possible_centers = [center_id for center_id in remaining_capacity 
                       if shortest_paths[new_loc_id][center_id] != float('inf')]
    
    # Try each center
    for center_id in possible_centers:
        # How much more capacity do we need?
        needed_capacity = new_residents - remaining_capacity[center_id]
        
        if needed_capacity <= 0:
            # We have enough capacity already
            assignment[new_loc_id] = center_id
            remaining_capacity[center_id] -= new_residents
            return True
        
        # Find locations assigned to this center
        assigned_locs = [loc_id for loc_id, c_id in assignment.items() if c_id == center_id]
        
        # Calculate potential reassignments
        potential_moves = []
        for loc_id in assigned_locs:
            loc_residents = location_dict[loc_id]
            
            # Skip if this location doesn't have enough residents to help
            if loc_residents < needed_capacity:
                continue
            
            # Find alternative centers for this location
            for alt_center_id in remaining_capacity:
                if alt_center_id == center_id:
                    continue
                
                if shortest_paths[loc_id][alt_center_id] != float('inf') and \
                   remaining_capacity[alt_center_id] >= loc_residents:
                    
                    # Calculate cost difference of the move
                    current_cost = shortest_paths[loc_id][center_id] * loc_residents
                    new_cost = shortest_paths[loc_id][alt_center_id] * loc_residents
                    cost_diff = new_cost - current_cost
                    
                    potential_moves.append((loc_id, alt_center_id, loc_residents, cost_diff))
        
        # Sort by cost difference (prefer cheaper moves)
        potential_moves.sort(key=lambda x: x[3])
        
        # Try to make moves to free up enough capacity
        freed_capacity = 0
        successful_moves = []
        
        for loc_id, alt_center_id, loc_residents, _ in potential_moves:
            if freed_capacity >= needed_capacity:
                break
                
            # Perform move
            freed_capacity += loc_residents
            successful_moves.append((loc_id, alt_center_id, loc_residents))
        
        # If we can free enough capacity, make the moves
        if freed_capacity >= needed_capacity:
            for loc_id, alt_center_id, loc_residents in successful_moves:
                # Update assignment
                assignment[loc_id] = alt_center_id
                
                # Update capacities
                remaining_capacity[center_id] += loc_residents
                remaining_capacity[alt_center_id] -= loc_residents
            
            # Assign the new location
            assignment[new_loc_id] = center_id
            remaining_capacity[center_id] -= new_residents
            
            return True
    
    # If we couldn't find a valid reassignment
    return False