from heapq import heappush, heappop
from collections import defaultdict
import math

def optimize_traffic(network, source, destination, total_flow, default_speed_limit, penalty_exponent, max_penalty):
    """
    Optimizes traffic flow by adjusting speed limits on road segments.
    Returns a dictionary of optimal speed limits for segments on the shortest path.
    """
    if not network or total_flow <= 0 or default_speed_limit <= 0:
        raise ValueError("Invalid input parameters")

    def calculate_segment_metrics(length, base_capacity, speed_factor, flow):
        """Calculate travel time and congestion penalty for a road segment"""
        effective_capacity = base_capacity * speed_factor
        travel_time = length / (default_speed_limit * speed_factor)
        
        if flow > effective_capacity:
            return float('inf'), float('inf')
        
        utilization_rate = flow / effective_capacity
        congestion_penalty = utilization_rate ** penalty_exponent
        
        return travel_time, congestion_penalty

    def find_optimal_speed_factor(length, base_capacity, flow):
        """Binary search for optimal speed factor that minimizes travel time while respecting constraints"""
        left, right = 0.5, 1.5
        best_speed = None
        best_time = float('inf')
        
        for _ in range(20):  # Binary search iterations
            speed = (left + right) / 2
            travel_time, penalty = calculate_segment_metrics(length, base_capacity, speed, flow)
            
            if penalty <= max_penalty and travel_time < best_time:
                best_speed = speed
                best_time = travel_time
            
            if penalty > max_penalty:
                left = speed
            else:
                right = speed
        
        return best_speed if best_speed is not None else 1.0

    def dijkstra():
        """Modified Dijkstra's algorithm to find shortest path with optimal speed factors"""
        distances = {node: float('inf') for node in network}
        distances[source] = 0
        predecessors = {}
        speed_factors = {}
        total_penalties = {node: 0 for node in network}
        
        pq = [(0, source)]
        
        while pq:
            current_dist, current = heappop(pq)
            
            if current == destination:
                break
                
            if current_dist > distances[current]:
                continue
            
            for next_node, length, base_capacity in network.get(current, []):
                optimal_speed = find_optimal_speed_factor(length, base_capacity, total_flow)
                if optimal_speed is None:
                    continue
                    
                travel_time, penalty = calculate_segment_metrics(length, base_capacity, optimal_speed, total_flow)
                new_dist = distances[current] + travel_time
                new_penalty = total_penalties[current] + penalty
                
                if new_dist < distances[next_node] and new_penalty <= max_penalty:
                    distances[next_node] = new_dist
                    total_penalties[next_node] = new_penalty
                    predecessors[next_node] = current
                    speed_factors[(current, next_node)] = optimal_speed
                    heappush(pq, (new_dist, next_node))
        
        return predecessors, speed_factors

    # Find shortest path and optimal speed factors
    predecessors, speed_factors = dijkstra()
    
    # If no path found to destination
    if destination not in predecessors and destination != source:
        return {}
    
    # Reconstruct the path and collect speed factors
    result = {}
    current = destination
    while current in predecessors:
        prev = predecessors[current]
        result[(prev, current)] = speed_factors[(prev, current)]
        current = prev
    
    return result