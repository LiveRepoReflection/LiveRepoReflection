from collections import deque


def find_shortest_trust_path(start_user_id, target_user_id, get_trusted_users):
    """
    Find the shortest trust path between two users in a decentralized network.
    
    Args:
        start_user_id (str): The starting user ID
        target_user_id (str): The target user ID
        get_trusted_users (function): A function that returns a list of trusted users for a given user ID
    
    Returns:
        list: A list of user IDs representing the shortest path, or an empty list if no path exists
    """
    # Special case: start and target are the same
    if start_user_id == target_user_id:
        return [start_user_id]
    
    # Initialize queue for BFS
    queue = deque([(start_user_id, [start_user_id])])
    
    # Keep track of visited users to avoid cycles
    visited = {start_user_id}
    
    # Cache of user's trusted connections to minimize queries
    trusted_cache = {}
    
    while queue:
        current_user, path = queue.popleft()
        
        # Get trusted users (using cache if available)
        if current_user not in trusted_cache:
            trusted_cache[current_user] = get_trusted_users(current_user)
        
        trusted_users = trusted_cache[current_user]
        
        # Check each trusted user
        for trusted_user in trusted_users:
            # Found the target
            if trusted_user == target_user_id:
                return path + [trusted_user]
            
            # Add to queue if not visited
            if trusted_user not in visited:
                visited.add(trusted_user)
                queue.append((trusted_user, path + [trusted_user]))
    
    # No path found
    return []