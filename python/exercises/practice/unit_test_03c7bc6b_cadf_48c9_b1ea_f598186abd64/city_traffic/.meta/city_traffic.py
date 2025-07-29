from collections import defaultdict, deque

def simulate_traffic(num_intersections, roads, demands, simulation_steps):
    """
    Simulates traffic flow in a city for a given number of time steps.
    
    Args:
        num_intersections: Number of intersections in the city.
        roads: List of tuples (u, v, capacity, travel_time) representing roads.
        demands: List of integers representing demand at each intersection.
        simulation_steps: Number of time steps to simulate.
        
    Returns:
        List of integers representing the number of cars at each intersection
        at the end of the simulation.
    """
    # Initialize data structures
    # Cars at each intersection
    intersection_cars = [0] * num_intersections
    
    # Queue of cars waiting to leave each intersection
    queued_cars = [0] * num_intersections
    
    # Outgoing roads from each intersection
    outgoing_roads = [[] for _ in range(num_intersections)]
    for u, v, capacity, travel_time in roads:
        outgoing_roads[u].append((v, capacity, travel_time))
    
    # Cars currently in transit on each road
    # Maps (u, v) to a queue of (cars, arrival_time) tuples
    in_transit = {}
    for u, v, capacity, travel_time in roads:
        in_transit[(u, v)] = deque()
    
    # Simulate traffic for the specified number of steps
    for step in range(1, simulation_steps + 1):
        # Step 1: Car Arrival - Process cars arriving at their destinations
        for (u, v), transit_queue in in_transit.items():
            # Check if any cars are arriving at this time step
            while transit_queue and transit_queue[0][1] == step:
                arriving_cars, _ = transit_queue.popleft()
                intersection_cars[v] += arriving_cars
        
        # Step 2: Demand Fulfillment
        for i in range(num_intersections):
            # Process negative demand (cars leaving the city)
            if demands[i] < 0:
                cars_to_remove = min(intersection_cars[i], abs(demands[i]))
                intersection_cars[i] -= cars_to_remove
            
            # Process positive demand (cars entering the city)
            if demands[i] > 0:
                intersection_cars[i] += demands[i]
        
        # Step 3: Road Usage
        # First, calculate the total cars at each intersection after demand fulfillment
        total_cars_at_intersection = intersection_cars.copy()
        
        # Add queued cars from previous step
        for i in range(num_intersections):
            total_cars_at_intersection[i] += queued_cars[i]
            queued_cars[i] = 0  # Reset queue for this step
        
        # Process each intersection
        for u in range(num_intersections):
            if total_cars_at_intersection[u] == 0:
                continue  # No cars to distribute
            
            if not outgoing_roads[u]:
                continue  # No outgoing roads
            
            # Calculate road usage based on equal distribution to all outgoing roads
            cars_to_distribute = total_cars_at_intersection[u]
            num_outgoing = len(outgoing_roads[u])
            
            # If there are cars and outgoing roads, distribute the cars
            if cars_to_distribute > 0 and num_outgoing > 0:
                # Distribute cars equally among all outgoing roads
                cars_per_road = cars_to_distribute // num_outgoing
                remainder = cars_to_distribute % num_outgoing
                
                cars_left = cars_to_distribute
                
                # Distribute cars to each outgoing road
                for idx, (v, capacity, travel_time) in enumerate(outgoing_roads[u]):
                    # Calculate cars for this road (with remainder distribution)
                    cars_for_this_road = cars_per_road + (1 if idx < remainder else 0)
                    
                    # Limit to capacity
                    cars_actually_sent = min(cars_for_this_road, capacity)
                    cars_left -= cars_actually_sent
                    
                    # Add cars to transit
                    if cars_actually_sent > 0:
                        arrival_time = step + travel_time
                        in_transit[(u, v)].append((cars_actually_sent, arrival_time))
                
                # Any remaining cars stay queued at the intersection
                queued_cars[u] = cars_left
                # Reset cars at intersection since they're now either in transit or queued
                intersection_cars[u] = 0
            
    # Final step: Count cars at each intersection after all simulation steps
    # Include cars that are queued but haven't moved yet
    final_count = [intersection_cars[i] + queued_cars[i] for i in range(num_intersections)]
    
    return final_count