from collections import defaultdict
import math


def min_total_latency(N, dependencies, D, G):
    """
    Calculate the minimum total latency for inter-service communication.
    
    Args:
        N (int): Number of microservices
        dependencies (list): List of tuples (u, v, w) representing dependencies
        D (int): Direct routing latency
        G (int): Group routing overhead
    
    Returns:
        int: Minimum total latency achievable
    """
    # If there are no dependencies, return 0
    if not dependencies:
        return 0
    
    # Create a dictionary to store messages for each destination service
    destination_messages = defaultdict(list)
    
    # Organize dependencies by destination service
    for src, dst, msgs in dependencies:
        destination_messages[dst].append((src, msgs))
    
    total_latency = 0
    
    # Calculate optimal routing strategy for each destination service
    for dest, sources in destination_messages.items():
        # Calculate latency for direct routing
        direct_latency = sum(msgs * D for _, msgs in sources)
        
        # Calculate latency for group routing
        total_msgs = sum(msgs for _, msgs in sources)
        # Only use group routing if there's more than one source
        if len(sources) > 1:
            # Calculate the per-message latency with grouping
            per_msg_latency = D + G / total_msgs
            group_latency = total_msgs * per_msg_latency
            # Round up to the nearest integer
            group_latency = math.ceil(group_latency)
        else:
            # If there's only one source, group routing is the same as direct
            group_latency = direct_latency
        
        # Choose the routing strategy with minimum latency
        total_latency += min(direct_latency, group_latency)
    
    return total_latency