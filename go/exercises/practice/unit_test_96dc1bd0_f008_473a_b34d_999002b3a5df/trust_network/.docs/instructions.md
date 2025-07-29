## Project Name

```
Decentralized Social Network Trust Graph
```

## Question Description

You are tasked with designing and implementing a trust graph for a decentralized social network. In this network, users can follow each other and assign trust scores to other users. The goal is to efficiently determine the trustworthiness of a given user within the network.

**Data Model:**

*   **User:** Each user is identified by a unique string ID (e.g., a public key hash).
*   **Trust Edge:** A directed edge from user A to user B represents that user A trusts user B to some degree. The trust is quantified by a floating-point number between 0.0 and 1.0 (inclusive), where 0.0 means no trust and 1.0 means complete trust. A user can follow another user without assigning any trust level.
*   **Graph:** The social network is represented as a directed graph where nodes are users and edges are trust relationships.

**Requirements:**

1.  **Data Storage:** Implement a data structure to efficiently store and retrieve the trust graph. Consider the trade-offs between memory usage and query performance. The graph can be large (millions of users and edges).

2.  **Trust Propagation:** Implement an algorithm to calculate the trustworthiness of a user. Trustworthiness is defined as the weighted average of trust scores from users who directly trust the target user.  Specifically, the trustworthiness of user `U` is calculated as follows:

    *   Let `Incoming(U)` be the set of users who trust `U`.
    *   For each user `V` in `Incoming(U)`, let `Trust(V, U)` be the trust score `V` has assigned to `U`. If no trust is assigned, `Trust(V, U)` is 0.
    *   Let `Trustworthiness(U)` be: `sum(Trust(V, U) for V in Incoming(U)) / len(Incoming(U))`.
    *   If `Incoming(U)` is empty, `Trustworthiness(U)` is 0.0.

3.  **Trust Path Discovery:** Given two users A and B, find the trust path (sequence of users) with the highest cumulative trust score from A to B. The cumulative trust score of a path is the product of the trust scores along the path. If multiple paths exist with the same highest cumulative trust score, return the shortest one (fewest users). If no path exists, return an empty path. You must efficiently calculate the path with maximal cumulative trust.

4.  **Circular Trust Detection:** Implement an algorithm to detect cycles in the trust graph. Specifically, identify all users who are part of any cycle in the graph.  This is important for mitigating Sybil attacks.

5.  **API:** Provide the following API functions:

    *   `AddUser(userID string)`: Adds a user to the network.
    *   `AddTrustEdge(fromUserID string, toUserID string, trustScore float64)`: Adds a trust edge between two users. The `trustScore` must be between 0.0 and 1.0 (inclusive).
    *   `GetTrustworthiness(userID string) float64`: Returns the trustworthiness of a user.
    *   `FindBestTrustPath(fromUserID string, toUserID string) []string`: Returns the best trust path (list of user IDs) from one user to another.
    *   `GetUsersInCycles() []string`: Returns a list of userIDs which are present in any cycle.

**Constraints:**

*   **Efficiency:** The graph operations (adding users, adding edges, calculating trustworthiness, finding trust paths, and detecting cycles) must be reasonably efficient, especially for large graphs. Consider using appropriate data structures and algorithms to minimize the time complexity.
*   **Scalability:** The solution should be designed to handle a large number of users and trust relationships.
*   **Error Handling:** Implement robust error handling, especially for invalid input (e.g., invalid trust scores, non-existent users).
*   **Real-world Considerations:** Consider the potential for malicious users attempting to manipulate the trust network (e.g., creating fake accounts to boost their trustworthiness). How might your design mitigate these attacks?  (No need to implement mitigation, just mention the consideration in a comment)

**Grading Criteria:**

*   Correctness: The solution must correctly implement all the required functionalities.
*   Efficiency: The solution must be efficient enough to handle large graphs within reasonable time limits.
*   Scalability: The solution should be designed to scale to a large number of users and trust relationships.
*   Code Quality: The code must be well-structured, readable, and maintainable.
*   Error Handling: The solution must handle errors gracefully and provide informative error messages.

This problem requires a strong understanding of graph data structures and algorithms, as well as the ability to design and implement a scalable and efficient solution. Good luck!
