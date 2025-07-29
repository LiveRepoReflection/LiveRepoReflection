Okay, here's a challenging Go coding problem, designed to be difficult and requiring a good understanding of data structures, algorithms, and optimization:

## Project Name:

```
network-routing
```

## Question Description:

You are tasked with designing an efficient routing algorithm for a large-scale communication network. The network consists of `n` nodes, where each node represents a router. The nodes are connected by bidirectional communication links, each having a specific latency (time delay) and bandwidth (data carrying capacity). The network topology is not necessarily a fully connected graph, and some nodes might not be directly connected.

Your goal is to implement a function that, given the network topology, a source node, a destination node, a minimum required bandwidth, and a maximum acceptable latency, finds the path with the highest available bandwidth among all paths that satisfy the maximum latency constraint.

**Input:**

*   `nodes`: An array of node IDs (integers from `0` to `n-1`).
*   `edges`: A list of tuples, where each tuple `(node1, node2, latency, bandwidth)` represents a bidirectional communication link between `node1` and `node2`. `latency` and `bandwidth` are integers.
*   `source`: The ID of the source node (integer).
*   `destination`: The ID of the destination node (integer).
*   `minBandwidth`: The minimum bandwidth required for the path to be considered valid (integer).
*   `maxLatency`: The maximum latency allowed for the path (integer).

**Output:**

*   A list of node IDs representing the optimal path from the source to the destination, satisfying both bandwidth and latency constraints. The path should start with the `source` node and end with the `destination` node. If no path exists that satisfies the constraints, return an empty list.

**Constraints and Considerations:**

1.  **Network Size:** The network can be large (up to 10,000 nodes and 50,000 edges).
2.  **Multiple Paths:** There can be multiple paths between the source and destination. You need to find the one with the *highest* available bandwidth among those that satisfy the latency constraint. The available bandwidth of a path is the minimum bandwidth of all the edges in that path.
3.  **Efficiency:** The solution needs to be efficient in terms of both time and memory usage. A naive approach like brute-force path enumeration will likely time out.  Consider efficient graph traversal algorithms.
4.  **Edge Cases:**
    *   Handle cases where the source and destination are the same node.
    *   Handle cases where there is no path between the source and destination.
    *   Handle cases where no path satisfies the minimum bandwidth or maximum latency constraints.
    *   Handle disconnected graphs.
5.  **Tiebreaker:** If multiple paths have the same highest available bandwidth and satisfy the latency constraint, you can return any of them.
6.  **Zero Latency/Bandwidth:** The problem statement does not prevent zero latency or bandwidth edges. Zero latency edges should be permitted, but a path with zero bandwidth should always be considered invalid unless `minBandwidth` is zero.

**Example:**

```
nodes = [0, 1, 2, 3]
edges = [(0, 1, 10, 50), (0, 2, 5, 20), (1, 2, 3, 30), (1, 3, 2, 40), (2, 3, 1, 60)]
source = 0
destination = 3
minBandwidth = 35
maxLatency = 15

Output: [0, 1, 3]  // Path 0 -> 1 -> 3 has a bandwidth of min(50, 40) = 40 >= 35 and latency of 10 + 2 = 12 <= 15. This is the best possible path.
```

**Challenge:**

The primary challenge lies in efficiently exploring the graph, considering both latency and bandwidth constraints simultaneously, and finding the *optimal* path, not just *any* valid path. Consider how to prune the search space to avoid unnecessary computations. Think about how to combine shortest path algorithms with bandwidth considerations.

Good luck!
