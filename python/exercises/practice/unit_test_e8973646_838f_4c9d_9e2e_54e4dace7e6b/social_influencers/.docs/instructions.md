## Question: Optimized Social Network Influencer Identification

### Question Description

You are tasked with identifying the top *k* influencers in a large social network. The social network is represented as a directed graph where nodes represent users and edges represent follower relationships (i.e., an edge from user A to user B means user A follows user B).

An influencer's influence is determined by a weighted PageRank-like algorithm.  However, instead of a uniform damping factor and equal weighting of links, this algorithm incorporates user-specific "credibility scores" and topic-based influence propagation.

Here's the breakdown:

1.  **Graph Representation:** The social network is provided as a list of tuples, where each tuple `(A, B, topic, interaction_strength)` represents a directed edge from user A to user B. `topic` is a string representing the category of the relationship (e.g., "sports", "politics", "technology"). `interaction_strength` is a float between 0 and 1 (inclusive) indicating how actively A interacts with B's content on that topic.

2.  **User Credibility Scores:** Each user has a credibility score, provided as a dictionary where keys are user IDs and values are floats between 0 and 1 (inclusive).

3.  **Topic-Based Influence Propagation:**  When a user's influence is propagated to their followers, the influence is split across topics. The proportion of influence propagated to a follower on a given topic is determined by the `interaction_strength` of the edge connecting them for that topic. The remaining influence (1 - sum of `interaction_strength` across all topics for a given follower) is considered "general" influence and is distributed equally across all topics.

4.  **Weighted PageRank Algorithm:** The influence score of a user *i* at iteration *t+1* is calculated as follows:

    ```
    influence(i, t+1) = (1 - damping_factor) * credibility(i) + damping_factor * sum(
        influence(j, t) * weight(j, i)
        for all j who follow i
    )
    ```

    where:

    *   `credibility(i)` is the credibility score of user *i*.
    *   `damping_factor` is a global damping factor (provided as input).
    *   `weight(j, i)` is the weighted influence of user *j* on user *i*.  This is calculated as follows:

        ```
        weight(j, i) = sum(
            interaction_strength(j, i, topic) * topic_weight(j, topic)
            for all topics
        ) + (1 - sum(interaction_strength(j, i, topic) for all topics)) * (sum(topic_weight(j, topic) for all topics) / num_topics)
        ```

        where:

        *   `interaction_strength(j, i, topic)` is the interaction strength between user *j* and user *i* for the given `topic`.
        *   `topic_weight(j, topic)` is the proportion of user *j*'s influence that is allocated to `topic`. This is calculated based on the previous iteration's influence scores across all topics:

            ```
            topic_weight(j, topic) = influence(j, topic, t) / sum(influence(j, topic', t) for all topics topic')
            ```

            If the denominator is zero, `topic_weight(j, topic)` defaults to `1 / num_topics`.
        *   `num_topics` is the total number of unique topics in the network.

5.  **Influence Tracking by Topic:** The `influence(i, t)` is now separated by topic. Start with an initial influence of 1/N for each user and each topic, where N is the number of users. The `influence(i, topic, t+1)` is calculated as:

    ```
    influence(i, topic, t+1) = (1 - damping_factor) * credibility(i) / num_topics + damping_factor * sum(
        influence(j, t) * topic_weight(j, topic) * interaction_strength(j, i, topic)
        for all j who follow i
    ) + damping_factor * sum(
        influence(j, t) * (sum(topic_weight(j, topic') for all topics topic') / num_topics) * (1 - sum(interaction_strength(j, i, topic') for all topics topic'))
        for all j who follow i
    )
    ```

    where `influence(j, t)` is the sum of `influence(j, topic, t)` over all topics.

6.  **Convergence:** The algorithm converges when the absolute difference between the influence scores of each user in consecutive iterations is less than a specified tolerance (`tolerance`).

7.  **Output:** After convergence, return a list of the top *k* influencers (user IDs) based on their *total* influence score (sum of influence across all topics). The list should be sorted in descending order of influence.

**Constraints:**

*   The number of users in the network can be very large (up to 10<sup>6</sup>).
*   The number of edges can be even larger (up to 10<sup>7</sup>).
*   The number of topics is limited to 100.
*   The algorithm must converge within a reasonable number of iterations (e.g., 100).
*   Efficiency is critical.  Solutions should be optimized for both time and memory usage.

**Input:**

*   `edges`: A list of tuples: `[(A, B, topic, interaction_strength), ...]`.
*   `user_credibility`: A dictionary mapping user IDs to credibility scores.
*   `damping_factor`: A float between 0 and 1.
*   `tolerance`: A small float representing the convergence tolerance.
*   `k`: An integer representing the number of top influencers to return.

**Example:**

```python
edges = [
    (1, 2, "sports", 0.8),
    (1, 3, "technology", 0.6),
    (2, 3, "sports", 0.9),
    (3, 2, "politics", 0.7)
]
user_credibility = {
    1: 0.7,
    2: 0.9,
    3: 0.5
}
damping_factor = 0.85
tolerance = 1e-6
k = 2

# Expected output (order may vary depending on implementation details):
# [2, 1]  (User 2 and User 1 are the top 2 influencers)
```

**Challenge:**

Implement the optimized weighted PageRank-like algorithm to efficiently identify the top *k* influencers in the social network, adhering to the constraints and specifications outlined above. Consider the trade-offs between different data structures and algorithmic approaches to achieve optimal performance. Your solution should be robust and handle various edge cases, including disconnected graphs and users with zero credibility.
