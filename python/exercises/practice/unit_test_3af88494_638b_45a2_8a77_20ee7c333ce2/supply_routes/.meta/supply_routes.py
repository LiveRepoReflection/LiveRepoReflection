from collections import defaultdict
import heapq
from typing import Dict, List, Set, Tuple

def solve(
    graph: Dict[str, Dict[str, int]],
    disrupted_routes: List[Tuple[str, str]],
    origins: List[str],
    destinations: List[str]
) -> Dict[Tuple[str, str], int]:
    """
    Solves the supply chain routing problem with disrupted routes.
    
    Args:
        graph: Dictionary representing the weighted directed graph
        disrupted_routes: List of tuples representing disrupted routes
        origins: List of origin location names
        destinations: List of destination location names
    
    Returns:
        Dictionary mapping (origin, destination) pairs to minimum costs
    """
    
    # Convert disrupted routes to a set for O(1) lookup
    disrupted = set(disrupted_routes)
    
    def dijkstra(start: str) -> Dict[str, int]:
        """
        Implements Dijkstra's algorithm to find shortest paths from start node
        while avoiding disrupted routes.
        """
        distances = defaultdict(lambda: float('inf'))
        distances[start] = 0
        pq = [(0, start)]
        visited = set()

        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            # Skip if we've found a shorter path already
            if current_dist > distances[current]:
                continue
            
            # Check all neighbors
            for neighbor, weight in graph[current].items():
                # Skip disrupted routes
                if (current, neighbor) in disrupted:
                    continue
                    
                distance = current_dist + weight
                
                # Update distance if we found a shorter path
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))
        
        return distances
    
    # Calculate result for each origin-destination pair
    result = {}
    
    # Cache dijkstra results for each origin to avoid recomputation
    shortest_paths = {}
    
    for origin in origins:
        # Calculate shortest paths from this origin to all other nodes
        if origin not in shortest_paths:
            shortest_paths[origin] = dijkstra(origin)
            
        # Get distances to all destinations
        for dest in destinations:
            result[(origin, dest)] = shortest_paths[origin][dest]
    
    return result