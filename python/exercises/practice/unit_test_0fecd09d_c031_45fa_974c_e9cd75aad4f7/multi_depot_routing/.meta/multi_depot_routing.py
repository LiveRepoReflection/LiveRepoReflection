import math

def plan_routes(depots, delivery_requests, distance_matrix, vehicle_speed, service_time):
    # Build mappings for depots and deliveries to indices in the distance matrix.
    # Depots are at indices 0 to len(depots)-1.
    depot_index = {}
    for idx, depot in enumerate(depots):
        depot_id, capacity, vehicles, location = depot
        depot_index[depot_id] = idx

    # Deliveries are at indices len(depots) to len(depots) + len(delivery_requests) - 1.
    delivery_index = {}
    delivery_dict = {}
    for idx, req in enumerate(delivery_requests):
        request_id, package_size, time_window, location = req
        delivery_index[request_id] = len(depots) + idx
        delivery_dict[request_id] = {
            'package_size': package_size,
            'time_window': time_window,
            'location': location
        }

    # Create route state for each available vehicle at each depot.
    # Each route state is a dictionary with:
    # 'depot': depot_id,
    # 'route': list of ids, initially [depot, depot] representing start and end,
    # 'load': current load of packages,
    # 'time': current departure time from the last visited node,
    # 'depot_capacity': capacity for this vehicle,
    # 'closed': whether no further deliveries can be added.
    routes = []
    for depot in depots:
        depot_id, capacity, vehicles, location = depot
        for _ in range(vehicles):
            routes.append({
                'depot': depot_id,
                'route': [depot_id, depot_id],
                'load': 0,
                'time': 0.0,
                'depot_capacity': capacity,
                'closed': False
            })

    # Set of unassigned delivery request ids.
    unassigned = set(delivery_dict.keys())

    # Greedy insertion: For each route, try to append a feasible delivery.
    # Continue until no further progress can be made.
    progress = True
    while unassigned and progress:
        progress = False
        for route in routes:
            if route['closed']:
                continue

            # Determine the current position and corresponding index in distance_matrix.
            # The current position is the last visited delivery (before the depot at the end)
            if len(route['route']) > 2:
                last_node_id = route['route'][-2]
                # Last node could be a delivery or a depot.
                # Since depot ids and delivery ids are in different ranges (assumed),
                # we check:
                if last_node_id in depot_index:
                    current_index = depot_index[last_node_id]
                else:
                    current_index = delivery_index[last_node_id]
            else:
                # Only the starting depot is in the route.
                last_node_id = route['route'][0]
                current_index = depot_index[last_node_id]

            best_candidate = None
            best_extra = None
            candidate_arrival_time = None

            # Look for a candidate delivery from the unassigned set that can be feasibly inserted at the end.
            for req_id in unassigned:
                delivery = delivery_dict[req_id]
                # Capacity check.
                if delivery['package_size'] > (route['depot_capacity'] - route['load']):
                    continue

                # Get matrix index for the delivery.
                d_index = delivery_index[req_id]
                travel_time = distance_matrix[current_index][d_index] / vehicle_speed
                arrival_time = route['time'] + travel_time
                # Wait if arriving before time window starts.
                if arrival_time < delivery['time_window'][0]:
                    arrival_time = delivery['time_window'][0]
                # Check that arrival is within the delivery's time window.
                if arrival_time > delivery['time_window'][1]:
                    continue

                # Use travel_time as a selection criterion (could be extra cost).
                if best_candidate is None or travel_time < best_extra:
                    best_candidate = req_id
                    best_extra = travel_time
                    candidate_arrival_time = arrival_time

            if best_candidate is not None:
                # Insert candidate: update route.
                # Remove the last depot id temporarily.
                route['route'].pop()
                route['route'].append(best_candidate)
                # Append the depot id at the end.
                route['route'].append(route['depot'])
                # Update route load and time.
                route['load'] += delivery_dict[best_candidate]['package_size']
                route['time'] = candidate_arrival_time + service_time
                unassigned.remove(best_candidate)
                progress = True
            else:
                # No candidate found, mark route as closed.
                route['closed'] = True

    # If there are still unassigned deliveries, they are infeasible under the current heuristic.
    # For the purpose of this solution, we assume inputs are such that all deliveries can be assigned.
    if unassigned:
        raise ValueError("Not all deliveries could be assigned under the current constraints.")

    # Return routes that have at least one delivery.
    result = []
    for route in routes:
        # Only include routes that have a delivery assigned (i.e., route length > 2).
        if len(route['route']) > 2:
            result.append(route['route'])
    return result