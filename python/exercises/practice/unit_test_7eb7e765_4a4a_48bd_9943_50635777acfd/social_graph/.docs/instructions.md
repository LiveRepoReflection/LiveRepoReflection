## Project Name

**Scalable Social Graph Analytics**

## Question Description

You are tasked with building a scalable system for analyzing relationships within a large social network. The social network consists of users and their connections (friendships).  The system should efficiently answer various analytical queries about the graph, with a focus on resilience to network partitions and the ability to handle a dynamically changing network.

**Data Model:**

*   **Users:** Each user is represented by a unique 64-bit integer ID.
*   **Connections:** A connection represents a friendship between two users. Connections are undirected (if A is a friend of B, then B is a friend of A).

**Functional Requirements:**

1.  **Add/Remove Users and Connections:**
    *   Implement methods to add new users to the network.
    *   Implement methods to add new connections between users.
    *   Implement methods to remove existing users from the network. Removing a user also removes all connections associated with that user.
    *   Implement methods to remove existing connections between users.
2.  **Retrieve User Information:**
    *   Given a user ID, retrieve a list of that user's friends (direct connections).
    *   Given a user ID, retrieve the degree of separation to another user.
        *   Assume that the degree of separation between a user and themselves is 0.
        *   If there is no connection between two users, return -1.
3.  **Analyze Network Topology:**
    *   **Strongly Connected Components (SCCs):** Detect and return all strongly connected components within the graph. (A strongly connected component is a subgraph where every vertex is reachable from every other vertex.)
    *   **Centrality Measures:** Implement at least **one** of the following centrality measures:
        *   **Betweenness Centrality:** For a given user, calculate its betweenness centrality.
        *   **Closeness Centrality:** For a given user, calculate its closeness centrality.
        *   **Eigenvector Centrality:** For a given user, calculate its eigenvector centrality.
4.  **Handle Dynamic Updates:** The social network is constantly evolving. Your system must efficiently handle a stream of add/remove user/connection operations while maintaining the ability to answer analytical queries with reasonable accuracy and latency.
5.  **Resilience to Network Partitions:** Design your system such that if parts of the network become temporarily disconnected (e.g., due to server outages), the system can still function and provide results based on the accessible data.  This is particularly important for retrieving user information and detecting SCCs within the accessible partitions.

**Constraints and Requirements:**

*   **Scalability:** The system should be designed to handle millions of users and connections.
*   **Efficiency:** Analytical queries (especially SCC detection and centrality measures) should be optimized for performance. Aim for sub-quadratic time complexity where possible.
*   **Accuracy:**  While absolute precision is desirable, approximations and heuristics are acceptable if they significantly improve performance, especially for centrality measures.  Clearly document any approximations used and their potential impact on accuracy.
*   **Memory Usage:** Be mindful of memory consumption, especially when dealing with large graphs.  Consider using appropriate data structures and techniques to minimize memory footprint.
*   **Real-World Considerations:**  Think about how real-world social networks differ from theoretical graphs.  Consider optimizations that exploit common network characteristics (e.g., power-law degree distribution, community structure).
*   **Concurrency:** Implement thread-safe data structures to handle concurrent requests.
*   **Modularity:** Design your system with clear separation of concerns.
*   **Testability:** Provide thorough unit tests to validate the correctness and performance of your implementation.

**Input/Output:**

*   The input to your system will be a stream of operations (add user, remove user, add connection, remove connection).
*   The output will be the results of the analytical queries (friend list, degree of separation, SCCs, centrality measures). The output format should be well-defined and easily parsable.

**Bonus Challenges:**

*   Implement a distributed version of your system that can run across multiple machines.
*   Support more complex relationship types (e.g., "follows," "family," "colleague") with different properties.
*   Implement a recommendation engine that suggests new connections to users based on their existing network and other users' interests.

This problem requires a solid understanding of graph algorithms, data structures, system design principles, and optimization techniques. Good luck!
