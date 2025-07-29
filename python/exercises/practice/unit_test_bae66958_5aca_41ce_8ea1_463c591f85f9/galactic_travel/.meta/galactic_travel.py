import heapq

def find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network):
    earliest_departure, latest_departure = departure_time_window
    # Prepare a set of all planets that might appear (as keys or destinations)
    all_planets = set(wormhole_network.keys())
    for planet in wormhole_network:
        for neighbor in wormhole_network[planet]:
            all_planets.add(neighbor)
    
    # Initialize arrival times for all planets to infinity
    arrival_times = {planet: float('inf') for planet in all_planets}
    # Set starting planet's arrival time to the earliest_departure time.
    arrival_times[start_planet] = earliest_departure

    # Priority queue holds tuples of (current_time, planet, at_start)
    # at_start is True when the planet is the start_planet and departure window must be enforced.
    pq = []
    heapq.heappush(pq, (earliest_departure, start_planet, True))
    
    while pq:
        current_time, planet, at_start = heapq.heappop(pq)
        if current_time > arrival_times.get(planet, float('inf')):
            continue
        if planet == destination_planet:
            return current_time
        # If planet has no outgoing wormholes, skip.
        if planet not in wormhole_network:
            continue
        
        for neighbor, wormholes in wormhole_network[planet].items():
            for wormhole in wormholes:
                capacity = wormhole["capacity"]
                # Check capacity constraint: if number of travelers exceeds capacity then this wormhole cannot be used.
                if num_travelers > capacity:
                    continue
                for (sched_start, sched_end, travel_time) in wormhole["schedule"]:
                    if at_start:
                        # For the starting planet, departure time must be within both the wormhole schedule and the provided departure window.
                        candidate_departure = max(current_time, sched_start, earliest_departure)
                        effective_sched_end = min(sched_end, latest_departure)
                    else:
                        candidate_departure = max(current_time, sched_start)
                        effective_sched_end = sched_end
                    if candidate_departure > effective_sched_end:
                        continue
                    arrival = candidate_departure + travel_time
                    if arrival < arrival_times.get(neighbor, float('inf')):
                        arrival_times[neighbor] = arrival
                        # Once we depart from the start planet, we no longer enforce the departure window constraint.
                        heapq.heappush(pq, (arrival, neighbor, False))
                        
    return None