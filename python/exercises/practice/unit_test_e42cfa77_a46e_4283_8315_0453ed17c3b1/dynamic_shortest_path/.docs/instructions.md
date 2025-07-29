Okay, here's a challenging problem designed to test advanced Python skills, suitable for a high-level programming competition:

**Problem Title:** Multi-Source Shortest Path with Dynamic Edge Weights

**Problem Description:**

You are given a directed graph representing a communication network. The graph has `N` nodes (numbered 0 to N-1) and `M` edges. Each edge initially has a weight associated with it, representing the latency of communication along that link.  However, the network is subject to dynamic changes: the weight of specific edges can change unpredictably over time.

You are also given a set of `K` source nodes.  The goal is to efficiently determine the shortest path distance from *any* of these source nodes to *every* other node in the graph, *after* a series of edge weight updates.

More formally:

1.  **Graph Representation:**  The graph is represented as a list of edges, where each edge is a tuple `(u, v, w)`, meaning there is a directed edge from node `u` to node `v` with weight `w`.

2.  **Source Nodes:** A list of `K` integers representing the source nodes.

3.  **Edge Weight Updates:** A list of update operations. Each update is a tuple `(u, v, new_weight)`, meaning the weight of the edge from node `u` to node `v` is changed to `new_weight`.  If the edge `(u,v)` does not exist in the initial graph, it should be added to the graph with the specified `new_weight`.

4.  **Shortest Path Calculation:** After all updates are applied, you need to calculate the shortest path distance from *any* of the source nodes to *every* other node in the graph. If a node is unreachable from any of the source nodes, its shortest path distance should be considered infinity (`float('inf')`).

**Input:**

*   `N`: The number of nodes in the graph (0 <= N <= 10<sup>5</sup>).
*   `edges`: A list of tuples representing the initial edges of the graph: `[(u1, v1, w1), (u2, v2, w2), ...]`, where:
    *   `0 <= u<sub>i</sub> < N`
    *   `0 <= v<sub>i</sub> < N`
    *   `1 <= w<sub>i</sub> <= 10<sup>6</sup>` (initial edge weights)
*   `sources`: A list of integers representing the source nodes: `[s1, s2, ..., sK]`, where `0 <= s<sub>i</sub> < N`.
*   `updates`: A list of tuples representing the edge weight updates: `[(u1, v1, new_w1), (u2, v2, new_w2), ...]`, where:
    *   `0 <= u<sub>i</sub> < N`
    *   `0 <= v<sub>i</sub> < N`
    *   `1 <= new_w<sub>i</sub> <= 10<sup>6</sup>` (updated edge weights)

**Output:**

*   A list of `N` numbers, where the i-th number represents the shortest path distance from any of the source nodes to node `i`. If node `i` is unreachable from any source node, the i-th number should be `float('inf')`.

**Constraints:**

*   1 <= N <= 10<sup>5</sup>
*   0 <= M <= 2 * 10<sup>5</sup> (number of initial edges)
*   1 <= K <= N (number of source nodes)
*   0 <= Number of updates <= 10<sup>4</sup>
*   The graph may contain cycles.
*   Edge weights are positive integers.

**Efficiency Requirements:**

The solution must be efficient enough to handle large graphs and a significant number of updates within a reasonable time limit (e.g., a few seconds). Naive approaches like recomputing shortest paths from scratch after each update will likely time out.

**Example:**

```
N = 5
edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (2, 3, 2), (3, 4, 4)]
sources = [0, 4]
updates = [(0, 1, 2), (2, 3, 1)]

Output:
[0, 2, 3, 4, 4]
```

**Explanation of Example:**

1.  Initial graph: Edges are (0,1,5), (0,2,3), (1,3,6), (2,3,2), (3,4,4).
2.  Source nodes: 0 and 4.
3.  Updates:
    *   Edge (0, 1) weight changes from 5 to 2.
    *   Edge (2, 3) weight changes from 2 to 1.
4.  Shortest paths after updates:
    *   Node 0: Distance is 0 (source node).
    *   Node 1: Shortest path is 0 -> 1 (distance 2).
    *   Node 2: Shortest path is 0 -> 2 (distance 3).
    *   Node 3: Shortest path is 0 -> 2 -> 3 (distance 3 + 1 = 4).
    *   Node 4: Shortest path is 4 (distance 0, source node) OR 0 -> 2 -> 3 -> 4 (distance 3 + 1 + 4 = 8, but 4 is a source so distance is 0) so 4.

This problem requires a combination of graph algorithms and efficient data structures to handle the dynamic nature of the edge weights.  Good luck!
