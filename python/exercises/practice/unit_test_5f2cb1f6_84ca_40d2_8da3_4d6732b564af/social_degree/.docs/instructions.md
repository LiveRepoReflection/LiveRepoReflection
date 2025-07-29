## Project Name:

`Decentralized Social Graph Analytics`

## Question Description:

Design and implement a system for analyzing a decentralized social graph, focusing on efficiency and scalability.

In a traditional, centralized social network, all user data and relationships are stored on a single server or within a cluster controlled by a single entity. This allows for relatively straightforward social graph analysis. However, with the rise of decentralized social networks (like those built on blockchain or federated systems), data is distributed across many independent nodes.

Your task is to create a system that can perform graph analytics on such a decentralized network. Specifically, you need to implement a function that efficiently determines the *k*-degree centrality for a given user within the network.

**Degree Centrality:** The degree centrality of a node (user) in a graph is the number of connections (edges) it has to other nodes. In a social network, this represents the number of friends or followers a user has. *k*-degree centrality extends this concept: it represents the number of nodes that can be reached from a starting node within *k* hops/connections.

**Input:**

*   `user_id`: The ID of the user for whom to calculate the *k*-degree centrality.
*   `k`: The maximum degree of separation/hops to consider. (1 <= k <= 10)
*   `get_neighbors(user_id)`: A function (provided to you) that, when given a `user_id`, returns a *generator* of the user IDs of that user's immediate neighbors (friends/followers).  This simulates accessing data from different nodes in the decentralized network. Assume each call to `get_neighbors` has a non-negligible latency (e.g., simulating network calls).

**Output:**

*   The *k*-degree centrality of the given `user_id`. This is the total number of *unique* users reachable within *k* hops from the starting user, *excluding* the starting user itself.

**Constraints and Considerations:**

1.  **Decentralized Data Access:** You *must* use the provided `get_neighbors` function to access the social graph data. Minimize the number of calls to `get_neighbors` to optimize for network latency.
2.  **Scalability:** The social graph can be very large, with millions of users and connections. Your solution needs to be memory-efficient. Prevent infinite loops in cyclic graphs.
3.  **Time Complexity:** Aim for the best possible time complexity. Consider using appropriate data structures and algorithms to optimize performance.  Avoid naive approaches that would result in excessive calls to `get_neighbors` or exponential time complexity.
4.  **Correctness:** Ensure your solution accurately calculates the *k*-degree centrality for all possible graph structures, including disconnected graphs and graphs with cycles.
5.  **Error Handling:** Add an argument validation to check the value of k and raise appropriate error.
6.  **Optimization:** Consider that the `get_neighbors` function might return duplicate user IDs. Your solution should handle these duplicates efficiently.
7.  **Large Datasets:** The dataset will be large, so efficiency is paramount. Pay attention to constant factors in your complexity analysis.

**Example:**

Assume the following connections:

*   User 1 is connected to users 2, 3, and 4.
*   User 2 is connected to users 1 and 5.
*   User 3 is connected to user 1.
*   User 4 is connected to user 1.
*   User 5 is connected to user 2.

If `user_id` is 1 and `k` is 2, the reachable users are:

*   1 hop: 2, 3, 4
*   2 hops: 5 (from 2)

The *k*-degree centrality is 4 (users 2, 3, 4, and 5).
