Okay, here's a challenging Java coding problem designed to be at LeetCode Hard level, incorporating the elements you requested:

## Project Name

`EvolvingNetwork`

## Question Description

You are tasked with designing and implementing a system to model and analyze an evolving social network. This network represents connections between users, but these connections change over time. Furthermore, users have associated *influence* scores that can also dynamically change based on their connections and activities.

The system must support the following operations efficiently:

1.  **`addUser(userId)`:** Adds a new user to the network. `userId` is a unique integer.

2.  **`removeUser(userId)`:** Removes a user from the network and all their connections.

3.  **`addConnection(userId1, userId2, timestamp)`:** Adds a connection between `userId1` and `userId2` at the given `timestamp`.  Connections are directed (from `userId1` to `userId2`).  If a connection already exists at an earlier timestamp, this new connection overwrites the previous one.

4.  **`removeConnection(userId1, userId2, timestamp)`:** Removes the connection from `userId1` to `userId2` at the given `timestamp`. If no connection exists at that timestamp, the operation has no effect. If a connection exists at an earlier timestamp, the connection should still exist.

5.  **`getConnections(userId, timestamp)`:** Returns a list of `userId`s that `userId` has a direct connection *to* at the given `timestamp`.  The list should be sorted in ascending order of `userId`. If no connections exist for the given `userId` at that timestamp, return an empty list. Only the connections whose timestamps are less than or equal to the query timestamp are relevant.

6.  **`calculateInfluenceScore(userId, timestamp, decayFactor)`:** Calculates the influence score of a user at a given `timestamp`. The influence score is calculated as follows:

    *   Start with an initial influence score of 1 for the user.
    *   For each user `v` that `userId` is connected to at the given `timestamp` (using `getConnections`):
        *   Add `decayFactor * influenceScore(v, timestamp, decayFactor)` to `userId`'s influence score.
    *   Return the final influence score.

    **Important Considerations for `calculateInfluenceScore`:**

    *   The influence score calculation is recursive.  To prevent infinite loops, you must detect and handle cycles in the network. If a cycle is detected during influence score calculation, break the cycle by treating the influence score of the current node in the cycle as 0 for subsequent calculations within that cycle.
    *   The `decayFactor` is a value between 0 and 1 (inclusive) that represents how much influence is passed from one user to another.
    *   The influence score calculation should be optimized. Naive recursive implementations will likely time out for larger networks.  Consider memoization or other techniques to improve performance.

**Constraints:**

*   `userId` is a positive integer between 1 and 10<sup>5</sup>.
*   `timestamp` is a positive integer representing seconds since the epoch, between 1 and 10<sup>9</sup>. Timestamps for connections are not necessarily monotonically increasing.
*   `decayFactor` is a double between 0.0 and 1.0 (inclusive).
*   The number of operations will be up to 10<sup>5</sup>.
*   Memory usage is a critical factor. Solutions that consume excessive memory may be rejected.
*   The number of users in the network will not exceed 10<sup>4</sup> at any point.
*   The number of connections for a given user at any given timestamp will not exceed 100.

**Optimization Requirements:**

The solution must be optimized for both time and space complexity.  Operations like `getConnections` and `calculateInfluenceScore` should be efficient, even for large networks and complex connection histories.

**Real-world Practical Scenarios:**

This problem models real-world scenarios such as social network analysis, citation networks, and dependency graphs. The dynamic nature of connections and the concept of influence propagation are relevant to many applications.

**System Design Aspects:**

Consider how your data structures are organized to support efficient retrieval of connections at specific timestamps. Think about the trade-offs between memory usage and query performance.

**Algorithmic Efficiency Requirements:**

*   Aim for logarithmic or constant time complexity for `addUser`, `removeUser`, `addConnection`, and `removeConnection` where possible, considering the constraints.
*   `getConnections` should be optimized for its timestamp-based retrieval.
*   `calculateInfluenceScore` must be carefully designed to handle cycles and large networks efficiently.  Memoization is strongly advised.

This problem requires a solid understanding of data structures (especially graphs and potentially specialized tree-like structures for managing timestamps), algorithmic optimization techniques (memoization, cycle detection), and careful consideration of edge cases and constraints. Good luck!
