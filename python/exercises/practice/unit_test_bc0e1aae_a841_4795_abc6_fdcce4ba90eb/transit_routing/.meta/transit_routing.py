import heapq
import bisect

def find_fastest_arrival(stations, routes, timetables, start_station, destination_station, departure_time, disruptions):
    # Build graph: station -> list of (end_station, route_id, travel_time)
    graph = {station: [] for station in stations}
    for start, end, route_id, travel_time in routes:
        graph[start].append((end, route_id, travel_time))
    
    # Preprocess disruptions into a dict: route_id -> list of (start, end) intervals, sorted by start
    disruption_dict = {}
    for route_id, d_start, duration in disruptions:
        interval = (d_start, d_start + duration)
        if route_id in disruption_dict:
            disruption_dict[route_id].append(interval)
        else:
            disruption_dict[route_id] = [interval]
    for route_id in disruption_dict:
        disruption_dict[route_id].sort(key=lambda x: x[0])
    
    # Helper function: Given current time, timetable (list of departure times in minutes, sorted)
    # and disruption intervals (list of (start, end)), return the next available departure time.
    # Timetable times repeat daily (period = 1440 minutes).
    def get_next_departure(current_time, timetable, disruptions_intervals):
        PERIOD = 1440
        while True:
            # Compute candidate departure from timetable based on current_time.
            mod_time = current_time % PERIOD
            day_offset = current_time - mod_time
            idx = bisect.bisect_left(timetable, mod_time)
            if idx < len(timetable):
                candidate = day_offset + timetable[idx]
            else:
                candidate = day_offset + PERIOD + timetable[0]
            
            # Check if candidate falls into any disruption interval.
            conflict = False
            if disruptions_intervals:
                for d_start, d_end in disruptions_intervals:
                    if candidate >= d_start and candidate < d_end:
                        # Candidate is within a disruption
                        current_time = d_end  # Wait until disruption ends and recompute schedule
                        conflict = True
                        break
            if not conflict:
                return candidate

    # Dijkstra algorithm: distances dictionary: station -> best arrival time so far.
    import math
    best = {station: math.inf for station in stations}
    best[start_station] = departure_time
    # Use priority queue as a min-heap: (arrival_time, station)
    heap = [(departure_time, start_station)]
    
    while heap:
        current_time, station = heapq.heappop(heap)
        if current_time > best[station]:
            continue
        if station == destination_station:
            return current_time
        for neighbor, route_id, travel_time in graph.get(station, []):
            # For each route, determine next available departure time taking into account the timetable and disruptions.
            timetable = timetables.get(route_id, [])
            if not timetable:
                continue
            disruptions_intervals = disruption_dict.get(route_id, [])
            next_departure = get_next_departure(current_time, timetable, disruptions_intervals)
            arrival_time = next_departure + travel_time
            if arrival_time < best.get(neighbor, math.inf):
                best[neighbor] = arrival_time
                heapq.heappush(heap, (arrival_time, neighbor))
    
    return -1