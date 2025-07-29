import math
import heapq
from collections import defaultdict, deque

def find_optimal_path(N, nodes, R, S, D, C):
    """
    Find the optimal path from source S to destination D in a wireless sensor network.
    
    Args:
        N: Number of sensor nodes
        nodes: List of tuples (x, y, B) representing node coordinates and battery level
        R: Transmission range
        S: Source node index
        D: Destination node index
        C: Energy consumption constant per unit distance
    
    Returns:
        List of node indices representing the optimal path, or empty list if no path exists
    """
    if S == D:
        return [S]  # Source and destination are the same
    
    # Create adjacency list with energy costs
    graph = defaultdict(list)
    
    # Build the graph with valid connections
    for i in range(N):
        x1, y1, battery_i = nodes[i]
        
        for j in range(N):
            if i == j:
                continue
                
            x2, y2, _ = nodes[j]
            
            # Calculate Euclidean distance
            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            
            # Check if node j is within range of node i and i has enough battery
            if distance <= R:
                energy_consumption = C * distance
                
                if battery_i >= energy_consumption:
                    # Add edge (i -> j) with energy consumption
                    graph[i].append((j, energy_consumption))
    
    # No outgoing connections from source or no incoming connections to destination
    if S not in graph or not any(D in [j for j, _ in graph[i]] for i in graph):
        return []
    
    # Modified Dijkstra's algorithm to find minimum hop path
    # with minimum energy consumption as a tie-breaker
    distances = {node: float('infinity') for node in range(N)}
    hop_counts = {node: float('infinity') for node in range(N)}
    energy_consumption = {node: float('infinity') for node in range(N)}
    
    distances[S] = 0
    hop_counts[S] = 0
    energy_consumption[S] = 0
    
    # Priority queue: (hop_count, energy, node)
    pq = [(0, 0, S)]
    previous = {node: None for node in range(N)}
    
    while pq:
        hops, energy, current = heapq.heappop(pq)
        
        # If we've reached the destination, we can stop
        if current == D:
            break
            
        # If we've already found a better path to this node, skip
        if hops > hop_counts[current] or (hops == hop_counts[current] and energy > energy_consumption[current]):
            continue
        
        # Check all neighbors
        for neighbor, edge_energy in graph[current]:
            new_hops = hops + 1
            new_energy = energy + edge_energy
            
            # If we found a path with fewer hops or same hops but less energy
            if (new_hops < hop_counts[neighbor] or 
                (new_hops == hop_counts[neighbor] and new_energy < energy_consumption[neighbor])):
                hop_counts[neighbor] = new_hops
                energy_consumption[neighbor] = new_energy
                distances[neighbor] = distances[current] + edge_energy
                previous[neighbor] = current
                heapq.heappush(pq, (new_hops, new_energy, neighbor))
    
    # Reconstruct path
    if hop_counts[D] == float('infinity'):
        return []  # No path found
        
    path = []
    current = D
    while current is not None:
        path.append(current)
        current = previous[current]
    
    return path[::-1]  # Reverse the path to get it from source to destination