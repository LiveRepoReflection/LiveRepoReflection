import heapq
import bisect

def convert_to_minutes(time_tuple):
    hour, minute = time_tuple
    return hour * 60 + minute

def convert_to_hour_minute(minutes):
    return (minutes // 60, minutes % 60)

def find_optimal_route(stops, routes, transfers, start_stop, end_stop, start_time, current_time, delay_updates, transfer_time):
    # Convert start_time and current_time to minutes
    start_time_m = convert_to_minutes(start_time)
    current_time_m = convert_to_minutes(current_time)
    initial_time = max(start_time_m, current_time_m)

    # If starting and ending stops are the same, return the starting time.
    if start_stop == end_stop:
        return convert_to_hour_minute(initial_time)

    # Preprocess delay updates into a dictionary for quick lookup.
    delay_dict = {}
    for route_id, stop_id, delay in delay_updates:
        delay_dict[(route_id, stop_id)] = delay

    # Preprocess each route:
    # For each route, compute:
    # - route_stops: list of stops
    # - sorted schedule in minutes (for departures from first stop)
    # - cumulative delays for each stop: cum[i] = total delay from index 1 to i.
    route_info = {}
    for route_id, route_data in routes.items():
        stops_list = route_data['stops']
        # Convert schedule to minutes and sort them
        scheduled = []
        for time_tuple in route_data['schedule']:
            time_m = convert_to_minutes(time_tuple)
            scheduled.append(time_m)
        scheduled.sort()
        # Compute cumulative delays. Index 0 has no travel time delay.
        cum_delays = [0] * len(stops_list)
        for i in range(1, len(stops_list)):
            delay_here = delay_dict.get((route_id, stops_list[i]), 0)
            cum_delays[i] = cum_delays[i-1] + delay_here
        route_info[route_id] = {
            'mode': route_data['mode'],
            'stops': stops_list,
            'schedule': scheduled,
            'cum_delays': cum_delays
        }

    # Build an index mapping stops to routes that pass through them.
    # stop_to_routes: key = stop id, value = list of tuples (route_id, index, schedule list, stops_list, cum_delays)
    stop_to_routes = {}
    for route_id, info in route_info.items():
        stops_list = info['stops']
        for index, stop in enumerate(stops_list):
            if stop not in stop_to_routes:
                stop_to_routes[stop] = []
            stop_to_routes[stop].append((route_id, index, info['schedule'], stops_list, info['cum_delays']))

    # Initialize best arrival times dictionary
    best_arrival = {stop: float('inf') for stop in stops}
    best_arrival[start_stop] = initial_time

    # Priority queue: (time, stop)
    heap = [(initial_time, start_stop)]
    while heap:
        current_time_state, current_stop = heapq.heappop(heap)
        if current_time_state > best_arrival[current_stop]:
            continue
        if current_stop == end_stop:
            return convert_to_hour_minute(current_time_state)
        # Option 1: Transfers - if available from current_stop, add neighbor stops with fixed transfer_time.
        if current_stop in transfers:
            for neighbor in transfers[current_stop]:
                new_time = current_time_state + transfer_time
                if new_time < best_arrival.get(neighbor, float('inf')):
                    best_arrival[neighbor] = new_time
                    heapq.heappush(heap, (new_time, neighbor))
        # Option 2: Transit routes from current_stop
        if current_stop in stop_to_routes:
            for route_entry in stop_to_routes[current_stop]:
                route_id, index, schedule_list, stops_list, cum_delays = route_entry
                # Calculate effective arrival time at this stop if boarding a vehicle that left at scheduled time S:
                # arrival_time = S + (5 * index) + cum_delays[index]
                # We need S such that S >= current_time_state - (5*index + cum_delays[index])
                boarding_offset = 5 * index + cum_delays[index]
                needed = current_time_state - boarding_offset
                pos = bisect.bisect_left(schedule_list, needed)
                if pos == len(schedule_list):
                    # No departure available today that meets the requirement.
                    continue
                # Use the earliest available departure time
                dep_time = schedule_list[pos]
                # For every subsequent stop along this route (only moving forward)
                for j in range(index + 1, len(stops_list)):
                    arrival_time = dep_time + 5 * j + cum_delays[j]
                    next_stop = stops_list[j]
                    if arrival_time < best_arrival.get(next_stop, float('inf')):
                        best_arrival[next_stop] = arrival_time
                        heapq.heappush(heap, (arrival_time, next_stop))
    return None