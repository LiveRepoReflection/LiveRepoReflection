def schedule_deliveries(city_graph, charging_stations, delivery_requests, drones, get_adjusted_flight_time, simulation_duration):
    # pending delivery requests: dictionary mapping id to request details
    pending = {req["id"]: req for req in delivery_requests}
    schedule = {}
    
    # Process each drone independently in a greedy fashion using shared pending requests.
    for drone in drones:
        drone_id = drone["id"]
        current_location = drone["current_location"]
        drone_time = 0
        battery = drone["max_flight_time"]
        schedule[drone_id] = []
        
        while drone_time < simulation_duration:
            candidate = None
            candidate_arrival_time = None
            candidate_t1 = None
            candidate_wait = None
            candidate_t2 = None

            # Search for a feasible pending delivery request
            for req in list(pending.values()):
                # Compute time to go from current_location to pickup (origin)
                t1 = get_adjusted_flight_time(current_location, req["origin"], drone_time)
                arrival_at_origin = drone_time + t1
                # Wait until the beginning of the time window if arrived early
                wait = 0
                if arrival_at_origin < req["time_window"][0]:
                    wait = req["time_window"][0] - arrival_at_origin
                # Compute flight time from origin (pickup) to destination (delivery)
                t2 = get_adjusted_flight_time(req["origin"], req["destination"], drone_time + t1 + wait)
                delivery_arrival = arrival_at_origin + wait + t2
                # Check if delivery arrival time fits within the time window and simulation duration
                if delivery_arrival > req["time_window"][1]:
                    continue
                if delivery_arrival > simulation_duration:
                    continue
                # Check if the drone has enough battery for the flight legs (pickup and delivery)
                if battery < (t1 + t2):
                    continue
                # Choose the candidate with the earliest delivery arrival time
                if candidate is None or delivery_arrival < candidate_arrival_time:
                    candidate = req
                    candidate_arrival_time = delivery_arrival
                    candidate_t1 = t1
                    candidate_wait = wait
                    candidate_t2 = t2

            if candidate is not None:
                # Schedule travel to pickup point (origin)
                pickup_arrival = drone_time + candidate_t1
                if pickup_arrival <= simulation_duration:
                    schedule[drone_id].append({
                        "location": candidate["origin"],
                        "arrival_time": pickup_arrival,
                        "deliveries": []
                    })
                # Update time to the pickup event; wait if necessary until the time window starts
                drone_time = pickup_arrival
                if drone_time < candidate["time_window"][0]:
                    drone_time = candidate["time_window"][0]
                # Schedule travel from pickup (origin) to destination
                delivery_arrival = drone_time + candidate_t2
                if delivery_arrival > simulation_duration:
                    break
                schedule[drone_id].append({
                    "location": candidate["destination"],
                    "arrival_time": delivery_arrival,
                    "deliveries": [candidate["id"]]
                })
                # Update drone state: consume battery and update location and time
                battery -= (candidate_t1 + candidate_t2)
                current_location = candidate["destination"]
                drone_time = delivery_arrival
                # Remove the delivered request from pending
                del pending[candidate["id"]]
            else:
                # No feasible delivery found.
                # If the drone is not at a charging station, try to go to the nearest charging station for recharge.
                if current_location not in charging_stations:
                    best_charger = None
                    best_time = None
                    for cs in charging_stations:
                        t_cs = get_adjusted_flight_time(current_location, cs, drone_time)
                        if best_time is None or t_cs < best_time:
                            best_time = t_cs
                            best_charger = cs
                    # If no charging station found (should not happen), break the loop.
                    if best_charger is None:
                        break
                    arrival_charger = drone_time + best_time
                    if arrival_charger > simulation_duration:
                        break
                    schedule[drone_id].append({
                        "location": best_charger,
                        "arrival_time": arrival_charger,
                        "deliveries": []
                    })
                    current_location = best_charger
                    drone_time = arrival_charger
                    # Recharge: battery is reset to maximum flight time.
                    battery = drone["max_flight_time"]
                else:
                    # If already at a charging station and no delivery is feasible, break out.
                    break
        # End while for this drone
    # End for each drone
    return schedule