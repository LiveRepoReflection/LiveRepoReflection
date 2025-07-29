from collections import deque
from typing import Callable, List, Set

def find_k_hop_neighborhood(start_user_id: int, k: int, 
                          get_neighbors: Callable[[int], List[int]], 
                          max_api_calls: int) -> List[int]:
    """
    Finds the k-hop neighborhood of a given user in a distributed social network graph.
    
    Args:
        start_user_id: The ID of the starting user
        k: The maximum number of hops to traverse
        get_neighbors: Function that returns a list of neighbors for a given user ID
        max_api_calls: Maximum number of allowed API calls
    
    Returns:
        A sorted list of unique user IDs within k hops of the start user
        (excluding the start user)
    
    Raises:
        Exception: If the number of API calls exceeds max_api_calls
    """
    
    # Track API calls
    api_calls = 0
    
    def get_neighbors_with_tracking(user_id: int) -> List[int]:
        nonlocal api_calls
        api_calls += 1
        if api_calls > max_api_calls:
            raise Exception(f"Exceeded maximum API calls limit of {max_api_calls}")
        return get_neighbors(user_id)
    
    # Set to track visited nodes to avoid cycles and duplicate processing
    visited: Set[int] = {start_user_id}
    
    # Set to store the k-hop neighborhood (will convert to sorted list at the end)
    neighborhood: Set[int] = set()
    
    # Queue stores tuples of (user_id, hop_distance)
    queue = deque([(start_user_id, 0)])
    
    # Dictionary to cache neighbor results to avoid redundant API calls
    neighbor_cache = {}
    
    while queue:
        current_id, current_hop = queue.popleft()
        
        # If we've reached the maximum hop distance, skip processing neighbors
        if current_hop >= k:
            continue
        
        # Use cached neighbors if available, otherwise make API call
        if current_id not in neighbor_cache:
            neighbor_cache[current_id] = get_neighbors_with_tracking(current_id)
        
        for neighbor_id in neighbor_cache[current_id]:
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                neighborhood.add(neighbor_id)
                # Only add to queue if we haven't reached max hop distance
                if current_hop + 1 < k:
                    queue.append((neighbor_id, current_hop + 1))
    
    # Convert set to sorted list before returning
    return sorted(list(neighborhood))