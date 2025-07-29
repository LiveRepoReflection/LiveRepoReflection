import heapq
from collections import defaultdict, deque
from itertools import permutations

def find_optimal_routes(graph, distribution_centers, delivery_locations):
    """
    Find optimal routes for delivery vehicles from multiple distribution centers.
    
    Args:
        graph: A dictionary representing the road network as an adjacency list with edge weights
        distribution_centers: A dictionary with centers as keys and vehicle information as values
        delivery_locations: A dictionary with locations as keys and delivery details as values
    
    Returns:
        A list of routes, where each route contains vehicle details, path, start times, and cost
    """
    # Compute shortest paths from all nodes to all other nodes
    shortest_paths, distances = compute_all_shortest_paths(graph)
    
    # Get all available vehicles
    vehicles = []
    for center, info in distribution_centers.items():
        for v in info['vehicles']:
            vehicles.append({
                'center': center,
                'capacity': v['capacity'],
                'cost_per_distance': v['cost_per_distance']
            })
    
    # Initialize the solution
    best_routes = []
    remaining_locations = set(delivery_locations.keys())
    
    # Sort vehicles by capacity (descending) to try to use larger vehicles first
    vehicles.sort(key=lambda v: v['capacity'], reverse=True)
    
    for vehicle in vehicles:
        # If all locations are covered, we're done
        if not remaining_locations:
            break
        
        # Find the best route for this vehicle
        best_route = find_best_route_for_vehicle(
            vehicle, 
            remaining_locations, 
            delivery_locations, 
            shortest_paths, 
            distances
        )
        
        if best_route and best_route['route'][1:]:  # If we found a non-empty route
            best_routes.append(best_route)
            # Remove the served locations from the remaining set
            remaining_locations -= set(best_route['route'][1:])
    
    return best_routes

def compute_all_shortest_paths(graph):
    """
    Compute shortest paths between all pairs of nodes using Floyd-Warshall algorithm.
    
    Args:
        graph: A dictionary representing the road network
    
    Returns:
        shortest_paths: Dictionary mapping (source, target) to the next node in the path
        distances: Dictionary mapping (source, target) to the shortest distance
    """
    # Initialize distance and path matrices
    distances = {}
    shortest_paths = {}
    
    # Set initial distances
    for u in graph:
        for v in graph:
            if u == v:
                distances[(u, v)] = 0
                shortest_paths[(u, v)] = None
            elif v in graph[u]:
                distances[(u, v)] = graph[u][v]
                shortest_paths[(u, v)] = v
            else:
                distances[(u, v)] = float('inf')
                shortest_paths[(u, v)] = None
    
    # Floyd-Warshall algorithm
    for k in graph:
        for i in graph:
            for j in graph:
                if distances[(i, k)] + distances[(k, j)] < distances[(i, j)]:
                    distances[(i, j)] = distances[(i, k)] + distances[(k, j)]
                    shortest_paths[(i, j)] = shortest_paths[(i, k)]
    
    return shortest_paths, distances

def reconstruct_path(source, target, shortest_paths):
    """
    Reconstruct the shortest path from source to target.
    
    Args:
        source: Source node
        target: Target node
        shortest_paths: Dictionary mapping (source, target) to the next node
    
    Returns:
        A list representing the path from source to target
    """
    if shortest_paths[(source, target)] is None:
        return []
    
    path = [source]
    while source != target:
        source = shortest_paths[(source, target)]
        if source is None:  # No path exists
            return []
        path.append(source)
    
    return path

def calculate_route_cost(route, vehicle, delivery_locations, distances):
    """
    Calculate the total cost of a route, including travel and waiting costs.
    
    Args:
        route: List of nodes representing the route
        vehicle: Dictionary with vehicle details
        delivery_locations: Dictionary with delivery details
        distances: Dictionary mapping (source, target) to the distance
    
    Returns:
        A dictionary with start_times at each location and total cost
    """
    start_times = [0]  # Start time at the distribution center is 0
    current_time = 0
    travel_cost = 0
    waiting_cost = 0
    
    for i in range(1, len(route)):
        prev_node = route[i-1]
        curr_node = route[i]
        
        # Calculate travel time (using distance as a proxy for time)
        travel_time = distances[(prev_node, curr_node)]
        
        # Update current time
        current_time += travel_time
        
        # Check if we need to wait
        if curr_node in delivery_locations:
            time_window = delivery_locations[curr_node]['time_window']
            if current_time < time_window[0]:
                waiting_time = time_window[0] - current_time
                waiting_cost += waiting_time * delivery_locations[curr_node]['waiting_cost']
                current_time = time_window[0]
            
            # Check if we're too late (after time window)
            if current_time > time_window[1]:
                return None  # Route is infeasible
        
        start_times.append(current_time)
        
        # Update travel cost
        travel_cost += travel_time * vehicle['cost_per_distance']
    
    return {
        'start_times': start_times,
        'total_cost': travel_cost + waiting_cost
    }

def check_capacity_constraint(route, vehicle, delivery_locations):
    """
    Check if the route satisfies the vehicle capacity constraint.
    
    Args:
        route: List of nodes representing the route
        vehicle: Dictionary with vehicle details
        delivery_locations: Dictionary with delivery details
    
    Returns:
        Boolean indicating if the route satisfies the capacity constraint
    """
    total_demand = sum(delivery_locations[node]['demand'] for node in route[1:] if node in delivery_locations)
    return total_demand <= vehicle['capacity']

def find_best_route_for_vehicle(vehicle, locations, delivery_locations, shortest_paths, distances):
    """
    Find the best route for a vehicle using a greedy approach with improvements.
    
    Args:
        vehicle: Dictionary with vehicle details
        locations: Set of remaining delivery locations
        delivery_locations: Dictionary with delivery details
        shortest_paths: Dictionary mapping (source, target) to the next node
        distances: Dictionary mapping (source, target) to the distance
    
    Returns:
        A dictionary with route details or None if no feasible route is found
    """
    center = vehicle['center']
    
    # Filter out locations that are unreachable from this center
    reachable_locations = {loc for loc in locations if shortest_paths[(center, loc)] is not None}
    
    if not reachable_locations:
        return None  # No reachable locations from this center
    
    best_route = None
    best_cost = float('inf')
    
    # For small numbers of locations, try all permutations
    if len(reachable_locations) <= 8:  # Limit for permutations to avoid excessive computation
        for subset_size in range(1, min(len(reachable_locations) + 1, 4)):  # Limit subset size for efficiency
            for subset in combinations(reachable_locations, subset_size):
                for perm in permutations(subset):
                    route = [center] + list(perm)
                    
                    # Check capacity constraint
                    if not check_capacity_constraint(route, vehicle, delivery_locations):
                        continue
                    
                    # Reconstruct full path with intermediate nodes
                    full_route = [center]
                    for i in range(1, len(route)):
                        full_path = reconstruct_path(route[i-1], route[i], shortest_paths)
                        if not full_path:  # No path exists
                            continue
                        full_route.extend(full_path[1:])  # Exclude the first node to avoid duplication
                    
                    # Calculate cost
                    cost_info = calculate_route_cost(route, vehicle, delivery_locations, distances)
                    if cost_info and cost_info['total_cost'] < best_cost:
                        best_route = {
                            'route': route,
                            'start_times': cost_info['start_times'],
                            'total_cost': cost_info['total_cost'],
                            'vehicle': vehicle
                        }
                        best_cost = cost_info['total_cost']
    else:
        # For larger problems, use a nearest-neighbor heuristic with improvements
        best_route = nearest_neighbor_with_improvements(
            center, 
            reachable_locations, 
            vehicle, 
            delivery_locations, 
            shortest_paths, 
            distances
        )
    
    return best_route

def combinations(iterable, r):
    """
    Return r length subsequences of elements from the input iterable.
    
    Args:
        iterable: Input iterable
        r: Length of subsequences
    
    Returns:
        Generator yielding combinations
    """
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

def nearest_neighbor_with_improvements(center, locations, vehicle, delivery_locations, shortest_paths, distances):
    """
    Implement a nearest-neighbor heuristic with improvements for finding routes.
    
    Args:
        center: Starting distribution center
        locations: Set of delivery locations
        vehicle: Dictionary with vehicle details
        delivery_locations: Dictionary with delivery details
        shortest_paths: Dictionary mapping (source, target) to the next node
        distances: Dictionary mapping (source, target) to the distance
    
    Returns:
        A dictionary with route details or None if no feasible route is found
    """
    # Start with an empty route
    route = [center]
    remaining_capacity = vehicle['capacity']
    current_time = 0
    start_times = [0]
    
    # Copy locations to a list for iteration
    available_locations = list(locations)
    
    while available_locations:
        best_next = None
        best_cost = float('inf')
        best_time = 0
        
        current_node = route[-1]
        
        for loc in available_locations:
            # Check if location is reachable
            if shortest_paths[(current_node, loc)] is None:
                continue
            
            # Check capacity constraint
            if delivery_locations[loc]['demand'] > remaining_capacity:
                continue
            
            # Calculate arrival time
            travel_time = distances[(current_node, loc)]
            arrival_time = current_time + travel_time
            
            # Check time window
            time_window = delivery_locations[loc]['time_window']
            actual_arrival = max(arrival_time, time_window[0])
            
            if actual_arrival > time_window[1]:
                continue  # Exceeds time window
            
            # Calculate cost (including waiting)
            waiting_time = max(0, time_window[0] - arrival_time)
            waiting_cost = waiting_time * delivery_locations[loc]['waiting_cost']
            travel_cost = travel_time * vehicle['cost_per_distance']
            total_cost = travel_cost + waiting_cost
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_next = loc
                best_time = actual_arrival
        
        if best_next is None:
            break  # No feasible next location
        
        # Add best next location to route
        route.append(best_next)
        start_times.append(best_time)
        current_time = best_time
        remaining_capacity -= delivery_locations[best_next]['demand']
        available_locations.remove(best_next)
    
    if len(route) == 1:  # Only contains the center
        return None
    
    # Calculate total cost of the route
    cost_info = calculate_route_cost(route, vehicle, delivery_locations, distances)
    if not cost_info:
        return None
    
    return {
        'route': route,
        'start_times': cost_info['start_times'],
        'total_cost': cost_info['total_cost'],
        'vehicle': vehicle
    }