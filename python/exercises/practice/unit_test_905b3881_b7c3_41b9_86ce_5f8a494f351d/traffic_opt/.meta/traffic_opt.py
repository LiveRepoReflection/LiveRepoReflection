def optimize_traffic(city, snapshots, cycle_length):
    """
    Optimize traffic light schedules for a given city graph and a series of snapshots.

    Parameters:
    - city: dict. Keys are intersection IDs (int) and values are lists of tuples (destination, capacity, free_flow_time)
    - snapshots: list of dicts. Each dictionary represents a snapshot with keys as (source, destination) tuples and values as number of cars.
    - cycle_length: int. The total cycle length (in seconds) for each intersection's lights.

    Returns:
    - A list of schedules with one schedule per snapshot. Each schedule is a dict where keys are intersection IDs,
      and values are dicts mapping destination intersection IDs (of outgoing roads) to green light durations.
    """
    schedules = []
    # Process each snapshot separately
    for snap in snapshots:
        schedule = {}
        # For each intersection in the city that has outgoing roads, compute schedule
        for src, roads in city.items():
            if not roads:
                continue  # Skip intersections with no outgoing roads
            # Calculate the traffic demand for each outgoing road from snapshot
            demand = {}
            total_demand = 0.0
            for (dest, capacity, free_flow_time) in roads:
                # Get traffic volume entering this road segment from snapshot; default to 0 if not present.
                vol = snap.get((src, dest), 0)
                demand[dest] = vol
                total_demand += vol

            # If there is traffic demand, allocate green light duration proportionally
            intersections_schedule = {}
            if total_demand > 0:
                for (dest, capacity, free_flow_time) in roads:
                    intersections_schedule[dest] = cycle_length * (demand[dest] / total_demand)
            else:
                # If no traffic, assign equal durations to all outgoing roads
                num_roads = len(roads)
                equal_duration = cycle_length / num_roads
                for (dest, capacity, free_flow_time) in roads:
                    intersections_schedule[dest] = equal_duration

            schedule[src] = intersections_schedule
        schedules.append(schedule)
    return schedules

if __name__ == '__main__':
    # Example usage
    city = {
        0: [(1, 100, 5), (2, 50, 10)],
        1: [(2, 75, 7)],
        2: []
    }
    snapshots = [
        {(0, 1): 50, (0, 2): 20, (1, 2): 30},
        {(0, 1): 70, (0, 2): 30, (1, 2): 40}
    ]
    cycle_length = 60
    result = optimize_traffic(city, snapshots, cycle_length)
    for idx, sched in enumerate(result):
        print("Snapshot", idx, "schedule:", sched)