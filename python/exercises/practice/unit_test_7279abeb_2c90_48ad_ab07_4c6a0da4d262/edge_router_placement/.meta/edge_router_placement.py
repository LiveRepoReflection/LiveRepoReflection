import math
import itertools
from collections import defaultdict
from typing import List, Tuple, Dict, Set


def optimize_router_placement(
    user_locations: List[Tuple[float, float]],
    potential_router_locations: List[Tuple[float, float]],
    k: int,
    max_latency: float,
    router_capacity: int,
    propagation_delay_factor: float,
    router_cost: int
) -> List[int]:
    """
    Finds optimal edge router placement for a CDN network.
    
    Args:
        user_locations: List of (latitude, longitude) coordinates for users
        potential_router_locations: List of (latitude, longitude) coordinates for potential router locations
        k: Maximum number of routers to place
        max_latency: Maximum allowable latency between user and router (in ms)
        router_capacity: Maximum number of users a single router can serve
        propagation_delay_factor: Latency per unit of distance (ms/km)
        router_cost: Cost per router
        
    Returns:
        List of indices of selected router locations (from the potential_router_locations list)
    """
    if k == 0 or not user_locations or not potential_router_locations:
        return []
    
    # Precompute the distance and latency between each user and potential router
    latency_matrix = []
    for user in user_locations:
        user_latencies = []
        for router in potential_router_locations:
            distance = haversine_distance(user, router)
            latency = distance * propagation_delay_factor
            user_latencies.append(latency)
        latency_matrix.append(user_latencies)
    
    # Build a mapping of which users each router can cover within max_latency
    router_coverage: Dict[int, Set[int]] = defaultdict(set)
    for router_idx in range(len(potential_router_locations)):
        for user_idx in range(len(user_locations)):
            if latency_matrix[user_idx][router_idx] <= max_latency:
                router_coverage[router_idx].add(user_idx)
    
    # Approach 1: Greedy algorithm enhanced with capacity constraints
    # This is more efficient for larger datasets
    if len(potential_router_locations) > 20 or k > 10:
        return greedy_approach(
            user_locations, 
            potential_router_locations, 
            k, 
            max_latency, 
            router_capacity, 
            latency_matrix, 
            router_coverage
        )
    
    # Approach 2: For smaller instances, use more thorough search to find optimal solution
    return exhaustive_approach(
        user_locations, 
        potential_router_locations, 
        k, 
        max_latency, 
        router_capacity, 
        latency_matrix, 
        router_coverage
    )


def greedy_approach(
    user_locations, 
    potential_router_locations, 
    k, 
    max_latency, 
    router_capacity, 
    latency_matrix, 
    router_coverage
) -> List[int]:
    """
    Greedy algorithm to solve the edge router placement problem.
    
    The algorithm selects routers one by one, each time choosing the router that
    covers the most currently uncovered users, while respecting capacity constraints.
    """
    remaining_users = set(range(len(user_locations)))
    selected_routers = []
    user_assignments = {}  # Maps user_idx -> router_idx
    router_loads = defaultdict(int)  # Maps router_idx -> number of assigned users
    
    while len(selected_routers) < k and remaining_users:
        best_router = -1
        best_coverage = -1
        
        # For each potential router, compute how many uncovered users it can cover
        for router_idx in range(len(potential_router_locations)):
            if router_idx in selected_routers:
                continue
                
            # Count how many uncovered users this router can handle (up to capacity)
            covered_users = 0
            for user_idx in router_coverage[router_idx]:
                if user_idx in remaining_users:
                    covered_users += 1
                    if covered_users >= router_capacity:
                        break
            
            if covered_users > best_coverage:
                best_coverage = covered_users
                best_router = router_idx
        
        if best_coverage == 0:
            # No more users can be covered by any router
            break
        
        # Add the best router and update coverage
        selected_routers.append(best_router)
        
        # Assign users to this router (up to capacity)
        users_to_assign = []
        for user_idx in router_coverage[best_router]:
            if user_idx in remaining_users and router_loads[best_router] < router_capacity:
                users_to_assign.append(user_idx)
                if len(users_to_assign) >= router_capacity:
                    break
        
        # Sort by latency to prioritize closer users for this router
        users_to_assign.sort(key=lambda user_idx: latency_matrix[user_idx][best_router])
        
        # Assign users to this router
        for user_idx in users_to_assign:
            user_assignments[user_idx] = best_router
            router_loads[best_router] += 1
            remaining_users.remove(user_idx)
    
    # If we've exhausted all possible routers but still have uncovered users, the problem is infeasible
    if remaining_users:
        return []
    
    # Optimize: Remove routers that aren't serving any users
    final_routers = []
    for router_idx in selected_routers:
        if router_loads[router_idx] > 0:
            final_routers.append(router_idx)
    
    return final_routers


def exhaustive_approach(
    user_locations, 
    potential_router_locations, 
    k, 
    max_latency, 
    router_capacity, 
    latency_matrix, 
    router_coverage
) -> List[int]:
    """
    More exhaustive approach that tries different router combinations to find the optimal solution.
    """
    n_users = len(user_locations)
    n_routers = len(potential_router_locations)
    
    best_solution = []
    best_router_count = float('inf')
    best_total_latency = float('inf')
    
    # Try all combinations of routers, starting from smaller sets
    for r in range(1, min(k + 1, n_routers + 1)):
        for router_combo in itertools.combinations(range(n_routers), r):
            # Check if this combination can cover all users within capacity constraints
            user_assignments = {}  # Maps user_idx -> router_idx
            router_loads = defaultdict(int)  # Maps router_idx -> number of assigned users
            
            # For each user, find the closest router in this combo
            uncovered_users = []
            for user_idx in range(n_users):
                best_router = -1
                best_latency = float('inf')
                
                for router_idx in router_combo:
                    latency = latency_matrix[user_idx][router_idx]
                    if latency <= max_latency and latency < best_latency:
                        best_latency = latency
                        best_router = router_idx
                
                if best_router == -1:
                    # This user can't be covered by any router in this combo
                    uncovered_users.append(user_idx)
                else:
                    user_assignments[user_idx] = best_router
            
            if uncovered_users:
                # Some users can't be covered, so this combination is invalid
                continue
            
            # Sort users by latency to assign them optimally to routers
            sorted_users = sorted(user_assignments.items(), 
                                key=lambda x: latency_matrix[x[0]][x[1]])
            
            # Try to assign users to routers respecting capacity
            user_assignments = {}
            router_loads = defaultdict(int)
            uncovered_after_capacity = False
            
            for user_idx, router_idx in sorted_users:
                # Find the closest router with available capacity
                assigned = False
                best_latency = float('inf')
                best_router = -1
                
                for r_idx in router_combo:
                    latency = latency_matrix[user_idx][r_idx]
                    if (latency <= max_latency and 
                        router_loads[r_idx] < router_capacity and 
                        latency < best_latency):
                        best_latency = latency
                        best_router = r_idx
                
                if best_router != -1:
                    user_assignments[user_idx] = best_router
                    router_loads[best_router] += 1
                else:
                    # This user can't be assigned to any router due to capacity
                    uncovered_after_capacity = True
                    break
            
            if uncovered_after_capacity:
                # Capacity constraints violated
                continue
            
            # This is a valid solution, calculate total latency
            total_latency = sum(latency_matrix[user_idx][router_idx] 
                               for user_idx, router_idx in user_assignments.items())
            
            # Check if this solution is better than our current best
            active_routers = [r for r in router_combo if router_loads[r] > 0]
            if (len(active_routers) < best_router_count or
                (len(active_routers) == best_router_count and total_latency < best_total_latency)):
                best_router_count = len(active_routers)
                best_total_latency = total_latency
                best_solution = active_routers
    
    return best_solution


def haversine_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    """
    Calculate the great-circle distance between two points on earth.
    
    Args:
        loc1: (latitude, longitude) of first point in degrees
        loc2: (latitude, longitude) of second point in degrees
        
    Returns:
        Distance in kilometers
    """
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1 = math.radians(loc1[0])
    lon1 = math.radians(loc1[1])
    lat2 = math.radians(loc2[0])
    lon2 = math.radians(loc2[1])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance