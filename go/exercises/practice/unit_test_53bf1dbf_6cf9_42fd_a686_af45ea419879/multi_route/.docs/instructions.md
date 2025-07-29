Okay, here's a Go coding problem designed to be challenging and require a solid understanding of data structures, algorithms, and optimization techniques.

**Problem Title: Optimal Multi-Source Shortest Path Routing**

**Problem Description:**

You are tasked with designing an efficient routing algorithm for a large-scale distributed system. The system consists of `N` nodes, each identified by a unique integer ID from `0` to `N-1`. The nodes are interconnected via bidirectional communication channels. The latency between any two directly connected nodes is known.

The goal is to find the shortest path from **any** of a given set of `K` source nodes to a designated destination node. This is a multi-source shortest path problem. Your solution must be able to handle a large number of nodes and connections efficiently.

Specifically, you are given the following inputs:

*   `N`: The total number of nodes in the system (1 <= N <= 100,000).
*   `K`: The number of source nodes (1 <= K <= N).
*   `sources`: A slice of `K` distinct integers representing the IDs of the source nodes.
*   `destination`: An integer representing the ID of the destination node.
*   `edges`: A slice of edges, where each edge is represented by a slice of three integers: `[node1, node2, latency]`. This indicates a bidirectional connection between `node1` and `node2` with a latency of `latency`.  (0 <= node1, node2 < N, 1 <= latency <= 1000).  There can be multiple edges between two nodes, latency is always non-negative.

Your task is to write a function `FindShortestPath(N int, K int, sources []int, destination int, edges [][]int) int` that returns the minimum latency required to reach the `destination` node from **any** of the `sources` nodes. If no path exists from any source to the destination, return `-1`.

**Constraints and Requirements:**

*   **Large Input:** The system can have a large number of nodes (up to 100,000) and edges. Your solution must be efficient in terms of both time and memory.
*   **Sparse Graph:** The graph is likely to be sparse (i.e., the number of edges is significantly less than the maximum possible number of edges).
*   **Multiple Edges:** Allow multiple edges between the same two nodes, and you need to consider the minimum latency among them.
*   **No Negative Latencies:** All latencies are non-negative.
*   **Optimization:** The most efficient solutions will likely involve optimized graph algorithms and data structures. Naive implementations will likely time out.
*   **Correctness:** Your solution must correctly handle all valid inputs, including edge cases such as:
    *   `destination` is equal to one of the `sources`.
    *   No path exists from any source to the destination.
    *   The graph is disconnected.
    *   Self-loops (edges where node1 == node2) exist (should be ignored or handled gracefully).
    *   Duplicate edges with different latencies.

This problem requires careful consideration of algorithmic efficiency and edge-case handling. Good luck!
