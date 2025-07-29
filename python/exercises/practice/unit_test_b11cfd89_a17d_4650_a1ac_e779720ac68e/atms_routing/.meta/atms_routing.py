import heapq
from typing import Dict, List, Callable, Optional

def find_fastest_route(
    graph: Dict[int, Dict[str, Dict[int, Dict[str, float]]]],
    start_intersection_id: int,
    end_intersection_id: int,
    departure_time: float
) -> List[int]:
    """
    Find the fastest route between two intersections in a traffic network.
    
    Args:
        graph: The road network graph representation
        start_intersection_id: Starting intersection ID
        end_intersection_id: Destination intersection ID
        departure_time: Time when the journey begins
        
    Returns:
        List of intersection IDs representing the fastest route
    """
    
    if start_intersection_id not in graph or end_intersection_id not in graph:
        return []
    
    if start_intersection_id == end_intersection_id:
        return [start_intersection_id]
    
    # Priority queue: (total_time, current_node, path)
    heap = []
    heapq.heappush(heap, (0, start_intersection_id, [start_intersection_id]))
    
    # Dictionary to store the best known time to reach each node
    best_times = {node: float('inf') for node in graph}
    best_times[start_intersection_id] = 0
    
    # Dictionary to store the best path to each node
    best_paths = {start_intersection_id: [start_intersection_id]}
    
    while heap:
        current_time, current_node, current_path = heapq.heappop(heap)
        
        if current_node == end_intersection_id:
            return current_path
        
        if current_time > best_times[current_node]:
            continue
            
        for neighbor, road_data in graph[current_node]['neighbors'].items():
            length = road_data['length']
            speed_limit = road_data['speed_limit']
            current_traffic = road_data['current_traffic']
            delay_function = road_data['delay_function']
            
            # Calculate base travel time (without traffic)
            speed_mps = speed_limit * 1000 / 3600  # Convert km/h to m/s
            base_time = length / speed_mps
            
            # Calculate traffic delay
            traffic_delay = delay_function(current_traffic) * current_traffic
            
            # Total time to traverse this road segment
            segment_time = base_time + traffic_delay
            
            total_time = current_time + segment_time
            
            if total_time < best_times[neighbor]:
                best_times[neighbor] = total_time
                new_path = current_path + [neighbor]
                best_paths[neighbor] = new_path
                heapq.heappush(heap, (total_time, neighbor, new_path))
    
    return []