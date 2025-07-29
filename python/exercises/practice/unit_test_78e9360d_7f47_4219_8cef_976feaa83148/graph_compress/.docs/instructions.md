Okay, here's a challenging problem designed for a competitive programming environment, focusing on algorithmic efficiency and incorporating several complex elements.

### Project Name

```
GraphCompression
```

### Question Description

You are given a directed graph represented as a list of edges. Each edge is a tuple `(u, v, w)` where `u` and `v` are node IDs (integers) and `w` is the edge weight (an integer).  Your task is to "compress" this graph while preserving shortest path distances between a specified set of important nodes.

Specifically:

1.  **Important Nodes:** You are given a set `S` of important node IDs.
2.  **Goal:** Construct a new directed graph `G'` with the following properties:
    *   The set of nodes in `G'` should be a subset of the original nodes in `G`.
    *   All nodes in `S` *must* be present in `G'`.
    *   For every pair of nodes `u, v` in `S`, the shortest path distance from `u` to `v` in `G'` must be *exactly* the same as the shortest path distance from `u` to `v` in the original graph `G`.  If there is no path from `u` to `v` in `G`, then there should be no path from `u` to `v` in `G'`.
3.  **Constraints:**
    *   You must use only the nodes and edges from the original graph `G` to construct `G'`. You cannot create new nodes or edges that do not exist in the original graph.
    *   The number of nodes in `G'` should be minimized. In other words, remove as many non-essential nodes as possible while satisfying the shortest path distance requirement.
    *   If multiple compressed graphs with the minimal number of nodes are possible, any of them is considered a valid solution.
4.  **Input:**
    *   `edges`: A list of tuples `(u, v, w)` representing the directed graph `G`.
    *   `important_nodes`: A set `S` of integers representing the important node IDs.
    *   Node IDs are non-negative integers. Edge weights are positive integers.
5.  **Output:**
    *   A list of tuples `(u, v, w)` representing the compressed directed graph `G'`.
6. **Optimizations:**
    * Aim for an efficient algorithm. The original graph G can contain up to 10,000 nodes and 100,000 edges. The number of important nodes can range from 2 to 100.
    * The graph can be sparse or dense.
7. **Edge Cases:**
    * Disconnected graph: The original graph may not be fully connected.
    * No path: There may be pairs of important nodes that have no path between them in the original graph.
    * Identical shortest paths: Different paths of the same length between nodes.
    * Self loops: Graph may contain self loops.
    * Zero weight cycles: Graph may contain zero weight cycles.
8. **Tie-Breaker**:
    * If there are multiple solutions with the same number of nodes, one with fewer edges should be selected.

This problem requires a combination of graph algorithms (shortest paths), data structure knowledge, and optimization techniques to achieve a good solution within reasonable time constraints. It's designed to be challenging and differentiate between strong candidates. Good luck!
