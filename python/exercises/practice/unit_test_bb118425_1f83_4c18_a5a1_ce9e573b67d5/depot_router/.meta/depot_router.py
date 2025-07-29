def optimize_routes(depots, customers, distance_matrix, vehicle_capacity, max_route_duration):
    # Number of depots and customers
    num_depots = len(depots)
    num_customers = len(customers)
    # Set of unassigned customer indices
    remaining_customers = set(range(num_customers))
    # Available vehicles per depot (copy from depots: index 2 is num_vehicles)
    available_vehicles = [depot[2] for depot in depots]
    result = []
    depot_count = num_depots  # In distance matrix, depots indices: 0..num_depots-1, customers: num_depots..num_depots+num_customers-1

    # Function to attempt building a route for a given depot index.
    def build_route(depot_index):
        # Starting point: depot_index for distance matrix, route variables.
        current_time = 0
        current_load = 0
        current_resource = 0  # travel time + service time (waiting time is not counted)
        current_location = depot_index  # current location index in distance_matrix
        route = []
        # Loop to add customers greedily
        while True:
            candidate = None
            candidate_metric = None
            candidate_new_time = None
            candidate_new_resource = None
            # Evaluate each remaining customer
            for j in list(remaining_customers):
                cust = customers[j]
                # cust = (lat, lon, demand, T_start, T_end, service_time, depot_preference_list)
                # Check depot preference
                if depot_index not in cust[6]:
                    continue
                # Compute travel time from current location to customer j.
                travel_time = distance_matrix[current_location][depot_count + j]
                arrival_time = current_time + travel_time
                # Wait if arriving before time window opens
                service_start = arrival_time if arrival_time >= cust[3] else cust[3]
                # If service cannot start within time window, skip
                if service_start > cust[4]:
                    continue
                finish_time = service_start + cust[5]
                # Check capacity constraint
                if current_load + cust[2] > vehicle_capacity:
                    continue
                # Compute new resource usage (travel_time + service time is added; waiting time not counted)
                new_resource = current_resource + travel_time + cust[5]
                # Check resource constraint: include return travel time to depot.
                return_to_depot = distance_matrix[depot_count + j][depot_index]
                if new_resource + return_to_depot > depots[depot_index][3]:
                    continue
                # Check route duration: finishing service plus travel back to depot must be within max_route_duration.
                if finish_time + return_to_depot > max_route_duration:
                    continue
                # Use travel_time as metric for greedy selection.
                if candidate is None or travel_time < candidate_metric:
                    candidate = j
                    candidate_metric = travel_time
                    candidate_new_time = finish_time
                    candidate_new_resource = new_resource
            if candidate is None:
                break
            # Assign candidate to route
            route.append(candidate)
            remaining_customers.remove(candidate)
            current_time = candidate_new_time
            current_resource = candidate_new_resource
            current_load += customers[candidate][2]
            current_location = depot_count + candidate
        return route

    progress = True
    # Continue while there are customers remaining and progress can be made.
    while remaining_customers and progress:
        progress = False
        # For each depot, if vehicles are available, try to build one route.
        for depot_index in range(num_depots):
            while available_vehicles[depot_index] > 0:
                route = build_route(depot_index)
                if not route:
                    break
                result.append((depot_index, route))
                available_vehicles[depot_index] -= 1
                progress = True
        # If no progress was made in this round, break out.
        if not progress:
            break

    # If not all customers are assigned, no valid solution is possible.
    if remaining_customers:
        return []
    return result

if __name__ == "__main__":
    # A simple test run
    depots = [(37.7749, -122.4194, 2, 480)]
    customers = [(37.7833, -122.4094, 10, 60, 120, 15, [0]),
                 (37.7937, -122.3962, 20, 180, 240, 30, [0])]
    distance_matrix = [
        [0,   10, 15],
        [10,  0,   8],
        [15,  8,   0]
    ]
    vehicle_capacity = 30
    max_route_duration = 400
    routes = optimize_routes(depots, customers, distance_matrix, vehicle_capacity, max_route_duration)
    print(routes)