## Question: Network Reconstruction with Minimum Latency

**Problem Description:**

You are given a set of `n` servers in a data center.  Each server has a unique ID from `0` to `n-1`.  These servers need to communicate with each other, and you are tasked with reconstructing the network topology to minimize the overall communication latency.

The network topology can be represented as a weighted, undirected graph where:

*   Nodes represent the servers.
*   Edges represent direct network connections between servers.
*   Edge weights represent the latency of communication between the connected servers.

You are given a partial connectivity matrix `partialConnectivity` of size `n x n`. `partialConnectivity[i][j]` represents the observed latency between server `i` and server `j`. If `partialConnectivity[i][j] == -1`, it means the latency between server `i` and server `j` is unknown and needs to be determined. If `i == j`, `partialConnectivity[i][j] == 0`.

Your goal is to complete the connectivity matrix `completedConnectivity` such that:

*   `completedConnectivity[i][j] >= 1` if there is a direct connection between server `i` and server `j`, and `completedConnectivity[i][j] == 0` if `i == j`.
*   `completedConnectivity[i][j] == completedConnectivity[j][i]` (undirected graph).
*   `completedConnectivity[i][j] >= partialConnectivity[i][j]` for all `i, j` where `partialConnectivity[i][j] != -1`
*   All server pairs can communicate via the network (the graph is connected).

The overall communication latency of the network is defined as the sum of the shortest path latencies between all pairs of servers.  Formally, it's the sum of all-pairs shortest paths, where the shortest path latency between server `i` and server `j` is the minimum sum of edge weights along any path connecting them in the `completedConnectivity` graph.

Your task is to write a function that takes `n` and `partialConnectivity` as input and returns the *minimum possible* overall communication latency achievable by completing the connectivity matrix, or `-1` if it's impossible to construct a connected graph satisfying the given constraints. If there are multiple valid topologies, you need to find the one with minimum overall communication latency.

**Constraints:**

*   `1 <= n <= 30`
*   `partialConnectivity[i][j] == -1` or `1 <= partialConnectivity[i][j] <= 100` or `partialConnectivity[i][j] == 0`
*   `partialConnectivity[i][j] == partialConnectivity[j][i]` for all `i, j`
*   You must use Java.
*   The time limit for this problem is strict. An inefficient solution will not pass.

**Example:**

```
n = 3
partialConnectivity = [
    [0, -1, 2],
    [-1, 0, -1],
    [2, -1, 0]
]
```

One possible `completedConnectivity` is:

```
[
    [0, 1, 2],
    [1, 0, 3],
    [2, 3, 0]
]
```

In this `completedConnectivity` matrix, the latency between server 0 and server 1 is 1, and the latency between server 1 and server 2 is 3.

**Input:**

*   `n`: The number of servers.
*   `partialConnectivity`: A 2D integer array representing the partial connectivity matrix.

**Output:**

*   The minimum possible overall communication latency, or `-1` if it's impossible to construct a connected graph satisfying the constraints.

**Judging Criteria:**

Solutions will be judged based on correctness, efficiency, and code clarity.  Test cases will include various scenarios, including:

*   Sparse and dense `partialConnectivity` matrices.
*   Cases where some latencies are already fixed, requiring careful consideration of the remaining connections.
*   Cases where it's impossible to construct a valid network.
*   Cases that require optimization to meet the time limit.
*   Edge cases with small and relatively large `n` values.
