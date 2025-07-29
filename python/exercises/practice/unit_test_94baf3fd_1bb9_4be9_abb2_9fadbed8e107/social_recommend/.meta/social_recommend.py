from collections import defaultdict, deque
import heapq

def recommend_users(user_id, k, get_neighbors):
    """
    Recommends k users to the target user based on interest score.
    
    Args:
        user_id: The ID of the target user.
        k: The number of recommendations to return.
        get_neighbors: A function that takes a user ID and returns (followers, followees).
        
    Returns:
        A list of k user IDs, sorted by interest score in descending order.
    """
    if k <= 0:
        return []
    
    # Get the target user's network information
    followers, followees = get_neighbors(user_id)
    
    # If user doesn't exist or has no connections, return empty list
    if not followers and not followees:
        return []
    
    # Initialize sets for tracking visited users and potential recommendations
    visited = {user_id} | followees  # Don't recommend self or users already followed
    potential_recommendations = set()
    
    # Cache to store user network information to avoid redundant API calls
    user_network_cache = {user_id: (followers, followees)}
    
    # First, explore the 2-hop neighborhood
    # Add followers' followees and followees' followers as potential recommendations
    for follower in followers:
        if follower not in user_network_cache:
            user_network_cache[follower] = get_neighbors(follower)
        follower_followers, follower_followees = user_network_cache[follower]
        potential_recommendations.update(follower_followees - visited)
    
    for followee in followees:
        if followee not in user_network_cache:
            user_network_cache[followee] = get_neighbors(followee)
        followee_followers, followee_followees = user_network_cache[followee]
        potential_recommendations.update(followee_followers - visited)
    
    # Add followers of followers and followees of followees for more depth
    followers_of_followers = set()
    for follower in followers:
        follower_followers, _ = user_network_cache[follower]
        for fof in follower_followers:
            if fof not in visited and fof not in potential_recommendations:
                followers_of_followers.add(fof)
    
    followees_of_followees = set()
    for followee in followees:
        _, followee_followees = user_network_cache[followee]
        for fof in followee_followees:
            if fof not in visited and fof not in potential_recommendations:
                followees_of_followees.add(fof)
    
    potential_recommendations.update(followers_of_followers)
    potential_recommendations.update(followees_of_followees)
    
    # If we still don't have enough potential recommendations, do a breadth-first search
    if len(potential_recommendations) < k:
        queue = deque(list(followers) + list(followees))
        while queue and len(potential_recommendations) < k * 2:  # Get more than needed for scoring
            current_user = queue.popleft()
            if current_user in visited:
                continue
            
            visited.add(current_user)
            if current_user != user_id and current_user not in followees:
                potential_recommendations.add(current_user)
            
            if current_user not in user_network_cache:
                user_network_cache[current_user] = get_neighbors(current_user)
            cur_followers, cur_followees = user_network_cache[current_user]
            
            for neighbor in list(cur_followers) + list(cur_followees):
                if neighbor not in visited and neighbor not in queue:
                    queue.append(neighbor)
    
    # Calculate interest scores for potential recommendations
    interest_scores = []
    for rec_user in potential_recommendations:
        if rec_user not in user_network_cache:
            user_network_cache[rec_user] = get_neighbors(rec_user)
        rec_followers, rec_followees = user_network_cache[rec_user]
        
        # Calculate common followees
        common_followees = len(followees.intersection(rec_followees))
        
        # Calculate follower overlap with influence weighting
        common_followers = followers.intersection(rec_followers)
        follower_overlap_score = 0
        for common_follower in common_followers:
            if common_follower not in user_network_cache:
                user_network_cache[common_follower] = get_neighbors(common_follower)
            _, cf_followees = user_network_cache[common_follower]
            influence = 1 / (1 + len(cf_followees))
            follower_overlap_score += influence
        
        # Calculate total interest score
        interest_score = common_followees + follower_overlap_score
        
        # Use negative score for max-heap (to get highest scores first)
        heapq.heappush(interest_scores, (-interest_score, rec_user))
    
    # Extract top k recommendations
    recommendations = []
    while interest_scores and len(recommendations) < k:
        _, rec_user = heapq.heappop(interest_scores)
        recommendations.append(rec_user)
    
    return recommendations


# For testing purposes, an example implementation of get_neighbors
def example_get_neighbors(user_id, network):
    """
    Example implementation of get_neighbors for testing.
    
    Args:
        user_id: The ID of the user.
        network: A dictionary mapping user_id to (followers, followees).
        
    Returns:
        A tuple (followers, followees) for the given user_id.
    """
    return network.get(user_id, (set(), set()))
