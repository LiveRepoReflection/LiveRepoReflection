import heapq
from collections import defaultdict

def find_optimal_influencer_path(graph, user_attributes, user_reach, target_audience_profile, 
                                max_attribute_values, seed_user_id, K, Lambda):
    """
    Find the optimal path of influencers from a seed user to maximize reach and minimize attribute distance.
    
    Args:
        graph (dict): Social network graph where keys are user IDs and values are lists of connected user IDs.
        user_attributes (dict): Dictionary of user attributes where keys are user IDs.
        user_reach (dict): Dictionary of user reach values where keys are user IDs.
        target_audience_profile (dict): Dictionary of target audience attributes.
        max_attribute_values (dict): Dictionary of maximum possible values for each attribute.
        seed_user_id (int): The ID of the starting influencer.
        K (int): Maximum length of the influencer chain.
        Lambda (float): Weighting factor for the optimization metric.
        
    Returns:
        list: Ordered list of user IDs forming the optimal influencer path.
    """
    if seed_user_id not in graph:
        return []
    
    # Calculate attribute distance for each user
    attribute_distances = {}
    for user_id, attrs in user_attributes.items():
        distance = 0
        for attr, target_val in target_audience_profile.items():
            if attr in attrs:
                distance += abs(attrs[attr] - target_val)
            else:
                # If attribute is missing, use the maximum possible value as the distance
                distance += max_attribute_values.get(attr, 0)
        attribute_distances[user_id] = distance
    
    # Priority queue for Dijkstra's algorithm with a metric
    # Each entry is (-metric, path)
    # We use negative because heapq is a min-heap and we want to maximize the metric
    heap = [(0, [seed_user_id])]
    
    # To keep track of the best metric for each path length
    best_metrics = defaultdict(lambda: float('-inf'))
    
    # To keep track of visited paths to avoid cycles
    visited_paths = set()
    visited_paths.add((seed_user_id,))
    
    # To store the best path found
    best_path = [seed_user_id] if seed_user_id in user_reach else []
    best_metric = calculate_metric([seed_user_id], user_reach, attribute_distances, Lambda) if best_path else float('-inf')
    
    while heap:
        current_neg_metric, current_path = heapq.heappop(heap)
        current_metric = -current_neg_metric
        
        # If the current path is better than the best found so far, update the best path
        if current_metric > best_metric:
            best_path = current_path.copy()
            best_metric = current_metric
        
        # If we've reached the maximum path length, continue to the next path
        if len(current_path) >= K:
            continue
        
        # Get the last user in the current path
        last_user = current_path[-1]
        
        # Explore all connected users
        for next_user in graph.get(last_user, []):
            # Skip if this would create a cycle
            if next_user in current_path:
                continue
            
            # Create a new path by adding the next user
            new_path = current_path + [next_user]
            
            # Convert to tuple for hashing
            new_path_tuple = tuple(new_path)
            
            # Skip if we've already visited this path
            if new_path_tuple in visited_paths:
                continue
            
            # Calculate the metric for the new path
            new_metric = calculate_metric(new_path, user_reach, attribute_distances, Lambda)
            
            # Add the new path to the queue if it's promising
            if new_metric > best_metrics[len(new_path)]:
                best_metrics[len(new_path)] = new_metric
                heapq.heappush(heap, (-new_metric, new_path))
                visited_paths.add(new_path_tuple)
    
    return best_path

def calculate_metric(path, user_reach, attribute_distances, Lambda):
    """
    Calculate the optimization metric for a given path.
    
    Args:
        path (list): List of user IDs forming a path.
        user_reach (dict): Dictionary of user reach values.
        attribute_distances (dict): Dictionary of attribute distances from target.
        Lambda (float): Weighting factor.
        
    Returns:
        float: The optimization metric value.
    """
    # Check if the path is valid
    if not path:
        return float('-inf')
    
    # Calculate path reach
    path_reach = sum(user_reach.get(user_id, 0) for user_id in path)
    
    # Calculate average attribute distance
    total_distance = sum(attribute_distances.get(user_id, float('inf')) for user_id in path)
    avg_distance = total_distance / len(path) if path else float('inf')
    
    # Calculate and return the metric
    return path_reach - Lambda * avg_distance