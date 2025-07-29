## The Interdimensional Cable Network

**Problem Description:**

You are tasked with designing and optimizing the interdimensional cable network for a burgeoning civilization capable of accessing alternate realities. This network allows users to "tune in" to broadcasts originating from different dimensions. However, maintaining signal integrity and minimizing interference across dimensions presents significant challenges.

The network can be represented as a weighted, undirected graph. Each node in the graph represents a dimensional hub, and each edge represents a cable connecting two hubs. Each cable has a *bandwidth* and a *latency*.

A user wants to tune into a broadcast originating from dimension *A* and wants to view it on dimension *B*. The network must establish a path from *A* to *B*.

**The Challenge:**

Given the network graph, a source dimension *A*, a destination dimension *B*, and a minimum required *bandwidth* *K*, find the path from *A* to *B* that satisfies the bandwidth requirement while minimizing the *total latency* of the path.  The bandwidth of a path is defined as the minimum bandwidth of all edges in the path.

**Constraints and Requirements:**

1.  **Graph Representation:** The graph can be quite large (up to 10<sup>5</sup> nodes and 10<sup>6</sup> edges).
2.  **Bandwidth Requirement:** The selected path *must* have a bandwidth of at least *K*.
3.  **Latency Minimization:** Among all paths that satisfy the bandwidth requirement, the path with the lowest total latency must be chosen.
4.  **Edge Cases:** Consider cases where no path exists between *A* and *B* that meets the bandwidth requirement. Also, handle disconnected graphs.
5.  **Optimization:** The solution must be computationally efficient. Naive approaches (e.g., brute-force searching all possible paths) will not scale to the problem size.  Consider algorithmic complexity.
6.  **Multiple Optimal Paths:** If multiple paths satisfy the bandwidth requirement and have the same minimal latency, any one of those paths is considered a valid solution.
7.  **Real-World Consideration:** Bandwidth and latency values will be positive integers. Node identifiers will also be positive integers.
8. **Memory Usage:** Try to use memory efficiently, considering the potentially large graph size.

**Input:**

The input will be provided in the following format:

*   `N`: The number of nodes (dimensional hubs) in the network.
*   `M`: The number of edges (cables) in the network.
*   `edges`: A list of tuples `(u, v, bandwidth, latency)`, where `u` and `v` are the IDs of the connected nodes, `bandwidth` is the bandwidth of the cable, and `latency` is the latency of the cable.
*   `A`: The ID of the source dimension.
*   `B`: The ID of the destination dimension.
*   `K`: The minimum required bandwidth.

**Output:**

Return the minimum total latency of a path from A to B that satisfies the bandwidth requirement K. If no such path exists, return -1.

Good luck!
