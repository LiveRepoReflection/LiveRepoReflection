import time

# Mapping package sizes to numeric values for comparison.
SIZE_MAP = {
    "small": 1,
    "medium": 2,
    "large": 3
}

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def path_congestion(p1, p2, city_map):
    """
    Compute the sum of congestion levels along a Manhattan path from p1 to p2.
    We construct the path by moving horizontally first then vertically.
    We do not include the starting cell congestion.
    """
    congestion_sum = 0
    x1, y1 = p1
    x2, y2 = p2

    # Horizontal move
    x_step = 1 if x2 > x1 else -1
    for x in range(x1 + x_step, x2 + x_step, x_step):
        # Keep y constant
        # Assume valid indices
        congestion_sum += city_map[y1][x]

    # Vertical move
    y_step = 1 if y2 > y1 else -1
    for y in range(y1 + y_step, y2 + y_step, y_step):
        # after horizontal move, x is now x2
        congestion_sum += city_map[y][x2]

    return congestion_sum

def compute_leg_cost(p1, p2, city_map, risk_factor):
    """
    Compute effective cost from point p1 to p2.
    Effective cost = Manhattan distance + risk penalty.
    Risk penalty = risk_factor * (sum of congestion along the path).
    """
    distance = manhattan_distance(p1, p2)
    if distance == 0:
        # if no movement, no congestion cost.
        return 0
    congestion_sum = path_congestion(p1, p2, city_map)
    risk_penalty = risk_factor * congestion_sum
    return distance + risk_penalty

def assign_deliveries(requests, city_map, drones, depot, risk_factor):
    """
    Assign delivery requests to available drones.
    
    Each request is a tuple:
       (request_id, pickup_location, delivery_location, package_size, priority, deadline)
    Each drone is a tuple:
       (drone_id, current_location, max_payload, speed)
    
    The returned dictionary maps drone_id to a list of assigned request_ids in order.
    """
    # Get the current time as the starting timestamp.
    current_time = time.time()
    
    # Initialize assignment dictionary: drone_id -> list of request_ids
    assignments = { drone[0]: [] for drone in drones }
    
    # Maintain drone state: dictionary mapping drone_id to [availability_time, current_location, drone_speed, max_payload]
    drone_state = {}
    for drone in drones:
        drone_id, location, max_payload, speed = drone
        # Drone is available immediately. Its initial position is provided.
        drone_state[drone_id] = [current_time, location, speed, SIZE_MAP[max_payload]]
    
    # Sort requests by priority (descending) and deadline (ascending)
    # Higher priority requests are to be handled first. If same priority, earlier deadline is prioritized.
    sorted_requests = sorted(requests, key=lambda r: (-r[4], r[5]))
    
    for req in sorted_requests:
        req_id, pickup, delivery, package_size, priority, deadline = req
        req_size_value = SIZE_MAP[package_size]

        best_drone = None
        best_finish_time = None
        
        # Try to assign this delivery to an available drone.
        for drone in drones:
            drone_id = drone[0]
            avail_time, current_loc, speed, drone_payload_value = drone_state[drone_id]
            # Check payload compatibility: drone's max capability must be >= request's requirement.
            if drone_payload_value < req_size_value:
                continue
            
            # Compute flight segments:
            # Leg 1: from drone's current location to pickup location.
            leg1 = compute_leg_cost(current_loc, pickup, city_map, risk_factor)
            # Leg 2: from pickup location to delivery location.
            leg2 = compute_leg_cost(pickup, delivery, city_map, risk_factor)
            # Leg 3: from delivery location to depot.
            leg3 = compute_leg_cost(delivery, depot, city_map, risk_factor)
            
            total_distance_cost = leg1 + leg2 + leg3
            # Flight time is effective cost divided by speed.
            flight_time = total_distance_cost / speed
            
            finish_time = avail_time + flight_time
            
            # Check deadline constraint: finish time must be before the deadline.
            if finish_time > deadline:
                continue
            
            # Choose the drone with the minimal finish time among feasible candidates.
            if best_finish_time is None or finish_time < best_finish_time:
                best_finish_time = finish_time
                best_drone = drone_id
        
        if best_drone is not None:
            # Assign the request to best_drone.
            assignments[best_drone].append(req_id)
            # Update the drone state.
            # After delivery, drone returns to depot.
            drone_state[best_drone][0] = best_finish_time  # new available time
            drone_state[best_drone][1] = depot  # reset location to depot
    
    return assignments