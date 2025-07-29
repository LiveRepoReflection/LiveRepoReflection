def predict_rating(user_ratings, global_info, target_item_id):
    # Regularization parameter
    lambda_reg = 1.0

    # If target item is not in global info, fallback to overall average
    if target_item_id not in global_info['item_stats']:
        overall_avg = sum(item['avg_rating'] for item in global_info['item_stats'].values()) / len(global_info['item_stats'])
        return overall_avg

    target_item = global_info['item_stats'][target_item_id]
    target_category = target_item.get('category', None)
    global_avg = target_item.get('avg_rating', 3.0)

    # If user has not rated anything, return global average rating for target item.
    if not user_ratings:
        return global_avg

    weighted_sum = 0.0
    weight_total = 0.0

    for rated_item_id, rating in user_ratings:
        if rated_item_id not in global_info['item_stats']:
            continue
        rated_item = global_info['item_stats'][rated_item_id]
        rated_category = rated_item.get('category', None)
        # Retrieve similarity from global_info; if not found, similarity defaults to 0.
        similarity = global_info['category_similarity'].get((target_category, rated_category), 0.0)
        weighted_sum += similarity * rating
        weight_total += similarity

    # Use regularization if no similar items found
    predicted = (weighted_sum + lambda_reg * global_avg) / (weight_total + lambda_reg)
    # Ensure rating within [1, 5]
    if predicted < 1.0:
        predicted = 1.0
    elif predicted > 5.0:
        predicted = 5.0
    return predicted

def get_recommendations(user_ratings, global_info, num_recommendations):
    # Build a set of item ids the user has already rated.
    rated_item_ids = set([item_id for item_id, _ in user_ratings])
    recommendations = []
    for item_id in global_info['item_stats']:
        if item_id in rated_item_ids:
            continue
        predicted = predict_rating(user_ratings, global_info, item_id)
        recommendations.append({'item_id': item_id, 'predicted_rating': predicted})
    # Sort recommendations in descending order of predicted rating.
    recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
    return recommendations[:num_recommendations]

def update_model(user_ratings, feedback_data, global_info):
    # feedback_data is a list of tuples: (item_id, feedback_rating)
    # Update the local user ratings with the provided feedback.
    updated_ratings = {item_id: rating for item_id, rating in user_ratings}
    for item_id, feedback_rating in feedback_data:
        updated_ratings[item_id] = feedback_rating
    # Convert back to list format.
    updated_user_ratings = list(updated_ratings.items())
    # Return new recommendations based on updated ratings.
    # For demonstration, we return recommendations for 3 items.
    return get_recommendations(updated_user_ratings, global_info, 3)