import random
import math

def assign_microservices(N, M, edges, latency_matrix):
    if N == 0 or M == 0:
        return []
    
    # Initialize with random assignment
    current_assignment = [random.randint(0, M-1) for _ in range(N)]
    current_cost = calculate_total_cost(current_assignment, edges, latency_matrix)
    
    # Simulated annealing parameters
    initial_temp = 1000
    final_temp = 0.1
    alpha = 0.99
    max_iterations = 10000
    
    temp = initial_temp
    iteration = 0
    
    while temp > final_temp and iteration < max_iterations:
        # Generate neighbor solution
        neighbor_assignment = current_assignment.copy()
        service_to_change = random.randint(0, N-1)
        new_dc = random.randint(0, M-1)
        neighbor_assignment[service_to_change] = new_dc
        
        # Calculate neighbor cost
        neighbor_cost = calculate_total_cost(neighbor_assignment, edges, latency_matrix)
        
        # Calculate cost difference
        cost_diff = neighbor_cost - current_cost
        
        # Decide whether to accept neighbor
        if cost_diff < 0 or random.random() < math.exp(-cost_diff / temp):
            current_assignment = neighbor_assignment
            current_cost = neighbor_cost
        
        # Cool down
        temp *= alpha
        iteration += 1
    
    return current_assignment

def calculate_total_cost(assignment, edges, latency_matrix):
    total_cost = 0
    for (si, sj, weight) in edges:
        dc_i = assignment[si]
        dc_j = assignment[sj]
        total_cost += weight * latency_matrix[dc_i][dc_j]
    return total_cost