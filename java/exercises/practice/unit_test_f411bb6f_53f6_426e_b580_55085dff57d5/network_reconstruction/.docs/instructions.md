## Project Name

`NetworkReconstruction`

## Question Description

You are given a set of servers in a data center. Each server has a unique ID from `1` to `N`. The servers are interconnected via a network. You are also given a log of network traffic. Each entry in the log represents a connection between two servers at a specific timestamp.

Your task is to reconstruct the underlying network topology based on the network traffic log. The network topology is represented as an adjacency list, where each server ID is a key, and the value is a list of server IDs that are directly connected to it.

However, due to intermittent logging failures, the log is incomplete. You are guaranteed that the provided log entries represent valid connections in the actual network, but the absence of a log entry does not necessarily mean the servers are not connected.

**Specific Requirements:**

1.  **Reconstruction Criteria:** Reconstruct the network such that the number of "hops" (number of edges) between any two servers is minimized, while **strictly** adhering to the connections evidenced in the log.
2.  **Edge weights:** Assume an unweighted graph for the network topology.
3.  **Optimization:** The solution must reconstruct the network in the most efficient way possible. The primary objective is to minimize the *average path length* between all pairs of servers in the reconstructed network. Shorter average path lengths indicate a more efficient network.  Assume each server can reach every other server through the network.
4.  **Handling Missing Information:** You must infer missing connections in the network to reduce the average path length, but ONLY if such connections do not contradict the existing log data.
5. **Constraint:** The number of servers in the data center should be greater or equal than 2.
6.  **Real-world:** Consider the real-world constraints of network infrastructure like limited bandwidth or other factors that incentivize shorter path lengths.

**Input:**

*   `N`: An integer representing the number of servers in the data center.
*   `log`: A list of tuples, where each tuple represents a network traffic log entry. Each tuple contains three elements: `(timestamp, server_id_1, server_id_2)`. The `timestamp` is a long integer, `server_id_1` and `server_id_2` are integers representing the IDs of the two servers connected in that log entry. It is guaranteed that `1 <= server_id_1, server_id_2 <= N` and `server_id_1 != server_id_2`. Also `log` can be empty.

**Output:**

*   A `Map<Integer, Set<Integer>>` representing the reconstructed network topology as an adjacency list. The keys are server IDs (integers from `1` to `N`), and the values are `Set` objects containing the IDs of their directly connected neighbors. Ensure that:

    *   The returned map contains exactly N keys (one for each server)
    *   The neighbors in each server's `Set` are sorted (ascending order).
    *   If `server_id_2` is in `server_id_1`'s neighbor set, `server_id_1` must be in `server_id_2`'s neighbor set (undirected graph).
    *   No server can be a neighbor of itself.

**Example:**

```
N = 4
log = [
    (1678886400, 1, 2),
    (1678886401, 2, 3),
]

Expected Output:

{
    1: {2, 4},
    2: {1, 3},
    3: {2, 4},
    4: {1, 3}
}

Explanation:
The log shows connections between 1-2 and 2-3. To minimize the average path length, we infer connections 1-4 and 3-4, forming a network that approximates a complete graph.

```

**Constraints:**

*   `2 <= N <= 200`
*   `0 <= len(log) <= N * (N - 1) / 2`
*   Timestamps in the log are unique.

**Bonus:**

*   Explain the time and space complexity of your solution.
*   Discuss the trade-offs of different approaches to solving this problem.
*   Consider how your solution would scale if `N` were significantly larger (e.g., `N = 10000`).

This problem tests your understanding of graph algorithms, data structures, optimization techniques, and your ability to handle incomplete data to make informed decisions. Good luck!
