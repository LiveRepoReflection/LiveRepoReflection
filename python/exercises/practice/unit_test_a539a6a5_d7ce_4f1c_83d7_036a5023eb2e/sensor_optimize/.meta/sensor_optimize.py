import math
from typing import List, Tuple

def calculate_coverage(sensor_locations: List[Tuple[float, float]], 
                     sensor_ranges: List[float],
                     region_locations: List[Tuple[float, float]]) -> List[List[int]]:
    coverage = []
    for region_x, region_y in region_locations:
        region_coverage = []
        for (sensor_x, sensor_y), sensor_range in zip(sensor_locations, sensor_ranges):
            distance = math.sqrt((sensor_x - region_x)**2 + (sensor_y - region_y)**2)
            region_coverage.append(1 if distance <= sensor_range else 0)
        coverage.append(region_coverage)
    return coverage

def optimize_sensor_network(N: int, M: int, K: int, T: int,
                          sensor_locations: List[Tuple[float, float]],
                          sensor_ranges: List[int],
                          region_locations: List[Tuple[float, float]],
                          region_importances: List[int]) -> List[List[int]]:
    
    # Precompute which sensors cover which regions
    coverage = calculate_coverage(sensor_locations, sensor_ranges, region_locations)
    
    # Initialize battery levels
    batteries = [100] * N
    
    # Initialize action plan
    action_plan = []
    
    for _ in range(T):
        # Calculate current coverage status for each region
        region_status = []
        for region_idx in range(M):
            active_sensors = 0
            for sensor_idx in range(N):
                if coverage[region_idx][sensor_idx] and batteries[sensor_idx] > 0:
                    active_sensors += 1
            region_status.append(active_sensors >= K)
        
        # Calculate importance score
        total_importance = sum(imp for imp, status in zip(region_importances, region_status) if status)
        
        # Greedy approach: activate sensors that cover the most important regions
        sensor_scores = [0] * N
        for region_idx in range(M):
            if not region_status[region_idx]:  # Only consider regions not already covered
                for sensor_idx in range(N):
                    if coverage[region_idx][sensor_idx] and batteries[sensor_idx] > 0:
                        sensor_scores[sensor_idx] += region_importances[region_idx]
        
        # Decide actions
        actions = []
        for sensor_idx in range(N):
            if batteries[sensor_idx] == 0:
                actions.append(0)  # Must sleep if no battery
            elif sensor_scores[sensor_idx] > 0:
                actions.append(1)  # Sense if it can contribute to coverage
            else:
                actions.append(0)  # Sleep otherwise
        
        # Update batteries
        for sensor_idx in range(N):
            if actions[sensor_idx] == 1:
                batteries[sensor_idx] -= 1
        
        action_plan.append(actions)
    
    return action_plan