from heapq import heappush, heappop
from typing import Dict, List, Tuple, Optional

def calculate_total_cost(
    distance: float,
    congestion: float,
    hub_occupancy: int,
    hub_capacity: int
) -> float:
    """Calculate the total cost (time) to traverse a path."""
    # Base cost is distance * congestion
    base_cost = distance * congestion
    
    # If hub is at or near capacity, add penalty
    if hub_occupancy >= hub_capacity:
        return float('inf')  # Hub is full
    elif hub_occupancy >= hub_capacity * 0.8:  # Hub is near capacity
        occupancy_factor = (hub_occupancy / hub_capacity) * 1.5
        return base_cost * (1 + occupancy_factor)
    
    return base_cost

def find_optimal_route(
    graph: Dict,
    source_hub_id: int,
    destination_hub_id: int,
    drone_battery_capacity: float,
    current_hub_occupancy: Dict[int, int]
) -> Optional[List[int]]:
    """
    Find the optimal route for a drone delivery considering battery constraints,
    hub capacities, and congestion.
    
    Args:
        graph: Network graph representation
        source_hub_id: Starting hub ID
        destination_hub_id: Target hub ID
        drone_battery_capacity: Initial battery capacity
        current_hub_occupancy: Current number of drones at each hub
    
    Returns:
        List of hub IDs representing the optimal route, or None if no valid route exists
    """
    # Handle same source and destination
    if source_hub_id == destination_hub_id:
        return []
    
    # Validate input hubs exist in graph
    if source_hub_id not in graph or destination_hub_id not in graph:
        return None

    # Priority queue for Dijkstra's algorithm
    # Format: (total_cost, battery_remaining, current_hub, path)
    pq = [(0, drone_battery_capacity, source_hub_id, [source_hub_id])]
    
    # Track visited states to avoid cycles
    # State: (hub_id, battery_remaining)
    visited = set()
    
    while pq:
        total_cost, battery_remaining, current_hub, path = heappop(pq)
        
        # Check if we've reached the destination
        if current_hub == destination_hub_id:
            return path
        
        # Create state tuple for current position
        state = (current_hub, round(battery_remaining, 2))
        
        # Skip if we've seen this state with better parameters
        if state in visited:
            continue
        visited.add(state)
        
        # Explore all possible edges from current hub
        for next_hub, distance, congestion in graph[current_hub]['edges']:
            # Calculate energy required for this edge
            energy_required = distance * congestion
            
            # Skip if we don't have enough battery
            if energy_required > battery_remaining:
                continue
            
            # Calculate new battery level after traversing edge
            new_battery = battery_remaining - energy_required
            
            # Get next hub's capacity and current occupancy
            next_hub_capacity = graph[next_hub]['capacity']
            next_hub_occupancy = current_hub_occupancy.get(next_hub, 0)
            
            # Calculate total cost for this edge
            edge_cost = calculate_total_cost(
                distance,
                congestion,
                next_hub_occupancy,
                next_hub_capacity
            )
            
            # Skip if hub is full (edge_cost will be inf)
            if edge_cost == float('inf'):
                continue
            
            # Calculate new total cost
            new_total_cost = total_cost + edge_cost
            
            # Create new path
            new_path = path + [next_hub]
            
            # Add to priority queue if we haven't visited this state
            new_state = (next_hub, round(new_battery, 2))
            if new_state not in visited:
                heappush(pq, (new_total_cost, new_battery, next_hub, new_path))
    
    # No valid path found
    return None

def validate_graph(graph: Dict) -> bool:
    """Validate graph structure and data types."""
    try:
        for hub_id, hub_data in graph.items():
            if not isinstance(hub_id, int):
                return False
            
            required_keys = {'coordinates', 'capacity', 'edges'}
            if not all(key in hub_data for key in required_keys):
                return False
            
            if not isinstance(hub_data['coordinates'], tuple) or \
               len(hub_data['coordinates']) != 2 or \
               not all(isinstance(x, (int, float)) for x in hub_data['coordinates']):
                return False
            
            if not isinstance(hub_data['capacity'], int) or hub_data['capacity'] <= 0:
                return False
            
            if not isinstance(hub_data['edges'], list):
                return False
            
            for edge in hub_data['edges']:
                if not isinstance(edge, tuple) or \
                   len(edge) != 3 or \
                   not isinstance(edge[0], int) or \
                   not isinstance(edge[1], (int, float)) or \
                   not isinstance(edge[2], (int, float)):
                    return False
                
                if edge[1] <= 0 or edge[2] <= 0:
                    return False
        
        return True
    except Exception:
        return False