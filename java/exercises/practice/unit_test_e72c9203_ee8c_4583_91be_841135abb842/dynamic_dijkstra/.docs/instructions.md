## Question: Optimized Multi-Source Dijkstra with Dynamic Updates

### Description

You are tasked with implementing an optimized version of Dijkstra's algorithm to find the shortest paths from multiple source nodes to all other nodes in a weighted, directed graph. However, this is not a standard, static graph. The edge weights are dynamic and can be updated frequently.

Specifically, you will be given a graph represented as an adjacency list. Each node in the graph is identified by a unique integer ID from `0` to `N-1`, where `N` is the total number of nodes in the graph.

Your implementation must support the following operations efficiently:

1.  **`initialize(N, edges)`**: Initializes the graph with `N` nodes and a list of edges. Each edge is represented as a tuple `(u, v, w)`, where `u` is the source node, `v` is the destination node, and `w` is the weight of the edge.
2.  **`setSources(sources)`**: Sets the source nodes for the multi-source Dijkstra algorithm. `sources` is a list of node IDs.
3.  **`updateEdge(u, v, w)`**: Updates the weight of the edge from node `u` to node `v` to `w`. If the edge does not exist, it should be created.
4.  **`getShortestPaths()`**: Executes Dijkstra's algorithm from the current set of source nodes and returns an array `dist` of length `N`, where `dist[i]` is the shortest distance from any of the source nodes to node `i`. If a node is unreachable from any source node, `dist[i]` should be `Integer.MAX_VALUE`.

**Constraints:**

*   `1 <= N <= 10^5` (Number of nodes)
*   `0 <= u, v < N` (Node IDs)
*   `1 <= w <= 10^9` (Edge weights)
*   The number of edges can be up to `2 * 10^5`.
*   The number of source nodes can be up to `N`.
*   The `updateEdge` operation will be called frequently. Optimize for its performance.
*   The `getShortestPaths` operation needs to be efficient.  Consider how updates to the graph affect its performance.
*   Your solution must handle disconnected graphs gracefully.
*   Edge weights can be updated to `0` or even negative values. However, **there are no negative cycles** in the graph.

**Requirements:**

*   Implement the solution in Java.
*   Pay close attention to algorithmic efficiency.  A naive implementation of Dijkstra's algorithm after each update will time out. Consider using appropriate data structures and techniques to optimize the algorithm, especially for the dynamic updates.
*   The `initialize`, `setSources`, `updateEdge`, and `getShortestPaths` operations should have reasonable time complexities. Consider the trade-offs between the time complexity of each operation. Aim for a balance that provides good overall performance.
*   Your code must be well-structured, readable, and maintainable.

**Judging Criteria:**

The solution will be judged based on correctness, efficiency (time complexity), code quality, and adherence to the constraints and requirements. The primary focus will be on the performance of the `updateEdge` and `getShortestPaths` operations. Solutions that time out for large graphs or frequent updates will not be accepted. Memory usage will also be considered.
