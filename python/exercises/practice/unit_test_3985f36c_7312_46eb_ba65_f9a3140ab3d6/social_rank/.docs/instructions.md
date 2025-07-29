## Problem: Decentralized Social Network Ranking

**Description:**

You are tasked with designing a ranking algorithm for a decentralized social network. Unlike traditional social networks with centralized servers, this network operates on a peer-to-peer (P2P) architecture. Each node in the network maintains a partial view of the graph, holding information about some users and their connections (followers and followees). There is no central authority or global view of the network.

Your algorithm must rank users in the network based on their influence, given only local information available at a single starting node. Influence is defined as the ability to spread information effectively throughout the network.

**Input:**

*   `node_id`: The starting user's ID in the network. This is the node where your algorithm begins its exploration.
*   `local_network`: A function that takes a `user_id` as input and returns a dictionary representing the user's local network. The dictionary has the following structure:

    ```python
    {
        "followers": [user_id1, user_id2, ...],  # List of user IDs who follow this user
        "followees": [user_id3, user_id4, ...]   # List of user IDs this user follows
    }
    ```

    If the `user_id` is invalid or the user's information is unavailable, the function returns `None`.  The network is assumed to be large and constantly evolving.  Repeated calls to `local_network` for the same `user_id` at different points in time may potentially return different results due to the dynamic nature of the decentralised network.

*   `max_hops`: An integer representing the maximum number of hops your algorithm can traverse from the starting node. This limits the scope of your exploration and represents a constraint on resource usage.  Each call to `local_network` counts as one hop.
*   `max_users`: An integer representing the maximum number of unique users your algorithm can process. This limits the memory usage of your algorithm and prevents infinite loops in a potentially cyclic network.

**Output:**

A list of tuples, sorted in descending order of influence score. Each tuple should contain a `user_id` and its calculated influence score: `[(user_id1, score1), (user_id2, score2), ...]`.  The influence score should be a non-negative float.

**Constraints and Requirements:**

*   **Decentralized Data:** You cannot assume access to a complete graph representation or global network information. You must rely solely on the `local_network` function to gather data.
*   **Limited Exploration:**  You are limited by `max_hops` and `max_users`. Exceeding either limit will result in termination. Your algorithm should gracefully handle these limits and return the best ranking possible within the given constraints.
*   **Dynamic Network:** The network is dynamic, meaning the connections may change over time. The ranking should be based on a snapshot of the network obtained during your algorithm's execution.  You must take this into account when designing your algorithm.
*   **Efficiency:**  The algorithm should be as efficient as possible in terms of both time and memory. Given the size of the network, brute-force approaches are likely to be infeasible.
*   **Cycles:** The network may contain cycles. Your algorithm must handle cycles gracefully to avoid infinite loops.
*   **Scalability:** While you only need to rank a subset of users, consider how your approach could potentially scale to larger portions of the network.
*   **Robustness:** The algorithm should be robust to missing data (e.g., `local_network` returning `None` for some users) and inconsistent data.
*   **Influence Metric:** The definition of "influence" is intentionally broad. You are free to choose your own metric, but it should reasonably reflect a user's ability to spread information within the network. Consider factors like the number of followers, the influence of followers, and the reach of their followees.  Justify your choice of influence metric in comments.
*   **Tie-breaking:** If multiple users have the same influence score, they should be sorted by `user_id` in ascending order.

**Example:**

```python
def rank_users(node_id, local_network, max_hops, max_users):
    # Your implementation here
    pass
```

**Judging Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The accuracy of the ranking, as determined by a hidden ground truth.
*   **Efficiency:** The time and memory usage of your algorithm.
*   **Scalability:** How well your algorithm performs as the network size and density increase.
*   **Robustness:** The ability to handle missing and inconsistent data.
*   **Clarity:** The readability and maintainability of your code.
*   **Justification:** A clear explanation of your chosen influence metric and its rationale.

This problem requires a deep understanding of graph algorithms, data structures, and optimization techniques. Good luck!
