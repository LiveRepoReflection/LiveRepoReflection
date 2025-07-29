import numpy as np
from typing import List

def optimize_routing(N: int, servers: List[int], latency: List[List[int]], 
                    traffic: List[List[int]]) -> np.ndarray:
    """
    Optimizes the routing strategy for inter-datacenter communication.
    
    Args:
        N: Number of datacenters
        servers: List of server counts for each datacenter
        latency: Matrix of latencies between datacenters
        traffic: Matrix of traffic between datacenters
    
    Returns:
        3D numpy array representing the routing strategy
    """
    # Input validation
    if N <= 0:
        raise ValueError("Number of datacenters must be positive")
    if len(servers) != N:
        raise ValueError("Servers list length must match number of datacenters")
    if len(latency) != N or any(len(row) != N for row in latency):
        raise ValueError("Latency matrix dimensions must be NxN")
    if len(traffic) != N or any(len(row) != N for row in traffic):
        raise ValueError("Traffic matrix dimensions must be NxN")
    if any(l < 0 for row in latency for l in row):
        raise ValueError("Latency values must be non-negative")
    if any(t < 0 for row in traffic for t in row):
        raise ValueError("Traffic values must be non-negative")

    # Convert inputs to numpy arrays for easier manipulation
    latency_array = np.array(latency)
    traffic_array = np.array(traffic)
    
    # Initialize routing matrix
    routing = np.zeros((N, N, N))
    
    # Floyd-Warshall algorithm to find all-pairs shortest paths
    dist = latency_array.copy()
    next_hop = np.array([[j if i != j else -1 for j in range(N)] for i in range(N)])
    
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_hop[i][j] = next_hop[i][k]

    # For each source-destination pair, find if routing through intermediate
    # datacenter(s) would be beneficial
    for i in range(N):
        for j in range(N):
            if i == j or traffic_array[i][j] == 0:
                continue
                
            # Find potential intermediate datacenters
            for k in range(N):
                if k == i or k == j:
                    continue
                    
                # Calculate cost of direct route vs. route through k
                direct_cost = latency_array[i][j]
                indirect_cost = latency_array[i][k] + latency_array[k][j]
                
                # If routing through k is cheaper, route all traffic through k
                if indirect_cost < direct_cost:
                    # Consider datacenter capacity constraints
                    max_throughput = min(
                        servers[k] * 10,  # Assume each server can handle 10 GB
                        traffic_array[i][j] - np.sum(routing[i][j])
                    )
                    
                    if max_throughput > 0:
                        routing[i][j][k] = max_throughput

    # Optimize routing using linear programming for remaining traffic
    remaining_traffic = traffic_array.copy()
    for i in range(N):
        for j in range(N):
            remaining_traffic[i][j] -= np.sum(routing[i][j])
    
    # Use greedy approach for remaining traffic
    for i in range(N):
        for j in range(N):
            if remaining_traffic[i][j] > 0:
                best_route = None
                best_cost = float('inf')
                
                # Try all possible intermediate datacenters
                for k in range(N):
                    if k == i or k == j:
                        continue
                        
                    route_cost = latency_array[i][k] + latency_array[k][j]
                    if route_cost < best_cost:
                        best_cost = route_cost
                        best_route = k
                
                # If we found a better route, use it
                if best_route is not None and best_cost < latency_array[i][j]:
                    max_throughput = min(
                        servers[best_route] * 10,
                        remaining_traffic[i][j]
                    )
                    routing[i][j][best_route] = max_throughput
                    remaining_traffic[i][j] -= max_throughput

    return routing

def calculate_total_cost(routing: np.ndarray, latency: List[List[int]], 
                        traffic: List[List[int]]) -> float:
    """
    Calculates the total communication cost for a given routing strategy.
    """
    N = len(latency)
    total_cost = 0.0
    
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
                
            # Cost of direct routing
            direct_traffic = traffic[i][j] - np.sum(routing[i][j])
            total_cost += direct_traffic * latency[i][j]
            
            # Cost of indirect routing
            for k in range(N):
                if k != i and k != j:
                    total_cost += routing[i][j][k] * (latency[i][k] + latency[k][j])
    
    return total_cost