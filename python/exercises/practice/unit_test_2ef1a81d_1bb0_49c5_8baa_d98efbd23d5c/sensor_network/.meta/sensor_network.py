import heapq
from collections import defaultdict
from typing import Dict, List, Set, Tuple

def optimal_coverage(
    graph: Dict[int, List[Tuple[int, int]]],
    sources: List[int],
    targets: List[int],
    k: int,
    coverage_radius: int
) -> Set[int]:
    """
    Find the optimal subset of sources that maximizes the number of covered targets.
    
    Args:
        graph: Adjacency list representation of the graph.
               Keys are node IDs and values are lists of (neighbor_id, weight) tuples.
        sources: List of potential source node IDs.
        targets: List of target node IDs that need to be covered.
        k: Maximum number of sources to select.
        coverage_radius: Maximum distance for a source to cover a target.
        
    Returns:
        A set of selected source node IDs (subset of sources) that maximizes
        the number of covered targets. The size of the set is at most k.
    """
    if not graph or not sources or not targets or k <= 0:
        return set()
    
    # Convert targets to a set for faster lookup
    targets_set = set(targets)
    
    # Calculate shortest paths from each source to all nodes
    source_to_targets = {}
    for source in sources:
        # Get all nodes reachable from this source within coverage_radius
        reachable = dijkstra(graph, source, coverage_radius)
        
        # Find which targets are covered by this source
        covered_targets = targets_set.intersection(reachable)
        source_to_targets[source] = covered_targets
    
    # Use greedy algorithm to select the best k sources
    selected_sources = set()
    remaining_targets = set(targets)
    
    for _ in range(min(k, len(sources))):
        if not remaining_targets:
            break
            
        # Find the source that covers the most remaining targets
        best_source = None
        most_covered = 0
        
        for source in sources:
            if source in selected_sources:
                continue
                
            covered = len(remaining_targets.intersection(source_to_targets[source]))
            if covered > most_covered:
                most_covered = covered
                best_source = source
        
        # If no source covers any remaining targets, we're done
        if most_covered == 0:
            break
            
        # Add the best source and update remaining targets
        selected_sources.add(best_source)
        remaining_targets -= source_to_targets[best_source]
    
    return selected_sources

def dijkstra(
    graph: Dict[int, List[Tuple[int, int]]],
    start: int,
    max_distance: int
) -> Set[int]:
    """
    Run Dijkstra's algorithm to find all nodes reachable from start within max_distance.
    
    Args:
        graph: Adjacency list representation of the graph.
        start: Starting node ID.
        max_distance: Maximum distance to consider.
        
    Returns:
        A set of node IDs reachable from start within max_distance.
    """
    if start not in graph:
        return {start} if max_distance >= 0 else set()
        
    # Initialize distances
    distances = {start: 0}
    pq = [(0, start)]  # (distance, node)
    reachable = {start}
    
    while pq:
        dist, node = heapq.heappop(pq)
        
        # Skip if we've found a better path already
        if dist > distances.get(node, float('inf')):
            continue
            
        # Skip if we've reached the maximum distance
        if dist > max_distance:
            continue
        
        # Process neighbors
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            
            # Only process if it's within our max_distance
            if new_dist <= max_distance:
                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
                    reachable.add(neighbor)
    
    return reachable