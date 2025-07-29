## Problem: Optimized Social Network Influence Propagation

**Description:**

You are tasked with designing an efficient algorithm to simulate influence propagation within a large social network. The network consists of users and the connections (friendships) between them. Each user has a certain level of "resistance" to influence. When a user is "activated" (e.g., by seeing an advertisement or a trending topic), they may influence their friends, potentially activating them as well.

Given a social network represented as a graph, an initial set of "seed" users who are activated, and a "propagation probability," determine the final set of activated users.

**Data Representation:**

The social network is represented as an adjacency list. The keys of the map are user IDs (integers). The values are vectors of user IDs representing the users connected to the key user.

**Activation Rules:**

1.  **Initial Activation:** The users in the given seed set are initially activated.
2.  **Propagation:** In each round, an activated user has a chance to activate each of their non-activated friends. The probability of activating a friend is determined by the `propagation_probability`.
3.  **Resistance:** Each user has a "resistance" value (integer). The actual probability of activation is `propagation_probability` divided by the `resistance`.
4.  **Iteration:** The propagation process continues until no new users are activated in a round.
5.  **Optimization:** Since the network can be very large, it is crucial to optimize the algorithm for speed and memory usage.

**Input:**

*   `network`: A `HashMap<usize, Vec<usize>>` representing the social network.  `usize` represents user ID.
*   `seed_users`: A `HashSet<usize>` representing the initial set of activated users.
*   `resistances`: A `HashMap<usize, usize>` representing the resistance value for each user.
*   `propagation_probability`: A `f64` representing the base probability of influence propagation.
*   `rounds_limit`: A `usize` representing the maximum number of rounds the propagation can run to prevent infinite loops.

**Output:**

*   A `HashSet<usize>` representing the final set of activated users.

**Constraints and Edge Cases:**

*   The network can be very large (millions of users and connections).
*   The seed set can be empty or contain a large number of users.
*   Users may have varying degrees of connectivity.
*   The graph may contain cycles.
*   The resistance values can vary significantly.
*   The `propagation_probability` is a float between 0.0 and 1.0 (inclusive).
*   Handle cases where a user in `seed_users` or a friend in the network does not have a corresponding entry in the `resistances` map. Assume a default resistance of 1 in such cases.
*   The graph may not be fully connected.
*   The `rounds_limit` must be strictly enforced to prevent infinite loops.
*   The function should gracefully handle invalid user IDs (i.e., IDs that are not present in the network).

**Requirements:**

*   **Efficiency:** The algorithm must be highly efficient in terms of both time and memory. Aim for an algorithm that scales well with the size of the network. Consider using appropriate data structures and algorithmic techniques to minimize computational complexity.
*   **Correctness:** The algorithm must accurately simulate the influence propagation process according to the specified rules.
*   **Rust Idiomaticity:** The solution should be written in idiomatic Rust, utilizing Rust's features for safety, concurrency (if applicable and beneficial), and performance.
*   **No External Dependencies:** The solution should not use any external crates beyond the standard library.

**Optimization Hints:**

*   Consider using bitsets or other space-efficient data structures to represent the set of activated users.
*   Optimize the iteration order to minimize unnecessary computations.
*   Explore parallel processing techniques if applicable and beneficial for performance.
*   Avoid unnecessary copying or cloning of data.

This problem requires a solid understanding of graph algorithms, probability, data structures, and efficient Rust programming. The challenge lies in designing an algorithm that can handle large-scale social networks within the given constraints. Good luck!
