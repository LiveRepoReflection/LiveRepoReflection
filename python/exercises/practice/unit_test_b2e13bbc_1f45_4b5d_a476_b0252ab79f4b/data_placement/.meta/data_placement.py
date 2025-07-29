import heapq
from collections import defaultdict, deque
from itertools import combinations


def find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands):
    """
    Determine the optimal placement of data centers to maximize covered demand.
    
    Args:
        graph: Dictionary representing the network graph. Keys are city names, values are
               dictionaries of neighboring cities and connection costs.
        num_data_centers: Maximum number of data centers to build.
        latency_radius: Maximum latency radius a data center can cover.
        city_demands: Dictionary of city names and their respective demands.
        
    Returns:
        A tuple of (list of optimal data center locations, total demand covered)
    """
    # Handle edge cases
    if not graph or num_data_centers <= 0 or not city_demands:
        return [], 0

    # Calculate all-pairs shortest paths
    distances = calculate_all_pairs_shortest_paths(graph)
    
    # Create a coverage map - for each city, which cities it can cover within the latency radius
    coverage_map = {}
    cities = list(graph.keys())
    
    for city in cities:
        coverage_map[city] = []
        for other_city in cities:
            if city in distances and other_city in distances[city] and distances[city][other_city] <= latency_radius:
                coverage_map[city].append(other_city)
    
    # Use a greedy approach to find the optimal data center locations
    if num_data_centers >= len(cities):
        # If we have enough data centers for all cities, place them in all cities
        return list(cities), sum(city_demands.values())
    
    remaining_cities = set(cities)
    selected_cities = []
    covered_cities = set()
    total_demand_covered = 0
    
    # Greedy algorithm: choose cities that maximize newly covered demand at each step
    for _ in range(min(num_data_centers, len(cities))):
        best_city = None
        best_new_demand = -1
        
        for city in remaining_cities:
            # Calculate how much new demand would be covered by placing a data center here
            new_covered = set(coverage_map[city]) - covered_cities
            new_demand = sum(city_demands.get(c, 0) for c in new_covered)
            
            if new_demand > best_new_demand:
                best_new_demand = new_demand
                best_city = city
        
        # If no additional demand can be covered, stop adding data centers
        if best_new_demand <= 0:
            break
            
        selected_cities.append(best_city)
        covered_cities.update(coverage_map[best_city])
        remaining_cities.remove(best_city)
        total_demand_covered += best_new_demand
    
    # Calculate the final covered demand - this accounts for cities that may be covered by multiple data centers
    total_covered_demand = 0
    all_covered_cities = set()
    for city in selected_cities:
        all_covered_cities.update(coverage_map[city])
    for city in all_covered_cities:
        if city in city_demands:
            total_covered_demand += city_demands[city]
    
    return selected_cities, total_covered_demand


def calculate_all_pairs_shortest_paths(graph):
    """
    Calculate the shortest path distances between all pairs of cities using Floyd-Warshall algorithm.
    
    Args:
        graph: Dictionary representing the network graph.
        
    Returns:
        Dictionary of dictionaries containing the shortest path distances.
    """
    cities = list(graph.keys())
    
    # Initialize distances with infinity
    distances = {city: {other_city: float('inf') for other_city in cities} for city in cities}
    
    # Set distance to self as 0
    for city in cities:
        distances[city][city] = 0
        
    # Set direct connections
    for city, neighbors in graph.items():
        for neighbor, cost in neighbors.items():
            if cost >= 0:  # Ensure non-negative latency
                distances[city][neighbor] = cost
    
    # Floyd-Warshall algorithm
    for k in cities:
        for i in cities:
            for j in cities:
                if distances[i][k] + distances[k][j] < distances[i][j]:
                    distances[i][j] = distances[i][k] + distances[k][j]
                    
    return distances