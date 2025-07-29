Okay, I'm ready to create a challenging Go coding problem. Here's the problem description:

**Project Name:** `OptimalNetworkRouting`

**Question Description:**

You are tasked with designing an optimal routing algorithm for a large-scale communication network. The network consists of `N` nodes, numbered from `0` to `N-1`, and `M` bidirectional communication links. Each link connects two nodes and has an associated cost representing the latency for data transmission across that link.

The network is represented as an adjacency list where `graph[i]` is a list of `(neighbor, cost)` tuples representing the nodes directly connected to node `i` and the associated latency cost to reach that neighbor.

A critical service runs on a subset of these nodes, designated as "service nodes".  A user at any node in the network needs to connect to the *nearest* service node. The distance to the nearest service node is defined as the minimum total latency cost required to reach any service node from the user's node.

Your task is to implement a function that calculates the *maximum* distance from *any* node in the network to its nearest service node. This represents the *worst-case* latency any user might experience when connecting to the service.

**Constraints:**

*   `1 <= N <= 100,000` (Number of nodes)
*   `0 <= M <= 200,000` (Number of links)
*   `1 <= cost <= 1,000` (Latency cost of each link)
*   The network is guaranteed to be connected.
*   There is guaranteed to be at least one service node.
*   Your solution should have a time complexity better than O(N^2).

**Input:**

*   `N`: An integer representing the number of nodes in the network.
*   `graph`: A slice of slices of integers representing the adjacency list of the network. `graph[i]` is a slice of `[neighbor, cost]` integers, indicating a connection from node `i` to node `neighbor` with latency cost `cost`.
*   `serviceNodes`: A slice of integers representing the indices of the nodes that are service nodes.

**Output:**

*   An integer representing the maximum distance from any node to its nearest service node. If all nodes are service nodes, return 0.

**Example:**

```
N = 5
graph = [][]int{
    {{1, 5}, {2, 2}},
    {{0, 5}, {3, 1}},
    {{0, 2}, {4, 8}},
    {{1, 1}, {4, 7}},
    {{2, 8}, {3, 7}},
}
serviceNodes = []int{0, 4}

Output: 6
```

**Explanation:**

*   Node 0 is a service node, so its distance to the nearest service node is 0.
*   Node 1's nearest service node is 0 (distance 5).
*   Node 2's nearest service node is 0 (distance 2).
*   Node 3's nearest service node is 4 (distance 7).
*   Node 4 is a service node, so its distance to the nearest service node is 0.

The maximum of these distances is 7 (Node 3).

Let me know if you want another one!
