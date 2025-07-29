import math

def calculate_reputation(users, posts, endorsements):
    # Build mapping from post_id to post_author.
    post_to_author = {}
    for post_id, author in posts:
        post_to_author[post_id] = author

    # Filter endorsements for uniqueness using a set.
    unique_endorsements = set()
    for post_id, endorser in endorsements:
        if post_id in post_to_author:
            unique_endorsements.add((post_id, endorser))
    
    # Build mapping of endorsements given by each user.
    # given_by[u][target] = count of endorsements that user u has given to posts authored by target.
    given_by = {}
    for post_id, endorser in unique_endorsements:
        author = post_to_author[post_id]
        if endorser not in given_by:
            given_by[endorser] = {}
        given_by[endorser][author] = given_by[endorser].get(author, 0) + 1

    # Build mapping for posts to unique endorsers.
    post_endorsements = {}
    for post_id, endorser in unique_endorsements:
        if post_id not in post_endorsements:
            post_endorsements[post_id] = set()
        post_endorsements[post_id].add(endorser)

    # Initialize reputation score for each user.
    reputation = {user: 0.0 for user in users}

    # For each post, calculate endorsement bonus.
    for post_id, author in post_to_author.items():
        if post_id not in post_endorsements:
            continue
        for endorser in post_endorsements[post_id]:
            # Reciprocal count: endorsements from the post author on posts by the endorser.
            reciprocal = 0
            if author in given_by and endorser in given_by[author]:
                reciprocal = given_by[author][endorser]
            bonus = 1.0 / math.log2(reciprocal + 2)
            reputation[author] += bonus

    # Round each reputation score to 5 decimals.
    for user in reputation:
        reputation[user] = round(reputation[user], 5)
    return reputation

if __name__ == '__main__':
    # Example usage for debugging purposes.
    users = ["user1", "user2", "user3"]
    posts = [("post1", "user1"), ("post2", "user1"), ("post3", "user2")]
    endorsements = [("post1", "user2"), ("post1", "user3"), ("post2", "user2"), ("post3", "user1")]
    print(calculate_reputation(users, posts, endorsements))