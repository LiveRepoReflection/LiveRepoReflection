import heapq
from collections import defaultdict

def minimum_average_travel_time(graph, observatories):
    """
    Calculate the minimum average travel time for synchronization between volcano observatories.
    
    Args:
        graph: A dictionary representing the adjacency list of the graph.
               Keys are island names (strings).
               Values are lists of tuples (neighbor_island, travel_time).
        observatories: A list of strings representing the names of the volcano observatories.
    
    Returns:
        A float representing the minimum average travel time, rounded to 6 decimal places.
        If no path exists between any pair of observatories, return float('inf').
    """
    # Handle edge cases
    if len(observatories) <= 1:
        return 0.0
    
    # Remove duplicate observatories
    unique_observatories = list(set(observatories))
    
    # Calculate total number of observatory pairs
    num_pairs = len(unique_observatories) * (len(unique_observatories) - 1)
    
    if num_pairs == 0:
        return 0.0
    
    # Calculate shortest paths between all observatory pairs
    total_travel_time = 0
    
    for source in unique_observatories:
        # Use Dijkstra's algorithm to find shortest paths from source to all other nodes
        distances = dijkstra(graph, source)
        
        # Sum up distances to other observatories
        for target in unique_observatories:
            if source != target:
                if target not in distances or distances[target] == float('inf'):
                    # If any pair of observatories is not connected, return infinity
                    return float('inf')
                total_travel_time += distances[target]
    
    # Calculate average travel time
    avg_travel_time = total_travel_time / num_pairs
    
    # Round to 6 decimal places
    return avg_travel_time

def dijkstra(graph, source):
    """
    Implementation of Dijkstra's algorithm to find the shortest paths from a source node to all other nodes.
    
    Args:
        graph: A dictionary representing the adjacency list of the graph.
        source: The source node to start the search from.
    
    Returns:
        A dictionary mapping each node to its shortest distance from the source.
    """
    # Initialize distances with infinity for all nodes except the source
    distances = {node: float('inf') for node in graph}
    distances[source] = 0
    
    # Priority queue to track nodes to visit
    priority_queue = [(0, source)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # If we've already found a shorter path to the current node, skip
        if current_distance > distances[current_node]:
            continue
        
        # Check all neighbors of the current node
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            
            # If we found a shorter path to the neighbor, update the distance
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances