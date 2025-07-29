import numpy as np
import math
from collections import defaultdict
from typing import List, Dict, Any, Callable


def add_laplace_noise(value: float, sensitivity: float, epsilon: float) -> float:
    """
    Add Laplace noise to a value for differential privacy.
    
    Args:
        value: The true value to be perturbed
        sensitivity: Maximum change in the value that can result from changing one user's data
        epsilon: Privacy parameter (smaller = more privacy)
        
    Returns:
        The perturbed value
    """
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise


def compute_similarity_with_privacy(user_id: int, other_user_id: int, 
                                    data_accessor: Any, epsilon: float) -> float:
    """
    Compute the similarity between two users with differential privacy.
    
    Args:
        user_id: ID of the first user
        other_user_id: ID of the second user
        data_accessor: Object to access user data
        epsilon: Privacy parameter
        
    Returns:
        A privacy-preserving similarity score
    """
    user_data = data_accessor.get_user_data(user_id)
    other_user_data = data_accessor.get_user_data(other_user_id)
    
    # Find common items rated by both users
    common_items = set(user_data.keys()) & set(other_user_data.keys())
    
    if not common_items:
        return 0.0
    
    # Get ratings for common items
    user_ratings = np.array([user_data[item] for item in common_items])
    other_ratings = np.array([other_user_data[item] for item in common_items])
    
    # Compute cosine similarity
    dot_product = np.sum(user_ratings * other_ratings)
    norm_user = np.sqrt(np.sum(user_ratings ** 2))
    norm_other = np.sqrt(np.sum(other_ratings ** 2))
    
    if norm_user == 0 or norm_other == 0:
        return 0.0
    
    similarity = dot_product / (norm_user * norm_other)
    
    # Apply differential privacy
    # Sensitivity is 1 for cosine similarity when ratings are normalized
    sensitivity = 2.0 / len(common_items) if common_items else 0.0
    private_similarity = add_laplace_noise(similarity, sensitivity, epsilon)
    
    # Clamp the result to [-1, 1]
    return max(min(private_similarity, 1.0), -1.0)


def federated_model_aggregation(user_ids: List[int], data_accessor: Any, 
                                epsilon: float) -> Dict[int, Dict[int, float]]:
    """
    Aggregate user models in a privacy-preserving manner.
    
    Args:
        user_ids: List of user IDs to include in the aggregation
        data_accessor: Object to access user data
        epsilon: Privacy parameter
        
    Returns:
        Aggregated model (user-item rating predictions)
    """
    aggregated_model = defaultdict(dict)
    
    # Compute the similarity matrix
    similarity_matrix = {}
    # Split epsilon for similarity computation and aggregation
    similarity_epsilon = epsilon / 2
    
    for user_id in user_ids:
        similarity_matrix[user_id] = {}
        for other_id in user_ids:
            if user_id == other_id:
                similarity_matrix[user_id][other_id] = 1.0
            elif other_id in similarity_matrix and user_id in similarity_matrix[other_id]:
                similarity_matrix[user_id][other_id] = similarity_matrix[other_id][user_id]
            else:
                similarity_matrix[user_id][other_id] = compute_similarity_with_privacy(
                    user_id, other_id, data_accessor, similarity_epsilon
                )
    
    # For each user, compute predicted ratings
    aggregation_epsilon = epsilon / 2
    for user_id in user_ids:
        user_data = data_accessor.get_user_data(user_id)
        
        # Find similar users
        similar_users = sorted(
            [(other_id, similarity_matrix[user_id][other_id]) 
             for other_id in user_ids if other_id != user_id],
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Use top-k similar users for prediction (use O(log n) similar users)
        k = max(1, int(math.log2(len(user_ids))))
        top_similar_users = similar_users[:k]
        
        # Get all items rated by similar users
        all_items = set()
        for other_id, _ in top_similar_users:
            other_data = data_accessor.get_user_data(other_id)
            all_items.update(other_data.keys())
        
        # Remove items already rated by the user
        all_items = all_items - set(user_data.keys())
        
        # Compute predicted ratings
        for item_id in all_items:
            numerator = 0.0
            denominator = 0.0
            
            for other_id, similarity in top_similar_users:
                other_data = data_accessor.get_user_data(other_id)
                if item_id in other_data:
                    weight = max(0.0, similarity)  # Only use positive similarities
                    numerator += weight * other_data[item_id]
                    denominator += weight
            
            if denominator > 0:
                # Predict the rating
                predicted_rating = numerator / denominator
                
                # Add noise for differential privacy
                # Sensitivity is 5 (max rating) / denominator
                sensitivity = 5.0 / denominator if denominator > 0 else 0.0
                private_rating = add_laplace_noise(predicted_rating, sensitivity, aggregation_epsilon)
                
                # Clamp to valid rating range
                private_rating = max(min(private_rating, 5.0), 1.0)
                
                aggregated_model[user_id][item_id] = private_rating
    
    return aggregated_model


def generate_recommendations(user_id: int, item_ids: List[int], 
                            epsilon: float, data_accessor: Any) -> List[int]:
    """
    Generate recommendations for a user using privacy-preserving collaborative filtering.
    
    Args:
        user_id: ID of the user for whom to generate recommendations
        item_ids: List of item IDs to consider for recommendation
        epsilon: Privacy parameter
        data_accessor: Object to access user data
        
    Returns:
        Sorted list of recommended item IDs
    """
    if not item_ids:
        return []
    
    # Get all user IDs (simulated by retrieving a set of users)
    # In a real system, this might be a subset of users or neighbors
    # We'll use a sliding window approach to simulate getting users in batches
    all_user_data = {}
    # Simulate getting about 1000 users or O(log N) * N users
    max_users = 1000
    
    # Start with the target user
    all_user_data[user_id] = data_accessor.get_user_data(user_id)
    
    # Then get data for other users (sliding window approach)
    for offset in range(0, max_users, 100):
        for i in range(offset, min(offset + 100, max_users)):
            current_id = (user_id + i) % max_users  # Wrap around to stay within range
            if current_id != user_id:
                all_user_data[current_id] = data_accessor.get_user_data(current_id)
    
    user_ids = list(all_user_data.keys())
    
    # Use federated model aggregation to compute recommendations
    aggregated_model = federated_model_aggregation(user_ids, data_accessor, epsilon)
    
    # Get predicted ratings for the target user
    if user_id not in aggregated_model:
        # If no predictions for user, return random recommendations
        np.random.shuffle(item_ids)
        return item_ids
    
    user_predictions = aggregated_model[user_id]
    
    # Filter and sort recommendations
    user_data = data_accessor.get_user_data(user_id)
    already_rated = set(user_data.keys())
    
    # Filter out already rated items and items not in item_ids
    candidate_items = [(item, user_predictions[item]) 
                       for item in user_predictions
                       if item in item_ids and item not in already_rated]
    
    # Add items that are in item_ids but don't have predictions
    # Assign them a neutral rating with noise
    unpredicted_items = set(item_ids) - set(already_rated) - set(item for item, _ in candidate_items)
    for item in unpredicted_items:
        # Neutral rating with differential privacy
        neutral_rating = add_laplace_noise(3.0, 1.0, epsilon)
        candidate_items.append((item, neutral_rating))
    
    # Sort by predicted rating (descending)
    sorted_items = sorted(candidate_items, key=lambda x: x[1], reverse=True)
    
    # Return sorted list of item IDs
    return [item for item, _ in sorted_items]