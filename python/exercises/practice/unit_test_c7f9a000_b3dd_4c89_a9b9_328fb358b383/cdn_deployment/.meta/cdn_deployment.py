from collections import defaultdict
import heapq
from itertools import combinations
import math

def find_optimal_cdn_locations(graph, num_servers, budget, server_cost):
    """
    Find optimal locations for CDN servers that minimize maximum latency while respecting constraints.
    
    Args:
        graph (dict): Dictionary representing the network topology
        num_servers (int): Maximum number of servers allowed
        budget (int): Maximum total budget for server deployment
        server_cost (dict): Dictionary mapping cities to their server deployment costs
    
    Returns:
        set: Set of city names where CDN servers should be deployed
    """
    if num_servers <= 0 or not graph:
        return set()

    def dijkstra(graph, start):
        """Calculate shortest paths from start node to all other nodes."""
        distances = {node: math.inf for node in graph}
        distances[start] = 0
        pq = [(0, start)]
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_distance > distances[current_node]:
                continue
                
            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))
        
        return distances

    def calculate_max_latency(server_locations):
        """Calculate the maximum latency for a given set of server locations."""
        if not server_locations:
            return math.inf
            
        # Calculate shortest paths from each server
        min_latencies = {node: math.inf for node in graph}
        
        for server in server_locations:
            distances = dijkstra(graph, server)
            for node in graph:
                min_latencies[node] = min(min_latencies[node], distances[node])
        
        return max(min_latencies.values())

    def calculate_total_latency(server_locations):
        """Calculate the sum of minimum latencies for all nodes."""
        if not server_locations:
            return math.inf
            
        total = 0
        min_latencies = {node: math.inf for node in graph}
        
        for server in server_locations:
            distances = dijkstra(graph, server)
            for node in graph:
                min_latencies[node] = min(min_latencies[node], distances[node])
        
        return sum(min_latencies.values())

    # Store best solution found
    best_solution = set()
    best_max_latency = math.inf
    best_total_latency = math.inf
    best_cost = math.inf

    # Try all possible combinations of server locations
    cities = list(graph.keys())
    for k in range(1, min(num_servers + 1, len(cities) + 1)):
        for combination in combinations(cities, k):
            # Check budget constraint
            total_cost = sum(server_cost[city] for city in combination)
            if total_cost > budget:
                continue

            current_solution = set(combination)
            current_max_latency = calculate_max_latency(current_solution)
            current_total_latency = calculate_total_latency(current_solution)

            # Update best solution if:
            # 1. Current max latency is lower, or
            # 2. Max latencies are equal but current total latency is lower, or
            # 3. Max and total latencies are equal but current cost is lower
            if (current_max_latency < best_max_latency or
                (current_max_latency == best_max_latency and 
                 current_total_latency < best_total_latency) or
                (current_max_latency == best_max_latency and 
                 current_total_latency == best_total_latency and 
                 total_cost < best_cost)):
                best_solution = current_solution
                best_max_latency = current_max_latency
                best_total_latency = current_total_latency
                best_cost = total_cost

    return best_solution