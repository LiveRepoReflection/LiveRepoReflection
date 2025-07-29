import heapq
from collections import defaultdict
import threading
from typing import Dict, List, Tuple, Callable, Set, Any

def optimize_multi_source_paths(
    graph: Dict[Any, List[Tuple[Any, float]]],
    sources: List[Any],
    T: float,
    congestion_factor: Callable[[float, float], float],
    vehicle_rate: float
) -> Dict[Any, Dict[Any, float]]:
    """
    Calculate the optimal paths from multiple sources to all other nodes in a graph,
    considering traffic congestion that evolves over time.
    
    Args:
        graph: A weighted, directed graph represented as an adjacency list.
                Each node maps to a list of (destination_node, base_travel_time) tuples.
        sources: List of source nodes from which to calculate shortest paths.
        T: Simulation duration.
        congestion_factor: Function that returns a multiplier for edge weight based on time and flow.
        vehicle_rate: Rate at which vehicles are added to an edge when it's traversed (vehicles/second).
    
    Returns:
        A dictionary mapping source nodes to dictionaries of destination nodes and their shortest travel times.
    """
    if not sources:
        return {}
    
    # Initialize result dictionary
    result = {}
    
    # Initialize traffic flow tracking
    edge_flows = defaultdict(lambda: defaultdict(float))
    
    # Thread lock for synchronized access to edge_flows
    lock = threading.RLock()
    
    # Get all nodes in the graph
    all_nodes = set(graph.keys()).union({dest for adj_list in graph.values() for dest, _ in adj_list})
    
    # Process each source node
    for source in sources:
        # Initialize distances with infinity for all nodes
        distances = {node: float('inf') for node in all_nodes}
        distances[source] = 0
        
        # Initialize predecessor tracking for path reconstruction
        predecessors = {node: None for node in all_nodes}
        
        # Initialize priority queue with source node
        priority_queue = [(0, source)]
        
        # Track visited nodes for potential optimizations
        visited = set()
        
        # Track arrival times at each node
        arrival_times = {node: float('inf') for node in all_nodes}
        arrival_times[source] = 0
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # Skip if we've already found a shorter path to this node
            if current_distance > distances[current_node]:
                continue
            
            # Skip if we've already processed this node
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Process all neighbors
            for neighbor, base_weight in graph.get(current_node, []):
                # Calculate the current time at which we're traversing this edge
                current_time = arrival_times[current_node]
                
                # Skip if we're beyond the simulation time
                if current_time >= T:
                    continue
                
                # Get the current flow on this edge
                with lock:
                    current_flow = edge_flows[current_node][neighbor]
                
                # Calculate the actual travel time considering congestion
                congestion_multiplier = congestion_factor(current_time, current_flow)
                actual_weight = base_weight * congestion_multiplier
                
                # Calculate new distance to neighbor through current node
                new_distance = distances[current_node] + actual_weight
                
                # If we found a shorter path, update distance and add to priority queue
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    arrival_times[neighbor] = current_time + actual_weight
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        # Once we have computed all shortest paths from this source,
        # simulate traffic flow along these paths
        for dest in all_nodes:
            if dest == source or distances[dest] == float('inf'):
                continue
                
            # Reconstruct path from source to dest
            path = []
            current = dest
            while current != source:
                prev = predecessors[current]
                if prev is None:  # Should not happen if distance is finite
                    break
                path.append((prev, current))
                current = prev
            path.reverse()  # Path is now from source to dest
            
            # Simulate traffic flow along the path
            current_time = 0
            for from_node, to_node in path:
                # Get the base travel time for this edge
                base_weight = next((w for n, w in graph.get(from_node, []) if n == to_node), float('inf'))
                
                # Get the current flow
                with lock:
                    current_flow = edge_flows[from_node][to_node]
                
                # Calculate the actual travel time
                congestion_multiplier = congestion_factor(current_time, current_flow)
                actual_weight = base_weight * congestion_multiplier
                
                # Update the flow for the duration of traversal
                travel_time = actual_weight
                
                with lock:
                    edge_flows[from_node][to_node] += vehicle_rate
                
                current_time += travel_time
        
        # Store the distances for this source
        result[source] = distances
    
    return result