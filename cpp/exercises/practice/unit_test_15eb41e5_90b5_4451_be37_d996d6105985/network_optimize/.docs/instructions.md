Okay, here's a challenging C++ coding problem, designed to be at the LeetCode Hard level.

**Project Name:** `NetworkOptimization`

**Question Description:**

You are tasked with designing an optimal communication network for a distributed computing cluster. The cluster consists of `N` nodes, numbered from `0` to `N-1`. Communication between nodes is achieved via direct connections (edges).  Each connection `(u, v)` has an associated latency `L(u, v)` and bandwidth `B(u, v)`.  Latency represents the time it takes for a packet to travel from node `u` to node `v`, and bandwidth represents the maximum data transfer rate between these two nodes. The network is undirected, meaning a connection from `u` to `v` implies a connection from `v` to `u` with the same latency and bandwidth.

The cluster needs to perform a large-scale parallel computation. To facilitate this, all nodes must be able to communicate effectively with each other. The effectiveness of communication is measured by the "bottleneck bandwidth" between any two nodes. The bottleneck bandwidth between nodes `u` and `v` is defined as the *minimum* bandwidth along the path with the *minimum* latency between `u` and `v`. Note that there may be multiple paths with the same minimum latency. The bottleneck bandwidth needs to consider all of those paths.

Your goal is to design a network topology that maximizes the *minimum* bottleneck bandwidth between any two nodes in the cluster. In other words, you want to find a network configuration such that the *weakest link* (the smallest bottleneck bandwidth between any pair of nodes) is as large as possible.

**Input:**

*   `N`: The number of nodes in the cluster (1 <= N <= 100).
*   `edges`: A vector of tuples, where each tuple represents a possible connection in the network. Each tuple has the form `(u, v, L, B)`, where:
    *   `u` and `v` are the node IDs (0 <= u, v < N, u != v).
    *   `L` is the latency of the connection (1 <= L <= 10<sup>6</sup>).
    *   `B` is the bandwidth of the connection (1 <= B <= 10<sup>6</sup>).
    The `edges` vector represents the *potential* connections. You can choose which of these edges to include in your final network. The size of `edges` is variable and can be up to `N * (N - 1) / 2`.

**Output:**

*   The maximum possible minimum bottleneck bandwidth between any two nodes in the cluster, achievable by selecting a subset of the given edges. If it's not possible to connect all nodes, return 0.

**Constraints:**

*   The solution must be efficient in terms of both time and space complexity.  Brute-force approaches that explore all possible edge combinations will likely time out.
*   The graph must be connected.  If there is no way to connect all N nodes with the selected edges, return 0.
*   You are not allowed to add edges that are not in the input `edges` vector.
*   The latency and bandwidth are integers.

**Example:**

```
N = 3
edges = {
    (0, 1, 10, 50),
    (0, 2, 20, 30),
    (1, 2, 5, 80)
}

Output: 50

Explanation:
The optimal network includes edges (0, 1, 10, 50) and (1, 2, 5, 80).
The bottleneck bandwidth between:
- 0 and 1: 50
- 1 and 2: 80
- 0 and 2: Path 0-1-2 has latency 15 and bottleneck bandwidth min(50, 80) = 50. Direct path 0-2 has latency 20 and bottleneck bandwidth 30. Thus, the bottleneck bandwidth between 0 and 2 is 50.

The minimum of these is 50.
```

**Challenge:**

The difficulty lies in efficiently exploring the possible edge combinations and computing the bottleneck bandwidth for each pair of nodes in a connected graph. You'll need to balance connectivity, minimizing latency, and maximizing bandwidth.  Consider using techniques like binary search, graph algorithms (Dijkstra, Floyd-Warshall, Minimum Spanning Tree), and potentially Disjoint Set Union (DSU) for checking connectivity. The need to find the *minimum* latency path first, and *then* consider the bottleneck bandwidth along *those* paths is a significant hurdle.
