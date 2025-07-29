## Problem: Optimal Multi-Source Shortest Path Tree Construction

**Question Description:**

You are given a directed graph represented by a list of nodes and a list of directed edges. Each edge has a positive integer weight representing the cost of traversing that edge. The graph may contain cycles.

You are also given a set of *k* source nodes within this graph.

Your task is to construct a *minimum-weight shortest-path tree* rooted at these *k* source nodes. A shortest-path tree is a subgraph of the original graph that satisfies the following conditions:

1.  **Reachability:** Every node in the original graph reachable from at least one of the *k* source nodes must also be reachable in the shortest-path tree from at least one of the *k* source nodes.

2.  **Shortest Paths:** For every node *v* reachable from at least one of the *k* source nodes, the distance from the *closest* source node to *v* in the shortest-path tree is equal to the distance from the *closest* source node to *v* in the original graph. The distance from a source node *s* to node *v* is defined as the sum of the weights of edges along the shortest path from *s* to *v*. If a node is unreachable from all source nodes, its distance is considered infinite.

3.  **Tree Structure:** The resulting subgraph must be a tree, meaning it contains no cycles (when considering the undirected version of the directed subgraph). Note that since the input graph is directed, cycles might still exist in the original graph, but the shortest-path tree you construct must not contain any cycles.

4.  **Minimum Weight:** Among all possible shortest-path trees that satisfy the above conditions, the tree you construct must have the minimum total edge weight.

**Input:**

*   `nodes`: A list of integers representing the node IDs. Node IDs are assumed to be positive integers.
*   `edges`: A list of tuples, where each tuple `(u, v, w)` represents a directed edge from node `u` to node `v` with weight `w`. `u` and `v` are node IDs (integers), and `w` is a positive integer representing the edge weight.
*   `sources`: A list of integers representing the IDs of the *k* source nodes. The source nodes are a subset of the nodes in the graph.

**Output:**

A list of tuples, where each tuple `(u, v, w)` represents a directed edge that is part of the constructed minimum-weight shortest-path tree. The edges in the output must form a valid shortest-path tree according to the conditions above.

**Constraints:**

*   The number of nodes in the graph can be large (up to 10<sup>5</sup>).
*   The number of edges in the graph can be very large (up to 10<sup>6</sup>).
*   The edge weights are positive integers and can be large (up to 10<sup>4</sup>).
*   The number of source nodes *k* can vary (1 <= *k* <= number of nodes).
*   The graph may be disconnected.
*   The graph may contain cycles.

**Efficiency Requirements:**

Your solution must be efficient enough to handle large graphs within a reasonable time limit (e.g., within a few seconds). Consider using efficient graph algorithms and data structures.

**Example:**

```
nodes = [1, 2, 3, 4, 5]
edges = [(1, 2, 1), (1, 3, 5), (2, 3, 2), (2, 4, 2), (3, 4, 1), (3, 5, 3), (4, 5, 2), (5, 1, 1)]
sources = [1, 2]

# Possible output (not necessarily unique, but must satisfy the conditions):
# [(1, 2, 1), (2, 3, 2), (2, 4, 2), (4, 5, 2)]
```

**Grading Criteria:**

*   Correctness: Your solution must produce a valid shortest-path tree that satisfies all the specified conditions.
*   Efficiency: Your solution must be efficient enough to handle large graphs within a reasonable time limit.
*   Minimum Weight: Your solution must find the shortest-path tree with the minimum possible total edge weight.
*   Handling Edge Cases: Your solution must correctly handle various edge cases, such as disconnected graphs, cycles, and different numbers of source nodes.
