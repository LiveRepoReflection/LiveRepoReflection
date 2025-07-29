## The Martian Network

**Problem Description:**

The year is 2077. Humanity has established a permanent colony on Mars. Communication within the colony relies on a complex network of interconnected nodes. These nodes are of varying capabilities and are prone to intermittent failures due to Martian dust storms and radiation flares.

You are tasked with designing a robust routing algorithm for this Martian network. The network can be represented as a directed graph where nodes represent communication hubs and edges represent communication links. Each link has a *time-varying* latency, represented by a function that depends on the current Martian sol (day).

More formally:

*   The network is a directed graph G = (V, E), where V is the set of nodes (numbered 0 to N-1) and E is the set of edges.
*   Each edge (u, v) in E has a latency function `latency(sol)` which returns the latency of the link from node `u` to node `v` at a given Martian sol (an integer). The latency function will always return a non-negative integer.
*   Nodes have a failure probability associated with them. Represented by `failure_probability(node)` which returns the failure probability (a float between 0 and 1 inclusive) for a given node. Nodes can fail independently.
*   The goal is to find the *most reliable* path between a source node `s` and a destination node `d` for a *given range* of Martian sols [start_sol, end_sol] (inclusive).
*   The reliability of a path is defined as the probability that *all* nodes on the path *except the destination* (as that node must exist for the message to be received) are operational throughout the entire range of sols and the sum of latencies from start to end sol is minimized.

**Reliability Calculation:**

1.  **Node Reliability:** The reliability of a node for a given sol is `1 - failure_probability(node)`.
2.  **Path Node Reliability:** The reliability of a node on a path for the entire sol range \[start\_sol, end\_sol] is the product of its reliability for each sol in the range.
3.  **Path Reliability:** The reliability of a path is the product of the reliability of each node (excluding the destination node) on that path.
4.  **Path Latency:** The latency of a path is the sum of the latencies of each link on the path, summed for all sols in the range [start_sol, end_sol]. `Sum( latency(sol) for sol in range(start_sol, end_sol + 1) )`
5. **Most Reliable Path:** The most reliable path is the one with the highest reliability. In the event of ties, the path with the *lowest total latency* across the sol range is preferred.

**Input:**

*   `N`: The number of nodes in the network.
*   `edges`: A list of tuples representing the edges in the graph. Each tuple is of the form `(u, v, latency_function)`, where `u` is the source node, `v` is the destination node, and `latency_function` is a callable that takes an integer `sol` as input and returns the latency of the edge at that sol.
*   `failure_probabilities`: A list of floats, where `failure_probabilities[i]` is the failure probability of node `i`.
*   `s`: The source node.
*   `d`: The destination node.
*   `start_sol`: The starting sol.
*   `end_sol`: The ending sol.

**Output:**

A tuple containing:

1.  A list representing the most reliable path from node `s` to node `d` (including both `s` and `d`). If no path exists, return an empty list `[]`.
2.  The reliability of the returned path (a float). If no path exists, return 0.0.
3.  The latency of the returned path (an integer) across the entire sol range. If no path exists, return 0.

**Constraints:**

*   1 <= N <= 500
*   0 <= `edges.length` <= N \* (N - 1)
*   0 <= `u`, `v` < N for each edge (u, v, latency\_function)
*   0.0 <= `failure_probabilities[i]` <= 1.0 for all i
*   0 <= `s`, `d` < N
*   0 <= `start_sol` <= `end_sol` <= 100
*   The graph may contain cycles.
*   The latency function always returns a non-negative integer.
*   You need to find the *most reliable* path. If there are multiple paths with the same reliability, return the path with the lowest total latency.

**Example:**

Let's say the network has 3 nodes (0, 1, 2).

*   `edges = [(0, 1, lambda sol: sol + 1), (1, 2, lambda sol: sol + 2), (0, 2, lambda sol: sol + 3)]`
*   `failure_probabilities = [0.1, 0.2, 0.3]`
*   `s = 0`
*   `d = 2`
*   `start_sol = 1`
*   `end_sol = 2`

There are two possible paths:

*   Path 1: 0 -> 2 (direct link)
*   Path 2: 0 -> 1 -> 2

The algorithm must determine which path is more reliable, considering the node failure probabilities and the time-varying latencies over sols 1 and 2.

**Judging Criteria:**

Your solution will be judged based on:

*   **Correctness:** The solution must correctly identify the most reliable path and its reliability, given the constraints.
*   **Efficiency:** The solution should be computationally efficient, especially for larger networks and wider sol ranges.  Solutions with excessive runtime (e.g., brute-force exploration of all paths) will be penalized or may fail. Consider using appropriate graph algorithms and data structures.
*   **Robustness:** The solution should handle edge cases gracefully, such as disconnected graphs or paths with very low reliability.

This problem requires a combination of graph traversal algorithms, probability calculations, and careful optimization. Good luck!
