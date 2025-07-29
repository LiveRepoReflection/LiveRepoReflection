import heapq
from collections import defaultdict
import random
import math

def simulate_traffic(N, roads, lights, green_times, max_cycle_time, arrival_times):
    # Build graph
    graph = defaultdict(list)
    for u, v, length, speed in roads:
        travel_time = length / speed
        graph[u].append((v, travel_time))
    
    # Initialize traffic light schedules
    light_schedules = {}
    for i, light in enumerate(lights):
        green_time = green_times[i]
        red_time = max_cycle_time - green_time
        light_schedules[light] = (green_time, red_time)
    
    total_wait_time = 0
    num_vehicles = len(arrival_times)
    
    for arrival_time, path in arrival_times:
        current_time = arrival_time
        for i in range(len(path)-1):
            current_node = path[i]
            next_node = path[i+1]
            
            # Find travel time to next node
            travel_time = None
            for neighbor, t in graph[current_node]:
                if neighbor == next_node:
                    travel_time = t
                    break
            
            if travel_time is None:
                raise ValueError("Invalid path")
            
            # Arrive at next node
            arrival_at_next = current_time + travel_time
            
            # Check if next node has traffic light
            if next_node in light_schedules:
                green, red = light_schedules[next_node]
                cycle_time = green + red
                
                # Calculate time in current cycle
                time_in_cycle = arrival_at_next % cycle_time
                
                # Calculate wait time
                if time_in_cycle > green:
                    wait_time = cycle_time - time_in_cycle
                    total_wait_time += wait_time
                    current_time = arrival_at_next + wait_time
                else:
                    current_time = arrival_at_next
            else:
                current_time = arrival_at_next
    
    return total_wait_time / num_vehicles if num_vehicles > 0 else 0

def optimize_traffic_lights(N, M, roads, K, lights, max_cycle_time, arrival_times):
    # Simulated annealing parameters
    initial_temp = 1000
    cooling_rate = 0.99
    min_temp = 1
    iterations_per_temp = 100
    
    # Initial random solution
    current_solution = [random.uniform(0, max_cycle_time) for _ in range(K)]
    current_cost = simulate_traffic(N, roads, lights, current_solution, max_cycle_time, arrival_times)
    
    best_solution = current_solution.copy()
    best_cost = current_cost
    
    temp = initial_temp
    
    while temp > min_temp:
        for _ in range(iterations_per_temp):
            # Generate neighbor solution
            neighbor_solution = []
            for i in range(K):
                perturbation = random.uniform(-temp/10, temp/10)
                new_val = current_solution[i] + perturbation
                new_val = max(0, min(new_val, max_cycle_time))
                neighbor_solution.append(new_val)
            
            neighbor_cost = simulate_traffic(N, roads, lights, neighbor_solution, max_cycle_time, arrival_times)
            
            # Calculate acceptance probability
            if neighbor_cost < current_cost:
                current_solution = neighbor_solution
                current_cost = neighbor_cost
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
            else:
                delta = neighbor_cost - current_cost
                acceptance_prob = math.exp(-delta / temp)
                if random.random() < acceptance_prob:
                    current_solution = neighbor_solution
                    current_cost = neighbor_cost
        
        temp *= cooling_rate
    
    # Round to 2 decimal places
    return [round(x, 2) for x in best_solution]