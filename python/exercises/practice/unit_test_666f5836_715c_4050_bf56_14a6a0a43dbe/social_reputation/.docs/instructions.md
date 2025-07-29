## Problem: Decentralized Social Network Reputation Aggregation

**Description:**

You are tasked with building a reputation aggregation system for a decentralized social network. This network consists of users, posts, and endorsements. Due to the decentralized nature, data is fragmented and potentially inconsistent across various nodes. Your system needs to efficiently aggregate reputation scores for users based on endorsements they receive on their posts.

**Data Model:**

*   **User:** Identified by a unique string `user_id`.
*   **Post:** Identified by a unique string `post_id`, authored by a `user_id`.
*   **Endorsement:** Represents a positive vote on a post. Contains the `post_id` and the `endorser_id` (the `user_id` of the person giving the endorsement). An endorser can only endorse each post once.

**Problem Statement:**

Given a large dataset containing information about users, posts, and endorsements distributed across multiple data sources, your goal is to calculate the reputation score for each user in the network.

**Reputation Score Calculation:**

The reputation score for a user is calculated as follows:

1.  For each post authored by the user, count the number of unique endorsements it has received.
2.  Sum the endorsement counts across all posts authored by the user.
3.  Apply a "reciprocity bonus". If an endorser has also received endorsements from the post author, a bonus of `(1 / log2(number of endorsements received by endorser from post author + 2))` is added to the endorsement count of the post.  Note: If number of endorsements received by endorser from post author is 0, the bonus will be `1 / log2(2) = 1`.

**Input:**

The input data will be provided in a structured format that simulates distributed data sources:

*   `users`: A list of `user_id` strings.
*   `posts`: A list of tuples, where each tuple represents a post and contains (`post_id`, `user_id`).
*   `endorsements`: A list of tuples, where each tuple represents an endorsement and contains (`post_id`, `endorser_id`).

**Output:**

A dictionary where the keys are `user_id` strings and the values are their calculated reputation scores (floating-point numbers) rounded to 5 decimal places. The dictionary should include all users from the input `users` list, even if their reputation score is 0.

**Constraints:**

*   The dataset can be very large (millions of users, posts, and endorsements).
*   The solution must be efficient in terms of time and memory usage.
*   The code should be well-structured, readable, and maintainable.
*   Assume that `post_id` and `user_id` are unique.
*   If `log2(x)` is undefined, use `0` as the result.
*   Endorser cannot endorse the same post twice.

**Example:**

```python
users = ["user1", "user2", "user3"]
posts = [("post1", "user1"), ("post2", "user1"), ("post3", "user2")]
endorsements = [("post1", "user2"), ("post1", "user3"), ("post2", "user2"), ("post3", "user1")]

# Expected output (Illustrative):
# {
#     "user1": 2.0,  # post1: 2 endorsements, post2: 1 endorsement; no reciprocity bonus in this example
#     "user2": 1.0,  # post3: 1 endorsement
#     "user3": 0.0
# }
```

**Challenge:**

Develop a Python solution that efficiently calculates the reputation scores for all users, considering the reciprocity bonus and the large-scale nature of the data. Optimize your solution for both time and memory efficiency.
