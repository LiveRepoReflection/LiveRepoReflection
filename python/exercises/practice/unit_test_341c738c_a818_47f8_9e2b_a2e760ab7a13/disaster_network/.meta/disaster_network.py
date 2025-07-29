import math
from collections import defaultdict
import heapq
from itertools import product

def design_response_network(cities, depots, cost_per_unit):
    """
    Designs an optimal disaster response network.
    
    Args:
        cities: List of tuples (x, y, population, demand)
        depots: List of tuples (x, y, capacity)
        cost_per_unit: Cost per unit distance for establishing a route
        
    Returns:
        Dictionary mapping city indices to dictionaries mapping depot indices to resource amounts
    """
    n_cities = len(cities)
    n_depots = len(depots)
    
    # Precompute distances between cities and depots
    distances = []
    for city_idx, city in enumerate(cities):
        city_distances = []
        for depot_idx, depot in enumerate(depots):
            distance = compute_distance(city, depot)
            city_distances.append((depot_idx, distance))
        distances.append(sorted(city_distances, key=lambda x: x[1]))
    
    # Step 1: Start with a greedy solution based on minimum distance
    network = {city_idx: {} for city_idx in range(n_cities)}
    remaining_demands = [city[3] for city in cities]
    remaining_capacities = [depot[2] for depot in depots]
    
    # First, allocate based on closest depot to satisfy basic connectivity
    for city_idx in range(n_cities):
        for depot_idx, distance in distances[city_idx]:
            if remaining_demands[city_idx] == 0:
                break
                
            if remaining_capacities[depot_idx] > 0:
                # Allocate as much as possible from this depot
                allocation = min(remaining_demands[city_idx], remaining_capacities[depot_idx])
                
                if allocation > 0:
                    if depot_idx not in network[city_idx]:
                        network[city_idx][depot_idx] = 0
                    network[city_idx][depot_idx] += allocation
                    
                    remaining_demands[city_idx] -= allocation
                    remaining_capacities[depot_idx] -= allocation
    
    # Step 2: Optimize to minimize cost while maintaining the delay constraint
    network = optimize_network(network, cities, depots, cost_per_unit, distances)
    
    # Step 3: Further optimize to minimize maximum delay
    network = minimize_max_delay(network, cities, depots, distances)
    
    return network

def compute_distance(city, depot):
    """Compute Euclidean distance between a city and a depot."""
    return math.sqrt((city[0] - depot[0])**2 + (city[1] - depot[1])**2)

def compute_network_cost(network, cities, depots, cost_per_unit):
    """Compute the total cost of the network."""
    total_cost = 0
    for city_idx, depot_allocations in network.items():
        city_x, city_y = cities[city_idx][0], cities[city_idx][1]
        for depot_idx, amount in depot_allocations.items():
            depot_x, depot_y = depots[depot_idx][0], depots[depot_idx][1]
            distance = compute_distance((city_x, city_y, 0, 0), (depot_x, depot_y, 0))
            total_cost += distance * amount * cost_per_unit
    return total_cost

def compute_max_delay(network, cities, depots):
    """Compute the maximum delay in the network."""
    max_delay = 0
    for city_idx, depot_allocations in network.items():
        if not depot_allocations:  # Skip if no allocations
            continue
        city_x, city_y = cities[city_idx][0], cities[city_idx][1]
        min_distance = float('inf')
        for depot_idx, amount in depot_allocations.items():
            if amount > 0:
                depot_x, depot_y = depots[depot_idx][0], depots[depot_idx][1]
                distance = compute_distance((city_x, city_y, 0, 0), (depot_x, depot_y, 0))
                min_distance = min(min_distance, distance)
        max_delay = max(max_delay, min_distance)
    return max_delay

def optimize_network(network, cities, depots, cost_per_unit, precomputed_distances):
    """Optimize the network to minimize cost while satisfying constraints."""
    n_iterations = 100  # Number of optimization iterations
    
    for _ in range(n_iterations):
        improved = False
        
        # Try to redistribute resources to reduce cost
        for city_idx, depot_allocations in network.items():
            if len(depot_allocations) <= 1:
                continue  # Only one depot, nothing to optimize
                
            city_demand = cities[city_idx][3]
            current_suppliers = list(depot_allocations.items())
            
            # Sort by distance (descending) to prioritize replacing farther depots
            current_suppliers.sort(key=lambda x: next(d for d_idx, d in precomputed_distances[city_idx] if d_idx == x[0]), reverse=True)
            
            for depot_idx, amount in current_suppliers:
                if amount == 0:
                    continue
                    
                # Try to replace some or all of this allocation with a closer depot
                for potential_depot_idx, _ in precomputed_distances[city_idx]:
                    if potential_depot_idx == depot_idx:
                        continue  # Same depot
                        
                    # Check depot capacity
                    curr_usage = sum(network.get(c_idx, {}).get(potential_depot_idx, 0) for c_idx in range(len(cities)))
                    available_capacity = depots[potential_depot_idx][2] - curr_usage
                    
                    if available_capacity <= 0:
                        continue
                        
                    transfer_amount = min(amount, available_capacity)
                    
                    # Calculate potential cost savings
                    old_distance = next(d for d_idx, d in precomputed_distances[city_idx] if d_idx == depot_idx)
                    new_distance = next(d for d_idx, d in precomputed_distances[city_idx] if d_idx == potential_depot_idx)
                    
                    cost_saving = (old_distance - new_distance) * transfer_amount * cost_per_unit
                    
                    if cost_saving > 0:
                        # Apply the transfer
                        network[city_idx][depot_idx] -= transfer_amount
                        if network[city_idx][depot_idx] == 0:
                            del network[city_idx][depot_idx]
                            
                        if potential_depot_idx not in network[city_idx]:
                            network[city_idx][potential_depot_idx] = 0
                        network[city_idx][potential_depot_idx] += transfer_amount
                        
                        improved = True
                        break  # Move to next supplier
                        
                if improved:
                    break  # Found an improvement, start over
                    
        if not improved:
            break  # No improvements found, we're done
            
    return network

def minimize_max_delay(network, cities, depots, precomputed_distances):
    """Further optimize the network to minimize the maximum delay."""
    # Calculate current max delay
    current_max_delay = compute_max_delay(network, cities, depots)
    
    # Identify the city with the maximum delay
    max_delay_city = -1
    max_delay_distance = 0
    
    for city_idx, depot_allocations in network.items():
        city_x, city_y = cities[city_idx][0], cities[city_idx][1]
        min_distance = float('inf')
        
        for depot_idx, amount in depot_allocations.items():
            if amount > 0:
                depot_x, depot_y = depots[depot_idx][0], depots[depot_idx][1]
                distance = compute_distance((city_x, city_y, 0, 0), (depot_x, depot_y, 0))
                min_distance = min(min_distance, distance)
                
        if min_distance > max_delay_distance:
            max_delay_distance = min_distance
            max_delay_city = city_idx
    
    if max_delay_city == -1:
        return network  # No cities or no valid solution
    
    # Try to improve the delay for the city with the maximum delay
    city_idx = max_delay_city
    city_demand = cities[city_idx][3]
    
    # Find the closest depot not currently serving this city
    closest_unused_depots = []
    
    for depot_idx, distance in precomputed_distances[city_idx]:
        if depot_idx not in network[city_idx] or network[city_idx].get(depot_idx, 0) == 0:
            # Check if this depot has any capacity left
            curr_usage = sum(network.get(c_idx, {}).get(depot_idx, 0) for c_idx in range(len(cities)))
            available_capacity = depots[depot_idx][2] - curr_usage
            
            if available_capacity > 0:
                closest_unused_depots.append((depot_idx, distance, available_capacity))
    
    # Try to allocate at least some resources from a closer depot
    if closest_unused_depots:
        closest_depot_idx, closest_distance, available_capacity = closest_unused_depots[0]
        
        if closest_distance < max_delay_distance:
            # Determine how much to transfer
            transfer_amount = min(1, available_capacity)  # Start with minimal amount
            
            # Find a depot to reduce allocation from
            current_depots = list(network[city_idx].items())
            if current_depots:
                # Take from the farthest depot first
                current_depots.sort(key=lambda x: next(d for d_idx, d in precomputed_distances[city_idx] if d_idx == x[0]), reverse=True)
                far_depot_idx, far_amount = current_depots[0]
                
                transfer_amount = min(transfer_amount, far_amount)
                
                if transfer_amount > 0:
                    # Update the network
                    network[city_idx][far_depot_idx] -= transfer_amount
                    if network[city_idx][far_depot_idx] == 0:
                        del network[city_idx][far_depot_idx]
                    
                    if closest_depot_idx not in network[city_idx]:
                        network[city_idx][closest_depot_idx] = 0
                    network[city_idx][closest_depot_idx] += transfer_amount
    
    return network

def is_valid_solution(network, cities, depots):
    """Verify that the solution satisfies all constraints."""
    n_cities = len(cities)
    n_depots = len(depots)
    
    # Check that all cities have their demands met
    for city_idx, city in enumerate(cities):
        city_demand = city[3]
        city_supply = sum(network.get(city_idx, {}).values())
        if city_supply < city_demand:
            return False
    
    # Check that no depot exceeds its capacity
    depot_usage = [0] * n_depots
    for city_idx, depot_allocations in network.items():
        for depot_idx, amount in depot_allocations.items():
            depot_usage[depot_idx] += amount
    
    for depot_idx, depot in enumerate(depots):
        if depot_usage[depot_idx] > depot[2]:
            return False
    
    # Check that all cities are connected to at least one depot
    for city_idx in range(n_cities):
        if not network.get(city_idx, {}):
            return False
    
    return True