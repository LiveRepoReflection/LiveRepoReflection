import heapq
from math import log

def find_critical_paths(graph, traffic, k):
    """
    Finds the K most critical communication paths in a service architecture.
    
    Args:
        graph (dict): A directed graph represented as an adjacency list.
            Keys are service IDs and values are lists of tuples (neighbor_id, latency).
        traffic (dict): A dictionary with keys as tuples (source_id, destination_id) 
            and values as the number of requests per second.
        k (int): The number of most critical paths to return.
    
    Returns:
        list: A list of the K most critical communication paths, sorted by criticality score.
            Each path is a tuple (source_id, destination_id, criticality_score).
    """
    # Handle edge cases
    if not graph or not traffic or k <= 0:
        return []
    
    critical_paths = []
    
    # Process each edge in the graph
    for source_id, edges in graph.items():
        for dest_id, latency in edges:
            # Get traffic volume or default to 0 if not provided
            volume = traffic.get((source_id, dest_id), 0)
            
            # Calculate criticality score
            # Using a scoring function that emphasizes both latency and traffic
            # log(x+1) prevents issues with log(0) and smooths the effect of very high values
            criticality_score = calculate_criticality_score(latency, volume)
            
            # We use a min-heap but want to find max criticality, so we negate the score
            heapq.heappush(critical_paths, (-criticality_score, -latency, -volume, source_id, dest_id))
    
    # Collect the K most critical paths
    result = []
    path_count = min(k, len(critical_paths))
    
    for _ in range(path_count):
        if not critical_paths:
            break
        
        neg_score, neg_latency, neg_volume, source, dest = heapq.heappop(critical_paths)
        # Convert back to positive values
        result.append((source, dest, -neg_score))
    
    return result

def calculate_criticality_score(latency, volume):
    """
    Calculates a criticality score for a communication path based on latency and traffic volume.
    
    The function uses a non-linear combination to emphasize high values in either factor,
    making paths with extreme values in either dimension more critical.
    
    Args:
        latency (float): The communication latency in milliseconds.
        volume (float): The traffic volume in requests per second.
    
    Returns:
        float: The calculated criticality score.
    """
    # Ensure we don't have negative or zero values for log calculation
    safe_latency = max(1, latency)
    safe_volume = max(1, volume)
    
    # Use a logarithmic scale to prevent extremely high traffic or latency from dominating completely
    # but still give them significant weight
    log_latency = log(safe_latency + 1)
    log_volume = log(safe_volume + 1)
    
    # Basic score is the product of latency and traffic, which penalizes paths that are bad in both dimensions
    base_score = safe_latency * safe_volume
    
    # Add logarithmic components to smooth the effect and boost the score for paths with extreme values
    # in either dimension
    enhanced_score = base_score + (safe_latency * log_volume) + (safe_volume * log_latency)
    
    # Additional penalty for paths that exceed certain thresholds in both dimensions
    if safe_latency > 50 and safe_volume > 500:
        enhanced_score *= 1.5
    
    return enhanced_score