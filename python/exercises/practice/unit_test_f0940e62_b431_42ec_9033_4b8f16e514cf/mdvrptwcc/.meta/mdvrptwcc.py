import math

def solve_depot_routing(depots, customers, vehicle_capacity, vehicle_speed):
    # Create a mutable copy of unassigned customers
    unassigned = customers.copy()
    routes = []
    
    # Process each depot in the given order
    for depot in depots:
        vehicles_used = 0
        # For each available vehicle slot in the depot
        for _ in range(depot['num_vehicles']):
            if not unassigned:
                break
            current_route = []
            current_load = 0
            current_time = 0.0
            current_x = depot['x']
            current_y = depot['y']
            
            while True:
                best_candidate = None
                best_distance = None
                best_arrival_time = None
                # Iterate over a copy of unassigned customers
                for cust in unassigned:
                    # Check capacity constraint
                    if current_load + cust['demand'] > vehicle_capacity:
                        continue
                    # Compute travel distance and travel time to customer
                    dx = cust['x'] - current_x
                    dy = cust['y'] - current_y
                    distance = math.sqrt(dx * dx + dy * dy)
                    travel_time = distance / vehicle_speed
                    arrival_time = current_time + travel_time
                    # If arriving before time window starts, wait until tw_start
                    if arrival_time < cust['tw_start']:
                        arrival_time = cust['tw_start']
                    # Check time window constraint
                    if arrival_time > cust['tw_end']:
                        continue
                    # Select the candidate with the smallest travel distance
                    if best_candidate is None or distance < best_distance:
                        best_candidate = cust
                        best_distance = distance
                        best_arrival_time = arrival_time
                # If no candidate is feasible, break from the route construction loop
                if best_candidate is None:
                    break
                # Add the best candidate to the current route
                current_route.append(best_candidate['id'])
                current_load += best_candidate['demand']
                current_time = best_arrival_time
                current_x = best_candidate['x']
                current_y = best_candidate['y']
                unassigned.remove(best_candidate)
            # If a route has been constructed, append it to routes list
            if current_route:
                routes.append((depot['id'], current_route))
            vehicles_used += 1
            if not unassigned:
                break
        if not unassigned:
            break
    # Check if all customers have been assigned
    if unassigned:
        raise ValueError("Cannot assign all customers with given vehicles and constraints")
    return routes