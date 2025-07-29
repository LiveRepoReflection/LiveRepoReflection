import itertools
from collections import defaultdict

def optimize_tower_placement(city_blocks, cost, k, r, coverage_weight, cost_weight):
    if not city_blocks or not cost:
        raise ValueError("City blocks and cost matrices cannot be empty")
    if len(city_blocks) != len(cost) or any(len(row) != len(cost[0]) for row in city_blocks):
        raise ValueError("City blocks and cost matrices must have the same dimensions")
    if abs(coverage_weight + cost_weight - 1.0) > 1e-9:
        raise ValueError("Coverage and cost weights must sum to 1.0")
    
    rows = len(city_blocks)
    cols = len(city_blocks[0]) if rows > 0 else 0
    
    # Precompute coverage for all possible positions
    coverage_map = defaultdict(set)
    for x in range(rows):
        for y in range(cols):
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols and abs(dx) + abs(dy) <= r:
                        coverage_map[(x, y)].add((nx, ny))
    
    # Greedy algorithm with lookahead
    selected = []
    remaining_positions = set(itertools.product(range(rows), range(cols)))
    current_coverage = set()
    
    for _ in range(k):
        best_score = -float('inf')
        best_position = None
        best_new_coverage = set()
        
        for pos in remaining_positions:
            x, y = pos
            new_coverage = coverage_map[pos] - current_coverage
            coverage_gain = len(new_coverage)
            total_cost = cost[x][y]
            
            score = (coverage_weight * coverage_gain) - (cost_weight * total_cost)
            
            if score > best_score or (score == best_score and total_cost < cost[best_position[0]][best_position[1]]):
                best_score = score
                best_position = pos
                best_new_coverage = new_coverage
        
        if best_position is None:
            break
            
        selected.append(best_position)
        current_coverage.update(best_new_coverage)
        remaining_positions.remove(best_position)
    
    return selected