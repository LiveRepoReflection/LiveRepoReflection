from collections import defaultdict, deque
from heapq import heappush, heappop

def simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path):
    """
    Simulates traffic flow in a city and calculates average travel time.
    
    Args:
        city_graph: Dictionary representing the city's road network
        vehicles: List of dictionaries representing vehicles
        simulation_time: Integer representing total time steps to simulate
        find_shortest_path: Function to find shortest path between two intersections
        
    Returns:
        Average travel time as a float, or -1 if no vehicles reach their destination
    """
    # Map vehicle type to size
    vehicle_sizes = {"car": 1, "truck": 2, "bus": 3}
    
    # Sort vehicles by departure time to process them in chronological order
    vehicles = sorted(vehicles, key=lambda v: v["departure_time"])
    
    # Track vehicles currently in the simulation
    active_vehicles = {}  # vehicle_id -> vehicle_state
    
    # Track completed vehicles and their travel times
    completed_vehicles = {}  # vehicle_id -> travel_time
    
    # Initialize street occupancy (for capacity tracking)
    street_occupancy = defaultdict(int)  # (from_intersection, to_intersection) -> current_occupancy
    
    # Queue of events (time, vehicle_id, event_type)
    event_queue = []
    
    # Initialize events for vehicle departures
    for vehicle in vehicles:
        vehicle_id = vehicle["vehicle_id"]
        departure_time = vehicle["departure_time"]
        # Ensure departure time is within simulation time
        if departure_time <= simulation_time:
            heappush(event_queue, (departure_time, vehicle_id, "departure"))
    
    # Main simulation loop
    current_time = 0
    while event_queue and current_time <= simulation_time:
        time, vehicle_id, event_type = heappop(event_queue)
        current_time = time
        
        if current_time > simulation_time:
            break
        
        if event_type == "departure":
            # Handle vehicle departure
            vehicle = next(v for v in vehicles if v["vehicle_id"] == vehicle_id)
            start = vehicle["start_intersection"]
            destination = vehicle["destination_intersection"]
            vehicle_type = vehicle["type"]
            vehicle_size = vehicle_sizes[vehicle_type]
            
            # Find route for vehicle
            route = find_shortest_path(city_graph, start, destination)
            
            if route is None or len(route) < 2:
                # No valid route to destination
                continue
            
            # Initialize vehicle state
            active_vehicles[vehicle_id] = {
                "route": route,
                "current_position": 0,  # Index in route
                "departure_time": time,
                "size": vehicle_size,
                "type": vehicle_type
            }
            
            # Try to move to the first street
            try_move_vehicle(vehicle_id, active_vehicles, city_graph, street_occupancy, event_queue, current_time)
            
        elif event_type == "arrival_at_intersection":
            # Handle vehicle arriving at an intersection
            if vehicle_id not in active_vehicles:
                continue  # Vehicle might have been removed
                
            vehicle_state = active_vehicles[vehicle_id]
            route = vehicle_state["route"]
            current_pos = vehicle_state["current_position"]
            
            # Check if vehicle has reached its destination
            if current_pos == len(route) - 1:
                # Vehicle has reached destination
                travel_time = current_time - vehicle_state["departure_time"]
                completed_vehicles[vehicle_id] = travel_time
                # Remove vehicle from simulation
                del active_vehicles[vehicle_id]
            else:
                # Try to move to the next street
                try_move_vehicle(vehicle_id, active_vehicles, city_graph, street_occupancy, event_queue, current_time)
    
    # Calculate average travel time
    if completed_vehicles:
        return sum(completed_vehicles.values()) / len(completed_vehicles)
    else:
        return -1

def try_move_vehicle(vehicle_id, active_vehicles, city_graph, street_occupancy, event_queue, current_time):
    """
    Attempts to move a vehicle to the next street on its route.
    
    Args:
        vehicle_id: ID of the vehicle to move
        active_vehicles: Dictionary of active vehicles
        city_graph: Dictionary representing the city's road network
        street_occupancy: Dictionary tracking street occupancy
        event_queue: Priority queue for events
        current_time: Current simulation time
    """
    vehicle_state = active_vehicles[vehicle_id]
    route = vehicle_state["route"]
    current_pos = vehicle_state["current_position"]
    vehicle_size = vehicle_state["size"]
    
    # Get current and next intersection
    from_intersection = route[current_pos]
    
    # Check if we have a next intersection
    if current_pos + 1 >= len(route):
        return
        
    to_intersection = route[current_pos + 1]
    
    # Find the street connecting these intersections
    street = None
    for dest, capacity, length, speed_limit in city_graph.get(from_intersection, []):
        if dest == to_intersection:
            street = (capacity, length, speed_limit)
            break
    
    if street is None:
        # Street doesn't exist - this shouldn't happen with a valid route
        return
    
    capacity, length, speed_limit = street
    street_key = (from_intersection, to_intersection)
    
    # Check if street has enough capacity
    if street_occupancy[street_key] + vehicle_size <= capacity:
        # Update vehicle position
        vehicle_state["current_position"] += 1
        
        # Update street occupancy
        street_occupancy[street_key] += vehicle_size
        
        # Calculate travel time for this street (assume speed_limit is in distance units per time unit)
        travel_time = length / speed_limit if speed_limit > 0 else 0
        arrival_time = current_time + travel_time
        
        # Schedule arrival event
        heappush(event_queue, (arrival_time, vehicle_id, "arrival_at_intersection"))
        
        # When vehicle leaves the street, reduce its occupancy
        if street_key in street_occupancy:
            street_occupancy[street_key] -= vehicle_size