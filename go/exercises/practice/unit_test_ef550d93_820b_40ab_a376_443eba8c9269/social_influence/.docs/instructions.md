Okay, I'm ready to set a challenging coding problem for a programming competition. Here's the problem description:

## Problem: Decentralized Social Network Analytics

**Description:**

You are tasked with building an analytics engine for a decentralized social network. This network is composed of nodes (users) and edges (connections between users).  Due to the decentralized nature, the network's structure is not centrally stored. Instead, each user node only holds information about its direct connections.

Your engine needs to efficiently answer analytical queries regarding the network's structure, specifically focusing on influence propagation.  Influence is a numerical value associated with each user.  When a user's influence changes, it can propagate to their connected users, and so on, with a decay factor applied at each step.

**Input:**

The input consists of two parts:

1.  **Network Description:** A stream of connection updates in the form of `(user1, user2, type)`, where:
    *   `user1` and `user2` are unique string identifiers for users (nodes).
    *   `type` is either `"add"` or `"remove"`, indicating the addition or removal of a connection between the two users.
    *   The stream ends with a special marker `("END", "END", "END")`.

2.  **Analytical Queries:** A stream of queries, each of the following format: `(user, influence_change, propagation_depth, decay_factor)`.
    *   `user` is the string identifier of the user whose influence is being modified.
    *   `influence_change` is a floating-point number representing the change in the user's influence. It can be positive or negative.
    *   `propagation_depth` is an integer representing the maximum number of hops the influence can propagate from the initial user.
    *   `decay_factor` is a floating-point number between 0 and 1 (inclusive) representing the factor by which the influence decreases with each hop.
    *   The stream ends with a special marker `("END", 0.0, 0, 0.0)`.

**Output:**

For each analytical query, your program should output the *net change* in influence for *every* user in the network, formatted as `user:change`, one user per line, sorted alphabetically by username. Round the change to 6 decimal places. If a user's influence does not change, do not output that user.

**Constraints:**

*   The number of users in the network can be up to 100,000.
*   The number of connections can be up to 500,000.
*   The number of queries can be up to 10,000.
*   `propagation_depth` can range from 0 to 10.
*   The absolute value of `influence_change` can be up to 1000.0.
*   The program must complete all queries within a reasonable time limit (e.g., 10 seconds).
*   Memory usage should be optimized (e.g., avoid storing the entire network structure in memory if possible).

**Edge Cases and Considerations:**

*   **Cycles:** The network might contain cycles. Your propagation algorithm should handle cycles to avoid infinite loops.
*   **Disconnected Components:** The network may consist of disconnected components.  The influence should only propagate within the component containing the initial user.
*   **Multiple Updates:** Multiple connection updates for the same user pair might occur. Your program should handle these updates correctly.
*   **Performance:**  Naive implementations (e.g., repeatedly traversing the network for each query) will likely timeout. You'll need to consider efficient data structures and algorithms to meet the performance requirements. Consider the trade-offs between memory usage and computational complexity.
*   **Floating-Point Precision:** Be mindful of floating-point precision issues when accumulating influence changes.

**Judging Criteria:**

*   Correctness: Does the program produce the correct output for all test cases?
*   Efficiency: Does the program complete all queries within the time limit?
*   Memory Usage: Does the program use memory efficiently?
*   Code Clarity: Is the code well-structured and easy to understand?

This problem challenges contestants to design and implement an efficient and robust algorithm for influence propagation in a decentralized social network, considering various real-world constraints and edge cases.  The large scale of the network and the time constraints demand careful optimization and algorithm selection. Good luck!
