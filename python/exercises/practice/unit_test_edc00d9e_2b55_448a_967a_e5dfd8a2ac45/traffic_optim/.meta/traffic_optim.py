from collections import defaultdict
import heapq

def min_travel_time(N, edges, queries):
    """
    Calculate the minimum travel time for each query in a traffic network.
    
    Args:
        N: Number of intersections (nodes) in the city
        edges: List of tuples (u, v, w) representing directed edges with weights
        queries: List of tuples (start, end, timestamp, congestion_events, blocked_events)
    
    Returns:
        List of integers representing the minimum travel time for each query
    """
    # Build adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    
    results = []
    
    for start, end, timestamp, congestion_events, blocked_events in queries:
        # Apply congestion and blockage events to create a modified graph for this query
        modified_graph = modify_graph(graph, N, timestamp, congestion_events, blocked_events)
        
        # Find the shortest path using Dijkstra's algorithm
        distance = dijkstra(modified_graph, N, start, end)
        
        # If distance is float('inf'), no path exists
        results.append(distance if distance != float('inf') else -1)
    
    return results

def modify_graph(graph, N, timestamp, congestion_events, blocked_events):
    """
    Modify the graph based on congestion and blockage events at the given timestamp.
    
    Args:
        graph: Original adjacency list representation of the graph
        N: Number of nodes
        timestamp: Current timestamp for the query
        congestion_events: List of congestion events
        blocked_events: List of blockage events
    
    Returns:
        Modified adjacency list representation of the graph
    """
    # Create a copy of the graph to modify
    modified_graph = defaultdict(list)
    
    # Copy the original graph
    for u in range(N):
        for v, w in graph[u]:
            modified_graph[u].append((v, w))
    
    # Process congestion events
    congestion_factors = {}
    for road_start, road_end, start_time, end_time, factor in congestion_events:
        # Only apply congestion if the timestamp falls within the event time range
        if start_time <= timestamp <= end_time:
            # Store the worst congestion factor for each road
            key = (road_start, road_end)
            congestion_factors[key] = max(congestion_factors.get(key, 0), factor)
    
    # Apply congestion factors to the graph
    for u in range(N):
        for i, (v, w) in enumerate(modified_graph[u]):
            key = (u, v)
            if key in congestion_factors:
                # Replace the edge with the congested weight
                modified_graph[u][i] = (v, w * congestion_factors[key])
    
    # Process blockage events - remove blocked roads
    for road_start, road_end, start_time, end_time in blocked_events:
        if start_time <= timestamp <= end_time:
            # Remove the blocked road from the graph
            modified_graph[road_start] = [(v, w) for v, w in modified_graph[road_start] if v != road_end]
    
    return modified_graph

def dijkstra(graph, N, start, end):
    """
    Implement Dijkstra's algorithm to find the shortest path.
    
    Args:
        graph: Adjacency list representation of the graph
        N: Number of nodes
        start: Starting node
        end: Destination node
    
    Returns:
        The minimum distance from start to end, or float('inf') if no path exists
    """
    # Initialize distances with infinity
    distances = [float('inf')] * N
    distances[start] = 0
    
    # Priority queue to keep track of nodes to visit
    priority_queue = [(0, start)]  # (distance, node)
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # If we've already found a better path to the current node, skip
        if current_distance > distances[current_node]:
            continue
        
        # If we've reached the destination, we're done
        if current_node == end:
            return current_distance
        
        # Check all neighboring nodes
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            
            # If we found a better path, update the distance and add to queue
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # If we've exhausted all possible paths and haven't reached the end
    return distances[end]