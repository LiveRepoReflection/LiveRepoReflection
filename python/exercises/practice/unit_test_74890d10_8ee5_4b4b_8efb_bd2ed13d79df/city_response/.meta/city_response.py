from collections import defaultdict
import heapq
from itertools import combinations
import math

def find_optimal_stations(N, M, K, P, roads):
    # Input validation
    if N <= 0 or K <= 0 or K > N or len(P) != N:
        raise ValueError("Invalid input parameters")
    if M != len(roads):
        raise ValueError("Number of roads doesn't match M")
    
    # Build adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v, t in roads:
        if not (1 <= u <= N and 1 <= v <= N):
            raise ValueError("Invalid road endpoints")
        graph[u].append((v, t))
        graph[v].append((u, t))

    def dijkstra(start_nodes):
        """
        Compute shortest paths from multiple source nodes using Dijkstra's algorithm
        Returns the minimum distance to each node from any of the start nodes
        """
        distances = [float('inf')] * (N + 1)
        pq = []
        
        # Initialize distances for start nodes
        for node in start_nodes:
            distances[node] = 0
            heapq.heappush(pq, (0, node))
            
        while pq:
            dist, current = heapq.heappop(pq)
            
            if dist > distances[current]:
                continue
                
            for neighbor, weight in graph[current]:
                new_dist = dist + weight
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
                    
        return distances[1:]  # Remove 0th index as nodes are 1-based

    def compute_max_weighted_response_time(stations):
        """
        Compute the maximum weighted response time for a given set of stations
        """
        distances = dijkstra(stations)
        return max(dist * pop for dist, pop in zip(distances, P))

    # Try all possible combinations of K stations
    min_max_response = float('inf')
    best_stations = None
    
    # Optimization: For very large graphs, we can use a greedy approach
    if N > 20 and K > 1:
        # Start with the highest population district
        stations = [max(range(1, N+1), key=lambda x: P[x-1])]
        
        # Add remaining stations greedily
        while len(stations) < K:
            best_next = None
            best_response = float('inf')
            
            for candidate in range(1, N+1):
                if candidate not in stations:
                    current_stations = stations + [candidate]
                    response = compute_max_weighted_response_time(current_stations)
                    if response < best_response:
                        best_response = response
                        best_next = candidate
            
            stations.append(best_next)
        return stations
    
    # For smaller graphs, use exhaustive search
    for stations in combinations(range(1, N+1), K):
        max_response = compute_max_weighted_response_time(stations)
        if max_response < min_max_response:
            min_max_response = max_response
            best_stations = stations

    return list(best_stations)