# Implementation of a scalable content recommendation engine

# Static dataset of content items
contents = [
    {"content_id": "content1", "popularity": 0.95, "metadata": {"tags": ["tech", "ai"]}},
    {"content_id": "content2", "popularity": 0.85, "metadata": {"tags": ["health", "wellness"]}},
    {"content_id": "content3", "popularity": 0.90, "metadata": {"tags": ["tech", "finance"]}},
    {"content_id": "content4", "popularity": 0.80, "metadata": {"tags": ["cooking", "food"]}},
    {"content_id": "content5", "popularity": 0.70, "metadata": {"tags": ["travel", "adventure"]}},
]

# Mapping from content_id to content details for quick lookup
content_map = {content["content_id"]: content for content in contents}

# Simulated user history
user_history = {
    "existing_user": ["content1", "content3"]
}

# Function to calculate popularity score. For new users, only this score is used.
def popularity_score(content):
    return content["popularity"]

# Function to calculate content based score by comparing user tags with content tags.
def content_based_score(user_tags, content):
    match_count = len(set(user_tags).intersection(set(content["metadata"]["tags"])))
    # Each matched tag contributes 0.1 to the score.
    return match_count * 0.1

# Function to simulate collaborative filtering score.
def collaborative_score(user_id, content):
    # For demonstration, assume similar users liked content2 and content4.
    similar_user_likes = {"content2", "content4"}
    return 0.2 if content["content_id"] in similar_user_likes else 0.0

# Main function to get recommendations for a given user_id.
def get_recommendations(user_id):
    if user_id is None:
        raise ValueError("User ID cannot be None")
    
    # Determine if the user is an existing user with history.
    is_existing = user_id in user_history

    # Build a set of content_ids the user has already interacted with.
    user_seen = set()
    user_tags = []
    if is_existing:
        user_seen = set(user_history[user_id])
        # Aggregate tags from all content items the user has viewed.
        for cid in user_seen:
            if cid in content_map:
                user_tags.extend(content_map[cid]["metadata"]["tags"])

    recommendations = []
    for content in contents:
        # Skip content already seen by existing users.
        if is_existing and content["content_id"] in user_seen:
            continue

        # For new users, use only popularity based recommendation.
        if not is_existing:
            score = popularity_score(content)
        else:
            # For existing users, combine multiple strategies.
            # Weights are: popularity 0.5, content-based 0.3, collaborative 0.2.
            pop_score = popularity_score(content)
            cont_score = content_based_score(user_tags, content)
            collab_score = collaborative_score(user_id, content)
            score = 0.5 * pop_score + 0.3 * cont_score + 0.2 * collab_score

        recommendations.append({"content_id": content["content_id"], "score": score})

    # Sort recommendations in descending order by score.
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations