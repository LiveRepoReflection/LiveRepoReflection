from collections import deque
from typing import Set, Callable, List

def compute_k_hop_neighborhood(
    user_id: int,
    k: int,
    shard_locator: Callable[[int], int],
    get_connections: Callable[[int, int], List[int]]
) -> Set[int]:
    """
    Compute the k-hop neighborhood of a given user in a decentralized social network.
    
    Args:
        user_id: The ID of the starting user
        k: Number of hops to explore (0 <= k <= 10)
        shard_locator: Function that returns the shard index for a given user_id
        get_connections: Function that returns connections for a user on a given shard
    
    Returns:
        Set of user IDs representing the k-hop neighborhood
    
    Raises:
        ValueError: If k is negative or greater than 10
    """
    # Validate k
    if not 0 <= k <= 10:
        raise ValueError("k must be between 0 and 10 inclusive")

    # Handle k=0 case
    if k == 0:
        return {user_id}

    # Initialize data structures
    visited = {user_id}  # Track all visited nodes
    current_level = {user_id}  # Nodes at current level
    result = {user_id}  # Final result set

    # Cache to store shard lookups to minimize redundant calls
    shard_cache = {}

    # Process each level up to k hops
    for hop in range(k):
        next_level = set()
        
        # Process all nodes in the current level
        for current_user in current_level:
            # Get shard index, using cache if available
            if current_user not in shard_cache:
                shard_cache[current_user] = shard_locator(current_user)
            shard_index = shard_cache[current_user]
            
            # Get connections for current user
            connections = get_connections(shard_index, current_user)
            
            # Process each connection
            for neighbor in connections:
                if neighbor not in visited:
                    next_level.add(neighbor)
                    visited.add(neighbor)
                    result.add(neighbor)

        # If no new nodes were found, we can stop early
        if not next_level:
            break

        current_level = next_level

    return result

def compute_k_hop_neighborhood_bfs(
    user_id: int,
    k: int,
    shard_locator: Callable[[int], int],
    get_connections: Callable[[int, int], List[int]]
) -> Set[int]:
    """
    Alternative implementation using BFS with a queue.
    This implementation might be more memory efficient for sparse graphs.
    """
    if not 0 <= k <= 10:
        raise ValueError("k must be between 0 and 10 inclusive")

    if k == 0:
        return {user_id}

    visited = {user_id}
    result = {user_id}
    queue = deque([(user_id, 0)])  # (user_id, hop_count)
    shard_cache = {}

    while queue:
        current_user, current_hop = queue.popleft()
        
        if current_hop >= k:
            break

        if current_user not in shard_cache:
            shard_cache[current_user] = shard_locator(current_user)
        shard_index = shard_cache[current_user]
        
        for neighbor in get_connections(shard_index, current_user):
            if neighbor not in visited:
                visited.add(neighbor)
                result.add(neighbor)
                queue.append((neighbor, current_hop + 1))

    return result