import heapq
import math
from collections import defaultdict
from functools import lru_cache

def find_min_cost_path(N, edges, start_node, end_node, earliest_departure_time, latest_departure_time, time_step, ship_speed, get_hazard_score):
    """
    Finds the minimum cost path between two nodes in a dynamic maritime environment.

    Args:
        N: The number of nodes.
        edges: A list of tuples (u, v, distance) representing edges.
        start_node: The starting node.
        end_node: The destination node.
        earliest_departure_time: The earliest departure time.
        latest_departure_time: The latest departure time.
        time_step: The time step.
        ship_speed: The ship's speed.
        get_hazard_score: A function that takes (u, v, timestamp) and returns the hazard score.

    Returns:
        The minimum cost of the path from start_node to end_node, or float('inf') if no path exists.
    """
    # Early exit if start and end are the same
    if start_node == end_node:
        return 0
    
    # Build the graph
    graph = defaultdict(list)
    for u, v, distance in edges:
        graph[u].append((v, distance))
        graph[v].append((u, distance))  # Undirected graph
    
    # If start_node or end_node are not in the graph, return infinity
    if start_node not in graph or end_node not in graph:
        return float('inf')
    
    # Cache for hazard scores to avoid expensive recalculations
    @lru_cache(maxsize=None)
    def cached_hazard_score(u, v, timestamp):
        return get_hazard_score(u, v, timestamp)
    
    # Calculate travel time for an edge, rounded up to nearest time_step
    def calculate_travel_time(distance):
        raw_time = distance / ship_speed
        return math.ceil(raw_time / time_step) * time_step
    
    # Calculate edge cost with hazard at a specific timestamp
    def calculate_edge_cost(u, v, distance, timestamp):
        hazard = cached_hazard_score(u, v, timestamp)
        return distance * (1 + hazard)
    
    # Modified Dijkstra's algorithm to find the minimum cost path
    min_cost = float('inf')
    
    # For each possible departure time
    for departure_time in range(earliest_departure_time, latest_departure_time + 1, time_step):
        # Use a priority queue for Dijkstra's algorithm
        # (cost, node, current_time)
        pq = [(0, start_node, departure_time)]
        # Keep track of visited nodes with their arrival time
        visited = {}
        
        while pq:
            cost, node, current_time = heapq.heappop(pq)
            
            # If we've reached the destination, update min_cost
            if node == end_node:
                min_cost = min(min_cost, cost)
                break
            
            # Skip if we've already visited this node at this time or earlier with a lower cost
            if node in visited and visited[node] <= current_time:
                continue
            
            # Mark node as visited at this time
            visited[node] = current_time
            
            # Explore neighbors
            for neighbor, distance in graph[node]:
                # Calculate travel time
                travel_time = calculate_travel_time(distance)
                arrival_time = current_time + travel_time
                
                # Calculate edge cost based on current time
                edge_cost = calculate_edge_cost(node, neighbor, distance, current_time)
                new_cost = cost + edge_cost
                
                # Add neighbor to the priority queue
                heapq.heappush(pq, (new_cost, neighbor, arrival_time))
    
    return min_cost