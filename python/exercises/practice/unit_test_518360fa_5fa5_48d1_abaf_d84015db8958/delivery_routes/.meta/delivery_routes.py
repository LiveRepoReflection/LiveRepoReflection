import math
import heapq
from collections import defaultdict

def haversine(coord1, coord2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Radius of Earth in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

def calculate_distance_matrix(hubs, delivery_points):
    """
    Calculate distance matrix between all locations (hubs and delivery points)
    """
    # Create a list of all locations
    hub_locations = [(hub_id, location) for hub_id, location, _, _ in hubs]
    point_locations = [(point_id, location) for point_id, location, _ in delivery_points]
    
    # Calculate distances
    dist_matrix = {}
    
    # Hub to point distances
    for hub_id, hub_loc in hub_locations:
        hub_key = f'h{hub_id}'
        dist_matrix[hub_key] = {}
        for point_id, point_loc in point_locations:
            point_key = f'p{point_id}'
            distance = haversine(hub_loc, point_loc)
            dist_matrix[hub_key][point_key] = distance
            
            # Initialize point-to-hub distances too
            if point_key not in dist_matrix:
                dist_matrix[point_key] = {}
            dist_matrix[point_key][hub_key] = distance
    
    # Point to point distances
    for i, (point_id1, point_loc1) in enumerate(point_locations):
        point_key1 = f'p{point_id1}'
        if point_key1 not in dist_matrix:
            dist_matrix[point_key1] = {}
            
        for j, (point_id2, point_loc2) in enumerate(point_locations):
            if i == j:
                continue  # Skip same point
                
            point_key2 = f'p{point_id2}'
            distance = haversine(point_loc1, point_loc2)
            dist_matrix[point_key1][point_key2] = distance
    
    return dist_matrix

def nearest_insertion_tsp(dist_matrix, start_key, points_to_visit):
    """
    Solve the TSP using the nearest insertion heuristic.
    Returns the ordered route and its total distance.
    """
    if not points_to_visit:
        return [], 0
        
    # Start with a route from the hub to the nearest point and back
    min_dist = float('inf')
    nearest_point = None
    for point in points_to_visit:
        dist = dist_matrix[start_key][point]
        if dist < min_dist:
            min_dist = dist
            nearest_point = point
            
    # If no points to visit, return empty route
    if nearest_point is None:
        return [], 0
        
    route = [nearest_point]
    remaining_points = set(points_to_visit)
    remaining_points.remove(nearest_point)
    
    # Total distance for the first point (hub -> point -> hub)
    total_distance = dist_matrix[start_key][nearest_point] + dist_matrix[nearest_point][start_key]
    
    # Iteratively insert the remaining points
    while remaining_points:
        best_insertion = None
        best_increase = float('inf')
        
        # For each remaining point
        for point in remaining_points:
            # Try inserting at each position in the current route
            for i in range(len(route) + 1):
                # Calculate the increase in distance
                if i == 0:
                    # Insert at the beginning
                    increase = (dist_matrix[start_key][point] + 
                               dist_matrix[point][route[0]] - 
                               dist_matrix[start_key][route[0]])
                elif i == len(route):
                    # Insert at the end
                    increase = (dist_matrix[route[-1]][point] + 
                               dist_matrix[point][start_key] - 
                               dist_matrix[route[-1]][start_key])
                else:
                    # Insert in the middle
                    increase = (dist_matrix[route[i-1]][point] + 
                               dist_matrix[point][route[i]] - 
                               dist_matrix[route[i-1]][route[i]])
                
                if increase < best_increase:
                    best_increase = increase
                    best_insertion = (point, i)
        
        if best_insertion:
            point, position = best_insertion
            route.insert(position, point)
            remaining_points.remove(point)
            total_distance += best_increase
    
    return route, total_distance

def savings_algorithm(hub_key, dist_matrix, delivery_points, max_capacity):
    """
    Clarke and Wright savings algorithm for VRP.
    Returns a list of routes where each route is a list of delivery point IDs.
    """
    # Extract point IDs and demands
    point_demands = {p[0]: p[2] for p in delivery_points}
    
    # Create a lookup from point_id to point_key
    point_id_to_key = {p[0]: f'p{p[0]}' for p in delivery_points}
    point_key_to_id = {f'p{p[0]}': p[0] for p in delivery_points}
    
    # Calculate savings for all pairs of points
    savings = []
    for i in range(len(delivery_points)):
        for j in range(i + 1, len(delivery_points)):
            point_i, point_j = delivery_points[i], delivery_points[j]
            key_i, key_j = f'p{point_i[0]}', f'p{point_j[0]}'
            
            # Savings: d(hub, i) + d(hub, j) - d(i, j)
            saving = (dist_matrix[hub_key][key_i] + 
                      dist_matrix[hub_key][key_j] - 
                      dist_matrix[key_i][key_j])
            
            heapq.heappush(savings, (-saving, point_i[0], point_j[0]))  # Negative for max-heap
    
    # Initialize each point as a separate route
    routes = {}  # route_id -> [point_ids]
    point_to_route = {}  # point_id -> route_id
    route_demands = {}  # route_id -> total demand
    
    next_route_id = 0
    for point in delivery_points:
        point_id = point[0]
        demand = point[2]
        
        if demand <= max_capacity:  # Skip points with demand > max_capacity
            route_id = next_route_id
            routes[route_id] = [point_id]
            point_to_route[point_id] = route_id
            route_demands[route_id] = demand
            next_route_id += 1
    
    # Merge routes based on savings
    while savings:
        _, point_i_id, point_j_id = heapq.heappop(savings)
        
        # Skip if points are already in the same route or not in any route
        if point_i_id not in point_to_route or point_j_id not in point_to_route:
            continue
            
        route_i = point_to_route[point_i_id]
        route_j = point_to_route[point_j_id]
        
        if route_i == route_j:
            continue
        
        # Check if merge is feasible
        if route_demands[route_i] + route_demands[route_j] <= max_capacity:
            # Determine if point_i is at the end of its route
            route_i_points = routes[route_i]
            is_i_at_end = route_i_points[-1] == point_i_id
            
            # Determine if point_j is at the beginning of its route
            route_j_points = routes[route_j]
            is_j_at_start = route_j_points[0] == point_j_id
            
            # Only merge if point_i is at end and point_j is at start
            if is_i_at_end and is_j_at_start:
                # Merge routes
                merged_route = route_i_points + route_j_points
                routes[route_i] = merged_route
                route_demands[route_i] += route_demands[route_j]
                
                # Update point_to_route for the points in route_j
                for point_id in route_j_points:
                    point_to_route[point_id] = route_i
                
                # Remove route_j
                del routes[route_j]
                del route_demands[route_j]
    
    # Convert routes dict to list of routes
    return [routes[r_id] for r_id in routes]

def assign_delivery_points_to_hubs(hubs, delivery_points, max_vehicle_capacity):
    """
    Assign delivery points to hubs based on proximity and capacity constraints.
    Returns a dictionary mapping hub_id -> list of assigned delivery points.
    """
    # Calculate distances from each hub to each delivery point
    hub_to_point_distances = []
    for hub_id, hub_loc, hub_capacity, _ in hubs:
        for point_id, point_loc, point_demand in delivery_points:
            if point_demand <= max_vehicle_capacity:  # Skip points that exceed vehicle capacity
                distance = haversine(hub_loc, point_loc)
                hub_to_point_distances.append((distance, hub_id, point_id, point_demand))
    
    # Sort by distance
    hub_to_point_distances.sort()
    
    # Assign points to hubs
    hub_assignments = defaultdict(list)
    hub_remaining_capacity = {h[0]: h[2] for h in hubs}
    assigned_points = set()
    
    for distance, hub_id, point_id, point_demand in hub_to_point_distances:
        if point_id in assigned_points:
            continue
            
        if hub_remaining_capacity[hub_id] >= point_demand:
            hub_assignments[hub_id].append((point_id, point_demand))
            hub_remaining_capacity[hub_id] -= point_demand
            assigned_points.add(point_id)
    
    # Convert to the desired format
    result = {}
    for hub_id, points in hub_assignments.items():
        result[hub_id] = [(p_id, p_demand) for p_id, p_demand in points]
    
    return result

def optimize_routes(hubs, delivery_points, max_vehicle_capacity):
    """
    Optimize delivery routes for a network of hubs and delivery points.
    Returns a dictionary mapping hub_id -> list of routes.
    """
    # Step 1: Assign delivery points to hubs
    hub_assignments = assign_delivery_points_to_hubs(hubs, delivery_points, max_vehicle_capacity)
    
    # Create a lookup for delivery points
    delivery_point_lookup = {p[0]: p for p in delivery_points}
    
    # Step 2: For each hub, solve the VRP using a two-phase approach
    final_routes = {}
    
    for hub_id, hub_data in [(h[0], h) for h in hubs if h[0] in hub_assignments]:
        hub_location = hub_data[1]
        max_vehicles = hub_data[3]
        
        # Get the assigned points for this hub
        assigned_points = hub_assignments[hub_id]
        if not assigned_points:
            continue
            
        assigned_point_details = [delivery_point_lookup[p_id] for p_id, _ in assigned_points]
        
        # Calculate distance matrix for this hub and its assigned points
        dist_matrix = calculate_distance_matrix([hub_data], assigned_point_details)
        
        hub_key = f'h{hub_id}'
        point_keys = [f'p{p[0]}' for p in assigned_point_details]
        
        # Use the savings algorithm to create initial routes
        initial_routes = savings_algorithm(hub_key, dist_matrix, assigned_point_details, max_vehicle_capacity)
        
        # Limit to the max number of vehicles
        if len(initial_routes) > max_vehicles:
            # Sort routes by total demand (descending) to prioritize larger routes
            route_demands = []
            for route in initial_routes:
                total_demand = sum(delivery_point_lookup[point_id][2] for point_id in route)
                route_demands.append((total_demand, route))
            
            route_demands.sort(reverse=True)
            initial_routes = [r for _, r in route_demands[:max_vehicles]]
        
        # Optimize each route using TSP
        optimized_routes = []
        for route in initial_routes:
            # Skip empty routes
            if not route:
                continue
                
            # Convert point IDs to keys for the distance matrix
            route_keys = [f'p{point_id}' for point_id in route]
            
            # Optimize the route order
            optimized_route, _ = nearest_insertion_tsp(dist_matrix, hub_key, route_keys)
            
            # Convert back from keys to point IDs
            optimized_point_ids = [int(key[1:]) for key in optimized_route]
            optimized_routes.append(optimized_point_ids)
        
        final_routes[hub_id] = optimized_routes
    
    return final_routes