import math
import heapq

def schedule_trains(N, M, tracks, K, trains, a, d, C, maintenance_schedules, get_speed_limit):
    # Build graph: For each station, list of (neighbor, length, max_speed)
    graph = {i: [] for i in range(1, N+1)}
    for (u, v, length, max_speed) in tracks:
        graph[u].append((v, length, max_speed))
        graph[v].append((u, length, max_speed))
    
    # Pre-sort maintenance schedules by track for easier filtering later.
    # We will not pre-organize them; simulate_edge will filter the list.
    
    # Maintain station occupancy schedule: mapping station -> list of (arrival, departure)
    # We use a minimal dwell time of 0.1 minutes to simulate occupancy.
    station_schedule = {i: [] for i in range(1, N+1)}
    
    def adjust_for_capacity(station, arrival_time):
        # Check the occupancy at the station at time arrival_time.
        # If occupancy count is < C, then schedule occupancy and return the arrival_time.
        # Otherwise, wait until the earliest departure time among occupying intervals.
        dwell = 0.1
        current_time = arrival_time
        while True:
            count = 0
            earliest_release = None
            for (a_t, d_t) in station_schedule[station]:
                # if the occupancy interval covers current_time
                if a_t <= current_time < d_t:
                    count += 1
                    if earliest_release is None or d_t < earliest_release:
                        earliest_release = d_t
            if count < C:
                # Reserve a slot with dwell time
                station_schedule[station].append((current_time, current_time + dwell))
                return current_time
            else:
                # Wait until the earliest releasing time and recheck
                current_time = earliest_release

    def simulate_edge(departure_time, u, v, length, edge_max_speed):
        # Simulate edge traversal considering acceleration/deceleration physics,
        # dynamic speed limits and maintenance windows.
        current_time = departure_time
        while True:
            # Get the current speed limit for the edge at current_time
            dynamic_speed = get_speed_limit(u, v, current_time)
            applicable_speed = min(edge_max_speed, dynamic_speed)
            # Compute travel time using physics formulas:
            # Convert speeds: they are in km/h; time in minutes.
            # Distance required to accelerate to applicable_speed:
            d_acc = (applicable_speed ** 2) / (120 * a)
            d_dec = (applicable_speed ** 2) / (120 * d)
            if d_acc + d_dec >= length:
                # Train cannot reach the full applicable_speed
                # Solve for v_eff from: length = v_eff^2/(120)*(1/a + 1/d)
                denom = (1/a + 1/d)
                v_eff = math.sqrt(120 * length / denom)
                t_acc = v_eff / a
                t_dec = v_eff / d
                total_time = t_acc + t_dec
            else:
                cruise_distance = length - d_acc - d_dec
                t_acc = applicable_speed / a
                t_dec = applicable_speed / d
                # Cruise time: distance / (speed in km/min) = distance / (applicable_speed/60)
                t_cruise = (cruise_distance * 60) / applicable_speed
                total_time = t_acc + t_cruise + t_dec
            
            arrival_time = current_time + total_time
            
            # Check for maintenance conflicts on this edge.
            conflict = False
            new_time = current_time
            for (m_u, m_v, m_start, m_end) in maintenance_schedules:
                if (m_u == u and m_v == v) or (m_u == v and m_v == u):
                    # Check if travel interval [current_time, arrival_time] overlaps maintenance period
                    if current_time < m_end and arrival_time > m_start:
                        conflict = True
                        # Wait until maintenance window ends.
                        new_time = max(new_time, m_end)
            if conflict:
                current_time = new_time
                continue
            else:
                return arrival_time

    def dijkstra(source, dest):
        # Use Dijkstra's algorithm to find a path from source to dest.
        # For simplicity, we use track length as weight.
        dist = {i: float("inf") for i in range(1, N+1)}
        prev = {i: None for i in range(1, N+1)}
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            d_cur, u = heapq.heappop(heap)
            if d_cur > dist[u]:
                continue
            if u == dest:
                break
            for (v, length, max_speed) in graph[u]:
                alt = d_cur + length
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))
        # Reconstruct path
        if dist[dest] == float("inf"):
            return []
        path = []
        u = dest
        while u is not None:
            path.append(u)
            u = prev[u]
        path.reverse()
        return path

    # Process trains in order of departure time for simulation.
    # We also need to return results in order of input.
    train_results = [None] * K
    indexed_trains = list(enumerate(trains))
    indexed_trains.sort(key=lambda x: x[1][2])  # sort by departure time

    for idx, (start, end, departure_time, preferred_arrival) in indexed_trains:
        # Compute route using Dijkstra using track length as heuristic weight.
        route = dijkstra(start, end)
        if not route or len(route) == 0:
            # If no route found, mark arrival time as -1.
            train_results[idx] = -1
            continue
        
        # Start simulation from the starting station.
        current_time = departure_time
        current_station = start
        # For starting station, we assume no occupancy constraint.
        # Traverse through the route edges.
        for next_station in route[1:]:
            # Find the track information between current_station and next_station
            edge_found = False
            for (v, length, max_speed) in graph[current_station]:
                if v == next_station:
                    edge_found = True
                    # Simulate travel on this edge.
                    current_time = simulate_edge(current_time, current_station, next_station, length, max_speed)
                    break
            if not edge_found:
                # This should not happen if route is correct.
                current_time = -1
                break
            # At intermediate stations (not destination), adjust for station capacity.
            if next_station != end:
                current_time = adjust_for_capacity(next_station, current_time)
            current_station = next_station
        # Final arrival time is at destination without capacity adjustment.
        train_results[idx] = current_time

    return train_results

if __name__ == "__main__":
    # Sample simple test run
    def dummy_speed_limit(u, v, t):
        return 100

    # Simple network sample
    N = 2
    M = 1
    tracks = [(1, 2, 100, 100)]
    K = 1
    trains = [(1, 2, 0, 200)]
    a = 10
    d = 10
    C = 2
    maintenance_schedules = []
    
    result = schedule_trains(N, M, tracks, K, trains, a, d, C, maintenance_schedules, dummy_speed_limit)
    print(result)