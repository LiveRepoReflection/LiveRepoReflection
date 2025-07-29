from typing import List, Tuple, Optional
import heapq
from collections import defaultdict

def optimize_traffic_lights(
    n: int,
    roads: List[Tuple[int, int, int, float]],
    target_intersection: int,
    time_horizon: int,
    min_green_time: int,
    max_green_time: int,
    amber_time: int
) -> Optional[List[int]]:
    """
    Optimizes traffic light schedules to minimize total waiting time.
    
    Args:
        n: Number of intersections in the city.
        roads: List of tuples (u, v, length, density) representing roads.
        target_intersection: The intersection for which to optimize traffic lights.
        time_horizon: Time horizon for optimization in seconds.
        min_green_time: Minimum allowed green time per road in seconds.
        max_green_time: Maximum allowed green time per road in seconds.
        amber_time: Fixed amber time in seconds.
        
    Returns:
        A list of optimal green times for each incoming road, or None if no valid solution exists.
    """
    # Find all incoming roads to the target intersection
    incoming_roads = []
    for i, (u, v, length, density) in enumerate(roads):
        if v == target_intersection:
            # Calculate expected vehicle count based on density
            # Assuming vehicles travel at 10 m/s, and arrive at rate proportional to density
            travel_time = length / 10.0  # seconds to reach the intersection
            vehicles_per_second = density * 10  # vehicles per second based on density
            
            # Expected number of vehicles arriving within time_horizon
            # We only count vehicles that will reach the intersection within the time horizon
            if travel_time < time_horizon:
                effective_time = time_horizon - travel_time
                expected_vehicles = vehicles_per_second * effective_time
                incoming_roads.append((i, expected_vehicles, u, v))
    
    # If no incoming roads, return an empty list
    if not incoming_roads:
        return []
    
    # Check if it's possible to give at least min_green_time to all roads
    total_min_time_needed = len(incoming_roads) * min_green_time + (len(incoming_roads) * amber_time)
    if total_min_time_needed > time_horizon:
        return None
    
    # Sort roads by expected vehicle count (descending)
    incoming_roads.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate remaining time after allocating minimum green time to each road
    remaining_time = time_horizon - total_min_time_needed
    
    # Initial allocation: minimum green time for all roads
    allocation = [min_green_time] * len(incoming_roads)
    
    # Calculate total expected vehicles
    total_vehicles = sum(road[1] for road in incoming_roads)
    
    # If no vehicles expected, return the minimum allocation
    if total_vehicles == 0:
        # If min equals max, return that value for all roads
        if min_green_time == max_green_time:
            return allocation
        
        # Distribute time evenly if no traffic data
        equal_share = min(max_green_time, 
                          min_green_time + remaining_time // len(incoming_roads))
        return [equal_share] * len(incoming_roads)
    
    # Distribute remaining time using a priority queue based approach
    # Each road gets additional time proportional to its vehicle density
    priority_queue = []
    for i, (road_idx, expected_vehicles, _, _) in enumerate(incoming_roads):
        # Calculate wait reduction per second of green time
        # Higher value means more benefit from additional green time
        if expected_vehicles > 0:
            benefit = expected_vehicles / min_green_time
            heapq.heappush(priority_queue, (-benefit, i))  # Negative for max-heap
    
    # Distribute remaining time to roads with highest benefit
    while remaining_time > 0 and priority_queue:
        benefit, road_idx = heapq.heappop(priority_queue)
        benefit = -benefit  # Convert back to positive
        
        if allocation[road_idx] < max_green_time:
            # Add one second of green time
            allocation[road_idx] += 1
            remaining_time -= 1
            
            # Recalculate benefit and push back to queue if still below max
            if allocation[road_idx] < max_green_time:
                new_benefit = incoming_roads[road_idx][1] / allocation[road_idx]
                heapq.heappush(priority_queue, (-new_benefit, road_idx))
    
    # Reorder allocation to match the original order of roads in the input
    # Create a mapping from original road index to allocation value
    road_to_allocation = {}
    for i, (road_idx, _, _, _) in enumerate(incoming_roads):
        road_to_allocation[road_idx] = allocation[i]
    
    # Create final result in original order
    result = []
    for i, (u, v, _, _) in enumerate(roads):
        if v == target_intersection:
            result.append(road_to_allocation[i])
    
    return result


def simulate_traffic(
    roads: List[Tuple[int, int, int, float]],
    target_intersection: int,
    green_times: List[int],
    amber_time: int,
    time_horizon: int
) -> float:
    """
    Helper function to simulate traffic and calculate total waiting time.
    
    Args:
        roads: List of road tuples.
        target_intersection: Target intersection ID.
        green_times: List of green times for each incoming road.
        amber_time: Amber time in seconds.
        time_horizon: Time horizon in seconds.
        
    Returns:
        Total waiting time for all vehicles.
    """
    # Find incoming roads to target intersection
    incoming_roads = []
    for i, (u, v, length, density) in enumerate(roads):
        if v == target_intersection:
            travel_time = length / 10.0  # Time to reach intersection
            vehicles_per_second = density * 10  # Arrival rate
            
            if travel_time < time_horizon:
                effective_time = time_horizon - travel_time
                incoming_roads.append((i, u, v, travel_time, vehicles_per_second))
    
    if not incoming_roads:
        return 0
    
    # Create arrival schedule for each road
    arrival_schedules = []
    for i, (road_idx, _, _, travel_time, rate) in enumerate(incoming_roads):
        schedule = []
        t = travel_time
        while t <= time_horizon:
            num_vehicles = rate  # Vehicles per second
            for _ in range(int(num_vehicles)):
                schedule.append(t)
            t += 1
            
        arrival_schedules.append((road_idx, schedule))
    
    # Simulate traffic light cycle
    cycle_time = sum(green_times) + len(green_times) * amber_time
    cycles = (time_horizon + cycle_time - 1) // cycle_time  # Ceiling division
    
    # Create traffic light schedule
    light_schedule = {}
    time = 0
    for cycle in range(cycles):
        for i, green_time in enumerate(green_times):
            road_idx = incoming_roads[i][0]
            # Road has green light during this period
            for t in range(time, time + green_time):
                light_schedule[(road_idx, t)] = "green"
            time += green_time
            
            # Amber period
            for t in range(time, time + amber_time):
                light_schedule[(road_idx, t)] = "amber"
            time += amber_time
    
    # Calculate waiting time for each vehicle
    total_waiting_time = 0
    for road_idx, schedule in arrival_schedules:
        for arrival_time in schedule:
            t = arrival_time
            while t < time_horizon:
                if (road_idx, t) in light_schedule and light_schedule[(road_idx, t)] == "green":
                    # Vehicle can pass
                    total_waiting_time += (t - arrival_time)
                    break
                t += 1
            
            # If vehicle couldn't pass by end of time horizon
            if t >= time_horizon:
                total_waiting_time += (time_horizon - arrival_time)
    
    return total_waiting_time