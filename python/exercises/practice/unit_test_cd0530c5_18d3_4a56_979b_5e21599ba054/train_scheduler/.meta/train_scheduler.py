def schedule_trains(n, tracks, trains):
    # Build a mapping for available tracks for each directed edge.
    # For parallel edges, we maintain a list of dictionaries containing track info and occupancy.
    # Each track info is a dictionary with keys: capacity, length, speed, occupancy.
    tracks_by_edge = {}
    for track in tracks:
        start, end, capacity, length, speed = track
        key = (start, end)
        track_entry = {
            'capacity': capacity,
            'length': length,
            'speed': speed,
            'occupancy': []  # List of tuples: (departure_time, arrival_time)
        }
        if key in tracks_by_edge:
            tracks_by_edge[key].append(track_entry)
        else:
            tracks_by_edge[key] = [track_entry]

    # Helper: Given a track (with its occupancy), a minimum start time (t0),
    # travel_time (length/speed), and capacity limit, find the earliest feasible departure time
    # for the new interval that satisfies non-overtaking and capacity constraints.
    def find_feasible_time(occupancy, t0, travel_time, capacity):
        candidate = t0
        while True:
            candidate_finish = candidate + travel_time
            # Non-overtaking: For any scheduled interval that started before candidate,
            # its finish time must be less than or equal candidate_finish.
            violation_nt = False
            next_candidate_nt = candidate
            for (s, e) in occupancy:
                if s < candidate and candidate_finish < e:
                    violation_nt = True
                    # To fix violation, wait until the conflicting train finishes.
                    if e > next_candidate_nt:
                        next_candidate_nt = e
            if violation_nt:
                candidate = next_candidate_nt
                continue

            # Capacity constraint: Use a sweep-line over the candidate interval with the occupancy intervals.
            events = []
            # Add events for the candidate interval
            events.append((candidate, 1))
            events.append((candidate_finish, -1))
            # Add events for all occupancy intervals that overlap with candidate interval.
            for (s, e) in occupancy:
                # if the occupancy interval overlaps with candidate interval:
                if not (e <= candidate or s >= candidate_finish):
                    # Overlap interval is [max(s, candidate), min(e, candidate_finish)]
                    overlap_start = max(s, candidate)
                    overlap_end = min(e, candidate_finish)
                    events.append((overlap_start, 1))
                    events.append((overlap_end, -1))
            # Sort events. When times equal, process end (-1) before start (+1)
            events.sort(key=lambda x: (x[0], x[1]))
            current = 0
            feasible = True
            for time, delta in events:
                current += delta
                if current > capacity:
                    feasible = False
                    break
            if not feasible:
                # Find the next candidate time: increase candidate to the earliest finishing time
                # among intervals that overlap with [candidate, candidate_finish]
                next_candidate_cap = candidate
                for (s, e) in occupancy:
                    if not (e <= candidate or s >= candidate_finish):
                        if e > next_candidate_cap:
                            next_candidate_cap = e
                # To avoid infinite loop if candidate doesn't advance, add a small epsilon.
                candidate = next_candidate_cap + 1e-6
                continue

            # Both constraints satisfied.
            return candidate

    # Result schedule: dictionary mapping train index to list of departure times
    schedule = {}

    # We process trains in the order of their given order.
    # A more sophisticated approach could reorder trains by earliest departure time or priority,
    # but here we follow the input order.
    for idx, train in enumerate(trains):
        dep_station, dest_station, earliest_departure, priority, route = train
        # Check that the route is valid: For each consecutive pair, there must be at least one track.
        valid = True
        for i in range(len(route) - 1):
            key = (route[i], route[i+1])
            if key not in tracks_by_edge:
                return None  # Invalid route: missing track.
        # Initialize list of times for this train.
        times = []
        # At origin, departure time is at least the earliest departure time.
        current_time = max(earliest_departure, 0.0)
        times.append(current_time)
        # For each segment in the route, choose a track (among available parallel tracks) that provides the earliest arrival.
        for i in range(len(route)-1):
            key = (route[i], route[i+1])
            available_tracks = tracks_by_edge[key]
            best_start = None
            best_finish = None
            best_track = None
            # For each track option, find the earliest feasible start time.
            for track in available_tracks:
                travel_time = track['length'] / track['speed']
                candidate_start = find_feasible_time(track['occupancy'], current_time, travel_time, track['capacity'])
                candidate_finish = candidate_start + travel_time
                if best_finish is None or candidate_finish < best_finish:
                    best_finish = candidate_finish
                    best_start = candidate_start
                    best_track = track
            # If no track was found, scheduling fails.
            if best_track is None:
                return None
            # Update the chosen track occupancy with the scheduled interval.
            best_track['occupancy'].append((best_start, best_finish))
            # Append the departure time from the current station (which is the candidate start time)
            # For the first station, times[0] is departure time. For intermediate station i+1, the departure time
            # is the arrival time from the previous segment.
            times.append(best_finish)
            current_time = best_finish
        schedule[idx] = times
    return schedule

if __name__ == '__main__':
    # Example execution for manual testing.
    # This code block will run only when the module is executed directly.
    n = 3
    tracks = [
        (0, 1, 2, 60, 60),
        (1, 2, 2, 60, 60)
    ]
    trains = [
        (0, 2, 0.0, 10, [0, 1, 2]),
        (0, 2, 5.0, 5, [0, 1, 2])
    ]
    result = schedule_trains(n, tracks, trains)
    print(result)