import heapq
import random
import math
import time
from collections import defaultdict, deque

def optimize_traffic_lights(N, edges, trips, min_duration, max_duration):
    """
    Optimize traffic light durations to minimize average travel time.
    
    Args:
        N (int): Number of intersections
        edges (list): List of tuples (u, v, t) representing roads and travel times
        trips (list): List of tuples (source, destination, traffic_volume)
        min_duration (int): Minimum allowed duration for traffic lights
        max_duration (int): Maximum allowed duration for traffic lights
    
    Returns:
        list: List of tuples (red_duration, green_duration) for each intersection
    """
    # Build the graph
    graph = defaultdict(list)
    for u, v, t in edges:
        graph[u].append((v, t))
    
    # If no trips, return default values
    if not trips:
        return [(min_duration, max_duration) for _ in range(N)]
    
    # Initialize solution with random light durations
    best_solution = [(random.randint(min_duration, max_duration), 
                      random.randint(min_duration, max_duration)) for _ in range(N)]
    best_avg_time = calculate_average_travel_time(N, graph, trips, best_solution)
    
    # Use a combination of simulated annealing and hill climbing
    return simulated_annealing(N, graph, trips, min_duration, max_duration, best_solution, best_avg_time)

def calculate_average_travel_time(N, graph, trips, light_durations):
    """Calculate average travel time across all trips with given light settings"""
    total_weighted_time = 0
    total_volume = 0
    
    for source, destination, volume in trips:
        if source == destination:
            continue  # No travel time for same source and destination
        
        travel_time = shortest_path_with_lights(N, graph, source, destination, light_durations)
        
        # If path doesn't exist, assign a large penalty
        if travel_time == float('inf'):
            travel_time = 10000  # Large penalty for impossible trips
        
        total_weighted_time += travel_time * volume
        total_volume += volume
    
    if total_volume == 0:
        return 0  # Avoid division by zero
    
    return total_weighted_time / total_volume

def shortest_path_with_lights(N, graph, source, destination, light_durations):
    """Find shortest path considering traffic lights"""
    # Initialize distances
    distances = [float('inf')] * N
    distances[source] = 0
    
    # Priority queue for Dijkstra's algorithm
    pq = [(0, source)]  # (time, node)
    
    while pq:
        current_time, current_node = heapq.heappop(pq)
        
        if current_node == destination:
            return current_time
        
        if current_time > distances[current_node]:
            continue  # Skip if we already found a better path
        
        # Get current node's traffic light settings
        red_duration, green_duration = light_durations[current_node]
        cycle_duration = red_duration + green_duration
        
        for neighbor, travel_time in graph[current_node]:
            # Calculate wait time at intersection
            # Simplified model: add average wait time based on light cycle
            wait_time = 0
            if current_node != source:  # No wait time at the starting node
                # Probability of hitting a red light and expected wait time
                # On average, wait half the red duration
                wait_time = red_duration * red_duration / (2 * cycle_duration)
            
            new_time = current_time + travel_time + wait_time
            
            if new_time < distances[neighbor]:
                distances[neighbor] = new_time
                heapq.heappush(pq, (new_time, neighbor))
    
    return distances[destination]  # Will be inf if no path exists

def simulated_annealing(N, graph, trips, min_duration, max_duration, initial_solution, initial_cost):
    """Use simulated annealing to optimize traffic light durations"""
    current_solution = initial_solution.copy()
    current_cost = initial_cost
    best_solution = current_solution.copy()
    best_cost = current_cost
    
    # Simulated annealing parameters
    temperature = 100.0
    cooling_rate = 0.95
    iterations_per_temp = 20
    min_temperature = 0.1
    
    # Time limit in seconds
    time_limit = min(30, N * len(trips) * 0.1)  # Scale with problem size, but cap at 30 seconds
    start_time = time.time()
    
    while temperature > min_temperature and time.time() - start_time < time_limit:
        for _ in range(iterations_per_temp):
            # Generate a neighbor solution
            neighbor = current_solution.copy()
            
            # Choose random light to modify
            intersection = random.randint(0, N-1)
            
            # Modify either red or green duration
            if random.random() < 0.5:
                # Modify red duration
                neighbor[intersection] = (
                    random.randint(min_duration, max_duration),
                    neighbor[intersection][1]
                )
            else:
                # Modify green duration
                neighbor[intersection] = (
                    neighbor[intersection][0],
                    random.randint(min_duration, max_duration)
                )
            
            # Calculate new cost
            neighbor_cost = calculate_average_travel_time(N, graph, trips, neighbor)
            
            # Decide whether to accept the neighbor
            cost_diff = neighbor_cost - current_cost
            
            # Always accept if better; sometimes accept if worse based on temperature
            if cost_diff < 0 or random.random() < math.exp(-cost_diff / temperature):
                current_solution = neighbor
                current_cost = neighbor_cost
                
                # Update best solution if this is better
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
        
        # Cool down
        temperature *= cooling_rate
    
    # After simulated annealing, perform hill climbing to fine-tune
    best_solution = hill_climbing(N, graph, trips, min_duration, max_duration, best_solution, best_cost, time_limit - (time.time() - start_time))
    
    return best_solution

def hill_climbing(N, graph, trips, min_duration, max_duration, initial_solution, initial_cost, time_limit):
    """Use hill climbing to fine-tune the solution"""
    current_solution = initial_solution.copy()
    current_cost = initial_cost
    
    improved = True
    start_time = time.time()
    
    while improved and time.time() - start_time < time_limit:
        improved = False
        
        # Try to improve each intersection's settings
        for i in range(N):
            original_setting = current_solution[i]
            
            # Try different values for red duration
            for red in range(min_duration, max_duration + 1, max(1, (max_duration - min_duration) // 10)):
                current_solution[i] = (red, original_setting[1])
                new_cost = calculate_average_travel_time(N, graph, trips, current_solution)
                
                if new_cost < current_cost:
                    current_cost = new_cost
                    improved = True
                else:
                    # Revert if not better
                    current_solution[i] = original_setting
            
            # Try different values for green duration
            for green in range(min_duration, max_duration + 1, max(1, (max_duration - min_duration) // 10)):
                current_solution[i] = (current_solution[i][0], green)
                new_cost = calculate_average_travel_time(N, graph, trips, current_solution)
                
                if new_cost < current_cost:
                    current_cost = new_cost
                    improved = True
                else:
                    # Keep the best red but revert green if not better
                    current_solution[i] = (current_solution[i][0], original_setting[1])
                    
    return current_solution