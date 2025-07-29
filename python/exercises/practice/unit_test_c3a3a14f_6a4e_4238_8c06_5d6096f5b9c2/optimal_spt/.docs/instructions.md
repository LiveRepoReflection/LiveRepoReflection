Okay, here's a challenging problem designed with the goals you outlined, aiming for LeetCode Hard difficulty.

**Problem Title:**  Optimal Multi-Source Shortest Path Tree

**Problem Description:**

You are given a directed graph represented by a list of edges. Each edge has a source node, a destination node, and a non-negative weight.  You are also given a list of *source nodes*. Your task is to construct an *Optimal Multi-Source Shortest Path Tree* (OMS-SPT).

An OMS-SPT is a tree rooted at *any* of the given source nodes, such that for every node in the graph, the path from the *nearest* source node to that node in the tree is the shortest possible path in the original graph. "Nearest" refers to the source node with the smallest shortest-path distance to a given node.

Formally:

1.  **Shortest Path Distance:** For each node `v` in the graph, determine the shortest path distance from each of the source nodes to `v`.

2.  **Nearest Source Node:** For each node `v`, identify the source node `s` that has the minimum shortest path distance to `v`.  If multiple source nodes are equidistant, choose the source node with the smallest node ID. Let's call this the "nearest source" for node `v`.

3.  **OMS-SPT Construction:** Build a tree such that for every node `v`, the path from its nearest source node `s` to `v` in the tree is *identical* to the shortest path from `s` to `v` in the original graph.  If multiple shortest paths exist from `s` to `v`, any of those paths is acceptable.

4.  **Output:** Return the edges of the OMS-SPT as a list of tuples, where each tuple `(u, v, w)` represents a directed edge from node `u` to node `v` with weight `w` in the tree.

**Input:**

*   `num_nodes`: An integer representing the number of nodes in the graph (nodes are numbered from 0 to `num_nodes` - 1).
*   `edges`: A list of tuples, where each tuple `(u, v, w)` represents a directed edge from node `u` to node `v` with weight `w`.
*   `source_nodes`: A list of integers representing the source nodes.

**Constraints:**

*   `1 <= num_nodes <= 10^5`
*   `0 <= len(edges) <= 2 * 10^5`
*   `0 <= u, v < num_nodes`
*   `0 <= w <= 10^4`
*   `1 <= len(source_nodes) <= num_nodes`
*   The graph may contain cycles.
*   The graph may not be fully connected.

**Optimization Requirements:**

*   The solution must be efficient enough to handle large graphs within a reasonable time limit (e.g., several seconds).  Consider using optimized graph algorithms and data structures.

**Edge Cases:**

*   Disconnected graph: Some nodes might not be reachable from any source node.  These nodes should *not* be included in the output tree.
*   Multiple shortest paths: If there are multiple shortest paths between a source node and a node, any of these paths is valid for inclusion in the tree.
*   Source node is the only node on shortest path: Ensure handles edge case when source node to node is only edge needed.
*   Empty graph (no edges): Should handle this case gracefully.

**Example:**

```
num_nodes = 6
edges = [(0, 1, 2), (0, 2, 4), (1, 2, 1), (1, 3, 7), (2, 4, 3), (3, 5, 1), (4, 3, 2), (4, 5, 5)]
source_nodes = [0, 4]

# One possible output (the exact edges might vary depending on shortest path selection):
# [(0, 1, 2), (1, 2, 1), (2, 4, 3), (4, 3, 2), (3, 5, 1)]
```

**Grading Criteria:**

*   Correctness: The solution must produce a valid OMS-SPT that satisfies all the conditions.
*   Efficiency: The solution must be efficient enough to handle large graphs within the time limit.
*   Handling Edge Cases: The solution must correctly handle all specified edge cases.

This problem requires a strong understanding of graph algorithms (Dijkstra's or similar), data structures (priority queues), and careful attention to detail to handle the various constraints and edge cases.  Good luck!
