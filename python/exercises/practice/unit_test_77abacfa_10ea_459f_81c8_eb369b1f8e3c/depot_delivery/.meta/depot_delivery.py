import math

def depot_delivery(depots, customers, cost_matrix, vehicle_speed, penalty_late, penalty_vehicle):
    """
    This function schedules routes for a multi-depot delivery system with time windows and split deliveries.
    It returns a dictionary with a list of routes and the total cost.
    
    Parameters:
      depots: List of depots. Each depot is a dict with keys: 
              "id" (unique identifier), "location" (tuple of (x, y)),
              "num_vehicles" (available vehicles), "capacity" (vehicle capacity),
              "operating_hours" (tuple, e.g., (start, end)).
      customers: List of customers. Each customer is a dict with keys:
              "id" (unique identifier), "location" (tuple of (x, y)),
              "demand" (demand to be delivered),
              "time_window" (tuple representing (earliest, latest) delivery times),
              "service_time" (time required to serve the customer).
      cost_matrix: A 2D list representing travel times between locations.
                   It is assumed that the order of locations is:
                     first all depots (in the order given in depots list) 
                     then all customers (in the order given in customers list).
      vehicle_speed: A float representing the vehicle speed.
      penalty_late: Cost per unit time for late deliveries.
      penalty_vehicle: Fixed cost penalty for each vehicle used.
      
    Returns:
      A dictionary with two keys:
        "routes": A list of route dictionaries. Each route dictionary contains:
                   "depot": the depot id used,
                   "route": list of visited location ids (starts and ends with depot id, with a customer id in between),
                   "demand": total demand delivered on that route,
                   "travel_time": total travel time for the route,
                   "penalty": any late delivery penalty incurred.
        "total_cost": The total cost computed as the sum over all routes of (travel_time + penalty + penalty_vehicle).
    """
    routes = []
    total_cost = 0

    # Create a depot lookup: depot_id -> depot info and available vehicle count.
    depot_info = {}
    for i, depot in enumerate(depots):
        depot_info[depot["id"]] = {
            "index": i,  # corresponding index in cost_matrix (0 <= index < len(depots))
            "available": depot["num_vehicles"],
            "capacity": depot["capacity"],
            "start_time": depot["operating_hours"][0]
        }
    
    # For each customer, we will try to satisfy their demand. We assume the cost_matrix order:
    # Depot indices: 0 to len(depots)-1; Customer indices: len(depots) to len(depots)+len(customers)-1
    num_depots = len(depots)
    
    for cust_idx, customer in enumerate(customers):
        remaining_demand = customer["demand"]
        customer_matrix_idx = num_depots + cust_idx

        # Prepare a sorted list of depots by round-trip travel time for this customer.
        depot_sorted = []
        for depot in depots:
            depot_id = depot["id"]
            depot_mat_idx = depot_info[depot_id]["index"]
            travel_one_way = cost_matrix[depot_mat_idx][customer_matrix_idx] / vehicle_speed
            round_trip = 2 * travel_one_way
            depot_sorted.append((round_trip, depot_id, travel_one_way))
        depot_sorted.sort(key=lambda x: x[0])
        
        # Assign deliveries from available depots in order of increasing round-trip cost.
        for round_trip, depot_id, travel_one_way in depot_sorted:
            if remaining_demand <= 0:
                break 
            available = depot_info[depot_id]["available"]
            if available <= 0:
                continue
            # Use one vehicle from this depot.
            delivery_amount = min(depot_info[depot_id]["capacity"], remaining_demand)
            depot_start = depot_info[depot_id]["start_time"]
            
            # Calculate arrival time at customer.
            travel_time_to_customer = travel_one_way
            arrival_time = depot_start + travel_time_to_customer
            # Wait if arrived before the customer's time window.
            start_service = max(arrival_time, customer["time_window"][0])
            finish_service = start_service + customer["service_time"]
            
            # Compute penalty if service finishes after time window end.
            lateness = max(0, finish_service - customer["time_window"][1])
            penalty = lateness * penalty_late

            # Total travel_time is round trip.
            travel_time = 2 * travel_time_to_customer
            
            # Build the route. The route is represented as a list with the depot id, customer id, and depot id.
            route_plan = {
                "depot": depot_id,
                "route": [depot_id, customer["id"], depot_id],
                "demand": delivery_amount,
                "travel_time": travel_time,
                "penalty": penalty
            }
            routes.append(route_plan)
            total_cost += travel_time + penalty + penalty_vehicle
            
            # Mark the vehicle as used.
            depot_info[depot_id]["available"] -= 1
            remaining_demand -= delivery_amount

        # If after checking all depots the customer's demand isn't fully met, then we enforce split deliveries
        # from depots with remaining available vehicles (even if not optimal).
        if remaining_demand > 0:
            for round_trip, depot_id, travel_one_way in depot_sorted:
                if remaining_demand <= 0:
                    break
                # Even if the vehicle count is 0, we cannot use that depot further (per constraints)
                if depot_info[depot_id]["available"] <= 0:
                    continue
                delivery_amount = min(depot_info[depot_id]["capacity"], remaining_demand)
                depot_start = depot_info[depot_id]["start_time"]
                travel_time_to_customer = travel_one_way
                arrival_time = depot_start + travel_time_to_customer
                start_service = max(arrival_time, customer["time_window"][0])
                finish_service = start_service + customer["service_time"]
                lateness = max(0, finish_service - customer["time_window"][1])
                penalty = lateness * penalty_late
                travel_time = 2 * travel_time_to_customer

                route_plan = {
                    "depot": depot_id,
                    "route": [depot_id, customer["id"], depot_id],
                    "demand": delivery_amount,
                    "travel_time": travel_time,
                    "penalty": penalty
                }
                routes.append(route_plan)
                total_cost += travel_time + penalty + penalty_vehicle
                depot_info[depot_id]["available"] -= 1
                remaining_demand -= delivery_amount

        # If still not fully delivered, then allocation is infeasible.
        if remaining_demand > 0:
            raise Exception(f"Unable to satisfy customer {customer['id']}'s demand due to insufficient vehicle capacity.")

    return {"routes": routes, "total_cost": total_cost}