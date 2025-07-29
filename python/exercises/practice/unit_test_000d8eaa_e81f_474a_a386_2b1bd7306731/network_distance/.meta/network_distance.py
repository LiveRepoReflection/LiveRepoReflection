from collections import deque

def network_distance(start_user_id, k, query_user, query_limit):
    """
    Finds all users within k degrees of separation from start_user_id.
    
    Args:
        start_user_id: The ID of the starting user.
        k: The maximum degree of separation.
        query_user: A function that returns (following, followers) for a given user ID,
                   or None if the user doesn't exist.
        query_limit: Maximum number of calls allowed to query_user.
    
    Returns:
        A set of user IDs within k degrees of separation from start_user_id.
    """
    if k < 0:
        return set()
    
    # Initialize structures to track our progress
    result = set()
    visited = set()
    query_count = 0
    
    # Check if the starting user is valid
    start_data = query_user(start_user_id)
    query_count += 1
    
    if start_data is None:
        return set()
    
    # BFS queue with (user_id, degree) pairs
    queue = deque([(start_user_id, 0)])
    visited.add(start_user_id)
    result.add(start_user_id)
    
    # Cache user query results to avoid redundant queries
    query_cache = {start_user_id: start_data}
    
    while queue and query_count < query_limit:
        user_id, degree = queue.popleft()
        
        # If we've reached the maximum degree, don't explore further
        if degree >= k:
            continue
        
        # Get user data (from cache if available)
        if user_id in query_cache:
            following, followers = query_cache[user_id]
        else:
            user_data = query_user(user_id)
            query_count += 1
            
            if user_data is None:
                continue
                
            following, followers = user_data
            query_cache[user_id] = (following, followers)
        
        # Process all neighbors (both following and followers)
        neighbors = list(following) + list(followers)
        
        # Prioritize neighbors that are already in the cache
        sorted_neighbors = sorted(neighbors, key=lambda n: n not in query_cache)
        
        for neighbor in sorted_neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                result.add(neighbor)
                queue.append((neighbor, degree + 1))
                
                # If we've exhausted our query limit, return what we have so far
                if query_count >= query_limit:
                    return result
    
    return result