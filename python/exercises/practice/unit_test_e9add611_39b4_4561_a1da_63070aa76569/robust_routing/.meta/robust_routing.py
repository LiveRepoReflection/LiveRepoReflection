import heapq
from math import log
from collections import defaultdict
from typing import List, Tuple, Set, Dict

def validate_input(N: int, edges: List[Tuple], source: int, destination: int, K: int, max_latency: int) -> None:
    """Validate input parameters."""
    if not (0 <= source < N and 0 <= destination < N):
        raise ValueError("Invalid source or destination node ID")
    if K <= 0:
        raise ValueError("K must be positive")
    if max_latency < 0:
        raise ValueError("Maximum latency must be non-negative")
    
    for u, v, latency, prob in edges:
        if not (0 <= u < N and 0 <= v < N):
            raise ValueError("Invalid node IDs in edges")
        if latency < 0:
            raise ValueError("Latency must be non-negative")
        if not 0 <= prob <= 1:
            raise ValueError("Probability must be between 0 and 1")

def build_graph(N: int, edges: List[Tuple]) -> Dict:
    """Build adjacency list representation of the graph."""
    graph = defaultdict(list)
    for u, v, latency, prob in edges:
        # Convert failure probability to success probability and then to log
        success_prob = 1 - prob
        log_prob = log(success_prob) if success_prob > 0 else float('-inf')
        graph[u].append((v, latency, log_prob))
        graph[v].append((u, latency, log_prob))
    return graph

def find_reliable_paths(N: int, edges: List[Tuple], source: int, destination: int, K: int, max_latency: int) -> List[List[int]]:
    """Find K most reliable paths from source to destination within max_latency constraint."""
    
    # Validate input
    validate_input(N, edges, source, destination, K, max_latency)
    
    # Handle trivial case where source and destination are the same
    if source == destination:
        return [[source]]
    
    # Build graph
    graph = build_graph(N, edges)
    
    # Priority queue entries: (negative_log_reliability, latency, current_node, path)
    pq = [(0, 0, source, [source])]
    # Keep track of visited states to avoid cycles
    visited = set()
    # Store result paths
    result_paths = []
    
    while pq and len(result_paths) < K:
        neg_log_reliability, latency, current, path = heapq.heappop(pq)
        
        # Convert negative log reliability back to actual reliability for comparison
        state = (current, tuple(path))
        if state in visited:
            continue
        visited.add(state)
        
        if current == destination:
            result_paths.append(path)
            continue
            
        for next_node, edge_latency, edge_log_prob in graph[current]:
            new_latency = latency + edge_latency
            if new_latency > max_latency:
                continue
                
            if next_node not in path:  # Avoid cycles
                new_neg_log_reliability = neg_log_reliability - edge_log_prob
                new_path = path + [next_node]
                heapq.heappush(pq, (new_neg_log_reliability, new_latency, next_node, new_path))
    
    return result_paths

def _calculate_path_reliability(path: List[int], edges: List[Tuple]) -> float:
    """Helper function to calculate the reliability of a path (for testing)."""
    edge_dict = {(u, v): 1-p for u, v, _, p in edges}
    edge_dict.update({(v, u): 1-p for u, v, _, p in edges})  # Add reverse edges
    
    reliability = 1.0
    for i in range(len(path)-1):
        reliability *= edge_dict.get((path[i], path[i+1]), 0)
    return reliability