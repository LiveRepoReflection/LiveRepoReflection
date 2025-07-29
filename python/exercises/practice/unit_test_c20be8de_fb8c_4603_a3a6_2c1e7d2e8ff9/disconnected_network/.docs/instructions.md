## The Disconnected Social Network

### Question Description

You are tasked with analyzing the structure of a large, dynamic social network represented as a graph. The network consists of `N` users (nodes) and `M` connections (edges) representing friendships. Due to various technical glitches and network partitions, the network can become disconnected, resulting in multiple independent sub-networks or "communities".

The network's connectivity changes over time as users join, leave, or form/break connections. You will receive a series of `Q` queries that simulate these changes and ask you to analyze the resulting network structure.

**Specifically, you need to implement a system that can efficiently handle the following operations:**

1.  **`add_user(user_id)`**: Adds a new user with the given `user_id` to the network.  If the user already exists, do nothing. User IDs are integers.
2.  **`remove_user(user_id)`**: Removes the user with the given `user_id` from the network. Also removes all connections associated with this user. If the user doesn't exist, do nothing.
3.  **`add_connection(user1_id, user2_id)`**: Adds a connection (undirected edge) between the users with IDs `user1_id` and `user2_id`. If the connection already exists or either user doesn't exist, do nothing. Also, self-loops (connecting a user to itself) should be ignored.
4.  **`remove_connection(user1_id, user2_id)`**: Removes the connection between the users with IDs `user1_id` and `user2_id`. If the connection doesn't exist or either user doesn't exist, do nothing.
5.  **`get_largest_community_size()`**: Returns the number of users in the largest connected community (sub-network). If the network is empty, return 0.
6.  **`get_community_count()`**: Returns the total number of distinct connected communities in the network. If the network is empty, return 0.
7.  **`are_users_connected(user1_id, user2_id)`**: Returns True if the given user ids are connected, meaning there is a path of any length between them, otherwise, return False. Return False if either user doesn't exist.

**Constraints:**

*   `1 <= N <= 10^6` (Maximum number of users that can exist at any time)
*   `1 <= M <= 10^7` (Maximum number of connections that can exist at any time)
*   `1 <= Q <= 10^5` (Number of queries)
*   User IDs are integers in the range `[1, 10^9]`
*   The operations must be performed efficiently, particularly `get_largest_community_size()` and `get_community_count()`, even with a large number of users and connections.
*   Memory usage should be considered; avoid storing the entire graph as an adjacency matrix if possible.

**Optimization Requirements:**

Your solution should be optimized for both time and space complexity.  Naive approaches that involve traversing the entire graph for each query will likely time out.  Consider using appropriate data structures and algorithms to achieve the best possible performance.  The `get_largest_community_size()` and `get_community_count()` functions should be implemented with a time complexity significantly better than O(N+M) for each call, where N is the number of users and M is the number of connections.

**Input/Output:**

You do not need to handle input/output. You only need to implement the functions described above. You are provided with an interface and should implement the methods accordingly.

**Judging Criteria:**

Your solution will be judged based on the following criteria:

*   Correctness: Your code must produce the correct output for all test cases.
*   Efficiency: Your code must execute within the time and memory limits.
*   Code Quality: Your code should be well-structured, readable, and maintainable.
*   Handling Edge Cases: Your code should handle all possible edge cases gracefully.
