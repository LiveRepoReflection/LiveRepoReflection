import heapq
from collections import defaultdict

def optimize_traffic_lights(num_intersections, road_segments, traffic_lights, vehicle_arrival_rates, time_horizon, switch_time):
    # Build graph representation
    graph = defaultdict(list)
    capacities = {}
    for u, v, capacity in road_segments:
        graph[u].append(v)
        capacities[(u, v)] = capacity

    # Initialize traffic light schedule
    schedule = {i: [] for i in range(num_intersections)}
    
    # Initialize queues for each road segment
    queues = defaultdict(list)
    for (u, v), rate in vehicle_arrival_rates.items():
        for t in range(time_horizon):
            if (t % int(1/rate)) == 0 if rate > 0 else False:
                queues[(u, v)].append(t)

    # Priority queue for traffic light switching events
    events = []
    for intersection in range(num_intersections):
        if intersection in traffic_lights and traffic_lights[intersection]:
            initial_light = 0
            schedule[intersection].append(initial_light)
            heapq.heappush(events, (switch_time, intersection, initial_light))

    # Process events
    while events and events[0][0] < time_horizon:
        time, intersection, current_light = heapq.heappop(events)
        
        # Choose next light (simple round-robin)
        next_light = (current_light + 1) % len(traffic_lights[intersection])
        schedule[intersection].append(next_light)
        
        # Schedule next switch
        heapq.heappush(events, (time + switch_time, intersection, next_light))

    # Balance the schedule for intersections with no events
    for intersection in range(num_intersections):
        if not schedule[intersection]:
            if intersection in traffic_lights and traffic_lights[intersection]:
                schedule[intersection] = [0] * (time_horizon // switch_time)
            else:
                schedule[intersection] = []

    return schedule