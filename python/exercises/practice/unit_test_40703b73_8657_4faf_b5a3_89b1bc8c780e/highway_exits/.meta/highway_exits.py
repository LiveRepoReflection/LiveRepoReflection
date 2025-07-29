import numpy as np
from scipy.optimize import minimize
import math

def find_optimal_exits(L, N, residential_zones, v1, v2):
    """
    Find the optimal positions for highway exits to minimize total travel time.
    
    Args:
        L (int): Length of the highway
        N (int): Number of exits to place
        residential_zones (list): List of tuples (x_i, y_i, p_i) representing zones
        v1 (int): Off-highway travel speed
        v2 (int): On-highway travel speed
        
    Returns:
        list: Sorted positions of the N exits
    """
    if not residential_zones:
        # If there are no residential zones, place exits evenly along the highway
        return [i * L / (N - 1) if N > 1 else L/2 for i in range(N)]
    
    # Define the objective function to minimize total travel time
    def total_travel_time(exit_positions):
        exits = exit_positions.reshape(N)
        total_time = 0
        
        for x, y, pop in residential_zones:
            # Calculate travel time from zone to each exit
            # Off-highway travel time is constant (y/v1)
            off_highway_time = y / v1
            
            # Calculate on-highway travel time to each exit
            on_highway_times = np.abs(exits - x) / v2
            
            # Find the minimum total travel time to any exit
            min_time = off_highway_time + np.min(on_highway_times)
            
            # Add this zone's contribution to the total
            total_time += pop * min_time
            
        return total_time
    
    # Initial guess: place exits evenly along the highway
    initial_guess = np.linspace(0, L, N)
    
    # Constraints: all exits must be within highway length
    bounds = [(0, L) for _ in range(N)]
    
    # Run the optimization
    result = minimize(
        total_travel_time,
        initial_guess,
        bounds=bounds,
        method='L-BFGS-B'
    )
    
    # Get the optimized exit positions and sort them
    exit_positions = sorted(result.x.tolist())
    
    # Round to 6 decimal places as required
    exit_positions = [round(pos, 6) for pos in exit_positions]
    
    return exit_positions