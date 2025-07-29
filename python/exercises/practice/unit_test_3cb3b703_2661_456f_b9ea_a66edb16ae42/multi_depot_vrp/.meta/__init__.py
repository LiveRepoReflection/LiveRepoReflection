def solve_vrp(depots, customers, travel_time_matrix):
    num_depots = len(depots)
    # Initial assignment: assign each customer to the nearest depot
    assigned_to_depot = {i: [] for i in range(num_depots)}
    for ci, cust in enumerate(customers):
        best_depot = None
        best_time = float('inf')
        for di, depot in enumerate(depots):
            t = travel_time_matrix[di][num_depots + ci]
            if t < best_time:
                best_time = t
                best_depot = di
        assigned_to_depot[best_depot].append(ci)

    result = []
    # For each depot, create routes using a greedy insertion heuristic.
    for di, depot in enumerate(depots):
        # Sort assigned customers by their time_window_start.
        assigned = assigned_to_depot[di]
        assigned.sort(key=lambda ci: customers[ci]['time_window_start'])
        routes = []
        used_routes = 0

        # Create routes until either all customers are scheduled or vehicles are exhausted.
        while assigned and used_routes < depot['vehicle_count']:
            route = []
            current_loc = di  # start at depot. For travel_time_matrix, depot indices: 0 .. num_depots-1.
            current_time = 0.0
            load = 0
            # Greedily append feasible customers.
            while True:
                best_customer = None
                best_cost = float('inf')
                best_arrival = None
                for cust_index in assigned:
                    travel = travel_time_matrix[current_loc][num_depots + cust_index]
                    arrival = current_time + travel
                    # If arriving before time window, must wait.
                    start_time = max(arrival, customers[cust_index]['time_window_start'])
                    if start_time > customers[cust_index]['time_window_end']:
                        continue
                    if load + customers[cust_index]['demand'] > depot['vehicle_capacity']:
                        continue
                    if travel < best_cost:
                        best_cost = travel
                        best_customer = cust_index
                        best_arrival = start_time
                if best_customer is None:
                    break
                route.append(best_customer)
                load += customers[best_customer]['demand']
                current_time = best_arrival
                current_loc = num_depots + best_customer
                assigned.remove(best_customer)
            routes.append(route)
            used_routes += 1

        # Try to insert any remaining customers into existing routes if possible.
        remaining = list(assigned)
        for cust_index in remaining:
            inserted = False
            for route in routes:
                if route:
                    # Simulate the current route.
                    current_load = sum(customers[c]['demand'] for c in route)
                    current_time = 0.0
                    current_loc = di
                    for c in route:
                        travel = travel_time_matrix[current_loc][num_depots + c]
                        current_time = max(current_time + travel, customers[c]['time_window_start'])
                        current_loc = num_depots + c
                    travel = travel_time_matrix[current_loc][num_depots + cust_index]
                    arrival = current_time + travel
                else:
                    current_load = 0
                    travel = travel_time_matrix[di][num_depots + cust_index]
                    arrival = travel
                start_time = max(arrival, customers[cust_index]['time_window_start'])
                if start_time > customers[cust_index]['time_window_end']:
                    continue
                if current_load + customers[cust_index]['demand'] > depot['vehicle_capacity']:
                    continue
                route.append(cust_index)
                inserted = True
                assigned.remove(cust_index)
                break
        # If there are still unscheduled customers and available vehicles, form new routes.
        while assigned and used_routes < depot['vehicle_count']:
            route = []
            current_loc = di
            current_time = 0.0
            load = 0
            while True:
                best_customer = None
                best_cost = float('inf')
                best_arrival = None
                for cust_index in assigned:
                    travel = travel_time_matrix[current_loc][num_depots + cust_index]
                    arrival = current_time + travel
                    start_time = max(arrival, customers[cust_index]['time_window_start'])
                    if start_time > customers[cust_index]['time_window_end']:
                        continue
                    if load + customers[cust_index]['demand'] > depot['vehicle_capacity']:
                        continue
                    if travel < best_cost:
                        best_cost = travel
                        best_customer = cust_index
                        best_arrival = start_time
                if best_customer is None:
                    break
                route.append(best_customer)
                load += customers[best_customer]['demand']
                current_time = best_arrival
                current_loc = num_depots + best_customer
                assigned.remove(best_customer)
            routes.append(route)
            used_routes += 1

        # Remove empty routes.
        routes = [r for r in routes if r]
        result.append({
            "depot_id": di,
            "routes": routes
        })

    # Final check: if any customer remains unassigned across all depots, assign them arbitrarily.
    all_served = []
    for depot_sol in result:
        for route in depot_sol["routes"]:
            all_served.extend(route)
    unassigned = set(range(len(customers))) - set(all_served)
    if unassigned:
        for cust_index in unassigned:
            for depot_id, depot in enumerate(depots):
                # Try to add to an existing route at the end if feasible.
                placed = False
                for sol in result:
                    if sol["depot_id"] != depot_id:
                        continue
                    for route in sol["routes"]:
                        current_load = sum(customers[c]['demand'] for c in route)
                        current_time = 0.0
                        current_loc = depot_id
                        for c in route:
                            travel = travel_time_matrix[current_loc][num_depots + c]
                            current_time = max(current_time + travel, customers[c]['time_window_start'])
                            current_loc = num_depots + c
                        travel = travel_time_matrix[current_loc][num_depots + cust_index]
                        arrival = current_time + travel
                        start_time = max(arrival, customers[cust_index]['time_window_start'])
                        if start_time > customers[cust_index]['time_window_end']:
                            continue
                        if current_load + customers[cust_index]['demand'] > depot['vehicle_capacity']:
                            continue
                        route.append(cust_index)
                        placed = True
                        break
                    if placed:
                        break
                if placed:
                    break
    return result