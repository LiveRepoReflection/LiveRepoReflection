## Problem: Decentralized Social Network Connectivity

**Description:**

Imagine a decentralized social network where users (nodes) are interconnected through bidirectional communication channels (edges). Due to the nature of the network, connections are not always reliable or persistent.  Users can dynamically join or leave the network.

You are given a constantly evolving network represented by the following operations:

1.  **`add_user(user_id)`:** Adds a new user to the network. `user_id` is a unique integer. If the user already exists, do nothing.

2.  **`remove_user(user_id)`:** Removes a user from the network. If the user does not exist, do nothing. Removing a user also removes all connections associated with that user.

3.  **`connect(user_id1, user_id2, latency)`:** Establishes a connection between `user_id1` and `user_id2` with a given `latency` (an integer representing the delay in communication). Connections are bidirectional. If the connection already exists, update the latency to the new value. If either user does not exist, do nothing. `latency` is always non-negative.

4.  **`disconnect(user_id1, user_id2)`:** Removes the connection between `user_id1` and `user_id2`. If the connection does not exist or either user does not exist, do nothing.

5.  **`get_shortest_path(user_id1, user_id2)`:**  Finds the shortest path (minimum total latency) between `user_id1` and `user_id2`. If no path exists or either user does not exist, return `-1`.

6.  **`get_kth_neighbor(user_id, k)`:** Return `user_id`'s kth immediate neighbor (connected by a single edge) in terms of `user_id`'s immediate neighbors's `user_id`s in ascending order. If there are less than `k` neighbors, return `-1`. If `k` is zero or less, raise ValueError.
    For example, if user `1` is connected to user `2` and `3`, and user id `2` < `3`, `get_kth_neighbor(1, 1)` should return `2`, `get_kth_neighbor(1, 2)` should return `3`.
    If user `1` does not exist, return `-1`.

**Constraints:**

*   The network can potentially grow very large (millions of users and connections).
*   Efficiency is crucial. The `get_shortest_path` operation should be optimized for speed.
*   User IDs are positive integers.
*   Multiple `connect` and `disconnect` operations can occur between the same pair of users.
*   The network is undirected; a connection between user A and user B is the same as a connection between user B and user A.

**Your Task:**

Implement a class or set of functions to efficiently manage this decentralized social network and perform the operations described above. Focus on minimizing the time complexity of the `get_shortest_path` operation, given the dynamic nature of the network. Consider appropriate data structures and algorithms to achieve optimal performance.

**Bonus Challenges:**

*   Implement a mechanism to handle network partitions (when the network splits into disconnected components).
*   Implement a "recommend friends" feature that suggests users to connect with based on common connections and shortest paths.
*   Incorporate a time-to-live (TTL) for connections; connections automatically expire after a certain duration unless refreshed.
