from collections import deque

def find_path(start_user_id, target_user_id):
    """
    Finds the shortest path between start_user_id and target_user_id in a decentralized social network.
    
    Uses a breadth-first search (BFS) approach while caching node lookups to minimize expensive get_node calls.
    
    Parameters:
        start_user_id (int): The starting user's ID.
        target_user_id (int): The target user's ID.
        
    Returns:
        list: List of user IDs representing the shortest path from start_user_id to target_user_id (inclusive).
              Returns None if either user does not exist or no path exists.
    """
    # If both ids are the same, the shortest path is the trivial path.
    if start_user_id == target_user_id:
        return [start_user_id]

    # Cache for storing already fetched nodes to reduce calls to get_node.
    node_cache = {}

    def fetch_node(user_id):
        """
        Retrieves the node for a given user_id and caches the result.
        """
        if user_id in node_cache:
            return node_cache[user_id]
        node = get_node(user_id)
        node_cache[user_id] = node
        return node

    # Check existence of start and target users.
    if fetch_node(start_user_id) is None or fetch_node(target_user_id) is None:
        return None

    # BFS initialization.
    queue = deque()
    visited = set()
    queue.append((start_user_id, [start_user_id]))
    visited.add(start_user_id)

    while queue:
        current_user, path = queue.popleft()
        current_node = fetch_node(current_user)
        if current_node is None:
            # This condition should normally not trigger as we have already validated user existence.
            continue
        # Retrieve friends from the current node.
        friends = current_node.get_friends(current_user)
        for friend in friends:
            if friend not in visited:
                visited.add(friend)
                new_path = path + [friend]
                if friend == target_user_id:
                    return new_path
                # Only add friend to the queue if the friend exists in the network.
                if fetch_node(friend) is not None:
                    queue.append((friend, new_path))
    # If no path is found.
    return None