import heapq
from collections import defaultdict
import math

def optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost):
    """
    Calculate the optimal evacuation time and capacity adjustment cost.
    
    Args:
        n: Number of intersections
        m: Number of streets
        edges: List of tuples (u, v, capacity, travel_time)
        population: List of population counts at each intersection
        safe_zone: Index of the safe zone
        increase_cost: Cost per 1% increase in capacity
        decrease_cost: Cost per 1% decrease in capacity
    
    Returns:
        Tuple (minimum_evacuation_time, capacity_adjustment_cost)
    """
    # Check if everyone is already at the safe zone
    if sum(population[:safe_zone] + population[safe_zone+1:]) == 0:
        return 0, 0
    
    # Create a graph representation
    graph = defaultdict(list)
    edge_details = {}  # To store capacity and travel time
    
    for u, v, capacity, travel_time in edges:
        graph[u].append(v)
        edge_details[(u, v)] = (capacity, travel_time)
    
    # Calculate distances from each node to the safe zone using Dijkstra's algorithm
    distances = find_distances_to_safe_zone(graph, edge_details, n, safe_zone)
    
    # If any node with population has infinite distance, they can't reach the safe zone
    unreachable_population = 0
    for i in range(n):
        if i != safe_zone and distances[i] == float('inf') and population[i] > 0:
            unreachable_population += population[i]
    
    # If all population is unreachable, return 0, 0
    if unreachable_population == sum(population) - population[safe_zone]:
        return 0, 0
    
    # Create a flow network for optimization
    # We'll use a simplified max-flow min-cost approach
    flow_network = create_flow_network(graph, edge_details, distances, n, safe_zone)
    
    # Optimize capacity adjustments to minimize evacuation time
    min_evacuation_time, capacity_adjustments = optimize_evacuation(
        flow_network, population, safe_zone, n, increase_cost, decrease_cost
    )
    
    # Calculate the cost of capacity adjustments
    adjustment_cost = calculate_adjustment_cost(
        capacity_adjustments, edge_details, increase_cost, decrease_cost
    )
    
    return min_evacuation_time, adjustment_cost

def find_distances_to_safe_zone(graph, edge_details, n, safe_zone):
    """
    Find the shortest path distances from each node to the safe zone.
    Uses backward Dijkstra's algorithm starting from the safe zone.
    """
    # Create a reversed graph
    rev_graph = defaultdict(list)
    for u in graph:
        for v in graph[u]:
            rev_graph[v].append(u)
    
    # Initialize distances
    distances = [float('inf')] * n
    distances[safe_zone] = 0
    
    # Priority queue for Dijkstra's algorithm
    pq = [(0, safe_zone)]
    
    while pq:
        dist, node = heapq.heappop(pq)
        
        if dist > distances[node]:
            continue
        
        for neighbor in rev_graph[node]:
            capacity, travel_time = edge_details[(neighbor, node)]
            new_dist = dist + travel_time
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    
    return distances

def create_flow_network(graph, edge_details, distances, n, safe_zone):
    """
    Create a network for flow optimization.
    Maps edges to their capacity, travel time, and path distance.
    """
    flow_network = {}
    
    for u in graph:
        for v in graph[u]:
            capacity, travel_time = edge_details[(u, v)]
            
            # We only care about edges that are on paths to the safe zone
            if distances[u] != float('inf') and distances[v] != float('inf'):
                # Store edge with its details
                flow_network[(u, v)] = {
                    'capacity': capacity,
                    'travel_time': travel_time,
                    'path_distance': distances[v] + travel_time
                }
    
    return flow_network

def optimize_evacuation(flow_network, population, safe_zone, n, increase_cost, decrease_cost):
    """
    Optimize capacity adjustments to minimize evacuation time.
    Uses a heuristic approach combining flow optimization and binary search.
    """
    # Calculate the total evacuating population
    total_population = sum(population) - population[safe_zone]
    
    # Filter out nodes that can't reach the safe zone
    reachable_nodes = [i for i in range(n) if i != safe_zone and find_path_to_safe_zone(i, safe_zone, flow_network, n)]
    reachable_population = sum(population[i] for i in reachable_nodes)
    
    if reachable_population == 0:
        return 0, {}
    
    # Binary search for the minimum evacuation time
    def is_evacuation_possible(target_time):
        # Create a copy of the flow network for this attempt
        network_copy = {edge: dict(details) for edge, details in flow_network.items()}
        
        # Adjust edge capacities to try to meet the target time
        adjusted_capacities = adjust_capacities_for_target_time(
            network_copy, population, safe_zone, target_time, n, reachable_nodes
        )
        
        # Check if the adjusted network can evacuate everyone within the target time
        return verify_evacuation_time(network_copy, population, safe_zone, target_time, n, reachable_nodes), adjusted_capacities
    
    # Calculate an upper bound for the evacuation time based on the limiting bottleneck
    max_possible_flow = sum(min(flow_network[(u, v)]['capacity'] * 1.5, 
                               population[u]) for u, v in flow_network if u != safe_zone)
    
    if max_possible_flow == 0:
        return float('inf'), {}
    
    # Estimate bounds for binary search
    # Lower bound: Best case where everyone takes the shortest path
    min_path_time = min(
        flow_network[(u, v)]['travel_time'] 
        for u, v in flow_network 
        if u in reachable_nodes
    ) if flow_network else 0
    
    lower_bound = min_path_time  # Best case - one unit of travel time
    
    # Upper bound: Worst case where bottleneck limits evacuation
    upper_bound = 10000  # A very large number as a safe upper bound
    
    best_time = upper_bound
    best_adjustments = {}
    
    # Binary search
    while lower_bound <= upper_bound:
        mid = (lower_bound + upper_bound) / 2
        possible, adjustments = is_evacuation_possible(mid)
        
        if possible:
            best_time = mid
            best_adjustments = adjustments
            upper_bound = mid - 0.1  # Try to find a better time
        else:
            lower_bound = mid + 0.1
    
    return best_time, best_adjustments

def find_path_to_safe_zone(start, safe_zone, flow_network, n):
    """
    Check if there's a path from start to safe_zone in the flow network.
    """
    visited = [False] * n
    
    def dfs(node):
        if node == safe_zone:
            return True
        
        visited[node] = True
        
        for edge in flow_network:
            u, v = edge
            if u == node and not visited[v]:
                if dfs(v):
                    return True
        
        return False
    
    return dfs(start)

def adjust_capacities_for_target_time(network, population, safe_zone, target_time, n, reachable_nodes):
    """
    Adjust edge capacities to try to meet the target evacuation time.
    Returns the capacity adjustments made.
    """
    # For each edge, calculate the desired capacity to meet target time
    adjustments = {}
    
    for edge, details in network.items():
        u, v = edge
        capacity = details['capacity']
        travel_time = details['travel_time']
        
        if u in reachable_nodes:
            # Calculate desired population flow rate
            desired_flow = population[u] / target_time
            
            # Adjust capacity, limited by +/- 50%
            max_capacity = capacity * 1.5
            min_capacity = capacity * 0.5
            
            # Aim for the desired flow rate, but within constraints
            new_capacity = min(max_capacity, max(min_capacity, desired_flow))
            
            # Record adjustment percentage
            adjustment_pct = (new_capacity - capacity) / capacity * 100
            adjustments[edge] = adjustment_pct
            
            # Update network with new capacity
            network[edge]['capacity'] = new_capacity
    
    return adjustments

def verify_evacuation_time(network, population, safe_zone, target_time, n, reachable_nodes):
    """
    Verify if all population can be evacuated within the target time.
    Uses a greedy flow allocation algorithm.
    """
    # Calculate max flow for each path
    remaining_population = population.copy()
    
    # Create a priority queue of paths based on travel time
    paths = []
    for u in reachable_nodes:
        # Find all edges from this node
        for edge, details in network.items():
            if edge[0] == u:
                paths.append((details['travel_time'], edge))
    
    # Sort paths by travel time
    paths.sort()
    
    # Assign population to paths greedily
    total_evacuation_time = 0
    
    for _, edge in paths:
        u, v = edge
        capacity = network[edge]['capacity']
        travel_time = network[edge]['travel_time']
        
        # Determine how many people can take this path
        flow = min(capacity, remaining_population[u])
        remaining_population[u] -= flow
        
        # Calculate evacuation time for this group
        if flow > 0:
            evac_time = travel_time + (flow / capacity)
            total_evacuation_time = max(total_evacuation_time, evac_time)
    
    # Check if anyone couldn't be evacuated
    for u in reachable_nodes:
        if remaining_population[u] > 0:
            return False
    
    # Check if evacuation time meets target
    return total_evacuation_time <= target_time

def calculate_adjustment_cost(adjustments, edge_details, increase_cost, decrease_cost):
    """
    Calculate the total cost of capacity adjustments.
    """
    total_cost = 0
    
    for edge, adjustment_pct in adjustments.items():
        if adjustment_pct > 0:
            # Cost for capacity increase
            total_cost += adjustment_pct * increase_cost
        else:
            # Cost for capacity decrease (adjustment_pct is negative)
            total_cost += -adjustment_pct * decrease_cost
    
    return total_cost