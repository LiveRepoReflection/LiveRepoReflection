import math
import random
from itertools import combinations

def circuit_placement(N, M, connections, D):
    # Initialize positions randomly within bounds
    positions = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(N)]
    
    # Simulated annealing parameters
    temp = 1000
    cooling_rate = 0.99
    min_temp = 1e-3
    max_iter = 10000
    
    def calculate_cost(pos):
        cost = 0
        for c1, c2, weight in connections:
            x1, y1 = pos[c1]
            x2, y2 = pos[c2]
            cost += weight * (abs(x1 - x2) + abs(y1 - y2))
        return cost
    
    def distance_constraint_satisfied(pos):
        for (i, p1), (j, p2) in combinations(enumerate(pos), 2):
            x1, y1 = p1
            x2, y2 = p2
            if math.sqrt((x1-x2)**2 + (y1-y2)**2) < D:
                return False
        return True
    
    current_cost = calculate_cost(positions)
    
    for _ in range(max_iter):
        if temp < min_temp:
            break
            
        # Generate neighbor solution
        new_positions = positions.copy()
        idx = random.randint(0, N-1)
        new_positions[idx] = (
            max(0, min(100, new_positions[idx][0] + random.uniform(-5, 5))),
            max(0, min(100, new_positions[idx][1] + random.uniform(-5, 5)))
        )
        
        # Check constraints
        if not distance_constraint_satisfied(new_positions):
            continue
            
        new_cost = calculate_cost(new_positions)
        
        # Acceptance probability
        if new_cost < current_cost or random.random() < math.exp((current_cost - new_cost)/temp):
            positions = new_positions
            current_cost = new_cost
            
        temp *= cooling_rate
    
    # Round to 2 decimal places
    return [(round(x, 2), round(y, 2)) for x, y in positions]