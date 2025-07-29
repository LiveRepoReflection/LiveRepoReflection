import math

def solve(depots, customers, distance_matrix, dynamic_events):
    # Merge initial customers and dynamic events into one list.
    # Each customer is a tuple: (customer_id, x, y, demand, service_time_window_start, service_time_window_end)
    merged_customers = []
    for cust in customers:
        merged_customers.append(cust)
    for event in dynamic_events:
        # event: (arrival_time, customer_id, x, y, demand, service_time_window_start, service_time_window_end)
        merged_customers.append((event[1], event[2], event[3], event[4], event[5], event[6]))
    
    # Number of depots
    N = len(depots)
    # Total number of customers after merging.
    total_customers = len(merged_customers)
    # Each customer in the distance matrix is represented with an index offset of N
    # Create an indexed list of customers: (relative_index, customer_tuple)
    customer_indices = [(i, merged_customers[i]) for i in range(total_customers)]
    
    # Assign each customer to the nearest depot based on the provided distance matrix.
    # The distance from depot at index i (0 <= i < N) to a customer at merged index j is distance_matrix[i][N + j].
    assigned = {i: [] for i in range(N)}
    for j, cust in customer_indices:
        best_depot = None
        best_distance = float('inf')
        for i in range(N):
            d = distance_matrix[i][N + j]
            if d < best_distance:
                best_distance = d
                best_depot = i
        assigned[best_depot].append((j, cust))
    
    total_cost = 0.0
    # For each depot, partition the assigned customers into routes based on vehicle capacity.
    # Then determine the route order using a greedy nearest-neighbor approach.
    for i, depot in enumerate(depots):
        # depot is a tuple:
        # (depot_id, x_coordinate, y_coordinate, num_vehicles, vehicle_capacity, vehicle_cost_per_distance, start_time_window_start, start_time_window_end)
        depot_id, dx, dy, num_vehicles, capacity, cost_factor, depot_tw_start, depot_tw_end = depot
        
        # Sort assigned customers by distance from the depot.
        assigned[i].sort(key=lambda x: distance_matrix[i][N + x[0]])
        
        # Partition customers into routes; each route must not exceed the vehicle's capacity.
        routes = []
        current_route = []
        current_capacity = 0
        for j, cust in assigned[i]:
            # cust is (customer_id, x, y, demand, service_time_window_start, service_time_window_end)
            cust_id, cx, cy, demand, tw_start, tw_end = cust
            if current_capacity + demand > capacity:
                if current_route:
                    routes.append(current_route)
                current_route = [(j, cust)]
                current_capacity = demand
            else:
                current_route.append((j, cust))
                current_capacity += demand
        if current_route:
            routes.append(current_route)
        
        # For each route, compute the route order using a greedy nearest neighbor method and add the route cost.
        for route in routes:
            if not route:
                continue
            unvisited = route[:]
            route_order = []
            # Start from depot: depot’s location index is i in the distance matrix.
            current_index = i  
            while unvisited:
                best = None
                best_dist = float('inf')
                for item in unvisited:
                    j, cust = item
                    dist = distance_matrix[current_index][N + j]
                    if dist < best_dist:
                        best_dist = dist
                        best = item
                route_order.append(best)
                # Update current_index to the customer’s index in the matrix, which is (N + j)
                current_index = N + best[0]
                unvisited.remove(best)
            # Compute route distance: from depot -> customer1 -> customer2 -> ... -> customer_k -> depot.
            route_distance = 0.0
            curr_location = i
            for j, cust in route_order:
                route_distance += distance_matrix[curr_location][N + j]
                curr_location = N + j
            route_distance += distance_matrix[curr_location][i]  # returning to depot
            # Multiply by vehicle cost per distance.
            total_cost += route_distance * cost_factor

    return total_cost

if __name__ == '__main__':
    # Example manual test run (not used in unit tests)
    depots = [
        (0, 0, 0, 1, 100, 1.0, 0, 1000)
    ]
    customers = [
        (101, 10, 0, 10, 0, 1000)
    ]
    dynamic_events = [
        (30, 102, 20, 0, 10, 50, 150)
    ]
    # Create a simple distance matrix:
    # Number of depots = 1, number of customers = initial 1 + 1 dynamic = 2
    # Matrix size = (1+2) x (1+2) = 3x3. Indices: 0 -> depot, 1 -> initial customer, 2 -> dynamic customer.
    distance_matrix = [
        [0.0, 10.0, 20.0],
        [10.0, 0.0, 10.0],
        [20.0, 10.0, 0.0]
    ]
    print(solve(depots, customers, distance_matrix, dynamic_events))