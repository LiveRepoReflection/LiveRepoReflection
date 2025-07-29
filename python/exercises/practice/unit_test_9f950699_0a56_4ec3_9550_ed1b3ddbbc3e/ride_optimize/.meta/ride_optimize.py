from collections import defaultdict
import heapq
from typing import Dict, List, Set, Tuple
import time

def dijkstra(graph: Dict[int, Dict[int, int]], start: int) -> Dict[int, int]:
    """Implementation of Dijkstra's shortest path algorithm."""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()

    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances

def validate_input(graph: Dict[int, Dict[int, int]], 
                  drivers: List[Tuple[int, int, int]], 
                  passengers: List[Tuple[int, int, int, int]]) -> None:
    """Validate input parameters."""
    if not graph:
        raise ValueError("Graph cannot be empty")
    
    # Check for negative weights
    for node in graph:
        for _, weight in graph[node].items():
            if weight < 0:
                raise ValueError("Negative weights are not allowed")
    
    # Check for valid locations
    nodes = set(graph.keys())
    for _, location, _ in drivers:
        if location not in nodes:
            raise ValueError(f"Invalid driver location: {location}")
    
    for _, pickup, dest, _ in passengers:
        if pickup not in nodes or dest not in nodes:
            raise ValueError(f"Invalid passenger location: {pickup} or {dest}")

def optimize_rides(graph: Dict[int, Dict[int, int]], 
                  drivers: List[Tuple[int, int, int]], 
                  passengers: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int]]:
    """
    Main function to optimize ride assignments.
    
    Args:
        graph: Dictionary representing the weighted graph
        drivers: List of tuples (driver_id, location, capacity)
        passengers: List of tuples (passenger_id, pickup_location, destination_location, max_waiting_time)
    
    Returns:
        List of tuples (driver_id, passenger_id) representing assignments
    """
    # Start timing
    start_time = time.time()
    
    # Validate input
    validate_input(graph, drivers, passengers)
    
    # Initialize result
    assignments: List[Tuple[int, int]] = []
    
    # Calculate shortest paths for all drivers
    driver_distances = {}
    for driver_id, location, _ in drivers:
        driver_distances[driver_id] = dijkstra(graph, location)
    
    # Track driver capacities
    remaining_capacity = {driver_id: capacity for driver_id, _, capacity in drivers}
    
    # Sort passengers by maximum waiting time (ascending)
    sorted_passengers = sorted(
        enumerate(passengers), 
        key=lambda x: x[1][3]
    )
    
    # Track assigned passengers
    assigned_passengers: Set[int] = set()
    
    # Process each passenger
    for passenger_idx, (passenger_id, pickup, dest, max_wait) in sorted_passengers:
        if time.time() - start_time > 0.95:  # Time limit check
            break
            
        best_driver = None
        min_wait_time = float('infinity')
        
        # Find the best available driver
        for driver_id, driver_loc, _ in drivers:
            if remaining_capacity[driver_id] <= 0:
                continue
                
            # Calculate waiting time
            wait_time = driver_distances[driver_id].get(pickup, float('infinity'))
            
            if wait_time <= max_wait and wait_time < min_wait_time:
                # Check if path to destination exists
                dest_time = dijkstra(graph, pickup).get(dest, float('infinity'))
                if dest_time != float('infinity'):
                    min_wait_time = wait_time
                    best_driver = driver_id
        
        # Assign the passenger if a suitable driver was found
        if best_driver is not None:
            assignments.append((best_driver, passenger_id))
            remaining_capacity[best_driver] -= 1
            assigned_passengers.add(passenger_id)
    
    return assignments

def optimize_batch(assignments: List[Tuple[int, int]], 
                  graph: Dict[int, Dict[int, int]], 
                  drivers: List[Tuple[int, int, int]], 
                  passengers: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int]]:
    """
    Optimize a batch of assignments using local search.
    """
    improved = True
    current_cost = calculate_total_wait_time(assignments, graph, drivers, passengers)
    
    while improved and time.time() - start_time < 0.95:
        improved = False
        
        # Try swapping assignments
        for i in range(len(assignments)):
            for j in range(i + 1, len(assignments)):
                new_assignments = assignments.copy()
                new_assignments[i], new_assignments[j] = new_assignments[j], new_assignments[i]
                
                new_cost = calculate_total_wait_time(new_assignments, graph, drivers, passengers)
                
                if new_cost < current_cost:
                    assignments = new_assignments
                    current_cost = new_cost
                    improved = True
                    break
            if improved:
                break
    
    return assignments

def calculate_total_wait_time(assignments: List[Tuple[int, int]], 
                            graph: Dict[int, Dict[int, int]], 
                            drivers: List[Tuple[int, int, int]], 
                            passengers: List[Tuple[int, int, int, int]]) -> float:
    """
    Calculate total waiting time for all assignments.
    """
    total_time = 0
    driver_locations = {driver_id: loc for driver_id, loc, _ in drivers}
    
    for driver_id, passenger_id in assignments:
        pickup = next(p[1] for p in passengers if p[0] == passenger_id)
        wait_time = dijkstra(graph, driver_locations[driver_id])[pickup]
        total_time += wait_time
    
    return total_time