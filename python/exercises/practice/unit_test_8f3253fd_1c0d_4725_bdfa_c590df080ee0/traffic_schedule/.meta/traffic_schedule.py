def optimize_traffic_lights(network, traffic_flow, min_green_time, max_green_time, yellow_time, total_simulation_time):
    # For each intersection, decide the green light duration for each incoming road.
    # We use a simple proportional allocation based on the flow from the source intersection
    # to the current intersection. If both flows are zero, assign minimum green time to both.
    schedule = {}
    for intersection_id, data in network.items():
        incoming = data.get('incoming', [])
        # Since each intersection is guaranteed to have 2 incoming roads, we process both.
        if len(incoming) < 2:
            # In case there is less than 2 incoming roads, assign min_green_time to each available road.
            durations = []
            for road in incoming:
                durations.append(min_green_time)
            schedule[intersection_id] = [(i, durations[i]) for i in range(len(durations))]
            continue

        flows = []
        for road in incoming:
            src = road[0]
            # The traffic flow from src to current intersection.
            flow = traffic_flow.get((src, intersection_id), 0)
            flows.append(flow)

        if flows[0] == 0 and flows[1] == 0:
            d0 = min_green_time
            d1 = min_green_time
        else:
            total_flow = flows[0] + flows[1]
            available_range = max_green_time - min_green_time
            # Calculate duration proportionately
            d0 = min_green_time + int(round((flows[0] / total_flow) * available_range))
            d1 = min_green_time + int(round((flows[1] / total_flow) * available_range))
            d0 = max(min_green_time, min(d0, max_green_time))
            d1 = max(min_green_time, min(d1, max_green_time))

        # The schedule for the intersection is a list of phases.
        # Each phase is represented as (incoming_road_index, duration)
        schedule[intersection_id] = [(0, d0), (1, d1)]
    return schedule

if __name__ == "__main__":
    # Example usage:
    network = {
        1: {'incoming': [(2, 500, 50), (3, 600, 40)], 'outgoing': [(4, 700, 60), (5, 800, 50)]},
        2: {'incoming': [(1, 500, 50), (6, 400, 30)], 'outgoing': [(7, 900, 40), (8, 300, 20)]},
        3: {'incoming': [(1, 600, 40), (9, 700, 50)], 'outgoing': [(10, 500, 30), (11, 600, 40)]}
    }

    traffic_flow = {
        (2, 1): 100,
        (3, 1): 80,
        (1, 2): 120,
        (6, 2): 90,
        (1, 3): 70,
        (9, 3): 110
    }

    min_green_time = 15
    max_green_time = 60
    yellow_time = 5
    total_simulation_time = 3600  # 1 hour

    schedule = optimize_traffic_lights(network, traffic_flow, min_green_time, max_green_time, yellow_time, total_simulation_time)
    print(schedule)