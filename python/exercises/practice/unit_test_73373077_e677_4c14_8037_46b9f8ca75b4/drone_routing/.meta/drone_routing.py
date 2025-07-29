import math
import heapq

def euclidean_distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def plan_routes(num_drones,
                depot_location,
                drone_battery_capacity,
                drone_package_capacity,
                battery_consumption_rate,
                delivery_requests,
                time_penalty_per_unit,
                missed_delivery_penalty,
                charging_time_per_unit,
                max_simulation_time):
    # Prepare delivery requests as dictionaries and sort them by start time.
    deliveries = []
    for req in delivery_requests:
        request_id, x, y, start_time, end_time, package_weight = req
        deliveries.append({
            'id': request_id,
            'location': (x, y),
            'start': start_time,
            'end': end_time,
            'weight': package_weight
        })
    deliveries.sort(key=lambda d: d['start'])
    
    # Initialize drone states.
    # Each state: (current_time, drone_id, location, battery, packages, route)
    drones = []
    drone_states = {}
    for i in range(num_drones):
        state = {
            'time': 0,
            'location': depot_location,
            'battery': drone_battery_capacity,
            'packages': 0,
            'route': [("depot", 0, 0)]
        }
        drone_states[i] = state
        heapq.heappush(drones, (state['time'], i))
    
    # Use a greedy simulation: while there are deliveries left and drones can operate.
    while deliveries and drones:
        current_time, drone_id = heapq.heappop(drones)
        state = drone_states[drone_id]
        # If drone's current time exceeds simulation time, skip further processing.
        if state['time'] > max_simulation_time:
            continue

        # Check if the drone must return to depot due to package capacity or insufficient battery to visit any delivery.
        # We'll check the next candidate delivery if any.
        candidate_found = None
        min_delivery_time = None
        candidate_index = None

        # If drone has reached package capacity, force return.
        if state['packages'] >= drone_package_capacity:
            candidate_found = None
        else:
            # Try to find a delivery that is feasible.
            for idx, delivery in enumerate(deliveries):
                # Compute travel time from current location to delivery.
                dist = euclidean_distance(state['location'], delivery['location'])
                travel_time = int(math.ceil(dist))
                battery_needed = travel_time * battery_consumption_rate
                # If battery not sufficient to reach delivery, then break this candidate.
                if state['battery'] < battery_needed:
                    continue

                arrival_time = state['time'] + travel_time
                # If arrival is earlier than start, drone can wait.
                deliver_time = arrival_time if arrival_time >= delivery['start'] else delivery['start']
                if deliver_time > delivery['end']:
                    continue  # Cannot serve this delivery.
                if deliver_time > max_simulation_time:
                    continue  # Exceeds simulation time.
                # Select candidate with earliest deliver_time.
                if candidate_found is None or deliver_time < min_delivery_time:
                    candidate_found = delivery
                    min_delivery_time = deliver_time
                    candidate_index = idx
        
        if candidate_found is not None:
            # Serve the delivery.
            delivery = candidate_found
            # Compute travel details.
            dist = euclidean_distance(state['location'], delivery['location'])
            travel_time = int(math.ceil(dist))
            battery_needed = travel_time * battery_consumption_rate
            arrival_time = state['time'] + travel_time
            deliver_time = arrival_time if arrival_time >= delivery['start'] else delivery['start']
            # Update drone state.
            state['time'] = deliver_time
            state['battery'] -= battery_needed
            state['packages'] += 1
            state['location'] = delivery['location']
            state['route'].append(("delivery", delivery['id'], deliver_time))
            # Remove delivery from list.
            del deliveries[candidate_index]
        else:
            # No feasible delivery found, force return to depot if not already there.
            if state['location'] != depot_location:
                dist_back = euclidean_distance(state['location'], depot_location)
                travel_time_back = int(math.ceil(dist_back))
                battery_needed_back = travel_time_back * battery_consumption_rate
                # If battery insufficient to return, then we assume drone can always perform depot-return because
                # the starting depot had full battery. In worst case, wait until simulation ends.
                if state['battery'] < battery_needed_back:
                    # If drone cannot return, then break out by setting time beyond simulation.
                    state['time'] = max_simulation_time + 1
                else:
                    state['time'] += travel_time_back
                    state['battery'] -= battery_needed_back
                    state['location'] = depot_location
                    state['route'].append(("depot", 0, state['time']))
                    # Recharge battery fully:
                    recharge_time = (drone_battery_capacity - state['battery']) * charging_time_per_unit
                    state['time'] += recharge_time
                    state['battery'] = drone_battery_capacity
                    # Reset package count.
                    state['packages'] = 0
            else:
                # At depot but no candidate delivery is feasible, then simply break out of loop for this drone.
                state['time'] = max_simulation_time + 1

        # Push the drone back into the heap if still within time.
        if state['time'] <= max_simulation_time:
            heapq.heappush(drones, (state['time'], drone_id))
    
    # For any drones still not at depot, return them to depot if possible.
    for drone_id, state in drone_states.items():
        if state['location'] != depot_location and state['time'] <= max_simulation_time:
            dist_back = euclidean_distance(state['location'], depot_location)
            travel_time_back = int(math.ceil(dist_back))
            battery_needed_back = travel_time_back * battery_consumption_rate
            if state['battery'] >= battery_needed_back:
                state['time'] += travel_time_back
                state['battery'] -= battery_needed_back
                state['location'] = depot_location
                state['route'].append(("depot", 0, state['time']))
            else:
                # If battery is insufficient, assume drone waits until it can return (simulate recharge at current location by waiting additional time at depot)
                # For simplicity, force the route to end at depot by adding a depot step with max_simulation_time.
                state['time'] = max_simulation_time
                state['location'] = depot_location
                state['route'].append(("depot", 0, state['time']))
    # Return routes in order of drone id.
    routes = []
    for i in range(num_drones):
        routes.append(drone_states[i]['route'])
    return routes