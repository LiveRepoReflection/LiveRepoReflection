## Question: Scalable Social Network Reach Estimator

### Question Description

You are building a large-scale social network. One of the key features is estimating the potential reach of a post. A post's reach is defined as the number of unique users who are likely to see it, considering the network's structure, user activity, and content relevance.

The social network consists of users and directed "follows" relationships. User A follows User B means that User A *may* see User B's posts.

Each user has a profile which contains:
1.  **User ID**: A unique integer identifier.
2.  **Interests**: A set of keywords representing the user's interests.

Each post has:
1.  **Poster ID**: The User ID of the user who created the post.
2.  **Keywords**: A set of keywords describing the post's content.

The reach estimation process has the following steps:

1.  **Seed Users**: Identify the initial set of users who will directly see the post. This includes the poster themselves and their direct followers.

2.  **Propagation**: Simulate how the post might spread through the network. A user who sees the post *may* share it with their followers.  The probability of a user sharing a post depends on:
    *   **Interest Alignment**:  How well the post's keywords align with the user's interests. This is calculated as the Jaccard index between the post's keywords and the user's interests:  `|postKeywords ∩ userInterests| / |postKeywords ∪ userInterests|`.
    *   **User Activity**: Each user has an activity score, ranging from 0 to 1, representing how frequently they share content.

    A user will share the post with their followers with a probability equal to `Interest Alignment * User Activity`.

3.  **Reach Calculation**: The reach is the total number of *unique* users who have seen the post (including the initial seed users and those reached through propagation).

**Constraints & Requirements:**

*   The social network can be very large (millions of users and connections). The solution must be scalable and efficient.
*   The propagation should be simulated for a limited number of *iterations* to prevent infinite loops and ensure reasonable execution time.
*   You need to implement a function that estimates the reach of a post given the network data, user profiles, post information, and simulation parameters.
*   The interest alignment calculation should be optimized to avoid redundant computations.
*   Consider the case where a user might see the same post multiple times through different paths. You only want to count each user once in the final reach calculation.
*   The graph structure of the social network can be cyclic, meaning that user A can follow user B, and user B can (directly or indirectly) follow user A. Your reach estimation must handle cycles gracefully and not get stuck in infinite loops.
*   The input data will be provided as follows:

    *   **Users**: A list of user IDs.
    *   **Follows**: A list of tuples, where each tuple `(A, B)` indicates that User A follows User B.
    *   **User Profiles**: A dictionary mapping user IDs to their profile data (interests and activity score).
    *   **Post**: A dictionary containing the poster ID and keywords.
    *   **Iterations**: The number of propagation iterations to perform.

**Your Task:**

Write a C++ function that takes the social network data, user profiles, post information, and simulation parameters as input and returns the estimated reach of the post.  The function signature should be similar to the following:

```cpp
int estimateReach(const std::vector<int>& users,
                  const std::vector<std::pair<int, int>>& follows,
                  const std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>>& userProfiles,
                  const std::pair<int, std::unordered_set<std::string>>& post,
                  int iterations);
```

**Example:**

Imagine a small network with 3 users: 1, 2, and 3.

*   1 follows 2
*   2 follows 3
*   3 follows 1

User profiles:

*   User 1: Interests = {"music", "movies"}, Activity = 0.8
*   User 2: Interests = {"movies", "sports"}, Activity = 0.6
*   User 3: Interests = {"sports", "news"}, Activity = 0.4

Post:

*   Poster = 1, Keywords = {"music", "movies"}

If iterations are set to a reasonable value (e.g., 3 or 4), your function should estimate the number of unique users who will see the post after it propagates through the network.
