from collections import defaultdict, deque
import heapq

def rank_users(node_id, local_network, max_hops, max_users):
    """
    Rank users in a decentralized social network based on their influence.
    
    Args:
        node_id: ID of the starting user
        local_network: Function that returns local network data for a user
        max_hops: Maximum number of network hops to explore
        max_users: Maximum number of users to process
        
    Returns:
        List of tuples (user_id, score) sorted by influence score (descending)
    """
    # Track visited users and their network data
    visited = {}
    
    # Queue for BFS traversal: (user_id, current_hop)
    queue = deque([(node_id, 0)])
    
    # Dictionary to store follower and followee counts
    followers_count = defaultdict(int)
    followees_count = defaultdict(int)
    
    # Set of users we've seen (to avoid re-processing)
    seen_users = {node_id}
    
    # Graph representation for calculating PageRank later
    graph = defaultdict(list)  # user -> list of followers
    out_degrees = defaultdict(int)  # number of users a user follows
    
    # BFS to explore the network within constraints
    while queue and len(visited) < max_users:
        current_id, hop_count = queue.popleft()
        
        # Skip if we've reached max hop limit
        if hop_count > max_hops:
            continue
        
        # Get network data for current user
        network_data = local_network(current_id)
        
        # Skip if data is unavailable
        if network_data is None:
            continue
        
        # Store the network data
        visited[current_id] = network_data
        followers = network_data.get("followers", [])
        followees = network_data.get("followees", [])
        
        # Update counts
        followers_count[current_id] += len(followers)
        for follower in followers:
            followees_count[follower] += 1
            # Add to graph (follower -> current_id, as current_id is followed by follower)
            graph[current_id].append(follower)
            out_degrees[follower] += 1
        
        # Add unvisited neighbors to the queue
        for user in set(followers + followees):
            if user not in seen_users and len(seen_users) < max_users:
                queue.append((user, hop_count + 1))
                seen_users.add(user)
    
    # Calculate influence score using a combination of:
    # 1. PageRank algorithm to measure global influence
    # 2. Direct followers count to boost users with many direct followers
    # 3. Weighted by the hop distance from the starting node
    
    # Implement PageRank
    pagerank = calculate_pagerank(graph, out_degrees, visited.keys())
    
    # Calculate final influence scores
    influence_scores = []
    for user_id in visited:
        # Base influence from PageRank
        score = pagerank.get(user_id, 0) * 0.7
        
        # Add direct follower component
        follower_count = followers_count.get(user_id, 0)
        normalized_follower_score = min(follower_count / 10.0, 1.0)  # Normalize to [0,1]
        score += normalized_follower_score * 0.3
        
        influence_scores.append((user_id, score))
    
    # Sort by score (descending), then by user_id (ascending) for ties
    influence_scores.sort(key=lambda x: (-x[1], x[0]))
    
    return influence_scores

def calculate_pagerank(graph, out_degrees, user_ids, damping=0.85, iterations=20):
    """
    Calculate PageRank for users in the network.
    
    Args:
        graph: Dictionary mapping user_ids to their followers
        out_degrees: Dictionary mapping user_ids to their out-degree (followees count)
        user_ids: Set of user ids to calculate PageRank for
        damping: Damping factor for PageRank algorithm
        iterations: Number of iterations for PageRank calculation
        
    Returns:
        Dictionary mapping user_ids to their PageRank scores
    """
    # Initialize PageRank scores
    n = len(user_ids)
    if n == 0:
        return {}
    
    pagerank = {user_id: 1.0 / n for user_id in user_ids}
    
    # Iteratively update PageRank
    for _ in range(iterations):
        new_pagerank = {user_id: (1 - damping) / n for user_id in user_ids}
        
        for user_id, followers in graph.items():
            if user_id in user_ids:  # Only consider users we've visited
                for follower in followers:
                    if follower in user_ids:  # Only calculate for users we've visited
                        # Each follower contributes based on their current PageRank and out-degree
                        out_degree = max(1, out_degrees.get(follower, 1))  # Avoid division by zero
                        new_pagerank[user_id] += damping * pagerank[follower] / out_degree
        
        # Update PageRank values
        pagerank = new_pagerank
    
    # Normalize PageRank values
    total_score = sum(pagerank.values()) or 1  # Avoid division by zero
    normalized_pagerank = {user_id: score / total_score for user_id, score in pagerank.items()}
    
    return normalized_pagerank