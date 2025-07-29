## Question: Optimized Social Network Reachability

**Problem Description:**

You are tasked with designing an efficient algorithm to determine the reachability between users in a large social network. The network is represented as a directed graph where each node represents a user, and a directed edge from user A to user B indicates that user A follows user B. This means information can flow from A to B.

Given a social network represented as a list of user IDs (integers) and a list of follow relationships (directed edges represented as pairs of user IDs), you need to implement a system that can efficiently answer reachability queries.

Specifically, you need to implement two core functionalities:

1.  **`add_friendship(user1, user2)`:** Adds a directed edge from `user1` to `user2`, indicating `user1` now follows `user2`.

2.  **`is_reachable(user1, user2)`:** Determines if there is a directed path from `user1` to `user2` in the social network.

**Constraints and Requirements:**

*   **Large Scale:** The social network can contain a very large number of users (up to 10<sup>6</sup>) and follow relationships (up to 10<sup>7</sup>).

*   **Real-time Queries:** The `is_reachable` queries should be answered as quickly as possible.  Consider that the system might receive a high volume of these queries.  Aim for sub-linear time complexity, ideally approaching O(1) after some preprocessing.

*   **Dynamic Updates:**  The `add_friendship` operation should also be reasonably efficient, as the social network is constantly evolving.

*   **Memory Limit:** The solution should use memory efficiently, avoiding excessive memory consumption, especially considering the large scale of the network.

*   **Edge Cases:** Handle cases where users do not exist in the network (initially), or when adding duplicate friendships.

*   **Optimization:** Pre-computation or caching strategies should be employed to optimize the `is_reachable` queries, considering the frequency with which certain user pairs might be queried.  However, ensure that updates to the network (via `add_friendship`) invalidate and update the cache appropriately.  Consider the trade-offs between memory usage and query speed.

*   **Multiple Valid Approaches:** There are several potential approaches to solving this problem, each with different trade-offs in terms of time and space complexity. The challenge is to choose the most appropriate approach given the constraints.

**Input:**

*   A list of initial user IDs (can be empty initially).
*   A list of initial follow relationships (can be empty initially).

**Output:**

*   The `add_friendship` method should not return any value.
*   The `is_reachable` method should return `true` if `user2` is reachable from `user1`, and `false` otherwise.

**Challenge:**

Design and implement a system that satisfies the above requirements. Pay close attention to algorithmic efficiency, memory usage, and handling edge cases.  Justify your design choices and analyze the time and space complexity of your solution. Focus on achieving optimal performance, especially for the `is_reachable` queries.
