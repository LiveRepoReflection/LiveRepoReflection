from collections import defaultdict
import heapq

def find_top_influencers(edges, user_credibility, damping_factor, tolerance, k):
    """
    Find the top k influencers in a social network using a weighted PageRank-like algorithm.
    
    Args:
        edges: List of tuples (A, B, topic, interaction_strength) representing edges in the social network.
        user_credibility: Dictionary mapping user IDs to their credibility scores.
        damping_factor: Float between 0 and 1 representing the damping factor.
        tolerance: Float representing the convergence tolerance.
        k: Integer representing the number of top influencers to return.
        
    Returns:
        List of user IDs representing the top k influencers.
    """
    if not user_credibility:
        return []

    # Extract all unique users and topics
    users = set(user_credibility.keys())
    for edge in edges:
        users.add(edge[0])
        users.add(edge[1])
    
    # Create a dictionary to map users to their indices
    user_to_idx = {user: idx for idx, user in enumerate(users)}
    idx_to_user = {idx: user for user, idx in user_to_idx.items()}
    
    # Extract all unique topics
    topics = set()
    for _, _, topic, _ in edges:
        topics.add(topic)
    
    # If there are no topics, create a default one
    if not topics:
        topics = {"default"}
    
    # Create a dictionary to map topics to their indices
    topic_to_idx = {topic: idx for idx, topic in enumerate(topics)}
    
    num_users = len(users)
    num_topics = len(topics)
    
    # Initialize influence scores for each user and topic
    influence = {}
    for user in users:
        influence[user] = {}
        for topic in topics:
            influence[user][topic] = 1.0 / num_users

    # Create an adjacency list to represent the network
    # For each user, store the list of users who follow them
    followers = defaultdict(list)
    
    # Store interaction strengths by user pairs and topics
    interaction_strengths = defaultdict(lambda: defaultdict(dict))
    
    for edge in edges:
        follower, followee, topic, strength = edge
        followers[followee].append(follower)
        interaction_strengths[follower][followee][topic] = strength
    
    # Initialize total_interaction_strengths for each follower-followee pair
    total_interaction_strengths = defaultdict(lambda: defaultdict(float))
    for follower in interaction_strengths:
        for followee in interaction_strengths[follower]:
            total = sum(interaction_strengths[follower][followee].values())
            total_interaction_strengths[follower][followee] = min(1.0, total)  # Cap at 1.0
    
    # Initialize previous influence scores
    prev_influence = {user: {topic: 0.0 for topic in topics} for user in users}
    
    # Main PageRank iteration loop
    iteration = 0
    max_iterations = 100  # Prevent infinite loops
    
    while iteration < max_iterations:
        iteration += 1
        
        # Store the current influence scores
        for user in users:
            for topic in topics:
                prev_influence[user][topic] = influence[user][topic]
        
        # Calculate new influence scores
        new_influence = {user: {topic: 0.0 for topic in topics} for user in users}
        
        for user in users:
            # First part of influence: credibility score
            user_credibility_value = user_credibility.get(user, 0.0)
            credibility_influence = (1 - damping_factor) * user_credibility_value / num_topics
            
            for topic in topics:
                new_influence[user][topic] = credibility_influence
        
        # Calculate topic weights for each user
        topic_weights = {}
        for user in users:
            topic_weights[user] = {}
            total_influence = sum(influence[user].values())
            
            if total_influence > 0:
                for topic in topics:
                    topic_weights[user][topic] = influence[user][topic] / total_influence
            else:
                # Default to equal distribution if total influence is zero
                for topic in topics:
                    topic_weights[user][topic] = 1.0 / num_topics
        
        # Calculate the second part of influence: influence propagation
        for followee in users:
            for follower in followers[followee]:
                follower_total_influence = sum(influence[follower].values())
                
                for topic in topics:
                    # Topic-specific influence propagation
                    if topic in interaction_strengths[follower][followee]:
                        strength = interaction_strengths[follower][followee][topic]
                        topic_weight = topic_weights[follower][topic]
                        
                        new_influence[followee][topic] += (
                            damping_factor * follower_total_influence * topic_weight * strength
                        )
                    
                    # General influence propagation
                    remaining_proportion = 1.0 - total_interaction_strengths[follower][followee]
                    if remaining_proportion > 0:
                        avg_topic_weight = sum(topic_weights[follower].values()) / num_topics
                        
                        new_influence[followee][topic] += (
                            damping_factor * follower_total_influence * avg_topic_weight * 
                            remaining_proportion / num_topics
                        )
        
        # Update influence scores
        influence = new_influence
        
        # Check for convergence
        max_diff = 0.0
        for user in users:
            for topic in topics:
                diff = abs(influence[user][topic] - prev_influence[user][topic])
                max_diff = max(max_diff, diff)
        
        if max_diff < tolerance:
            break
    
    # Calculate total influence for each user
    total_influence = {user: sum(influence[user].values()) for user in users}
    
    # Find the top k influencers
    top_k = []
    min_heap = []
    
    for user, score in total_influence.items():
        if len(min_heap) < k:
            heapq.heappush(min_heap, (score, user))
        elif score > min_heap[0][0]:
            heapq.heappushpop(min_heap, (score, user))
    
    # Sort in descending order of influence
    top_k = [user for _, user in sorted(min_heap, reverse=True)]
    
    return top_k