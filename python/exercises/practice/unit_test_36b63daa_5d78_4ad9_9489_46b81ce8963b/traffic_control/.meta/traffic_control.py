import math
from typing import List, Dict

def optimize_signal_timings(
    intersection_state: List[Dict],
    min_cycle_length: int,
    max_cycle_length: int,
    min_green_time: int,
) -> Dict[str, float]:
    """
    Optimizes traffic signal timings for a four-way intersection using a weighted approach
    that considers both queue lengths and arrival rates, while ensuring fairness.
    """
    
    # Calculate total demand for each approach
    approach_demands = {}
    for approach in intersection_state:
        total_demand = (
            approach["through_queue"] * approach["through_arrival_rate"] +
            approach["left_queue"] * approach["left_arrival_rate"] +
            approach["right_queue"] * approach["right_arrival_rate"]
        )
        approach_demands[approach["approach_name"]] = total_demand
    
    # Calculate total system demand
    total_system_demand = sum(approach_demands.values())
    
    # Handle edge case where there's no traffic
    if total_system_demand == 0:
        equal_time = max(min_cycle_length, min_green_time * 4) / 4
        return {approach["approach_name"]: equal_time for approach in intersection_state}
    
    # Calculate proportional demands
    proportional_demands = {
        name: demand / total_system_demand 
        for name, demand in approach_demands.items()
    }
    
    # Determine optimal cycle length based on demand
    base_cycle = min(
        max_cycle_length,
        max(
            min_cycle_length,
            math.ceil(total_system_demand * 10)  # Scaling factor
        )
    )
    
    # Calculate initial green times based on proportional demands
    green_times = {}
    remaining_time = base_cycle
    
    # First pass: assign minimum green times
    for name in approach_demands:
        green_times[name] = min_green_time
        remaining_time -= min_green_time
    
    # Second pass: distribute remaining time proportionally
    if remaining_time > 0:
        total_proportional = sum(
            proportional_demands[name] 
            for name in approach_demands
        )
        
        for name in approach_demands:
            additional_time = (
                proportional_demands[name] / total_proportional * remaining_time
            )
            green_times[name] += additional_time
    
    # Round to nearest second and ensure we don't exceed max_cycle_length
    total = 0
    for name in green_times:
        green_times[name] = round(green_times[name])
        total += green_times[name]
    
    # Adjust if we went slightly over max_cycle_length due to rounding
    if total > max_cycle_length:
        excess = total - max_cycle_length
        # Reduce from the approach with largest green time
        max_approach = max(green_times.items(), key=lambda x: x[1])[0]
        green_times[max_approach] -= excess
    
    # Ensure no approach gets less than min_green_time
    for name in green_times:
        green_times[name] = max(green_times[name], min_green_time)
    
    return green_times