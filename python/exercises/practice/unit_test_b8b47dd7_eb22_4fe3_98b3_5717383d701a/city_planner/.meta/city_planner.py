import random
import math
from typing import List

def solve_city_planning(N: int, R: int, C: int, P: int, I: int,
                       commercial_weight: int, park_weight: int,
                       infrastructure_weight: int) -> List[List[str]]:
    """
    Solves the city planning problem by placing buildings on an N x N grid to maximize happiness score.
    Uses a simulated annealing approach to find a good solution.
    """
    
    # Initialize grid with empty cells
    grid = [['.' for _ in range(N)] for _ in range(N)]
    
    # Place buildings randomly initially
    buildings = ['R']*R + ['C']*C + ['P']*P + ['I']*I
    random.shuffle(buildings)
    
    positions = random.sample([(i,j) for i in range(N) for j in range(N)], R+C+P+I)
    for (i,j), building in zip(positions, buildings):
        grid[i][j] = building
    
    # Calculate initial happiness score
    current_score = calculate_happiness(grid, commercial_weight, park_weight, infrastructure_weight)
    
    # Simulated annealing parameters
    temperature = 1.0
    cooling_rate = 0.999
    min_temperature = 0.0001
    iterations = 10000
    
    best_grid = [row[:] for row in grid]
    best_score = current_score
    
    for _ in range(iterations):
        if temperature < min_temperature:
            break
            
        # Create a new candidate solution
        new_grid = [row[:] for row in grid]
        
        # Swap two random buildings
        building_positions = [(i,j) for i in range(N) for j in range(N) if new_grid[i][j] != '.']
        if len(building_positions) < 2:
            continue
            
        a, b = random.sample(building_positions, 2)
        new_grid[a[0]][a[1]], new_grid[b[0]][b[1]] = new_grid[b[0]][b[1]], new_grid[a[0]][a[1]]
        
        # Check constraints
        if not validate_grid(new_grid):
            continue
            
        # Calculate new happiness score
        new_score = calculate_happiness(new_grid, commercial_weight, park_weight, infrastructure_weight)
        
        # Accept if better or with some probability if worse
        if new_score > current_score or random.random() < math.exp((new_score - current_score)/temperature):
            grid = new_grid
            current_score = new_score
            
            if current_score > best_score:
                best_grid = [row[:] for row in grid]
                best_score = current_score
                
        # Cool down
        temperature *= cooling_rate
    
    return best_grid

def calculate_happiness(grid: List[List[str]], commercial_weight: int, park_weight: int, infrastructure_weight: int) -> float:
    """
    Calculates the happiness score for a given grid configuration.
    """
    N = len(grid)
    happiness = 0.0
    
    # Find all building positions
    residential = []
    commercial = []
    parks = []
    infrastructure = []
    
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 'R':
                residential.append((i,j))
            elif grid[i][j] == 'C':
                commercial.append((i,j))
            elif grid[i][j] == 'P':
                parks.append((i,j))
            elif grid[i][j] == 'I':
                infrastructure.append((i,j))
    
    # Calculate happiness for each residential zone
    for (ri, rj) in residential:
        # Commercial contribution
        if commercial:
            min_commercial_dist = min(abs(ri-ci) + abs(rj-cj) for (ci,cj) in commercial)
            happiness += commercial_weight / (min_commercial_dist + 1)  # +1 to avoid division by zero
        
        # Park contribution
        if parks:
            min_park_dist = min(abs(ri-pi) + abs(rj-pj) for (pi,pj) in parks)
            happiness += park_weight / (min_park_dist + 1)
        
        # Infrastructure penalty
        if infrastructure:
            max_infra_dist = max(abs(ri-ii) + abs(rj-ij) for (ii,ij) in infrastructure)
            happiness -= infrastructure_weight * max_infra_dist
    
    return happiness

def validate_grid(grid: List[List[str]]) -> bool:
    """
    Validates that the grid meets all constraints:
    1. No park is adjacent to a commercial hub
    """
    N = len(grid)
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 'P':
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < N and 0 <= nj < N and grid[ni][nj] == 'C':
                        return False
    return True