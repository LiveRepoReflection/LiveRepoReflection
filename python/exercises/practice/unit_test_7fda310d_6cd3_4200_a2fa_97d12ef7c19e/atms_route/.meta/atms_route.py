import heapq
import math
from typing import Dict, List, Tuple, Any, Optional


def calculate_travel_time(
    road_segment: Tuple[str, int, int, List[int]],
    traffic: int,
    current_time: int
) -> float:
    """
    Calculate the travel time for a road segment based on traffic conditions and traffic light patterns.
    
    Args:
        road_segment: A tuple (destination_id, capacity, length, traffic_light_pattern)
        traffic: Number of vehicles on the road segment
        current_time: Current time in time units
        
    Returns:
        The estimated travel time for the road segment
    """
    _, capacity, length, light_pattern = road_segment
    
    # Base travel time calculation based on road length
    # Assume baseline speed is 1 length unit per time unit when no traffic
    base_travel_time = length
    
    # Traffic impact calculation using a sigmoid function
    # As traffic approaches capacity, travel time increases rapidly
    traffic_ratio = traffic / capacity
    if traffic_ratio >= 1.0:
        traffic_multiplier = 5.0  # Severe congestion
    else:
        # Sigmoid function to model congestion: 1 + 4/(1 + e^(-10*(x-0.8)))
        # This gives a smooth transition from free-flow to congestion
        traffic_multiplier = 1.0 + 4.0 / (1.0 + math.exp(-10 * (traffic_ratio - 0.8)))
    
    # Adjusted travel time based on traffic
    adjusted_travel_time = base_travel_time * traffic_multiplier
    
    # Traffic light delay calculation
    light_cycle_total = sum(light_pattern) + 30 * len(light_pattern)  # 30 seconds of red light per green phase
    
    # Determine current position in traffic light cycle
    time_in_cycle = current_time % light_cycle_total
    
    # Check if we'll hit a red light
    light_delay = 0
    current_cycle_time = 0
    
    for green_duration in light_pattern:
        if time_in_cycle < current_cycle_time + green_duration:
            # Will arrive during green, no delay
            break
        current_cycle_time += green_duration
        
        if time_in_cycle < current_cycle_time + 30:
            # Will arrive during red, calculate delay
            light_delay = current_cycle_time + 30 - time_in_cycle
            break
        current_cycle_time += 30
    
    return adjusted_travel_time + light_delay


def predict_traffic(
    graph: Dict[str, List[Tuple[str, int, int, List[int]]]],
    current_traffic: Dict[Tuple[str, str], int],
    look_ahead: int
) -> Dict[Tuple[str, str], List[Tuple[int, int]]]:
    """
    Predict traffic conditions over the look_ahead time period.
    
    Args:
        graph: Road network graph
        current_traffic: Current traffic conditions
        look_ahead: Time horizon for prediction
        
    Returns:
        Dictionary mapping road segments to list of (time, traffic) tuples
    """
    predicted_traffic = {}
    
    # For now, implement a simple model that assumes traffic decreases slightly over time
    # A more sophisticated model would consider inflow/outflow at intersections
    for road_segment, current_vehicles in current_traffic.items():
        source, destination = road_segment
        
        # Find capacity for this road segment
        capacity = 0
        for dest, cap, _, _ in graph.get(source, []):
            if dest == destination:
                capacity = cap
                break
        
        # Initialize prediction list
        predictions = []
        
        # Simple decay model: traffic decreases by 5% every 10 time units until it reaches 50% of capacity
        current_count = current_vehicles
        min_traffic = max(capacity * 0.5, current_vehicles * 0.7)  # Don't go below 50% capacity or 70% of current
        
        for t in range(0, look_ahead, 10):
            predictions.append((t, int(current_count)))
            # Apply decay
            current_count = max(min_traffic, current_count * 0.95)
        
        # Add final prediction at look_ahead time
        predictions.append((look_ahead, int(current_count)))
        
        predicted_traffic[road_segment] = predictions
    
    return predicted_traffic


def get_traffic_at_time(
    predicted_traffic: Dict[Tuple[str, str], List[Tuple[int, int]]],
    road_segment: Tuple[str, str],
    time: int
) -> int:
    """
    Get the predicted traffic for a road segment at a specific time.
    
    Args:
        predicted_traffic: Dictionary of traffic predictions
        road_segment: The road segment to check
        time: The time to check
        
    Returns:
        Predicted traffic at the specified time
    """
    if road_segment not in predicted_traffic:
        return 0  # Default if no prediction exists
        
    predictions = predicted_traffic[road_segment]
    
    # Find the closest prediction time that's earlier than the requested time
    closest_earlier = predictions[0]
    
    for prediction_time, traffic in predictions:
        if prediction_time <= time and prediction_time >= closest_earlier[0]:
            closest_earlier = (prediction_time, traffic)
    
    # If we have a later prediction, interpolate between the two
    for prediction_time, traffic in predictions:
        if prediction_time > closest_earlier[0]:
            closest_later = (prediction_time, traffic)
            if time < closest_later[0]:
                # Linear interpolation
                time_diff = closest_later[0] - closest_earlier[0]
                if time_diff > 0:
                    weight = (time - closest_earlier[0]) / time_diff
                    interpolated_traffic = int(closest_earlier[1] + weight * (closest_later[1] - closest_earlier[1]))
                    return interpolated_traffic
                break
    
    # If no later prediction or time >= latest prediction, use the latest
    return closest_earlier[1]


def find_fastest_route(
    graph: Dict[str, List[Tuple[str, int, int, List[int]]]],
    traffic_conditions: Dict[Tuple[str, str], int],
    source: str,
    destination: str,
    time_unit: int,
    look_ahead: int
) -> Tuple[List[str], int]:
    """
    Find the fastest route from source to destination considering real-time traffic conditions.
    
    Args:
        graph: Road network graph
        traffic_conditions: Current traffic conditions
        source: Source intersection ID
        destination: Destination intersection ID
        time_unit: The smallest unit of time the system considers
        look_ahead: Time horizon for predicting traffic conditions
        
    Returns:
        A tuple containing (route, travel_time) where route is a list of intersection IDs
        and travel_time is the estimated travel time in time_unit units
    """
    # Handle edge case: source equals destination
    if source == destination:
        return [source], 0
    
    # Generate traffic predictions
    predicted_traffic = predict_traffic(graph, traffic_conditions, look_ahead)
    
    # Priority queue for Dijkstra's algorithm
    # Each element is (estimated_total_time, current_time, node, path)
    pq = [(0, 0, source, [source])]
    
    # Keep track of visited nodes with their arrival times
    # We may need to visit a node multiple times if we arrive at different times
    visited = {}  # {node: best_arrival_time}
    
    while pq:
        estimated_total_time, current_time, node, path = heapq.heappop(pq)
        
        # Check if we've reached the destination
        if node == destination:
            return path, current_time
        
        # Skip if we've already found a better path to this node
        if node in visited and visited[node] <= current_time:
            continue
            
        # Mark this node as visited with the current arrival time
        visited[node] = current_time
        
        # Explore neighbors
        for neighbor_data in graph.get(node, []):
            neighbor_id = neighbor_data[0]
            
            # Calculate travel time for this road segment
            road_segment = (node, neighbor_id)
            traffic = get_traffic_at_time(predicted_traffic, road_segment, current_time)
            segment_travel_time = calculate_travel_time(neighbor_data, traffic, current_time)
            
            # Calculate new arrival time
            new_time = current_time + segment_travel_time
            
            # Skip if we've found a better path to the neighbor
            if neighbor_id in visited and visited[neighbor_id] <= new_time:
                continue
            
            # Calculate heuristic for remaining distance (straight-line estimate)
            # This is a placeholder - in a real-world scenario, you'd use geographic coordinates
            # For now, we'll just use the shortest possible travel time based on road length
            # This maintains admissibility for A* search
            heuristic = 0
            
            # Calculate total estimated time
            total_estimated_time = new_time + heuristic
            
            # Add to priority queue
            new_path = path + [neighbor_id]
            heapq.heappush(pq, (total_estimated_time, new_time, neighbor_id, new_path))
    
    # If we've exhausted the queue without reaching the destination, no route exists
    return [], -1